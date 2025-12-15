'use client'

import { Button } from 'components/ui/button'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { toast } from 'sonner'

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

export default function DashboardHome() {
    const router = useRouter()
    const [role, setRole] = useState<'general' | 'logged_in' | null>(null)

    useEffect(() => {
        const checkSession = async () => {
            const res = await fetch(`${API_BASE}/check-session`, { credentials: 'include' })
            if (res.ok) {
                const data = await res.json()
                if (data.role === 'logged_in') {
                    setRole('logged_in')
                } else {
                    router.push('/login')
                }
            } else {
                toast.error('Session invalid. Redirecting...')
                router.push('/login')
            }
        }

        checkSession()
    }, [router])

    if (role === null) {
        return <p className="p-6">Checking session...</p>
    }

    return (
        <div className="p-6 max-w-xl mx-auto space-y-6">
            <h1 className="text-2xl font-bold text-center">Welcome to AmityBot Admin</h1>
            <div className="flex flex-col gap-4">
                <Button variant="outline" onClick={() => router.push('/chat')}>
                    Open Chat Interface
                </Button>
                <Button variant="outline" onClick={() => router.push('/dashboard/kb-upload')}>
                    Upload Knowledge Base
                </Button>
            </div>
        </div>
    )
}
