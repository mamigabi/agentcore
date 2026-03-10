"use client"
import { useEffect, useState } from 'react';
import { Activity, ServerPulse, Database, Clock, BrainCircuit } from 'lucide-react';

export default function Dashboard() {
    const [teamStatus, setTeamStatus] = useState<Record<string, string>>({});
    const [sysHealth, setSysHealth] = useState<any>(null);

    useEffect(() => {
        // Polling API every 5s for realtime simulation
        const fetchData = async () => {
            try {
                const resTeam = await fetch('/api/team');
                const dtTeam = await resTeam.json();
                setTeamStatus(dtTeam.team_roles || {});

                const resHealth = await fetch('/api/health');
                const dtHealth = await resHealth.json();
                setSysHealth(dtHealth);
            } catch (e) {
                console.error(e);
            }
        };

        fetchData();
        const intv = setInterval(fetchData, 5000);
        return () => clearInterval(intv);
    }, []);

    return (
        <div className="flex flex-col h-full bg-[#1e1e21] text-zinc-100 overflow-y-auto">
            <header className="px-8 py-8 border-b border-border bg-[#111]">
                <div className="flex items-center gap-3">
                    <Activity className="w-8 h-8 text-emerald-400" />
                    <h1 className="text-3xl font-extrabold tracking-tight">System Global Dashboard</h1>
                </div>
            </header>

            <div className="p-8 max-w-6xl mx-auto w-full grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

                {/* API Health Card */}
                <div className="bg-gradient-to-br from-zinc-800 to-zinc-900 p-6 rounded-2xl border border-white/10 shadow-lg relative overflow-hidden group">
                    <ServerPulse className="w-10 h-10 text-emerald-400 mb-4 opacity-75" />
                    <h3 className="text-lg font-bold text-white mb-2">Backend & API Status</h3>
                    <div className="space-y-2 mt-4 text-sm font-medium">
                        <div className="flex justify-between items-center bg-black/20 p-2 text-emerald-400 rounded-md">
                            <span>Punto de entrada API:</span> <span className="uppercase text-xs font-bold tracking-widest">{sysHealth ? sysHealth.status : 'Loading...'}</span>
                        </div>
                        <div className="flex justify-between items-center text-zinc-400 px-2">
                            <span>Motor LLM Principal:</span> <span>{sysHealth ? sysHealth.models.primary : '--'}</span>
                        </div>
                        <div className="flex justify-between items-center text-zinc-400 px-2">
                            <span>Motor Fallback Groq:</span> <span>{sysHealth ? sysHealth.models.fallback : '--'}</span>
                        </div>
                    </div>
                    <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/10 blur-3xl rounded-full group-hover:bg-emerald-500/20 transition-all" />
                </div>

                {/* Database & Memory Card */}
                <div className="bg-gradient-to-br from-zinc-800 to-zinc-900 p-6 rounded-2xl border border-white/10 shadow-lg relative overflow-hidden group">
                    <Database className="w-10 h-10 text-cyan-400 mb-4 opacity-75" />
                    <h3 className="text-lg font-bold text-white mb-2">Supabase & pgvector</h3>
                    <div className="space-y-2 mt-4 text-sm font-medium">
                        <div className="flex justify-between items-center bg-black/20 p-2 text-cyan-400 rounded-md">
                            <span>Memoria Semántica:</span> <span className="uppercase text-xs font-bold tracking-widest">Activa</span>
                        </div>
                        <div className="flex justify-between items-center text-zinc-400 px-2">
                            <span>Base de Datos:</span> <span>Conectado</span>
                        </div>
                        <div className="flex justify-between items-center text-zinc-400 px-2">
                            <span>Vector Embeddings:</span> <span>text-embedding-004</span>
                        </div>
                    </div>
                    <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-500/10 blur-3xl rounded-full group-hover:bg-cyan-500/20 transition-all" />
                </div>

                {/* Vercel Cron Card */}
                <div className="bg-gradient-to-br from-zinc-800 to-zinc-900 p-6 rounded-2xl border border-white/10 shadow-lg relative overflow-hidden group">
                    <Clock className="w-10 h-10 text-pink-400 mb-4 opacity-75" />
                    <h3 className="text-lg font-bold text-white mb-2">Vercel Cron Jobs</h3>
                    <div className="space-y-2 mt-4 text-sm font-medium">
                        <div className="flex justify-between items-center bg-black/20 p-2 text-pink-400 rounded-md">
                            <span>Sincronización:</span> <span className="uppercase text-xs font-bold tracking-widest">Operativo</span>
                        </div>
                        <div className="flex justify-between items-center text-zinc-400 px-2">
                            <span>Morning Task:</span> <span>09:00 AM (UTC)</span>
                        </div>
                        <div className="flex justify-between items-center text-zinc-400 px-2">
                            <span>Evening Task:</span> <span>20:00 PM (UTC)</span>
                        </div>
                    </div>
                    <div className="absolute top-0 right-0 w-32 h-32 bg-pink-500/10 blur-3xl rounded-full group-hover:bg-pink-500/20 transition-all" />
                </div>

            </div>

            <div className="px-8 max-w-6xl mx-auto w-full mb-8">
                <h2 className="text-xl font-bold mb-4 flex items-center gap-2"><BrainCircuit className="w-5 h-5 text-indigo-400" /> Sub-Agent Fleet Status</h2>
                <div className="bg-zinc-800/50 rounded-2xl border border-white/10 overflow-hidden">
                    <table className="w-full text-left text-sm">
                        <thead className="bg-black/40 text-zinc-400 uppercase text-xs font-semibold tracking-wider">
                            <tr>
                                <th className="px-6 py-4">Agente</th>
                                <th className="px-6 py-4">Status Interno</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {Object.keys(teamStatus).map(key => (
                                <tr key={key} className="hover:bg-white/5 transition-colors">
                                    <td className="px-6 py-4 font-medium text-white flex items-center gap-2">
                                        <span className="w-2 h-2 rounded-full bg-emerald-500" />
                                        {key}
                                    </td>
                                    <td className="px-6 py-4 text-zinc-300">
                                        <span className="bg-zinc-800 px-3 py-1 rounded-md text-xs font-mono">{teamStatus[key]}</span>
                                    </td>
                                </tr>
                            ))}
                            {!Object.keys(teamStatus).length && (
                                <tr>
                                    <td colSpan={2} className="text-center py-8 text-zinc-500">Recopilando datos del servidor...</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
