import json
from typing import Any, Dict, Optional
from llm.groq import generate_response

threshold = 0.70

def _keyword_classify_ticket(ticket_text: str) -> Dict[str, Any]:
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
        return {"category": "Production Outage", "confidence": 1.0, "source": "rule_based_fallback"}

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
        return {"category": "Security Incident", "confidence": 1.0, "source": "rule_based_fallback"}

    if any(keyword in text for keyword in [
        "project allocation",
        "no project allocation",
        "no project allocated",
        "not assigned to any project",
        "unassigned",
        "bench",
        "allocation",
        "assigned project",
    ]):
        return {"category": "Service Request", "confidence": 1.0, "source": "rule_based_fallback"}

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
        return {"category": "Access Issue", "confidence": 1.0, "source": "rule_based_fallback"}

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
        return {"category": "Network Issue", "confidence": 1.0, "source": "rule_based_fallback"}

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
        return {"category": "Hardware Issue", "confidence": 1.0, "source": "rule_based_fallback"}

    if any(keyword in text for keyword in [
        "laptop slow",
        "system slow",
        "freeze",
        "hang",
        "device slow",
        "cpu",
        "memory"
    ]):
        return {"category": "Desktop Issue", "confidence": 1.0, "source": "rule_based_fallback"}

    if any(keyword in text for keyword in [
        "outlook",
        "mailbox",
        "email not sending",
        "email not receiving",
        "mail stuck",
        "attachment",
        "outbox"
    ]):
        return {"category": "Email Issue", "confidence": 1.0, "source": "rule_based_fallback"}

    if any(keyword in text for keyword in [
        "software installation",
        "install software",
        "license",
        "new software",
        "software request"
    ]):
        return {"category": "Software Request", "confidence": 1.0, "source": "rule_based_fallback"}

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
        return {"category": "Bug", "confidence": 1.0, "source": "rule_based_fallback"}

    if any(keyword in text for keyword in [
        "slow",
        "timeout",
        "performance",
        "delay",
        "loading"
    ]):
        return {"category": "Performance Issue", "confidence": 1.0, "source": "rule_based_fallback"}

    if any(keyword in text for keyword in [
        "invoice",
        "payment",
        "billing",
        "refund",
        "charge"
    ]):
        return {"category": "Billing Issue", "confidence": 1.0, "source": "rule_based_fallback"}

    if any(keyword in text for keyword in [
        "feature",
        "enhancement",
        "improvement",
        "request",
        "new functionality"
    ]):
        return {"category": "Feature Request", "confidence": 1.0, "source": "rule_based_fallback"}

    return {"category": "General Support", "confidence": 0.5, "source": "rule_based_fallback"}


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


def _build_classification_prompt(ticket_text: str) -> str:
    return f"""
You are an IT ticket classifier.
Return ONLY valid JSON with these keys:
{{
  "category": "one of: Production Outage, Security Incident, Access Issue, Network Issue, Hardware Issue, Desktop Issue, Email Issue, Software Request, Bug, Performance Issue, Billing Issue, Feature Request, General Support",
  "confidence": number between 0 and 1,
  "reason": "short explanation"
}}

Ticket text:
{ticket_text}

Use the category that best matches the issue description.
""".strip()


def _normalize_classification_result(
    result: Dict[str, Any],
    fallback_category: str
) -> Dict[str, Any]:
    confidence = float(result.get("confidence", 0.0) or 0.0)
    if confidence < 0.0:
        confidence = 0.0
    if confidence > 1.0:
        confidence = 1.0

    return {
        "category": str(result.get("category") or fallback_category),
        "confidence": confidence,
        "reason": result.get("reason"),
        "source": "llm",
    }


def classify_ticket(ticket_text: str) -> str:
    prompt = _build_classification_prompt(ticket_text)

    try:
        llm_output = generate_response(prompt)
        parsed = _parse_llm_json(llm_output)

        if not parsed:
            return _keyword_classify_ticket(ticket_text)["category"]

        fallback = _keyword_classify_ticket(ticket_text)
        normalized = _normalize_classification_result(parsed, fallback["category"])

        if normalized["confidence"] < threshold:
            return fallback["category"]

        return normalized["category"]

    except Exception:
        return _keyword_classify_ticket(ticket_text)["category"]
