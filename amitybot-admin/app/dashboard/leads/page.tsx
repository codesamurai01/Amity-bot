'use client'
import { useEffect, useState } from 'react'

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

export default function LeadsPage() {
    const [leads, setLeads] = useState<any[]>([])

    useEffect(() => {
        fetch(`${API_BASE}/leads`)
            .then((res) => res.json())
            .then((data) => setLeads(data || []))
    }, [])

    return (
        <div className="p-6">
            <h2 className="text-xl font-semibold mb-4">Leads</h2>
            <table className="w-full border-collapse">
                <thead>
                    <tr className="bg-gray-100">
                        <th className="border px-4 py-2 text-left">ID</th>
                        <th className="border px-4 py-2 text-left">Name</th>
                        <th className="border px-4 py-2 text-left">Status</th>
                    </tr>
                </thead>
                <tbody>
                    {leads.map((lead) => (
                        <tr key={lead.id}>
                            <td className="border px-4 py-2">{lead.id}</td>
                            <td className="border px-4 py-2">{lead.name}</td>
                            <td className="border px-4 py-2">{lead.status}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}
