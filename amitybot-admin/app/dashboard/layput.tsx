// app/dashboard/layout.tsx
'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { toast } from 'sonner'

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
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
        toast.error('Session expired. Redirecting...')
        router.push('/login')
      }
    }

    checkSession()
  }, [router])

  const handleLogout = async () => {
    await fetch(`${API_BASE}/logout`, { method: 'POST', credentials: 'include' })
    toast.success('Logged out')
    router.push('/login')
  }

  if (role === null) {
    return <p className="p-6">Checking session...</p>
  }

  return (
    <div>
      <nav className="bg-gray-900 text-white px-6 py-4 flex items-center justify-between">
        <div className="space-x-4">
          <Link href="/dashboard" className="hover:underline">
            Home
          </Link>
          <Link href="/chat" className="hover:underline">
            Chat
          </Link>
          <Link href="/dashboard/kb-upload" className="hover:underline">
            KB Upload
          </Link>
        </div>
        <button onClick={handleLogout} className="text-sm bg-red-500 px-3 py-1 rounded hover:bg-red-600">
          Logout
        </button>
      </nav>
      <main className="p-6">{children}</main>
    </div>
  )
}
