import React, { useState } from 'react';
import { VisualTopologyEngine } from './components/VisualTopologyEngine';
import { KnotSimulator } from './components/KnotSimulator';
import { Hexagon, Activity, Compass, Cpu } from 'lucide-react';

type ViewMode = 'home' | 'simulator';

const App: React.FC = () => {
  const [viewMode, setViewMode] = useState<ViewMode>('home');

  return (
    <div className="relative min-h-screen bg-[#07070c] text-white font-sans overflow-hidden">
      {/* Background visual engine */}
      {viewMode === 'home' && <VisualTopologyEngine />}

      {viewMode === 'home' ? (
        <div className="relative z-10 min-h-screen flex flex-col justify-between p-6 md:p-12">
          {/* Header */}
          <header className="flex justify-between items-center w-full">
            <div className="flex items-center gap-3">
              <Hexagon className="text-[#00f0ff] animate-pulse" size={28} />
              <div>
                <h1 className="text-xl font-bold tracking-wider uppercase">Topology Studio</h1>
                <p className="text-gray-400 text-[10px] tracking-widest uppercase">Algebraic & Geometric manifolds</p>
              </div>
            </div>
          </header>

          {/* Main Hero Card */}
          <main className="max-w-xl my-auto space-y-6">
            <div className="glass-panel p-8 rounded-2xl backdrop-blur-md bg-black/45 border border-white/10 shadow-2xl space-y-4">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#00f0ff]/10 border border-[#00f0ff]/30 text-xs text-[#00f0ff] font-semibold">
                <Activity size={12} />
                <span>GPU ACCELERATED</span>
              </div>
              
              <h2 className="text-4xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-gray-200 to-gray-500">
                Geometric Manifolds & Torus Knots
              </h2>
              
              <p className="text-gray-300 text-sm leading-relaxed">
                An interactive WebGL playground for visualizing knot invariants, 
                exploring parametric torus geometries, and projecting higher-dimensional coordinate curves onto 3D surfaces.
              </p>
              
              <div className="pt-4 flex gap-4">
                <button 
                  onClick={() => setViewMode('simulator')}
                  className="px-6 py-3 rounded-lg font-bold text-sm bg-gradient-to-r from-[#00f0ff] to-blue-500 text-black hover:opacity-90 transition-all flex items-center gap-2 shadow-lg shadow-[#00f0ff]/20"
                >
                  <Compass size={16} />
                  <span>Launch Simulator</span>
                </button>
              </div>
            </div>
          </main>

          {/* Footer */}
          <footer className="w-full text-xs text-gray-400 flex flex-col md:flex-row justify-between gap-2 border-t border-white/5 pt-4">
            <p>© 2026 Topology Studio Inc.</p>
            <p className="flex items-center gap-1">
              <Cpu size={12} className="text-pink-500" />
              <span>Three.js & React Three Fiber integration</span>
            </p>
          </footer>
        </div>
      ) : (
        <KnotSimulator onBack={() => setViewMode('home')} />
      )}
    </div>
  );
};

export default App;
