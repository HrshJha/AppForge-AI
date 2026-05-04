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
    <html lang="en" className="dark">
      <body className="min-h-screen selection:bg-blue-500/30">
        <nav className="sticky top-0 z-50 border-b border-white/5 bg-black/60 backdrop-blur-xl px-6 py-4">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
                <span className="text-white font-bold text-lg leading-none">A</span>
              </div>
              <div>
                <h1 className="text-lg font-semibold tracking-tight leading-none">AppForge AI</h1>
                <p className="text-[10px] font-mono text-muted uppercase tracking-widest mt-1">Compiler Engine v0.1.0</p>
              </div>
            </div>
            <div className="flex items-center gap-8">
              <div className="hidden md:flex gap-6 text-sm font-medium">
                <a href="/" className="text-foreground hover:text-blue-400 transition-colors">Compiler</a>
                <a href="/preview" className="text-muted hover:text-foreground transition-colors">Preview</a>
                <a href="/metrics" className="text-muted hover:text-foreground transition-colors">Metrics</a>
              </div>
              <div className="h-4 w-[1px] bg-white/10 hidden md:block" />
              <button className="text-xs px-3 py-1.5 rounded-full border border-white/10 hover:bg-white/5 transition-colors font-medium">
                Documentation
              </button>
            </div>
          </div>
        </nav>
        <main className="relative">
          {/* Background Gradient */}
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-4xl h-[500px] bg-blue-600/10 blur-[120px] -z-10 pointer-events-none" />
          <div className="p-6 max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </body>
    </html>
  );
}
