'use client';

import { useState } from 'react';
import { compileApp } from '@/lib/api';
import { CompileResponse } from '@/lib/types';

const PIPELINE_STAGES = [
  { id: 1, name: 'Intent Extraction' },
  { id: 2, name: 'System Design' },
  { id: 3, name: 'Schema Generation' },
  { id: 4, name: 'Validation & Repair' },
  { id: 5, name: 'Execution Check' },
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
      // Simulate stage progress
      const stageInterval = setInterval(() => {
        setCurrentStage((prev) => Math.min(prev + 1, 5));
      }, 2000);

      const data = await compileApp(prompt);
      clearInterval(stageInterval);
      setCurrentStage(5);
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'Compile failed');
      setCurrentStage(0);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Left Column — Prompt Input */}
      <div className="border border-gray-200 rounded-lg p-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Prompt
        </label>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          className="w-full h-48 border border-gray-300 rounded p-3 text-sm font-mono resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Describe the app you want to build..."
          maxLength={2000}
          disabled={loading}
        />
        <div className="flex items-center justify-between mt-2">
          <span className="text-xs text-gray-400">{prompt.length}/2000</span>
          <button
            onClick={handleCompile}
            disabled={loading || !prompt.trim()}
            className="bg-blue-600 text-white px-4 py-2 rounded text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Compiling...' : 'Compile App'}
          </button>
        </div>
        {error && (
          <p className="mt-2 text-sm text-red-600 font-mono">{error}</p>
        )}
        {result?.clarifications_needed && result.clarifications_needed.length > 0 && (
          <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded text-sm">
            <p className="font-medium text-yellow-800 mb-1">Clarification needed:</p>
            <ul className="list-disc list-inside text-yellow-700">
              {result.clarifications_needed.map((q, i) => <li key={i}>{q}</li>)}
            </ul>
          </div>
        )}
      </div>

      {/* Center Column — Pipeline Status */}
      <div className="border border-gray-200 rounded-lg p-4">
        <h2 className="text-sm font-medium text-gray-700 mb-3">Pipeline Status</h2>
        <div className="space-y-2">
          {PIPELINE_STAGES.map((stage) => {
            let icon = '○';
            let color = 'text-gray-400';
            if (currentStage > stage.id) {
              icon = '✓';
              color = 'text-green-600';
            } else if (currentStage === stage.id && loading) {
              icon = '◉';
              color = 'text-blue-600';
            }
            return (
              <div key={stage.id} className={`flex items-center gap-2 text-sm ${color}`}>
                <span className="font-mono w-4">{icon}</span>
                <span>Stage {stage.id}: {stage.name}</span>
              </div>
            );
          })}
        </div>
        {result && (
          <div className="mt-4 pt-3 border-t border-gray-200">
            <div className="flex items-center gap-2 mb-2">
              <span className={`inline-block w-2 h-2 rounded-full ${
                result.status === 'success' ? 'bg-green-500' :
                result.status === 'partial' ? 'bg-yellow-500' :
                result.status === 'clarification_needed' ? 'bg-blue-500' :
                'bg-red-500'
              }`} />
              <span className="text-sm font-medium capitalize">{result.status}</span>
            </div>
            {result.app_config && (
              <a
                href="/preview"
                className="text-sm text-blue-600 hover:underline"
                onClick={() => {
                  if (typeof window !== 'undefined') {
                    localStorage.setItem('appforge_result', JSON.stringify(result));
                  }
                }}
              >
                View Full Preview →
              </a>
            )}
          </div>
        )}
      </div>

      {/* Right Column — Metrics */}
      <div className="border border-gray-200 rounded-lg p-4">
        <h2 className="text-sm font-medium text-gray-700 mb-3">Compile Metrics</h2>
        {result ? (
          <div className="space-y-3">
            <Metric label="Status" value={result.status} />
            <Metric label="Latency" value={`${result.metrics?.total_latency_ms || result.metrics?.latency_ms || 0}ms`} />
            <Metric label="Repairs" value={String(result.metrics?.repair_count || 0)} />
            <Metric label="Cost" value={`$${result.metrics?.total_cost_usd?.toFixed(4) || '0.0000'}`} />
            <Metric label="Assumptions" value={String(result.metrics?.assumption_count || 0)} />
            {result.execution_report && (
              <>
                <hr className="border-gray-200" />
                <h3 className="text-xs font-medium text-gray-500 uppercase">Execution Report</h3>
                <Check label="DB Bootable" passed={result.execution_report.db_bootable.passed} />
                <Check label="API Complete" passed={result.execution_report.api_complete.passed} />
                <Check label="UI Renderable" passed={result.execution_report.ui_renderable.passed} />
                <Check label="Auth Sane" passed={result.execution_report.auth_sane.passed} />
              </>
            )}
          </div>
        ) : (
          <p className="text-sm text-gray-400">Compile an app to see metrics.</p>
        )}
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between text-sm">
      <span className="text-gray-500">{label}</span>
      <span className="font-mono font-medium">{value}</span>
    </div>
  );
}

function Check({ label, passed }: { label: string; passed: boolean }) {
  return (
    <div className="flex justify-between text-sm">
      <span className="text-gray-500">{label}</span>
      <span className={passed ? 'text-green-600' : 'text-red-600'}>
        {passed ? '✓ Pass' : '✗ Fail'}
      </span>
    </div>
  );
}
