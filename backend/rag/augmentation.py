import os
from typing import List, Dict
from dotenv import load_dotenv

from rag.retreiver import retriever
from llm.groq import generate_response

load_dotenv()


class AugmentationManager:
    def __init__(self, minimum_score: float = 0.50):
        self.minimum_score = minimum_score

    def build_augmented_context(self, ticket_text: str):
        if not ticket_text or not ticket_text.strip():
            raise ValueError("Ticket text cannot be empty.")

        retrieval_result = retriever.retrieve(ticket_text)

        retrieved_chunks = retrieval_result["retrieved_chunks"]
        sources = retrieval_result["sources"]
        best_score = retrieval_result["best_score"]

        if not retrieved_chunks or best_score < self.minimum_score:
            return {
                "rag_used": False,
                "rag_score": best_score,
                "rag_sources": sources,
                "retrieved_context": "",
                "llm_response": "No strong internal knowledge base match was found.",
                "suggested_solution": [
                    "Review the request with the responsible team or manager.",
                    "Check whether the user has the correct allocation, access, or assignment records.",
                    "Escalate to the appropriate support owner if the assignment still cannot be confirmed.",
                ],
            }

        retrieved_context = self._format_retrieved_context(retrieved_chunks)

        prompt = self._build_prompt(
            ticket_text=ticket_text,
            retrieved_context=retrieved_context
        )

        print("Generating RAG answer using LLM...")
        response_text = generate_response(prompt)

        suggested_solution = self._convert_response_to_steps(response_text)

        return {
            "rag_used": True,
            "rag_score": best_score,
            "rag_sources": sources,
            "retrieved_context": retrieved_context,
            "llm_response": response_text,
            "suggested_solution": suggested_solution
        }

    def _format_retrieved_context(self, retrieved_chunks: List[Dict]):
        context_parts = []

        for chunk in retrieved_chunks:
            context_parts.append(
                f"Source: {chunk['source']}\n"
                f"Chunk ID: {chunk['chunk_id']}\n"
                f"Score: {chunk['score']}\n"
                f"Content:\n{chunk['text']}"
            )

        return "\n\n---\n\n".join(context_parts)

    def _build_prompt(self, ticket_text: str, retrieved_context: str):
        return f"""
You are an AI IT Helpdesk Ticket Triage Assistant.
Use ONLY the internal knowledge base below.

User Ticket:
{ticket_text}
Context:
{retrieved_context}

Return a concise support answer with this exact structure:
Issue Summary:
Likely Cause:
Troubleshooting Steps:
1.
2.
3.
Escalation Condition:

Rules:
- Every troubleshooting step must be a concrete action the user can take.
- Use at least 3 steps when possible.
- If the issue is access-related, include steps for checking permissions, account state, and ownership/team assignment.
- If the issue is not clearly solvable, say that clearly and include a handoff/escalation step.
""".strip()


    def _convert_response_to_steps(self, response_text: str):
        steps = []
        current_section = ""

        for line in response_text.splitlines():
            clean = line.strip()

            if not clean:
                continue

            lowered = clean.lower()
            if lowered.startswith("issue summary:"):
                current_section = "summary"
                continue
            if lowered.startswith("likely cause:"):
                current_section = "cause"
                continue
            if lowered.startswith("troubleshooting steps:") or lowered.startswith("steps:"):
                current_section = "steps"
                continue
            if lowered.startswith("escalation condition:") or lowered.startswith("escalation:"):
                current_section = "escalation"
                continue

            clean = clean.lstrip("-*").strip()
            if len(clean) > 1 and clean[0].isdigit() and clean[1] == ".":
                clean = clean[2:].strip()

            if current_section in ["summary", "cause"]:
                continue

            if clean and clean not in steps:
                steps.append(clean)

        if not steps:
            steps.extend([
                "Review the account, assignment, and permission records.",
                "Confirm the request with the relevant manager or team owner.",
                "Escalate to the appropriate support team if allocation is still missing.",
            ])

        return steps[:6]


augmentation_manager = AugmentationManager()
