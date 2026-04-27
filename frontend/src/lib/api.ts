/**
 * API client — typed fetch wrapper for the backend.
 */

import { CompileResponse } from './types';

const API_BASE = 'http://localhost:8000/api/v1';

export async function compileApp(prompt: string): Promise<CompileResponse> {
  const res = await fetch(`${API_BASE}/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt }),
  });
  if (!res.ok) {
    const err: { detail?: string } = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? `HTTP ${res.status}`);
  }
  return res.json() as Promise<CompileResponse>;
}

interface PipelineMetrics {
  total_compiles: number;
  success_count: number;
  success_rate: number;
  avg_latency_ms: number;
  avg_repair_count: number;
  avg_cost_usd: number;
}

export async function getMetrics(): Promise<PipelineMetrics> {
  const res = await fetch(`${API_BASE}/metrics`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json() as Promise<PipelineMetrics>;
}

export async function healthCheck(): Promise<{ status: string }> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json() as Promise<{ status: string }>;
}
