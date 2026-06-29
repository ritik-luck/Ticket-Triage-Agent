export default function WorkflowCard({ icon, title, text }) {
  return (
    <div className="workflow-card">
      <div className="workflow-icon">{icon}</div>
      <h3>{title}</h3>
      <p>{text}</p>
    </div>
  );
}
