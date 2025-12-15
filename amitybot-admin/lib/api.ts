export async function sendChat({
    query,
    session_id,
    chat_history,
    role = "general",
}: {
    query: string;
    session_id: string;
    chat_history: [string, string][];
    role?: "general" | "logged_in";
}) {
    const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, session_id, chat_history, role }),
    });

    if (!res.ok) {
        throw new Error(`Chat API failed with ${res.status}`);
    }

    const data = await res.json();
    return data;
}
