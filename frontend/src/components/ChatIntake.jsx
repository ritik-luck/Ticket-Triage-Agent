import { useMemo, useState } from "react";
import { sendChatMessage } from "../api/chatApi.js";
import { triageTicket } from "../api/triageApi.js";
import styles from "./ChatIntake.module.css";

function ChatBubble({ role, content }) {
  return (
    <div className={`${styles.chatBubble} ${styles[role]}`}>
      <span className={styles.chatBubbleRole}>{role === "assistant" ? "Assistant" : "You"}</span>
      <p>{content}</p>
    </div>
  );
}

export default function ChatIntake({ onTriageComplete, userRole }) {
  const [sessionId, setSessionId] = useState("");
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Hi, I can help capture your ticket. What is your name?",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [readyTicket, setReadyTicket] = useState(null);
  const [error, setError] = useState("");

  const lastAssistantMessage = useMemo(() => {
    return [...messages].reverse().find((message) => message.role === "assistant");
  }, [messages]);

  async function handleSend(event) {
    event.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput("");
    setLoading(true);
    setError("");

    try {
      const response = await sendChatMessage({
        session_id: sessionId || undefined,
        message: userMessage,
      });

      setSessionId(response.session_id);
      setMessages(response.messages || []);
      setReadyTicket(response.ticket || null);

      if (response.ready_for_submission && response.ticket) {
        const triageResponse = await triageTicket(response.ticket, userRole);
        onTriageComplete(triageResponse);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={`card ${styles.chatIntakeCard}`}>
      <div className="card-header">
        <p className="section-label">Chat Intake</p>
        <h2>Conversational Ticket Assistant</h2>
      </div>

      <div className={styles.chatThread}>
        {messages.map((message, index) => (
          <ChatBubble key={`${message.role}-${index}`} role={message.role} content={message.content} />
        ))}
      </div>

      {readyTicket && (
        <div className="info-box">
          <span>Captured Ticket</span>
          <strong>{readyTicket.subject || "Ready"}</strong>
          <p className="hint">{readyTicket.description}</p>
        </div>
      )}

      {error && <p className="error-text">{error}</p>}

      {lastAssistantMessage && (
        <form className={styles.chatForm} onSubmit={handleSend}>
          <input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Type your reply..."
          />
          <button type="submit" disabled={loading}>
            {loading ? "Sending..." : "Send"}
          </button>
        </form>
      )}
    </div>
  );
}
