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
      <body className="min-h-screen selection:bg-blue-500/30 noise-overlay bg-grid">
        {/* Floating Orbs */}
        <div className="fixed inset-0 overflow-hidden pointer-events-none -z-10">
          <div className="orb orb-1" />
          <div className="orb orb-2" />
          <div className="orb orb-3" />
        </div>

        <nav className="sticky top-0 z-50 border-b border-white/5 bg-[#030308]/80 backdrop-blur-2xl px-6 py-4">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <a href="/" className="flex items-center gap-4 group">
              <div className="relative w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 via-violet-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-blue-500/20 group-hover:shadow-blue-500/40 transition-shadow duration-300">
                <span className="text-white font-bold text-lg leading-none">A</span>
                <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-blue-500 via-violet-500 to-cyan-500 opacity-0 group-hover:opacity-100 blur-lg transition-opacity duration-300" />
              </div>
              <div>
                <h1 className="text-lg font-semibold tracking-tight leading-none group-hover:text-white transition-colors">AppForge AI</h1>
                <p className="text-[10px] font-mono text-muted uppercase tracking-widest mt-1">Compiler Engine v0.1.0</p>
              </div>
            </a>
            <div className="flex items-center gap-8">
              <div className="hidden md:flex gap-1 text-sm font-medium">
                <NavLink href="/" label="Compiler" kbd="1" />
                <NavLink href="/preview" label="Preview" kbd="2" />
                <NavLink href="/metrics" label="Metrics" kbd="3" />
              </div>
              <div className="h-4 w-[1px] bg-white/10 hidden md:block" />
              <button className="text-xs px-4 py-2 rounded-full border border-white/10 hover:bg-white/5 hover:border-white/20 transition-all font-medium magnetic-btn">
                Documentation
              </button>
            </div>
          </div>
        </nav>
        <main className="relative">
          <div className="p-6 max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </body>
    </html>
  );
}

function NavLink({ href, label, kbd }: { href: string; label: string; kbd: string }) {
  return (
    <a
      href={href}
      className="relative px-4 py-2 rounded-lg text-muted hover:text-white hover:bg-white/5 transition-all duration-200 flex items-center gap-3 group"
    >
      {label}
      <span className="kbd opacity-0 group-hover:opacity-100 transition-opacity">{kbd}</span>
    </a>
  );
}
