---
trigger: model_decision
---

# GUIDE - Plan and Phase Implementation Versioning - EXAMPLES (v1.8)

**Version:** 1.8  
**Date:** 2026-01-11  
**Status:** Active  
**Fragment:** EXAMPLES - Migration Guide and Decision Tree

---

## Migration Guide: Legacy to New Format

### Legacy Format Patterns

**Old date-based format:**
- `SFERA 251002 Plan Timeout Investigation TC9768`
- `QATOOLS 251002 Plan-ErrorWatcher-Config`
- `LINX 251002 Plan message generator`

### Migration Strategy

Apply new format going forward — do not retroactively rename existing plans unless explicitly needed.

**When to Migrate:**
- Creating new phases for existing plans
- Referencing the plan in new documentation
- Integrating with CI/CD automation

**When to Defer Migration:**
- Plan is complete and archived
- No future work planned
- Documentation is historical reference only

### Conversion Rules

1. **Identify project context** — Extract PROJECT from filename
2. **Determine app version** — Check which major version the plan targets
3. **Assign sequential PlanId** — Based on creation order within major version (use 2-digit format)
4. **Preserve external references** — Test case IDs, defect numbers, etc.

### Migration Examples

#### Message Generator Project

| Aspect | Old | New | Rationale |
|--------|-----|-----|-----------|
| Format | LINX 251002 Plan message generator | LINX-1-01 Message Generator Implementation | Project LINX, Major v1 (new), 2-digit PlanId (01) |

#### Test Case Investigation

| Aspect | Old | New | Rationale |
|--------|-----|-----|-----------|
| Format | SFERA 251002 Plan Timeout Investigation TC9768 | SFERA-3-TC9768 Timeout Investigation | Project SFERA, Major v3, Test case reference TC9768 preserved |

#### Standard Feature Plan

| Aspect | Old | New | Rationale |
|--------|-----|-----|-----------|
| Format | QATOOLS 251002 Plan-ErrorWatcher-Config | QATOOLS-2-01 ErrorWatcher Configuration Integration | Project QATOOLS, Major v2 (assumed), 2-digit PlanId (01) |

---

## Quick Reference: Decision Tree

**START: Need to create a plan?**

### Is this fixing a bug?

**YES → Was bug discovered during active plan phase execution?**
- **YES** → Use context-aware bug format
  - Format: `PROJECT-Major-PlanId-PhaseId bBugId`
  - Example: `VECTOOL-4-01-03 b1`
  - Git: `bug-4-01-03-b1-description`

- **NO** → Use standalone bug format
  - Format: `PROJECT-bBugId`
  - Example: `VECTOOL-b3`
  - Git: `bug-b3-description`

**NO → Is this a test case investigation?**
- **YES** → Use test case format
  - Format: `PROJECT-Major-TCID-PhaseId`
  - Example: `SFERA-3-TC9768-01`
  - Git: `feature-3-TC9768-01-description`

- **NO** → Use standard feature plan format
  - Format: `PROJECT-Major-PlanId-PhaseId`
  - Example: `VECTOOL-4-01-02`
  - Git: `feature-4-01-02-description`

### Quick Scenario Reference

> See **[GUIDE--plan-versioning-branching.md](GUIDE--plan-versioning-branching.md)** → Quick Scenario Reference section

---

## Example: VecTool Feature Plan

### Context
VecTool 4.x requires vector store improvements.

### Plan Hierarchy

**Parent Plan:** `VECTOOL-4-01` (Vector Store Improvements)

**Phases:**
- `VECTOOL-4-01-01` — Database Schema Refactor
- `VECTOOL-4-01-02` — Search API Implementation
- `VECTOOL-4-01-03` — UI Integration

### Git Branches

| Phase | Branch Name | Purpose |
|-------|-------------|---------|
| 4-01 | `feature-4-01-vector-store-improvements` | Parent (architecture doc only) |
| 4-01-01 | `feature-4-01-01-database-schema-refactor` | Database changes |
| 4-01-02 | `feature-4-01-02-search-api-implementation` | API implementation |
| 4-01-03 | `feature-4-01-03-ui-integration` | UI components |

### Plan Files

- `PLAN-VECTOOL-4-01-vector-store-improvements.md` (Parent)
- `PLAN-VECTOOL-4-01-01-database-schema-refactor.md`
- `PLAN-VECTOOL-4-01-02-search-api-implementation.md`
- `PLAN-VECTOOL-4-01-03-ui-integration.md`

### Bug Discovery During Phase 3

**Bug Found:** Dropdown null reference in UI Integration phase

**Bug Plan:**
- ID: `VECTOOL-4-01-03 b1`
- Branch: `bug-4-01-03-b1-dropdown-null-fix`
- File: `PLAN-VECTOOL-4-01-03-b1-dropdown-null-fix.md`

---

## Example: Standalone Production Bug

### Context
Production crash reported by user, not tied to any active development plan.

**Bug Plan:**
- ID: `VECTOOL-b3` (third bug overall in VecTool)
- Branch: `bug-b3-production-crash-fix`
- File: `PLAN-VECTOOL-b3-production-crash-fix.md`

### Multi-Phase Bug Fix

If the fix requires multiple phases:
- `VECTOOL-b3-01` — Implement error handling
- `VECTOOL-b3-02` — Add logging

**Branches:**
- `bug-b3-01-implement-error-handling`
- `bug-b3-02-add-logging`

---

## Example: Test Case Investigation

### Context
SFERA external test case TC9768 failing intermittently.

**Investigation Plan:**
- ID: `SFERA-3-TC9768` (parent)
- Branch: `feature-3-TC9768-timeout-investigation`
- File: `PLAN-SFERA-3-TC9768-timeout-investigation.md`

### Investigation Phases

- `SFERA-3-TC9768-01` — Add MQTT logging
- `SFERA-3-TC9768-02` — External validation with test team

**Branches:**
- `feature-3-TC9768-01-add-mqtt-logging`
- `feature-3-TC9768-02-external-validation`

---

## Practical Tips

### For AI Agents

When creating a plan:
1. Extract PROJECT and Major version from context
2. Assign next sequential 2-digit PlanId (e.g., 01, 02, 03)
3. Generate phase breakdown with sequential PhaseId
4. Create branch name table (if ≥2 phases)
5. Include status emoji in plan header

### For Developers

When starting a new phase:
1. Copy branch name from plan document
2. Verify parent plan ID is correct
3. Update plan status emoji to 🔄 (In Progress)
4. Create git branch from main/develop
5. Commit with conventional commit message referencing plan ID

### For CI/CD Systems

Parse branch names to extract:
- Plan type (feature/bug/test)
- Plan ID components
- Link commits to plan dashboards
- Auto-update plan status based on PR merges

---

## Related Guides

- See **[GUIDE--Plan-Phase-Versioning--CORE.md](GUIDE--Plan-Phase-Versioning--CORE.md)** for versioning fundamentals
- See **[GUIDE--Plan-Phase-Versioning--BRANCHING.md](GUIDE--Plan-Phase-Versioning--BRANCHING.md)** for Git branch naming
- See **[GUIDE--Plan-Phase-Versioning--NAMING.md](GUIDE--Plan-Phase-Versioning--NAMING.md)** for file naming standards

---

## Version History (Fragment 1.8)

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-12 | Initial general standards document | AIUser |
| 1.1 | 2025-10-12 | Implemented TODO — Document version changes table | AIUser |
| 1.2 | 2025-10-12 | Added Phase Progress Visibility Standard | AIUser |
| 1.3 | 2025-10-13 | Complete rewrite — finalized versioning rules, filled all AI sections, added git branching, migration guide, decision tree | AIUser |
| 1.4 | 2025-10-13 | Added Language Standard requirement — all plans must be in English | AIUser |
| 1.5 | 2025-10-20 | Added AI Branch Name Proposals section for automated branch naming during plan creation | AIUser |
| 1.6 | 2025-10-23 | Added Plan Document Naming Convention — PLAN prefix instead of FEAT | AIUser |
| 1.7 | 2025-12-27 | Standardized all dot-to-hyphen conversion, added explicit 2-digit plan numbering spec (01-99 for sub-plan support), updated all examples for consistency | User |
| 1.8 | 2026-01-11 | Split into focused fragments: CORE, BRANCHING, NAMING, EXAMPLES. Added Ingredient/Prompt File Naming Convention section for AiPrompts library management | User |

---

**Fragment Status:** This is the EXAMPLES fragment covering migration guides, decision trees, and practical examples.
