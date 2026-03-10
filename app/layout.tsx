import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Sidebar from '@/components/Sidebar'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
    title: 'AgentCore - AI Autonomous Agent',
    description: 'Pro interface for AgentCore multi-agent operations.',
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en" className="dark">
            <body className={`${inter.className} flex h-screen overflow-hidden bg-background`}>
                <Sidebar />
                <main className="flex-1 overflow-hidden relative">
                    {children}
                </main>
            </body>
        </html>
    )
}
