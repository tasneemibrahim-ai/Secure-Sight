<div align="center">

<img src="https://img.shields.io/badge/SecureSight-AI%20Surveillance-00E5FF?style=for-the-badge&logo=shield&logoColor=0A0F1E" alt="SecureSight" />

# 🛡️ SecureSight

### AI-Powered Real-Time Intelligent Surveillance System

[![React](https://img.shields.io/badge/React-18.x-61DAFB?style=flat-square&logo=react)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-5.x-646CFF?style=flat-square&logo=vite)](https://vitejs.dev)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v3-06B6D4?style=flat-square&logo=tailwindcss)](https://tailwindcss.com)
[![React Router](https://img.shields.io/badge/React_Router-v6-CA4245?style=flat-square&logo=reactrouter)](https://reactrouter.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen?style=flat-square)](CONTRIBUTING.md)

**Detects threats. Routes alerts. Protects communities — in under 800ms.**

[🚀 Live Demo](#) · [📖 Specs](docs/specs/00-overview.md) · [🐛 Report Bug](https://github.com/Omnia-adel1/SecureSight/issues) · [✨ Request Feature](https://github.com/Omnia-adel1/SecureSight/issues)

</div>

---

## 📋 Table of Contents

- [About the Project](#-about-the-project)
- [Project Abstract](#project-abstract)
- [System Architecture](#-system-architecture)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [Project Structure](#-project-structure)
- [Pages & Routes](#-pages--routes)
- [API Reference](#-api-reference)
- [Mock Data Schema](#-mock-data-schema)
- [Design System](#-design-system)
- [Specs & Documentation](#-specs--documentation)
- [Contributing](#-contributing)
- [Team](#-team)
- [License](#-license)

---

## 🔍 About the Project

**SecureSight** is an intelligent video anomaly detection system for smart surveillance. It processes live video streams, or uploaded videos during testing, and raises alerts when abnormal activity is detected.

The system serves **three subscriber roles**:

| Role | Alert Types | Access |
|---|---|---|
| 🚔 **Police** | Theft, Fighting, Vandalism, Suspicious Activity | `/dashboard/police` |
| 🏥 **Hospital** | Injury, Person Down, Medical Emergency | `/dashboard/hospital` |
| 🚒 **Firefighters** | Fire, Smoke, Explosion, Gas Leak | `/dashboard/firefighters` |
| 🔐 **Admin** | All alerts + subscriber management | `/dashboard/admin` |

> ℹ️ **This repository contains the web interface, Node/Express API, and local model inference code.** The current app can run against demo videos through `test_videos/` and the Python inference engine in `Model/`.

---

## Project Abstract

**Abstract—** SecureSight is an intelligent, real-time video anomaly detection system designed for smart surveillance applications. The system processes live or uploaded video streams and raises automated alerts to relevant responders upon detecting abnormal activities. The core anomaly detection model is built on a hybrid deep learning architecture that fuses spatial features extracted via a pre-trained ResNet-50 network with temporal features extracted using an R(2+1)D-18 video network. These concatenated representations are projected into a unified feature space and processed by a 4-layer Vision Transformer (ViT) temporal encoder with 8-head self-attention to classify activities into nine distinct security categories based on the UCF Crime dataset.

To optimize detection accuracy, the model was trained using supervised learning guided by official temporal annotations, increasing classification accuracy to approximately 70%, which significantly outperformed early experiments using manually extracted, frame-level features (50-60% accuracy). Furthermore, metaheuristic evolutionary optimization algorithms—specifically Grey Wolf Optimization (GWO), Particle Swarm Optimization (PSO), Spider Monkey Optimization (SMO), Shuffled Frog Leaping Algorithm (SFLA), and Harris Hawks Optimization (HHO)—were comprehensively evaluated for hyperparameters search, but the baseline Vision Transformer configuration was ultimately retained as it yielded the most stable performance.

The end-to-end system is deployed via a decoupled client-server architecture. The frontend is built on React 18, Vite, and Tailwind CSS, presenting role-based dashboards tailored for public safety entities (Police, Hospital, Firefighters, and Administrators). The backend is powered by a Node.js and Express API gateway paired with a MySQL database to manage authentication, alert dispatching, and logs, communicating with a PyTorch model inference engine. To minimize false positives, the system implements inference-time safeguards including confidence thresholding (set at 0.7) and temporal confirmation delays. Privacy concerns are strictly handled by conducting inference on-the-fly without persistent video storage. Overall, SecureSight presents a fully integrated, secure, and performant AI-driven surveillance solution with ethical safeguards.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        SecureSight System                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│   CCTV Cameras                                                    │
│       │                                                           │
│       ▼                                                           │
│   ┌──────────────────────────────┐                               │
│   │   Vision Transformer Model    │                               │
│   │   ┌──────────────────────┐    │                               │
│   │   │ Temporal annotations │    │  ← UCF Crime supervised data  │
│   │   └──────────┬───────────┘    │                               │
│   │              ▼                │                               │
│   │   ┌──────────────────────┐    │                               │
│   │   │ Confidence + delay   │    │  ← False-alert safeguards     │
│   │   └──────────┬───────────┘    │                               │
│   └──────────────┼───────────────┘                               │
│                  │ Threat Classification                           │
│                  ▼                                                 │
│   ┌──────────────────────────┐                                    │
│   │  Node/Express API        │                                    │
│   │  classify + auth routes  │                                    │
│   └──────┬──────┬──────┬─────┘                                    │
│          │      │      │                                          │
│     police  hospital  fire                                         │
│          │      │      │                                          │
│   ┌──────▼──────▼──────▼──────┐                                   │
│   │   SecureSight Frontend    │  ← This Repository               │
│   │   React 18 + Vite         │                                   │
│   │   Role-based Dashboards   │                                   │
│   └───────────────────────────┘                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

### Implemented (Frontend MVP)
- ✅ **Public Landing Page** — animated AI orb hero, stats, feature cards, how-it-works, subscriber cards
- ✅ **Login Page** — split layout with canvas-rendered cyber-eye animation, mock auth, form validation
- ✅ **Sign Up Page** — 2-step glassmorphism form, password strength meter, org type dropdown, success state
- ✅ **Spec-Driven Development** — full `docs/specs/` folder with approved specs for all pages
- ✅ **Design System** — Tailwind tokens, glassmorphism utilities, cyan glow animations
- ✅ **Responsive** — mobile-first, tested at 375px / 768px / 1024px / 1440px

### Upcoming (Teammate Pages)
- 🔲 Police Dashboard — live alert feed, severity badges, acknowledge flow
- 🔲 Hospital Dashboard — triage panel, dispatch tracking
- 🔲 Firefighters Dashboard — hazard feed, spread-risk indicators
- 🔲 Admin Dashboard — subscriber management, role assignment table

---

## 🛠️ Tech Stack

| Layer | Technology | Version | Why |
|---|---|---|---|
| UI Framework | **React** | 18.x | Concurrent mode for real-time UI updates |
| Build Tool | **Vite** | ^5.x | <300ms cold start, instant HMR |
| Styling | **Tailwind CSS** | ^3.x | Utility-first, prevents CSS conflicts across branches |
| Routing | **React Router** | v6 | Nested routes map cleanly to role-based pages |
| Icons | **lucide-react** | latest | Consistent, tree-shakeable icon set |
| API Server | **Node.js + Express** | Express 5.x | Serves auth, demo videos, and classification endpoints |
| Model Inference | **Python + PyTorch** | local environment | Runs the SecureSight anomaly detection model |
| State (MVP) | **React Context + hooks** | — | Lightweight UI state for auth and dashboards |
| Demo Data | **`test_videos/` + MySQL schema** | — | Supports local testing without permanent video storage |

> 📐 For the full rationale, see [`docs/adr/0001-tech-stack.md`](docs/adr/0001-tech-stack.md)

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** ≥ 18.x — [download](https://nodejs.org)
- **npm** ≥ 9.x (comes with Node)
- **Git** — [download](https://git-scm.com)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Omnia-adel1/SecureSight.git

# 2. Navigate into the project
cd SecureSight

# 3. Install dependencies
npm install

# 4. Start the development server
npm run dev
```

The app will be available at **[http://localhost:5173](http://localhost:5173)**

### Available Scripts

| Command | Description |
|---|---|
| `npm run dev` | Start Vite dev server with HMR |
| `npm run build` | Build production bundle to `dist/` |
| `npm run preview` | Preview production build locally |
| `npm run lint` | Run ESLint |

---

## 📁 Project Structure

```
SecureSight/
│
├── .github/
│   └── PULL_REQUEST_TEMPLATE.md    # Required checklist for all PRs
│
├── docs/                            # Spec-kit documentation
│   ├── README.md                    # How to read/write specs
│   ├── adr/
│   │   └── 0001-tech-stack.md      # Architecture Decision Record
│   └── specs/
│       ├── 00-overview.md          # Project overview & design system
│       ├── 01-home-page.md         # HomePage functional spec
│       ├── 02-auth.md              # Login + SignUp spec
│       └── 03-dashboard.md         # All 4 dashboards spec (teammate-owned)
│
├── public/
│   └── favicon.svg
│
├── src/
│   ├── assets/                     # Static images & SVGs
│   │
│   ├── mock/
│   │   └── mockData.js             # ⭐ Single source of truth for all mock data
│   │
│   ├── pages/
│   │   ├── HomePage.jsx            # Public landing page  [/]
│   │   ├── LoginPage.jsx           # Login page           [/login]
│   │   ├── SignUpPage.jsx          # Sign up page         [/signup]
│   │   └── dashboard/              # Teammate-owned pages
│   │       ├── PoliceDashboard.jsx
│   │       ├── HospitalDashboard.jsx
│   │       ├── FirefightersDashboard.jsx
│   │       └── AdminDashboard.jsx
│   │
│   ├── App.jsx                     # Router setup
│   ├── index.css                   # Tailwind + global utilities
│   └── main.jsx                    # React entry point
│
├── CONTRIBUTING.md                  # Contribution workflow & rules
├── tailwind.config.js               # Design tokens & custom animations
├── vite.config.js
└── package.json
```

---

## 🗺️ Pages & Routes

| Route | Component | Access | Status |
|---|---|---|---|
| `/` | `HomePage` | Public | ✅ Done |
| `/login` | `LoginPage` | Public | ✅ Done |
| `/signup` | `SignUpPage` | Public | ✅ Done |
| `/dashboard` | Redirect by role | Auth required | 🔲 Pending |
| `/dashboard/police` | `PoliceDashboard` | `role: police` | 🔲 Teammate A |
| `/dashboard/hospital` | `HospitalDashboard` | `role: hospital` | 🔲 Teammate B |
| `/dashboard/firefighters` | `FirefightersDashboard` | `role: firefighters` | 🔲 Teammate C |
| `/dashboard/admin` | `AdminDashboard` | `role: admin` | 🔲 Teammate D |
| `/pending-approval` | `PendingPage` | Auth required | 🔲 Pending |
| `*` | Redirect → `/` | — | ✅ Done |

---

## 📡 API Reference

> ℹ️ **The local API is implemented in `server/index.js`.** It serves authentication, demo video discovery, and video classification endpoints. Classification requests are forwarded to the Python model service in `Model/` when available, with a direct Python-process fallback for local testing.

### Base URL

```
Development: http://localhost:3001/api
```

### Authentication

All protected endpoints require a Bearer token in the `Authorization` header:

```http
Authorization: Bearer <jwt_token>
```

---

### 🔐 Auth Endpoints

#### `POST /auth/register`

Register a new user account. Role is assigned by admin after approval.

**Request Body:**
```json
{
  "name":         "Alex Rivera",
  "email":        "alex@police.gov",
  "password":     "SecurePass@123",
  "orgName":      "Cairo Police District 5",
  "orgType":      "police",
  "phone":        "+20 100 123 4567",
  "location":     "Cairo, Egypt"
}
```

**Success Response — `201 Created`:**
```json
{
  "success": true,
  "message": "Account created. Awaiting admin approval.",
  "user": {
    "id":     "usr_abc123",
    "name":   "Alex Rivera",
    "email":  "alex@police.gov",
    "role":   null,
    "status": "pending"
  }
}
```

**Error Responses:**

| Code | Reason | Body |
|---|---|---|
| `400` | Missing required fields | `{ "error": "VALIDATION_ERROR", "fields": { "email": "required" } }` |
| `409` | Email already registered | `{ "error": "EMAIL_EXISTS", "message": "An account with this email already exists." }` |
| `422` | Password too weak | `{ "error": "WEAK_PASSWORD", "message": "Password must be ≥8 chars and contain a number." }` |

---

#### `POST /auth/login`

Authenticate a user and receive a JWT token.

**Request Body:**
```json
{
  "email":    "alex@police.gov",
  "password": "SecurePass@123"
}
```

**Success Response — `200 OK`:**
```json
{
  "success": true,
  "token":   "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id":     "usr_abc123",
    "name":   "Alex Rivera",
    "email":  "alex@police.gov",
    "role":   "police",
    "status": "approved",
    "avatar": null
  }
}
```

**Error Responses:**

| Code | Reason | Body |
|---|---|---|
| `401` | Wrong credentials | `{ "error": "INVALID_CREDENTIALS", "message": "Invalid email or password." }` |
| `403` | Account pending | `{ "error": "ACCOUNT_PENDING", "message": "Your account is awaiting admin approval." }` |
| `429` | Too many attempts | `{ "error": "RATE_LIMITED", "retryAfter": 60 }` |

---

#### `POST /auth/logout`

Invalidate the current session token.

**Headers:** `Authorization: Bearer <token>`

**Success Response — `200 OK`:**
```json
{ "success": true, "message": "Logged out successfully." }
```

---

#### `GET /auth/me`

Returns the currently authenticated user's profile.

**Headers:** `Authorization: Bearer <token>`

**Success Response — `200 OK`:**
```json
{
  "id":        "usr_abc123",
  "name":      "Alex Rivera",
  "email":     "alex@police.gov",
  "role":      "police",
  "status":    "approved",
  "orgName":   "Cairo Police District 5",
  "orgType":   "police",
  "location":  "Cairo, Egypt",
  "createdAt": "2026-03-13T20:00:00Z"
}
```

---

### 🚨 Alerts Endpoints

#### `GET /alerts`

Fetch all alerts visible to the authenticated user (filtered by role server-side).

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `type` | `string` | — | Filter by alert type: `theft`, `fight`, `fire`, `injury`, etc. |
| `severity` | `string` | — | `critical`, `high`, `medium`, `low` |
| `status` | `string` | `active` | `active`, `acknowledged`, `resolved` |
| `limit` | `number` | `20` | Results per page (max 100) |
| `cursor` | `string` | — | Pagination cursor from previous response |

**Success Response — `200 OK`:**
```json
{
  "alerts": [
    {
      "id":          "alrt_001",
      "type":        "theft",
      "category":    "police",
      "severity":    "critical",
      "status":      "active",
      "cameraId":    "CAM-07",
      "location":    "Zone 4 — Main Gate",
      "confidence":  0.987,
      "summary":     "Suspected shoplifting detected. Individual concealing merchandise.",
      "detectedAt":  "2026-03-13T21:45:00Z",
      "thumbnail":   "https://cdn.securesight.ai/snapshots/alrt_001.jpg"
    }
  ],
  "nextCursor": "eyJpZCI6ImFscnRfMDIwIn0=",
  "total":      142
}
```

---

#### `GET /alerts/:id`

Fetch full detail for a single alert.

**Success Response — `200 OK`:**
```json
{
  "id":          "alrt_001",
  "type":        "theft",
  "category":    "police",
  "severity":    "critical",
  "status":      "active",
  "cameraId":    "CAM-07",
  "location":    "Zone 4 — Main Gate",
  "confidence":  0.987,
  "summary":     "Suspected shoplifting detected.",
  "aiInsights":  "Subject entered at 21:43:12. Concealment motion detected at 21:44:58.",
  "detectedAt":  "2026-03-13T21:45:00Z",
  "thumbnail":   "https://cdn.securesight.ai/snapshots/alrt_001.jpg",
  "videoClip":   "https://cdn.securesight.ai/clips/alrt_001.mp4"
}
```

---

#### `PATCH /alerts/:id/acknowledge`

Mark an alert as acknowledged by the current responder.

**Headers:** `Authorization: Bearer <token>`

**Request Body:** *(optional)*
```json
{ "note": "Unit dispatched to Zone 4." }
```

**Success Response — `200 OK`:**
```json
{
  "id":             "alrt_001",
  "status":         "acknowledged",
  "acknowledgedBy": "usr_abc123",
  "acknowledgedAt": "2026-03-13T21:47:30Z"
}
```

---

### 👥 Users / Admin Endpoints

#### `GET /admin/users`

List all registered users. **Admin role required.**

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `status` | `string` | — | `pending`, `approved` |
| `role` | `string` | — | `police`, `hospital`, `firefighters`, `admin` |
| `search` | `string` | — | Search by name or email |
| `limit` | `number` | `50` | Max 200 |

**Success Response — `200 OK`:**
```json
{
  "users": [
    {
      "id":        "usr_abc123",
      "name":      "Alex Rivera",
      "email":     "alex@police.gov",
      "role":      null,
      "status":    "pending",
      "orgName":   "Cairo Police District 5",
      "orgType":   "police",
      "createdAt": "2026-03-13T20:00:00Z"
    }
  ],
  "total": 24
}
```

---

#### `PATCH /admin/users/:id/role`

Assign a role and approve an account. **Admin role required.**

**Request Body:**
```json
{
  "role":   "police",
  "status": "approved"
}
```

**Success Response — `200 OK`:**
```json
{
  "id":         "usr_abc123",
  "role":       "police",
  "status":     "approved",
  "approvedBy": "usr_admin_001",
  "approvedAt": "2026-03-13T22:00:00Z"
}
```

**Error Responses:**

| Code | Reason |
|---|---|
| `403` | Caller is not admin |
| `404` | User not found |
| `400` | Invalid role value |

---

### 📊 Stats Endpoint

#### `GET /stats/dashboard`

Returns summary statistics for the authenticated user's dashboard.

**Success Response — `200 OK` (example for police role):**
```json
{
  "role":          "police",
  "activeAlerts":  4,
  "acknowledgedToday": 12,
  "avgResponseTime":   "4m 20s",
  "camerasOnline": 24,
  "camerasTotal":  30,
  "lastUpdated":   "2026-03-13T22:45:00Z"
}
```

---

### 🔌 Alert Transport (Future Real-Time Alerts)

For production deployments, SecureSight can publish confirmed anomaly alerts to role-scoped channels. The current local implementation focuses on demo-video classification through the Node/Express API and Python inference engine.

| Topic | Subscriber | Payload |
|---|---|---|
| `alerts/police` | Police role | Alert object (see above) |
| `alerts/hospital` | Hospital role | Alert object |
| `alerts/firefighters` | Firefighters role | Alert object |
| `alerts/all` | Admin role | Alert object with `category` field |
| `cameras/status` | All | `{ cameraId, status: "online"│"offline" }` |

**Example future connection:**
```
wss://api.securesight.ai/mqtt
```

---

## 📦 Local Demo Data Schema

Local testing uses demo videos from **`test_videos/`**, user records from the database schema, and any remaining UI seed data from **`src/mock/mockData.js`**.

### `mockUsers`

```js
export const mockUsers = [
  {
    id:       "usr_001",
    name:     "Alex Rivera",
    email:    "alex@police.gov",
    password: "secure123",          // plaintext — mock only, never log
    role:     "police",
    status:   "approved",
    orgName:  "Cairo Police District 5",
    orgType:  "police",
    location: "Cairo, Egypt",
  },
  // ... more users
];
```

### `policeAlerts`

```js
export const policeAlerts = [
  {
    id:         "alrt_001",
    type:       "theft",
    severity:   "critical",          // critical | high | medium | low
    status:     "active",            // active | acknowledged | resolved
    cameraId:   "CAM-07",
    location:   "Zone 4 — Main Gate",
    confidence: 0.987,
    summary:    "Shoplifting detected.",
    detectedAt: "2026-03-13T21:45:00Z",
  },
];
```

### `heroStats`

```js
export const heroStats = [
  { value: 99.7, suffix: "%",   label: "Detection Accuracy" },
  { value: 2,    prefix: "<", suffix: "s", label: "Response Time" },
  { value: 24,   suffix: "/7",  label: "Monitoring" },
  { value: 3,    suffix: "",    label: "Subscriber Types" },
];
```

---

## 🎨 Design System

| Token | Value | Usage |
|---|---|---|
| `--bg-primary` | `#0A0F1E` | Page background |
| `--accent-cyan` | `#00E5FF` | CTAs, borders, highlights |
| `--accent-cyan-dim` | `#00B8D4` | Hover states |
| `--danger` | `#FF4444` | Errors, critical alerts |
| `--warning` | `#FFB020` | Medium alerts |
| `--success` | `#00E676` | Success states |
| `--text-primary` | `#FFFFFF` | Headings |
| `--text-secondary` | `#94A3B8` | Body, labels |

**Glassmorphism Card:**
```css
background:    rgba(255, 255, 255, 0.05);
border:        1px solid rgba(255, 255, 255, 0.10);
border-radius: 16px;
backdrop-filter: blur(20px);
box-shadow:    0 8px 32px rgba(0, 0, 0, 0.4);
```

**Font:** [Inter](https://fonts.google.com/specimen/Inter) via Google Fonts

---

## 📖 Specs & Documentation

This project uses **Spec-Driven Development** (spec-kit methodology). Read specs *before* building.

| File | Contents |
|---|---|
| [`docs/specs/00-overview.md`](docs/specs/00-overview.md) | Project overview, design system, mock data shape |
| [`docs/specs/01-home-page.md`](docs/specs/01-home-page.md) | HomePage functional spec |
| [`docs/specs/02-auth.md`](docs/specs/02-auth.md) | Login + SignUp spec |
| [`docs/specs/03-dashboard.md`](docs/specs/03-dashboard.md) | Dashboard specs (teammate-owned) |
| [`docs/adr/0001-tech-stack.md`](docs/adr/0001-tech-stack.md) | Why this tech stack? |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Branch naming, PR process, rules |
| [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md) | PR checklist |

---

## 🤝 Contributing

> **Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before opening any PR.**

### Quick Start for Teammates

```bash
# 1. Clone & install
git clone https://github.com/Omnia-adel1/SecureSight.git
cd SecureSight && npm install

# 2. Read your spec
#    Open: docs/specs/03-dashboard.md → find your assigned section

# 3. Create your feature branch
git checkout -b feature/police-dashboard    # example

# 4. Build your page
#    File: src/pages/dashboard/PoliceDashboard.jsx
#    Mock data: src/mock/mockData.js (add at bottom, don't touch others' entries)

# 5. Open a PR linking the spec
```

### Branch Naming Convention

| Type | Pattern | Example |
|---|---|---|
| Feature page | `feature/[page-name]` | `feature/hospital-dashboard` |
| Spec / docs | `docs/[description]` | `docs/firefighters-spec` |
| Bug fix | `fix/[description]` | `fix/login-redirect` |
| Design system | `design/[component]` | `design/alert-card` |

### PR Requirements

Every PR **must**:
- [ ] Link to the spec it implements
- [ ] Pass `npm run lint` with 0 errors
- [ ] Include desktop + mobile screenshots
- [ ] Receive ≥ 1 approving review

---

## 👥 Team

| Role | Name | Pages |
|---|---|---|
| **Frontend Lead** | Omnia Adel | Project setup, HomePage, LoginPage, SignUpPage |
| **Teammate A** | — | Police Dashboard |
| **Teammate B** | — | Hospital Dashboard |
| **Teammate C** | — | Firefighters Dashboard |
| **Teammate D** | — | Admin Dashboard |

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ for public safety**

[![GitHub stars](https://img.shields.io/github/stars/Omnia-adel1/SecureSight?style=social)](https://github.com/Omnia-adel1/SecureSight)
[![GitHub forks](https://img.shields.io/github/forks/Omnia-adel1/SecureSight?style=social)](https://github.com/Omnia-adel1/SecureSight/fork)

</div>
