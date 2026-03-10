"use client"
import { useState } from 'react';
import { Users, LayoutGrid, Cpu, BookOpen, BarChart3, Megaphone, Loader2 } from 'lucide-react';

const agents = [
    { id: 'Investigator', name: 'Agente Investigador', icon: BookOpen, color: 'text-blue-400', bg: 'bg-blue-500/10' },
    { id: 'Redactor', name: 'Agente Redactor', icon: Edit3, color: 'text-pink-400', bg: 'bg-pink-500/10' },
    { id: 'Analyst', name: 'Agente Analista', icon: BarChart3, color: 'text-amber-400', bg: 'bg-amber-500/10' },
    { id: 'Publisher', name: 'Agente Publicador', icon: Megaphone, color: 'text-rose-400', bg: 'bg-rose-500/10' }
];

// Fallback icon since lucide-react Edit3 may not exist, using LayoutGrid as fallback
function Edit3(props: any) { return <LayoutGrid {...props} /> }

export default function MultiAgentManager() {
    const [objective, setObjective] = useState('');
    const [status, setStatus] = useState<'idle' | 'running' | 'success'>('idle');
    const [result, setResult] = useState('');

    const launchManager = async () => {
        if (!objective.trim()) return;
        setStatus('running');
        setResult('');
        try {
            const res = await fetch('/api/manager', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ objective })
            });
            const data = await res.json();
            setResult(data.response);
            setStatus('success');
        } catch {
            setResult('Error al coordinar los sub-agentes.');
            setStatus('idle');
        }
    };

    return (
        <div className="flex flex-col h-full bg-[#1e1e21] text-zinc-100 overflow-y-auto">
            <header className="px-8 py-10 border-b border-border bg-gradient-to-r from-amber-900/20 to-orange-900/10">
                <div className="flex items-center gap-3 mb-2">
                    <div className="p-2 bg-amber-500/20 rounded-lg">
                        <Users className="w-8 h-8 text-amber-400" />
                    </div>
                    <h1 className="text-3xl font-extrabold tracking-tight">Manager LangGraph</h1>
                </div>
                <p className="text-zinc-400 max-w-2xl text-lg pl-14">
                    Delega una misión global al Director. Él dividirá las tareas, enrutará a cada experto y sintetizará el trabajo final.
                </p>
            </header>

            <div className="p-8 max-w-5xl w-full mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">

                {/* Panel Izquierdo: Control */}
                <div className="col-span-1 lg:col-span-2 space-y-6">
                    <div className="bg-[#2a2a2f] p-6 rounded-2xl border border-white/5 shadow-xl">
                        <label className="text-sm font-medium text-amber-300 mb-2 block uppercase tracking-wider">Misión Global</label>
                        <textarea
                            value={objective}
                            onChange={(e) => setObjective(e.target.value)}
                            disabled={status === 'running'}
                            placeholder="Escribe la misión para toda la agencia..."
                            className="w-full h-32 bg-[#1e1e21] border border-white/10 rounded-xl p-4 text-zinc-200 focus:outline-none focus:border-amber-500/50 resize-none transition-colors"
                        />
                        <button
                            onClick={launchManager}
                            disabled={status === 'running' || !objective.trim()}
                            className="mt-4 w-full flex items-center justify-center gap-2 bg-amber-600 hover:bg-amber-500 text-white font-bold py-3 px-4 rounded-xl disabled:opacity-50 transition-all"
                        >
                            {status === 'running' ? <><Loader2 className="w-5 h-5 animate-spin" /> Coordinando Equipo...</> : <><Cpu className="w-5 h-5" /> Autorizar y Ejecutar</>}
                        </button>
                    </div>

                    {/* Resultado */}
                    {status !== 'idle' && (
                        <div className="bg-[#2a2a2f] p-6 rounded-2xl border border-white/5 shadow-xl">
                            <h3 className="text-lg font-bold text-amber-400 mb-3">Informe de Entrega del Manager</h3>
                            {status === 'running' ? (
                                <div className="h-40 flex items-center justify-center flex-col gap-4 text-zinc-400">
                                    <Loader2 className="w-10 h-10 animate-spin text-amber-500/50" />
                                    <p>Todos los sub-agentes trabajando coordinadamente en backend...</p>
                                </div>
                            ) : (
                                <div className="bg-[#1e1e21] p-4 rounded-xl whitespace-pre-wrap text-zinc-300 border border-white/5 font-serif text-sm leading-relaxed">
                                    {result}
                                </div>
                            )}
                        </div>
                    )}
                </div>

                {/* Panel Derecho: Sub-agentes */}
                <div className="col-span-1 space-y-4">
                    <h3 className="text-sm font-semibold uppercase tracking-wider text-zinc-500 mb-2">Equipo Activo</h3>
                    {agents.map((agent, i) => {
                        const Icon = agent.icon;
                        const isWorking = status === 'running';
                        return (
                            <div key={agent.id} className="bg-[#2a2a2f] p-4 rounded-xl border border-white/5 flex items-center gap-4 transition-all hover:bg-white/5 relative overflow-hidden">
                                <div className={`p-3 rounded-xl ${agent.bg}`}>
                                    <Icon className={`w-6 h-6 ${agent.color}`} />
                                </div>
                                <div>
                                    <h4 className="font-bold text-zinc-200">{agent.name}</h4>
                                    <p className="text-xs text-zinc-500 font-medium tracking-wide">
                                        {isWorking ? (
                                            <span className="text-amber-400 flex items-center gap-1">En espera / Actuando <Loader2 className="w-3 h-3 animate-spin inline ml-1" /></span>
                                        ) : 'Libre - Standby'}
                                    </p>
                                </div>

                                {isWorking && (
                                    <div className={`absolute bottom-0 left-0 h-1 bg-gradient-to-r from-transparent via-${agent.color.split('-')[1]}-500 to-transparent w-full animate-pulse-fast`} style={{ animationDelay: `${i * 0.2}s` }} />
                                )}
                            </div>
                        )
                    })}
                </div>
            </div>
        </div>
    );
}
