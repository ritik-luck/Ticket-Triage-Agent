from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional


class TicketRequest(BaseModel):
    user_name: str 
    user_email: EmailStr
    department: Optional[str] 
    subject: str 
    description: str 


class TriageResponse(BaseModel):
    ticket_id: str
    category: str
    confidence: float
    priority: str
    assigned_team: str
    rag_score: float
    rag_used: bool
    web_search_used: bool
    suggested_solution: List[str]
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
