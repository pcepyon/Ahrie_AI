'use client';

import { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import styles from './JourneySection.module.scss';

gsap.registerPlugin(ScrollTrigger);

interface JourneySectionProps {
  language?: 'en' | 'ar' | 'ko';
}

const JourneySection: React.FC<JourneySectionProps> = ({ language = 'en' }) => {
  const sectionRef = useRef<HTMLElement>(null);
  const timelineRef = useRef<HTMLDivElement>(null);
  const progressRef = useRef<HTMLDivElement>(null);

  const content = {
    en: {
      title: 'Your Journey to Transformation',
      subtitle: 'A seamless experience from consultation to recovery',
      steps: [
        {
          id: 'consult',
          number: '01',
          title: 'Initial Consultation',
          description: 'Connect with our AI assistant Ahrie for personalized treatment recommendations',
          duration: '30 min',
          icon: '💬'
        },
        {
          id: 'plan',
          number: '02',
          title: 'Treatment Planning',
          description: 'Receive detailed treatment plans from verified Korean clinics',
          duration: '1-2 days',
          icon: '📋'
        },
        {
          id: 'arrange',
          number: '03',
          title: 'Travel Arrangements',
          description: 'We handle visa support, accommodation, and halal requirements',
          duration: '3-5 days',
          icon: '✈️'
        },
        {
          id: 'treatment',
          number: '04',
          title: 'Treatment & Care',
          description: 'Experience world-class Korean medical expertise with cultural sensitivity',
          duration: 'Varies',
          icon: '🏥'
        },
        {
          id: 'recovery',
          number: '05',
          title: 'Recovery & Follow-up',
          description: 'Comprehensive aftercare with continuous support until full recovery',
          duration: 'Ongoing',
          icon: '🌸'
        }
      ]
    },
    ar: {
      title: 'رحلتك نحو التحول',
      subtitle: 'تجربة سلسة من الاستشارة إلى التعافي',
      steps: [
        {
          id: 'consult',
          number: '٠١',
          title: 'الاستشارة الأولية',
          description: 'تواصلي مع مساعدتنا الذكية أهري للحصول على توصيات علاجية مخصصة',
          duration: '٣٠ دقيقة',
          icon: '💬'
        },
        {
          id: 'plan',
          number: '٠٢',
          title: 'التخطيط للعلاج',
          description: 'احصلي على خطط علاجية مفصلة من عيادات كورية معتمدة',
          duration: '١-٢ يوم',
          icon: '📋'
        },
        {
          id: 'arrange',
          number: '٠٣',
          title: 'ترتيبات السفر',
          description: 'نتولى دعم التأشيرة والإقامة والمتطلبات الحلال',
          duration: '٣-٥ أيام',
          icon: '✈️'
        },
        {
          id: 'treatment',
          number: '٠٤',
          title: 'العلاج والرعاية',
          description: 'اختبري الخبرة الطبية الكورية العالمية مع الحساسية الثقافية',
          duration: 'متغير',
          icon: '🏥'
        },
        {
          id: 'recovery',
          number: '٠٥',
          title: 'التعافي والمتابعة',
          description: 'رعاية شاملة بعد العلاج مع دعم مستمر حتى التعافي الكامل',
          duration: 'مستمر',
          icon: '🌸'
        }
      ]
    },
    ko: {
      title: '변화를 향한 여정',
      subtitle: '상담부터 회복까지 원활한 경험',
      steps: [
        {
          id: 'consult',
          number: '01',
          title: '초기 상담',
          description: 'AI 어시스턴트 아리와 연결하여 맞춤형 치료 추천을 받으세요',
          duration: '30분',
          icon: '💬'
        },
        {
          id: 'plan',
          number: '02',
          title: '치료 계획',
          description: '검증된 한국 클리닉의 상세한 치료 계획을 받으세요',
          duration: '1-2일',
          icon: '📋'
        },
        {
          id: 'arrange',
          number: '03',
          title: '여행 준비',
          description: '비자 지원, 숙박 및 할랄 요구사항을 처리해드립니다',
          duration: '3-5일',
          icon: '✈️'
        },
        {
          id: 'treatment',
          number: '04',
          title: '치료 및 관리',
          description: '문화적 민감성을 갖춘 세계적 수준의 한국 의료 전문성을 경험하세요',
          duration: '다양함',
          icon: '🏥'
        },
        {
          id: 'recovery',
          number: '05',
          title: '회복 및 후속 조치',
          description: '완전한 회복까지 지속적인 지원으로 포괄적인 사후 관리',
          duration: '지속적',
          icon: '🌸'
        }
      ]
    }
  };

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Animate section title
      gsap.from(sectionRef.current?.querySelector('h2'), {
        scrollTrigger: {
          trigger: sectionRef.current,
          start: 'top 80%',
          toggleActions: 'play none none reverse'
        },
        y: 60,
        opacity: 0,
        duration: 1,
        ease: 'power3.out'
      });

      // Animate timeline progress
      gsap.to(progressRef.current, {
        scrollTrigger: {
          trigger: timelineRef.current,
          start: 'top 70%',
          end: 'bottom 50%',
          scrub: 1
        },
        scaleY: 1,
        ease: 'none'
      });

      // Animate each step
      const steps = gsap.utils.toArray('.journey-step');
      steps.forEach((step, index) => {
        const element = step as HTMLElement;
        
        // Entry animation
        gsap.from(element, {
          scrollTrigger: {
            trigger: element,
            start: 'top 85%',
            toggleActions: 'play none none reverse'
          },
          x: index % 2 === 0 ? -100 : 100,
          opacity: 0,
          duration: 0.8,
          ease: 'power3.out'
        });

        // Animate step number
        gsap.from(element.querySelector('.step-number'), {
          scrollTrigger: {
            trigger: element,
            start: 'top 85%',
            toggleActions: 'play none none reverse'
          },
          scale: 0,
          rotation: -180,
          duration: 0.6,
          delay: 0.2,
          ease: 'back.out(1.7)'
        });

        // Hover animations
        element.addEventListener('mouseenter', () => {
          gsap.to(element.querySelector('.step-icon'), {
            scale: 1.2,
            rotation: 10,
            duration: 0.3
          });
          gsap.to(element.querySelector('.step-glow'), {
            opacity: 1,
            duration: 0.3
          });
        });

        element.addEventListener('mouseleave', () => {
          gsap.to(element.querySelector('.step-icon'), {
            scale: 1,
            rotation: 0,
            duration: 0.3
          });
          gsap.to(element.querySelector('.step-glow'), {
            opacity: 0,
            duration: 0.3
          });
        });
      });

      // Animate connecting lines
      const connectors = gsap.utils.toArray('.connector');
      connectors.forEach((connector) => {
        gsap.from(connector as Element, {
          scrollTrigger: {
            trigger: connector as Element,
            start: 'top 80%',
            toggleActions: 'play none none reverse'
          },
          scaleX: 0,
          duration: 0.6,
          ease: 'power3.inOut'
        });
      });
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section ref={sectionRef} className={styles.journey}>
      <div className={styles.container}>
        <div className={styles.header}>
          <h2 className={styles.title}>{content[language].title}</h2>
          <p className={styles.subtitle}>{content[language].subtitle}</p>
        </div>

        <div ref={timelineRef} className={styles.timeline}>
          <div className={styles.timelineLine}>
            <div ref={progressRef} className={styles.timelineProgress} />
          </div>

          {content[language].steps.map((step, index) => (
            <div key={step.id} className={`${styles.step} journey-step`}>
              <div className={styles.stepContent}>
                <div className={`${styles.stepNumber} step-number`}>
                  {step.number}
                </div>
                <div className={styles.stepInfo}>
                  <div className={`${styles.stepIcon} step-icon`}>
                    {step.icon}
                  </div>
                  <h3 className={styles.stepTitle}>{step.title}</h3>
                  <p className={styles.stepDescription}>{step.description}</p>
                  <span className={styles.stepDuration}>{step.duration}</span>
                </div>
                <div className={`${styles.stepGlow} step-glow`} />
              </div>
              {index < content[language].steps.length - 1 && (
                <div className={`${styles.connector} connector`} />
              )}
            </div>
          ))}
        </div>

        <div className={styles.cta}>
          <button className={styles.ctaButton}>
            <span>Start Your Journey</span>
            <div className={styles.ctaGlow} />
          </button>
        </div>
      </div>

      <div className={styles.backgroundElements}>
        <div className={styles.gradientOrb} />
        <div className={styles.noiseTexture} />
      </div>
    </section>
  );
};

export default JourneySection;