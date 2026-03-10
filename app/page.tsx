"use client"
import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, Loader2 } from 'lucide-react';

type Message = { id: string, role: 'user' | 'assistant', content: string };

export default function Home() {
    const [messages, setMessages] = useState<Message[]>([
        { id: '1', role: 'assistant', content: 'Hola Gabi. AgentCore inicializado. ¿En qué te ayudo hoy?' }
    ]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    // Create a unique session per tab load
    const [sessionId] = useState(() => `sess_${Math.random().toString(36).substring(2, 9)}`);

    useEffect(() => {
        if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }, [messages]);

    const handleSend = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isTyping) return;

        const newMsg: Message = { id: Date.now().toString(), role: 'user', content: input };
        setMessages(prev => [...prev, newMsg]);
        setInput('');
        setIsTyping(true);

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId, message: newMsg.content })
            });
            const data = await res.json();
            setMessages(prev => [...prev, { id: Date.now().toString(), role: 'assistant', content: data.response || "Error en el agente: no response." }]);
        } catch (error) {
            setMessages(prev => [...prev, { id: Date.now().toString(), role: 'assistant', content: "Error de conexión con el backend." }]);
        } finally {
            setIsTyping(false);
        }
    };

    return (
        <div className="flex flex-col h-full bg-[#1e1e21] text-zinc-100">
            <header className="flex items-center justify-between px-6 py-4 border-b border-border bg-[#111]/50 backdrop-blur-md sticky top-0 z-10">
                <div className="flex items-center gap-3">
                    <Bot className="w-6 h-6 text-purple-400" />
                    <h1 className="text-xl font-bold">AgentCore <span className="text-zinc-500 font-normal ml-2 text-sm">| Chat Principal</span></h1>
                </div>
                <div className="flex items-center gap-2 text-xs font-semibold px-3 py-1 bg-white/5 rounded-full border border-white/10 text-emerald-400">
                    <Sparkles className="w-3 h-3" />
                    <span className="tracking-wide">Gemini 2.5 Flash</span>
                </div>
            </header>

            <div className="flex-1 overflow-y-auto w-full max-w-4xl mx-auto p-4 md:p-8 space-y-6" ref={scrollRef}>
                {messages.map((m) => (
                    <div key={m.id} className={`flex w-full gap-4 animate-fade-in-up ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        {m.role === 'assistant' && (
                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center shrink-0">
                                <Bot className="w-5 h-5 text-white" />
                            </div>
                        )}

                        <div className={`px-5 py-3.5 max-w-[85%] leading-relaxed whitespace-pre-wrap rounded-2xl ${m.role === 'user'
                                ? 'bg-zinc-800 text-white rounded-br-sm'
                                : 'bg-[#2a2a2f] text-zinc-200 border border-white/5 rounded-bl-sm shadow-sm'
                            }`}>
                            {m.content}
                        </div>

                        {m.role === 'user' && (
                            <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center shrink-0">
                                <User className="w-5 h-5 text-white" />
                            </div>
                        )}
                    </div>
                ))}
                {isTyping && (
                    <div className="flex w-full gap-4 animate-fade-in-up">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center shrink-0">
                            <Bot className="w-5 h-5 text-white" />
                        </div>
                        <div className="px-5 py-3.5 bg-[#2a2a2f] text-zinc-400 border border-white/5 rounded-2xl rounded-bl-sm shadow-sm flex items-center gap-2">
                            <Loader2 className="w-4 h-4 animate-spin text-purple-400" />
                            Analizando e interactuando...
                        </div>
                    </div>
                )}
            </div>

            <div className="p-4 mx-auto w-full max-w-4xl pb-8">
                <form onSubmit={handleSend} className="relative flex items-center bg-[#2f2f36] rounded-xl border border-white/10 shadow-lg group focus-within:ring-2 focus-within:ring-purple-500/50 transition-all">
                    <input
                        type="text"
                        placeholder="Escribe tu prompt al agente..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        className="flex-1 bg-transparent border-none py-4 px-5 text-white placeholder-zinc-400 focus:outline-none focus:ring-0"
                        disabled={isTyping}
                    />
                    <button
                        type="submit"
                        disabled={isTyping || !input.trim()}
                        className="absolute right-2 p-2.5 rounded-lg bg-white/10 text-white hover:bg-purple-500 disabled:opacity-50 disabled:hover:bg-white/10 transition-colors"
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </form>
                <p className="text-center text-xs text-zinc-500 mt-4">AgentCore puede cometer errores. Considera verificar la información importante.</p>
            </div>
        </div>
    );
}
