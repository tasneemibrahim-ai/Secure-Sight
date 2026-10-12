# HomePage Spec

**Spec ID:** 01  
**Status:** Approved  
**Owner:** SecureSight Frontend Team  
**Last Updated:** 2026-03-13  
**Route:** `/`  
**Access:** Public (no authentication required)

---

## Overview

The HomePage is the public-facing landing page for SecureSight. Its primary goal is to
communicate the product's value proposition to potential organizational subscribers
(police departments, hospitals, fire stations) and drive them toward sign-up or login.

It must feel **premium, trustworthy, and technically credible** — visitors are public-safety
decision-makers, not general consumers.

---

## User Stories

- As a **potential subscriber** (police chief, hospital security director), I want to
  understand what SecureSight does at a glance so I can evaluate whether it fits my
  organization's needs.
- As a **returning user**, I want to quickly find the Login button so I can access my
  dashboard without scrolling.
- As a **new visitor**, I want to see the key threat types the system detects so I know
  if it covers the scenarios my organization faces.
- As a **mobile user**, I want all content to be readable and CTAs to be tappable
  on small screens.

---

## Functional Requirements

### FR-01 — Navigation Bar

**Description:** Fixed top navigation bar visible at all scroll positions.

**Acceptance Criteria:**
- [ ] Logo / brand mark on the left: "SecureSight" wordmark with cyan accent color
- [ ] Navigation links: Home, Features, How It Works, Contact
- [ ] Primary CTA button "Get Started" → navigates to `/signup`
- [ ] Secondary link "Login" → navigates to `/login`
- [ ] Navigation collapses into a hamburger menu on mobile (≤ 768px)
- [ ] Bar has a glassmorphism dark background with slight blur on scroll

### FR-02 — Hero Section

**Description:** Full-viewport hero section that immediately communicates the product.

**Acceptance Criteria:**
- [ ] Headline: "Real-Time AI Surveillance. Zero Missed Threats." (or equivalent approved copy)
- [ ] Subheadline: brief product description (2–3 sentences max)
- [ ] Primary CTA: "Start Free Trial" → `/signup`
- [ ] Secondary CTA: "Watch Demo" → triggers a modal or scrolls to video section
- [ ] Background: animated gradient or particle network on dark navy (`#0A0F1E`)
- [ ] A hero visual (abstract eye / network graphic, or camera + AI overlay) occupies
  the right half on desktop, collapses under text on mobile
- [ ] Subtle scan-line or data-stream animation to reinforce the AI/tech feel

### FR-03 — Stats / Social Proof Bar

**Description:** A horizontal strip of key numbers to build credibility.

**Acceptance Criteria:**
- [ ] At least 3 stats with animated count-up on scroll-into-view, e.g.:
  - "99.7% Detection Accuracy"
  - "< 800ms Alert Latency"
  - "50+ Threat Categories"
  - "24/7 Monitoring"
- [ ] Stats are sourced from `mockData.js` (not hardcoded inline)
- [ ] Animated count-up uses `IntersectionObserver` (or equivalent hook), not
  a timer that fires immediately on load

### FR-04 — Features Section

**Description:** 3-column grid of feature cards showcasing what the system does.

**Acceptance Criteria:**
- [ ] Section heading: "How SecureSight Protects You"
- [ ] At least 6 feature cards, grouped by category:
  - **Threat Detection:** Theft, Fighting/Violence, Fire & Smoke, Injury Detection
  - **Response Routing:** Automated MQTT alert routing to Police / Hospital / Fire
  - **System Intelligence:** Two-Stream AI model, real-time inference, ViT scene understanding
- [ ] Each card: icon + title + 2-sentence description
- [ ] Cards use the glassmorphism pattern (see design system in `00-overview.md`)
- [ ] Hover: card lifts slightly with cyan border glow
- [ ] Responsive: 3 cols → 2 cols → 1 col

### FR-05 — How It Works Section

**Description:** A numbered step-by-step flow showing the system pipeline.

**Acceptance Criteria:**
- [ ] Steps presented as a horizontal flow on desktop, vertical on mobile:
  1. CCTV camera captures footage
  2. Two-Stream AI model analyses frames in real time
  3. Threat classification and severity scoring
  4. MQTT alert routed to the correct responder channel
  5. Responder dashboard displays actionable alert
- [ ] Each step has: step number, icon, title, short description
- [ ] Steps connected by animated dashed-line arrows (desktop only)

### FR-06 — Responder Roles Section

**Description:** Communicates the role-based access model to prospective customers.

**Acceptance Criteria:**
- [ ] Three highlighted role cards: Police 🚔, Hospital 🏥, Firefighters 🔥
- [ ] Each card lists the specific alert categories it receives
- [ ] CTA within each card: "Learn More" or "Sign Up as [Role]" → `/signup`
- [ ] Cards animate in (fade + slide up) when scrolled into view

### FR-07 — Footer

**Description:** Standard informational footer.

**Acceptance Criteria:**
- [ ] Columns: Product (Features, Pricing, Docs), Company (About, Blog, Careers),
  Legal (Privacy, Terms), Contact
- [ ] Social links: GitHub, LinkedIn, Twitter/X (icons only, links go to `#` for now)
- [ ] Copyright: "© 2026 SecureSight. All rights reserved."
- [ ] Dark background, lighter than `#0A0F1E` to visually separate from page

---

## Non-Functional Requirements

- **Performance:** Largest Contentful Paint ≤ 2.5s on simulated 4G
- **Accessibility:** All interactive elements keyboard-navigable; `aria-label` on icon-only buttons
- **Responsiveness:** Must render correctly at 320px, 768px, 1024px, 1440px
- **Animation:** All CSS animations must respect `prefers-reduced-motion`
- **No layout shift:** Hero image and stats bar must not shift as fonts load

---

## UI Layout (Desktop)

```
┌──────────────────────────────────────────────────────────────┐
│  NAVBAR  [Logo]    Home  Features  How It Works    [Login] [Get Started] │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│   HERO                          [ Hero Visual / AI Eye ]    │
│   "Real-Time AI Surveillance."                              │
│   "Zero Missed Threats."                                    │
│   [Start Free Trial]  [Watch Demo]                          │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│  [ 99.7% Accuracy ]  [ <800ms Latency ]  [ 50+ Threats ]  [ 24/7 ] │
├──────────────────────────────────────────────────────────────┤
│  HOW SECURESIGHT PROTECTS YOU                               │
│  [ Card ] [ Card ] [ Card ]                                 │
│  [ Card ] [ Card ] [ Card ]                                 │
├──────────────────────────────────────────────────────────────┤
│  HOW IT WORKS                                               │
│  [1]───[2]───[3]───[4]───[5]                                │
├──────────────────────────────────────────────────────────────┤
│  RESPONDER ROLES                                            │
│  [ Police 🚔 ]  [ Hospital 🏥 ]  [ Firefighters 🔥 ]       │
├──────────────────────────────────────────────────────────────┤
│  FOOTER                                                     │
└──────────────────────────────────────────────────────────────┘
```

---

## Mock Data

All dynamic content must be imported from `src/mock/mockData.js`:

```js
export const heroStats = [
  { label: "Detection Accuracy", value: 99.7, suffix: "%" },
  { label: "Alert Latency", value: 800, prefix: "<", suffix: "ms" },
  { label: "Threat Categories", value: 50, suffix: "+" },
  { label: "Uptime", value: 99.9, suffix: "%" },
];

export const features = [
  { id: "f1", icon: "shield", title: "Theft Detection", category: "threat", description: "..." },
  // ... more features
];

export const howItWorksSteps = [
  { step: 1, icon: "camera", title: "Camera Capture", description: "..." },
  // ... more steps
];
```

---

## Out of Scope

- Real video streaming or live camera feeds on the landing page
- Pricing page (separate spec if built)
- Blog section
- Actual contact form submission (form renders, submit is a no-op)
- Dark/light mode toggle (dark mode only for MVP)

---

## Open Questions

- None — spec approved.
