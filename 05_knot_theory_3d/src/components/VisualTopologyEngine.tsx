import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, MeshDistortMaterial, Sparkles } from '@react-three/drei';
import * as THREE from 'three';

const MorphingTopology: React.FC = () => {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.x = state.clock.elapsedTime * 0.15;
      meshRef.current.rotation.y = state.clock.elapsedTime * 0.25;
    }
  });

  return (
    <mesh ref={meshRef}>
      <torusKnotGeometry args={[1.6, 0.35, 256, 64, 3, 5]} />
      <MeshDistortMaterial
        color="#8b5cf6"
        emissive="#0f002b"
        wireframe
        distort={0.35}
        speed={1.2}
        roughness={0.1}
        metalness={0.9}
      />
    </mesh>
  );
};

export const VisualTopologyEngine: React.FC = () => {
  return (
    <div className="absolute inset-0 z-0 bg-[#07070c] pointer-events-none">
      <Canvas camera={{ position: [0, 0, 7], fov: 45 }}>
        <ambientLight intensity={0.3} />
        <directionalLight position={[8, 8, 5]} intensity={1.2} color="#00f0ff" />
        <directionalLight position={[-8, -8, -5]} intensity={0.6} color="#ec4899" />
        <MorphingTopology />
        <Sparkles count={150} scale={10} size={1.5} speed={0.3} opacity={0.3} color="#00f0ff" />
        <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.4} />
      </Canvas>
    </div>
  );
};
