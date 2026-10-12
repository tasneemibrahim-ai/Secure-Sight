# SecureSight — Project Overview

**Spec ID:** 00  
**Status:** Approved  
**Owner:** SecureSight Frontend Team  
**Last Updated:** 2026-06-04

---

## 🛡️ What Is SecureSight?

SecureSight is an **intelligent video anomaly detection system** for smart surveillance
applications. It processes live video streams, or uploaded videos during testing, and
produces alerts when abnormal activities are detected.

The anomaly detection engine is based on a **Vision Transformer architecture** trained
with the UCF Crime Dataset and official temporal annotations. The annotation-guided
training improved performance from early manually extracted feature experiments, which
reached roughly 50-60% accuracy, to approximately 70% accuracy.

Additional experiments evaluated evolutionary optimization techniques, including Grey
Wolf Optimization, Particle Swarm Optimization, Spider Monkey Optimization, Shuffled
Frog Leaping Algorithm, and Harris Hawks Optimization. These experiments did not
surpass the baseline model, so the baseline Vision Transformer model was retained for
deployment.

The deployed system includes inference-time safeguards such as confidence thresholding
and temporal confirmation delays to reduce false alerts. Privacy is addressed by
processing videos for classification without permanent video storage.

---

## 🎯 Project Goals

1. Give security operators a live, at-a-glance threat status across all cameras
2. Eliminate manual triage — AI routes alerts automatically to the right responder
3. Provide role-based access so each responder only sees alerts relevant to them
4. Allow an admin to manage subscriber accounts and assign roles post-signup

---

## 🔭 Scope — This Contributor's Pages

The frontend is divided across multiple contributors. **This spec file covers only:**

| Page | Route | Description |
|---|---|---|
| **HomePage** | `/` | Public landing page — explains the product, CTA to sign up / log in |
| **LoginPage** | `/login` | Authenticate existing users |
| **SignUpPage** | `/signup` | Register a new account (role assigned by admin later) |

> 📄 See [`01-home-page.md`](./01-home-page.md) and [`02-auth.md`](./02-auth.md) for
> detailed specs on each of these pages.

---

## 🚫 Out of Scope (Teammate Pages)

The following pages are **assigned to separate contributors** and have their own spec files:

| Page | Spec File | Owner |
|---|---|---|
| Police Dashboard | `03-dashboard.md` (police section) | Teammate A |
| Hospital Dashboard | `03-dashboard.md` (hospital section) | Teammate B |
| Firefighters Dashboard | `03-dashboard.md` (fire section) | Teammate C |
| Admin Dashboard | `03-dashboard.md` (admin section) | Teammate D |

Do **not** build or modify these pages as part of your branch.

---

## 👤 User Roles

| Role | Alert Category | Can See |
|---|---|---|
| `police` | Crime | Theft, fighting, vandalism alerts |
| `hospital` | Medical | Injury, unconscious person, medical emergency alerts |
| `firefighters` | Fire/Hazard | Fire, smoke, explosion alerts |
| `admin` | All | All alerts + subscriber management + role assignment |

> ⚠️ **Role assignment happens post-signup.** When a user signs up, they have no role yet.
> The admin reviews pending accounts and assigns a role from the Admin Dashboard.
> Until a role is assigned, the user sees a "Pending Approval" screen after login.

---

## 🧑‍💻 Tech Stack

| Layer | Technology | Version |
|---|---|---|
| UI Framework | React | 18.x |
| Build Tool | Vite | ^5.x |
| Styling | Tailwind CSS | ^3.x |
| Routing | React Router | v6 |
| State (MVP) | React Context + `useState` / `useReducer` | — |
| Mock Data | `src/mock/mockData.js` | — |
| API Server | Node.js + Express | 5.x |
| Model Inference | Python + PyTorch | local environment |
| Demo Videos | `test_videos/` | — |

> 📐 For the rationale behind these choices, see [`../adr/0001-tech-stack.md`](../adr/0001-tech-stack.md).

---

## 🎨 Design System

All pages **must** follow this design system. Do not deviate without opening a discussion.

### Color Palette

| Token | Hex | Usage |
|---|---|---|
| `bg-primary` | `#0A0F1E` | Page background (dark navy) |
| `accent-cyan` | `#00E5FF` | CTAs, highlight borders, active states |
| `accent-cyan-dim` | `#00B8D4` | Hover state for cyan elements |
| `surface` | `rgba(255,255,255,0.05)` | Glassmorphism card background |
| `surface-border` | `rgba(255,255,255,0.1)` | Glassmorphism card border |
| `text-primary` | `#FFFFFF` | Headings, primary text |
| `text-secondary` | `#94A3B8` | Subtext, labels, captions |
| `danger` | `#FF4444` | Error states, high-severity alerts |
| `warning` | `#FFB020` | Medium-severity alerts |
| `success` | `#00E676` | Success states, low-severity alerts |

### Typography

- **Font:** [Inter](https://fonts.google.com/specimen/Inter) — import via Google Fonts
- **Headings:** `font-weight: 700` (bold), tracked slightly (`letter-spacing: -0.02em`)
- **Body:** `font-weight: 400`, line-height `1.6`
- **Monospace / ID labels:** `font-family: 'JetBrains Mono', monospace`

### Component Patterns

#### Glassmorphism Card
```
background: rgba(255, 255, 255, 0.05)
border: 1px solid rgba(255, 255, 255, 0.10)
border-radius: 16px
backdrop-filter: blur(20px)
box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4)
```

#### Cyan Glow Button (Primary CTA)
```
background: #00E5FF
color: #0A0F1E
font-weight: 700
border-radius: 8px
box-shadow: 0 0 20px rgba(0, 229, 255, 0.4)
transition: box-shadow 0.2s ease, transform 0.1s ease
hover → box-shadow: 0 0 35px rgba(0, 229, 255, 0.7), transform: translateY(-2px)
```

#### Animated Background
All pages use one of:
- **Particle network** — animated floating nodes with connecting lines (auth pages)
- **Grid pulse** — subtle dark grid with slow pulse animation (dashboard pages)
- **Hero gradient** — animated dark-to-navy sweep (landing page)

### Spacing & Layout
- Max content width: `1280px`
- Base spacing unit: `8px` (Tailwind's `2` = 8px)
- Section vertical padding: `py-20` (80px)

---

## 📦 Mock Data

All mock data lives in **`src/mock/mockData.js`**.

### Required Exports for Auth Pages

```js
// Array of mock users for login simulation
export const mockUsers = [
  {
    id: "usr_001",
    name: "Alex Rivera",
    email: "alex@police.gov",
    password: "secure123",   // plaintext for mock only
    role: "police",
    avatar: null,
    status: "approved"
  },
  {
    id: "usr_002",
    name: "Dr. Sara Chen",
    email: "sara@hospital.org",
    password: "medic456",
    role: "hospital",
    avatar: null,
    status: "approved"
  },
  {
    id: "usr_003",
    name: "Omar Hassan",
    email: "omar@fire.dept",
    password: "flame789",
    role: "firefighters",
    avatar: null,
    status: "approved"
  },
  {
    id: "usr_004",
    name: "Admin User",
    email: "admin@securesight.ai",
    password: "admin000",
    role: "admin",
    avatar: null,
    status: "approved"
  },
  {
    id: "usr_005",
    name: "New Recruit",
    email: "recruit@police.gov",
    password: "pending123",
    role: null,             // no role yet — admin must assign
    avatar: null,
    status: "pending"
  }
];
```

---

## 📂 Recommended Folder Structure

```
src/
├── assets/               # Static images, SVGs, icons
├── components/
│   ├── ui/               # Reusable primitives (Button, Input, Card, Badge)
│   └── layout/           # Navbar, Footer, PageWrapper
├── contexts/             # React context providers (AuthContext, AlertContext)
├── hooks/                # Custom hooks (useAuth, useMockAlerts)
├── mock/
│   └── mockData.js       # Single source of truth for all mock data
├── pages/
│   ├── HomePage.jsx
│   ├── LoginPage.jsx
│   ├── SignUpPage.jsx
│   └── dashboard/        # Teammate-owned — do not modify
│       ├── PoliceDashboard.jsx
│       ├── HospitalDashboard.jsx
│       ├── FirefightersDashboard.jsx
│       └── AdminDashboard.jsx
├── router/
│   └── AppRouter.jsx     # All routes defined here
└── styles/
    └── globals.css       # Tailwind base + custom CSS vars
```

---

## 🔗 References

- [`docs/adr/0001-tech-stack.md`](../adr/0001-tech-stack.md) — why this stack?
- [`docs/specs/01-home-page.md`](./01-home-page.md) — HomePage spec
- [`docs/specs/02-auth.md`](./02-auth.md) — Login + SignUp spec
- [`docs/specs/03-dashboard.md`](./03-dashboard.md) — Dashboard specs (teammate-owned)
- [`CONTRIBUTING.md`](../../CONTRIBUTING.md) — how to contribute
