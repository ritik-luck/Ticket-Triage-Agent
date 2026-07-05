import { useState } from "react";
import styles from "./TicketForm.module.css";

const defaultTicket = {
  user_name: "",
  user_email: "",
  department: "",
  subject: "",
  description: "",
};

export default function TicketForm({ onSubmit, loading }) {
  const [form, setForm] = useState(defaultTicket);

  function updateField(event) {
    const { name, value } = event.target;
    setForm((oldForm) => ({ ...oldForm, [name]: value }));
  }

  function submitForm(event) {
    event.preventDefault();
    onSubmit(form);
  }

  return (
    <div className={`card ${styles.formCard}`}>
      <div className={styles.cardHeader}>
        <p className="section-label">Input</p>
        <h2>Submit Ticket</h2>
      </div>

      <form className={styles.form} onSubmit={submitForm}>
        <div className={styles.formGrid}>
          <label className={styles.label}>
            <span>User Name</span>
            <input
              name="user_name"
              value={form.user_name}
              onChange={updateField}
              placeholder=""
              required
            />
          </label>

          <label className={styles.label}>
            <span>User Email</span>
            <input
              name="user_email"
              type="email"
              value={form.user_email}
              onChange={updateField}
              placeholder=""
              required
            />
          </label>

          <label className={styles.label}>
            <span>Department</span>
            <input
              name="department"
              value={form.department}
              onChange={updateField}
              placeholder=""
            />
          </label>

          <label className={styles.label}>
            <span>Subject</span>
            <input
              name="subject"
              value={form.subject}
              onChange={updateField}
              placeholder=""
              required
            />
          </label>

          <label className={`${styles.label} ${styles.fullWidth}`}>
            <span>Description</span>
            <textarea
              name="description"
              rows="6"
              value={form.description}
              onChange={updateField}
              required
            />
          </label>
        </div>

        <div className={styles.formFooter}>
          <button disabled={loading} type="submit" className="primary-button">
            {loading ? "Triaging..." : "Submit Ticket"}
          </button>
        </div>
      </form>
    </div>
  );
}
