'use client';

import { useRef, useEffect, useState } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Environment, Float } from '@react-three/drei';
import * as THREE from 'three';
import styles from './KBeautySymbol.module.scss';

interface KBeautySymbolProps {
  mousePosition: { x: number; y: number };
}

const LotusRose = ({ mousePosition }: { mousePosition: { x: number; y: number } }) => {
  const meshRef = useRef<THREE.Mesh>(null!);
  const materialRef = useRef<THREE.ShaderMaterial>(null!);
  const { viewport } = useThree();

  const vertexShader = `
    uniform float uTime;
    uniform vec2 uMouse;
    varying vec2 vUv;
    varying vec3 vNormal;
    varying vec3 vPosition;
    
    void main() {
      vUv = uv;
      vNormal = normalize(normalMatrix * normal);
      vPosition = position;
      
      vec3 pos = position;
      float wave = sin(uTime * 2.0 + position.y * 3.0) * 0.05;
      pos.x += wave * uMouse.x;
      pos.z += wave * uMouse.y;
      
      gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
    }
  `;

  const fragmentShader = `
    uniform float uTime;
    uniform vec2 uMouse;
    varying vec2 vUv;
    varying vec3 vNormal;
    varying vec3 vPosition;
    
    vec3 goldColor = vec3(0.831, 0.686, 0.216); // #D4AF37
    vec3 roseColor = vec3(1.0, 0.714, 0.757);   // #FFB6C1
    vec3 medicalColor = vec3(0.0, 0.831, 0.667); // #00D4AA
    
    void main() {
      vec3 viewDirection = normalize(cameraPosition - vPosition);
      float fresnel = pow(1.0 - dot(viewDirection, vNormal), 2.0);
      
      // Iridescent effect
      float angle = atan(vPosition.y, vPosition.x);
      float radius = length(vPosition.xy);
      
      vec3 color1 = mix(goldColor, roseColor, sin(angle * 3.0 + uTime) * 0.5 + 0.5);
      vec3 color2 = mix(roseColor, medicalColor, cos(angle * 2.0 - uTime) * 0.5 + 0.5);
      vec3 finalColor = mix(color1, color2, fresnel);
      
      // Add shimmer
      float shimmer = sin(uTime * 10.0 + radius * 20.0) * 0.1 + 0.9;
      finalColor *= shimmer;
      
      // Glow effect
      float glow = fresnel * 0.8;
      finalColor += vec3(glow);
      
      gl_FragColor = vec4(finalColor, 0.9 + fresnel * 0.1);
    }
  `;

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.005;
      meshRef.current.rotation.z = Math.sin(state.clock.elapsedTime * 0.5) * 0.1;
    }
    
    if (materialRef.current) {
      materialRef.current.uniforms.uTime.value = state.clock.elapsedTime;
      materialRef.current.uniforms.uMouse.value = [mousePosition.x, mousePosition.y];
    }
  });

  return (
    <Float speed={2} rotationIntensity={0.5} floatIntensity={0.5}>
      <mesh ref={meshRef}>
        <torusKnotGeometry args={[2, 0.6, 256, 32, 3, 4]} />
        <shaderMaterial
          ref={materialRef}
          vertexShader={vertexShader}
          fragmentShader={fragmentShader}
          uniforms={{
            uTime: { value: 0 },
            uMouse: { value: [0, 0] }
          }}
          transparent
          side={THREE.DoubleSide}
        />
      </mesh>
    </Float>
  );
};

const Particles = () => {
  const particlesRef = useRef<THREE.Points>(null!);
  const particleCount = 500;
  
  const positions = new Float32Array(particleCount * 3);
  const colors = new Float32Array(particleCount * 3);
  
  for (let i = 0; i < particleCount; i++) {
    const i3 = i * 3;
    positions[i3] = (Math.random() - 0.5) * 10;
    positions[i3 + 1] = (Math.random() - 0.5) * 10;
    positions[i3 + 2] = (Math.random() - 0.5) * 10;
    
    // Random color between gold and rose
    const mix = Math.random();
    colors[i3] = 0.831 * mix + 1.0 * (1 - mix);
    colors[i3 + 1] = 0.686 * mix + 0.714 * (1 - mix);
    colors[i3 + 2] = 0.216 * mix + 0.757 * (1 - mix);
  }
  
  useFrame((state) => {
    if (particlesRef.current) {
      particlesRef.current.rotation.y = state.clock.elapsedTime * 0.05;
      particlesRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.1) * 0.1;
    }
  });
  
  return (
    <points ref={particlesRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={particleCount}
          array={positions}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-color"
          count={particleCount}
          array={colors}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.05}
        vertexColors
        transparent
        opacity={0.6}
        sizeAttenuation
      />
    </points>
  );
};

const KBeautySymbol: React.FC<KBeautySymbolProps> = ({ mousePosition }) => {
  const [isWebGLAvailable, setIsWebGLAvailable] = useState(true);

  useEffect(() => {
    // Check WebGL availability
    try {
      const canvas = document.createElement('canvas');
      const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
      if (!gl) {
        setIsWebGLAvailable(false);
      }
    } catch (e) {
      setIsWebGLAvailable(false);
    }
  }, []);

  if (!isWebGLAvailable) {
    // Dynamic import to avoid circular dependency
    const KBeautyVisual = require('./KBeautyVisual').default;
    return <KBeautyVisual mousePosition={mousePosition} />;
  }

  return (
    <div className={styles.container}>
      <Canvas
        camera={{ position: [0, 0, 8], fov: 45 }}
        gl={{ 
          antialias: true, 
          alpha: true,
          powerPreference: 'high-performance',
          failIfMajorPerformanceCaveat: false
        }}
        onCreated={({ gl }) => {
          gl.domElement.addEventListener('webglcontextlost', (event) => {
            event.preventDefault();
            setIsWebGLAvailable(false);
          });
        }}
      >
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        <pointLight position={[-10, -10, -10]} intensity={0.5} color="#FFB6C1" />
        
        <LotusRose mousePosition={mousePosition} />
        <Particles />
        
        <Environment preset="studio" />
        <OrbitControls 
          enableZoom={false} 
          enablePan={false}
          autoRotate
          autoRotateSpeed={0.5}
        />
      </Canvas>
    </div>
  );
};

export default KBeautySymbol;