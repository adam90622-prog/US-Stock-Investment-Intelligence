---
name: High-Performance Intelligence
colors:
  surface: '#10131a'
  surface-dim: '#10131a'
  surface-bright: '#363940'
  surface-container-lowest: '#0b0e14'
  surface-container-low: '#191c22'
  surface-container: '#1d2026'
  surface-container-high: '#272a31'
  surface-container-highest: '#32353c'
  on-surface: '#e1e2eb'
  on-surface-variant: '#bbc9cf'
  inverse-surface: '#e1e2eb'
  inverse-on-surface: '#2e3037'
  outline: '#859399'
  outline-variant: '#3c494e'
  surface-tint: '#4cd6ff'
  primary: '#a4e6ff'
  on-primary: '#003543'
  primary-container: '#00d1ff'
  on-primary-container: '#00566a'
  inverse-primary: '#00677f'
  secondary: '#3ce42f'
  on-secondary: '#003a00'
  secondary-container: '#00c705'
  on-secondary-container: '#004b00'
  tertiary: '#ffd2cc'
  on-tertiary: '#690003'
  tertiary-container: '#ffaba0'
  on-tertiary-container: '#a20007'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#b7eaff'
  primary-fixed-dim: '#4cd6ff'
  on-primary-fixed: '#001f28'
  on-primary-fixed-variant: '#004e60'
  secondary-fixed: '#77ff62'
  secondary-fixed-dim: '#3ce42f'
  on-secondary-fixed: '#002200'
  on-secondary-fixed-variant: '#005300'
  tertiary-fixed: '#ffdad5'
  tertiary-fixed-dim: '#ffb4aa'
  on-tertiary-fixed: '#410001'
  on-tertiary-fixed-variant: '#930005'
  background: '#10131a'
  on-background: '#e1e2eb'
  surface-variant: '#32353c'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  display-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  data-tabular:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 16px
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.05em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  grid-margin: 24px
  grid-gutter: 16px
  section-gap: 24px
  component-padding-x: 12px
  component-padding-y: 8px
  dense-padding: 4px
---

## Brand & Style
The design system is engineered for professional financial analysts and semiconductor industry experts. It prioritizes information density, precision, and rapid cognitive processing. The aesthetic is "Financial Terminal Modern"—a synthesis of traditional high-stakes trading environments and cutting-edge AI technology.

The primary style is **Modern Corporate** with **Glassmorphic** accents. It utilizes a dark-mode-first approach to reduce eye strain during long analytical sessions. Visual hierarchy is established through tonal layering and subtle luminosity rather than aggressive shadows, evoking the feel of a sophisticated, high-performance machine.

## Colors
The palette is rooted in a deep, nocturnal base to allow data visualizations to pop with maximum clarity. 

- **Primary Accent (Cyan):** Used for AI-driven insights, primary actions, and active states. It should feel "electric" against the dark background.
- **Semantic Colors:** Green and Red are reserved strictly for performance indicators (Profit/Loss). Their saturation is high to ensure immediate recognition in dense tables.
- **Neutral/Surface:** The background uses a specific deep navy (#0B0E14). Secondary surfaces and cards use slightly lighter shades to create depth without relying on heavy borders.

## Typography
Typography is the core of the financial terminal experience. **Inter** is used for all UI labels and interface elements to provide a clean, neutral, and highly legible framework. 

For data-heavy areas, including stock tickers, price points, and table values, **JetBrains Mono** is utilized. Its monospaced nature ensures that columns of numbers align perfectly, allowing users to scan vertical lists of figures for discrepancies or trends with zero "visual jitter." Mobile sizes are strictly optimized to maintain density without sacrificing touch-target clarity.

## Layout & Spacing
This design system employs a **Fluid Grid** model with high density. The layout is divided into a fixed sidebar navigation (240px) and a flexible main content area that utilizes a 12-column system.

- **Density:** Spacing is tighter than consumer apps. Use 4px increments for internal component spacing and 16px/24px for layout-level gaps.
- **Breakpoints:** 
  - **Desktop (1440px+):** Full 12-column view with expanded sidebars.
  - **Tablet (768px - 1439px):** Sidebar collapses to icons; grid shifts to 6 columns.
  - **Mobile (<767px):** Single column stack; critical tickers stay pinned to the top.

## Elevation & Depth
In this design system, depth is communicated through **Tonal Layers** and **Backdrop Blurs**. Shadows are avoided to maintain a crisp, digital feel.

- **Base Layer:** #0B0E14 (Deepest)
- **Content Layer (Cards):** #161B22 with a 1px border (#30363D).
- **Overlays/Modals:** Semi-transparent versions of the surface color with a 12px background blur to create a "glass" effect, allowing the data below to remain vaguely visible.
- **Glow Effects:** Critical AI insights or "Buy" signals may use a subtle outer neon glow (5-10px blur) in the Primary Accent color to draw immediate attention.

## Shapes
The shape language is **Soft (0.25rem)**. The design system avoids large radii to maintain a professional, architectural feel. Small corner radii on cards and buttons provide just enough approachability without appearing "bubbly" or consumer-oriented. Actionable elements like "Trade" buttons or "Filter" chips use this 4px standard consistently.

## Components

- **Data Tables:** High-density rows with 1px bottom borders. Hover states should highlight the entire row in a subtle #30363D. Numerical data must be right-aligned.
- **Buttons:** 
  - *Primary:* Solid Cyan background with black text for maximum contrast.
  - *Ghost:* Cyan border with transparent background for secondary actions.
- **Glow Charts:** Line charts should use a 2px stroke width with a subtle vertical gradient (glow) underneath the line to emphasize the trend area.
- **Status Chips:** Small, rectangular badges with a subtle background tint and high-contrast text (e.g., Green text on a very dark green background).
- **Input Fields:** Darker than the card background, using a focus state that adds a 1px Primary Accent border and a minimal inner glow.
- **Sidebar:** Vertical orientation, using monochromatic icons that switch to Primary Cyan when active.