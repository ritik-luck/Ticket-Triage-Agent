from llm.groq import generate_response

def web_search_fallback(ticket_text: str) -> dict:
    prompt = f"""
You are an IT support assistant.
The internal knowledge base did not match this ticket.
Provide practical troubleshooting guidance that is specific, actionable, and not vague.

Ticket:
{ticket_text}

Return:
Issue Understanding:
Likely Cause:
Steps:
1.
2.
3.
Escalation:

Rules:
- Steps must be concrete actions, not generic advice.
- Include permission/account/team checks when the issue mentions assignment or access.
- If the user is asking about allocation or assignment, suggest checking manager/HR/project-owner assignment records.
"""

    response_text = generate_response(prompt)

    return {
        "source": "llm_fallback",
        "ticket": ticket_text,
        "answer": response_text,
        "search_queries": [],
        "source_pages": []
    }
