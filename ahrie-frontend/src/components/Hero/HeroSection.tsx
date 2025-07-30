'use client';

import { useEffect, useRef, useState } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import dynamic from 'next/dynamic';
import styles from './HeroSection.module.scss';
import KBeautyVisual from './KBeautyVisual';

// Try to load 3D component, fallback to 2D visual
const KBeautySymbol = dynamic(() => import('./KBeautySymbol'), {
  ssr: false,
  loading: () => <KBeautyVisual mousePosition={{ x: 0, y: 0 }} />
});

gsap.registerPlugin(ScrollTrigger);

interface HeroSectionProps {
  language?: 'en' | 'ar' | 'ko';
}

const HeroSection: React.FC<HeroSectionProps> = ({ language = 'en' }) => {
  const heroRef = useRef<HTMLElement>(null);
  const titleRef = useRef<HTMLHeadingElement>(null);
  const subtitleRef = useRef<HTMLParagraphElement>(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  const content = {
    en: {
      title: 'Transform your beauty journey',
      subtitle: 'Experience Korean beauty excellence with cultural comfort',
      cta: 'Begin Your Transformation'
    },
    ar: {
      title: 'حوّلي رحلة جمالك',
      subtitle: 'اختبري تميز الجمال الكوري مع الراحة الثقافية',
      cta: 'ابدئي تحولك'
    },
    ko: {
      title: '당신의 아름다움을 변화시키세요',
      subtitle: '문화적 편안함과 함께 한국 뷰티의 우수성을 경험하세요',
      cta: '변화를 시작하세요'
    }
  };

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Initial animations
      const tl = gsap.timeline();
      
      tl.from(titleRef.current, {
        y: 100,
        opacity: 0,
        duration: 1.2,
        ease: 'power3.out'
      })
      .from(subtitleRef.current, {
        y: 50,
        opacity: 0,
        duration: 1,
        ease: 'power3.out'
      }, '-=0.8')
      .from('.hero-cta', {
        scale: 0.9,
        opacity: 0,
        duration: 0.8,
        ease: 'back.out(1.7)'
      }, '-=0.6');

      // Scroll-triggered animations
      ScrollTrigger.create({
        trigger: heroRef.current,
        start: 'top top',
        end: 'bottom top',
        scrub: 1,
        onUpdate: (self) => {
          const progress = self.progress;
          if (titleRef.current) {
            titleRef.current.style.transform = `translateY(${progress * 50}px)`;
            titleRef.current.style.opacity = `${1 - progress * 0.5}`;
          }
        }
      });
    }, heroRef);

    return () => ctx.revert();
  }, []);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const { clientX, clientY } = e;
      const { innerWidth, innerHeight } = window;
      setMousePosition({
        x: (clientX / innerWidth - 0.5) * 2,
        y: (clientY / innerHeight - 0.5) * 2
      });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return (
    <section ref={heroRef} className={styles.hero}>
      <div className={styles.background}>
        <div className={styles.gradientMesh} />
        <div className={styles.noiseOverlay} />
      </div>

      <div className={styles.content}>
        <div className={styles.textContent}>
          <h1 
            ref={titleRef} 
            className={styles.title}
            data-text={content[language].title}
          >
            {content[language].title.split('').map((char, index) => (
              <span
                key={index}
                className={styles.char}
                style={{ animationDelay: `${index * 0.05}s` }}
              >
                {char === ' ' ? '\u00A0' : char}
              </span>
            ))}
          </h1>
          
          <p ref={subtitleRef} className={styles.subtitle}>
            {content[language].subtitle}
          </p>

          <button className={`${styles.cta} hero-cta`}>
            <span className={styles.ctaText}>{content[language].cta}</span>
            <div className={styles.ctaGlow} />
          </button>
        </div>

        <div 
          className={styles.symbolContainer}
          style={{
            transform: `translate(${mousePosition.x * 10}px, ${mousePosition.y * 10}px)`
          }}
        >
          <KBeautySymbol mousePosition={mousePosition} />
        </div>
      </div>

      <div className={styles.scrollIndicator}>
        <div className={styles.scrollLine} />
        <span className={styles.scrollText}>Scroll to explore</span>
      </div>
    </section>
  );
};

export default HeroSection;