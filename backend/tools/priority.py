import json
from typing import Any, Dict, Optional
from llm.groq import generate_response

threshold= 0.70

def _keyword_detect_priority(ticket_text: str) -> Dict[str, Any]:
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
        return {"priority": "Critical", "confidence": 1.0, "source": "rule_based_fallback"}

    if any(keyword in text for keyword in high_keywords):
        return {"priority": "High", "confidence": 1.0, "source": "rule_based_fallback"}

    if any(keyword in text for keyword in medium_keywords):
        return {"priority": "Medium", "confidence": 1.0, "source": "rule_based_fallback"}

    if any(keyword in text for keyword in low_keywords):
        return {"priority": "Low", "confidence": 1.0, "source": "rule_based_fallback"}

    return {"priority": "Low", "confidence": 0.5, "source": "rule_based_fallback"}


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


def _build_priority_prompt(ticket_text: str) -> str:
    return f"""
You are an IT ticket priority classifier.
Return ONLY valid JSON with these keys:
{{
  "priority": "one of: Critical, High, Medium, Low",
  "confidence": number between 0 and 1,
  "reason": "short explanation"
}}

Ticket text:
{ticket_text}

Assign the priority based on business impact, urgency, and affected users.
""".strip()


def _normalize_priority_result(
    result: Dict[str, Any],
    fallback_priority: str
) -> Dict[str, Any]:
    confidence = float(result.get("confidence", 0.0) or 0.0)
    if confidence < 0.0:
        confidence = 0.0
    if confidence > 1.0:
        confidence = 1.0

    return {
        "priority": str(result.get("priority") or fallback_priority),
        "confidence": confidence,
        "reason": result.get("reason"),
        "source": "llm",
    }


def detect_priority(ticket_text: str) -> str:
    prompt = _build_priority_prompt(ticket_text)

    try:
        llm_output = generate_response(prompt)
        parsed = _parse_llm_json(llm_output)

        if not parsed:
            return _keyword_detect_priority(ticket_text)["priority"]

        fallback = _keyword_detect_priority(ticket_text)
        normalized = _normalize_priority_result(parsed, fallback["priority"])

        if normalized["confidence"] < threshold:
            return fallback["priority"]

        return normalized["priority"]

    except Exception:
        return _keyword_detect_priority(ticket_text)["priority"]
