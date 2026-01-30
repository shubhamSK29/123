# Fractured Key — Design Specification

**Theme:** Tech-inspired, mysterious, sleek. Evokes encryption, digital fragments, broken patterns, security, and futuristic systems.

---

## Part 1 — Overall GUI Design

### Design Principles

| Principle | Application |
|-----------|-------------|
| **Clean & premium** | Generous whitespace, minimal chrome, refined components |
| **Strong hierarchy** | Clear section headings, focus areas, and visual weight (size/color) |
| **Balanced palette** | Dark base with accent gradients; high contrast for text |
| **Modern typography** | Professional heading font + readable body font |
| **Grid-based layout** | Consistent spacing scale (4/8/12/16/24/32/48px) |
| **Depth & softness** | Rounded corners (12–24px), soft shadows, layered cards |
| **Micro-interactions** | Hover states, focus rings, loading feedback, subtle transitions |
| **Accessibility** | WCAG AA contrast, 16px+ body, focus indicators, semantic structure |

---

## 1. Color Palette (HEX)

### Primary palette

| Role | HEX | Usage |
|------|-----|--------|
| **Background — darkest** | `#050B14` | App chrome, deepest layer |
| **Background — dark** | `#0A1628` | Main canvas |
| **Background — medium** | `#0F172A` | Cards, elevated surfaces |
| **Background — light** | `#1E293B` | Inputs, hover surfaces |
| **Background — hover** | `#334155` | Interactive hover |

### Accent (blue gradient family)

| Role | HEX | Usage |
|------|-----|--------|
| **Deep blue** | `#1E3A8A` | Top bars, strong accents |
| **Neon blue (primary)** | `#3B82F6` | Primary buttons, links, active states |
| **Sky blue** | `#0EA5E9` | Highlights, taglines |
| **Light blue** | `#38BDF8` | Secondary accents, icons |
| **Glow blue** | `#60A5FA` | Hover on primary, borders |

### Semantic

| Role | HEX | Usage |
|------|-----|--------|
| **Success** | `#10B981` | Success states, confirm actions |
| **Warning** | `#F59E0B` | Warnings, disclaimers |
| **Error** | `#EF4444` | Errors, destructive actions |

### Text

| Role | HEX | Min contrast |
|------|-----|--------------|
| **Primary** | `#F8FAFC` | On dark BG |
| **Secondary** | `#94A3B8` | Supporting text |
| **Muted** | `#64748B` | Captions, hints |

### Borders & dividers

| Role | HEX |
|------|-----|
| **Default** | `#334155` |
| **Light** | `#475569` |
| **Glow (accent)** | `#3B82F640` (with alpha for focus) |

---

## 2. Typography Pairing

### Heading font

- **Preferred:** **Inter** (Bold / SemiBold for headings)
- **Fallbacks:** Segoe UI (Windows), SF Pro Display (macOS), system-ui

**Usage:** Hero, page titles, card titles, nav labels.

| Style | Size | Weight | Line height |
|-------|------|--------|-------------|
| Hero | 40–48px | Bold | 1.1 |
| H1 | 28px | Bold | 1.2 |
| H2 | 22px | Bold | 1.25 |
| H3 | 18px | SemiBold | 1.3 |
| H4 | 14px | SemiBold | 1.35 |

### Body font

- **Preferred:** **Inter** (Regular / Medium)
- **Fallbacks:** Segoe UI, system-ui

**Usage:** Descriptions, labels, list text, captions.

| Style | Size | Weight | Line height |
|-------|------|--------|-------------|
| Body large | 16px | Regular | 1.5 |
| Body | 14px | Regular | 1.5 |
| Body small | 12px | Regular | 1.45 |
| Caption | 11px | Regular | 1.4 |

### Monospace (logs, code)

- **Font:** Cascadia Code or Consolas  
- **Size:** 11–12px

---

## 3. Component Styles

### Buttons

| Type | Background | Hover | Text | Radius | Height |
|------|------------|-------|------|--------|--------|
| **Primary** | `#3B82F6` | `#60A5FA` | `#FFFFFF` | 14px | 48–52px |
| **Secondary** | transparent | `#334155` | `#F8FAFC` | 14px | 48px |
| **Success** | `#10B981` | `#059669` | `#FFFFFF` | 14px | 48px |
| **Danger** | `#EF4444` | `#DC2626` | `#FFFFFF` | 14px | 48px |

- Border: secondary = 2px `#475569`
- Font: 13px Bold (heading font)
- Padding: 20–24px horizontal
- Micro-interaction: 150ms ease on background/border; optional slight scale (1.02) on hover

### Cards

| Property | Value |
|----------|--------|
| Background | `#0F172A` |
| Border | 1px `#334155` |
| Radius | 20px |
| Padding | 24px |
| Shadow | 0 4px 24px rgba(0,0,0,0.2) (optional) |

- **Hover:** Border → `#3B82F6` (150ms ease)
- **Active/focus:** Border `#3B82F6`, optional soft glow

### Inputs (text / password)

| Property | Value |
|----------|--------|
| Background | `#1E293B` |
| Border | 2px `#334155` |
| Focus border | 2px `#3B82F6` |
| Radius | 12px |
| Height | 48px |
| Padding | 14px 16px |
| Placeholder | `#64748B` |
| Text | `#F8FAFC`, 14px |

- Transition: border 150ms ease

### Modals / dialogs

| Property | Value |
|----------|--------|
| Overlay | `rgba(5,11,20,0.85)` |
| Panel background | `#0F172A` |
| Border | 1px `#334155` |
| Radius | 24px |
| Padding | 32px |
| Shadow | 0 24px 48px rgba(0,0,0,0.4) |

- Title: 22px Bold, primary text
- Body: 14px, secondary text
- Buttons: primary + secondary, right-aligned, 12px gap

---

## 4. Layout Structure & UI Flow

### Grid system

- **Base unit:** 4px  
- **Scale:** 4, 8, 12, 16, 24, 32, 40, 48, 64  
- **Content max-width:** 720px (single column), 1200px (app width)  
- **Gutters:** 24px (mobile), 44px (desktop)  
- **Section spacing:** 24–36px vertical between sections  

### App structure

```
┌─────────────────────────────────────────────────────────┐
│  Header (logo, title, version)                          │
├──────────────┬──────────────────────────────────────────┤
│              │                                          │
│  Sidebar     │  Content area (tab: Encrypt / Decrypt /   │
│  (nav +      │  Manual / About)                         │
│  security    │  - Page title + subtitle                  │
│  bullets)    │  - Cards (form, options, output)          │
│              │  - Buttons, progress, log                 │
│              │                                          │
├──────────────┴──────────────────────────────────────────┤
│  Status bar (status text, tech badge)                   │
└─────────────────────────────────────────────────────────┘
```

### UI flow

1. **Start** → Landing (intro) page only.
2. **Get Started / Login** → Main app, Encrypt tab.
3. **Explore Features** → Main app, About tab.
4. **Sidebar** → Encrypt, Decrypt, Manual, About (instant tab switch).
5. **Encrypt** → Form → Run → Progress + log.
6. **Decrypt** → Select images + master password → Run → Progress + log.
7. **Manual** → Select .bin + master password → Run → Log.

---

## 5. Introductory / Landing Page — Wireframe Description

### Layout (top to bottom)

**1. Top bar (optional)**  
- Thin strip, full width, 6–8px height, `#1E3A8A`.  
- Suggests “fractured” or “signal” with a single accent line.

**2. Hero section (center-aligned)**  
- **Title:** “Fractured Key” — 48px Bold, `#F8FAFC`, centered.  
- **Accent line:** Short horizontal bar under title, 4px height, `#3B82F6`, ~120px wide, centered.  
- **Tagline:** One line, 16–18px, `#38BDF8`, e.g. “A next-generation secure authentication system”.  
- **Description:** 2–4 lines, 14–16px, `#94A3B8`, max-width ~680px, centered.  
- **CTA:** Single primary button, e.g. “Get Started”, 52px height, centered.  
- **Secondary CTAs:** “Explore Features”, “Login” — text or outline buttons, 8px apart.  
- **Spacing:** 40px below title, 24px below tagline, 24px below description, 40px below CTAs.

**3. Feature highlights (3–5 cards)**  
- Horizontal row (or 2x2 + 1) of cards.  
- Each card:  
  - Icon (24–32px, accent color)  
  - Title (14–16px Bold)  
  - Short line of body text (12–14px, muted)  
- Card: same as global card style; padding 20–24px; 16px gap between cards.  
- Suggested features:  
  1. **Encryption** — AES-256-GCM, Argon2id.  
  2. **Fragmented secrets** — Shamir Secret Sharing.  
  3. **Steganography** — Hidden in images.  
  4. **Offline-first** — No cloud dependency.  
  5. **Recovery** — Partial fragments enough to recover.

**4. Footer**  
- One line: “Secure · Offline · Portfolio-ready” or similar, 11px, `#64748B`, centered.  
- 24–32px padding bottom.

### Responsive behavior

- **Desktop:** Hero + 5 cards in one row (or 3 + 2).  
- **Tablet:** Cards 2 per row.  
- **Mobile:** Single column; hero text and buttons stack; cards stack; padding 16–24px.

---

## 6. Animation & Interaction Suggestions

### Entry (landing → app)

- **Landing:** Optional short fade-in (200–300ms) for hero block, then tagline, then description, then CTAs (stagger 80–100ms).  
- **Transition to app:** Landing content fade-out 150ms → main app fade-in 200ms (or instant swap if toolkit is limited).

### Micro-interactions

| Element | Trigger | Effect |
|--------|--------|--------|
| Buttons | Hover | Background transition 150ms; optional scale 1.02 |
| Buttons | Focus | 2px outline `#3B82F6`, offset 2px |
| Cards | Hover | Border color → `#3B82F6`, 150ms ease |
| Inputs | Focus | Border → `#3B82F6`, 150ms ease |
| Nav items | Hover | Background `#334155`, 100ms |
| Nav items | Active | Background `#1E293B`, accent text/icon |

### Loading states

- **Encrypt/Decrypt:** Indeterminate progress bar (blue), 8px height, rounded.  
- **Buttons:** Disabled state (reduced opacity or grey) + “Processing…” in status bar.  
- Optional: subtle pulse on primary CTA when idle (low opacity, 1.5s loop).

### Scroll (if landing is long)

- Cards: Fade-in + slight Y move (e.g. 12px) when entering viewport (once).  
- Duration: 300–400ms ease-out.

### Accessibility

- All interactive elements: visible focus ring (2px `#3B82F6`).  
- No motion-only critical info; reduce motion respected if implemented.  
- Focus order: hero CTA → Explore → Login → (in app) sidebar → content.

---

## 7. Icons

- **Style:** Outline or duotone; 24px default, 20px in nav, 32px in feature cards.  
- **Set:** Segoe UI Fluent Icons, Phosphor, or Heroicons; single set app-wide.  
- **Color:** Default `#94A3B8`; active/hover `#3B82F6`; success `#10B981`.  
- **Usage:** Nav (Encrypt, Decrypt, Manual, About), feature cards, buttons (e.g. lock, key, shield), status indicators.

---

## 8. Summary Checklist

- [x] Color palette (HEX) — dark base + blue gradient accents + semantic  
- [x] Typography — Inter (or fallback) for heading + body; sizes and weights  
- [x] Button, card, input, modal styles — radii, colors, hover/focus  
- [x] Layout structure — grid, app shell, content width  
- [x] UI flow — landing → app, tabs, actions  
- [x] Intro page wireframe — hero, tagline, description, CTA, feature cards, footer  
- [x] Animations and interactions — hover, focus, loading, optional entry/scroll  

Use this spec to keep the Fractured Key GUI consistent, accessible, and on-theme (tech, mysterious, sleek, security/fragments/futuristic).
