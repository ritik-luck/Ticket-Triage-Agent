import uuid
import asyncio
from typing import List, Dict, Any, Optional
from models import TicketRequest, TriageResponse
from utils.logger import get_logger
from rag.augmentation import augmentation_manager
from rag.embeddings import embedding_manager
from tools.classification import classify_ticket
from tools.priority import detect_priority
from tools.routing import route_ticket
from tools.web_search import web_search_fallback
from tools.sla import predict_sla
from memory.memory_manager import memory_manager
from tools.guadrails import apply_guardrails
from sentence_transformers.util import cos_sim


logger = get_logger(__name__)
CACHE_SIMILARITY_THRESHOLD = 0.75
SIMILAR_TICKET_THRESHOLD = 0.55
LOW_CONFIDENCE_THRESHOLD = 0.60


def build_issue_text(request: TicketRequest) -> str:
    issue_text = f"""
    Subject: {request.subject}
    Description: {request.description}
    """

    return issue_text.strip()


def find_cached_ticket(issue_text: str) -> Optional[Dict[str, Any]]:
    past_tickets = memory_manager.get_all_ticket_logs()
    if not past_tickets:
        return None

    if not getattr(embedding_manager, "model", None):
        logger.info("Embedding model unavailable; cache similarity lookup skipped.")
        return None

    issue_embedding = embedding_manager.generate_embeddings([issue_text])[0]
    best_match = None
    best_score = 0.0

    for ticket in reversed(past_tickets):
        ticket_subject = str(ticket.get("subject", "")).strip()
        ticket_description = str(ticket.get("description", "")).strip()
        suggested_solution = ticket.get("suggested_solution", [])

        if not isinstance(suggested_solution, list):
            suggested_solution = [str(suggested_solution)]

        solution_text = " ".join(str(item).strip() for item in suggested_solution if str(item).strip())
        candidate_text = " ".join(
            part for part in [ticket_subject, ticket_description, solution_text] if part
        ).strip()

        if not candidate_text:
            continue

        candidate_embedding = embedding_manager.generate_embeddings([candidate_text])[0]
        score = float(cos_sim([issue_embedding], [candidate_embedding])[0][0])

        if score > best_score:
            best_score = score
            best_match = ticket

    if best_match and best_score >= CACHE_SIMILARITY_THRESHOLD:
        logger.info(
            "Cache hit found with semantic similarity %.3f for ticket %s",
            best_score,
            best_match.get("ticket_id", "unknown"),
        )
        return best_match

    logger.info("No cache hit above similarity threshold %.2f", CACHE_SIMILARITY_THRESHOLD)

    return None


def find_similar_tickets(issue_text: str, limit: int = 3) -> List[Dict[str, Any]]:
    past_tickets = memory_manager.get_all_ticket_logs()
    if not past_tickets:
        return []

    if not getattr(embedding_manager, "model", None):
        logger.info("Embedding model unavailable; similar ticket lookup skipped.")
        return []

    issue_embedding = embedding_manager.generate_embeddings([issue_text])[0]
    matches = []
    scored_tickets = []

    for ticket in reversed(past_tickets):
        ticket_subject = str(ticket.get("subject", "")).strip()
        ticket_description = str(ticket.get("description", "")).strip()
        suggested_solution = ticket.get("suggested_solution", [])

        if not isinstance(suggested_solution, list):
            suggested_solution = [str(suggested_solution)]

        solution_text = " ".join(str(item).strip() for item in suggested_solution if str(item).strip())
        candidate_text = " ".join(
            part for part in [ticket_subject, ticket_description, solution_text] if part
        ).strip()

        if not candidate_text:
            continue

        candidate_embedding = embedding_manager.generate_embeddings([candidate_text])[0]
        score = float(cos_sim([issue_embedding], [candidate_embedding])[0][0])

        similar_solution = ticket.get("suggested_solution", [])
        if not isinstance(similar_solution, list):
            similar_solution = [str(similar_solution)]

        candidate = {
            "ticket_id": ticket.get("ticket_id", "unknown"),
            "category": ticket.get("category", ""),
            "priority": ticket.get("priority", ""),
            "assigned_team": ticket.get("assigned_team", ""),
            "score": round(score, 3),
            "suggested_solution": [
                str(item) for item in similar_solution if str(item).strip()
            ],
        }
        scored_tickets.append(candidate)

        if score >= SIMILAR_TICKET_THRESHOLD:
            matches.append(candidate)

    if not matches and scored_tickets:
        matches = scored_tickets

    matches.sort(key=lambda item: item["score"], reverse=True)
    return matches[:limit]


def convert_web_answer_to_steps(answer: str) -> List[str]:
    if not answer or not answer.strip():
        return ["No web search solution was generated."]

    lines = answer.splitlines()
    steps = []

    for line in lines:
        clean_line = line.strip()

        if not clean_line:
            continue

        clean_line = clean_line.lstrip("-").strip()
        clean_line = clean_line.lstrip("*").strip()

        if clean_line and clean_line not in steps:
            steps.append(clean_line)

    if not steps:
        steps.append(answer.strip())

    return steps[:6]


def build_decision_context(
    issue_text: str,
    llm_response: str,
    suggested_solution: List[str],
    retrieved_context: str = ""
) -> str:
    solution_text = "\n".join(f"- {step}" for step in suggested_solution)

    return f"""
Raw User Ticket:
{issue_text}

LLM / RAG Analysis:
{llm_response or "No LLM analysis available."}

Suggested Solution:
{solution_text or "No suggested solution available."}

Retrieved Knowledge Context:
{retrieved_context or "No retrieved context available."}
""".strip()


def calculate_confidence(
    rag_used: bool,
    rag_score: float,
    web_search_used: bool
) -> float:
    if rag_used:
        return round(min(max(float(rag_score), 0.0), 1.0), 2)

    if web_search_used:
        return 0.70

    return 0.50


def build_confidence_reason(rag_used: bool, web_search_used: bool, similar_tickets: List[Dict[str, Any]]) -> str:
    if similar_tickets:
        top = similar_tickets[0]
        return (
            f"Matched a similar historical ticket ({top.get('ticket_id', 'unknown')}) "
            f"with similarity {top.get('score', 0):.2f}."
        )

    if rag_used:
        return "Confidence came from an internal knowledge base match."

    if web_search_used:
        return "Confidence came from the web fallback response."

    return "Confidence was estimated from model routing signals."


def build_clarifying_question(
    confidence: float,
    category: str,
    assigned_team: str,
    similar_tickets: List[Dict[str, Any]]
) -> Optional[str]:
    if confidence >= LOW_CONFIDENCE_THRESHOLD:
        return None

    if similar_tickets:
        top = similar_tickets[0]
        return (
            f"I found a close match to {top.get('ticket_id', 'a past ticket')}. "
            f"Can you confirm whether your issue is similar to that {top.get('category', 'related')} case?"
        )

    if category or assigned_team:
        return (
            f"To confirm the routing, can you share one more detail about the issue before we finalize "
            f"the {category or 'ticket'} assignment to {assigned_team or 'the support team'}?"
        )

    return "Can you share one more detail about the issue so I can route it more accurately?"


def run_ticket_triage(request: TicketRequest) -> TriageResponse:
    audit_trail = []

    ticket_id = f"TICKET-{uuid.uuid4().hex[:8].upper()}"
    audit_trail.append(f"Ticket created with ID: {ticket_id}")

    issue_text = build_issue_text(request)
    cached_ticket = find_cached_ticket(issue_text)

    if cached_ticket:
        cached_audit_trail = cached_ticket.get("audit_trail", [])

        if not isinstance(cached_audit_trail, list):
            cached_audit_trail = [str(cached_audit_trail)]

        cached_audit_trail.append("Returned from cache because a repeated issue was detected.")

        cached_ticket["audit_trail"] = cached_audit_trail

        cached_ticket["guardrail_applied"] = (
            cached_ticket.get("guardrail_applied") is True
            or cached_ticket.get("guardrailApplied") is True
            or any(
                "guardrail applied" in str(item).lower()
                for item in cached_audit_trail
            )
        )

        return TriageResponse(**cached_ticket)

    audit_trail.append("Ticket text prepared successfully.")
    similar_tickets = find_similar_tickets(issue_text)
    if similar_tickets:
        audit_trail.append(
            "Similar historical tickets detected: "
            + ", ".join(
                f"{ticket['ticket_id']} ({ticket['score']:.2f})" for ticket in similar_tickets
            )
        )

    try:
        rag_result = augmentation_manager.build_augmented_context(issue_text)
        audit_trail.append("RAG augmentation executed successfully.")

    except Exception as error:
        rag_result = {
            "rag_used": False,
            "rag_score": 0.0,
            "rag_sources": [],
            "retrieved_context": "",
            "llm_response": "",
            "suggested_solution": [
                "RAG pipeline failed. Web search fallback will be used."
            ]
        }

        audit_trail.append(f"RAG augmentation failed: {str(error)}")

    rag_used = rag_result.get("rag_used", False)
    rag_score = rag_result.get("rag_score", 0.0)
    rag_sources_value = rag_result.get("rag_sources", [])
    if rag_sources_value is None:
        rag_sources = []
    elif isinstance(rag_sources_value, list):
        rag_sources = [str(item) for item in rag_sources_value if str(item).strip()]
    else:
        rag_sources = [str(rag_sources_value)]

    suggested_solution_value = rag_result.get("suggested_solution", [])
    if suggested_solution_value is None:
        suggested_solution = []
    elif isinstance(suggested_solution_value, list):
        suggested_solution = [
            str(item) for item in suggested_solution_value if str(item).strip()
        ]
    else:
        suggested_solution = [str(suggested_solution_value)]
    retrieved_context = rag_result.get("retrieved_context", "")
    llm_response = rag_result.get("llm_response", "")

    web_search_used = False

    audit_trail.append(f"RAG used: {rag_used}")
    audit_trail.append(f"RAG score: {rag_score}")

    if not rag_used:
        audit_trail.append("No strong internal KB match. Using web fallback.")

        web_search_used = True

        try:
            web_result = web_search_fallback(issue_text)

            web_answer = web_result.get(
                "answer",
                "Web search fallback returned no result."
            )

            suggested_solution = convert_web_answer_to_steps(web_answer)
            llm_response = web_answer
            audit_trail.append("Web fallback executed successfully.")

        except Exception as error:
            suggested_solution = [
                "Web fallback failed.",
                "Please review manually.",
                f"Error: {str(error)}"
            ]

            llm_response = "Web fallback failed. Manual review is required."
            audit_trail.append(f"Web fallback failed: {str(error)}")

    decision_context = build_decision_context(
        issue_text=issue_text,
        llm_response=llm_response,
        suggested_solution=suggested_solution,
        retrieved_context=retrieved_context
    )

    category = classify_ticket(decision_context)

    priority = detect_priority(decision_context)

    assigned_team = route_ticket(
        category=category,
        ticket_text=decision_context
    )

    audit_trail.append(f"Ticket category detected as: {category}")
    audit_trail.append(f"Ticket priority detected as: {priority}")
    audit_trail.append(f"Ticket routed to: {assigned_team}")

    guardrail_result = apply_guardrails(
        category=category,
        priority=priority,
        assigned_team=assigned_team,
        ticket_text=decision_context
    )

    category = guardrail_result.get("category", category)
    priority = guardrail_result.get("priority", priority)
    assigned_team = guardrail_result.get("assigned_team", assigned_team)
    guardrail_applied = guardrail_result.get("guardrail_applied", False)
    guardrail_reason = guardrail_result.get("reason")

    if guardrail_result.get("reason"):
        audit_trail.append(guardrail_result["reason"])
    else:
        audit_trail.append(
            "No guardrail triggered. Normal classification, priority, and routing retained."
        )

    if guardrail_result.get("force_human_review"):
        audit_trail.append(
            "Escalated for human review because guardrail detected a high-risk issue."
        )

    audit_trail.append(f"Final category after guardrails: {category}")
    audit_trail.append(f"Final priority after guardrails: {priority}")
    audit_trail.append(f"Final assigned team after guardrails: {assigned_team}")

    confidence = calculate_confidence(
        rag_used=rag_used,
        rag_score=rag_score,
        web_search_used=web_search_used
    )
    confidence_reason = build_confidence_reason(rag_used, web_search_used, similar_tickets)
    clarifying_question = build_clarifying_question(confidence, category, assigned_team, similar_tickets)
    audit_trail.append(f"Final confidence calculated as: {confidence}")
    audit_trail.append(confidence_reason)
    if clarifying_question:
        audit_trail.append(f"Clarifying question generated: {clarifying_question}")

    escalation_required = priority in ["Critical", "High"]
    human_review_required = confidence < LOW_CONFIDENCE_THRESHOLD or guardrail_applied or bool(similar_tickets)
    human_review_reason = None

    if human_review_required:
        if confidence < LOW_CONFIDENCE_THRESHOLD:
            human_review_reason = (
                f"Low confidence ({confidence:.2f}) - recommend human review before final routing."
            )
        elif guardrail_applied:
            human_review_reason = "Guardrail triggered - human review recommended."
        else:
            human_review_reason = "Similar ticket match available - human approval can confirm the route."

        audit_trail.append(human_review_reason)

    sla_result = predict_sla(
        category=category,
        priority=priority,
        assigned_team=assigned_team,
        escalation_required=escalation_required,
        confidence=confidence
    )
    audit_trail.append(sla_result["sla_reason"])

    response = TriageResponse(
        ticket_id=ticket_id,
        category=category,
        confidence=confidence,
        confidence_reason=confidence_reason,
        human_review_required=human_review_required,
        human_review_reason=human_review_reason,
        clarifying_question=clarifying_question,
        priority=priority,
        assigned_team=assigned_team,
        rag_used=rag_used,
        rag_score=rag_score,
        rag_sources=rag_sources,
        web_search_used=web_search_used,
        suggested_solution=suggested_solution,
        similar_tickets=similar_tickets,
        llm_response=llm_response,
        escalation_required=escalation_required,
        sla_target_hours=sla_result.get("sla_target_hours"),
        sla_response_hours=sla_result.get("sla_response_hours"),
        sla_breach_risk=sla_result.get("sla_breach_risk"),
        sla_escalation_required=sla_result.get("sla_escalation_required", False),
        sla_reason=sla_result.get("sla_reason"),
        audit_trail=audit_trail,
        guardrail_applied=guardrail_applied,
        guardrail_reason=guardrail_reason
    )

    memory_manager.save_ticket_log(response.model_dump())

    return response


async def run_ticket_triage_async(request: TicketRequest) -> TriageResponse:
    return await asyncio.to_thread(run_ticket_triage, request)
