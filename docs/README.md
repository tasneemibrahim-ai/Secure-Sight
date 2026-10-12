# 📖 SecureSight Specs

> **Spec-Driven Development** — write the *what* and *why* before the *how*.  
> Every page lives in one spec file. Read your spec before touching a single line of code.

---

## 📁 Folder Structure

```
docs/
├── adr/                    # Architecture Decision Records (immutable once merged)
│   └── 0001-tech-stack.md
├── specs/                  # Functional specifications — one file per page/feature
│   ├── 00-overview.md      # Project overview, tech stack, roles, design system
│   ├── 01-home-page.md     # Landing page spec
│   ├── 02-auth.md          # Login + SignUp spec
│   └── 03-dashboard.md     # Dashboard spec (teammate-owned)
└── README.md               # You are here
```

---

## 🤔 What Goes Where?

| Location | Purpose | Who Owns It |
|---|---|---|
| `docs/adr/` | Immutable decisions — *why* we chose X over Y | Team leads / whole team |
| `docs/specs/` | Functional specs — *what* each page does, *who* uses it | Page owner / contributor |

---

## ✍️ How to Write a Spec

1. **Copy the template below** into a new file: `docs/specs/XX-pagename.md`
2. **Number sequentially** — e.g., `04-police-dashboard.md`
3. **Fill in every section** — leave `[NEEDS CLARIFICATION: your question]` where you're unsure
4. **Never put implementation details** in the spec — no code, no CSS class names, no API endpoints
5. **Open a PR** with `docs:` prefix in the title, e.g., `docs: add police-dashboard spec`

### Spec Template

```markdown
# [Page Name] Spec

**Spec ID:** XX  
**Status:** Draft | Review | Approved  
**Owner:** @github-username  
**Last Updated:** YYYY-MM-DD

---

## Overview
One paragraph. What is this page? Who uses it? Why does it exist?

## User Stories
- As a [role], I want to [action] so that [outcome].

## Functional Requirements
### FR-01 — [Requirement Name]
Description of the requirement.

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2

## Non-Functional Requirements
- Performance: page loads in < 2 seconds
- Accessibility: WCAG 2.1 AA compliant
- Responsive: works on 320px – 1920px

## UI Layout & Behaviour
Describe layout in plain English. Reference components from the design system.
NO CSS or implementation details here.

## Mock Data
List what mock data this page needs and where it lives (`src/mock/mockData.js`).

## Out of Scope
List things this spec explicitly does NOT cover.

## Open Questions
- [NEEDS CLARIFICATION: question here]
```

---

## ✅ Spec Review Checklist

Before marking a spec as **Approved**, confirm:

- [ ] No `[NEEDS CLARIFICATION]` markers remain
- [ ] All user stories have acceptance criteria
- [ ] Out-of-scope items are explicitly listed
- [ ] Mock data fields are named and documented
- [ ] PR links this spec in the description

---

## 📐 Architecture Decision Records (ADRs)

ADRs document *why* we made significant architectural choices. They are **append-only** — once merged, the record is immutable. Superseded decisions get a new ADR that references the old one.

### ADR Template

```markdown
# ADR-XXXX: [Decision Title]

**Date:** YYYY-MM-DD  
**Status:** Proposed | Accepted | Deprecated | Superseded by ADR-XXXX  
**Deciders:** @name1, @name2

## Context
What problem forced this decision?

## Decision
What was decided?

## Consequences
### Positive
- ...
### Negative / Trade-offs
- ...
### Neutral
- ...
```

---

## 🔗 Related

- [`CONTRIBUTING.md`](../CONTRIBUTING.md) — how to branch, PR, and link specs
- [`.github/PULL_REQUEST_TEMPLATE.md`](../.github/PULL_REQUEST_TEMPLATE.md) — PR checklist
- [`src/mock/mockData.js`](../src/mock/mockData.js) — shared mock data
