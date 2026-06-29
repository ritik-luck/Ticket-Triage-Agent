def classify_ticket(ticket_text: str) -> str:
    text = ticket_text.lower()

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
        return "Production Outage"

    if any(keyword in text for keyword in [
        "phishing",
        "malware",
        "suspicious login",
        "suspicious email",
        "breach",
        "data leak",
        "credential compromise",
        "credentials stolen",
        "account compromised",
        "compromised account",
        "password exposed",
        "unauthorized access",
        "security incident",
        "hacked"
    ]):
        return "Security Incident"

    if any(keyword in text for keyword in [
        "login",
        "password",
        "access",
        "permission",
        "authentication",
        "account locked",
        "mfa",
        "unable to login",
        "cannot login"
    ]):
        return "Access Issue"

    if any(keyword in text for keyword in [
        "vpn",
        "wifi",
        "network",
        "internet",
        "connectivity",
        "latency",
        "connection",
        "not connecting"
    ]):
        return "Network Issue"

    if any(keyword in text for keyword in [
        "monitor",
        "keyboard",
        "mouse",
        "printer",
        "screen",
        "display",
        "hdmi",
        "laptop",
        "desktop",
        "hardware",
        "charger"
    ]):
        return "Hardware Issue"

    if any(keyword in text for keyword in [
        "laptop slow",
        "system slow",
        "freeze",
        "hang",
        "device slow",
        "cpu",
        "memory"
    ]):
        return "Desktop Issue"

    if any(keyword in text for keyword in [
        "outlook",
        "mailbox",
        "email not sending",
        "email not receiving",
        "mail stuck",
        "attachment",
        "outbox"
    ]):
        return "Email Issue"

    if any(keyword in text for keyword in [
        "software installation",
        "install software",
        "license",
        "new software",
        "software request"
    ]):
        return "Software Request"

    if any(keyword in text for keyword in [
        "api",
        "database",
        "server",
        "backend",
        "endpoint",
        "exception",
        "crash",
        "error",
        "failed",
        "not working"
    ]):
        return "Bug"

    if any(keyword in text for keyword in [
        "slow",
        "timeout",
        "performance",
        "delay",
        "loading"
    ]):
        return "Performance Issue"

    if any(keyword in text for keyword in [
        "invoice",
        "payment",
        "billing",
        "refund",
        "charge"
    ]):
        return "Billing Issue"

    if any(keyword in text for keyword in [
        "feature",
        "enhancement",
        "improvement",
        "request",
        "new functionality"
    ]):
        return "Feature Request"

    return "General Support"