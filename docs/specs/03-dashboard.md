# Dashboard Spec — Role-Based Dashboards

**Spec ID:** 03  
**Status:** Draft  
**Owner:** Teammate Contributors (see table below)  
**Last Updated:** 2026-03-13  
**Routes:** `/dashboard`, `/dashboard/police`, `/dashboard/hospital`,
`/dashboard/firefighters`, `/dashboard/admin`  
**Access:** Authenticated users only — redirects to `/login` if not logged in

---

## Overview

This spec is the **teammate spec file** that covers all four role-based dashboards.
Each dashboard section below is owned by a different contributor. The shared layout
and routing are defined in the Shared Layout section — every contributor **must** use
these shared components and must not modify them.

| Route | Dashboard | Owner |
|---|---|---|
| `/dashboard/police` | Police Alerts Dashboard | Teammate A |
| `/dashboard/hospital` | Hospital Alerts Dashboard | Teammate B |
| `/dashboard/firefighters` | Firefighters Alerts Dashboard | Teammate C |
| `/dashboard/admin` | Admin Management Dashboard | Teammate D |

**The contributor who owns `00-overview.md` / `01-home-page.md` / `02-auth.md` does
NOT implement any page in this file.**

---

## Shared Layout (Mandatory for All Dashboards)

All dashboard routes share a common shell. This shell must be implemented as
`src/components/layout/DashboardLayout.jsx` **before** any teammate starts their page.

> ⚠️ **Do not duplicate the shell.** If your page is wrapped in `<DashboardLayout>`,
> you do not render a sidebar or navbar yourself.

### Shared Layout Requirements

- [ ] Fixed sidebar (left, 240px wide) on desktop; drawer on mobile
- [ ] Sidebar items: logo at top, nav links for the current user's role, logout at bottom
- [ ] Top bar: page title (dynamic), notification bell icon (badge with unread count),
  user avatar + name + role badge
- [ ] Main content area to the right of the sidebar, scrollable
- [ ] Dark navy background (`#0A0F1E`), grid pulse animation behind content area

### Routing Guard

- [ ] All `/dashboard/*` routes are wrapped in a `<ProtectedRoute>` component
  that checks `AuthContext.user`
- [ ] If `user === null`, redirect to `/login`
- [ ] After login, the app redirects to the correct sub-route based on `user.role`:
  - `police` → `/dashboard/police`
  - `hospital` → `/dashboard/hospital`
  - `firefighters` → `/dashboard/firefighters`
  - `admin` → `/dashboard/admin`
  - `null` (pending) → `/pending-approval`

---

## Police Alerts Dashboard — Teammate A

**Route:** `/dashboard/police`  
**Owner:** Teammate A  
**Spec Status:** Draft — `[NEEDS CLARIFICATION]` markers remain

### Overview

The Police dashboard shows real-time crime-related alerts detected by the AI model.
Alert types: **Theft**, **Fighting/Violence**, **Vandalism**, **Suspicious Person**.

### User Stories

- As a **police officer**, I want to see a live list of active alerts sorted by severity
  so I can dispatch to the most critical incident first.
- As a **police officer**, I want to click an alert to see the associated camera feed,
  location, and timestamp.
- As a **police officer**, I want to mark an alert as "Acknowledged" to indicate I am
  responding.

### Functional Requirements

#### FR-PD-01 — Alert Feed

**Acceptance Criteria:**
- [ ] Real-time alert list, newest first, fetched from `mockData.js` (`policeAlerts` array)
- [ ] Each alert card shows: severity badge (Critical / High / Medium / Low),
  threat type, camera ID, detected-at timestamp (relative: "2 min ago"),
  brief AI summary
- [ ] Severity badge colors: Critical → `#FF4444`, High → `#FFB020`, Medium → `#00B8D4`,
  Low → `#94A3B8`
- [ ] New mock alerts are injected every 30 seconds (use `setInterval`) to simulate real-time

#### FR-PD-02 — Alert Detail Modal

**Acceptance Criteria:**
- [ ] Clicking an alert card opens a modal with: expanded AI summary, camera location
  name, confidence score, mock thumbnail placeholder, "Acknowledge" button
- [ ] "Acknowledge" button changes alert status to `acknowledged` and updates the card
  in the feed

#### FR-PD-03 — Stats Bar

**Acceptance Criteria:**
- [ ] Top of page: 4 mini-stat tiles:
  "Active Alerts", "Acknowledged Today", "Avg Response Time", "Cameras Online"
- [ ] Values sourced from `mockData.js` (`policeStats` object)

#### FR-PD-04 — Filter & Search

**Acceptance Criteria:**
- [ ] Filter by alert type (multi-select checkboxes)
- [ ] Filter by severity (radio buttons)
- [ ] Text search by camera ID or location name
- [ ] `[NEEDS CLARIFICATION: Should filters persist across page refresh via URL params?]`

---

## Hospital Alerts Dashboard — Teammate B

**Route:** `/dashboard/hospital`  
**Owner:** Teammate B  
**Spec Status:** Draft

### Overview

The Hospital dashboard shows alerts for **medical emergencies** detected by the AI:
**Injury/Fall Detection**, **Unconscious Person**, **Person Down**, **Medical Emergency**.

### Functional Requirements

#### FR-HD-01 — Emergency Feed

**Acceptance Criteria:**
- [ ] Alert feed, newest first, from `mockData.js` (`hospitalAlerts` array)
- [ ] Each card: medical type icon, injury type label, camera ID, timestamp, triage level
  (Critical → `#FF4444`, Urgent → `#FFB020`, Non-urgent → `#00B8D4`)
- [ ] Mock refresh every 45 seconds

#### FR-HD-02 — Alert Triage Panel

**Acceptance Criteria:**
- [ ] Clicking an alert opens a side-panel (not modal) — 400px, slides in from right
- [ ] Side panel: AI injury description, camera snapshot placeholder, estimated number
  of persons affected, "Dispatch Ambulance" button (mock — toggles status)

#### FR-HD-03 — Stats

**Acceptance Criteria:**
- [ ] Tiles: "Active Emergencies", "Dispatched Units", "Average Scene ETA", "Resolved Today"

---

## Firefighters Alerts Dashboard — Teammate C

**Route:** `/dashboard/firefighters`  
**Owner:** Teammate C  
**Spec Status:** Draft

### Overview

The Firefighters dashboard shows alerts for **fire and hazard events**: **Fire Detected**,
**Smoke Detected**, **Explosion**, **Gas Leak Suspected**.

### Functional Requirements

#### FR-FD-01 — Hazard Feed

**Acceptance Criteria:**
- [ ] Alert feed, from `mockData.js` (`fireAlerts` array), sorted by newest
- [ ] Each card: hazard icon (🔥/💨), hazard type, camera ID, building/location name,
  estimated spread risk (Low / Medium / High / Critical), timestamp
- [ ] Critical + High alerts animate with a subtle pulse/glow on the card border

#### FR-FD-02 — Map View (Optional Stretch)

**Acceptance Criteria:**
- [ ] `[NEEDS CLARIFICATION: Should there be a map view showing camera locations?
  If mocked, use a static SVG building floor plan.]`

#### FR-FD-03 — Stats

**Acceptance Criteria:**
- [ ] Tiles: "Active Fires", "Smoke Alerts", "Units Deployed", "Cameras in Affected Zone"

---

## Admin Dashboard — Teammate D

**Route:** `/dashboard/admin`  
**Owner:** Teammate D  
**Spec Status:** Draft

### Overview

The Admin dashboard is the **control center**. The admin can view all alerts across all
categories and manages subscriber accounts — viewing pending signups and assigning roles.

### Functional Requirements

#### FR-AD-01 — Global Alert Summary

**Acceptance Criteria:**
- [ ] Aggregated stats across all alert types: "Total Active", "Police Alerts",
  "Hospital Alerts", "Fire Alerts"
- [ ] A unified alert feed (all categories, filterable by type)

#### FR-AD-02 — Subscriber Management Table

**Acceptance Criteria:**
- [ ] Table of all users from `mockUsers` in `mockData.js`
- [ ] Columns: Name, Email, Role (dropdown to assign), Status (Pending / Approved),
  Joined date, Actions
- [ ] "Assign Role" dropdown per row: Police / Hospital / Firefighters (sets `role` in mock state)
- [ ] "Approve" button: changes `status` from `pending` to `approved` (mock state only)
- [ ] Status badge: Pending → `#FFB020`, Approved → `#00E676`

#### FR-AD-03 — Role Assignment Flow

**Acceptance Criteria:**
- [ ] Selecting a role from dropdown and clicking "Assign & Approve" updates the user in
  mock state (does not persist to file — this is all in React state)
- [ ] Success toast: "Role assigned to [name]. Account approved."

---

## Shared Mock Data for Dashboards

These exports must exist in `src/mock/mockData.js` for teammates to reference:

```js
export const policeAlerts = [ /* ... */ ];
export const policeStats = { activeAlerts: 4, acknowledgedToday: 12, avgResponseTime: "4m 20s", camerasOnline: 24 };

export const hospitalAlerts = [ /* ... */ ];
export const hospitalStats = { activeEmergencies: 2, dispatchedUnits: 3, avgETA: "6m", resolvedToday: 8 };

export const fireAlerts = [ /* ... */ ];
export const fireStats = { activeFires: 1, smokeAlerts: 3, unitsDeployed: 2, affectedCameras: 5 };
```

---

## Out of Scope (for All Dashboard Pages)

- Real MQTT subscription or WebSocket connection
- Actual map integration (Leaflet, Google Maps, etc.)
- PDF report export
- Push notifications / browser notification API
- Multi-language / i18n support

---

## Open Questions

- `[NEEDS CLARIFICATION: Teammate A — should filters in police dashboard persist via URL params?]`
- `[NEEDS CLARIFICATION: Teammate C — is a floor-plan map view in scope for the MVP?]`
- `[NEEDS CLARIFICATION: Teammate D — should the admin be able to revoke an already-assigned role?]`
