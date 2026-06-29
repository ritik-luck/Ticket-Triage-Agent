from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional


class TicketRequest(BaseModel):
    user_name: str = Field(..., min_length=1)
    user_email: EmailStr
    department: Optional[str] = None
    subject: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)


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
    rag_sources: List[str]
    audit_trail: List[str]
    guardrail_applied: bool = False


class UserTriageResponse(BaseModel):
    ticket_id: str
    category: str
    priority: str
    assigned_team: str
    suggested_solution: List[str]