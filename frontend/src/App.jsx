import { useState } from "react";
import { Bot, ShieldCheck, Search, Route, Database } from "lucide-react";

import TicketForm from "./components/TicketForm.jsx";
import ResultPanel from "./components/ResultPanel.jsx";
import WorkflowCard from "./components/WorkflowCard.jsx";
import AnalyticsDashboard from "./components/AnalyticsDashboard.jsx";
import AdminTicketViewer from "./components/AdminTicketViewer.jsx";

import { triageTicket } from "./api/triageApi.js";

export default function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [analyticsRefreshKey, setAnalyticsRefreshKey] = useState(0);
  const [userRole, setUserRole] = useState("user");

  async function handleTriage(ticketData) {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await triageTicket(ticketData, userRole);
      setResult(data);
      setAnalyticsRefreshKey((prev) => prev + 1);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page">
      <section className="hero">
        <div className="hero-copy">
          <h1>AI Ticket Triage & Response Automation</h1>
          <p className="hero-text">
            Helping support teams triage tickets faster with AI-powered routing and knowledge assistance
          </p>
          <div className="hero-stat-grid">
            <div className="hero-stat">
            </div>
            <div className="hero-stat">
            </div>
          </div>
        </div>

        <div className="hero-icon">
          <Bot size={72} />
        </div>
      </section>

      <div className="role-selector">
        <div>
          <p className="section-label">Access mode</p>
          <h2 className="role-label">Current role</h2>
        </div>

        <select
          value={userRole}
          onChange={(e) => setUserRole(e.target.value)}
          className="role-select"
        >
          <option value="user">User</option>
          <option value="admin">Admin</option>
        </select>
      </div>

      <section className="workflow-grid">
        <WorkflowCard
          icon={<ShieldCheck />}
          title="Classification"
          text="Automatically detects category and intent from user input."
        />

        <WorkflowCard
          icon={<Database />}
          title="Knowledge Retrieval"
          text="Checks internal knowledge base before escalating."
        />

        <WorkflowCard
          icon={<Search />}
          title="Web Fallback"
          text="Searches external sources when the KB is sparse."
        />

        <WorkflowCard
          icon={<Route />}
          title="Routing"
          text="Assigns the right team with priority context."
        />
      </section>

      {userRole === "user" && (
        <section className="main-grid">
          <TicketForm onSubmit={handleTriage} loading={loading} />

          {(result || loading || error) && (
            <ResultPanel
              result={result}
              loading={loading}
              error={error}
              userRole={userRole}
            />
          )}
        </section>
      )}

      {userRole === "admin" && (
        <section className="admin-panel-grid">
          <AnalyticsDashboard
            refreshKey={analyticsRefreshKey}
            userRole={userRole}
          />
          <AdminTicketViewer userRole={userRole} />
        </section>
      )}
    </main>
  );
}
