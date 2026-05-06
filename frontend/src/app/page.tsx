'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Zap,
  Layers,
  Database,
  ShieldCheck,
  Code2,
  CheckCircle2,
  Loader2,
  AlertCircle,
  ArrowRight,
  Activity,
  DollarSign,
  Clock,
  ExternalLink,
  ChevronRight,
  Sparkles,
  Command,
  History,
  Trash2,
  RotateCcw,
} from 'lucide-react';
import { compileApp } from '@/lib/api';
import { CompileResponse } from '@/lib/types';

const PIPELINE_STAGES = [
  { id: 1, name: 'Intent Extraction', icon: Zap, description: 'Analyzing requirements and resolving ambiguities', color: '#3b82f6' },
  { id: 2, name: 'System Design', icon: Layers, description: 'Architecting entities, flows, and access controls', color: '#8b5cf6' },
  { id: 3, name: 'Schema Generation', icon: Database, description: 'Synthesizing DB, API, and UI schemas', color: '#06b6d4' },
  { id: 4, name: 'Validation & Repair', icon: ShieldCheck, description: 'Enforcing cross-layer consistency', color: '#f59e0b' },
  { id: 5, name: 'Execution Check', icon: Code2, description: 'Final verification in isolated environment', color: '#10b981' },
];

const PROMPT_SUGGESTIONS = [
  'Build a CRM with login, contacts, dashboard, admin analytics',
  'E-commerce store with cart, payments, inventory management',
  'Project management tool with kanban boards and team chat',
  'Social media app with posts, likes, comments, and messaging',
];

const HERO_WORDS = ['Vision', 'Ideas', 'Concepts', 'Dreams'];

interface HistoryEntry {
  id: string;
  prompt: string;
  status: string;
  timestamp: number;
  latency: number;
  result: CompileResponse;
}

export default function Home() {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CompileResponse | null>(null);
  const [error, setError] = useState('');
  const [currentStage, setCurrentStage] = useState(0);
  const [stageStartTime, setStageStartTime] = useState(0);
  const [stageElapsed, setStageElapsed] = useState(0);
  const [heroWordIndex, setHeroWordIndex] = useState(0);
  const [showConfetti, setShowConfetti] = useState(false);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Load history from localStorage
  useEffect(() => {
    try {
      const stored = localStorage.getItem('appforge_history');
      if (stored) setHistory(JSON.parse(stored));
    } catch (_) {}
  }, []);

  const saveToHistory = (data: CompileResponse, usedPrompt: string) => {
    const entry: HistoryEntry = {
      id: data.job_id || Date.now().toString(),
      prompt: usedPrompt,
      status: data.status,
      timestamp: Date.now(),
      latency: data.metrics?.total_latency_ms ?? data.metrics?.latency_ms ?? 0,
      result: data,
    };
    const updated = [entry, ...history].slice(0, 10); // keep last 10
    setHistory(updated);
    localStorage.setItem('appforge_history', JSON.stringify(updated));
  };

  const deleteHistoryEntry = (id: string) => {
    const updated = history.filter((h) => h.id !== id);
    setHistory(updated);
    localStorage.setItem('appforge_history', JSON.stringify(updated));
  };

  const loadHistoryEntry = (entry: HistoryEntry) => {
    setResult(entry.result);
    setPrompt(entry.prompt);
    setCurrentStage(5);
    setError('');
    localStorage.setItem('appforge_result', JSON.stringify(entry.result));
  };

  // Rotating hero word
  useEffect(() => {
    const interval = setInterval(() => {
      setHeroWordIndex((prev) => (prev + 1) % HERO_WORDS.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  // Stage elapsed timer
  useEffect(() => {
    if (!loading || currentStage === 0) return;
    setStageStartTime(Date.now());
    const timer = setInterval(() => {
      setStageElapsed(Date.now() - stageStartTime);
    }, 100);
    return () => clearInterval(timer);
  }, [loading, currentStage]);

  // Keyboard shortcut: Cmd+Enter to compile
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter' && prompt.trim() && !loading) {
        handleCompile();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [prompt, loading]);

  const handleCompile = async () => {
    setLoading(true);
    setError('');
    setResult(null);
    setCurrentStage(1);
    setShowConfetti(false);

    try {
      const stageInterval = setInterval(() => {
        setCurrentStage((prev) => Math.min(prev + 1, 5));
      }, 2500);

      const data = await compileApp(prompt);
      clearInterval(stageInterval);
      setCurrentStage(5);
      setResult(data);
      saveToHistory(data, prompt);
      if (data.status === 'success') {
        setShowConfetti(true);
        setTimeout(() => setShowConfetti(false), 3000);
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Compile failed';
      setError(message);
      setCurrentStage(0);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-12 pb-20 relative">
      {/* Confetti */}
      <AnimatePresence>
        {showConfetti && <ConfettiBurst />}
      </AnimatePresence>

      {/* Hero Section */}
      <section className="text-center space-y-5 max-w-3xl mx-auto pt-8">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
        >
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-white/10 bg-white/[0.03] text-[11px] font-mono text-blue-400 mb-6 tracking-wider">
            <Sparkles className="w-3 h-3" />
            COMPILER-GRADE SYNTHESIS ENGINE
          </div>
          <h2 className="text-4xl md:text-6xl font-extrabold tracking-tight leading-[1.1]">
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-white via-white to-white/40">
              Forge Your{' '}
            </span>
            <AnimatePresence mode="wait">
              <motion.span
                key={heroWordIndex}
                initial={{ opacity: 0, y: 20, filter: 'blur(8px)' }}
                animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
                exit={{ opacity: 0, y: -20, filter: 'blur(8px)' }}
                transition={{ duration: 0.4 }}
                className="bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-violet-400 to-cyan-400 animate-gradient-text inline-block"
              >
                {HERO_WORDS[heroWordIndex]}
              </motion.span>
            </AnimatePresence>
          </h2>
          <p className="text-muted text-lg mt-5 font-light max-w-lg mx-auto leading-relaxed">
            High-fidelity application synthesis with compiler-grade validation.
            Describe it. We build it.
          </p>
        </motion.div>
      </section>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-8 items-start">
        {/* Left Column — Prompt & Input */}
        <div className="xl:col-span-4 space-y-5">
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="glass rounded-2xl p-6 relative overflow-hidden group"
          >
            <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-15 transition-opacity duration-500">
              <Zap className="w-16 h-16" />
            </div>

            <label className="block text-sm font-medium text-white/70 mb-3 uppercase tracking-widest">
              Application Blueprint
            </label>
            <textarea
              ref={textareaRef}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="w-full h-52 bg-black/40 border border-white/10 rounded-xl p-4 text-sm font-mono resize-none focus:border-blue-500/30 transition-all placeholder:text-white/15"
              placeholder="Describe the app you want to build..."
              maxLength={2000}
              disabled={loading}
            />

            {/* Prompt Suggestions */}
            {!prompt && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
                className="mt-3 space-y-2"
              >
                <p className="text-[10px] uppercase tracking-widest text-white/20 font-bold">Try a suggestion</p>
                <div className="flex flex-wrap gap-2">
                  {PROMPT_SUGGESTIONS.map((s, i) => (
                    <button
                      key={i}
                      onClick={() => setPrompt(s)}
                      className="prompt-chip rounded-lg px-3 py-1.5 text-[11px] text-white/50 hover:text-white/80 font-medium"
                    >
                      {s.length > 40 ? s.slice(0, 40) + '…' : s}
                    </button>
                  ))}
                </div>
              </motion.div>
            )}

            <div className="flex items-center justify-between mt-4">
              <div className="flex items-center gap-3">
                <span className="text-[10px] font-mono text-muted uppercase tracking-tighter">
                  {prompt.length} / 2000
                </span>
                {prompt.length > 0 && (
                  <div className="w-16 h-1 rounded-full bg-white/5 overflow-hidden">
                    <motion.div
                      className="h-full bg-blue-500/50 rounded-full"
                      initial={{ width: 0 }}
                      animate={{ width: `${(prompt.length / 2000) * 100}%` }}
                    />
                  </div>
                )}
              </div>
              <button
                onClick={handleCompile}
                disabled={loading || !prompt.trim()}
                className="relative flex items-center gap-2 bg-gradient-to-r from-blue-500 to-violet-500 text-white px-6 py-2.5 rounded-full text-sm font-bold hover:opacity-90 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-xl shadow-blue-500/20 magnetic-btn"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Synthesizing...
                  </>
                ) : (
                  <>
                    Compile
                    <div className="flex items-center gap-0.5 ml-1 opacity-60">
                      <Command className="w-3 h-3" />
                      <span className="text-[10px]">↵</span>
                    </div>
                  </>
                )}
              </button>
            </div>

            {error && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="mt-4 p-3 bg-red-500/10 border border-red-500/20 rounded-xl flex gap-2 items-start"
              >
                <AlertCircle className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
                <p className="text-xs text-red-400 font-mono leading-relaxed">{error}</p>
              </motion.div>
            )}
          </motion.div>

          {result?.clarifications_needed && result.clarifications_needed.length > 0 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="p-5 bg-blue-500/10 border border-blue-500/20 rounded-2xl space-y-3"
            >
              <div className="flex items-center gap-2 text-blue-400">
                <Activity className="w-4 h-4" />
                <span className="text-sm font-semibold uppercase tracking-wider">Clarifications Needed</span>
              </div>
              <ul className="space-y-2">
                {result.clarifications_needed.map((q, i) => (
                  <motion.li
                    key={i}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.1 }}
                    className="text-xs text-blue-200/70 flex gap-2"
                  >
                    <ChevronRight className="w-3 h-3 shrink-0 mt-0.5" />
                    {q}
                  </motion.li>
                ))}
              </ul>
            </motion.div>
          )}
        </div>

        {/* Middle Column — Pipeline */}
        <div className="xl:col-span-5 space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="glass rounded-2xl p-6"
          >
            <h3 className="text-sm font-medium text-white/70 mb-6 uppercase tracking-widest flex items-center gap-2">
              <Activity className="w-4 h-4" />
              Pipeline Execution
              {loading && (
                <span className="ml-auto text-[10px] font-mono text-blue-400 animate-pulse">
                  Stage {currentStage}/5
                </span>
              )}
            </h3>
            <div className="relative">
              {/* Connector Line */}
              <div className="absolute left-[31px] top-[32px] bottom-[32px] w-[2px] bg-white/5 rounded-full overflow-hidden">
                {loading && (
                  <motion.div
                    className="w-full bg-gradient-to-b from-blue-500 to-violet-500"
                    initial={{ height: '0%' }}
                    animate={{ height: `${(currentStage / 5) * 100}%` }}
                    transition={{ duration: 0.5 }}
                  />
                )}
                {!loading && result && (
                  <div className="w-full h-full bg-gradient-to-b from-green-500/50 to-green-500/20" />
                )}
              </div>

              {PIPELINE_STAGES.map((stage) => {
                const isActive = currentStage === stage.id && loading;
                const isCompleted = currentStage > stage.id || (currentStage === 5 && !loading && result);
                const isPending = currentStage < stage.id;

                return (
                  <motion.div
                    key={stage.id}
                    initial={false}
                    animate={isActive ? { scale: [1, 1.01, 1] } : {}}
                    transition={{ repeat: Infinity, duration: 2 }}
                    className={`relative flex items-start gap-5 p-3 rounded-xl transition-all duration-300 ${
                      isActive ? 'bg-blue-500/5' : ''
                    }`}
                  >
                    <div
                      className={`
                      relative z-10 w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-500 shrink-0
                      ${isCompleted
                        ? 'bg-green-500/20 text-green-400 border border-green-500/30 shadow-[0_0_20px_rgba(34,197,94,0.15)]'
                        : isActive
                        ? 'bg-blue-500 text-white border border-blue-400 shadow-[0_0_30px_rgba(59,130,246,0.4)] animate-glow'
                        : 'bg-white/5 text-white/20 border border-white/5'}
                    `}
                    >
                      {isCompleted ? (
                        <motion.div
                          initial={{ scale: 0, rotate: -90 }}
                          animate={{ scale: 1, rotate: 0 }}
                          transition={{ type: 'spring', stiffness: 300 }}
                        >
                          <CheckCircle2 className="w-5 h-5" />
                        </motion.div>
                      ) : (
                        <stage.icon className="w-5 h-5" />
                      )}
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between gap-2">
                        <span className={`text-sm font-bold tracking-tight transition-colors ${isPending ? 'text-white/20' : 'text-white'}`}>
                          {stage.name}
                        </span>
                        {isActive && (
                          <span className="text-[10px] bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded font-mono animate-pulse shrink-0">
                            Processing...
                          </span>
                        )}
                        {isCompleted && (
                          <motion.span
                            initial={{ opacity: 0, scale: 0.8 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="text-[10px] text-green-400/60 font-mono shrink-0"
                          >
                            ✓ done
                          </motion.span>
                        )}
                      </div>
                      <p className={`text-[11px] mt-0.5 transition-colors ${isPending ? 'text-white/10' : 'text-white/35'}`}>
                        {stage.description}
                      </p>
                      {isActive && (
                        <motion.div
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          className="mt-2 h-1 rounded-full bg-white/5 overflow-hidden"
                        >
                          <div className="h-full w-full progress-bar-shimmer rounded-full" />
                        </motion.div>
                      )}
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>
        </div>

        {/* Right Column — Results */}
        <div className="xl:col-span-3 space-y-6">
          <AnimatePresence mode="wait">
            {result ? (
              <motion.div
                key="results"
                initial={{ opacity: 0, x: 30 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.5 }}
                className="space-y-5"
              >
                {/* Score Card */}
                <div className="glass rounded-2xl p-6 border-blue-500/20 bg-gradient-to-br from-blue-500/5 via-transparent to-violet-500/5 card-lift">
                  <div className="flex items-center justify-between mb-5">
                    <span className="text-[10px] font-bold uppercase tracking-widest text-muted">Synthesis Status</span>
                    <motion.span
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ type: 'spring', stiffness: 400, delay: 0.2 }}
                      className={`text-[10px] font-bold uppercase px-3 py-1 rounded-full ${
                        result.status === 'success'
                          ? 'bg-green-500/10 text-green-400 border border-green-500/20'
                          : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                      }`}
                    >
                      {result.status}
                    </motion.span>
                  </div>
                  <div className="space-y-4">
                    <AnimatedMetric icon={Clock} label="Latency" value={`${result.metrics?.total_latency_ms ?? result.metrics?.latency_ms ?? 0}ms`} delay={0} />
                    <AnimatedMetric icon={Zap} label="Repairs" value={String(result.metrics?.repair_count ?? 0)} delay={0.1} />
                    <AnimatedMetric icon={DollarSign} label="Cost" value={`$${(result.metrics?.total_cost_usd ?? 0).toFixed(4)}`} delay={0.2} />
                    <AnimatedMetric icon={ShieldCheck} label="Assumptions" value={String(result.metrics?.assumption_count ?? 0)} delay={0.3} />
                  </div>
                </div>

                {/* Execution Health */}
                {result.execution_report && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="glass rounded-2xl p-6 card-lift"
                  >
                    <h4 className="text-[10px] font-bold uppercase tracking-widest text-muted mb-4">System Health</h4>
                    <div className="grid grid-cols-2 gap-3">
                      <HealthToggle label="DB" passed={result.execution_report.db_bootable.passed} delay={0.1} />
                      <HealthToggle label="API" passed={result.execution_report.api_complete.passed} delay={0.2} />
                      <HealthToggle label="UI" passed={result.execution_report.ui_renderable.passed} delay={0.3} />
                      <HealthToggle label="AUTH" passed={result.execution_report.auth_sane.passed} delay={0.4} />
                    </div>
                  </motion.div>
                )}

                {/* CTA */}
                <motion.a
                  href="/preview"
                  whileHover={{ scale: 1.02, y: -2 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => {
                    if (typeof window !== 'undefined') {
                      localStorage.setItem('appforge_result', JSON.stringify(result));
                    }
                  }}
                  className="flex items-center justify-between w-full p-4 glass rounded-2xl bg-gradient-to-r from-blue-500/5 to-violet-500/5 border-white/10 hover:border-blue-500/30 transition-all group"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500/20 to-violet-500/20 flex items-center justify-center">
                      <ExternalLink className="w-4 h-4 text-blue-400" />
                    </div>
                    <span className="text-sm font-semibold">Explore Configuration</span>
                  </div>
                  <ChevronRight className="w-4 h-4 text-muted group-hover:text-white group-hover:translate-x-1 transition-all" />
                </motion.a>
              </motion.div>
            ) : (
              <motion.div
                key="placeholder"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="glass rounded-2xl p-12 text-center border-dashed border-white/10 flex flex-col items-center justify-center gap-4"
              >
                <motion.div
                  animate={{ rotate: [0, 5, -5, 0] }}
                  transition={{ repeat: Infinity, duration: 4, ease: 'easeInOut' }}
                  className="w-14 h-14 rounded-2xl bg-gradient-to-br from-white/5 to-white/[0.02] flex items-center justify-center text-white/10 border border-white/5"
                >
                  <Activity className="w-7 h-7" />
                </motion.div>
                <p className="text-sm text-white/20 font-medium max-w-[180px] leading-relaxed">
                  Awaiting compiler initialization...
                </p>
                <div className="flex gap-1.5 mt-2">
                  {[0, 1, 2].map((i) => (
                    <motion.div
                      key={i}
                      className="w-1.5 h-1.5 rounded-full bg-white/10"
                      animate={{ opacity: [0.2, 0.6, 0.2] }}
                      transition={{ repeat: Infinity, duration: 1.5, delay: i * 0.3 }}
                    />
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Compile History Section */}
      {history.length > 0 && (
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mt-4"
        >
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="flex items-center gap-2 text-sm font-medium text-white/40 hover:text-white/70 transition-colors mb-4 group"
          >
            <History className="w-4 h-4" />
            Recent Compilations ({history.length})
            <ChevronRight className={`w-3 h-3 transition-transform ${showHistory ? 'rotate-90' : ''}`} />
          </button>

          <AnimatePresence>
            {showHistory && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="overflow-hidden"
              >
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
                  {history.map((entry, idx) => (
                    <motion.div
                      key={entry.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: idx * 0.05 }}
                      className="glass rounded-xl p-4 group/card hover:border-white/15 transition-all cursor-pointer card-lift"
                      onClick={() => loadHistoryEntry(entry)}
                    >
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <p className="text-xs font-medium text-white/70 line-clamp-2 leading-relaxed flex-1">
                          {entry.prompt}
                        </p>
                        <button
                          onClick={(e) => { e.stopPropagation(); deleteHistoryEntry(entry.id); }}
                          className="p-1 rounded-md opacity-0 group-hover/card:opacity-100 hover:bg-red-500/10 hover:text-red-400 text-white/20 transition-all shrink-0"
                        >
                          <Trash2 className="w-3 h-3" />
                        </button>
                      </div>
                      <div className="flex items-center gap-3 text-[10px] font-mono text-white/30">
                        <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold uppercase ${
                          entry.status === 'success'
                            ? 'bg-green-500/10 text-green-400'
                            : 'bg-amber-500/10 text-amber-400'
                        }`}>
                          {entry.status}
                        </span>
                        <span>{entry.latency}ms</span>
                        <span className="ml-auto">{new Date(entry.timestamp).toLocaleTimeString()}</span>
                      </div>
                      <div className="mt-2 flex items-center gap-1 text-[10px] text-blue-400/50 opacity-0 group-hover/card:opacity-100 transition-opacity">
                        <RotateCcw className="w-3 h-3" />
                        Click to reload
                      </div>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.section>
      )}
    </div>
  );
}

function AnimatedMetric({ icon: Icon, label, value, delay }: { icon: any; label: string; value: string; delay: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay }}
      className="flex items-center justify-between group"
    >
      <div className="flex items-center gap-2.5 text-muted group-hover:text-white/60 transition-colors">
        <Icon className="w-3.5 h-3.5" />
        <span className="text-xs font-medium">{label}</span>
      </div>
      <span className="text-xs font-mono font-bold text-white/90">{value}</span>
    </motion.div>
  );
}

function HealthToggle({ label, passed, delay }: { label: string; passed: boolean; delay: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay }}
      whileHover={{ scale: 1.05 }}
      className={`
        flex items-center gap-2 px-3 py-2.5 rounded-xl border transition-all cursor-default
        ${passed
          ? 'bg-green-500/5 border-green-500/10 text-green-400 hover:bg-green-500/10'
          : 'bg-red-500/5 border-red-500/10 text-red-400 hover:bg-red-500/10'}
      `}
    >
      {passed ? <CheckCircle2 className="w-3.5 h-3.5" /> : <AlertCircle className="w-3.5 h-3.5" />}
      <span className="text-[10px] font-bold tracking-tight">{label}</span>
    </motion.div>
  );
}

function ConfettiBurst() {
  const colors = ['#3b82f6', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ec4899'];
  const particles = Array.from({ length: 40 }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    color: colors[Math.floor(Math.random() * colors.length)],
    delay: Math.random() * 0.5,
    duration: 1.5 + Math.random() * 1.5,
    size: 4 + Math.random() * 6,
  }));

  return (
    <div className="fixed inset-0 pointer-events-none z-50">
      {particles.map((p) => (
        <motion.div
          key={p.id}
          initial={{ y: -20, x: `${p.x}vw`, opacity: 1, rotate: 0 }}
          animate={{ y: '110vh', opacity: 0, rotate: 720 }}
          exit={{ opacity: 0 }}
          transition={{ duration: p.duration, delay: p.delay, ease: 'easeIn' }}
          style={{
            position: 'absolute',
            width: p.size,
            height: p.size,
            background: p.color,
            borderRadius: Math.random() > 0.5 ? '50%' : '2px',
          }}
        />
      ))}
    </div>
  );
}
