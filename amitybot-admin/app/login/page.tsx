'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from 'components/ui/button'
import { Input } from 'components/ui/input'
import { toast } from 'sonner'

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

export default function LoginPage() {
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const router = useRouter()

    const handleLogin = async () => {
        if (!username || !password) {
            toast.error('Please enter username and password')
            return
        }

        try {
            const formData = new FormData()
            formData.append('username', username)
            formData.append('password', password)

            const res = await fetch(`${API_BASE}/login`, {
                method: 'POST',
                credentials: 'include',
                body: formData,
            })

            if (res.ok) {
                toast.success('Login successful')
                router.replace('/dashboard/kb-upload')
            } else {
                const data = await res.json()
                toast.error(data.detail || 'Login failed')
            }
        } catch (err) {
            console.error(err)
            toast.error('Something went wrong')
        }
    }

    return (
        <div className="p-6 max-w-sm mx-auto space-y-4">
            <h2 className="text-xl font-semibold text-center">Login to AmityBot</h2>
            <Input
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
            />
            <Input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
            />
            <Button className="w-full" onClick={handleLogin}>
                Login
            </Button>
        </div>
    )
}
