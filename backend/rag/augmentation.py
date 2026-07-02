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
                    "No strong internal knowledge base match was found.",
                    "Please review the ticket manually or use web search fallback."
                ]
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

Generate:
- Issue summary
- Troubleshooting steps
- Escalation condition
"""

    def _convert_response_to_steps(self, response_text: str):
        steps = []

        for line in response_text.splitlines():
            clean = line.strip().lstrip("-*").strip()

            if clean and clean not in steps:
                steps.append(clean)

        if not steps:
            steps.append("No clear steps extracted.")

        return steps[:6]


augmentation_manager = AugmentationManager()