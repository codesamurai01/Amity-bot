import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'AmityBot Admin',
  description: 'Admin dashboard for AmityBot with knowledge base sync and chat support',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-gray-100 text-gray-900 min-h-screen">{children}</body>
    </html>
  )
}
