from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Literal


class TicketRequest(BaseModel):
    user_name: str
    user_email: EmailStr
    department: Optional[str] = None
    subject: str
    description: str


class TriageResponse(BaseModel):
    ticket_id: str
    category: str
    confidence: float
    confidence_reason: Optional[str] = None
    human_review_required: bool = False
    human_review_reason: Optional[str] = None
    clarifying_question: Optional[str] = None
    priority: str
    assigned_team: str
    rag_score: float
    rag_used: bool
    web_search_used: bool
    suggested_solution: List[str]
    similar_tickets: List[dict] = Field(default_factory=list)
    llm_response: Optional[str] = None
    recommended_action: Optional[str] = None
    escalation_required: bool = False
    sla_target_hours: Optional[float] = None
    sla_response_hours: Optional[float] = None
    sla_breach_risk: Optional[str] = None
    sla_escalation_required: bool = False
    sla_reason: Optional[str] = None
    rag_sources: List[str]
    audit_trail: List[str]
    guardrail_applied: bool = False
    guardrail_reason: Optional[str] = None


class UserTriageResponse(BaseModel):
    ticket_id: str
    category: str
    priority: str
    assigned_team: str
    suggested_solution: List[str]
    similar_tickets: List[dict] = Field(default_factory=list)


class ChatMessageRequest(BaseModel):
    session_id: Optional[str] = None
    message: str


class ChatMessage(BaseModel):
    role: Literal["assistant", "user"]
    content: str


class ChatIntakeResponse(BaseModel):
    session_id: str
    messages: List[ChatMessage]
    ready_for_submission: bool = False
    ticket: Optional[TicketRequest] = None
