'use client';

import { useEffect, useState } from 'react';
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

  if (loading) return <p className="text-gray-400 text-sm">Loading metrics...</p>;
  if (error) return <p className="text-red-600 text-sm">Error: {error}</p>;

  return (
    <div>
      <h2 className="text-lg font-bold mb-4">Pipeline Metrics</h2>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <MetricCard label="Total Compiles" value={metrics?.total_compiles ?? 0} />
        <MetricCard label="Success Rate" value={`${((metrics?.success_rate ?? 0) * 100).toFixed(0)}%`} />
        <MetricCard label="Avg Latency" value={`${Math.round(metrics?.avg_latency_ms ?? 0)}ms`} />
        <MetricCard label="Avg Repairs" value={(metrics?.avg_repair_count ?? 0).toFixed(1)} />
      </div>

      <div className="border border-gray-200 rounded-lg p-4">
        <h3 className="text-sm font-medium text-gray-700 mb-2">Raw Metrics</h3>
        <pre className="bg-gray-50 border border-gray-200 rounded p-3 text-xs font-mono">
          {JSON.stringify(metrics, null, 2)}
        </pre>
      </div>
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="border border-gray-200 rounded-lg p-4">
      <div className="text-xs text-gray-500 uppercase">{label}</div>
      <div className="text-2xl font-bold mt-1">{value}</div>
    </div>
  );
}
