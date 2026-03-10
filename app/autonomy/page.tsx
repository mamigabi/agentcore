"use client"
import { useState } from 'react';
import { Target, Zap, ChevronRight, CheckCircle2, Play, Loader2 } from 'lucide-react';

export default function AutonomyPanel() {
    const [objective, setObjective] = useState('');
    const [status, setStatus] = useState<'idle' | 'running' | 'success'>('idle');
    const [result, setResult] = useState('');

    const executeAutonomy = async () => {
        if (!objective.trim()) return;
        setStatus('running');
        setResult('');

        try {
            const res = await fetch('/api/autonomy', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ objective })
            });
            const data = await res.json();
            setResult(data.response);
            setStatus('success');
        } catch (e) {
            setResult('Error al ejecutar autonomía. Revisa los logs.');
            setStatus('idle');
        }
    };

    return (
        <div className="flex flex-col h-full bg-[#1e1e21] text-zinc-100 overflow-y-auto">
            <header className="px-8 py-10 border-b border-border bg-gradient-to-r from-indigo-900/20 to-purple-900/10">
                <div className="flex items-center gap-3 mb-2">
                    <div className="p-2 bg-indigo-500/20 rounded-lg">
                        <Zap className="w-8 h-8 text-indigo-400" />
                    </div>
                    <h1 className="text-3xl font-extrabold tracking-tight">Panel de Autonomía</h1>
                </div>
                <p className="text-zinc-400 max-w-2xl text-lg pl-14">
                    Define un objetivo complejo. El Agente Inteligente razonará, usará sus herramientas y no se detendrá hasta cumplir la misión.
                </p>
            </header>

            <div className="p-8 max-w-4xl w-full mx-auto space-y-8 mt-4">

                <div className="bg-[#2a2a2f] p-6 rounded-2xl border border-white/5 shadow-xl">
                    <label className="flex items-center gap-2 text-sm font-medium text-indigo-300 mb-3 uppercase tracking-wider">
                        <Target className="w-4 h-4" /> Objetivo Estratégico
                    </label>
                    <textarea
                        value={objective}
                        onChange={(e) => setObjective(e.target.value)}
                        disabled={status === 'running'}
                        placeholder="Ejemplo: Averigua las últimas 3 tendencias sobre agentes IA en HackerNews, resúmelas y reescríbelas en tono corporativo para un email."
                        className="w-full h-32 bg-[#1e1e21] border border-white/10 rounded-xl p-4 text-zinc-200 placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 resize-none transition-all"
                    />
                    <div className="mt-4 flex justify-end">
                        <button
                            onClick={executeAutonomy}
                            disabled={status === 'running' || !objective.trim()}
                            className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-3 rounded-xl font-medium transition-all hover:shadow-[0_0_20px_rgba(79,70,229,0.4)] disabled:opacity-50 disabled:pointer-events-none"
                        >
                            {status === 'running' ? (
                                <><Loader2 className="w-5 h-5 animate-spin" /> Procesando Operación...</>
                            ) : (
                                <><Play className="w-5 h-5" /> Iniciar Misión Autónoma</>
                            )}
                        </button>
                    </div>
                </div>

                {status !== 'idle' && (
                    <div className={`p-6 rounded-2xl border transition-all duration-500 ${status === 'success' ? 'bg-emerald-900/10 border-emerald-500/30' : 'bg-indigo-900/10 border-indigo-500/30'} shadow-lg`}>
                        <div className="flex items-center gap-3 mb-4">
                            {status === 'success' ? (
                                <CheckCircle2 className="w-6 h-6 text-emerald-400" />
                            ) : (
                                <div className="w-6 h-6 rounded-full border-2 border-indigo-400 border-t-transparent animate-spin" />
                            )}
                            <h2 className={`text-xl font-bold ${status === 'success' ? 'text-emerald-400' : 'text-indigo-400'}`}>
                                {status === 'success' ? 'Misión Completada Exitosamente' : 'Agente Operando en Segundo Plano...'}
                            </h2>
                        </div>

                        <div className="bg-[#1e1e21] rounded-xl p-5 border border-white/5 font-mono text-sm leading-relaxed text-zinc-300 whitespace-pre-wrap max-h-96 overflow-y-auto custom-scrollbar">
                            {result || 'Ejecutando ciclos ReAct (Pensamiento -> Acción -> Observación). El pipeline de razonamiento interno se mostrará en los logs del backend. Por favor espera el informe final...'}
                        </div>
                    </div>
                )}

            </div>
        </div>
    );
}
