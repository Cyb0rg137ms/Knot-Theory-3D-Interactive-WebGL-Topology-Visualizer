import React, { useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, TorusKnot, Text } from '@react-three/drei';
import { ArrowLeft, Settings2 } from 'lucide-react';

interface KnotSimulatorProps {
  onBack: () => void;
}

export const KnotSimulator: React.FC<KnotSimulatorProps> = ({ onBack }) => {
  const [p, setP] = useState<number>(3);
  const [q, setQ] = useState<number>(5);
  const [wireframe, setWireframe] = useState<boolean>(false);
  const [color, setColor] = useState<string>("#00f0ff");

  // Calculates topological invariants (Alexander Polynomial approximations for display)
  const getAlexanderPolynomialStr = (p_val: number, q_val: number): string => {
    # Torus knots T(p,q) Alexander polynomial formula details
    return `t^${(p_val-1)*(q_val-1)} - t^${(p_val-1)*(q_val-1)-1} + ... + 1`;
  };

  return (
    <div className="relative z-20 min-h-screen flex flex-col animate-fade-in bg-[#07070c] bg-opacity-80">
      {/* Absolute Control Overlay */}
      <div className="absolute top-0 w-full p-6 flex flex-col md:flex-row justify-between items-start gap-4 z-30 pointer-events-none">
        <button 
          onClick={onBack}
          className="flex items-center gap-2 text-gray-300 hover:text-white transition-colors pointer-events-auto bg-black/40 px-4 py-2 rounded-full backdrop-blur-md border border-white/10"
        >
          <ArrowLeft size={18} />
          <span>Back</span>
        </button>
        
        <div className="glass-panel p-6 rounded-2xl pointer-events-auto w-80 backdrop-blur-md bg-black/50 border border-white/10 shadow-lg">
          <div className="flex items-center gap-2 mb-4 text-[#00f0ff]">
            <Settings2 size={18} />
            <h3 className="font-bold tracking-wider uppercase text-sm">Knot Parametrization</h3>
          </div>
          
          <div className="space-y-4 text-sm">
            <div>
              <label className="flex justify-between text-xs text-gray-400 mb-1">
                <span>P (Azimuthal Wraps)</span>
                <span className="text-[#00f0ff] font-bold">{p}</span>
              </label>
              <input 
                type="range" min="1" max="12" value={p} onChange={(e) => setP(parseInt(e.target.value))}
                className="w-full accent-[#00f0ff]"
              />
            </div>
            
            <div>
              <label className="flex justify-between text-xs text-gray-400 mb-1">
                <span>Q (Poloidal Wraps)</span>
                <span className="text-pink-500 font-bold">{q}</span>
              </label>
              <input 
                type="range" min="1" max="12" value={q} onChange={(e) => setQ(parseInt(e.target.value))}
                className="w-full accent-pink-500"
              />
            </div>
            
            <div className="pt-2 border-t border-white/10 flex items-center justify-between">
              <span className="text-gray-300 text-xs">Wireframe Mode</span>
              <button 
                onClick={() => setWireframe(!wireframe)}
                className={`w-10 h-5 rounded-full relative transition-colors ${wireframe ? 'bg-[#00f0ff]' : 'bg-white/20'}`}
              >
                <div className={`w-4 h-4 rounded-full bg-white absolute top-0.5 transition-all ${wireframe ? 'left-5' : 'left-1'}`} />
              </button>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-gray-300 text-xs">Primary Tint</span>
              <div className="flex gap-2">
                {["#00f0ff", "#ff007f", "#a78bfa", "#f59e0b"].map((c) => (
                  <button
                    key={c}
                    onClick={() => setColor(c)}
                    className={`w-5 h-5 rounded-full border ${color === c ? 'border-white' : 'border-transparent'}`}
                    style={{ backgroundColor: c }}
                  />
                ))}
              </div>
            </div>
          </div>
          
          <div className="mt-4 pt-3 border-t border-white/10 text-[11px] text-gray-400 space-y-1">
            <p className="font-bold text-gray-300">Invariant Properties:</p>
            <p>Genus $g = {(p-1)*(q-1)/2}$</p>
            <p className="truncate">Alexander Poly: {getAlexanderPolynomialStr(p, q)}</p>
          </div>
        </div>
      </div>

      {/* R3F 3D Canvas */}
      <div className="flex-1 w-full h-full cursor-grab active:cursor-grabbing">
        <Canvas camera={{ position: [0, 0, 10], fov: 45 }}>
          <ambientLight intensity={0.4} />
          <pointLight position={[10, 10, 10]} intensity={1.2} color={color} />
          <pointLight position={[-10, -10, -10]} intensity={0.6} color="#ff0080" />
          
          <TorusKnot args={[2.5, 0.6, 256, 64, p, q]}>
            <meshStandardMaterial 
              color={color}
              roughness={0.15}
              metalness={0.85}
              wireframe={wireframe}
            />
          </TorusKnot>

          <Text
            position={[0, -5, 0]}
            fontSize={0.55}
            color="#ffffff"
            anchorX="center"
            anchorY="middle"
            font="https://fonts.gstatic.com/s/orbitron/v25/yV08Q5VXJQ5aTrB7JqXeuxs.woff"
          >
            {`Torus Knot T(${p}, ${q})`}
          </Text>

          <OrbitControls 
            autoRotate 
            autoRotateSpeed={0.8}
            enablePan={true}
            enableZoom={true}
          />
        </Canvas>
      </div>

      <div className="absolute bottom-6 left-1/2 -translate-x-1/2 glass-panel px-6 py-3 rounded-full border border-white/10 bg-black/40 text-xs text-gray-300 backdrop-blur-md pointer-events-none">
        Drag to rotate • Scroll to zoom • Parameters update in real-time
      </div>
    </div>
  );
};
