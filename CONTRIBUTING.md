# Contributing to SecureSight

Welcome to the SecureSight frontend project! 👋

SecureSight uses **Spec-Driven Development** — every page is fully specified *before*
any code is written. This means your first job as a contributor is to **read the spec**
for the page you're building, not to open your editor.

This guide explains the complete contribution workflow.

---

## 📋 Table of Contents

- [Before You Write a Single Line of Code](#before-you-write-a-single-line-of-code)
- [Tech Stack Quick Reference](#tech-stack-quick-reference)
- [Reading the Specs](#reading-the-specs)
- [Creating a New Spec](#creating-a-new-spec-for-your-dashboard-page)
- [Branch Naming](#branch-naming)
- [Development Workflow](#development-workflow)
- [Design System Rules](#design-system-rules)
- [Mock Data Rules](#mock-data-rules)
- [Pull Request Process](#pull-request-process)
- [Code Review Standards](#code-review-standards)

---

## Before You Write a Single Line of Code

> 🛑 **Hard rule:** No implementation without an approved spec.

The workflow is always:

```
1. Read docs/specs/00-overview.md          ← Project context + design system
2. Read the spec for your assigned page    ← e.g., docs/specs/03-dashboard.md
3. Clarify any NEEDS CLARIFICATION items   ← Open a discussion in the PR or Discord
4. Get spec section approved               ← Lead marks it "Approved" in the Status field
5. Create your feature branch              ← see Branch Naming below
6. Code, PR, iterate
```

---

## Tech Stack Quick Reference

| Technology | Version | Docs |
|---|---|---|
| React | 18.x | [react.dev](https://react.dev) |
| Vite | ^5.x | [vitejs.dev](https://vitejs.dev) |
| Tailwind CSS | ^3.x | [tailwindcss.com/docs](https://tailwindcss.com/docs) |
| React Router | v6 | [reactrouter.com](https://reactrouter.com/en/main) |

> **Why this stack?** See [`docs/adr/0001-tech-stack.md`](docs/adr/0001-tech-stack.md).

### Local Setup

```bash
# Install dependencies
npm install

# Start dev server (http://localhost:5173)
npm run dev

# Run linter
npm run lint

# Build for production (only if asked)
npm run build
```

---

## Reading the Specs

All specs live in `docs/specs/`. Start here:

| File | Contents |
|---|---|
| [`docs/specs/00-overview.md`](docs/specs/00-overview.md) | Project overview, design system, mock data, folder structure |
| [`docs/specs/01-home-page.md`](docs/specs/01-home-page.md) | Landing page spec |
| [`docs/specs/02-auth.md`](docs/specs/02-auth.md) | Login + SignUp pages |
| [`docs/specs/03-dashboard.md`](docs/specs/03-dashboard.md) | All role-based dashboards |

### Spec Status Meanings

| Status | Meaning |
|---|---|
| **Draft** | Being written — do NOT implement yet |
| **Review** | Under discussion — may still change |
| **Approved** | Frozen — safe to implement |

> If a section you need is still in **Draft**, ping the spec owner before starting.

### `[NEEDS CLARIFICATION]` Markers

If you see `[NEEDS CLARIFICATION: some question]` in a spec, the spec is **not yet
approved** for that section. Do not implement that section until it is resolved.

To resolve one:
1. Open a GitHub Discussion or comment on the spec PR
2. Tag the spec owner and the project lead
3. Once agreed, the spec owner removes the marker and updates Status to Approved

---

## Creating a New Spec for Your Dashboard Page

If you are adding a **new page** that doesn't have a spec entry yet, you must write the
spec first. Follow these steps:

### 1. Create a New Spec File

```bash
# Name format: NN-pagename.md — use the next available number
# Example:
touch docs/specs/04-police-dashboard.md
```

### 2. Use the Spec Template

Copy the template from [`docs/README.md`](docs/README.md#-how-to-write-a-spec)
into your new file.

Fill in every section. Mark anything uncertain as:
```
[NEEDS CLARIFICATION: your specific question here]
```

### 3. Open a `docs:` PR

```bash
git checkout -b docs/police-dashboard-spec
git add docs/specs/04-police-dashboard.md
git commit -m "docs: add police-dashboard spec"
git push origin docs/police-dashboard-spec
```

Open a PR with the `docs:` prefix. The spec must be approved **before** you open an
implementation PR.

### 4. Get It Approved

A teammate or the project lead reviews the spec. Once approved, their approval comment
is sufficient — update the **Status** field to `Approved` in the file.

---

## Branch Naming

Use this naming convention — **no exceptions**:

| Type | Pattern | Example |
|---|---|---|
| Feature / page implementation | `feature/[page-name]` | `feature/police-dashboard` |
| Spec / documentation only | `docs/[description]` | `docs/hospital-dashboard-spec` |
| Bug fix | `fix/[short-description]` | `fix/login-redirect-loop` |
| Design system update | `design/[component]` | `design/toast-component` |
| Refactor | `refactor/[area]` | `refactor/auth-context` |

### Examples

```bash
# Starting work on the police dashboard
git checkout -b feature/police-dashboard

# Adding a spec doc only
git checkout -b docs/firefighters-dashboard-spec

# Fixing a bug in the login shake animation
git checkout -b fix/login-shake-animation
```

> Never push directly to `main`. Always branch and PR.

---

## Development Workflow

### 1. Pull the Latest `main`

```bash
git checkout main
git pull origin main
```

### 2. Create Your Branch

```bash
git checkout -b feature/your-page-name
```

### 3. Work in Your Page's Scope

As a dashboard contributor, your scope is:
- `src/pages/dashboard/YourDashboard.jsx` (your file — own it)
- `src/mock/mockData.js` (add your mock data entries at the bottom — DO NOT modify
  entries added by others)

**Never modify:**
- `src/router/AppRouter.jsx` (ask the router owner to add your route)
- `src/contexts/AuthContext.jsx` (shared — discuss before touching)
- `src/components/layout/DashboardLayout.jsx` (shared shell — coordinate changes)
- Any other contributor's page file

### 4. Commit Often, With Meaningful Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add alert feed component to police dashboard
fix: correct severity badge color for Medium alerts
docs: update 03-dashboard spec with approved police section
style: apply glassmorphism to hospital alert cards
refactor: extract AlertCard into shared component
```

### 5. Self-Review Before PR

Run through the checklist in `PULL_REQUEST_TEMPLATE.md` yourself before opening your PR.

---

## Design System Rules

The design system is defined in [`docs/specs/00-overview.md`](docs/specs/00-overview.md#-design-system).

### Mandatory Rules

- ✅ **Background color:** `#0A0F1E` — always
- ✅ **Primary accent:** `#00E5FF` (cyan) — CTAs, active borders, highlights
- ✅ **Cards:** use the glassmorphism pattern exactly as specified
- ✅ **Font:** Inter — loaded via Google Fonts in `index.html`
- ✅ **Tailwind config** is the source of truth for color tokens — use the design tokens,
  not raw hex values inline (e.g., use `text-accent-cyan`, not `text-[#00E5FF]`)

### Forbidden

- ❌ Do not use `!important` anywhere
- ❌ Do not add third-party UI component libraries (MUI, Chakra, shadcn, etc.) without
  team agreement and an ADR
- ❌ Do not hardcode colors or spacing values inline if a Tailwind token exists
- ❌ Do not write styles in `.module.css` files — Tailwind utilities only (with rare
  exceptions for complex animations in `globals.css`)

---

## Mock Data Rules

All mock data lives exclusively in **`src/mock/mockData.js`**.

- ✅ Import mock data into your component — never define mock arrays inside component files
- ✅ Add new mock exports at the **bottom** of `mockData.js` with a comment:
  ```js
  // --- Police Dashboard Mock Data ---
  export const policeAlerts = [ ... ];
  ```
- ❌ Do not modify exports that belong to other contributors' pages
- ❌ Do not hardcode mock arrays inside JSX files

---

## Pull Request Process

### 1. PR Title Format

```
feat: implement [page name] (spec: docs/specs/NN-pagename.md)

Examples:
feat: implement police dashboard (spec: docs/specs/03-dashboard.md)
fix: login error toast not appearing on wrong password
docs: approve firefighters dashboard spec
```

### 2. Link the Spec in the PR Body

Your PR description **must** link to the spec it implements. Use the
`.github/PULL_REQUEST_TEMPLATE.md` (it will auto-populate).

### 3. Required Checks Before Requesting Review

- [ ] All acceptance criteria in your spec section are implemented
- [ ] No `console.log` or `debugger` statements left in code
- [ ] No TypeErrors on app startup (`npm run dev` shows no errors in console)
- [ ] Responsive — manually checked at 375px and 1440px
- [ ] `npm run lint` passes with 0 errors

### 4. Screenshots Required

Add desktop + mobile screenshots to your PR. See the PR template for the table format.

### 5. Getting Merged

- At least **1 approving review** from a teammate (not yourself)
- All automated checks must pass (if CI is set up)
- No unresolved review comments

---

## Code Review Standards

When reviewing a teammate's PR:

1. **Check the spec first** — does the implementation match the spec?
2. **Design system compliance** — does it use the correct colors, glassmorphism, fonts?
3. **Mock data** — does the PR import from `mockData.js` (not hardcode data)?
4. **Accessibility** — labels on inputs, `aria-label` on icon buttons, focus management?
5. **Responsiveness** — does it roughly work at 375px?
6. **No interference** — does the PR modify code outside the contributor's assigned scope?

Be constructive and specific. Point to the spec if a requirement is missed.

---

## Need Help?

- Open a GitHub Discussion for questions about the spec
- Tag `@project-lead` for design system questions
- For bugs in shared components, open an issue with the `shared-component` label

Happy building! 🛡️
