from typing import Dict, Any


def _clamp_hours(hours: float) -> float:
    return round(max(hours, 1.0), 1)


def predict_sla(
    category: str,
    priority: str,
    assigned_team: str,
    escalation_required: bool,
    confidence: float
) -> Dict[str, Any]:
    priority_hours = {
        "Critical": 2.0,
        "High": 8.0,
        "Medium": 24.0,
        "Low": 72.0,
    }

    team_multiplier = 1.0

    if assigned_team in ["Incident Response Team", "Security / IAM Team", "Data Support Team"]:
        team_multiplier = 0.8
    elif assigned_team in ["Backend Team", "DevOps Team", "Network Operations Team"]:
        team_multiplier = 0.9
    elif assigned_team in ["Service Desk Team", "General Support Team"]:
        team_multiplier = 1.1

    base_hours = priority_hours.get(priority, 24.0)

    if category in ["Production Outage", "Security Incident", "Data Loss Incident"]:
        base_hours = min(base_hours, 4.0)

    if escalation_required:
        base_hours *= 0.75

    base_hours *= team_multiplier

    predicted_resolution_hours = _clamp_hours(base_hours)
    predicted_response_hours = _clamp_hours(max(predicted_resolution_hours * 0.25, 1.0))

    if priority == "Critical" or predicted_resolution_hours <= 2.0:
        risk = "High"
    elif predicted_resolution_hours <= 8.0:
        risk = "Medium"
    else:
        risk = "Low"

    if confidence < 0.65 and risk != "High":
        risk = "Medium" if risk == "Low" else risk

    return {
        "sla_target_hours": predicted_resolution_hours,
        "sla_response_hours": predicted_response_hours,
        "sla_breach_risk": risk,
        "sla_escalation_required": risk == "High" or escalation_required,
        "sla_reason": _build_sla_reason(
            category=category,
            priority=priority,
            assigned_team=assigned_team,
            escalation_required=escalation_required,
            confidence=confidence,
            predicted_resolution_hours=predicted_resolution_hours,
            risk=risk,
        ),
    }


def _build_sla_reason(
    category: str,
    priority: str,
    assigned_team: str,
    escalation_required: bool,
    confidence: float,
    predicted_resolution_hours: float,
    risk: str
) -> str:
    escalation_text = "Escalation is already required." if escalation_required else "No immediate escalation flag."

    return (
        f"SLA predicted at {predicted_resolution_hours} hours for {priority} "
        f"{category} assigned to {assigned_team}. Risk is {risk}. "
        f"Confidence: {confidence:.2f}. {escalation_text}"
    )
