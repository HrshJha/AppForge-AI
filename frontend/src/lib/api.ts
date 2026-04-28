/**
 * API client — typed fetch wrapper for the backend.
 * BASE_URL reads from NEXT_PUBLIC_API_URL at build time (set in Railway Variables).
 * Falls back to empty string so Next.js rewrites handle local dev proxying.
 */

import { CompileResponse } from './types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

export async function compileApp(prompt: string): Promise<CompileResponse> {
  const res = await fetch(`${BASE_URL}/api/v1/generate`, {
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
  const res = await fetch(`${BASE_URL}/api/v1/metrics`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json() as Promise<PipelineMetrics>;
}

export async function healthCheck(): Promise<{ status: string }> {
  const res = await fetch(`${BASE_URL}/api/v1/health`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json() as Promise<{ status: string }>;
}
