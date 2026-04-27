/**
 * API client — typed fetch wrapper for the backend.
 */

import { CompileResponse } from './types';

const API_BASE = '/api/v1';

export async function compileApp(prompt: string): Promise<CompileResponse> {
  const res = await fetch(`${API_BASE}/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function getMetrics(): Promise<any> {
  const res = await fetch(`${API_BASE}/metrics`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function healthCheck(): Promise<{ status: string }> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}
