def apply_guardrails(
    category: str,
    priority: str,
    assigned_team: str,
    ticket_text: str
):
    text = ticket_text.lower()

    escalation = {
        "category": category,
        "priority": priority,
        "assigned_team": assigned_team,
        "guardrail_applied": False,
        "force_human_review": False,
        "reason": None
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
        "security incident"
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
        "business critical outage"
    ]

    data_loss_keywords = [
        "data loss",
        "deleted data",
        "missing data",
        "records missing",
        "database corrupted",
        "lost files",
        "file deleted"
    ]

    if any(keyword in text for keyword in security_keywords):
        escalation["category"] = "Security Incident"
        escalation["priority"] = "Critical"
        escalation["assigned_team"] = "Security / IAM Team"
        escalation["guardrail_applied"] = True
        escalation["force_human_review"] = True
        escalation["reason"] = (
            "Guardrail applied: Security incident detected. "
            "Priority changed to Critical and ticket routed to Security / IAM Team."
        )
        return escalation

    if any(keyword in text for keyword in outage_keywords):
        escalation["category"] = "Production Outage"
        escalation["priority"] = "Critical"
        escalation["assigned_team"] = "Incident Response Team"
        escalation["guardrail_applied"] = True
        escalation["force_human_review"] = True
        escalation["reason"] = (
            "Guardrail applied: Production outage detected. "
            "Priority changed to Critical and ticket routed to Incident Response Team."
        )
        return escalation

    if any(keyword in text for keyword in data_loss_keywords):
        escalation["category"] = "Data Loss Incident"
        escalation["priority"] = "High"
        escalation["assigned_team"] = "Data Support Team"
        escalation["guardrail_applied"] = True
        escalation["force_human_review"] = True
        escalation["reason"] = (
            "Guardrail applied: Data loss signal detected. "
            "Priority changed to High and ticket routed to Data Support Team."
        )
        return escalation

    return escalation