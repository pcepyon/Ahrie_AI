# Ahrie AI Hero Page Technical Implementation Guide

## Core Component Examples

### 1. Hero Section with Morphing Typography

```tsx
// components/Hero/HeroSection.tsx
import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { MorphSVGPlugin } from 'gsap/MorphSVGPlugin';
import { useLanguage } from '@/hooks/useLanguage';
import KBeautySymbol from './KBeautySymbol';

gsap.registerPlugin(ScrollTrigger, MorphSVGPlugin);

const HeroSection = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const titleRef = useRef<HTMLHeadingElement>(null);
  const { language } = useLanguage();
  
  const titles = {
    en: "Transform Your Beauty Journey",
    ar: "حوّلي رحلة جمالك",
    ko: "당신의 아름다움을 변화시키세요"
  };

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Initial reveal animation
      gsap.fromTo(titleRef.current,
        {
          opacity: 0,
          y: 100,
          filter: 'blur(20px)',
        },
        {
          opacity: 1,
          y: 0,
          filter: 'blur(0px)',
          duration: 2,
          ease: 'power4.out',
          scrollTrigger: {
            trigger: containerRef.current,
            start: 'top 80%',
            end: 'top 20%',
            scrub: 1,
          }
        }
      );

      // Liquid morph effect on hover
      const letters = gsap.utils.toArray('.hero-letter');
      letters.forEach((letter: any) => {
        letter.addEventListener('mouseenter', () => {
          gsap.to(letter, {
            scaleY: 1.2,
            scaleX: 0.9,
            duration: 0.3,
            ease: 'elastic.out(1, 0.3)',
          });
        });
        
        letter.addEventListener('mouseleave', () => {
          gsap.to(letter, {
            scaleY: 1,
            scaleX: 1,
            duration: 0.5,
            ease: 'elastic.out(1, 0.3)',
          });
        });
      });
    }, containerRef);

    return () => ctx.revert();
  }, [language]);

  return (
    <section ref={containerRef} className="hero-section">
      <div className="hero-background">
        <div className="gradient-orb gradient-orb-1" />
        <div className="gradient-orb gradient-orb-2" />
      </div>
      
      <div className="hero-content">
        <h1 ref={titleRef} className="hero-title">
          {titles[language].split('').map((char, i) => (
            <span key={i} className="hero-letter">
              {char === ' ' ? '\u00A0' : char}
            </span>
          ))}
        </h1>
        
        <div className="hero-symbol">
          <KBeautySymbol />
        </div>
      </div>
      
      <ScrollIndicator />
    </section>
  );
};
```

### 2. 3D K-Beauty Symbol Component

```tsx
// components/Hero/KBeautySymbol.tsx
import { useRef, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { BufferGeometry, Float32BufferAttribute } from 'three';
import { useSpring, animated } from '@react-spring/three';

const KBeautyGeometry = () => {
  const meshRef = useRef<THREE.Mesh>(null);
  const [spring, api] = useSpring(() => ({
    scale: 1,
    rotation: [0, 0, 0],
    config: { mass: 1, tension: 170, friction: 26 }
  }));

  useFrame((state) => {
    if (!meshRef.current) return;
    
    // Continuous rotation
    meshRef.current.rotation.y = state.clock.elapsedTime * 0.1;
    
    // Breathing effect
    const breathe = Math.sin(state.clock.elapsedTime * 0.5) * 0.1 + 1;
    meshRef.current.scale.setScalar(breathe);
    
    // Mouse interaction
    const mouse = state.mouse;
    meshRef.current.rotation.x = mouse.y * 0.1;
    meshRef.current.rotation.z = mouse.x * 0.1;
  });

  // Create custom geometry inspired by Korean patterns
  const geometry = useRef(() => {
    const geo = new BufferGeometry();
    const vertices = [];
    const colors = [];
    
    // Generate vertices for a stylized rose/lotus pattern
    const petalCount = 8;
    const layers = 5;
    
    for (let layer = 0; layer < layers; layer++) {
      for (let petal = 0; petal < petalCount; petal++) {
        const angle = (petal / petalCount) * Math.PI * 2;
        const layerOffset = layer / layers;
        const radius = 1 - layerOffset * 0.5;
        
        // Create petal shape
        vertices.push(
          Math.cos(angle) * radius,
          Math.sin(angle * 2) * 0.3 * layerOffset,
          Math.sin(angle) * radius
        );
        
        // Gradient colors from rose gold to pearl white
        colors.push(
          0.83 + layerOffset * 0.17,  // R
          0.69 + layerOffset * 0.31,  // G
          0.22 + layerOffset * 0.78   // B
        );
      }
    }
    
    geo.setAttribute('position', new Float32BufferAttribute(vertices, 3));
    geo.setAttribute('color', new Float32BufferAttribute(colors, 3));
    geo.computeBoundingSphere();
    
    return geo;
  })();

  return (
    <animated.mesh
      ref={meshRef}
      geometry={geometry.current}
      scale={spring.scale}
      rotation={spring.rotation}
    >
      <shaderMaterial
        vertexShader={`
          varying vec3 vColor;
          varying vec3 vPosition;
          
          void main() {
            vColor = color;
            vPosition = position;
            
            vec3 transformed = position;
            transformed.y += sin(position.x * 10.0 + time) * 0.05;
            
            gl_Position = projectionMatrix * modelViewMatrix * vec4(transformed, 1.0);
          }
        `}
        fragmentShader={`
          uniform float time;
          varying vec3 vColor;
          varying vec3 vPosition;
          
          void main() {
            // Iridescent effect
            float iridescence = sin(vPosition.x * 10.0 + time) * 0.5 + 0.5;
            vec3 finalColor = mix(vColor, vec3(1.0, 0.75, 0.8), iridescence * 0.3);
            
            // Soft glow
            float glow = 1.0 - length(vPosition.xy) * 0.5;
            finalColor += vec3(0.1, 0.05, 0.05) * glow;
            
            gl_FragColor = vec4(finalColor, 1.0);
          }
        `}
        uniforms={{
          time: { value: 0 }
        }}
        vertexColors
      />
    </animated.mesh>
  );
};

const KBeautySymbol = () => {
  return (
    <div className="kbeauty-symbol-container">
      <Canvas
        camera={{ position: [0, 0, 5], fov: 45 }}
        dpr={[1, 2]}
        gl={{ 
          antialias: true,
          alpha: true,
          powerPreference: 'high-performance'
        }}
      >
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        <pointLight position={[-10, -10, -10]} intensity={0.5} color="#FFB6C1" />
        
        <KBeautyGeometry />
        
        {/* Floating particles */}
        <Particles />
      </Canvas>
    </div>
  );
};
```

### 3. Smooth Scroll Implementation

```tsx
// hooks/useSmoothScroll.ts
import { useEffect } from 'react';
import Lenis from '@studio-freight/lenis';

export const useSmoothScroll = () => {
  useEffect(() => {
    const lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      direction: 'vertical',
      gestureDirection: 'vertical',
      smooth: true,
      mouseMultiplier: 1,
      smoothTouch: false,
      touchMultiplier: 2,
      infinite: false,
    });

    function raf(time: number) {
      lenis.raf(time);
      requestAnimationFrame(raf);
    }

    requestAnimationFrame(raf);

    return () => {
      lenis.destroy();
    };
  }, []);
};
```

### 4. Service Cards with Magnetic Hover

```tsx
// components/Services/ServiceCard.tsx
import { useRef, useEffect } from 'react';
import { gsap } from 'gsap';
import { useTranslation } from 'next-i18next';

interface ServiceCardProps {
  service: {
    id: string;
    icon: string;
    titleKey: string;
    descriptionKey: string;
    image: string;
  };
  index: number;
}

const ServiceCard: React.FC<ServiceCardProps> = ({ service, index }) => {
  const cardRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);
  const { t } = useTranslation();

  useEffect(() => {
    const card = cardRef.current;
    const content = contentRef.current;
    if (!card || !content) return;

    // Magnetic effect
    const handleMouseMove = (e: MouseEvent) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      
      const deltaX = (x - centerX) / centerX;
      const deltaY = (y - centerY) / centerY;
      
      gsap.to(card, {
        x: deltaX * 20,
        y: deltaY * 20,
        rotateY: deltaX * 10,
        rotateX: -deltaY * 10,
        duration: 0.3,
        ease: 'power2.out',
      });
      
      gsap.to(content, {
        x: deltaX * -10,
        y: deltaY * -10,
        duration: 0.3,
        ease: 'power2.out',
      });
    };

    const handleMouseLeave = () => {
      gsap.to([card, content], {
        x: 0,
        y: 0,
        rotateY: 0,
        rotateX: 0,
        duration: 0.5,
        ease: 'elastic.out(1, 0.3)',
      });
    };

    card.addEventListener('mousemove', handleMouseMove);
    card.addEventListener('mouseleave', handleMouseLeave);

    // Scroll reveal animation
    gsap.fromTo(card,
      {
        opacity: 0,
        y: 100,
        scale: 0.9,
      },
      {
        opacity: 1,
        y: 0,
        scale: 1,
        duration: 1,
        delay: index * 0.1,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: card,
          start: 'top 80%',
          end: 'top 50%',
          scrub: 1,
        }
      }
    );

    return () => {
      card.removeEventListener('mousemove', handleMouseMove);
      card.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, [index]);

  return (
    <div ref={cardRef} className="service-card">
      <div className="service-card-glow" />
      <div ref={contentRef} className="service-card-content">
        <div className="service-icon">{service.icon}</div>
        <h3 className="service-title">{t(service.titleKey)}</h3>
        <p className="service-description">{t(service.descriptionKey)}</p>
        <div className="service-image-container">
          <img src={service.image} alt={t(service.titleKey)} />
          <div className="service-image-overlay" />
        </div>
      </div>
    </div>
  );
};
```

### 5. Cultural Features Component

```tsx
// components/Cultural/CulturalBridge.tsx
import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useRTL } from '@/hooks/useRTL';

const CulturalBridge = () => {
  const { isRTL, toggleRTL } = useRTL();
  const [prayerTimes, setPrayerTimes] = useState(null);
  const [nearbyHalal, setNearbyHalal] = useState([]);

  useEffect(() => {
    // Fetch prayer times based on user location
    fetchPrayerTimes();
    fetchHalalPlaces();
  }, []);

  return (
    <section className="cultural-bridge">
      <motion.div 
        className="cultural-content"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1 }}
      >
        {/* RTL Toggle with smooth transition */}
        <div className="rtl-toggle">
          <motion.button
            onClick={toggleRTL}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <span className={`flag ${isRTL ? 'flag-sa' : 'flag-us'}`} />
            <span className="toggle-text">
              {isRTL ? 'العربية' : 'English'}
            </span>
          </motion.button>
        </div>

        {/* Halal Certification Badge */}
        <div className="halal-section">
          <motion.div 
            className="halal-badge"
            animate={{ 
              rotate: [0, 5, -5, 0],
              scale: [1, 1.1, 1]
            }}
            transition={{ 
              duration: 4,
              repeat: Infinity,
              repeatType: "reverse"
            }}
          >
            <img src="/halal-certified.svg" alt="Halal Certified" />
          </motion.div>
          
          <div className="halal-info">
            <h3>{isRTL ? 'معتمد حلال' : 'Halal Certified Partners'}</h3>
            <p>{isRTL 
              ? 'جميع شركائنا الطبيين معتمدون لتقديم خدمات متوافقة مع الشريعة'
              : 'All our medical partners are certified to provide Sharia-compliant services'
            }</p>
          </div>
        </div>

        {/* Prayer Times Widget */}
        <AnimatePresence>
          {prayerTimes && (
            <motion.div 
              className="prayer-times"
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
            >
              <h4>{isRTL ? 'مواقيت الصلاة في سيول' : 'Prayer Times in Seoul'}</h4>
              <div className="prayer-grid">
                {Object.entries(prayerTimes).map(([prayer, time]) => (
                  <div key={prayer} className="prayer-item">
                    <span className="prayer-name">{prayer}</span>
                    <span className="prayer-time">{time}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Nearby Halal Restaurants */}
        <div className="halal-places">
          <h4>{isRTL ? 'مطاعم حلال قريبة' : 'Nearby Halal Restaurants'}</h4>
          <div className="places-carousel">
            {nearbyHalal.map((place, index) => (
              <motion.div
                key={place.id}
                className="place-card"
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <img src={place.image} alt={place.name} />
                <h5>{place.name}</h5>
                <p>{place.distance} km</p>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.div>
    </section>
  );
};
```

### 6. SCSS Architecture

```scss
// styles/globals.scss
@import 'variables';
@import 'mixins';
@import 'animations';

// Base styles
:root {
  --color-bg: #000000;
  --color-bg-alt: #0A0A0A;
  --color-text: #FFFFFF;
  --color-text-secondary: #B8B8B8;
  --color-accent-gold: #D4AF37;
  --color-accent-rose: #FFB6C1;
  --color-accent-medical: #00D4AA;
  
  // Dynamic viewport units
  --vh: 1vh;
  --vw: 1vw;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  font-size: clamp(14px, 1.5vw, 18px);
  
  &[dir="rtl"] {
    .hero-title {
      font-family: var(--font-arabic-display);
      letter-spacing: 0;
    }
  }
}

body {
  background-color: var(--color-bg);
  color: var(--color-text);
  font-family: var(--font-body);
  overflow-x: hidden;
  
  // Noise texture overlay
  &::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: url('/noise.png');
    opacity: 0.03;
    pointer-events: none;
    z-index: 1;
  }
}

// Hero Section Styles
.hero-section {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  
  .hero-background {
    position: absolute;
    inset: 0;
    overflow: hidden;
    
    .gradient-orb {
      position: absolute;
      border-radius: 50%;
      filter: blur(100px);
      opacity: 0.3;
      animation: float 20s infinite ease-in-out;
      
      &-1 {
        width: 80vw;
        height: 80vw;
        background: radial-gradient(circle, var(--color-accent-gold), transparent);
        top: -40vw;
        left: -20vw;
      }
      
      &-2 {
        width: 60vw;
        height: 60vw;
        background: radial-gradient(circle, var(--color-accent-rose), transparent);
        bottom: -30vw;
        right: -20vw;
        animation-delay: -10s;
      }
    }
  }
  
  .hero-title {
    font-size: clamp(3rem, 8vw, 8rem);
    font-weight: 900;
    line-height: 0.9;
    text-align: center;
    mix-blend-mode: difference;
    
    .hero-letter {
      display: inline-block;
      transform-origin: center bottom;
      transition: transform 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
      
      &:hover {
        color: var(--color-accent-gold);
      }
    }
  }
}

// Service Card Styles
.service-card {
  position: relative;
  background: linear-gradient(135deg, 
    rgba(255, 255, 255, 0.05) 0%,
    rgba(255, 255, 255, 0.02) 100%
  );
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: 2rem;
  transform-style: preserve-3d;
  transition: all 0.3s ease;
  
  &:hover {
    .service-card-glow {
      opacity: 1;
    }
    
    .service-image-overlay {
      opacity: 0;
    }
  }
  
  .service-card-glow {
    position: absolute;
    inset: -2px;
    background: linear-gradient(45deg,
      var(--color-accent-gold),
      var(--color-accent-rose),
      var(--color-accent-medical)
    );
    border-radius: 24px;
    opacity: 0;
    filter: blur(20px);
    transition: opacity 0.5s ease;
    z-index: -1;
  }
}

// Animations
@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -30px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
}

// Media Queries
@media (max-width: 768px) {
  .hero-title {
    font-size: clamp(2rem, 12vw, 4rem);
  }
  
  .service-card {
    padding: 1.5rem;
  }
}

// Accessibility
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### 7. Performance Monitoring

```typescript
// utils/performance.ts
export class PerformanceMonitor {
  private fps: number = 60;
  private lastTime: number = performance.now();
  private frames: number = 0;
  private adaptiveQuality: boolean = true;
  
  constructor(private onQualityChange: (quality: number) => void) {
    this.startMonitoring();
  }
  
  private startMonitoring() {
    const checkFPS = () => {
      const currentTime = performance.now();
      this.frames++;
      
      if (currentTime >= this.lastTime + 1000) {
        this.fps = (this.frames * 1000) / (currentTime - this.lastTime);
        this.frames = 0;
        this.lastTime = currentTime;
        
        if (this.adaptiveQuality) {
          this.adjustQuality();
        }
      }
      
      requestAnimationFrame(checkFPS);
    };
    
    checkFPS();
  }
  
  private adjustQuality() {
    if (this.fps < 30) {
      // Reduce quality
      this.onQualityChange(0.7);
      document.body.classList.add('reduced-quality');
    } else if (this.fps < 45) {
      // Medium quality
      this.onQualityChange(0.85);
      document.body.classList.add('medium-quality');
    } else {
      // Full quality
      this.onQualityChange(1);
      document.body.classList.remove('reduced-quality', 'medium-quality');
    }
  }
  
  public getFPS(): number {
    return this.fps;
  }
}
```

This implementation provides a solid foundation for creating a premium, culturally-aware hero page that adapts Nisa AI's sophisticated design language for Ahrie AI's K-Beauty medical tourism platform.