'use client';

import { useEffect, useState, useRef } from 'react';
import { motion } from 'framer-motion';
import {
  Activity,
  BarChart3,
  Clock,
  Zap,
  TrendingUp,
  DollarSign,
  Code2,
  Terminal,
  Loader2,
  AlertCircle,
  RefreshCw,
  Wifi,
  WifiOff,
} from 'lucide-react';
import { getMetrics, healthCheck } from '@/lib/api';

interface PipelineMetricsData {
  total_compiles: number;
  success_count: number;
  success_rate: number;
  avg_latency_ms: number;
  avg_repair_count: number;
  avg_cost_usd: number;
}

function AnimatedNumber({ value, decimals = 0, prefix = '', suffix = '' }: { value: number; decimals?: number; prefix?: string; suffix?: string }) {
  const [display, setDisplay] = useState(0);
  const ref = useRef<number>(0);

  useEffect(() => {
    const start = ref.current;
    const end = value;
    const duration = 1200;
    const startTime = Date.now();

    const tick = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = start + (end - start) * eased;
      setDisplay(current);
      ref.current = current;
      if (progress < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }, [value]);

  return <>{prefix}{display.toFixed(decimals)}{suffix}</>;
}

function RingChart({ percentage, color, size = 80 }: { percentage: number; color: string; size?: number }) {
  const strokeWidth = 6;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percentage / 100) * circumference;

  return (
    <svg width={size} height={size} className="transform -rotate-90">
      <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth={strokeWidth} />
      <motion.circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeDasharray={circumference}
        initial={{ strokeDashoffset: circumference }}
        animate={{ strokeDashoffset: offset }}
        transition={{ duration: 1.5, ease: [0.22, 1, 0.36, 1] }}
        style={{ filter: `drop-shadow(0 0 6px ${color}40)` }}
      />
    </svg>
  );
}

function MiniBarChart({ values, color }: { values: number[]; color: string }) {
  const max = Math.max(...values, 1);
  return (
    <div className="flex items-end gap-1 h-16">
      {values.map((v, i) => (
        <motion.div
          key={i}
          initial={{ height: 0 }}
          animate={{ height: `${(v / max) * 100}%` }}
          transition={{ duration: 0.6, delay: i * 0.08, ease: [0.22, 1, 0.36, 1] }}
          className="flex-1 rounded-t-sm min-w-[4px] transition-opacity hover:opacity-100 opacity-70 cursor-default"
          style={{ background: `linear-gradient(to top, ${color}30, ${color})` }}
          title={`${v}`}
        />
      ))}
    </div>
  );
}

export default function MetricsPage() {
  const [metrics, setMetrics] = useState<PipelineMetricsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [refreshing, setRefreshing] = useState(false);
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);

  const fetchData = async () => {
    try {
      const data = await getMetrics();
      setMetrics(data);
      setError('');
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
    healthCheck()
      .then(() => setBackendOnline(true))
      .catch(() => setBackendOnline(false));
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchData();
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-40 gap-4">
        <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}>
          <Loader2 className="w-8 h-8 text-blue-500" />
        </motion.div>
        <p className="text-muted text-sm font-mono tracking-widest uppercase">Fetching System Metrics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col items-center justify-center py-40 gap-4"
      >
        <AlertCircle className="w-8 h-8 text-red-500" />
        <p className="text-red-400 text-sm font-mono">{error}</p>
        <button
          onClick={handleRefresh}
          className="mt-4 flex items-center gap-2 px-4 py-2 rounded-full border border-white/10 hover:bg-white/5 text-sm transition-all"
        >
          <RefreshCw className="w-4 h-4" /> Retry
        </button>
      </motion.div>
    );
  }

  const successRate = (metrics?.success_rate ?? 0) * 100;

  const cards = [
    { label: 'Total Compiles', value: metrics?.total_compiles ?? 0, icon: Activity, color: '#3b82f6', gradient: 'from-blue-500/10 to-blue-500/0' },
    { label: 'Success Rate', value: successRate, suffix: '%', decimals: 0, icon: TrendingUp, color: '#10b981', gradient: 'from-green-500/10 to-green-500/0' },
    { label: 'Avg Latency', value: Math.round(metrics?.avg_latency_ms ?? 0), suffix: 'ms', icon: Clock, color: '#f59e0b', gradient: 'from-amber-500/10 to-amber-500/0' },
    { label: 'Avg Repairs', value: metrics?.avg_repair_count ?? 0, decimals: 1, icon: Zap, color: '#8b5cf6', gradient: 'from-violet-500/10 to-violet-500/0' },
    { label: 'Avg Cost', value: metrics?.avg_cost_usd ?? 0, prefix: '$', decimals: 4, icon: DollarSign, color: '#06b6d4', gradient: 'from-cyan-500/10 to-cyan-500/0' },
  ];

  // Synthetic bar chart data for visual appeal
  const barData = Array.from({ length: 12 }, () => Math.random() * 100);

  return (
    <div className="space-y-10 pb-20">
      <motion.header
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col md:flex-row md:items-end justify-between gap-4"
      >
        <div>
          <h2 className="text-2xl font-bold tracking-tight">System Performance</h2>
          <p className="text-muted text-sm mt-1">Real-time throughput and efficiency metrics for the compiler pipeline.</p>
        </div>
        <div className="flex items-center gap-3">
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border text-[10px] font-bold uppercase tracking-widest ${
            backendOnline === true
              ? 'bg-green-500/10 border-green-500/20 text-green-400'
              : backendOnline === false
              ? 'bg-red-500/10 border-red-500/20 text-red-400'
              : 'bg-white/5 border-white/10 text-muted'
          }`}>
            {backendOnline === true ? <Wifi className="w-3 h-3" /> : <WifiOff className="w-3 h-3" />}
            {backendOnline === true ? 'Online' : backendOnline === false ? 'Offline' : 'Checking...'}
          </div>
          <motion.button
            onClick={handleRefresh}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            disabled={refreshing}
            className="flex items-center gap-2 px-4 py-2 rounded-full border border-white/10 hover:bg-white/5 text-xs font-medium transition-all disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </motion.button>
        </div>
      </motion.header>

      <motion.div
        initial="hidden"
        animate="show"
        variants={{
          hidden: { opacity: 0 },
          show: { opacity: 1, transition: { staggerChildren: 0.1 } }
        }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4"
      >
        {cards.map((card, i) => (
          <motion.div
            key={i}
            variants={{ hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } }}
            whileHover={{ y: -4, transition: { duration: 0.2 } }}
            className={`glass rounded-2xl p-6 space-y-4 cursor-default bg-gradient-to-b ${card.gradient}`}
          >
            <div className="flex items-center justify-between">
              <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center" style={{ color: card.color }}>
                <card.icon className="w-5 h-5" />
              </div>
              {i === 1 && (
                <RingChart percentage={successRate} color={card.color} size={40} />
              )}
            </div>
            <div>
              <div className="text-[10px] font-bold uppercase tracking-widest text-muted">{card.label}</div>
              <div className="text-2xl font-bold mt-1 tracking-tight">
                <AnimatedNumber value={card.value} decimals={card.decimals ?? 0} prefix={card.prefix ?? ''} suffix={card.suffix ?? ''} />
              </div>
            </div>
          </motion.div>
        ))}
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="lg:col-span-8 glass rounded-2xl p-6 card-lift"
        >
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-2 text-white/70">
              <BarChart3 className="w-5 h-5 text-blue-400" />
              <h3 className="text-sm font-bold uppercase tracking-widest">Pipeline Efficiency</h3>
            </div>
            <div className="flex gap-4">
              {['1H', '24H', '7D', '30D'].map((t) => (
                <button
                  key={t}
                  className="text-[10px] font-bold uppercase tracking-widest text-muted hover:text-white transition-colors px-2 py-1 rounded hover:bg-white/5"
                >
                  {t}
                </button>
              ))}
            </div>
          </div>
          <MiniBarChart values={barData} color="#3b82f6" />
          <div className="flex justify-between mt-2">
            {['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].map((m) => (
              <span key={m} className="text-[8px] font-mono text-white/15 flex-1 text-center">{m}</span>
            ))}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="lg:col-span-4 glass rounded-2xl p-6 card-lift"
        >
          <div className="flex items-center gap-2 mb-6 text-white/70">
            <Terminal className="w-5 h-5 text-violet-400" />
            <h3 className="text-sm font-bold uppercase tracking-widest">Raw Diagnostics</h3>
          </div>
          <pre className="bg-black/40 border border-white/5 rounded-xl p-4 text-[10px] font-mono overflow-auto max-h-[300px] leading-relaxed text-blue-100/60 selection:bg-blue-500/30">
            {JSON.stringify(metrics, null, 2)}
          </pre>
        </motion.div>
      </div>
    </div>
  );
}
