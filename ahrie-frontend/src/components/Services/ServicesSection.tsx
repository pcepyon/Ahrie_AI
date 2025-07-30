'use client';

import { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import styles from './ServicesSection.module.scss';

gsap.registerPlugin(ScrollTrigger);

interface ServicesSectionProps {
  language?: 'en' | 'ar' | 'ko';
}

const ServicesSection: React.FC<ServicesSectionProps> = ({ language = 'en' }) => {
  const sectionRef = useRef<HTMLElement>(null);
  const servicesRef = useRef<HTMLDivElement>(null);
  
  const content = {
    en: {
      title: 'Transform with Excellence',
      subtitle: 'Comprehensive beauty solutions tailored for Middle Eastern clients',
      services: [
        {
          id: 'facial',
          title: 'Facial Aesthetics',
          description: 'Advanced K-beauty facial treatments from Seoul\'s top clinics',
          features: ['Glass Skin Treatment', 'V-Line Surgery', 'Rhinoplasty'],
          icon: '✨'
        },
        {
          id: 'body',
          title: 'Body Contouring',
          description: 'Cutting-edge body sculpting with minimal downtime',
          features: ['Liposuction', 'Brazilian Lift', 'Tummy Tuck'],
          icon: '💫'
        },
        {
          id: 'wellness',
          title: 'Medical Wellness',
          description: 'Holistic health and anti-aging solutions',
          features: ['Stem Cell Therapy', 'IV Therapy', 'Hormone Balance'],
          icon: '🌟'
        },
        {
          id: 'dental',
          title: 'Cosmetic Dentistry',
          description: 'Perfect smile with Korean dental aesthetics',
          features: ['Veneers', 'Implants', 'Whitening'],
          icon: '✦'
        }
      ]
    },
    ar: {
      title: 'تحولي بامتياز',
      subtitle: 'حلول تجميل شاملة مصممة للعملاء من الشرق الأوسط',
      services: [
        {
          id: 'facial',
          title: 'تجميل الوجه',
          description: 'علاجات الوجه الكورية المتقدمة من أفضل عيادات سيول',
          features: ['علاج البشرة الزجاجية', 'جراحة الخط V', 'تجميل الأنف'],
          icon: '✨'
        },
        {
          id: 'body',
          title: 'نحت الجسم',
          description: 'نحت الجسم المتطور مع أقل وقت للتعافي',
          features: ['شفط الدهون', 'الرفع البرازيلي', 'شد البطن'],
          icon: '💫'
        },
        {
          id: 'wellness',
          title: 'العافية الطبية',
          description: 'حلول شاملة للصحة ومكافحة الشيخوخة',
          features: ['العلاج بالخلايا الجذعية', 'العلاج الوريدي', 'توازن الهرمونات'],
          icon: '🌟'
        },
        {
          id: 'dental',
          title: 'طب الأسنان التجميلي',
          description: 'ابتسامة مثالية مع جماليات الأسنان الكورية',
          features: ['الفينير', 'الزرعات', 'التبييض'],
          icon: '✦'
        }
      ]
    },
    ko: {
      title: '최고의 변화를 경험하세요',
      subtitle: '중동 고객을 위한 맞춤형 종합 뷰티 솔루션',
      services: [
        {
          id: 'facial',
          title: '안면 미용',
          description: '서울 최고 클리닉의 첨단 K-뷰티 안면 치료',
          features: ['유리 피부 트리트먼트', 'V라인 수술', '코 성형'],
          icon: '✨'
        },
        {
          id: 'body',
          title: '바디 컨투어링',
          description: '최소한의 회복 시간으로 최첨단 바디 조각',
          features: ['지방흡입', '브라질리언 리프트', '복부 성형'],
          icon: '💫'
        },
        {
          id: 'wellness',
          title: '메디컬 웰니스',
          description: '전체적인 건강 및 노화 방지 솔루션',
          features: ['줄기세포 치료', 'IV 치료', '호르몬 균형'],
          icon: '🌟'
        },
        {
          id: 'dental',
          title: '심미 치과',
          description: '한국 치과 미학으로 완벽한 미소',
          features: ['베니어', '임플란트', '미백'],
          icon: '✦'
        }
      ]
    }
  };

  useEffect(() => {
    const ctx = gsap.context(() => {
      const services = gsap.utils.toArray('.service-card');
      
      // Animate title and subtitle
      gsap.from(sectionRef.current?.querySelector('h2'), {
        scrollTrigger: {
          trigger: sectionRef.current,
          start: 'top 80%',
          end: 'top 50%',
          scrub: 1
        },
        y: 100,
        opacity: 0
      });

      // Animate service cards
      services.forEach((service, index) => {
        gsap.from(service as Element, {
          scrollTrigger: {
            trigger: service as Element,
            start: 'top 85%',
            toggleActions: 'play none none reverse'
          },
          y: 80,
          opacity: 0,
          duration: 0.8,
          delay: index * 0.1,
          ease: 'power3.out'
        });

        // Hover animation setup
        const card = service as HTMLElement;
        const icon = card.querySelector('.service-icon');
        
        card.addEventListener('mouseenter', () => {
          gsap.to(icon, {
            rotation: 360,
            scale: 1.2,
            duration: 0.6,
            ease: 'power2.inOut'
          });
        });

        card.addEventListener('mouseleave', () => {
          gsap.to(icon, {
            rotation: 0,
            scale: 1,
            duration: 0.6,
            ease: 'power2.inOut'
          });
        });
      });

      // Parallax effect for background elements
      gsap.to('.services-bg-gradient', {
        scrollTrigger: {
          trigger: sectionRef.current,
          start: 'top bottom',
          end: 'bottom top',
          scrub: 1
        },
        y: -100,
        ease: 'none'
      });
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section ref={sectionRef} className={styles.services}>
      <div className={styles.backgroundElements}>
        <div className="services-bg-gradient" />
        <div className={styles.floatingOrbs}>
          <div className={styles.orb} />
          <div className={styles.orb} />
          <div className={styles.orb} />
        </div>
      </div>

      <div className={styles.container}>
        <div className={styles.header}>
          <h2 className={styles.title}>{content[language].title}</h2>
          <p className={styles.subtitle}>{content[language].subtitle}</p>
        </div>

        <div ref={servicesRef} className={styles.servicesGrid}>
          {content[language].services.map((service) => (
            <div key={service.id} className={`${styles.serviceCard} service-card`}>
              <div className={styles.cardContent}>
                <div className={`${styles.serviceIcon} service-icon`}>
                  {service.icon}
                </div>
                <h3 className={styles.serviceTitle}>{service.title}</h3>
                <p className={styles.serviceDescription}>{service.description}</p>
                <ul className={styles.serviceFeatures}>
                  {service.features.map((feature, index) => (
                    <li key={index}>{feature}</li>
                  ))}
                </ul>
                <button className={styles.serviceAction}>
                  <span>Learn More</span>
                  <svg className={styles.arrow} viewBox="0 0 24 24">
                    <path d="M5 12h14M12 5l7 7-7 7" />
                  </svg>
                </button>
              </div>
              <div className={styles.cardGlow} />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default ServicesSection;