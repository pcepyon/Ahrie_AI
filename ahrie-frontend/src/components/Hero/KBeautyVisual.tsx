'use client';

import { useEffect, useRef } from 'react';
import styles from './KBeautyVisual.module.scss';

interface KBeautyVisualProps {
  mousePosition: { x: number; y: number };
}

const KBeautyVisual: React.FC<KBeautyVisualProps> = ({ mousePosition }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const handleMouseMove = () => {
      if (containerRef.current) {
        const { x, y } = mousePosition;
        containerRef.current.style.transform = `translate(${x * 20}px, ${y * 20}px)`;
      }
    };

    handleMouseMove();
  }, [mousePosition]);

  return (
    <div ref={containerRef} className={styles.container}>
      <div className={styles.symbolWrapper}>
        {/* Lotus flower petals */}
        <div className={styles.lotus}>
          {[...Array(8)].map((_, i) => (
            <div
              key={i}
              className={styles.petal}
              style={{
                transform: `rotate(${i * 45}deg)`,
                animationDelay: `${i * 0.1}s`
              }}
            />
          ))}
        </div>

        {/* Center gem */}
        <div className={styles.centerGem}>
          <div className={styles.gemFacet} />
          <div className={styles.gemGlow} />
        </div>

        {/* Floating particles */}
        <div className={styles.particles}>
          {[...Array(20)].map((_, i) => (
            <div
              key={i}
              className={styles.particle}
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 5}s`,
                animationDuration: `${3 + Math.random() * 4}s`
              }}
            />
          ))}
        </div>

        {/* Orbital rings */}
        <div className={styles.orbitals}>
          <div className={styles.orbital} />
          <div className={styles.orbital} />
          <div className={styles.orbital} />
        </div>
      </div>

      {/* Background glow effects */}
      <div className={styles.glowEffects}>
        <div className={styles.glowGold} />
        <div className={styles.glowRose} />
      </div>
    </div>
  );
};

export default KBeautyVisual;