import { useEffect, useState } from "react";
import { ChevronLeft, ChevronRight, Search } from "lucide-react";

const PAGE_SIZE = 5;

function AdminTicketViewer({ userRole }) {
  const [tickets, setTickets] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [selected, setSelected] = useState(null);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("");

  useEffect(() => {
    fetchTickets();
  }, []);

  const fetchTickets = async () => {
    const res = await fetch("http://127.0.0.1:8000/tickets", {
      headers: { "x-user-role": userRole },
    });
    const data = await res.json();
    setTickets(data.tickets || []);
    setFiltered(data.tickets || []);
  };

  useEffect(() => {
    let data = tickets;

    if (search) {
      data = data.filter((t) =>
        t.ticket_id.toLowerCase().includes(search.toLowerCase())
      );
    }

    if (categoryFilter) {
      data = data.filter((t) => t.category === categoryFilter);
    }

    if (priorityFilter) {
      data = data.filter((t) => t.priority === priorityFilter);
    }

    setFiltered(data);
    setPage(1);
  }, [search, categoryFilter, priorityFilter, tickets]);

  const totalPages = Math.ceil(filtered.length / PAGE_SIZE);
  const start = (page - 1) * PAGE_SIZE;
  const pageTickets = filtered.slice(start, start + PAGE_SIZE);

  const fetchTicketById = async (id) => {
    const res = await fetch(`http://127.0.0.1:8000/tickets/${id}`, {
      headers: { "x-user-role": userRole },
    });
    const data = await res.json();
    setSelected(data);
  };

  return (
    <div className="admin-container admin-viewer">
      <div className="admin-header admin-header-split">
        <div>
          <p className="section-label">Admin</p>
          <h2>Ticket Audit Dashboard</h2>
          <p className="hint">Search, filter, and inspect ticket audit trails in one view.</p>
        </div>

        <div className="filter-bar">
          <div className="search-box">
            <Search size={16} />
            <input
              placeholder="Search Ticket ID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <select value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)}>
            <option value="">All Categories</option>
            <option>Network Issue</option>
            <option>Access Issue</option>
            <option>Hardware Issue</option>
            <option>Email Issue</option>
            <option>Bug</option>
            <option>General Support</option>
          </select>

          <select value={priorityFilter} onChange={(e) => setPriorityFilter(e.target.value)}>
            <option value="">All Priorities</option>
            <option>Critical</option>
            <option>High</option>
            <option>Medium</option>
            <option>Low</option>
          </select>
        </div>
      </div>

      <div className="admin-layout">
        <div className="ticket-list">
          {pageTickets.length === 0 ? (
            <div className="empty-state small">No tickets match the current filters.</div>
          ) : (
            pageTickets.map((ticket) => (
              <div
                key={ticket.ticket_id}
                className="ticket-card"
                onClick={() => fetchTicketById(ticket.ticket_id)}
              >
                <div className="ticket-card-title">{ticket.ticket_id}</div>
                <div className="ticket-card-meta">
                  {ticket.category && <span>{ticket.category}</span>}
                  {ticket.priority && (
                    <span className={`pill ${ticket.priority.toLowerCase()}`}>
                      {ticket.priority}
                    </span>
                  )}
                </div>
              </div>
            ))
          )}

          <div className="pagination">
            <button disabled={page === 1} onClick={() => setPage(page - 1)}>
              <ChevronLeft size={16} />
            </button>
            <span>{page} / {totalPages || 1}</span>
            <button disabled={page === totalPages || totalPages === 0} onClick={() => setPage(page + 1)}>
              <ChevronRight size={16} />
            </button>
          </div>
        </div>

        <div className="ticket-details ticket-details-card">
          {!selected ? (
            <div className="empty-state">
              Select a ticket to inspect the audit trail and suggested solution.
            </div>
          ) : (
            <>
              <div className="ticket-details-header">
                <div>
                  <p className="section-label">Details</p>
                  <h3>{selected.ticket_id}</h3>
                </div>
                {selected.priority && (
                  <span className={`pill ${selected.priority.toLowerCase()}`}>
                    {selected.priority}
                  </span>
                )}
              </div>

              <div className="info-grid admin-info-grid">
                <Info label="Category" value={selected.category} />
                <Info label="Priority" value={selected.priority} />
                <Info label="Team" value={selected.assigned_team} />
                <Info label="Confidence" value={selected.confidence} />
              </div>

              <div className="section section-card">
                <h4>Suggested Solution</h4>
                {selected.suggested_solution?.length ? (
                  <ul>
                    {selected.suggested_solution.map((solution, index) => (
                      <li key={index}>{solution}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="hint">No suggested solution available yet.</p>
                )}
              </div>

              <div className="section section-card">
                <h4>Audit Trail</h4>
                <div className="audit-box">
                  {selected.audit_trail?.length ? (
                    selected.audit_trail.map((log, index) => (
                      <p key={index}>{log}</p>
                    ))
                  ) : (
                    <p className="hint">No audit entries available.</p>
                  )}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function Info({ label, value }) {
  return (
    <div className="info-card">
      <span>{label}</span>
      <strong>{value || "N/A"}</strong>
    </div>
  );
}

export default AdminTicketViewer;
