import styles from "./TriagePipeline.module.css";

const pipelineSteps = [
  "Ticket captured",
  "Classifying intent",
  "Checking internal knowledge",
  "Launching web fallback",
  "Routing to the right team",
  "Preparing final response",
];

export default function TriagePipeline({ activeStep, completed }) {
  return (
    <div className={`card ${styles.pipelineCard}`}>
      <div className={styles.pipelineHeader}>
        <div>
          <p className="section-label">Live Pipeline</p>
          <h2>Triage in Motion</h2>
        </div>
        <div className={styles.pipelinePulse} />
      </div>

      <div className={styles.pipelineTrack}>
        {pipelineSteps.map((step, index) => {
          const isComplete = completed || index < activeStep;
          const isActive = !completed && index === activeStep;

          return (
            <div
              key={step}
              className={`${styles.pipelineStep} ${isComplete ? styles.complete : ""} ${isActive ? styles.active : ""}`}
              style={{ "--delay": `${index * 500}ms` }}
            >
              <div className={styles.pipelineStepNode}>
                <span>{index + 1}</span>
              </div>

              <div className={styles.pipelineStepCopy}>
                <strong>{step}</strong>
                <p>
                  {isComplete ? "Completed" : isActive ? "Processing now" : "Waiting in queue"}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
