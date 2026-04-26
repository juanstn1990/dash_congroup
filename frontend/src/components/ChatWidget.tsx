import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageCircle, X, Send, Bot, User, ChevronDown, ChevronUp, Loader2 } from 'lucide-react';
import { apiFetch } from '@/lib/api';
import { cn } from '@/lib/utils';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  sql?: string;
  columns?: string[];
  data?: Record<string, unknown>[];
  error?: string;
}

const SUGGESTIONS = [
  '¿Quién vendió más en 2025?',
  '¿Cuántos pedidos hay pendientes?',
  '¿Cuál es el BB3 promedio por vendedor?',
  '¿Qué tipo de venta es más frecuente?',
];

function SqlBlock({ sql }: { sql: string }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="mt-2 rounded-lg border border-slate-200 overflow-hidden text-[10px] md:text-[11px]">
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between px-2.5 py-1.5 bg-slate-50 text-slate-500 hover:bg-slate-100 transition-colors"
      >
        <span className="font-mono font-medium">SQL generado</span>
        {open ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
      </button>
      {open && (
        <pre className="p-2.5 bg-slate-900 text-emerald-400 overflow-x-auto font-mono leading-relaxed">
          {sql}
        </pre>
      )}
    </div>
  );
}

function DataTable({ columns, data }: { columns: string[]; data: Record<string, unknown>[] }) {
  if (!data.length) return null;
  return (
    <div className="mt-2 overflow-auto max-h-48 rounded-lg border border-slate-200 text-[10px] md:text-[11px]">
      <table className="w-full min-w-max">
        <thead className="sticky top-0 bg-congroup-blue text-white">
          <tr>
            {columns.map((c) => (
              <th key={c} className="px-2 py-1 text-left font-semibold whitespace-nowrap">{c}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={i} className={i % 2 === 1 ? 'bg-slate-50' : 'bg-white'}>
              {columns.map((c) => (
                <td key={c} className="px-2 py-1 whitespace-nowrap">
                  {row[c] == null ? '—' : String(row[c])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 300);
    }
  }, [open]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const send = async (text?: string) => {
    const question = (text ?? input).trim();
    if (!question || loading) return;
    setInput('');

    const userMsg: ChatMessage = { role: 'user', content: question };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const history = messages.map((m) => ({ role: m.role, content: m.content }));
      const res = await apiFetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, history }),
      });
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: res.answer,
          sql: res.sql,
          columns: res.columns,
          data: res.data,
          error: res.error,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Error al conectar con el servidor. Intenta de nuevo.' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Floating button */}
      <motion.button
        onClick={() => setOpen((v) => !v)}
        whileTap={{ scale: 0.93 }}
        className={cn(
          'fixed bottom-5 right-5 z-[80] w-13 h-13 rounded-full shadow-xl flex items-center justify-center transition-colors',
          open
            ? 'bg-slate-700 hover:bg-slate-800'
            : 'bg-congroup-blue hover:bg-congroup-blue-med'
        )}
        style={{ width: 52, height: 52 }}
        aria-label="Abrir chat"
      >
        <AnimatePresence mode="wait" initial={false}>
          {open ? (
            <motion.span key="close" initial={{ rotate: -90, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} exit={{ rotate: 90, opacity: 0 }} transition={{ duration: 0.15 }}>
              <X className="w-5 h-5 text-white" />
            </motion.span>
          ) : (
            <motion.span key="open" initial={{ rotate: 90, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} exit={{ rotate: -90, opacity: 0 }} transition={{ duration: 0.15 }}>
              <MessageCircle className="w-5 h-5 text-white" />
            </motion.span>
          )}
        </AnimatePresence>
      </motion.button>

      {/* Chat panel */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.97 }}
            transition={{ duration: 0.2, ease: [0.25, 0.46, 0.45, 0.94] }}
            className="fixed z-[79] shadow-2xl flex flex-col bg-white border border-slate-200 rounded-2xl overflow-hidden"
            style={{
              bottom: 68,
              right: 20,
              width: 'min(420px, calc(100vw - 24px))',
              height: 'min(580px, calc(100dvh - 90px))',
            }}
          >
            {/* Header */}
            <div className="flex items-center gap-2.5 px-4 py-3 bg-congroup-blue text-white shrink-0">
              <div className="w-7 h-7 rounded-full bg-white/15 flex items-center justify-center">
                <Bot className="w-4 h-4" />
              </div>
              <div>
                <p className="text-sm font-semibold leading-tight">Asistente Congroup</p>
                <p className="text-[10px] text-blue-200/80">Pregunta en lenguaje natural</p>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-3 py-3 space-y-3 overscroll-contain">
              {messages.length === 0 && (
                <div className="space-y-3">
                  <p className="text-xs text-slate-400 text-center pt-2">
                    Puedo responder preguntas sobre ventas, vendedores y datos de la base de datos.
                  </p>
                  <div className="grid grid-cols-1 gap-1.5">
                    {SUGGESTIONS.map((s) => (
                      <button
                        key={s}
                        onClick={() => send(s)}
                        className="text-left text-[11px] px-3 py-2 rounded-lg bg-slate-50 hover:bg-blue-50 border border-slate-200 hover:border-blue-200 text-slate-600 hover:text-congroup-blue transition-colors"
                      >
                        {s}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {messages.map((msg, i) => (
                <div key={i} className={cn('flex gap-2', msg.role === 'user' ? 'justify-end' : 'justify-start')}>
                  {msg.role === 'assistant' && (
                    <div className="w-6 h-6 rounded-full bg-congroup-blue/10 flex items-center justify-center shrink-0 mt-0.5">
                      <Bot className="w-3.5 h-3.5 text-congroup-blue" />
                    </div>
                  )}
                  <div className={cn('max-w-[85%] space-y-1', msg.role === 'user' ? 'items-end' : 'items-start')}>
                    <div
                      className={cn(
                        'px-3 py-2 rounded-2xl text-[12px] leading-relaxed',
                        msg.role === 'user'
                          ? 'bg-congroup-blue text-white rounded-tr-sm'
                          : 'bg-slate-100 text-slate-800 rounded-tl-sm'
                      )}
                    >
                      {msg.content}
                    </div>
                    {msg.error && (
                      <p className="text-[10px] text-red-500 px-1">Error SQL: {msg.error}</p>
                    )}
                    {msg.sql && <SqlBlock sql={msg.sql} />}
                    {msg.columns && msg.data && (
                      <DataTable columns={msg.columns} data={msg.data} />
                    )}
                  </div>
                  {msg.role === 'user' && (
                    <div className="w-6 h-6 rounded-full bg-congroup-blue flex items-center justify-center shrink-0 mt-0.5">
                      <User className="w-3.5 h-3.5 text-white" />
                    </div>
                  )}
                </div>
              ))}

              {loading && (
                <div className="flex gap-2 justify-start">
                  <div className="w-6 h-6 rounded-full bg-congroup-blue/10 flex items-center justify-center shrink-0">
                    <Bot className="w-3.5 h-3.5 text-congroup-blue" />
                  </div>
                  <div className="px-3 py-2.5 rounded-2xl rounded-tl-sm bg-slate-100 flex items-center gap-1.5">
                    <Loader2 className="w-3.5 h-3.5 text-slate-400 animate-spin" />
                    <span className="text-[11px] text-slate-400">Consultando...</span>
                  </div>
                </div>
              )}

              <div ref={bottomRef} />
            </div>

            {/* Input */}
            <div className="shrink-0 px-3 py-2.5 border-t border-slate-100 bg-white">
              <form
                onSubmit={(e) => { e.preventDefault(); send(); }}
                className="flex gap-2 items-center"
              >
                <input
                  ref={inputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Escribe tu pregunta..."
                  disabled={loading}
                  className="flex-1 text-[12px] px-3 py-2 rounded-xl border border-slate-200 bg-slate-50 focus:outline-none focus:ring-2 focus:ring-congroup-blue/30 focus:border-congroup-blue/50 disabled:opacity-50 placeholder:text-slate-400"
                />
                <button
                  type="submit"
                  disabled={loading || !input.trim()}
                  className="w-8 h-8 rounded-xl bg-congroup-blue hover:bg-congroup-blue-med disabled:opacity-40 flex items-center justify-center transition-colors shrink-0"
                >
                  <Send className="w-3.5 h-3.5 text-white" />
                </button>
              </form>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
