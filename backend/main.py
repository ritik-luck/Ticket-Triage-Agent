from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware

from models import TicketRequest, TriageResponse, UserTriageResponse
from agent import run_ticket_triage
from memory.memory_manager import memory_manager
from memory.analytics_manager import analytics_manager


app = FastAPI(title="Ticket Triage Agent API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def is_admin_role(role: str) -> bool:
    return role.lower().strip() == "admin"


def build_user_response(response: TriageResponse) -> UserTriageResponse:
    return UserTriageResponse(
        ticket_id=response.ticket_id,
        category=response.category,
        priority=response.priority,
        assigned_team=response.assigned_team,
        suggested_solution=response.suggested_solution,
    )


@app.get("/")
def home():
    return {
        "message": "Ticket Triage Agent API is running successfully."
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ticket-triage-agent-api"
    }


@app.post("/triage")
def triage_ticket(
    request: TicketRequest,
    x_user_role: str = Header(default="user")
):
    try:
        response = run_ticket_triage(request)

        if is_admin_role(x_user_role):
            return response

        return build_user_response(response)

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Ticket triage failed: {str(error)}"
        )


@app.get("/tickets")
def get_all_tickets(
    x_user_role: str = Header(default="user")
):
    tickets = memory_manager.get_all_ticket_logs()

    if is_admin_role(x_user_role):
        return {
            "total_tickets": len(tickets),
            "tickets": tickets
        }

    user_tickets = []

    for ticket in tickets:
        user_tickets.append(
            {
                "ticket_id": ticket.get("ticket_id"),
                "category": ticket.get("category"),
                "priority": ticket.get("priority"),
                "assigned_team": ticket.get("assigned_team"),
                "suggested_solution": ticket.get("suggested_solution"),
            }
        )

    return {
        "total_tickets": len(user_tickets),
        "tickets": user_tickets
    }


@app.get("/tickets/{ticket_id}")
def get_ticket(
    ticket_id: str,
    x_user_role: str = Header(default="user")
):
    ticket = memory_manager.get_ticket_by_id(ticket_id)

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    if is_admin_role(x_user_role):
        return ticket

    return {
        "ticket_id": ticket.get("ticket_id"),
        "category": ticket.get("category"),
        "priority": ticket.get("priority"),
        "assigned_team": ticket.get("assigned_team"),
        "suggested_solution": ticket.get("suggested_solution"),
    }


@app.delete("/tickets")
def clear_ticket_memory(
    x_user_role: str = Header(default="user")
):
    if not is_admin_role(x_user_role):
        raise HTTPException(
            status_code=403,
            detail="Only admin can clear ticket memory."
        )

    memory_manager.clear_memory()

    return {
        "message": "Ticket memory cleared successfully."
    }


@app.get("/analytics")
def get_analytics_dashboard(
    x_user_role: str = Header(default="user")
):
    if not is_admin_role(x_user_role):
        raise HTTPException(
            status_code=403,
            detail="Only admin can view analytics dashboard."
        )

    return analytics_manager.get_dashboard_summary()


@app.get("/analytics/tickets")
def get_analytics_tickets(
    x_user_role: str = Header(default="user")
):
    if not is_admin_role(x_user_role):
        raise HTTPException(
            status_code=403,
            detail="Only admin can view analytics tickets."
        )

    tickets = memory_manager.get_all_ticket_logs()

    normalized_tickets = []

    for ticket in tickets:
        audit_trail = ticket.get("audit_trail", [])

        if audit_trail is None:
            audit_trail = []

        if not isinstance(audit_trail, list):
            audit_trail = [str(audit_trail)]

        audit_text = " ".join(str(item) for item in audit_trail).lower()

        guardrail_applied = (
            ticket.get("guardrail_applied") is True
            or ticket.get("guardrailApplied") is True
            or "guardrail applied" in audit_text
        )

        normalized_ticket = {
            **ticket,
            "audit_trail": audit_trail,
            "guardrail_applied": guardrail_applied,
        }

        normalized_tickets.append(normalized_ticket)

    return {
        "total_tickets": len(normalized_tickets),
        "tickets": normalized_tickets
    }