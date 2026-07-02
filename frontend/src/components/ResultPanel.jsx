export default function ResultPanel({ result, loading, error, userRole = "user" }) {
  if (loading) {
    return (
      <div className="card result-card center-card">
        <div className="loader" />
        <h2>Agent is analyzing the ticket...</h2>
        <p>Classification → Internal Search → Web Search fallback → Routing → Response</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card result-card error-card">
        <h2>Connection Error</h2>
        <p>{error}</p>
        <p className="hint">Make sure your backend is running at http://localhost:8000</p>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="card result-card center-card">
        <h2>Triage Output</h2>
        <p>Submit a ticket and your backend response will appear here.</p>
      </div>
    );
  }

  const isAdmin = userRole === "admin";
  const auditTrail = getAuditTrail(result);
  const auditText = getAuditText(result);
  const cacheTriggered = auditText.includes("cache");

  const guardrailTriggered =
    result.guardrail_applied === true ||
    result.guardrailApplied === true ||
    auditText.includes("guardrail applied");

  const guardrailReason = getGuardrailReason(result);

  return (
    <div className="card result-card">
      {cacheTriggered && (
        <div className="cache-badge">⚡ Served from cache (recent similar issue)</div>
      )}

      {guardrailTriggered && (
        <div className="guardrail-badge">
          🚨 Guardrail Triggered (Escalation Applied)
          <div className="guardrail-badge-reason">{guardrailReason}</div>
        </div>
      )}

      <div className="triage-heading">
        <div>
          <p className="section-label">Output</p>
          <h2>Triage Result</h2>
        </div>

        {isAdmin && <span className="role-badge">Admin View</span>}
      </div>

      <div className="triage-summary-header">
        <div className="summary-main">
          <span>Ticket ID</span>
          <strong>{result.ticket_id || result.ticketId || "Not returned"}</strong>
        </div>

        <div className="summary-main">
          <span>Category</span>
          <strong>{result.category || "Not returned"}</strong>
        </div>

        <div className="summary-main">
          <span>Priority</span>
          <strong className={`priority-text ${String(result.priority || "").toLowerCase()}`}>
            {result.priority || "Not returned"}
          </strong>
        </div>

        <div className="summary-main">
          <span>Assigned Team</span>
          <strong>{result.assigned_team || result.assignedTeam || "Not returned"}</strong>
        </div>
      </div>

      {isAdmin && (
        <div className="result-grid">
          <Info label="Confidence" value={formatValue(result.confidence)} />
          <Info label="Internal Search Score" value={formatValue(result.rag_score)} />
          <Info label="Internal Search Used" value={yesNo(result.rag_used)} />
          <Info label="Web Search Used" value={yesNo(result.web_search_used)} />
        </div>
      )}

      {isAdmin && guardrailTriggered && (
        <div className="info-box guardrail-info-box">
          <span>Guardrail Status</span>
          <strong>Triggered</strong>
          <p className="hint">{guardrailReason}</p>
        </div>
      )}

      {isAdmin && (
        <div className="info-box">
          <span>Jira</span>
          <strong>{result.jira_created ? result.jira_key || "Created" : "Not created"}</strong>
          {result.jira_url ? (
            <a href={result.jira_url} target="_blank" rel="noreferrer">
              Open in Jira
            </a>
          ) : (
            <p className="hint">{result.jira_message || "No Jira status returned"}</p>
          )}
        </div>
      )}

      {isAdmin && (
        <Block
          title="Internal Search Sources"
          data={result.rag_sources || result.ragSources}
          empty="No source returned"
        />
      )}

      <Block
        title="Suggested Solution"
        data={result.suggested_solution || result.suggestedSolution}
        empty="No solution returned"
      />

      {isAdmin && (
        <Block
          title="Recommended Action"
          data={result.recommended_action || result.recommendedAction}
          empty="No recommended action returned"
        />
      )}

      {isAdmin && (
        <Block
          title="LLM Response"
          data={result.llm_response || result.llmResponse}
          empty="No LLM response returned"
        />
      )}

      {isAdmin && (
        <Block title="Audit Trail" data={auditTrail} empty="No audit trail returned" />
      )}
    </div>
  );
}

function Info({ label, value }) {
  return (
    <div className="info-box">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function Block({ title, data, empty }) {
  return (
    <div className="block">
      <h3>{title}</h3>

      {Array.isArray(data) && data.length > 0 ? (
        <ul>
          {data.map((item, index) => (
            <li key={`${title}-${index}`}>{String(item)}</li>
          ))}
        </ul>
      ) : typeof data === "string" && data.trim().length > 0 ? (
        <ul>
          <li>{data}</li>
        </ul>
      ) : (
        <p className="hint">{empty}</p>
      )}
    </div>
  );
}

function yesNo(value) {
  if (value === true) return "Yes";
  if (value === false) return "No";
  return "Not returned";
}

function formatValue(value) {
  if (value === undefined || value === null || value === "") {
    return "Not returned";
  }

  if (typeof value === "number") {
    return Number.isInteger(value) ? String(value) : value.toFixed(3);
  }

  return String(value);
}

function getAuditTrail(result) {
  return result.audit_trail || result.auditTrail || result.audit || [];
}

function getAuditText(result) {
  const auditTrail = getAuditTrail(result);

  if (Array.isArray(auditTrail)) {
    return auditTrail.map((item) => String(item)).join(" ").toLowerCase();
  }

  return String(auditTrail || "").toLowerCase();
}

function getGuardrailReason(result) {
  const auditTrail = getAuditTrail(result);

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
}
