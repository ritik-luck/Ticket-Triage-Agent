import { useEffect, useMemo, useState } from "react";
import styles from "./ResultPanel.module.css";

export default function ResultPanel({ result, loading, error, userRole = "user" }) {
  if (loading) {
    return (
      <div className={`card ${styles.resultCard} ${styles.centerCard}`}>
        <div className={styles.skeletonShell}>
          <div className={styles.skeletonHeader} />
          <div className={styles.skeletonLineLg} />
          <div className={styles.skeletonGrid}>
            <div className={styles.skeletonBlock} />
            <div className={styles.skeletonBlock} />
            <div className={styles.skeletonBlock} />
            <div className={styles.skeletonBlock} />
          </div>
          <div className={styles.skeletonStack}>
            <div className={styles.skeletonLine} />
            <div className={styles.skeletonLine} />
            <div className={styles.skeletonLine} />
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`card ${styles.resultCard} ${styles.errorCard}`}>
        <h2>Connection Error</h2>
        <p>{error}</p>
        <p className="hint">Make sure your backend is running at http://localhost:8000</p>
      </div>
    );
  }

  if (!result) {
    return (
      <div className={`card ${styles.resultCard} ${styles.centerCard}`}>
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
  const suggestedSolution = result.suggested_solution || result.suggestedSolution || [];
  const typedSolution = useTypewriter(suggestedSolution);
  const [expandedSimilarTicket, setExpandedSimilarTicket] = useState(null);

  function downloadTicket() {
    const ticketPayload = {
      ticket_id: result.ticket_id || result.ticketId || "",
      category: result.category || "",
      priority: result.priority || "",
      assigned_team: result.assigned_team || result.assignedTeam || "",
      suggested_solution: suggestedSolution,
    };

    const pdfBlob = buildTicketPdf(ticketPayload);
    const url = URL.createObjectURL(pdfBlob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${ticketPayload.ticket_id || "ticket"}-triage.pdf`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  return (
    <div className={`card ${styles.resultCard}`}>
      {cacheTriggered && (
        <div className="cache-badge">⚡ Served from cache (recent similar issue)</div>
      )}

      {guardrailTriggered && (
        <div className={`guardrail-badge ${styles.guardrailBadge}`}>
          🚨 Guardrail Triggered (Escalation Applied)
          <div className="guardrail-badge-reason">{guardrailReason}</div>
        </div>
      )}

      {Array.isArray(result.similar_tickets) && result.similar_tickets.length > 0 && (
        <section className={`${styles.similarTicketsPanel} ${styles.similarTicketsFeatured}`}>
          <div className={styles.panelHeader}>
            <div>
              <p className="section-label">Top Matches</p>
              <h3>Similar Tickets</h3>
              <p className="hint">
                {result.similar_tickets.length} similar ticket{result.similar_tickets.length === 1 ? "" : "s"} found.
                Click one to see the assigned team and solution.
              </p>
            </div>
          </div>
          <div className={styles.similarTicketsList}>
            {result.similar_tickets.map((ticket) => (
              <article key={ticket.ticket_id} className={styles.similarTicketCard}>
                <button
                  type="button"
                  className={styles.similarTicketButton}
                  onClick={() =>
                    setExpandedSimilarTicket(
                      expandedSimilarTicket === ticket.ticket_id ? null : ticket.ticket_id
                    )
                  }
                >
                  <div className={styles.similarTicketMeta}>
                    <span>{ticket.category || "Category not returned"}</span>
                    <span>{ticket.assigned_team || "Team not returned"}</span>
                  </div>
                  <span className={styles.similarTicketCta}>
                    {expandedSimilarTicket === ticket.ticket_id ? "Hide details" : "Show solution"}
                  </span>
                </button>
                {expandedSimilarTicket === ticket.ticket_id && (
                  <div className={styles.similarTicketDetails}>
                    <div className={styles.similarTicketDetailBlock}>
                      <span>Assigned Team</span>
                      <strong>{ticket.assigned_team || "Not returned"}</strong>
                    </div>
                    <div className={styles.similarTicketDetailBlock}>
                      <span>Suggested Solution</span>
                      {Array.isArray(ticket.suggested_solution) && ticket.suggested_solution.length > 0 ? (
                        <ul>
                          {ticket.suggested_solution.slice(0, 4).map((step, index) => (
                            <li key={`${ticket.ticket_id}-solution-${index}`}>{String(step)}</li>
                          ))}
                        </ul>
                      ) : (
                        <p className="hint">No solution returned</p>
                      )}
                    </div>
                  </div>
                )}
              </article>
            ))}
          </div>
        </section>
      )}

      <div className={styles.triageHeading}>
        <div>
          <p className="section-label">Output</p>
          <h2>Triage Result</h2>
        </div>

        <div className={styles.headerActions}>
          <button type="button" className={styles.downloadButton} onClick={downloadTicket}>
            Download Ticket
          </button>
          {isAdmin && <span className="role-badge">Admin View</span>}
        </div>
      </div>

      <div className={styles.triageSummaryHeader}>
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
          <strong
            className={`priority-text ${styles.priorityPulse} ${String(result.priority || "").toLowerCase()}`}
          >
            {result.priority || "Not returned"}
          </strong>
        </div>

        <div className="summary-main">
          <span>Assigned Team</span>
          <strong>{result.assigned_team || result.assignedTeam || "Not returned"}</strong>
        </div>
      </div>

      {isAdmin && (
        <div className={styles.resultGrid}>
          <Info label="Confidence" value={formatValue(result.confidence)} />
          <Info label="Internal Search Score" value={formatValue(result.rag_score)} />
          <Info label="Internal Search Used" value={yesNo(result.rag_used)} />
          <Info label="Web Search Used" value={yesNo(result.web_search_used)} />
        </div>
      )}

      {!isAdmin && result.clarifying_question && (
        <div className={styles.clarifyingQuestionPanel}>
          <p className="section-label">Need one more detail</p>
          <h3>{result.clarifying_question}</h3>
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

      <section className={styles.suggestedSolutionPanel}>
        <div className={styles.panelHeader}>
          <div>
            <h3>Suggested Solution</h3>
          </div>
        </div>
        <Block
          title=""
          data={typedSolution.length ? typedSolution : suggestedSolution}
          empty="No solution returned"
        />
      </section>

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

      {isAdmin && <Block title="Audit Trail" data={auditTrail} empty="No audit trail returned" />}
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
    <div className={styles.block}>
      {title ? <h3>{title}</h3> : null}

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

function useTypewriter(lines) {
  const normalizedLines = useMemo(
    () => (Array.isArray(lines) ? lines.map((line) => String(line)) : []),
    [lines]
  );
  const [typedCount, setTypedCount] = useState(0);

  useEffect(() => {
    setTypedCount(0);
    if (!normalizedLines.length) return undefined;

    let index = 0;
    const timer = setInterval(() => {
      index += 1;
      setTypedCount(index);
      if (index >= normalizedLines.length) {
        clearInterval(timer);
      }
    }, 220);

    return () => clearInterval(timer);
  }, [normalizedLines]);

  return normalizedLines.slice(0, typedCount);
}

function buildTicketPdf(ticket) {
  const lines = [
    "Ticket Triage Summary",
    "",
    `Ticket ID: ${ticket.ticket_id || ""}`,
    `Category: ${ticket.category || ""}`,
    `Priority: ${ticket.priority || ""}`,
    `Assigned Team: ${ticket.assigned_team || ""}`,
    "",
    "Suggested Solution:",
    ...(Array.isArray(ticket.suggested_solution) && ticket.suggested_solution.length
      ? ticket.suggested_solution.map((item, index) => `${index + 1}. ${item}`)
      : ["No suggested solution returned."]),
  ];

  const contentLines = lines.map((line) => escapePdfText(String(line)));
  const contentStream = buildPdfTextStream(contentLines);
  const objects = [];

  objects.push("<< /Type /Catalog /Pages 2 0 R >>");
  objects.push("<< /Type /Pages /Kids [3 0 R] /Count 1 >>");
  objects.push("<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>");
  objects.push(`<< /Length ${contentStream.length} >>\nstream\n${contentStream}\nendstream`);
  objects.push("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>");

  let pdf = "%PDF-1.4\n";
  const offsets = [0];

  objects.forEach((object, index) => {
    offsets.push(pdf.length);
    pdf += `${index + 1} 0 obj\n${object}\nendobj\n`;
  });

  const xrefStart = pdf.length;
  pdf += `xref\n0 ${objects.length + 1}\n`;
  pdf += "0000000000 65535 f \n";
  for (let index = 1; index <= objects.length; index += 1) {
    pdf += `${String(offsets[index]).padStart(10, "0")} 00000 n \n`;
  }
  pdf += `trailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xrefStart}\n%%EOF`;

  return new Blob([pdf], { type: "application/pdf" });
}

function buildPdfTextStream(lines) {
  const commands = [
    "BT",
    "/F1 14 Tf",
    "50 790 Td",
    "16 TL",
  ];

  lines.forEach((line, index) => {
    const escaped = line.replace(/\\/g, "\\\\").replace(/\(/g, "\\(").replace(/\)/g, "\\)");
    if (index === 0) {
      commands.push(`(${escaped}) Tj`);
    } else {
      commands.push("T*");
      commands.push(`(${escaped}) Tj`);
    }
  });

  commands.push("ET");
  return commands.join("\n");
}

function escapePdfText(text) {
  return text.replace(/[^\x20-\x7E]/g, "");
}
