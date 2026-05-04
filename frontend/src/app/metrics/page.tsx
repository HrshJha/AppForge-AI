'use client';

import { useEffect, useState } from 'react';
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
  AlertCircle
} from 'lucide-react';
import { getMetrics } from '@/lib/api';

interface PipelineMetricsData {
  total_compiles: number;
  success_count: number;
  success_rate: number;
  avg_latency_ms: number;
  avg_repair_count: number;
  avg_cost_usd: number;
}

export default function MetricsPage() {
  const [metrics, setMetrics] = useState<PipelineMetricsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getMetrics()
      .then((data: PipelineMetricsData) => setMetrics(data))
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-40 gap-4">
        <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
        <p className="text-muted text-sm font-mono tracking-widest uppercase">Fetching System Metrics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-40 gap-4">
        <AlertCircle className="w-8 h-8 text-red-500" />
        <p className="text-red-400 text-sm font-mono">{error}</p>
      </div>
    );
  }

  const cards = [
    { label: 'Total Compiles', value: metrics?.total_compiles ?? 0, icon: Activity, color: 'text-blue-400' },
    { label: 'Success Rate', value: `${((metrics?.success_rate ?? 0) * 100).toFixed(0)}%`, icon: TrendingUp, color: 'text-green-400' },
    { label: 'Avg Latency', value: `${Math.round(metrics?.avg_latency_ms ?? 0)}ms`, icon: Clock, color: 'text-amber-400' },
    { label: 'Avg Repairs', value: (metrics?.avg_repair_count ?? 0).toFixed(1), icon: Zap, color: 'text-violet-400' },
    { label: 'Avg Cost', value: `$${(metrics?.avg_cost_usd ?? 0).toFixed(4)}`, icon: DollarSign, color: 'text-emerald-400' },
  ];

  return (
    <div className="space-y-10 pb-20">
      <header>
        <h2 className="text-2xl font-bold tracking-tight">System Performance</h2>
        <p className="text-muted text-sm mt-1">Real-time throughput and efficiency metrics for the compiler pipeline.</p>
      </header>

      <motion.div 
        initial="hidden"
        animate="show"
        variants={{
          hidden: { opacity: 0 },
          show: {
            opacity: 1,
            transition: {
              staggerChildren: 0.1
            }
          }
        }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4"
      >
        {cards.map((card, i) => (
          <motion.div
            key={i}
            variants={{
              hidden: { opacity: 0, y: 20 },
              show: { opacity: 1, y: 0 }
            }}
            className="glass rounded-2xl p-6 space-y-4"
          >
            <div className={`w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center ${card.color}`}>
              <card.icon className="w-5 h-5" />
            </div>
            <div>
              <div className="text-[10px] font-bold uppercase tracking-widest text-muted">{card.label}</div>
              <div className="text-2xl font-bold mt-1 tracking-tight">{card.value}</div>
            </div>
          </motion.div>
        ))}
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-8 glass rounded-2xl p-6">
          <div className="flex items-center gap-2 mb-6 text-white/70">
            <BarChart3 className="w-5 h-5 text-blue-400" />
            <h3 className="text-sm font-bold uppercase tracking-widest">Pipeline Efficiency</h3>
          </div>
          <div className="h-64 flex items-center justify-center border border-dashed border-white/10 rounded-xl bg-white/[0.02]">
            <div className="text-center space-y-2">
              <Code2 className="w-8 h-8 text-white/5 mx-auto" />
              <p className="text-xs text-white/20 font-mono">Historical graph visualization pending synthesis data...</p>
            </div>
          </div>
        </div>

        <div className="lg:col-span-4 glass rounded-2xl p-6">
          <div className="flex items-center gap-2 mb-6 text-white/70">
            <Terminal className="w-5 h-5 text-violet-400" />
            <h3 className="text-sm font-bold uppercase tracking-widest">Raw Diagnostics</h3>
          </div>
          <pre className="bg-black/40 border border-white/5 rounded-xl p-4 text-[10px] font-mono overflow-auto max-h-[300px] leading-relaxed text-blue-100/60 selection:bg-blue-500/30">
            {JSON.stringify(metrics, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  );
}
