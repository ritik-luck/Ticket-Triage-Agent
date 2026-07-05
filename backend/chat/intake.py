import uuid
from typing import Dict, List, Optional, Tuple
from models import ChatIntakeResponse, ChatMessage, ChatMessageRequest, TicketRequest

REQUIRED_FIELDS = ["user_name", "user_email", "subject", "description"]
FIELD_PROMPTS = {
    "user_name": "What is your name?",
    "user_email": "What is your email address?",
    "subject": "What is the issue in one short subject line?",
    "description": "Please describe the problem in a little more detail.",
    "department": "Which department is this related to? If you are not sure, say skip.",
}


class ChatIntakeManager:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, object]] = {}

    def start_or_continue(self, request: ChatMessageRequest) -> ChatIntakeResponse:
        session_id = request.session_id or str(uuid.uuid4())
        session = self.sessions.get(session_id)

        if session is None:
            session = {
                "history": [],
                "ticket": {
                    "user_name": "",
                    "user_email": "",
                    "department": None,
                    "subject": "",
                    "description": "",
                },
            }
            self.sessions[session_id] = session

        history: List[ChatMessage] = session["history"]  
        ticket = session["ticket"]  

        user_text = request.message.strip()
        history.append(ChatMessage(role="user", content=user_text))
        self._merge_message_into_ticket(user_text, ticket)

        next_field = self._next_missing_field(ticket)

        if next_field is None:
            ready_ticket = TicketRequest(**ticket)
            response = ChatIntakeResponse(
                session_id=session_id,
                messages=list(history)
                + [
                    ChatMessage(
                        role="assistant",
                        content="Thanks. I have everything I need and the ticket is ready to submit.",
                    )
                ],
                ready_for_submission=True,
                ticket=ready_ticket,
            )
            session["completed"] = True
            return response

        prompt = FIELD_PROMPTS[next_field]
        history.append(ChatMessage(role="assistant", content=prompt))
        return ChatIntakeResponse(
            session_id=session_id,
            messages=list(history),
            ready_for_submission=False,
            ticket=None,
        )

    def _next_missing_field(self, ticket: Dict[str, object]) -> Optional[str]:
        for field in REQUIRED_FIELDS:
            value = str(ticket.get(field, "") or "").strip()
            if not value:
                return field
        return None

    def _merge_message_into_ticket(self, message: str, ticket: Dict[str, object]) -> None:
        lower = message.lower()

        if not ticket.get("user_name") and len(message.split()) <= 4 and "@" not in message:
            ticket["user_name"] = message
            return

        if not ticket.get("user_email") and "@" in message:
            ticket["user_email"] = message
            return

        if not ticket.get("subject") and len(message.split()) <= 12:
            ticket["subject"] = message
            return

        if not ticket.get("description"):
            ticket["description"] = message
            return

        if ticket.get("department") is None and any(
            keyword in lower
            for keyword in ["finance", "hr", "it", "support", "sales", "operations", "engineering"]
        ):
            ticket["department"] = message


chat_intake_manager = ChatIntakeManager()
