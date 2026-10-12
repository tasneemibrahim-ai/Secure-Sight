# ADR-0001: Frontend Tech Stack — React 18 + Vite + Tailwind CSS v3 + React Router v6

**Date:** 2026-03-13  
**Status:** Accepted  
**Deciders:** SecureSight Frontend Team

---

## Context

SecureSight needs a frontend for a real-time AI-powered surveillance system. The backend
(AI model inference, MQTT broker, alert routing) is being developed in parallel by a
separate team. The frontend must:

- Display live camera feeds and real-time threat alerts
- Support multiple user roles (police, hospital, firefighters, admin)
- Be fast to iterate on — the backend is **not yet ready**, so we rely on mock data
- Look premium and trust-inspiring (this is a public-safety tool)
- Allow multiple contributors to work on different pages in parallel without conflicts

We evaluated the following options before reaching a decision:

| Concern | Option A | Option B (Chosen) |
|---|---|---|
| Bundler | Create React App | **Vite** |
| Styling | Plain CSS / CSS Modules | **Tailwind CSS v3** |
| Routing | React Router v5 | **React Router v6** |
| State | Redux Toolkit | **React Context + hooks** (MVP phase) |

---

## Decision

We will use **React 18 + Vite + Tailwind CSS v3 + React Router v6** as the frontend stack.

### React 18
React's concurrent features (`useTransition`, `Suspense`) allow us to defer non-urgent
renders (e.g., alert list updates) without blocking the main UI thread — critical for a
real-time dashboard context.

### Vite
Vite's native ESM dev server starts in < 300 ms and supports instant HMR. Compared to
CRA's Webpack-based approach, Vite reduces cold-start time by ~10× and build time by ~3×.
Multiple contributors working on different pages will each benefit from faster feedback loops.

### Tailwind CSS v3
Utility-first CSS eliminates naming collisions across parallel-developed pages. The
JIT engine ships only used classes, keeping the production bundle small. The design
system tokens (colors, spacing, blur for glassmorphism) are centralised in
`tailwind.config.js`, ensuring visual consistency across all contributor pages.

### React Router v6
File-based nested routes cleanly map to the role-based page structure
(`/dashboard/police`, `/dashboard/hospital`, etc.). The `<Outlet>` API makes shared
layout wrappers trivial to implement.

### Mock Data Strategy
Until the backend is ready, all data lives in `src/mock/mockData.js`. Components import
from this file only — no hardcoded values inline. This allows the backend team to later
replace the mock with real API calls without touching component code.

---

## Consequences

### Positive
- Fast dev server (Vite) reduces contributor friction
- Tailwind's utility classes prevent CSS merge conflicts across branches
- React 18 concurrent mode future-proofs the real-time dashboard
- React Router v6 nested routes model role-based dashboards naturally
- Mock data layer means frontend work is fully unblocked from backend

### Negative / Trade-offs
- Tailwind requires all contributors to understand utility-first conventions;
  a brief onboarding note is added to `CONTRIBUTING.md`
- Context + hooks state management will need to migrate to a proper store
  (Zustand / Redux Toolkit) once real-time MQTT data is wired in
- No SSR: the surveillance dashboard is an authenticated app, so SSR/SEO is
  irrelevant for inner pages; the landing page is static enough to be fast

### Neutral
- TypeScript was not chosen for the MVP phase to reduce onboarding friction,
  but the project structure is compatible with a future migration (`*.jsx → *.tsx`)
- Testing setup (Vitest + React Testing Library) is scaffolded but not enforced
  at PR-level for the MVP phase

---

## References

- [Vite docs](https://vitejs.dev/)
- [Tailwind CSS v3 docs](https://tailwindcss.com/docs)
- [React Router v6 docs](https://reactrouter.com/en/main)
- [React 18 concurrent features](https://react.dev/blog/2022/03/29/react-v18)
