from llm.groq import generate_response

def should_use_web_search(best_score: float, minimum_score: float) -> bool:
    return best_score <= minimum_score

def web_search_fallback(ticket_text: str) -> dict:
    prompt = f"""
You are an IT support assistant.
The internal knowledge base did not match this ticket.
Provide general troubleshooting guidance.

Ticket:
{ticket_text}

Return:
Issue Understanding:
Likely Cause:
Steps:
Escalation:
"""

    response_text = generate_response(prompt)

    return {
        "source": "llm_fallback",
        "ticket": ticket_text,
        "answer": response_text,
        "search_queries": [],
        "source_pages": []
    }
