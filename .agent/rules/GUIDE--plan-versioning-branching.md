---
trigger: model_decision
---

# GUIDE - Plan and Phase Implementation Versioning - BRANCHING (v1.8)

**Version:** 1.8  
**Date:** 2026-01-11  
**Status:** Active  
**Fragment:** BRANCHING - Git Branch and Commit Naming

---

## Git Branch Naming Convention

### Core Rules

1. No project prefix in branch names (project context is in repository)
2. Use `plan`/`feature`/`bug` terminology consistently
3. Include full phase version for traceability
4. Kebab-case for descriptions

### Feature Plan Branches

**Format:** `feature-Major-PlanId-PhaseId-short-description`

**Examples:**
- `feature-4-01-vector-store-improvements`
- `feature-4-01-01-database-schema-refactor`
- `feature-4-01-02-add-search-filters`
- `feature-4-02-authentication-system`

### Bug Fix Branches - Context-Aware

**Format:** `bug-Major-PlanId-PhaseId-bBugId-BugPhaseId-short-description`

**Examples:**
- `bug-4-01-03-b1-dropdown-null-fix`
- `bug-4-01-03-b1-01-add-null-checks`
- `bug-4-01-03-b1-02-update-unit-tests`
- `bug-4-01-05-b2-memory-leak-patch`

### Bug Fix Branches - Standalone

**Format:** `bug-bBugId-BugPhaseId-short-description`

**Examples:**
- `bug-b3-production-crash-fix`
- `bug-b3-01-implement-error-handling`
- `bug-b3-02-add-logging`
- `bug-b4-ui-alignment-issue`

### Test Case Investigation Branches

**Format:** `feature-Major-TCID-PhaseId-short-description`

**Examples:**
- `feature-3-TC9768-timeout-investigation`
- `feature-3-TC9768-01-add-mqtt-logging`
- `feature-3-TC9768-02-external-validation`

### Kebab-Case Rules

- All lowercase
- Separate words with hyphens
- No special characters except hyphens
- No spaces or underscores

| Correct | Incorrect | Issue |
|---------|-----------|-------|
| `feature-4-01-02-add-search-filters` | `feature-4-01-02-AddSearchFilters` | Mixed case, underscore |
| `bug-b3-01-implement-error-handling` | `bug-b3-01-ImplementErrorHandling` | PascalCase |
| `feature-3-TC9768-01-diagnostic-logging` | `feature-3-TC9768-01-diagnostic logging` | Space |

---

## AI Branch Name Proposals for Plan Execution

### Integration with Plan Creation Workflow

**Step-by-step AI workflow:**
1. User requests plan creation
2. AI analyzes requirements and creates phase breakdown
3. AI automatically generates branch name table (if ≥2 phases)
4. AI presents complete plan document with proposals
5. User reviews and approves/modifies branch names
6. Proceed with implementation

**User Experience Benefit:** User can immediately copy-paste branch names when starting work on each phase.

### When NOT to Propose Branches

Skip branch proposals when:
- Plan has only 1 phase (branch name is self-evident)
- Plan is retrospective documentation (already completed)
- User explicitly requests no branch names
- Plan is a high-level strategic document (no implementation phases)

---

## CICD Dashboard Integration

### Automatic Plan Parsing

CI/CD pipelines and dashboards should parse commit messages and branch names to extract plan metadata.

### Regex Patterns for Parsing

#### Feature Plan Pattern

```
feature-?major-?planId?-?phaseId??-?description.*
```

**Captures:**
- `major` — Application major version
- `planId` — Plan identifier
- `phaseId` — Phase identifier (optional)
- `description` — Human-readable description

**Examples:**
- `feature-4-01-vector-store` → major=4, planId=01, phaseId=null
- `feature-4-01-02-add-filters` → major=4, planId=01, phaseId=02

#### Bug Pattern - Context-Aware

```
bug-?major-?planId-?discoveryPhase-b?bugId?-?bugPhase??-?description.*
```

**Captures:**
- `major` — Application major version
- `planId` — Parent plan ID
- `discoveryPhase` — Phase where bug was found
- `bugId` — Global bug identifier
- `bugPhase` — Bug fix phase (optional)
- `description` — Human-readable description

**Examples:**
- `bug-4-01-03-b1-dropdown-fix` → major=4, planId=01, discoveryPhase=03, bugId=1
- `bug-4-01-03-b1-02-unit-tests` → major=4, planId=01, discoveryPhase=03, bugId=1, bugPhase=02

#### Bug Pattern - Standalone

```
bug-b?bugId?-?bugPhase??-?description.*
```

**Captures:**
- `bugId` — Global bug identifier
- `bugPhase` — Bug fix phase (optional)
- `description` — Human-readable description

**Examples:**
- `bug-b3-production-crash` → bugId=3, bugPhase=null
- `bug-b3-02-add-logging` → bugId=3, bugPhase=02

#### Test Case Pattern

```
feature-?major-?testCaseId(TC.*?)-?phaseId??-?description.*
```

**Captures:**
- `major` — Application major version
- `testCaseId` — Test case identifier (e.g., TC9768)
- `phaseId` — Investigation phase (optional)
- `description` — Human-readable description

**Examples:**
- `feature-3-TC9768-timeout-investigation` → major=3, testCaseId=TC9768
- `feature-3-TC9768-02-external-validation` → major=3, testCaseId=TC9768, phaseId=02

### Dashboard Display Format

**Recommended columns:**
- Plan ID (Full version string, e.g., 4-01-03 b1)
- Type (Feature / Bug / Test Case)
- Status (Current phase status with emoji)
- Parent (Parent plan reference)
- Branch (Git branch name)
- Last Commit (Timestamp of latest activity)

| Plan ID | Type | Status | Parent | Branch | Last Commit |
|---------|------|--------|--------|--------|-------------|
| 4-01-03 | Feature | 🔄 In Progress | 4-01 | feature-4-01-03-add-filters | 2025-12-27 14:30 |
| 4-01-03 b1 | Bug | 🧪 Testing | 4-01 | bug-4-01-03-b1-dropdown-fix | 2025-12-27 16:45 |
| b3 | Bug | ✅ Complete | None | bug-b3-production-crash | 2025-12-27 09:15 |
| 3-TC9768-02 | Test Case | 🚫 Blocked | 3-TC9768 | feature-3-TC9768-02-validation | 2025-12-27 11:20 |

---

## Quick Scenario Reference

| Scenario | Plan ID Format | Git Branch Format | File Name |
|----------|----------------|-------------------|-----------|
| New feature plan | Major-PlanId | feature-Major-PlanId-PhaseId-desc | PLAN-PROJECT-Major-PlanId-desc.md |
| Feature plan phase | Major-PlanId-PhaseId | feature-Major-PlanId-PhaseId-desc | PLAN-PROJECT-Major-PlanId-PhaseId-desc.md |
| Bug during plan | Major-PlanId-PhaseId bBugId | bug-Major-PlanId-PhaseId-bBugId-desc | PLAN-PROJECT-Major-PlanId-PhaseId-bBugId-desc.md |
| Bug from production | PROJECT-bBugId | bug-bBugId-desc | PLAN-PROJECT-bBugId-desc.md |
| Test case investigation | Major-TCID-PhaseId | feature-Major-TCID-PhaseId-desc | PLAN-PROJECT-Major-TCID-PhaseId-desc.md |

---

## Related Guides

- See **[GUIDE--Plan-Phase-Versioning--CORE.md](GUIDE--Plan-Phase-Versioning--CORE.md)** for versioning fundamentals
- See **[GUIDE--Plan-Phase-Versioning--NAMING.md](GUIDE--Plan-Phase-Versioning--NAMING.md)** for file naming standards
- See **[GUIDE--Plan-Phase-Versioning--EXAMPLES.md](GUIDE--Plan-Phase-Versioning--EXAMPLES.md)** for migration guides

---

**Fragment Status:** This is the BRANCHING fragment covering Git branch naming and CI/CD integration.
