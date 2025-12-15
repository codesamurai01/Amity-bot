"use client";

import { useState } from "react";
import { sendChat } from "lib/api";
import { v4 as uuidv4 } from "uuid";

export default function ChatPage() {
    const [query, setQuery] = useState("");
    const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);
    const [sessionId] = useState(() => uuidv4());
    const [history, setHistory] = useState<[string, string][]>([]);

    const handleSend = async () => {
        if (!query.trim()) return;
        const userMessage = { role: "user", content: query };
        setMessages((prev) => [...prev, userMessage]);

        try {
            const res = await sendChat({
                query,
                session_id: sessionId,
                chat_history: history,
                role: "general", // Or "logged_in"
            });

            const botMessage = { role: "bot", content: res.result };
            setMessages((prev) => [...prev, botMessage]);
            setHistory((prev) => [...prev, [query, res.result]]);
        } catch (err: any) {
            console.error(err);
            setMessages((prev) => [...prev, { role: "bot", content: "Error from server." }]);
        }

        setQuery("");
    };

    return (
        <div className="p-6">
            <div className="space-y-4">
                {messages.map((m, i) => (
                    <div key={i} className={m.role === "user" ? "text-right" : "text-left"}>
                        <div className="inline-block px-4 py-2 rounded bg-gray-100 dark:bg-gray-800">
                            <strong>{m.role === "user" ? "You" : "AmityBot"}:</strong> {m.content}
                        </div>
                    </div>
                ))}
            </div>
            <div className="mt-6 flex gap-2">
                <input
                    className="w-full p-2 border rounded"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Ask something about Amity..."
                />
                <button
                    className="px-4 py-2 bg-blue-600 text-white rounded"
                    onClick={handleSend}
                >
                    Send
                </button>
            </div>
        </div>
    );
}
