'use client';

import { useState, useEffect } from 'react';
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
  ChevronRight
} from 'lucide-react';
import { compileApp } from '@/lib/api';
import { CompileResponse } from '@/lib/types';

const PIPELINE_STAGES = [
  { id: 1, name: 'Intent Extraction', icon: Zap, description: 'Analyzing requirements and resolving ambiguities' },
  { id: 2, name: 'System Design', icon: Layers, description: 'Architecting entities, flows, and access controls' },
  { id: 3, name: 'Schema Generation', icon: Database, description: 'Synthesizing DB, API, and UI schemas' },
  { id: 4, name: 'Validation & Repair', icon: ShieldCheck, description: 'Enforcing cross-layer consistency and auto-fixing' },
  { id: 5, name: 'Execution Check', icon: Code2, description: 'Final verification in isolated environment' },
];

export default function Home() {
  const [prompt, setPrompt] = useState('Build a CRM with login, contacts, dashboard, admin analytics');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CompileResponse | null>(null);
  const [error, setError] = useState('');
  const [currentStage, setCurrentStage] = useState(0);

  const handleCompile = async () => {
    setLoading(true);
    setError('');
    setResult(null);
    setCurrentStage(1);

    try {
      const stageInterval = setInterval(() => {
        setCurrentStage((prev) => Math.min(prev + 1, 5));
      }, 2500);

      const data = await compileApp(prompt);
      clearInterval(stageInterval);
      setCurrentStage(5);
      setResult(data);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Compile failed';
      setError(message);
      setCurrentStage(0);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-12 pb-20">
      {/* Hero Section */}
      <section className="text-center space-y-4 max-w-3xl mx-auto pt-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-white/50 tracking-tight">
            Forge Your Vision Into Reality
          </h2>
          <p className="text-muted text-lg mt-4 font-light">
            High-fidelity application synthesis with compiler-grade validation.
          </p>
        </motion.div>
      </section>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-8 items-start">
        {/* Left Column — Prompt & Input */}
        <div className="xl:col-span-4 space-y-6">
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="glass rounded-2xl p-6 relative overflow-hidden group"
          >
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <Zap className="w-12 h-12" />
            </div>
            
            <label className="block text-sm font-medium text-white/70 mb-3 uppercase tracking-widest">
              Application Blueprint
            </label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="w-full h-64 bg-black/40 border border-white/10 rounded-xl p-4 text-sm font-mono resize-none focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all placeholder:text-white/20"
              placeholder="Describe the app you want to build in detail..."
              maxLength={2000}
              disabled={loading}
            />
            <div className="flex items-center justify-between mt-4">
              <span className="text-[10px] font-mono text-muted uppercase tracking-tighter">
                {prompt.length} / 2000 chars
              </span>
              <button
                onClick={handleCompile}
                disabled={loading || !prompt.trim()}
                className="relative flex items-center gap-2 bg-white text-black px-6 py-2.5 rounded-full text-sm font-bold hover:bg-white/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-xl shadow-white/5 overflow-hidden group/btn"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Synthesizing...
                  </>
                ) : (
                  <>
                    Compile App
                    <ArrowRight className="w-4 h-4 group-hover/btn:translate-x-1 transition-transform" />
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
                  <li key={i} className="text-xs text-blue-200/70 flex gap-2">
                    <ChevronRight className="w-3 h-3 shrink-0 mt-0.5" />
                    {q}
                  </li>
                ))}
              </ul>
            </motion.div>
          )}
        </div>

        {/* Middle Column — Pipeline Stage Tracker */}
        <div className="xl:col-span-5 space-y-6">
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="glass rounded-2xl p-6"
          >
            <h3 className="text-sm font-medium text-white/70 mb-6 uppercase tracking-widest flex items-center gap-2">
              <Activity className="w-4 h-4" />
              Pipeline Execution
            </h3>
            <div className="space-y-4 relative">
              {/* Connector Line */}
              <div className="absolute left-[19px] top-4 bottom-4 w-[2px] bg-white/5" />
              
              {PIPELINE_STAGES.map((stage, idx) => {
                const isActive = currentStage === stage.id && loading;
                const isCompleted = currentStage > stage.id || (currentStage === 5 && !loading && result);
                const isPending = currentStage < stage.id;

                return (
                  <div key={stage.id} className="relative flex items-start gap-5 group">
                    <div className={`
                      relative z-10 w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-500
                      ${isCompleted ? 'bg-green-500/20 text-green-400 border border-green-500/30 shadow-[0_0_15px_rgba(34,197,94,0.1)]' : 
                        isActive ? 'bg-blue-500 text-white border border-blue-400 shadow-[0_0_20px_rgba(59,130,246,0.4)] animate-glow' : 
                        'bg-white/5 text-white/30 border border-white/5'}
                    `}>
                      {isCompleted ? <CheckCircle2 className="w-5 h-5" /> : <stage.icon className="w-5 h-5" />}
                    </div>
                    
                    <div className="flex-1 pt-1">
                      <div className="flex items-center justify-between">
                        <span className={`text-sm font-bold tracking-tight transition-colors ${isPending ? 'text-white/30' : 'text-white'}`}>
                          {stage.name}
                        </span>
                        {isActive && (
                          <span className="text-[10px] bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded font-mono animate-pulse">
                            Processing...
                          </span>
                        )}
                      </div>
                      <p className={`text-[11px] mt-1 transition-colors ${isPending ? 'text-white/10' : 'text-white/40'}`}>
                        {stage.description}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </motion.div>
        </div>

        {/* Right Column — Insights & Metrics */}
        <div className="xl:col-span-3 space-y-6">
          <AnimatePresence mode="wait">
            {result ? (
              <motion.div 
                key="results"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="space-y-6"
              >
                {/* Score Card */}
                <div className="glass rounded-2xl p-6 border-blue-500/20 bg-gradient-to-br from-blue-500/5 to-transparent">
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-[10px] font-bold uppercase tracking-widest text-muted">Synthesis Status</span>
                    <span className={`text-[10px] font-bold uppercase px-2 py-1 rounded-full ${
                      result.status === 'success' ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 
                      'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                    }`}>
                      {result.status}
                    </span>
                  </div>
                  <div className="space-y-4">
                    <Metric icon={Clock} label="Latency" value={`${result.metrics?.total_latency_ms ?? result.metrics?.latency_ms ?? 0}ms`} />
                    <Metric icon={Zap} label="Repairs" value={String(result.metrics?.repair_count ?? 0)} />
                    <Metric icon={DollarSign} label="Cost" value={`$${(result.metrics?.total_cost_usd ?? 0).toFixed(4)}`} />
                    <Metric icon={ShieldCheck} label="Assumptions" value={String(result.metrics?.assumption_count ?? 0)} />
                  </div>
                </div>

                {/* Execution Health */}
                {result.execution_report && (
                  <div className="glass rounded-2xl p-6">
                    <h4 className="text-[10px] font-bold uppercase tracking-widest text-muted mb-4">System Health</h4>
                    <div className="grid grid-cols-2 gap-3">
                      <HealthToggle label="DB" passed={result.execution_report.db_bootable.passed} />
                      <HealthToggle label="API" passed={result.execution_report.api_complete.passed} />
                      <HealthToggle label="UI" passed={result.execution_report.ui_renderable.passed} />
                      <HealthToggle label="AUTH" passed={result.execution_report.auth_sane.passed} />
                    </div>
                  </div>
                )}

                {/* Call to Action */}
                <motion.a
                  href="/preview"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => {
                    if (typeof window !== 'undefined') {
                      localStorage.setItem('appforge_result', JSON.stringify(result));
                    }
                  }}
                  className="flex items-center justify-between w-full p-4 glass rounded-2xl bg-white/5 border-white/10 hover:border-white/20 transition-all group"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center">
                      <ExternalLink className="w-4 h-4" />
                    </div>
                    <span className="text-sm font-semibold">Explore Configuration</span>
                  </div>
                  <ChevronRight className="w-4 h-4 text-muted group-hover:text-white transition-colors" />
                </motion.a>
              </motion.div>
            ) : (
              <motion.div 
                key="placeholder"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="glass rounded-2xl p-12 text-center border-dashed border-white/10 flex flex-col items-center justify-center gap-4"
              >
                <div className="w-12 h-12 rounded-2xl bg-white/5 flex items-center justify-center text-white/10">
                  <Activity className="w-6 h-6" />
                </div>
                <p className="text-sm text-white/20 font-medium max-w-[150px]">
                  Awaiting compiler initialization...
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}

function Metric({ icon: Icon, label, value }: { icon: any; label: string; value: string }) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-2 text-muted">
        <Icon className="w-3.5 h-3.5" />
        <span className="text-xs font-medium">{label}</span>
      </div>
      <span className="text-xs font-mono font-bold text-white/90">{value}</span>
    </div>
  );
}

function HealthToggle({ label, passed }: { label: string; passed: boolean }) {
  return (
    <div className={`
      flex items-center gap-2 px-3 py-2 rounded-xl border transition-all
      ${passed ? 'bg-green-500/5 border-green-500/10 text-green-400' : 'bg-red-500/5 border-red-500/10 text-red-400'}
    `}>
      {passed ? <CheckCircle2 className="w-3 h-3" /> : <AlertCircle className="w-3 h-3" />}
      <span className="text-[10px] font-bold tracking-tighter">{label}</span>
    </div>
  );
}
