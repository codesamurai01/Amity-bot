'use client';

import { cn } from 'lib/utils'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

const navItems = [
  { href: '/dashboard/kb-upload', label: 'KB Upload' },
  { href: '/dashboard/chat', label: 'Chat' },
  { href: '/dashboard/leads', label: 'Leads' },
  { href: '/dashboard/sync-logs', label: 'Sync Logs' }
]

export default function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-64 bg-white border-r p-4 space-y-2">
      <h1 className="text-xl font-bold mb-4">AmityBot Admin</h1>
      {navItems.map(({ href, label }) => (
        <Link
          key={href}
          href={href}
          className={cn(
            'block p-2 rounded hover:bg-gray-100',
            pathname === href && 'bg-gray-200 font-semibold'
          )}
        >
          {label}
        </Link>
      ))}
    </aside>
  )
}
