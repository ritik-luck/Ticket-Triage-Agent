import styles from "./WorkflowCard.module.css";

export default function WorkflowCard({ icon, title, text }) {
  return (
    <div className={`${styles.workflowCard} workflow-card`}>
      <div className={styles.workflowIcon}>{icon}</div>
      <h3 className={styles.workflowTitle}>{title}</h3>
      <p className={styles.workflowText}>{text}</p>
    </div>
  );
}
