import { useState } from "react";

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
    <div className="card form-card">
      <div className="card-header">
        <p className="section-label">Input</p>
        <h2>Submit Ticket</h2>
      </div>

      <form className="form" onSubmit={submitForm}>
        <div className="form-grid">
          <label>
            <span>User Name</span>
            <input
              name="user_name"
              value={form.user_name}
              onChange={updateField}
              placeholder=""
              required
            />
          </label>

          <label>
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

          <label>
            <span>Department</span>
            <input
              name="department"
              value={form.department}
              onChange={updateField}
              placeholder=""
            />
          </label>

          <label>
            <span>Subject</span>
            <input
              name="subject"
              value={form.subject}
              onChange={updateField}
              placeholder=""
              required
            />
          </label>

          <label className="full-width">
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

        <div className="form-footer">
          <button disabled={loading} type="submit" className="primary-button">
            {loading ? "Triaging..." : "Submit Ticket"}
          </button>
        </div>
      </form>
    </div>
  );
}
