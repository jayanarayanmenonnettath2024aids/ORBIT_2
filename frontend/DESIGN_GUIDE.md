# 🎨 Visual Design Guide

## Color Palette

### Primary Colors
```
Main Purple:     #6366f1
Dark Purple:     #4f46e5
Light Purple:    #818cf8
Ultra Light:     #c7d2fe
```

### Gradients
```
Primary:    linear-gradient(135deg, #667eea 0%, #764ba2 100%)
Alt:        linear-gradient(135deg, #f093fb 0%, #f5576c 100%)
Secondary:  linear-gradient(135deg, #0ea5e9 0%, #22c55e 100%)
```

### Status Colors
```
Success:  #22c55e
Danger:   #ef4444
Warning:  #f59e0b
Info:     #06b6d4
```

---

## Component Styles

### Glass Effect
```css
background: rgba(255, 255, 255, 0.95);
backdrop-filter: blur(20px) saturate(180%);
border: 1px solid rgba(255, 255, 255, 0.3);
box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
```

### Button Primary
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
border-radius: 9999px;
padding: 1rem 2rem;
box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
```

### Card Hover
```css
transform: translateY(-10px) scale(1.02);
box-shadow: 0 25px 70px rgba(99, 102, 241, 0.3);
```

---

## Animation Timings

- **Fast**: 150ms (micro-interactions)
- **Base**: 250ms (standard transitions)
- **Smooth**: 400ms (page transitions)
- **Bounce**: 600ms (playful interactions)

---

## Spacing Scale

```
0.25rem = 4px   (xs)
0.5rem  = 8px   (sm)
0.75rem = 12px  (md)
1rem    = 16px  (base)
1.5rem  = 24px  (lg)
2rem    = 32px  (xl)
3rem    = 48px  (2xl)
4rem    = 64px  (3xl)
```

---

## Border Radius

```
sm:    8px
md:    12px
lg:    16px
xl:    20px
2xl:   24px
full:  9999px
```

---

## Typography

### Font Family
```
'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', ...
```

### Font Weights
- Regular: 400
- Medium: 500
- Semibold: 600
- Bold: 700
- Extrabold: 800
- Black: 900

### Font Sizes
```
0.75rem   = 12px  (xs)
0.875rem  = 14px  (sm)
1rem      = 16px  (base)
1.125rem  = 18px  (lg)
1.25rem   = 20px  (xl)
1.5rem    = 24px  (2xl)
2rem      = 32px  (3xl)
2.5rem    = 40px  (4xl)
```

---

## Shadow System

### Small
`0 1px 2px 0 rgba(0, 0, 0, 0.05)`

### Medium
`0 4px 6px -1px rgba(0, 0, 0, 0.1)`

### Large
`0 10px 15px -3px rgba(0, 0, 0, 0.1)`

### Extra Large
`0 20px 25px -5px rgba(0, 0, 0, 0.1)`

### Colored
`0 8px 32px rgba(99, 102, 241, 0.2)`

---

## Best Practices

### Do's ✅
- Use gradient backgrounds for primary actions
- Apply glass effects to major containers
- Add hover states to all interactive elements
- Use smooth transitions (250-400ms)
- Maintain consistent spacing
- Use semantic color meanings

### Don'ts ❌
- Don't mix too many gradients
- Avoid harsh shadows
- Don't animate layout properties
- Don't use too many colors
- Avoid instant transitions
- Don't skip focus states

---

## Accessibility

### Color Contrast
- Text on white: >= 4.5:1
- Text on colored: >= 3:1
- Large text: >= 3:1

### Focus Indicators
```css
outline: 3px solid var(--primary);
outline-offset: 2px;
```

### Interactive Targets
- Minimum size: 44x44px
- Clear hover states
- Visible focus states

---

## Responsive Breakpoints

```
Mobile:    < 768px
Tablet:    768px - 1024px
Desktop:   > 1024px
```

### Mobile Adjustments
- Single column layouts
- Larger touch targets
- Simplified navigation
- Stacked forms

---

*Design system created for Opportunity Intelligence System*
