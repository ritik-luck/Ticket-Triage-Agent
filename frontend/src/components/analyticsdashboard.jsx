import React, { useEffect, useMemo, useState } from "react";
import styles from "./AnalyticsDashboard.module.css";

const API_BASE_URL = "http://localhost:8000";

function AnimatedNumber({ value }) {
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    let frame;
    const start = performance.now();
    const duration = 900;

    function tick(now) {
      const progress = Math.min((now - start) / duration, 1);
      setCurrent(Math.round(value * progress));
      if (progress < 1) frame = requestAnimationFrame(tick);
    }

    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [value]);

  return <strong className={styles.metricValue}>{current}</strong>;
}

function AnalyticsDashboard({ refreshKey = 0 }) {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showGuardrailBreakdown, setShowGuardrailBreakdown] = useState(false);
  const [showSlaBreakdown, setShowSlaBreakdown] = useState(false);

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

  const getAuditTrail = (ticket) => ticket.audit_trail || ticket.auditTrail || ticket.audit || [];

  const getAuditText = (ticket) => {
    const auditTrail = getAuditTrail(ticket);
    return Array.isArray(auditTrail) ? auditTrail.join(" ").toLowerCase() : String(auditTrail || "").toLowerCase();
  };

  const getGuardrailDescription = (ticket) => {
    const explicitReason = ticket.guardrail_reason || ticket.guardrailReason || "";
    if (String(explicitReason).trim()) return String(explicitReason);
    const auditTrail = getAuditTrail(ticket);
    if (Array.isArray(auditTrail)) {
      const reason = auditTrail.find((item) => String(item).toLowerCase().includes("guardrail"));
      return reason || "Guardrail applied";
    }
    const auditText = String(auditTrail || "");
    return auditText.toLowerCase().includes("guardrail") ? auditText : "Guardrail applied";
  };

  const analytics = useMemo(() => {
    const ragUsedCount = tickets.filter((ticket) => ticket.rag_used === true || ticket.ragUsed === true).length;
    const webSearchUsedCount = tickets.filter((ticket) => ticket.web_search_used === true || ticket.webSearchUsed === true).length;
    const guardrailTickets = tickets.filter((ticket) => {
      const auditText = getAuditText(ticket);
      return ticket.guardrail_applied === true || ticket.guardrailApplied === true || auditText.includes("guardrail");
    });
    const productionOutageTickets = guardrailTickets.filter((ticket) => {
      const auditText = getAuditText(ticket);
      return auditText.includes("production outage") || auditText.includes("production system down") || auditText.includes("system down") || auditText.includes("multiple users affected") || auditText.includes("outage");
    });
    const securityIncidentTickets = guardrailTickets.filter((ticket) => {
      const auditText = getAuditText(ticket);
      return auditText.includes("security incident") || auditText.includes("security") || auditText.includes("phishing") || auditText.includes("suspicious login") || auditText.includes("account compromised");
    });
    const dataLossTickets = guardrailTickets.filter((ticket) => {
      const auditText = getAuditText(ticket);
      return auditText.includes("data loss") || auditText.includes("deleted data") || auditText.includes("missing data");
    });
    const slaTickets = tickets.filter((ticket) => ticket.sla_target_hours !== undefined || ticket.slaTargetHours !== undefined);
    const slaLowRiskTickets = slaTickets.filter((ticket) => String(ticket.sla_breach_risk || ticket.slaBreachRisk || "").toLowerCase() === "low");
    const slaMediumRiskTickets = slaTickets.filter((ticket) => String(ticket.sla_breach_risk || ticket.slaBreachRisk || "").toLowerCase() === "medium");
    const slaHighRiskTickets = slaTickets.filter((ticket) => String(ticket.sla_breach_risk || ticket.slaBreachRisk || "").toLowerCase() === "high");
    return {
      totalTicketCount: tickets.length,
      ragUsedCount,
      webSearchUsedCount,
      guardrailCount: productionOutageTickets.length + securityIncidentTickets.length + dataLossTickets.length,
      guardrailTotalCount: guardrailTickets.length,
      productionOutageCount: productionOutageTickets.length,
      securityIncidentCount: securityIncidentTickets.length,
      dataLossCount: dataLossTickets.length,
      slaTicketCount: slaLowRiskTickets.length + slaMediumRiskTickets.length + slaHighRiskTickets.length,
      slaTotalCount: slaTickets.length,
      slaLowRiskCount: slaLowRiskTickets.length,
      slaMediumRiskCount: slaMediumRiskTickets.length,
      slaHighRiskCount: slaHighRiskTickets.length,
      latestGuardrailDescription: guardrailTickets.length ? getGuardrailDescription(guardrailTickets[guardrailTickets.length - 1]) : "",
      latestSlaDescription: slaTickets.length ? getSlaDescription(slaTickets[slaTickets.length - 1]) : "",
    };
  }, [tickets]);

  function getSlaDescription(ticket) {
    const reason = ticket.sla_reason || ticket.slaReason || "";
    if (String(reason).trim()) return String(reason);
    const target = ticket.sla_target_hours || ticket.slaTargetHours;
    const risk = ticket.sla_breach_risk || ticket.slaBreachRisk;
    if (target) return `SLA target is ${target} hours with ${risk || "unknown"} breach risk.`;
    return "SLA was calculated.";
  }

  if (loading) {
    return (
      <section className="analytics-dashboard">
        <div className={styles.loadingSkeleton}>
          <div className={styles.skLine} />
          <div className={styles.skCard} />
          <div className={styles.skCard} />
          <div className={styles.skCard} />
        </div>
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
        <div className={`analytics-card ${styles.metricCard}`}>
          <span className="analytics-label">Total Tickets</span>
          <AnimatedNumber value={analytics.totalTicketCount} />
        </div>
        <div className={`analytics-card ${styles.metricCard}`}>
          <span className="analytics-label">Internal Search Used</span>
          <AnimatedNumber value={analytics.ragUsedCount} />
        </div>
        <div className={`analytics-card ${styles.metricCard}`}>
          <span className="analytics-label">Web Search Used</span>
          <AnimatedNumber value={analytics.webSearchUsedCount} />
        </div>
        <div
          className={`analytics-card guardrail-card guardrail-toggle-card ${analytics.slaTicketCount > 0 ? "guardrail-active" : ""}`}
          role="button"
          tabIndex={0}
          onClick={() => setShowSlaBreakdown((prev) => !prev)}
          onKeyDown={(event) => {
            if (event.key === "Enter" || event.key === " ") {
              event.preventDefault();
              setShowSlaBreakdown((prev) => !prev);
            }
          }}
        >
          <span className="analytics-label">SLA</span>
          <AnimatedNumber value={analytics.slaTicketCount} />
        </div>
        <div
          className={`analytics-card guardrail-card guardrail-toggle-card ${analytics.guardrailCount > 0 ? "guardrail-active" : ""}`}
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
          <span className="analytics-label">Guardrail</span>
          <AnimatedNumber value={analytics.guardrailCount} />
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

      {showSlaBreakdown && (
        <div className="guardrail-breakdown-box">
          <div className="guardrail-breakdown-item">
            <span className="analytics-label">Low Risk</span>
            <strong>{analytics.slaLowRiskCount}</strong>
          </div>
          <div className="guardrail-breakdown-item">
            <span className="analytics-label">Medium Risk</span>
            <strong>{analytics.slaMediumRiskCount}</strong>
          </div>
          <div className="guardrail-breakdown-item">
            <span className="analytics-label">High Risk</span>
            <strong>{analytics.slaHighRiskCount}</strong>
          </div>
        </div>
      )}

      {analytics.slaTicketCount > 0 && (
        <div className="guardrail-alert-box">
          <div>
            <p>{analytics.latestSlaDescription}</p>
          </div>
        </div>
      )}
    </section>
  );
}

export default AnalyticsDashboard;
