'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import styles from './LanguageToggle.module.scss';

interface LanguageToggleProps {
  currentLanguage: 'en' | 'ar' | 'ko';
  onLanguageChange?: (lang: 'en' | 'ar' | 'ko') => void;
}

const LanguageToggle: React.FC<LanguageToggleProps> = ({ 
  currentLanguage, 
  onLanguageChange 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const languages = {
    en: { name: 'English', flag: '🇬🇧', dir: 'ltr' },
    ar: { name: 'العربية', flag: '🇸🇦', dir: 'rtl' },
    ko: { name: '한국어', flag: '🇰🇷', dir: 'ltr' }
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLanguageSelect = (lang: 'en' | 'ar' | 'ko') => {
    if (onLanguageChange) {
      onLanguageChange(lang);
    }
    setIsOpen(false);
    
    // Update document direction
    document.documentElement.dir = languages[lang].dir;
    document.documentElement.lang = lang;
  };

  return (
    <div ref={dropdownRef} className={styles.languageToggle}>
      <motion.button
        className={styles.toggleButton}
        onClick={() => setIsOpen(!isOpen)}
        whileTap={{ scale: 0.95 }}
      >
        <span className={styles.flag}>{languages[currentLanguage].flag}</span>
        <span className={styles.languageName}>{languages[currentLanguage].name}</span>
        <motion.svg
          className={styles.chevron}
          animate={{ rotate: isOpen ? 180 : 0 }}
          transition={{ duration: 0.2 }}
          width="12"
          height="12"
          viewBox="0 0 12 12"
          fill="none"
        >
          <path
            d="M3 4.5L6 7.5L9 4.5"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </motion.svg>
      </motion.button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            className={styles.dropdown}
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            {Object.entries(languages).map(([code, lang]) => (
              <motion.button
                key={code}
                className={`${styles.languageOption} ${
                  currentLanguage === code ? styles.active : ''
                }`}
                onClick={() => handleLanguageSelect(code as 'en' | 'ar' | 'ko')}
                whileHover={{ x: languages[code].dir === 'rtl' ? -5 : 5 }}
                transition={{ duration: 0.1 }}
              >
                <span className={styles.flag}>{lang.flag}</span>
                <span className={styles.languageName}>{lang.name}</span>
                {currentLanguage === code && (
                  <motion.div
                    className={styles.activeIndicator}
                    layoutId="activeLanguage"
                    transition={{ duration: 0.2 }}
                  />
                )}
              </motion.button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default LanguageToggle;