# Ahrie AI Hero Page Design Plan
## Inspired by Nisa AI's Premium Aesthetic

### 1. Visual Design Analysis & Adaptation

#### Core Design Principles from Nisa AI
- **Dark Aesthetic**: Pure black (#000000) background with high contrast
- **Typography-First**: Custom variable fonts with dramatic weight variations
- **Minimalist Luxury**: Sparse use of elements, focus on negative space
- **Fluid Motion**: Organic, liquid-like animations
- **3D Depth**: WebGL elements creating spatial hierarchy

#### Ahrie AI Adaptation
```scss
// Color Palette
$colors: (
  'background': #000000,
  'background-alt': #0A0A0A,
  'text-primary': #FFFFFF,
  'text-secondary': #B8B8B8,
  'accent-gold': #D4AF37,      // Korean luxury aesthetic
  'accent-rose': #FFB6C1,      // K-Beauty pink
  'accent-medical': #00D4AA,   // Medical trust
  'gradient-start': #1A0033,   // Deep purple
  'gradient-end': #330019      // Deep rose
);

// Typography System
$typography: (
  'display': ('Gmarket Sans', 'SF Arabic', 'Noto Sans KR'),
  'body': ('Inter', 'IBM Plex Sans Arabic', 'Pretendard'),
  'accent': ('Playfair Display', 'Amiri', 'Nanum Myeongjo')
);
```

### 2. Hero Page Structure

```
┌─────────────────────────────────────────┐
│ Navigation (Floating, Transparent)       │
├─────────────────────────────────────────┤
│                                         │
│  Hero Section                           │
│  - Animated Typography                  │
│  - 3D Korean Pattern (WebGL)           │
│  - Scroll Indicator                    │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│  Value Proposition                      │
│  - Animated Statistics                  │
│  - Trust Indicators                     │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│  Service Showcase                       │
│  - Interactive Cards                    │
│  - Hover Reveals                        │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│  Cultural Bridge                        │
│  - RTL/LTR Toggle                      │
│  - Halal Certifications               │
│                                         │
└─────────────────────────────────────────┘
```

### 3. Interactive Elements Design

#### 3D Korean Beauty Symbol (Three.js)
```javascript
// Concept: Rotating 3D Hanbok-inspired geometric pattern
const KBeautySymbol = {
  geometry: 'Custom BufferGeometry',
  material: {
    type: 'ShaderMaterial',
    vertexShader: `
      // Flowing fabric simulation
      // Inspired by traditional Korean dress
    `,
    fragmentShader: `
      // Iridescent pearl effect
      // Subtle color shifts pink to gold
    `
  },
  animation: {
    rotation: 'Continuous slow spin',
    morph: 'Breathing effect',
    particles: 'Floating sakura/rose petals'
  }
};
```

#### Typography Animations (GSAP)
```javascript
// Hero Title Sequence
const heroAnimation = {
  stage1: "Transform your beauty journey",
  stage2: "حوّلي رحلة جمالك",  // Arabic
  stage3: "당신의 아름다움을 변화시키세요",  // Korean
  transition: {
    type: 'morphSVG',
    duration: 2.5,
    ease: 'power3.inOut'
  }
};
```

### 4. Component Architecture

```
frontend/
├── src/
│   ├── components/
│   │   ├── Hero/
│   │   │   ├── HeroSection.tsx
│   │   │   ├── Typography3D.tsx
│   │   │   ├── KBeautySymbol.tsx
│   │   │   └── ScrollIndicator.tsx
│   │   ├── Navigation/
│   │   │   ├── NavBar.tsx
│   │   │   ├── LanguageToggle.tsx
│   │   │   └── MenuOverlay.tsx
│   │   ├── Services/
│   │   │   ├── ServiceCard.tsx
│   │   │   ├── ServiceGrid.tsx
│   │   │   └── ServiceDetail.tsx
│   │   └── Cultural/
│   │       ├── HalalBadge.tsx
│   │       ├── PrayerTimes.tsx
│   │       └── CulturalInfo.tsx
│   ├── hooks/
│   │   ├── useScrollProgress.ts
│   │   ├── useMousePosition.ts
│   │   ├── useIntersection.ts
│   │   └── useRTL.ts
│   ├── utils/
│   │   ├── animations.ts
│   │   ├── webgl-utils.ts
│   │   └── i18n.ts
│   └── styles/
│       ├── globals.scss
│       ├── mixins.scss
│       └── variables.scss
```

### 5. Key Interactions

#### Scroll-Triggered Sequences
```typescript
const scrollSequences = [
  {
    trigger: 0.1,
    action: 'Reveal hero text with liquid morph',
    duration: 1.2
  },
  {
    trigger: 0.3,
    action: 'Activate 3D symbol rotation',
    duration: 2.0
  },
  {
    trigger: 0.5,
    action: 'Cascade service cards',
    stagger: 0.1
  },
  {
    trigger: 0.7,
    action: 'Reveal trust indicators',
    countUp: true
  }
];
```

#### Mouse Interactions
```typescript
const mouseEffects = {
  heroArea: {
    effect: 'Parallax depth layers',
    intensity: 0.02,
    smoothing: 0.1
  },
  serviceCards: {
    effect: 'Magnetic hover',
    threshold: 100,
    elasticity: 0.3
  },
  buttons: {
    effect: 'Liquid morph on hover',
    viscosity: 0.8
  }
};
```

### 6. Cultural Adaptations

#### RTL Support Strategy
```scss
// Bidirectional Design System
[dir="rtl"] {
  // Typography adjustments
  .heading {
    font-family: 'SF Arabic', 'Amiri', sans-serif;
    letter-spacing: 0; // Arabic doesn't use letter-spacing
  }
  
  // Layout flips
  .service-card {
    transform: scaleX(-1);
    .content { transform: scaleX(-1); }
  }
  
  // Animation directions
  .slide-in { animation: slideInRTL 1s ease; }
}
```

#### Multi-Language Typography
```typescript
const TypographySystem = {
  // Dynamic font loading based on language
  loadFonts: (lang: 'ar' | 'en' | 'ko') => {
    const fontMap = {
      ar: ['SF Arabic', 'Amiri'],
      en: ['Inter', 'Playfair Display'],
      ko: ['Noto Sans KR', 'Nanum Myeongjo']
    };
    return loadFonts(fontMap[lang]);
  },
  
  // Responsive sizing for different scripts
  getSize: (base: number, lang: string) => {
    const multipliers = { ar: 1.1, en: 1.0, ko: 0.95 };
    return base * multipliers[lang];
  }
};
```

### 7. Performance Optimization

#### WebGL Optimization
```javascript
const webGLConfig = {
  pixelRatio: Math.min(window.devicePixelRatio, 2),
  antialias: window.devicePixelRatio < 2,
  powerPreference: 'high-performance',
  
  // Adaptive quality
  adaptiveQuality: {
    enabled: true,
    targetFPS: 30,
    minPixelRatio: 1,
    maxPixelRatio: 2
  }
};
```

#### Loading Strategy
```typescript
const loadingStrategy = {
  // Critical path
  phase1: [
    'hero-typography',
    'navigation',
    'above-fold-content'
  ],
  
  // Enhanced experience
  phase2: [
    'webgl-scene',
    'animations',
    'interactive-elements'
  ],
  
  // Nice-to-have
  phase3: [
    'particle-effects',
    'advanced-shaders',
    'easter-eggs'
  ]
};
```

### 8. Technical Stack

```json
{
  "framework": "Next.js 14",
  "styling": "SCSS + CSS Modules",
  "animations": {
    "2D": "GSAP + Framer Motion",
    "3D": "Three.js + React Three Fiber",
    "scroll": "Lenis + ScrollTrigger"
  },
  "state": "Zustand",
  "i18n": "next-i18next",
  "fonts": "next/font with variable fonts",
  "bundler": "Turbopack",
  "deployment": "Vercel Edge Functions"
}
```

### 9. Accessibility Considerations

```typescript
const a11yFeatures = {
  // Motion preferences
  reducedMotion: {
    check: 'prefers-reduced-motion',
    fallback: 'Static beauty shots',
    animations: 'CSS transitions only'
  },
  
  // Screen readers
  srSupport: {
    liveRegions: 'Service updates',
    descriptions: 'All visual elements',
    navigation: 'Skip links + landmarks'
  },
  
  // Keyboard navigation
  keyboard: {
    tabOrder: 'Logical flow',
    focusIndicators: 'High contrast rings',
    shortcuts: 'J/K navigation'
  }
};
```

### 10. Brand Personality Translation

#### From Nisa AI to Ahrie AI
- **Nisa**: Tech-forward, mysterious, avant-garde
- **Ahrie**: Luxurious, trustworthy, culturally-aware

#### Visual Translation
```scss
// Nisa: Sharp, geometric, cold
// Ahrie: Soft, organic, warm

.hero-gradient {
  // Nisa approach
  background: linear-gradient(180deg, #000 0%, #111 100%);
  
  // Ahrie adaptation
  background: radial-gradient(
    ellipse at center,
    rgba(212, 175, 55, 0.1) 0%,    // Gold shimmer
    rgba(255, 182, 193, 0.05) 30%, // K-Beauty pink
    rgba(0, 0, 0, 1) 70%           // Deep black
  );
}
```

### Implementation Phases

#### Phase 1: Foundation (Week 1-2)
- Setup Next.js with TypeScript
- Implement design system
- Create basic components
- Setup i18n infrastructure

#### Phase 2: Core Experience (Week 3-4)
- Hero section with basic animations
- Navigation system
- Service showcase
- Responsive design

#### Phase 3: Premium Features (Week 5-6)
- WebGL 3D elements
- Advanced animations
- Mouse interactions
- Performance optimization

#### Phase 4: Cultural Features (Week 7)
- RTL support
- Prayer time widget
- Halal indicators
- Cultural content

#### Phase 5: Polish (Week 8)
- Accessibility audit
- Performance tuning
- Cross-browser testing
- Launch preparation