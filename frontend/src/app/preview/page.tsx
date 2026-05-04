'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FileJson, 
  Search, 
  ShieldAlert, 
  Wrench, 
  Monitor, 
  Copy, 
  Check, 
  ChevronRight,
  Database,
  Layers,
  Zap,
  Code2,
  Lock,
  Layout as LayoutIcon,
  AlertTriangle
} from 'lucide-react';
import { CompileResponse, UIComponent, UIPage } from '@/lib/types';

const TABS = [
  { id: 0, label: 'Intent IR', key: 'intent_ir', icon: Search },
  { id: 1, label: 'System Design', key: 'system_design_ir', icon: Layers },
  { id: 2, label: 'DB Schema', key: 'db', icon: Database },
  { id: 3, label: 'API Schema', key: 'api', icon: Zap },
  { id: 4, label: 'UI Schema', key: 'ui', icon: LayoutIcon },
  { id: 5, label: 'Auth Schema', key: 'auth', icon: Lock },
];

export default function PreviewPage() {
  const [result, setResult] = useState<CompileResponse | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('appforge_result');
      if (stored) {
        try {
          setResult(JSON.parse(stored));
        } catch (_e) {
          // Ignore parse errors from corrupt localStorage
        }
      }
    }
  }, []);

  const handleCopy = (data: any) => {
    navigator.clipboard.writeText(JSON.stringify(data, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!result) {
    return (
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center py-40 space-y-6"
      >
        <div className="w-16 h-16 bg-white/5 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-white/10">
          <FileJson className="w-8 h-8 text-white/20" />
        </div>
        <div>
          <h2 className="text-xl font-bold">No Synthesis Results</h2>
          <p className="text-muted text-sm mt-2">Initialize a compilation from the engine home first.</p>
        </div>
        <a 
          href="/" 
          className="inline-flex items-center gap-2 text-sm text-blue-400 hover:text-blue-300 transition-colors"
        >
          Return to Engine <ChevronRight className="w-4 h-4" />
        </a>
      </motion.div>
    );
  }

  const getTabData = (): unknown => {
    const key = TABS[activeTab].key;
    if (key === 'intent_ir') return result.intent_ir;
    if (key === 'system_design_ir') return result.system_design_ir;
    if (result.app_config) {
      const config = result.app_config as unknown as Record<string, unknown>;
      return config[key];
    }
    return null;
  };

  const tabData = getTabData();

  return (
    <div className="space-y-8 pb-20">
      <header className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Configuration Explorer</h2>
          <p className="text-muted text-sm mt-1">Deep-dive into synthesized artifacts and validation logs.</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="px-3 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-[10px] font-mono text-blue-400 font-bold uppercase tracking-widest">
            {result.job_id}
          </div>
          <div className="px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-[10px] font-mono text-muted font-bold uppercase tracking-widest">
            v{result.app_config?.metadata.version ?? '0.1.0'}
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-8 items-start">
        {/* Schema Viewer */}
        <div className="xl:col-span-8 glass rounded-2xl overflow-hidden border-white/10">
          <div className="flex border-b border-white/10 bg-white/[0.02] overflow-x-auto no-scrollbar">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex items-center gap-2 px-6 py-4 text-xs font-bold uppercase tracking-widest transition-all relative whitespace-nowrap
                  ${activeTab === tab.id ? 'text-blue-400' : 'text-muted hover:text-white'}
                `}
              >
                <tab.icon className="w-3.5 h-3.5" />
                {tab.label}
                {activeTab === tab.id && (
                  <motion.div 
                    layoutId="activeTab"
                    className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]" 
                  />
                )}
              </button>
            ))}
          </div>
          
          <div className="p-6">
            <div className="flex justify-between items-center mb-4">
              <div className="flex items-center gap-2">
                <Code2 className="w-4 h-4 text-blue-400/50" />
                <span className="text-[10px] font-mono text-muted uppercase tracking-tighter">
                  artifacts / {TABS[activeTab].key}.json
                </span>
              </div>
              <button
                onClick={() => handleCopy(tabData)}
                className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest text-muted hover:text-white transition-colors group"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-green-400" /> : <Copy className="w-3.5 h-3.5 group-hover:scale-110 transition-transform" />}
                {copied ? 'Copied' : 'Copy JSON'}
              </button>
            </div>
            
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-black/20 pointer-events-none" />
              <pre className="bg-black/40 border border-white/5 rounded-xl p-6 text-[11px] font-mono overflow-auto max-h-[65vh] leading-relaxed selection:bg-blue-500/30">
                <code className="text-blue-100/80">
                  {tabData ? JSON.stringify(tabData, null, 2) : '/* No data available for this layer */'}
                </code>
              </pre>
            </div>
          </div>
        </div>

        {/* Sidebar Info */}
        <div className="xl:col-span-4 space-y-6">
          {/* Validation & Repair */}
          <div className="glass rounded-2xl p-6 space-y-6">
            <section>
              <div className="flex items-center gap-2 text-red-400 mb-4">
                <ShieldAlert className="w-4 h-4" />
                <h3 className="text-[10px] font-bold uppercase tracking-widest">Validation Integrity</h3>
              </div>
              {result.validation_errors && result.validation_errors.length > 0 ? (
                <div className="space-y-3">
                  {result.validation_errors.map((err: any, i: number) => (
                    <div key={i} className="flex gap-3 p-3 rounded-xl bg-red-500/5 border border-red-500/10">
                      <AlertTriangle className="w-3.5 h-3.5 text-red-500 shrink-0 mt-0.5" />
                      <p className="text-[11px] font-mono text-red-200/60 leading-tight">
                        {typeof err === 'string' ? err : (err.message ?? JSON.stringify(err))}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex items-center gap-3 p-4 rounded-xl bg-green-500/5 border border-green-500/10">
                  <Check className="w-4 h-4 text-green-500" />
                  <span className="text-xs text-green-200/60">Semantic integrity verified.</span>
                </div>
              )}
            </section>

            <div className="h-[1px] bg-white/5" />

            <section>
              <div className="flex items-center gap-2 text-blue-400 mb-4">
                <Wrench className="w-4 h-4" />
                <h3 className="text-[10px] font-bold uppercase tracking-widest">Self-Repair Sequence</h3>
              </div>
              {result.repair_log && result.repair_log.length > 0 ? (
                <div className="space-y-2">
                  {result.repair_log.map((action: any, i: number) => (
                    <div key={i} className="flex items-center justify-between p-2.5 rounded-lg border border-white/5 bg-white/[0.02]">
                      <div className="flex flex-col">
                        <span className="text-[9px] font-mono text-muted uppercase">Pass {action.pass_number} • {action.layer}</span>
                        <span className="text-[11px] font-medium mt-0.5">{action.success ? 'Correction Applied' : 'Repair Attempted'}</span>
                      </div>
                      <div className={`w-1.5 h-1.5 rounded-full ${action.success ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]' : 'bg-amber-500'}`} />
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-muted text-center py-4 italic">No anomalies detected during synthesis.</p>
              )}
            </section>
          </div>

          {/* Visual Architecture Mini-Map */}
          {result.app_config?.ui && (
            <div className="glass rounded-2xl p-6">
              <div className="flex items-center gap-2 text-white/70 mb-4">
                <Monitor className="w-4 h-4" />
                <h3 className="text-[10px] font-bold uppercase tracking-widest">UI Architecture</h3>
              </div>
              <div className="space-y-3">
                {result.app_config.ui.pages.map((page: UIPage) => (
                  <div key={page.id} className="p-3 rounded-xl border border-white/5 bg-white/[0.02] space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] font-bold">{page.title}</span>
                      <span className="text-[9px] font-mono text-muted">{page.route}</span>
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {page.components.map((comp: UIComponent, j: number) => (
                        <div key={j} className="px-2 py-0.5 rounded-md bg-blue-500/10 border border-blue-500/20 text-[9px] text-blue-300 font-mono">
                          {comp.type}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
