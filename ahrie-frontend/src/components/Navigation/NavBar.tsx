'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import styles from './NavBar.module.scss';
import LanguageToggle from './LanguageToggle';

interface NavBarProps {
  language?: 'en' | 'ar' | 'ko';
  onLanguageChange?: (lang: 'en' | 'ar' | 'ko') => void;
}

const NavBar: React.FC<NavBarProps> = ({ language = 'en', onLanguageChange }) => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const navItems = {
    en: {
      services: 'Services',
      journey: 'Your Journey',
      testimonials: 'Testimonials',
      culture: 'Cultural Care',
      contact: 'Contact'
    },
    ar: {
      services: 'الخدمات',
      journey: 'رحلتك',
      testimonials: 'آراء العملاء',
      culture: 'الرعاية الثقافية',
      contact: 'اتصل بنا'
    },
    ko: {
      services: '서비스',
      journey: '당신의 여정',
      testimonials: '고객 후기',
      culture: '문화적 케어',
      contact: '문의하기'
    }
  };

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <nav className={`${styles.navbar} ${isScrolled ? styles.scrolled : ''}`}>
      <div className={styles.container}>
        <Link href="/" className={styles.logo}>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, ease: 'easeOut' }}
          >
            <span className={styles.logoText}>Ahrie</span>
            <span className={styles.logoSubtext}>AI</span>
          </motion.div>
        </Link>

        <div className={styles.navContent}>
          <ul className={styles.navLinks}>
            {Object.entries(navItems[language]).map(([key, value], index) => (
              <motion.li
                key={key}
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1, ease: 'easeOut' }}
              >
                <Link href={`#${key}`} className={styles.navLink}>
                  <span className={styles.linkText}>{value}</span>
                  <span className={styles.linkUnderline} />
                </Link>
              </motion.li>
            ))}
          </ul>

          <div className={styles.navActions}>
            <LanguageToggle 
              currentLanguage={language} 
              onLanguageChange={onLanguageChange}
            />
            
            <motion.button
              className={styles.ctaButton}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6, delay: 0.5, ease: 'easeOut' }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <span className={styles.ctaText}>
                {language === 'ar' ? 'احجز الآن' : language === 'ko' ? '지금 예약' : 'Book Now'}
              </span>
              <div className={styles.ctaGlow} />
            </motion.button>
          </div>
        </div>

        <button
          className={`${styles.menuToggle} ${isMenuOpen ? styles.active : ''}`}
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          aria-label="Toggle menu"
        >
          <span className={styles.menuLine} />
          <span className={styles.menuLine} />
          <span className={styles.menuLine} />
        </button>
      </div>

      <AnimatePresence>
        {isMenuOpen && (
          <motion.div
            className={styles.mobileMenu}
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3, ease: 'easeOut' }}
          >
            <ul className={styles.mobileNavLinks}>
              {Object.entries(navItems[language]).map(([key, value]) => (
                <li key={key}>
                  <Link 
                    href={`#${key}`} 
                    className={styles.mobileNavLink}
                    onClick={() => setIsMenuOpen(false)}
                  >
                    {value}
                  </Link>
                </li>
              ))}
            </ul>

            <div className={styles.mobileActions}>
              <LanguageToggle 
                currentLanguage={language} 
                onLanguageChange={onLanguageChange}
              />
              <button className={styles.mobileCta}>
                {language === 'ar' ? 'احجز الآن' : language === 'ko' ? '지금 예약' : 'Book Now'}
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
};

export default NavBar;