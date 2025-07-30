'use client';

import { useState, useEffect } from 'react';
import NavBar from '@/components/Navigation/NavBar';
import HeroSection from '@/components/Hero/HeroSection';
import ServicesSection from '@/components/Services/ServicesSection';
import JourneySection from '@/components/Journey/JourneySection';
import LenisScroll from '@/components/LenisScroll';

export default function Home() {
  const [language, setLanguage] = useState<'en' | 'ar' | 'ko'>('en');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  return (
    <>
      <LenisScroll />
      
      <div className={`loading-screen ${!isLoading ? 'loaded' : ''}`}>
        <div className="loading-spinner">
          <div className="spinner-ring"></div>
          <div className="spinner-ring"></div>
          <div className="spinner-ring"></div>
        </div>
      </div>

      <NavBar 
        language={language} 
        onLanguageChange={setLanguage} 
      />
      
      <main>
        <HeroSection language={language} />
        <ServicesSection language={language} />
        <JourneySection language={language} />
      </main>

      <div className="noise-overlay" />
    </>
  );
}
