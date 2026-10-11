# AI Ticket Triage Agent

An AI-powered support-ticket triage system that classifies issues, sets priority, routes tickets to the right team, and suggests resolutions.

## Highlights

- RAG-powered knowledge-base retrieval and similar-ticket matching
- AI classification, priority detection, routing, and SLA risk prediction
- Guardrails and escalation for high-risk tickets
- Conversational ticket intake, audit trails, and ticket analytics
- Role-based views for users and administrators

## Tech Stack

- **Frontend:** React, Vite
- **Backend:** FastAPI, Pydantic
- **AI & Retrieval:** Groq, Sentence Transformers, ChromaDB

## Run Locally

1. Set `GROQ_API_KEY` in a `backend/.env` file.
2. Install the frontend dependencies and start the app:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. Install the required Python packages, then start the API:

   ```bash
   cd backend
   pip install fastapi uvicorn pydantic[email] python-dotenv groq pandas sentence-transformers chromadb
   uvicorn main:app --reload
   ```

The API is available at `http://127.0.0.1:8000`, with interactive documentation at `/docs`.
