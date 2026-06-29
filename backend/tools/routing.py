def route_ticket(category: str, ticket_text: str) -> str:
    text = ticket_text.lower()
    category = category.strip()

    if category == "Production Outage":
        return "Incident Response Team"

    if category == "Security Incident":
        return "Security / IAM Team"

    if category == "Data Loss Incident":
        return "Data Support Team"

    if category == "Access Issue":
        return "Security / IAM Team"

    if category == "Network Issue":
        return "Network Operations Team"

    if category == "Email Issue":
        return "Messaging / Email Support Team"

    if category == "Hardware Issue":
        return "Desktop Support Team"

    if category == "Desktop Issue":
        return "Desktop Support Team"

    if category == "Software Request":
        return "Software Support Team"

    if category == "Service Request":
        if any(keyword in text for keyword in [
            "software",
            "install",
            "installation",
            "license",
            "new software"
        ]):
            return "Software Support Team"

        if any(keyword in text for keyword in [
            "access",
            "permission",
            "role",
            "account",
            "login",
            "password",
            "mfa"
        ]):
            return "Security / IAM Team"

        return "Service Desk Team"

    if category == "Bug":
        if any(keyword in text for keyword in [
            "api",
            "database",
            "server",
            "backend",
            "endpoint"
        ]):
            return "Backend Team"

        if any(keyword in text for keyword in [
            "ui",
            "button",
            "page",
            "frontend",
            "screen",
            "form"
        ]):
            return "Frontend Team"

        if any(keyword in text for keyword in [
            "monitor",
            "keyboard",
            "mouse",
            "printer",
            "display",
            "hdmi",
            "hardware"
        ]):
            return "Desktop Support Team"

        return "Application Support Team"

    if category == "Performance Issue":
        if any(keyword in text for keyword in [
            "laptop",
            "system slow",
            "browser",
            "freeze",
            "hang",
            "device slow"
        ]):
            return "Desktop Support Team"

        if any(keyword in text for keyword in [
            "server",
            "cpu",
            "memory",
            "infrastructure",
            "deployment"
        ]):
            return "DevOps Team"

        if any(keyword in text for keyword in [
            "api",
            "database",
            "backend",
            "endpoint"
        ]):
            return "Backend Team"

        return "Application Support Team"

    if category == "Billing Issue":
        return "Billing Support Team"

    if category == "Feature Request":
        return "Product Team"

    if any(keyword in text for keyword in [
        "production down",
        "production system down",
        "system down",
        "application down",
        "service unavailable",
        "outage",
        "major outage",
        "all users affected",
        "multiple users affected",
        "many users affected",
        "business critical outage"
    ]):
        return "Incident Response Team"

    if any(keyword in text for keyword in [
        "phishing",
        "malware",
        "suspicious login",
        "suspicious email",
        "security",
        "breach",
        "data leak",
        "account compromised",
        "credentials stolen",
        "unauthorized access"
    ]):
        return "Security / IAM Team"

    if any(keyword in text for keyword in [
        "data loss",
        "deleted data",
        "missing data",
        "records missing",
        "database corrupted",
        "lost files",
        "file deleted"
    ]):
        return "Data Support Team"

    if any(keyword in text for keyword in [
        "vpn",
        "network",
        "wifi",
        "internet",
        "connectivity",
        "not connecting"
    ]):
        return "Network Operations Team"

    if any(keyword in text for keyword in [
        "outlook",
        "mailbox",
        "email not sending",
        "email not receiving",
        "outbox",
        "mail stuck",
        "attachment"
    ]):
        return "Messaging / Email Support Team"

    if any(keyword in text for keyword in [
        "monitor",
        "keyboard",
        "mouse",
        "printer",
        "display",
        "screen",
        "hdmi",
        "hardware",
        "laptop",
        "desktop",
        "charger"
    ]):
        return "Desktop Support Team"

    if any(keyword in text for keyword in [
        "software",
        "install",
        "installation",
        "license",
        "new software"
    ]):
        return "Software Support Team"

    return "General Support Team"