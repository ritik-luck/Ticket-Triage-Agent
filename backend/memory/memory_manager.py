import json
from pathlib import Path
from typing import Dict, List, Any, Optional

MEMORY_DIR = Path("memory")
TICKET_LOG_FILE = MEMORY_DIR / "ticket_logs.json"


class MemoryManager:
    def __init__(self):
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        self._initialize_log_file()

    def _initialize_log_file(self) -> None:
        if not TICKET_LOG_FILE.exists():
            with open(TICKET_LOG_FILE, "w", encoding="utf-8") as file:
                json.dump([], file, indent=4)

    def save_ticket_log(self, ticket_response: Dict[str, Any]) -> None:
        logs = self.get_all_ticket_logs()

        normalized_ticket = self._normalize_ticket_log(ticket_response)

        logs.append(normalized_ticket)

        with open(TICKET_LOG_FILE, "w", encoding="utf-8") as file:
            json.dump(logs, file, indent=4, ensure_ascii=False)

    def get_all_ticket_logs(self) -> List[Dict[str, Any]]:
        try:
            with open(TICKET_LOG_FILE, "r", encoding="utf-8") as file:
                logs = json.load(file)

            if isinstance(logs, list):
                return logs

            return []

        except Exception:
            return []

    def get_ticket_by_id(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        logs = self.get_all_ticket_logs()

        for ticket in logs:
            if ticket.get("ticket_id") == ticket_id:
                return ticket

        return None

    def clear_memory(self) -> None:
        with open(TICKET_LOG_FILE, "w", encoding="utf-8") as file:
            json.dump([], file, indent=4)

    def _normalize_ticket_log(self, ticket_response: Dict[str, Any]) -> Dict[str, Any]:
        ticket = dict(ticket_response)

        audit_trail = (
            ticket.get("audit_trail")
            or ticket.get("auditTrail")
            or ticket.get("audit")
            or []
        )

        if audit_trail is None:
            audit_trail = []

        if not isinstance(audit_trail, list):
            audit_trail = [str(audit_trail)]

        ticket["audit_trail"] = audit_trail

        audit_text = " ".join(str(item) for item in audit_trail).lower()

        guardrail_applied = (
            ticket.get("guardrail_applied") is True
            or ticket.get("guardrailApplied") is True
            or "guardrail applied" in audit_text
        )

        ticket["guardrail_applied"] = guardrail_applied
        ticket["guardrail_reason"] = (
            ticket.get("guardrail_reason")
            or ticket.get("guardrailReason")
            or self._extract_guardrail_reason(audit_trail)
        )

        return ticket

    def _extract_guardrail_reason(self, audit_trail: List[str]) -> Optional[str]:
        if not audit_trail:
            return None

        for item in audit_trail:
            text = str(item).strip()
            if "guardrail" in text.lower():
                return text

        return None


memory_manager = MemoryManager()
