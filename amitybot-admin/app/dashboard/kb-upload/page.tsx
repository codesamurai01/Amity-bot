'use client'

import { Button } from 'components/ui/button'
import { Input } from 'components/ui/input'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { toast } from 'sonner'

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

export default function KBUploadPage() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(true)
  const [role, setRole] = useState<string>('general')
  const router = useRouter()

  // Check session on load
  useEffect(() => {
    const fetchSession = async () => {
      try {
        const res = await fetch(`${API_BASE}/check-session`, {
          credentials: 'include',
        })
        const data = await res.json()
        if (data.role !== 'logged_in') {
          router.replace('/login')
        } else {
          setRole('logged_in')
        }
      } catch (error) {
        console.error('Session check failed:', error)
        router.replace('/login')
      } finally {
        setLoading(false)
      }
    }

    fetchSession()
  }, [router])

  const handleUpload = async () => {
    if (!file) {
      toast.error('Please select a file first.')
      return
    }

    const formData = new FormData()
    formData.append('file', file)

    const res = await fetch(`${API_BASE}/kb-upload`, {
      method: 'POST',
      credentials: 'include',
      body: formData,
    })

    if (res.ok) toast.success('✅ File uploaded and indexed')
    else {
      const data = await res.json()
      toast.error(`❌ Upload failed: ${data.message || 'Unknown error'}`)
    }
  }

  const handleReindex = async () => {
    const res = await fetch(`${API_BASE}/reindex`, {
      method: 'POST',
      credentials: 'include',
    })

    if (res.ok) toast.success('✅ Reindexing triggered')
    else toast.error('❌ Failed to reindex')
  }

  const handleLogout = async () => {
    await fetch(`${API_BASE}/logout`, {
      method: 'POST',
      credentials: 'include',
    })
    toast.success('Logged out')
    router.push('/login')
  }

  if (loading) {
    return (
      <div className="p-6">
        <p className="text-gray-600">Checking login status...</p>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">Knowledge Base Upload</h2>
        <Button variant="outline" onClick={handleLogout}>
          Logout
        </Button>
      </div>
      <Input
        type="file"
        accept=".txt,.md,.pdf,.png,.jpg,.jpeg"
        onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
          setFile(e.target.files?.[0] || null)
        }
      />
      <div className="flex gap-4">
        <Button onClick={handleUpload}>Upload</Button>
        <Button onClick={handleReindex} disabled={!file}>
          Sync Now
        </Button>
      </div>
    </div>
  )
}
