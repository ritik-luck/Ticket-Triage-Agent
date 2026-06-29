def detect_priority(ticket_text: str) -> str:
    text = ticket_text.lower()

    critical_keywords = [
        "production down",
        "production system down",
        "system down",
        "application down",
        "service unavailable",
        "complete outage",
        "major outage",
        "outage",
        "all users affected",
        "multiple users affected",
        "many users affected",
        "business critical outage",
        "business critical",
        "nobody can access",
        "cannot access the application",
        "complete impacted",
        "complete impact"
    ]

    high_keywords = [
        "data loss",
        "deleted data",
        "missing data",
        "records missing",
        "database corrupted",
        "security breach",
        "account compromised",
        "credentials stolen",
        "password exposed",
        "phishing",
        "malware",
        "suspicious login",
        "unauthorized access",
        "blocked",
        "all users blocked",
        "major issue",
        "client delivery blocked",
        "not able to work",
        "work blocked",
        "cannot login",
        "unable to login",
        "vpn not working",
        "authentication failed"
    ]

    medium_keywords = [
        "not working",
        "failed",
        "failure",
        "error",
        "issue",
        "problem",
        "delay",
        "slow",
        "timeout",
        "performance",
        "intermittent",
        "unable to access",
        "not connecting"
    ]

    low_keywords = [
        "request",
        "information",
        "how to",
        "need help",
        "question",
        "minor",
        "low impact"
    ]

    if any(keyword in text for keyword in critical_keywords):
        return "Critical"

    if any(keyword in text for keyword in high_keywords):
        return "High"

    if any(keyword in text for keyword in medium_keywords):
        return "Medium"

    if any(keyword in text for keyword in low_keywords):
        return "Low"

    return "Low"


def is_escalation_required(priority: str, ticket_text: str) -> bool:
    text = ticket_text.lower()

    escalation_keywords = [
        "production down",
        "production system down",
        "system down",
        "application down",
        "service unavailable",
        "complete outage",
        "major outage",
        "outage",
        "all users affected",
        "multiple users affected",
        "many users affected",
        "business critical outage",
        "security breach",
        "security incident",
        "phishing",
        "malware",
        "suspicious login",
        "account compromised",
        "credentials stolen",
        "unauthorized access",
        "data loss",
        "deleted data",
        "missing data",
        "database corrupted"
    ]

    if priority in ["Critical", "High"]:
        return True

    if any(keyword in text for keyword in escalation_keywords):
        return True

    return False