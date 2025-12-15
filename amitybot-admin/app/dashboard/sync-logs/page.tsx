'use client'
import { useEffect, useState } from 'react'

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

export default function SyncLogsPage() {
    const [logs, setLogs] = useState<any[]>([])

    useEffect(() => {
        fetch(`${API_BASE}/sync-logs`)
            .then((res) => res.json())
            .then((data) => setLogs(data || []))
    }, [])

    return (
        <div className="p-6">
            <h2 className="text-xl font-semibold mb-4">Sync Logs</h2>
            <table className="w-full border-collapse">
                <thead>
                    <tr className="bg-gray-100">
                        <th className="border px-4 py-2 text-left">Job ID</th>
                        <th className="border px-4 py-2 text-left">Status</th>
                        <th className="border px-4 py-2 text-left">Duration</th>
                    </tr>
                </thead>
                <tbody>
                    {logs.map((log) => (
                        <tr key={log.job_id}>
                            <td className="border px-4 py-2">{log.job_id}</td>
                            <td className="border px-4 py-2">{log.status}</td>
                            <td className="border px-4 py-2">{log.duration}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}
