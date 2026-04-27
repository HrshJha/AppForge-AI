'use client';

import { useEffect, useState } from 'react';
import { CompileResponse, UIComponent, UIPage } from '@/lib/types';

const TABS = ['Intent IR', 'System Design', 'DB Schema', 'API Schema', 'UI Schema', 'Auth Schema'];
const TAB_KEYS = ['intent_ir', 'system_design_ir', 'db', 'api', 'ui', 'auth'] as const;

export default function PreviewPage() {
  const [result, setResult] = useState<CompileResponse | null>(null);
  const [activeTab, setActiveTab] = useState(0);

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

  if (!result) {
    return (
      <div className="text-center py-20 text-gray-400">
        <p className="text-lg">No compile result found.</p>
        <a href="/" className="text-blue-600 hover:underline text-sm">Go compile an app first →</a>
      </div>
    );
  }

  const getTabData = (): unknown => {
    const key = TAB_KEYS[activeTab];
    if (key === 'intent_ir') return result.intent_ir;
    if (key === 'system_design_ir') return result.system_design_ir;
    if (result.app_config) {
      const config = result.app_config as Record<string, unknown>;
      return config[key];
    }
    return null;
  };

  const tabData = getTabData();

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Schema Tabs — spans 2 columns */}
      <div className="lg:col-span-2 border border-gray-200 rounded-lg">
        <div className="flex border-b border-gray-200 overflow-x-auto">
          {TABS.map((tab, i) => (
            <button
              key={tab}
              onClick={() => setActiveTab(i)}
              className={`px-4 py-2 text-sm font-medium whitespace-nowrap border-b-2 ${
                activeTab === i
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
        <div className="p-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-xs text-gray-400 font-mono">{TAB_KEYS[activeTab]}</span>
            <button
              onClick={() => {
                navigator.clipboard.writeText(JSON.stringify(tabData, null, 2));
              }}
              className="text-xs text-blue-600 hover:underline"
            >
              Copy JSON
            </button>
          </div>
          <pre className="bg-gray-50 border border-gray-200 rounded p-4 text-xs font-mono overflow-auto max-h-[60vh]">
            {tabData ? JSON.stringify(tabData, null, 2) : 'No data available'}
          </pre>
        </div>
      </div>

      {/* Right Sidebar — Validation/Repair Log + Mini Renderer */}
      <div className="space-y-4">
        {/* Validation Log */}
        <div className="border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-medium text-gray-700 mb-2">Validation Log</h3>
          {result.validation_errors && result.validation_errors.length > 0 ? (
            <ul className="space-y-1 text-xs font-mono">
              {result.validation_errors.map((err: Record<string, unknown>, i: number) => (
                <li key={i} className="text-red-600">• {typeof err === 'string' ? err : (err.message as string) ?? JSON.stringify(err)}</li>
              ))}
            </ul>
          ) : (
            <p className="text-xs text-green-600">✓ No validation errors</p>
          )}
        </div>

        {/* Repair Log */}
        <div className="border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-medium text-gray-700 mb-2">Repair Log</h3>
          {result.repair_log && result.repair_log.length > 0 ? (
            <ul className="space-y-1 text-xs font-mono">
              {result.repair_log.map((action: Record<string, unknown>, i: number) => (
                <li key={i} className={action.success ? 'text-green-600' : 'text-yellow-600'}>
                  Pass {action.pass_number as number} [{action.layer as string}]: {action.success ? '✓ Fixed' : '⚠ Attempted'}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-xs text-gray-400">No repairs needed</p>
          )}
        </div>

        {/* Mini App Renderer */}
        {result.app_config?.ui && (
          <div className="border border-gray-200 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Rendered App Preview</h3>
            <div className="bg-gray-50 border border-gray-200 rounded p-3 space-y-2">
              {result.app_config.ui.pages.map((page: UIPage) => (
                <div key={page.id} className="text-xs">
                  <div className="font-medium text-gray-700">
                    📄 {page.title} ({page.route})
                    {page.roles.length > 0 && (
                      <span className="ml-1 text-gray-400">[{page.roles.join(', ')}]</span>
                    )}
                  </div>
                  <div className="ml-4 text-gray-500">
                    {page.components.map((comp: UIComponent, j: number) => (
                      <div key={j}>
                        → {comp.type}
                        {comp.data_source && <span className="text-blue-500 ml-1">({comp.data_source})</span>}
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
  );
}
