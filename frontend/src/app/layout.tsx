import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'AppForge AI — Compiler-Grade App Generator',
  description: 'Convert natural language app descriptions into cross-layer consistent, validated, executable application configurations.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-white text-gray-900 min-h-screen">
        <nav className="border-b border-gray-200 px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-bold">AppForge AI</h1>
            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded font-mono">v0.1.0</span>
          </div>
          <div className="flex gap-4 text-sm">
            <a href="/" className="text-gray-600 hover:text-gray-900">Compile</a>
            <a href="/preview" className="text-gray-600 hover:text-gray-900">Preview</a>
            <a href="/metrics" className="text-gray-600 hover:text-gray-900">Metrics</a>
          </div>
        </nav>
        <main className="p-6 max-w-7xl mx-auto">
          {children}
        </main>
      </body>
    </html>
  );
}
