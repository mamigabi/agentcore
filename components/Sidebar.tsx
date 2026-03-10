"use client"
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { MessageSquare, Zap, Users, Shield, Settings, Activity } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function Sidebar() {
    const pathname = usePathname();

    const links = [
        { href: '/', icon: MessageSquare, label: 'Chat Principal' },
        { href: '/autonomy', icon: Zap, label: 'Panel Autonomía' },
        { href: '/manager', icon: Users, label: 'Manager / Multi-Agente' },
        { href: '/team', icon: Activity, label: 'Dashboard Estado' },
    ];

    return (
        <div className="w-64 border-r border-border bg-[#111] flex flex-col h-full hidden md:flex">
            <div className="p-4 flex items-center gap-2 border-b border-border">
                <Shield className="w-6 h-6 text-white" />
                <span className="text-xl font-bold tracking-tight text-white">AgentCore</span>
            </div>

            <div className="flex-1 p-3 space-y-2 overflow-y-auto">
                <p className="text-xs font-semibold text-muted-foreground mb-4 mt-2 px-2 uppercase tracking-wider">Módulos</p>
                {links.map((link) => {
                    const Icon = link.icon;
                    const isActive = pathname === link.href;

                    return (
                        <Link
                            key={link.href}
                            href={link.href}
                            className={cn(
                                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors group",
                                isActive
                                    ? "bg-secondary text-white"
                                    : "text-zinc-400 hover:text-white hover:bg-white/5"
                            )}
                        >
                            <Icon className={cn("w-5 h-5", isActive ? "text-white" : "text-zinc-500 group-hover:text-zinc-300")} />
                            {link.label}
                        </Link>
                    )
                })}
            </div>

            <div className="p-4 border-t border-border/40 mt-auto flex items-center gap-3 cursor-pointer hover:bg-white/5 transition-colors">
                <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center text-xs font-bold text-white">
                    AG
                </div>
                <div className="flex flex-col">
                    <span className="text-sm font-medium text-white">Admin Gabi</span>
                    <span className="text-xs text-zinc-500">Nivel 5 Activo</span>
                </div>
                <Settings className="w-4 h-4 ml-auto text-zinc-500" />
            </div>
        </div>
    );
}
