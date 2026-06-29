def generate_final_response(ticket_text: str,category: str,priority: str,assigned_team: str,escalation_required: bool,rag_context: str = "",fallback_response: str = "") -> dict:
    
    recommended_action = generate_recommended_action(priority=priority,assigned_team=assigned_team,escalation_required=escalation_required)

    return {
        "ticket": ticket_text,
        "category": category,
        "priority": priority,
        "assigned_team": assigned_team,
        "escalation_required": escalation_required,
        "rag_context_used": rag_context,
        "fallback_response": fallback_response,
        "recommended_action": recommended_action
    }


def generate_recommended_action(priority: str,assigned_team: str,escalation_required: bool) -> str:

    if escalation_required:
        return f"Immediately assign this ticket to {assigned_team} and notify the escalation owner."

    if priority == "Medium":
        return f"Assign this ticket to {assigned_team} for standard investigation and resolution."

    if priority == "Low":
        return f"Add this ticket to the {assigned_team} backlog and handle as per normal SLA."

    return f"Assign this ticket to {assigned_team} for further analysis."