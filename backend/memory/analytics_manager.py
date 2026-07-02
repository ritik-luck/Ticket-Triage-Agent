from collections import Counter
from typing import Dict, Any, List

from memory.memory_manager import memory_manager


class AnalyticsManager:
    def get_dashboard_summary(self) -> Dict[str, Any]:
        tickets = memory_manager.get_all_ticket_logs()

        total_tickets = len(tickets)

        category_distribution = self._count_by_field(
            tickets=tickets,
            field_name="category"
        )

        priority_distribution = self._count_by_field(
            tickets=tickets,
            field_name="priority"
        )

        team_distribution = self._count_by_field(
            tickets=tickets,
            field_name="assigned_team"
        )

        rag_web_summary = self._build_rag_web_summary(tickets)

        guardrail_summary = self._build_guardrail_summary(tickets)

        sla_summary = self._build_sla_summary(tickets)

        recent_tickets = self._get_recent_tickets(
            tickets=tickets,
            limit=5
        )

        repeated_issues = self._find_repeated_issues(tickets)

        return {
            "total_tickets": total_tickets,
            "category_distribution": category_distribution,
            "priority_distribution": priority_distribution,
            "team_distribution": team_distribution,
            "rag_web_summary": rag_web_summary,
            "guardrail_summary": guardrail_summary,
            "sla_summary": sla_summary,
            "recent_tickets": recent_tickets,
            "repeated_issues": repeated_issues
        }

    def _count_by_field(
        self,
        tickets: List[Dict[str, Any]],
        field_name: str
    ) -> Dict[str, int]:
        values = []

        for ticket in tickets:
            value = ticket.get(field_name, "Unknown")

            if not value:
                value = "Unknown"

            values.append(value)

        return dict(Counter(values))

    def _build_rag_web_summary(
        self,
        tickets: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        rag_used_count = 0
        web_search_used_count = 0

        for ticket in tickets:
            rag_used = ticket.get("rag_used", False)
            web_search_used = ticket.get("web_search_used", False)

            if rag_used:
                rag_used_count += 1

            if web_search_used:
                web_search_used_count += 1

        return {
            "rag_used": rag_used_count,
            "web_search_used": web_search_used_count
        }

    def _build_guardrail_summary(
        self,
        tickets: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        guardrail_triggered_count = 0
        production_outage_count = 0
        security_incident_count = 0
        data_loss_count = 0

        for ticket in tickets:
            audit_text = self._get_audit_text(ticket)

            guardrail_applied = (
                ticket.get("guardrail_applied") is True
                or ticket.get("guardrailApplied") is True
                or "guardrail applied" in audit_text
            )

            if guardrail_applied:
                guardrail_triggered_count += 1

                if (
                    "production outage" in audit_text
                    or "production down" in audit_text
                    or "production system down" in audit_text
                    or "system down" in audit_text
                    or "multiple users affected" in audit_text
                    or "outage" in audit_text
                ):
                    production_outage_count += 1

                if (
                    "security incident" in audit_text
                    or "security" in audit_text
                    or "phishing" in audit_text
                    or "suspicious login" in audit_text
                    or "account compromised" in audit_text
                ):
                    security_incident_count += 1

                if (
                    "data loss" in audit_text
                    or "deleted data" in audit_text
                    or "missing data" in audit_text
                    or "records missing" in audit_text
                ):
                    data_loss_count += 1

        return {
            "guardrail_triggered": guardrail_triggered_count,
            "production_outage": production_outage_count,
            "security_incident": security_incident_count,
            "data_loss": data_loss_count
        }

    def get_latest_guardrail_reason(
        self,
        tickets: List[Dict[str, Any]]
    ) -> str:
        for ticket in reversed(tickets):
            if ticket.get("guardrail_applied") is not True and ticket.get("guardrailApplied") is not True:
                continue

            reason = (
                ticket.get("guardrail_reason")
                or ticket.get("guardrailReason")
                or self._get_guardrail_reason(ticket)
            )

            if reason:
                return str(reason)

        return "Guardrail triggered, but no description was recorded."

    def _get_guardrail_reason(
        self,
        ticket: Dict[str, Any]
    ) -> str:
        audit_trail = (
            ticket.get("audit_trail")
            or ticket.get("auditTrail")
            or ticket.get("audit")
            or []
        )

        if isinstance(audit_trail, list):
            for item in audit_trail:
                text = str(item).strip()
                if "guardrail" in text.lower():
                    return text

        if audit_trail:
            return str(audit_trail)

        return ""

    def _build_sla_summary(
        self,
        tickets: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        total_with_sla = 0
        high_risk_count = 0
        medium_risk_count = 0
        low_risk_count = 0

        for ticket in tickets:
            if ticket.get("sla_target_hours") is None and ticket.get("slaTargetHours") is None:
                continue

            total_with_sla += 1

            risk = str(
                ticket.get("sla_breach_risk")
                or ticket.get("slaBreachRisk")
                or ""
            ).lower()

            if risk == "high":
                high_risk_count += 1
            elif risk == "medium":
                medium_risk_count += 1
            elif risk == "low":
                low_risk_count += 1

        return {
            "tickets_with_sla": total_with_sla,
            "high_risk": high_risk_count,
            "medium_risk": medium_risk_count,
            "low_risk": low_risk_count,
        }

    def _get_audit_text(
        self,
        ticket: Dict[str, Any]
    ) -> str:
        audit_trail = (
            ticket.get("audit_trail")
            or ticket.get("auditTrail")
            or ticket.get("audit")
            or []
        )

        if isinstance(audit_trail, list):
            return " ".join(str(item) for item in audit_trail).lower()

        return str(audit_trail).lower()

    def _get_recent_tickets(
        self,
        tickets: List[Dict[str, Any]],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        recent_tickets = tickets[-limit:]

        return list(reversed(recent_tickets))

    def _find_repeated_issues(
        self,
        tickets: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        category_counts = self._count_by_field(
            tickets=tickets,
            field_name="category"
        )

        repeated_issues = {
            category: count
            for category, count in category_counts.items()
            if count > 1
        }

        return repeated_issues


analytics_manager = AnalyticsManager()
