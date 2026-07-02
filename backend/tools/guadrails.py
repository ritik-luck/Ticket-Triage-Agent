import json
from typing import Any, Dict, Optional
from llm.groq import generate_response

threshold= 0.70

def _keyword_guardrail_fallback(
    category: str,
    priority: str,
    assigned_team: str,
    ticket_text: str
) -> Dict[str, Any]:
    text = ticket_text.lower()

    escalation = {
        "category": category,
        "priority": priority,
        "assigned_team": assigned_team,
        "guardrail_applied": False,
        "force_human_review": False,
        "reason": None,
        "confidence": 0.0,
        "source": "rule_based_fallback",
    }

    security_keywords = [
        "phishing",
        "malware",
        "breach",
        "hacked",
        "data leak",
        "suspicious login",
        "suspicious email",
        "account compromised",
        "compromised account",
        "credentials stolen",
        "password exposed",
        "unauthorized access",
        "security incident",
    ]

    outage_keywords = [
        "system down",
        "production down",
        "production system down",
        "application down",
        "service unavailable",
        "outage",
        "major outage",
        "all users affected",
        "multiple users affected",
        "many users affected",
        "business critical outage",
    ]

    data_loss_keywords = [
        "data loss",
        "deleted data",
        "missing data",
        "records missing",
        "database corrupted",
        "lost files",
        "file deleted",
    ]

    if any(keyword in text for keyword in security_keywords):
        escalation.update(
            category="Security Incident",
            priority="Critical",
            assigned_team="Security / IAM Team",
            guardrail_applied=True,
            force_human_review=True,
            reason=(
                "Guardrail applied by fallback rule: Security incident detected. "
                "Priority changed to Critical and ticket routed to Security / IAM Team."
            ),
            confidence=1.0,
        )
        return escalation

    if any(keyword in text for keyword in outage_keywords):
        escalation.update(
            category="Production Outage",
            priority="Critical",
            assigned_team="Incident Response Team",
            guardrail_applied=True,
            force_human_review=True,
            reason=(
                "Guardrail applied by fallback rule: Production outage detected. "
                "Priority changed to Critical and ticket routed to Incident Response Team."
            ),
            confidence=1.0,
        )
        return escalation

    if any(keyword in text for keyword in data_loss_keywords):
        escalation.update(
            category="Data Loss Incident",
            priority="High",
            assigned_team="Data Support Team",
            guardrail_applied=True,
            force_human_review=True,
            reason=(
                "Guardrail applied by fallback rule: Data loss signal detected. "
                "Priority changed to High and ticket routed to Data Support Team."
            ),
            confidence=1.0,
        )
        return escalation

    return escalation


def _parse_llm_json(raw_text: str) -> Optional[Dict[str, Any]]:
    if not raw_text:
        return None

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        start = raw_text.find("{")
        end = raw_text.rfind("}")

        if start == -1 or end == -1 or end <= start:
            return None

        try:
            return json.loads(raw_text[start : end + 1])
        except json.JSONDecodeError:
            return None


def _build_guardrail_prompt(
    category: str,
    priority: str,
    assigned_team: str,
    ticket_text: str
) -> str:
    return f"""
You are a guardrail classifier for an IT ticket triage system.
Decide whether this ticket should be escalated to a stricter category, priority, or team.
Return ONLY valid JSON with these keys:
{{
  "guardrail_applied": true or false,
  "force_human_review": true or false,
  "confidence": number between 0 and 1,
  "category": "string",
  "priority": "string",
  "assigned_team": "string",
  "reason": "short explanation"
}}

Current triage values:
- category: {category}
- priority: {priority}
- assigned_team: {assigned_team}

Ticket text:
{ticket_text}

Only apply a guardrail when the ticket clearly indicates a high-risk issue such as production, security, outage, or data loss.
If you do not need to change anything, return the current values and set guardrail_applied to false.
""".strip()


def _normalize_llm_result(
    result: Dict[str, Any],
    category: str,
    priority: str,
    assigned_team: str
) -> Dict[str, Any]:
    normalized = {
        "category": str(result.get("category") or category),
        "priority": str(result.get("priority") or priority),
        "assigned_team": str(result.get("assigned_team") or assigned_team),
        "guardrail_applied": bool(result.get("guardrail_applied", False)),
        "force_human_review": bool(result.get("force_human_review", False)),
        "reason": result.get("reason"),
        "confidence": float(result.get("confidence", 0.0) or 0.0),
        "source": "llm",
    }

    if normalized["confidence"] < 0.0:
        normalized["confidence"] = 0.0
    if normalized["confidence"] > 1.0:
        normalized["confidence"] = 1.0

    return normalized


def apply_guardrails(
    category: str,
    priority: str,
    assigned_team: str,
    ticket_text: str
) -> Dict[str, Any]:
    prompt = _build_guardrail_prompt(
        category=category,
        priority=priority,
        assigned_team=assigned_team,
        ticket_text=ticket_text
    )

    try:
        llm_output = generate_response(prompt)
        parsed = _parse_llm_json(llm_output)

        if not parsed:
            return _keyword_guardrail_fallback(
                category=category,
                priority=priority,
                assigned_team=assigned_team,
                ticket_text=ticket_text
            )

        normalized = _normalize_llm_result(
            parsed,
            category=category,
            priority=priority,
            assigned_team=assigned_team
        )

        if normalized["confidence"] < threshold:
            fallback = _keyword_guardrail_fallback(
                category=category,
                priority=priority,
                assigned_team=assigned_team,
                ticket_text=ticket_text
            )

            if fallback["guardrail_applied"]:
                fallback["reason"] = (
                    f"{fallback['reason']} LLM confidence was below threshold "
                    f"({normalized['confidence']:.2f} < {threshold:.2f})."
                )
                fallback["source"] = "rule_based_fallback_after_low_confidence_llm"
                fallback["confidence"] = normalized["confidence"]
                return fallback

            return {
                "category": category,
                "priority": priority,
                "assigned_team": assigned_team,
                "guardrail_applied": False,
                "force_human_review": False,
                "reason": (
                    "LLM guardrail confidence was below threshold and no fallback rule matched."
                ),
                "confidence": normalized["confidence"],
                "source": "llm_below_threshold",
            }

        if not normalized["guardrail_applied"]:
            normalized["reason"] = (
                normalized.get("reason")
                or "LLM guardrail checked the ticket and no escalation was required."
            )

        return normalized

    except Exception as error:
        fallback = _keyword_guardrail_fallback(
            category=category,
            priority=priority,
            assigned_team=assigned_team,
            ticket_text=ticket_text
        )

        fallback["reason"] = (
            f"{fallback['reason'] + ' ' if fallback['reason'] else ''}"
            f"LLM guardrail failed, so fallback rules were used: {str(error)}"
        ).strip()
        fallback["source"] = "rule_based_fallback_after_llm_error"
        return fallback
