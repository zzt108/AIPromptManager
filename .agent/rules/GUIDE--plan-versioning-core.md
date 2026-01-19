---
trigger: model_decision
---

# GUIDE - Plan and Phase Implementation Versioning - CORE (v1.8)

**Version:** 1.8  
**Date:** 2026-01-11  
**Status:** Active  
**Fragment:** CORE - Overview, Terminology, Phase Hierarchy

---

## Overview

This guide establishes the hierarchical versioning system for AI-assisted development plans and their integration with application versioning in VecTool and related projects.

### Critical Terminology

The following terms are equivalent and used interchangeably in this document and across the development workflow:
- **Plan** / **Feature** / **Feat** (used in git branch naming: `feature`)
- **Bug Plan** / **Bug** / **Bugfix** (used in git branch naming: `bug`)

All references to Plan in this document apply to both feature development plans and bug fix plans unless explicitly differentiated.

### Language Standard

**CRITICAL REQUIREMENT:** All plan documents, phase descriptions, commit messages, and technical documentation **MUST** be written in English only. This ensures:
- Consistency across all projects and teams
- Universal accessibility for code reviews and CI/CD automation
- Compatibility with international development standards
- Proper parsing by automated tools and dashboards

*Note: While user interfaces may support multiple languages, all planning and development artifacts remain in English.*

---

## Phase Progress Visibility Standard

**Requirement:** Every plan document **MUST** include a standardized header that immediately shows plan hierarchy and current progress status.

### Header Format

```
🚀 [Plan Title] - Plan Version [X-YZ] - Phase [A/B]
| Plan Version | [Current Phase Version] |
| Parent Plan | [Parent Plan ID] |
| App Version | Target App Version |
| Status | [Current Status with Emoji] |
```

### Status Emoji Legend

| Status | Emoji | Description |
|--------|-------|-------------|
| Planning | 📋 | Initial phase, requirements gathering |
| In Progress | 🔄 | Active development work |
| Testing | 🧪 | Implementation complete, testing phase |
| Blocked | 🚫 | Waiting on dependency or external factor |
| Review | 👀 | Code review or validation in progress |
| Complete | ✅ | Phase fully implemented and validated |
| Deprecated | ❌ | Plan superseded or cancelled |

---

## Plan Versioning Pattern

### Plan ID Format (2-Digit Specification)

Plan IDs are **always 2-digit numbers** (01-99) to allow for future sub-plan definitions. This standardization enables:
- Clear hierarchical structure for sub-plans (e.g., 01-a, 01-b)
- Consistent sorting and parsing in automated systems
- Room for 99 plans per major version
- Prevention of ambiguity in version strings

### Feature Plan Versioning

**Format:** `PROJECT-Major-PlanId-PhaseId`

**Components:**
- **PROJECT** — Project identifier (e.g., VECTOOL, SFERA, QATOOLS, LINX, AIPM)
- **Major** — Application major version number (e.g., 4 for VecTool 4.x)
- **PlanId** — 2-digit sequential plan number within the major version (01-99)
- **PhaseId** — Sequential phase number within the plan (01, 02, 03, etc.)

**Examples:**
- `VECTOOL-4-01` — First plan in VecTool 4.x (parent plan)
- `VECTOOL-4-01-01` — Phase 1 of Plan 01
- `VECTOOL-4-01-02` — Phase 2 of Plan 01
- `VECTOOL-4-02` — Second plan in VecTool 4.x
- `AIPM-1-01` — First plan in AiPrompts Manager 1.x

### Bug Plan Versioning - Context-Aware (Bugs Discovered During Plan Execution)

**Format:** `PROJECT-Major-PlanId-PhaseId bBugId-BugPhaseId`

**Components:**
- **Parent context** — Full phase path where bug was discovered
- **BugId** — Globally unique bug counter (never resets, increments project-wide)
- **BugPhaseId** — Phase within the bug fix plan (optional, only if bug plan has phases)

**Examples:**
- `VECTOOL-4-01-03 b1` — First bug ever, discovered during Plan 01, Phase 3
- `VECTOOL-4-01-03 b1-01` — Phase 1 of bug fix b1
- `VECTOOL-4-01-03 b1-02` — Phase 2 of bug fix b1
- `VECTOOL-4-01-05 b2` — Second bug discovered during Plan 01, Phase 5

### Bug Plan Versioning - Standalone (Not Tied to Active Plans)

**Format:** `PROJECT-bBugId-BugPhaseId`

**Used for bugs discovered through:**
- Manual testing (not during plan execution)
- Production user reports
- Code reviews
- External quality audits

**Examples:**
- `VECTOOL-b3` — Third bug overall (continues global sequence), standalone parent plan
- `VECTOOL-b3-01` — Phase 1 of standalone bug fix
- `VECTOOL-b3-02` — Phase 2 of standalone bug fix
- `VECTOOL-4-02-01 b4` — Fourth bug, discovered during Plan 02, Phase 1

**Critical Rule:** Bug IDs are globally unique per project and never reset. The counter continues across all plans and standalone bugs.

### Test Case Investigation Plans

**Format:** `PROJECT-Major-TCID-PhaseId`

**Components:**
- **TCID** — External test case identifier (e.g., TC9768)
- **PhaseId** — Investigation phase number

**Examples:**
- `SFERA-3-TC9768` — Investigation plan for test case 9768 (parent)
- `SFERA-3-TC9768-01` — Phase 1 of investigation
- `SFERA-3-TC9768-02` — Phase 2 of investigation

*Note: If multiple separate investigations are needed for the same test case, increment the TC number or append a suffix (TC9768-A, TC9768-B)*

---

## Phase Hierarchy and Numbering

### Parent Plans

Parent plans represent the top-level work item:
- **Format:** `Major-PlanId` (e.g., 4-01, 4-02)
- Contain high-level objectives, success criteria, and phase breakdown
- Never have implementation details — only strategic overview

### Child Phases

Child phases are executable work units:
- **Format:** `Major-PlanId-PhaseId` (e.g., 4-01-01, 4-01-02)
- Contain specific tasks, code changes, and deliverables
- Must have clear success criteria and completion indicators

### Numbering Rules

| Rule | Correct | Incorrect | Note |
|------|---------|-----------|------|
| Sequential numbering starts at 1 | 4-01-01, 4-01-02, 4-01-03 | 4-01-00 | Don't use -00 for phases |
| No gaps | 4-01-01, 4-01-02, 4-01-03 | 4-01-01, 4-01-03 | Skipped 4-01-02 |
| No reuse | Each phase numbered once | 4-01-01, 4-01-01 (again) | Invalid duplicate |
| Parent versions end at PlanId | 4-01 is parent | 4-01-01 is parent | Clear hierarchy required |

---

## Gap Analysis

**Requirement:** Gap analysis is required when:
1. Phase completion — Compare implemented vs. planned features
2. Bug discovery — Assess impact on parent plan timeline
3. Blocked status — Identify missing prerequisites
4. Major milestone — Before releasing to production

### Gap Analysis Template

**Plan Version:** [Version]  
**Date:** [Date]

#### Implemented Features
- ✅ Feature A
- ✅ Feature B (with notes on deviations)
- ⚠️ Feature C (partial — missing validation)

#### Planned Features
- ⏳ Feature D (not started)
- 🚫 Feature E (blocked by external dependency)

#### Gaps Identified
1. **Feature B validation** — Missing edge case tests
2. **Feature C** — Blocked by external API dependency
3. **Performance** — Load testing not completed

#### Next Actions
1. Complete Feature B validation tests — *Priority: High*
2. Follow up with API team for Feature C unblocking — *Priority: High*
3. Schedule load testing session — *Priority: Medium*

---

## Related Guides

- See **[GUIDE--Plan-Phase-Versioning--BRANCHING.md](GUIDE--Plan-Phase-Versioning--BRANCHING.md)** for Git branch naming conventions
- See **[GUIDE--Plan-Phase-Versioning--NAMING.md](GUIDE--Plan-Phase-Versioning--NAMING.md)** for file naming standards
- See **[GUIDE--Plan-Phase-Versioning--EXAMPLES.md](GUIDE--Plan-Phase-Versioning--EXAMPLES.md)** for migration guides and examples

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.8 | 2026-01-11 | Split into focused fragments: CORE, BRANCHING, NAMING, EXAMPLES | User |

---

**Fragment Status:** This is the CORE fragment covering versioning fundamentals and phase hierarchy.
