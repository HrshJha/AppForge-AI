'use client';

import { useEffect, useState, useMemo } from 'react';
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
  AlertTriangle,
  Download,
  Maximize2,
  Minimize2,
} from 'lucide-react';
import { CompileResponse, UIComponent, UIPage } from '@/lib/types';

const TABS = [
  { id: 0, label: 'Intent IR', key: 'intent_ir', icon: Search, color: '#3b82f6' },
  { id: 1, label: 'System Design', key: 'system_design_ir', icon: Layers, color: '#8b5cf6' },
  { id: 2, label: 'DB Schema', key: 'db', icon: Database, color: '#06b6d4' },
  { id: 3, label: 'API Schema', key: 'api', icon: Zap, color: '#f59e0b' },
  { id: 4, label: 'UI Schema', key: 'ui', icon: LayoutIcon, color: '#10b981' },
  { id: 5, label: 'Auth Schema', key: 'auth', icon: Lock, color: '#ec4899' },
];

function syntaxHighlightJSON(json: string): string {
  return json
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(
      /("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false)\b|-?\d+(?:\.\d*)?(?:[eE][+-]?\d+)?|null)/g,
      (match) => {
        let cls = 'json-number';
        if (/^"/.test(match)) {
          if (/:$/.test(match)) {
            cls = 'json-key';
            match = match.replace(/:$/, '') + '<span class="json-colon">:</span>';
          } else {
            cls = 'json-string';
          }
        } else if (/true|false/.test(match)) {
          cls = 'json-boolean';
        } else if (/null/.test(match)) {
          cls = 'json-null';
        }
        return `<span class="${cls}">${match}</span>`;
      }
    )
    .replace(/[[\]{}]/g, (m) => `<span class="json-bracket">${m}</span>`);
}

export default function PreviewPage() {
  const [result, setResult] = useState<CompileResponse | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const [copied, setCopied] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

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

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight' && !e.metaKey) {
        setActiveTab((prev) => Math.min(prev + 1, TABS.length - 1));
      } else if (e.key === 'ArrowLeft' && !e.metaKey) {
        setActiveTab((prev) => Math.max(prev - 1, 0));
      } else if ((e.metaKey || e.ctrlKey) && e.key === 'f') {
        e.preventDefault();
        document.getElementById('json-search')?.focus();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  const handleCopy = (data: any) => {
    navigator.clipboard.writeText(JSON.stringify(data, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = (data: any) => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${TABS[activeTab].key}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (!result) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center py-40 space-y-6"
      >
        <motion.div
          animate={{ rotate: [0, 5, -5, 0] }}
          transition={{ repeat: Infinity, duration: 4 }}
          className="w-16 h-16 bg-white/5 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-white/10"
        >
          <FileJson className="w-8 h-8 text-white/20" />
        </motion.div>
        <div>
          <h2 className="text-xl font-bold">No Synthesis Results</h2>
          <p className="text-muted text-sm mt-2">Initialize a compilation from the engine home first.</p>
        </div>
        <a
          href="/"
          className="inline-flex items-center gap-2 text-sm text-blue-400 hover:text-blue-300 transition-colors group"
        >
          Return to Engine <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
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
  const rawJson = tabData ? JSON.stringify(tabData, null, 2) : '/* No data available for this layer */';
  const highlightedJson = tabData ? syntaxHighlightJSON(rawJson) : rawJson;

  const lineCount = rawJson.split('\n').length;

  return (
    <div className="space-y-8 pb-20">
      <motion.header
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col md:flex-row md:items-end justify-between gap-4"
      >
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Configuration Explorer</h2>
          <p className="text-muted text-sm mt-1">Deep-dive into synthesized artifacts and validation logs.</p>
        </div>
        <div className="flex items-center gap-3">
          <motion.div
            whileHover={{ scale: 1.05 }}
            className="px-3 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-[10px] font-mono text-blue-400 font-bold uppercase tracking-widest"
          >
            {result.job_id}
          </motion.div>
          <div className="px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-[10px] font-mono text-muted font-bold uppercase tracking-widest">
            v{result.app_config?.metadata.version ?? '0.1.0'}
          </div>
        </div>
      </motion.header>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-8 items-start">
        {/* Schema Viewer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className={`${expanded ? 'xl:col-span-12' : 'xl:col-span-8'} glass rounded-2xl overflow-hidden border-white/10 transition-all duration-500`}
        >
          <div className="flex border-b border-white/10 bg-white/[0.02] overflow-x-auto no-scrollbar">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex items-center gap-2 px-5 py-4 text-xs font-bold uppercase tracking-widest transition-all relative whitespace-nowrap
                  ${activeTab === tab.id ? 'text-white' : 'text-muted hover:text-white/70'}
                `}
              >
                <tab.icon className="w-3.5 h-3.5" style={activeTab === tab.id ? { color: tab.color } : {}} />
                {tab.label}
                {activeTab === tab.id && (
                  <motion.div
                    layoutId="activeTab"
                    className="absolute bottom-0 left-0 right-0 h-[2px] rounded-full"
                    style={{ background: tab.color, boxShadow: `0 0 12px ${tab.color}50` }}
                  />
                )}
              </button>
            ))}
          </div>

          <div className="p-6">
            <div className="flex justify-between items-center mb-4">
              <div className="flex items-center gap-3">
                <Code2 className="w-4 h-4 text-blue-400/50" />
                <span className="text-[10px] font-mono text-muted uppercase tracking-tighter">
                  artifacts / {TABS[activeTab].key}.json
                </span>
                <span className="text-[9px] font-mono text-white/15 ml-2">{lineCount} lines</span>
              </div>
              <div className="flex items-center gap-2">
                {/* Search */}
                <div className="relative">
                  <input
                    id="json-search"
                    type="text"
                    placeholder="Search..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-0 focus:w-40 bg-transparent border border-transparent focus:border-white/10 rounded-lg px-3 py-1.5 text-[11px] font-mono text-white/70 placeholder:text-white/20 transition-all duration-300 focus:bg-black/30"
                  />
                  <Search className="absolute right-2 top-1/2 -translate-y-1/2 w-3 h-3 text-white/20 pointer-events-none" />
                </div>
                <button
                  onClick={() => setExpanded(!expanded)}
                  className="p-1.5 rounded-lg hover:bg-white/5 transition-colors tooltip-wrapper"
                >
                  {expanded ? <Minimize2 className="w-3.5 h-3.5 text-muted" /> : <Maximize2 className="w-3.5 h-3.5 text-muted" />}
                  <span className="tooltip-text">{expanded ? 'Collapse' : 'Expand'}</span>
                </button>
                <button
                  onClick={() => handleDownload(tabData)}
                  className="p-1.5 rounded-lg hover:bg-white/5 transition-colors tooltip-wrapper"
                >
                  <Download className="w-3.5 h-3.5 text-muted" />
                  <span className="tooltip-text">Download JSON</span>
                </button>
                <button
                  onClick={() => handleCopy(tabData)}
                  className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest text-muted hover:text-white transition-colors group px-2 py-1.5 rounded-lg hover:bg-white/5"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-green-400" /> : <Copy className="w-3.5 h-3.5 group-hover:scale-110 transition-transform" />}
                  {copied ? 'Copied' : 'Copy'}
                </button>
              </div>
            </div>

            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.2 }}
                className="relative group"
              >
                <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-black/30 pointer-events-none rounded-xl" />
                <pre className={`bg-black/40 border border-white/5 rounded-xl p-6 text-[11px] font-mono overflow-auto ${expanded ? 'max-h-[80vh]' : 'max-h-[65vh]'} leading-relaxed selection:bg-blue-500/30`}>
                  <code dangerouslySetInnerHTML={{ __html: highlightedJson }} />
                </pre>
              </motion.div>
            </AnimatePresence>
          </div>
        </motion.div>

        {/* Sidebar Info */}
        {!expanded && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="xl:col-span-4 space-y-6"
          >
            {/* Validation & Repair */}
            <div className="glass rounded-2xl p-6 space-y-6 card-lift">
              <section>
                <div className="flex items-center gap-2 text-red-400 mb-4">
                  <ShieldAlert className="w-4 h-4" />
                  <h3 className="text-[10px] font-bold uppercase tracking-widest">Validation Integrity</h3>
                </div>
                {result.validation_errors && result.validation_errors.length > 0 ? (
                  <div className="space-y-3">
                    {result.validation_errors.map((err: any, i: number) => (
                      <motion.div
                        key={i}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.05 }}
                        className="flex gap-3 p-3 rounded-xl bg-red-500/5 border border-red-500/10 hover:border-red-500/20 transition-colors"
                      >
                        <AlertTriangle className="w-3.5 h-3.5 text-red-500 shrink-0 mt-0.5" />
                        <p className="text-[11px] font-mono text-red-200/60 leading-tight">
                          {typeof err === 'string' ? err : (err.message ?? JSON.stringify(err))}
                        </p>
                      </motion.div>
                    ))}
                  </div>
                ) : (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex items-center gap-3 p-4 rounded-xl bg-green-500/5 border border-green-500/10"
                  >
                    <Check className="w-4 h-4 text-green-500" />
                    <span className="text-xs text-green-200/60">Semantic integrity verified.</span>
                  </motion.div>
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
                      <motion.div
                        key={i}
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: i * 0.05 }}
                        whileHover={{ scale: 1.02 }}
                        className="flex items-center justify-between p-2.5 rounded-lg border border-white/5 bg-white/[0.02] hover:bg-white/[0.04] transition-colors cursor-default"
                      >
                        <div className="flex flex-col">
                          <span className="text-[9px] font-mono text-muted uppercase">Pass {action.pass_number} • {action.layer}</span>
                          <span className="text-[11px] font-medium mt-0.5">{action.success ? 'Correction Applied' : 'Repair Attempted'}</span>
                        </div>
                        <div className={`w-2 h-2 rounded-full ${action.success ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]' : 'bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]'}`} />
                      </motion.div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-muted text-center py-4 italic">No anomalies detected during synthesis.</p>
                )}
              </section>
            </div>

            {/* Visual Architecture Mini-Map */}
            {result.app_config?.ui && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
                className="glass rounded-2xl p-6 card-lift"
              >
                <div className="flex items-center gap-2 text-white/70 mb-4">
                  <Monitor className="w-4 h-4" />
                  <h3 className="text-[10px] font-bold uppercase tracking-widest">UI Architecture</h3>
                </div>
                <div className="space-y-3">
                  {result.app_config.ui.pages.map((page: UIPage, idx: number) => (
                    <motion.div
                      key={page.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.1 * idx }}
                      whileHover={{ scale: 1.02, borderColor: 'rgba(59,130,246,0.2)' }}
                      className="p-3 rounded-xl border border-white/5 bg-white/[0.02] space-y-2 cursor-default transition-all"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-[11px] font-bold">{page.title}</span>
                        <span className="text-[9px] font-mono text-muted bg-white/5 px-2 py-0.5 rounded">{page.route}</span>
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {page.components.map((comp: UIComponent, j: number) => (
                          <motion.div
                            key={j}
                            whileHover={{ scale: 1.1, y: -1 }}
                            className="px-2 py-0.5 rounded-md bg-blue-500/10 border border-blue-500/20 text-[9px] text-blue-300 font-mono cursor-default"
                          >
                            {comp.type}
                          </motion.div>
                        ))}
                      </div>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}
          </motion.div>
        )}
      </div>
    </div>
  );
}
