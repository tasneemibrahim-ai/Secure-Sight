# Auth Spec — Login + SignUp

**Spec ID:** 02  
**Status:** Approved  
**Owner:** SecureSight Frontend Team  
**Last Updated:** 2026-03-13  
**Routes:** `/login`, `/signup`  
**Access:** Public (redirects to `/dashboard` if already authenticated)

---

## Overview

This spec covers both authentication routes: **Login** and **SignUp**. Neither connects
to a real backend — authentication is simulated against `mockUsers` in
`src/mock/mockData.js`. The primary goal is to establish the visual identity and the
UX flow so teammates can use these pages as the entry point into the role-based
dashboard system.

---

## User Stories

- As a **returning user**, I want to log in with my email and password so I can access
  my role-specific dashboard.
- As a **new user** (officer, doctor, firefighter), I want to create an account quickly
  so I can request access to the system.
- As a **returning user who is already logged in**, I do not want to see the login screen
  again — I should be redirected automatically to `/dashboard`.
- As any user, I want clear error messages when my credentials are wrong so I know
  what to fix.

---

## Route: `/login` — Login Page

### Layout

**Split layout — two equal halves:**

| Left Panel | Right Panel |
|---|---|
| Animated cyber-eye / surveillance visualization | Login form (glassmorphism card) |
| Full height, dark navy background | Dark background, centered card |
| Decorative — no interactive elements | All form interaction here |

On **tablet and below (≤ 1024px):** the left panel collapses; only the form panel is shown,
full-width, with the particle animation running as the page background.

### Left Panel — Animated Cyber-Eye

**Description:** A purely decorative, looping animation that reinforces the AI
surveillance brand. This should feel like a live feed being analyzed by an AI.

**Requirements:**
- [ ] Central "cyber-eye" graphic — circular, with animated iris scan-line sweeping vertically
- [ ] Concentric rings pulse outward from the eye (radar-like animation)
- [ ] Data-stream text fragments (`0x4A`, `THREAT: NONE`, `CAM-07`, etc.) float and fade
  in the background — CSS or canvas, not SVG sprites
- [ ] System status indicators shown as small floating badges:
  `SYSTEM ONLINE`, `AI MODEL ACTIVE`, `0 ACTIVE THREATS`
- [ ] Color palette: dark navy base + cyan glows — matches design system exactly
- [ ] Animation must be pure CSS or lightweight JS; no heavy canvas libraries

### Right Panel — Login Form

#### FR-L-01 — Form Fields

**Acceptance Criteria:**
- [ ] Email input: `type="email"`, `id="login-email"`, placeholder `"Work email address"`
- [ ] Password input: `type="password"`, `id="login-password"`, placeholder `"Password"`
- [ ] Show/hide password toggle (eye icon button) on password field
- [ ] Both fields use the glassmorphism input style:
  ```
  background: rgba(255,255,255,0.05)
  border: 1px solid rgba(255,255,255,0.1)
  border-radius: 8px
  focus → border-color: #00E5FF, box-shadow: 0 0 0 3px rgba(0,229,255,0.15)
  ```
- [ ] Field labels are visually present (not placeholder-only — placeholders disappear on focus)

#### FR-L-02 — Remember Me + Forgot Password

**Acceptance Criteria:**
- [ ] "Remember me" checkbox — stores email in `localStorage` (mock behavior only)
- [ ] "Forgot password?" link — renders but navigates to `#` (out of scope for MVP)

#### FR-L-03 — Social Login Buttons

**Description:** UI-only social auth buttons. No real OAuth integration.

**Acceptance Criteria:**
- [ ] "Continue with Google" button — Google icon + label, full width
- [ ] "Continue with Microsoft" button — Microsoft icon + label, full width
- [ ] Clicking either button shows a `toast` or `alert`: "Social login coming soon."
- [ ] Divider between social buttons and the email form: `— or —`
- [ ] Buttons styled consistently with the glassmorphism surface style, NOT cyan CTA style

#### FR-L-04 — Form Submission & Mock Auth

**Description:** Validate inputs client-side, then simulate an async auth check.

**Mock Auth Logic:**

```
1. Click "Sign In" button
2. Client-side validate: both fields non-empty, email is valid format
   → If invalid: show inline field error, do NOT proceed
3. Simulate async delay: show loading spinner on button for 1000ms
4. Match email + password against mockUsers array (case-insensitive email)
   a. MATCH FOUND + status === "approved":
      → Store user object in AuthContext
      → Redirect to /dashboard
      → No toast needed (redirect is confirmation enough)
   b. MATCH FOUND + status === "pending":
      → Redirect to /pending-approval (simple informational page)
   c. NO MATCH:
      → Show error message below form: "Invalid email or password."
      → Do NOT specify which field was wrong (security best practice)
      → Shake animation on the card
```

**Acceptance Criteria:**
- [ ] "Sign In" button: `id="login-submit"`, disabled while loading
- [ ] Loading state: spinner replaces button text, button stays same size
- [ ] Error message: `role="alert"` for accessibility, styled in danger red (`#FF4444`)
- [ ] Shake animation: `@keyframes shake` — 3 quick left-right shifts, 400ms total
- [ ] No page reload on form submit — SPA behavior only

#### FR-L-05 — Navigation Links

**Acceptance Criteria:**
- [ ] "Don't have an account? **Sign Up**" link → `/signup`
- [ ] Link positioned below the form card

#### FR-L-06 — Redirect Guard

**Acceptance Criteria:**
- [ ] If user is already authenticated (AuthContext has a user), redirect to `/dashboard`
  before the login page renders

---

## Route: `/signup` — SignUp Page

### Layout

**Centered glassmorphism card** on a full-page animated particle network background.

- Background: animated particle network (floating dots connected by thin lines),
  color palette dark navy + subtle cyan particles
- Card centered both horizontally and vertically on desktop
- Card width: `480px` max on desktop, full width with padding on mobile
- `SecureSight` logo / wordmark at the top of the card

### FR-S-01 — Step Indicator (UI Only)

**Description:** Show a 2-step indicator at the top of the form, but only Step 1 is
implemented. Step 2 is shown as "locked" (admin assigns role later).

**Acceptance Criteria:**
- [ ] Step indicators: `Step 1: Your Details` (active) → `Step 2: Organization` (locked 🔒)
- [ ] Step 2 indicator is grayed-out and non-clickable
- [ ] Small tooltip on Step 2: "Role assigned by admin after approval"

### FR-S-02 — Step 1 Form Fields

**Acceptance Criteria:**
- [ ] **Full Name** input: `id="signup-name"`, `type="text"`, placeholder `"Full name"`, required
- [ ] **Work Email** input: `id="signup-email"`, `type="email"`, placeholder `"Work email address"`, required
  - Validation: must be a valid email format
  - Note: we do NOT require a specific domain filter for the mock
- [ ] **Password** input: `id="signup-password"`, `type="password"`, placeholder `"Create password"`, required
  - Password strength indicator (4-level: Weak / Fair / Good / Strong)
  - Minimum 8 characters; must contain at least one number
- [ ] **Confirm Password** input: `id="signup-confirm-password"`, `type="password"`, placeholder `"Confirm password"`, required
  - Real-time match validation: show "Passwords don't match" inline as user types
- [ ] All inputs use the same glassmorphism style as the login form
- [ ] All inputs have visible floating labels (not just placeholders)

### FR-S-03 — Password Strength Indicator

**Acceptance Criteria:**
- [ ] 4-segment progress bar below the password field
- [ ] Segments fill left-to-right as strength increases:
  - 1 segment filled → `#FF4444` — "Weak"
  - 2 segments → `#FFB020` — "Fair"
  - 3 segments → `#00B8D4` — "Good"
  - 4 segments → `#00E676` — "Strong"
- [ ] Label updates dynamically next to the bar

### FR-S-04 — Terms & Conditions

**Acceptance Criteria:**
- [ ] Checkbox: "I agree to the Terms of Service and Privacy Policy"
  (`id="signup-terms"`, required to enable submit)
- [ ] "Terms of Service" and "Privacy Policy" are links → `#` (out of scope)
- [ ] Submit button is **disabled** until checkbox is checked

### FR-S-05 — Form Submission & Mock API

**Mock Submission Logic:**

```
1. User clicks "Create Account"
2. Client-side validate:
   - All fields non-empty
   - Email valid format
   - Password ≥ 8 chars, contains at least 1 number
   - Passwords match
   - Terms checkbox checked
   → If invalid: show inline errors per field, do NOT submit
3. Simulate async API delay: 1500ms loading state
4. On "success" (always succeeds for mock):
   → Show full-card success animation (checkmark + green glow)
   → After 800ms, redirect to /login with success toast:
     "Account created! Awaiting admin approval before you can log in."
5. Error simulation: If email already exists in mockUsers (case-insensitive):
   → Skip success state
   → Show inline error on email field: "An account with this email already exists."
```

**Acceptance Criteria:**
- [ ] "Create Account" button: `id="signup-submit"`, full width
- [ ] Loading state: spinner + "Creating account…" text
- [ ] Success animation: checkmark SVG scales in (scale 0→1, ease out), card border
  briefly pulses green
- [ ] Success toast on `/login` page persists for 5 seconds then auto-dismisses
- [ ] Duplicate email check runs against `mockUsers` array in `mockData.js`

### FR-S-06 — Navigation Links

**Acceptance Criteria:**
- [ ] "Already have an account? **Sign In**" link → `/login`

### FR-S-07 — Redirect Guard

**Acceptance Criteria:**
- [ ] If user is already authenticated, redirect to `/dashboard` before rendering the signup page

---

## Shared Auth Requirements

### Toast Notification System

A lightweight toast system is needed for both auth routes (and will be reused by
teammates' dashboards). It must be implemented as a **reusable component** in
`src/components/ui/Toast.jsx`.

**Spec:**
- [ ] Toasts appear in the bottom-right corner (desktop) or bottom-center (mobile)
- [ ] Props: `message`, `type` (success | error | info | warning), `duration` (ms, default 4000)
- [ ] Slide-in animation from the right (desktop) / bottom (mobile)
- [ ] Auto-dismiss after `duration` ms, with a dissolve-out animation
- [ ] Manual dismiss via `×` button
- [ ] Multiple toasts stack vertically with a small gap

### AuthContext

A React context (`src/contexts/AuthContext.jsx`) that provides:
```js
{
  user,           // null | mockUser object
  login(user),    // stores user, persists to sessionStorage
  logout(),       // clears user, redirects to /login
  isLoading,      // true during async auth simulation
}
```

- [ ] Context wraps the entire app in `AppRouter.jsx`
- [ ] `user` is rehydrated from `sessionStorage` on page refresh
- [ ] Protected routes redirect to `/login` if `user === null`

---

## Non-Functional Requirements

- **Performance:** Login page (with animation) renders first interactive content in < 1.5s
  on simulated 4G
- **Accessibility:**
  - All form fields have associated `<label>` elements
  - Error messages are announced via `role="alert"`
  - Form submittable via keyboard (Enter key on last field)
  - Focus management: after error, focus moves to the first invalid field
- **Responsiveness:** Fully functional at 320px, 768px, 1024px, 1440px
- **Security (mock):** Passwords are never `console.log`-ged, even in mock mode
- **Animation:** All animations respect `prefers-reduced-motion: reduce`

---

## Out of Scope

- Real OAuth integration with Google or Microsoft
- Password reset / forgot password flow
- Email verification on signup
- Backend API calls — all auth is mock-only
- Step 2 of signup (organization type) — admin assigns role post-approval
- Remember me with real session persistence beyond page reload

---

## Open Questions

- None — spec approved.
