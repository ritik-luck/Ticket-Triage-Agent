import React, { useEffect, useMemo, useState } from "react";

const API_BASE_URL = "http://localhost:8000";

function AnalyticsDashboard({ refreshKey = 0 }) {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showGuardrailBreakdown, setShowGuardrailBreakdown] = useState(false);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API_BASE_URL}/analytics/tickets`, {
        headers: {
          "x-user-role": "admin",
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch analytics data");
      }

      const data = await response.json();

      if (Array.isArray(data)) {
        setTickets(data);
      } else if (Array.isArray(data.tickets)) {
        setTickets(data.tickets);
      } else if (Array.isArray(data.data)) {
        setTickets(data.data);
      } else {
        setTickets([]);
      }
    } catch (err) {
      setError(err.message || "Something went wrong while loading analytics");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, [refreshKey]);

  const getAuditTrail = (ticket) => {
    return ticket.audit_trail || ticket.auditTrail || ticket.audit || [];
  };

  const getAuditText = (ticket) => {
    const auditTrail = getAuditTrail(ticket);

    if (Array.isArray(auditTrail)) {
      return auditTrail.join(" ").toLowerCase();
    }

    return String(auditTrail || "").toLowerCase();
  };

  const getGuardrailDescription = (ticket) => {
    const auditTrail = getAuditTrail(ticket);

    if (Array.isArray(auditTrail)) {
      const reason = auditTrail.find((item) =>
        String(item).toLowerCase().includes("guardrail applied")
      );

      return reason || "Guardrail applied";
    }

    const auditText = String(auditTrail || "");

    if (auditText.toLowerCase().includes("guardrail applied")) {
      return auditText;
    }

    return "Guardrail applied";
  };

  const analytics = useMemo(() => {
    const ragUsedCount = tickets.filter(
      (ticket) => ticket.rag_used === true || ticket.ragUsed === true
    ).length;

    const webSearchUsedCount = tickets.filter(
      (ticket) =>
        ticket.web_search_used === true || ticket.webSearchUsed === true
    ).length;

    const guardrailTickets = tickets.filter((ticket) => {
      const auditText = getAuditText(ticket);

      return (
        ticket.guardrail_applied === true ||
        ticket.guardrailApplied === true ||
        auditText.includes("guardrail applied")
      );
    });

    const productionOutageTickets = guardrailTickets.filter((ticket) => {
      const auditText = getAuditText(ticket);

      return (
        auditText.includes("production outage") ||
        auditText.includes("production system down") ||
        auditText.includes("system down") ||
        auditText.includes("multiple users affected") ||
        auditText.includes("outage")
      );
    });

    const securityIncidentTickets = guardrailTickets.filter((ticket) => {
      const auditText = getAuditText(ticket);

      return (
        auditText.includes("security incident") ||
        auditText.includes("security") ||
        auditText.includes("phishing") ||
        auditText.includes("suspicious login") ||
        auditText.includes("account compromised")
      );
    });

    const dataLossTickets = guardrailTickets.filter((ticket) => {
      const auditText = getAuditText(ticket);

      return (
        auditText.includes("data loss") ||
        auditText.includes("deleted data") ||
        auditText.includes("missing data")
      );
    });

    return {
      totalTicketCount: tickets.length,
      ragUsedCount,
      webSearchUsedCount,
      guardrailCount: guardrailTickets.length,
      productionOutageCount: productionOutageTickets.length,
      securityIncidentCount: securityIncidentTickets.length,
      dataLossCount: dataLossTickets.length,
      latestGuardrailDescription: guardrailTickets.length
        ? getGuardrailDescription(guardrailTickets[guardrailTickets.length - 1])
        : "",
    };
  }, [tickets]);

  if (loading) {
    return (
      <section className="analytics-dashboard">
        <h2>Analytics Dashboard</h2>
        <p>Loading analytics...</p>
      </section>
    );
  }

  if (error) {
    return (
      <section className="analytics-dashboard">
        <h2>Analytics Dashboard</h2>
        <p className="error-text">{error}</p>
      </section>
    );
  }

  return (
    <section className="analytics-dashboard">
      <div className="analytics-header">
        <div>
          <h2>Analytics Dashboard</h2>
        </div>
      </div>

      <div className="analytics-grid">
        <div className="analytics-card">
          <span className="analytics-label">Total Tickets</span>
          <strong>{analytics.totalTicketCount}</strong>
        </div>

        <div className="analytics-card">
          <span className="analytics-label">RAG Used</span>
          <strong>{analytics.ragUsedCount}</strong>
        </div>

        <div className="analytics-card">
          <span className="analytics-label">Web Search Used</span>
          <strong>{analytics.webSearchUsedCount}</strong>
        </div>

        <div
          className={`analytics-card guardrail-card guardrail-toggle-card ${
            analytics.guardrailCount > 0 ? "guardrail-active" : ""
          }`}
          role="button"
          tabIndex={0}
          onClick={() => setShowGuardrailBreakdown((prev) => !prev)}
          onKeyDown={(event) => {
            if (event.key === "Enter" || event.key === " ") {
              event.preventDefault();
              setShowGuardrailBreakdown((prev) => !prev);
            }
          }}
        >
          <span className="analytics-label">Guardrail Count</span>
          <strong>{analytics.guardrailCount}</strong>
        </div>
      </div>

      {analytics.guardrailCount > 0 && (
        <div className="guardrail-alert-box">
          <div>
            <p>{analytics.latestGuardrailDescription}</p>
          </div>
        </div>
      )}

      {showGuardrailBreakdown && (
        <div className="guardrail-breakdown-box">
          <div className="guardrail-breakdown-item">
            <span className="analytics-label">Production Outage</span>
            <strong>{analytics.productionOutageCount}</strong>
          </div>
          <div className="guardrail-breakdown-item">
            <span className="analytics-label">Security Incident</span>
            <strong>{analytics.securityIncidentCount}</strong>
          </div>
          <div className="guardrail-breakdown-item">
            <span className="analytics-label">Data Loss</span>
            <strong>{analytics.dataLossCount}</strong>
          </div>
        </div>
      )}
    </section>
  );
}

export default AnalyticsDashboard;
