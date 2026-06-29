const API_BASE_URL = "http://127.0.0.1:8000";

export async function triageTicket(ticketData, userRole = "user") {
  try {
    const response = await fetch(`${API_BASE_URL}/triage`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-user-role": userRole,
      },
      body: JSON.stringify(ticketData),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Backend returned error: ${response.status} - ${errorText || 'Unknown error'}`);
    }

    return response.json();
  } catch (err) {
    if (err.message.includes('Failed to fetch')) {
      throw new Error(
        `Backend not responding at ${API_BASE_URL}. Make sure FastAPI server is running: python -m uvicorn main:app --host 127.0.0.1 --port 8000`
      );
    }
    throw err;
  }
}
