import { useEffect, useMemo, useRef, useState } from "react";
import {
  Bot,
  ShieldCheck,
  Search,
  Route,
  Database,
  Sparkles,
  PartyPopper,
  Bell,
  User,
  Shield,
} from "lucide-react";

import TicketForm from "./components/TicketForm.jsx";
import ChatIntake from "./components/ChatIntake.jsx";
import ResultPanel from "./components/ResultPanel.jsx";
import WorkflowCard from "./components/WorkflowCard.jsx";
import AnalyticsDashboard from "./components/AnalyticsDashboard.jsx";
import AdminTicketViewer from "./components/AdminTicketViewer.jsx";
import TriagePipeline from "./components/TriagePipeline.jsx";
import styles from "./App.module.css";

import { triageTicket } from "./api/triageApi.js";

export default function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [analyticsRefreshKey, setAnalyticsRefreshKey] = useState(0);
  const [userRole, setUserRole] = useState("user");
  const [intakeMode, setIntakeMode] = useState("chat");
  const [pipelineActiveStep, setPipelineActiveStep] = useState(-1);
  const [pipelineVisible, setPipelineVisible] = useState(false);
  const [pipelineCompleted, setPipelineCompleted] = useState(false);
  const [pendingResult, setPendingResult] = useState(null);
  const [toasts, setToasts] = useState([]);
  const [scrollReady, setScrollReady] = useState(false);
  const pipelineTimers = useRef([]);
  const pageRef = useRef(null);
  const heroRef = useRef(null);
  const resultRef = useRef(null);

  const particles = useMemo(
    () =>
      Array.from({ length: 18 }, (_, index) => ({
        id: index,
        left: `${(index * 17) % 100}%`,
        top: `${(index * 23) % 100}%`,
        size: 10 + (index % 4) * 8,
        duration: 8 + (index % 5) * 2,
        delay: index * 0.25,
      })),
    []
  );

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add(styles.revealVisible);
          }
        });
      },
      { threshold: 0.16 }
    );

    document.querySelectorAll("[data-reveal]").forEach((node) => observer.observe(node));
    setScrollReady(true);

    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (!scrollReady) return undefined;
    document.body.classList.toggle("admin-mode-active", userRole === "admin");
    return undefined;
  }, [scrollReady, userRole]);

  useEffect(() => {
    if (result && resultRef.current) {
      resultRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [result]);

  function clearPipelineTimers() {
    pipelineTimers.current.forEach((timer) => clearTimeout(timer));
    pipelineTimers.current = [];
  }

  function runPipelineReveal(resultData) {
    clearPipelineTimers();
    setPipelineVisible(true);
    setPipelineCompleted(false);
    setPipelineActiveStep(-1);
    setResult(null);
    setPendingResult(resultData);
    setError("");

    const stepCount = 6;

    for (let index = 0; index < stepCount; index += 1) {
      pipelineTimers.current.push(
        setTimeout(() => {
          setPipelineActiveStep(index);
        }, index * 500)
      );
    }

    pipelineTimers.current.push(
      setTimeout(() => {
        setPipelineCompleted(true);
        setResult(resultData);
        setPendingResult(null);
        setAnalyticsRefreshKey((prev) => prev + 1);
        pushToast("Triage completed successfully", "success");
        setTimeout(() => {
          setPipelineVisible(false);
          setPipelineActiveStep(-1);
        }, 380);
      }, stepCount * 500 + 220)
    );
  }

  async function handleTriage(ticketData) {
    setLoading(true);
    setError("");
    setResult(null);
    setPendingResult(null);
    clearPipelineTimers();

    try {
      const data = await triageTicket(ticketData, userRole);
      runPipelineReveal(data);
    } catch (err) {
      setError(err.message);
      pushToast("Triage failed", "error");
    } finally {
      setLoading(false);
    }
  }

  function pushToast(title, type = "info") {
    const id = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    setToasts((current) => [...current, { id, title, type }]);
    setTimeout(() => {
      setToasts((current) => current.filter((toast) => toast.id !== id));
    }, 3200);
  }

  return (
    <main ref={pageRef} className={`page ${styles.page}`}>
      <div className={styles.particlesLayer} aria-hidden="true">
        {particles.map((particle) => (
          <span
            key={particle.id}
            className={styles.particle}
            style={{
              left: particle.left,
              top: particle.top,
              width: `${particle.size}px`,
              height: `${particle.size}px`,
              animationDuration: `${particle.duration}s`,
              animationDelay: `${particle.delay}s`,
            }}
          />
        ))}
      </div>

      <section ref={heroRef} className={`hero ${styles.hero}`} data-reveal>
        <div className="hero-copy">
          <h1>AI Ticket Triage & Response Automation</h1>
          <p className="hero-text">
            Helping support teams triage tickets faster with AI-powered routing and knowledge assistance
          </p>
          <div className="hero-stat-grid">
            <div className="hero-stat"></div>
            <div className="hero-stat"></div>
          </div>
        </div>

        <div className="hero-icon">
          <Bot size={72} />
        </div>
      </section>

      <div className={`role-selector ${styles.roleSelector}`} data-reveal>
        <div>
          <p className="section-label">Access mode</p>
          <h2 className="role-label">Current role</h2>
        </div>

        <div className={styles.roleSwitch}>
          <button
            type="button"
            className={`${styles.roleToggle} ${userRole === "user" ? styles.roleActive : ""}`}
            onClick={() => setUserRole("user")}
          >
            <User size={16} />
            User
          </button>
          <button
            type="button"
            className={`${styles.roleToggle} ${userRole === "admin" ? styles.roleActive : ""}`}
            onClick={() => setUserRole("admin")}
          >
            <Shield size={16} />
            Admin
          </button>
        </div>
      </div>

      <section className="workflow-grid" data-reveal>
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
        <div className={styles.modeWrap}>
          <div className={`role-selector intake-selector ${styles.intakeSelector}`} data-reveal>
            <div>
              <p className="section-label">Intake mode</p>
              <h2 className="role-label">Choose how to create a ticket</h2>
            </div>

            <select
              value={intakeMode}
              onChange={(e) => setIntakeMode(e.target.value)}
              className="role-select"
            >
              <option value="chat">Assistant</option>
              <option value="form">Classic</option>
            </select>
          </div>

          {intakeMode === "form" ? (
            <section className={`main-grid ${styles.modeTransition}`} data-reveal>
              <TicketForm onSubmit={handleTriage} loading={loading} />

              {(pipelineVisible || pendingResult || result || error) && (
                <div className="result-stage-stack">
                  {pipelineVisible && !result && (
                    <TriagePipeline
                      activeStep={pipelineActiveStep}
                      completed={pipelineCompleted}
                    />
                  )}

                  {result && (
                    <div
                      ref={resultRef}
                      className={`result-panel-enter ${pipelineCompleted ? "show" : ""}`}
                    >
                      <ResultPanel
                        result={result}
                        loading={false}
                        error={error}
                        userRole={userRole}
                      />
                    </div>
                  )}
                </div>
              )}
            </section>
          ) : (
            <section className={`main-grid ${styles.modeTransition}`} data-reveal>
              <ChatIntake onTriageComplete={runPipelineReveal} userRole={userRole} />

              {(pipelineVisible || pendingResult || result || error) && (
                <div className="result-stage-stack">
                  {pipelineVisible && !result && (
                    <TriagePipeline
                      activeStep={pipelineActiveStep}
                      completed={pipelineCompleted}
                    />
                  )}

                  {result && (
                    <div
                      ref={resultRef}
                      className={`result-panel-enter ${pipelineCompleted ? "show" : ""}`}
                    >
                      <ResultPanel
                        result={result}
                        loading={false}
                        error={error}
                        userRole={userRole}
                      />
                    </div>
                  )}
                </div>
              )}
            </section>
          )}
        </div>
      )}

      {userRole === "admin" && (
        <section className={`admin-panel-grid ${styles.modeTransition}`} data-reveal>
          <AnalyticsDashboard
            refreshKey={analyticsRefreshKey}
            userRole={userRole}
          />
          <AdminTicketViewer userRole={userRole} />
        </section>
      )}

      <div className={styles.toastStack} aria-live="polite" aria-atomic="true">
        {toasts.map((toast) => (
          <div key={toast.id} className={`${styles.toast} ${styles[toast.type]}`}>
            <Bell size={16} />
            <span>{toast.title}</span>
          </div>
        ))}
      </div>

      {pipelineCompleted && (
        <div className={styles.successBurst} aria-hidden="true">
          <PartyPopper size={28} />
          <Sparkles size={28} />
        </div>
      )}
    </main>
  );
}
