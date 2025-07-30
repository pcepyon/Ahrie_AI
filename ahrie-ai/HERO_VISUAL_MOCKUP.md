# Ahrie AI Hero Page Visual Mockup Guide

## Visual Layout Breakdown

### Hero Section (100vh)

```
┌────────────────────────────────────────────────────────────┐
│                                                            │
│  [Logo]                              [عربي] [한국어] [EN]    │
│                                                            │
│                                                            │
│                    ✧ ✦ ✧                                  │
│              Transform Your Beauty                          │
│                    Journey                                  │
│                   ╱     ╲                                  │
│                  ╱       ╲                                 │
│                 │ 3D Rose │                                │
│                 │ Symbol  │                                │
│                  ╲       ╱                                 │
│                   ╲     ╱                                  │
│                                                            │
│              Seoul's Premium K-Beauty                       │
│              Medical Tourism Partner                        │
│                                                            │
│                    ↓ Scroll                                │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Visual Design Elements

#### 1. Background Treatment
- **Base**: Pure black (#000000)
- **Gradient Orbs**: Subtle floating elements
  - Gold orb (top-left): 80vw diameter, -40vw offset
  - Rose orb (bottom-right): 60vw diameter, -30vw offset
  - Blur: 100px, Opacity: 30%
- **Noise Texture**: 3% opacity overlay for depth

#### 2. Typography Hierarchy
```
Main Title:
- Size: 8rem (desktop) / 4rem (mobile)
- Weight: 900
- Line Height: 0.9
- Animation: Liquid morph on hover

Subtitle:
- Size: 1.5rem
- Weight: 300
- Letter Spacing: 0.2em
- Color: #B8B8B8
```

#### 3. 3D Element Visualization
```
     ∗ ∗ ∗ (floating particles)
       ╱╲
      ╱  ╲
     ╱    ╲    (rotating rose/lotus hybrid)
    │  ❀  │    (Korean beauty symbol)
     ╲    ╱    (iridescent shader)
      ╲  ╱
       ╲╱
     ∗ ∗ ∗ (floating particles)
```

### Service Cards Section

```
┌────────────────────────────────────────────────────────────┐
│                                                            │
│                 Our Premium Services                        │
│                                                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │             │  │             │  │             │       │
│  │  Rhinoplasty│  │ Double      │  │ Facial      │       │
│  │     鼻       │  │ Eyelid      │  │ Contouring  │       │
│  │             │  │    👁        │  │     ✨      │       │
│  │ ▓▓▓▓▓▓▓▓▓▓ │  │ ▓▓▓▓▓▓▓▓▓▓ │  │ ▓▓▓▓▓▓▓▓▓▓ │       │
│  └─────────────┘  └─────────────┘  └─────────────┘       │
│                                                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │             │  │             │  │             │       │
│  │ Liposuction │  │ Hair        │  │ Skin        │       │
│  │     💪      │  │ Transplant  │  │ Treatments  │       │
│  │             │  │     🌱      │  │     ✨      │       │
│  │ ▓▓▓▓▓▓▓▓▓▓ │  │ ▓▓▓▓▓▓▓▓▓▓ │  │ ▓▓▓▓▓▓▓▓▓▓ │       │
│  └─────────────┘  └─────────────┘  └─────────────┘       │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Cultural Bridge Section

```
┌────────────────────────────────────────────────────────────┐
│                                                            │
│              Your Comfort, Our Priority                    │
│                                                            │
│  ┌───────────────────────┬──────────────────────┐         │
│  │                       │                      │         │
│  │   🕌 HALAL CERTIFIED  │  🧕 FEMALE DOCTORS  │         │
│  │   All our partner    │  Privacy-conscious   │         │
│  │   clinics serve      │  care with female   │         │
│  │   halal meals        │  medical staff      │         │
│  │                       │                      │         │
│  └───────────────────────┴──────────────────────┘         │
│                                                            │
│  ┌─────────────────────────────────────────────┐         │
│  │         📍 Prayer Times in Seoul             │         │
│  │  Fajr    Dhuhr   Asr    Maghrib   Isha     │         │
│  │  05:21   12:45   15:58   18:32    19:51    │         │
│  └─────────────────────────────────────────────┘         │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Animation Sequences

#### 1. Initial Load Sequence
```
Timeline:
0ms    - Black screen
100ms  - Gradient orbs fade in (opacity: 0 → 0.3)
300ms  - Navigation appears (slide down + fade)
500ms  - Main title reveals (blur: 20px → 0px, y: 100 → 0)
800ms  - 3D symbol fades in with rotation
1000ms - Subtitle appears (opacity: 0 → 1)
1200ms - Scroll indicator pulses
```

#### 2. Scroll-Triggered Animations
```
Scroll Position → Animation
0%             → Hero fully visible
10%            → Title starts parallax (speed: 0.5)
20%            → 3D symbol scales up (1 → 1.2)
30%            → Hero starts fading out
40%            → Service cards start appearing
50%            → Cards fully visible with stagger
70%            → Cultural section reveals
```

#### 3. Interactive States

**Hover on Title Letters**:
```
Normal:  | T |
Hover:   | T̃ | (scaleY: 1.2, scaleX: 0.9)
         liquid morph effect
```

**Service Card Hover**:
```
Normal:      [  Card  ]
Hover:       [ >Card< ] + glow effect
Mouse move:  Magnetic follow (20px range)
```

### Color Application Guide

```
Background Layers:
├─ Base (#000000)
├─ Gradient Orb 1 (#D4AF37 @ 30% opacity)
├─ Gradient Orb 2 (#FFB6C1 @ 30% opacity)
└─ Noise Texture (white @ 3% opacity)

Text Hierarchy:
├─ Primary (#FFFFFF)
├─ Secondary (#B8B8B8)
├─ Accent Gold (#D4AF37)
└─ Accent Rose (#FFB6C1)

Interactive Elements:
├─ Default: rgba(255, 255, 255, 0.1)
├─ Hover: gradient(#D4AF37, #FFB6C1)
└─ Active: #00D4AA
```

### Responsive Breakpoints

```
Desktop (1440px+):
- Hero title: 8rem
- 3D symbol: 500px
- Service cards: 3 columns

Laptop (1024px-1439px):
- Hero title: 6rem
- 3D symbol: 400px
- Service cards: 3 columns

Tablet (768px-1023px):
- Hero title: 4rem
- 3D symbol: 300px
- Service cards: 2 columns

Mobile (< 768px):
- Hero title: 3rem
- 3D symbol: 200px
- Service cards: 1 column
```

### Accessibility Considerations

```
Focus States:
┌─────────────┐
│ ◉ Element   │ (High contrast ring)
└─────────────┘

Screen Reader Landmarks:
- <main> Hero Section
- <nav> Primary Navigation
- <section> Services
- <section> Cultural Information

Reduced Motion:
- 3D symbol: Static image
- Animations: CSS transitions only
- Scroll: Native behavior
```

### Loading Performance Strategy

```
Priority 1 (0-500ms):
├─ Critical CSS
├─ Hero text content
└─ Navigation

Priority 2 (500-1000ms):
├─ WebGL scene setup
├─ Font loading (subset)
└─ Above-fold images

Priority 3 (1000ms+):
├─ Animation libraries
├─ Particle effects
├─ Below-fold content
└─ Full font sets
```

This visual mockup guide provides a comprehensive blueprint for implementing the Ahrie AI hero page with the sophisticated aesthetic inspired by Nisa AI while maintaining cultural sensitivity and medical professionalism.