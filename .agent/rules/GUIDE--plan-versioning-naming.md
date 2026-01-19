---
trigger: model_decision
---

# GUIDE - Plan and Phase Implementation Versioning - NAMING (v1.9)

**Version:** 1.9  
**Date:** 2026-01-11  
**Status:** Active  
**Fragment:** NAMING - File Naming for Plans and Ingredients

---

## Plan Document Naming Convention

### Purpose

Plan document filenames must clearly differentiate planning artifacts from source code files to ensure:
- Instant recognition of document type in file explorers
- Clean separation between implementation files and planning documents
- Search efficiency when filtering by document category
- Version control clarity when reviewing changes

### Naming Standard

**Format:** `PLAN-PROJECT-Version-Description.md`

**Components:**
- **PLAN** — Required prefix for all planning documents
- **PROJECT** — Project identifier (VECTOOL, SFERA, QATOOLS, LINX, AIPM)
- **Version** — Plan version in hyphen notation (e.g., 4-01, 4-01-03, b3, 4-01-03-b1)
- **Description** — Kebab-case title (2-5 words)
- **.md** — Markdown file extension

### File Naming Examples

| Scenario | Filename |
|----------|----------|
| Feature plan parent | `PLAN-VECTOOL-4-01-vector-store-improvements.md` |
| Feature plan phase | `PLAN-VECTOOL-4-01-01-database-schema-refactor.md` |
| Context-aware bug | `PLAN-VECTOOL-4-01-03-b1-dropdown-null-fix.md` |
| Standalone bug | `PLAN-VECTOOL-b3-production-memory-leak.md` |
| Test case investigation | `PLAN-SFERA-3-TC9768-timeout-analysis.md` |
| AiPrompts Manager plan | `PLAN-AIPM-1-01-registry-service.md` |

### Description Keywords

Common patterns for selecting description text:
- **Schema work:** schema-refactor, database-migration, index-optimization
- **API development:** api-implementation, rest-endpoints, query-parser
- **UI changes:** ui-integration, form-controls, layout-updates
- **Testing:** unit-tests, integration-tests, test-coverage
- **Bug fixes:** null-checks, error-handling, validation-fix
- **Performance:** performance-optimization, caching-layer, load-testing
- **Refactoring:** code-refactor, dependency-injection, pattern-implementation
- **Configuration:** config-updates, settings-migration, environment-setup
- **Monitoring:** logging-implementation, metrics-tracking, diagnostics

---

## Ingredient/Prompt File Naming Convention (AiPrompts Library)

### Purpose

Ingredient files (AI prompts, guides, workflows) serve as reusable assets in the AiPrompts library. Clear naming conventions enable:
- Version tracking of prompt evolution
- Easy identification of content type and purpose
- Automated registry management
- Efficient filtering and search

### Naming Strategies

Two strategies exist based on file lifecycle and purpose:

#### 1. Content Versioning (Evolving Content)

**Format:** `{TYPE}-{major}-{minor}-{topic}.md`

**When to use:**
- Content that evolves over time
- Multiple versions may coexist
- Version history is important

**Components:**
- **TYPE** — Document category (GUIDE, PROMPT, WORKFLOW, etc.)
- **major** — Major version number (breaking changes)
- **minor** — Minor version number (additive changes)
- **topic** — Lowercase, hyphenated description
- **.md** — Markdown extension

**Examples:**
| File | Description |
|------|-------------|
| `GUIDE-2-0-logging.md` | Logging standards v2.0 |
| `GUIDE-3-0-logging.md` | Logging standards v3.0 (new, coexists) |
| `GUIDE-3-0-conventions.md` | Coding conventions v3.0 |
| `WORKFLOW-1-2-commit-rules.md` | Commit rules v1.2 (minor update) |

**Version Bump Rules:**
- **Major bump** (e.g., 2-0 → 3-0): Breaking changes, new architecture, incompatible with previous
- **Minor bump** (e.g., 1-0 → 1-1): Additive changes, clarifications, expansions

#### 2. Type-Prefixed (Date-Versioned or Living Documents)

**Format:** `{TYPE}-{identifier}-{topic}.md`

**When to use:**
- Project-specific contexts (SPACE prompts)
- Living documents (GUIDEs that update in-place)
- Workflows tied to specific processes

**Components:**
- **TYPE** — Document category (SPACE, GUIDE, WORKFLOW, PROMPT, FRAGMENT)
- **identifier** — Date (YYMMDD) or unique ID
- **topic** — Kebab-case description
- **.md** — Markdown extension

**Examples:**
| File | Type | Description |
|------|------|-------------|
| `SPACE-260110-AIPrompts-Python.md` | Space Prompt | Project context for AiPrompts (dated Jan 10, 2026) |
| `SPACE-260107-VecTool-Avalonia.md` | Space Prompt | Project context for VecTool |
| `GUIDE-CodingConvention-Python.md` | Guide | Living doc (no version, updates in-place) |
| `GUIDE-Plan-Phase-Versioning.md` | Guide | This document |
| `WORKFLOW-gap-analysis-1-0.md` | Workflow | Gap analysis workflow v1.0 |
| `PROMPT-FRAGMENT-Logging.md` | Fragment | Reusable logging prompt snippet |

### Type Definitions

| Type | Purpose | Versioning | Examples |
|------|---------|------------|----------|
| **SPACE** | Project-specific AI context and rules | Date-versioned (YYMMDD) | SPACE-260110-AIPrompts-Python.md |
| **GUIDE** | Reference documentation | Unversioned or semantic | GUIDE-CodingConvention-Python.md |
| **WORKFLOW** | Process automation instructions | Semantic versioning | WORKFLOW-gap-analysis-1-0.md |
| **PROMPT** | Standalone AI instructions | Semantic versioning | PROMPT-code-review-2-0.md |
| **FRAGMENT** | Reusable prompt components | Unversioned | PROMPT-FRAGMENT-Logging.md |

### Hyphen Usage Rules

**CRITICAL:** All version identifiers use hyphens, never dots.

| Context | Correct | Incorrect |
|---------|---------|-----------|
| Version numbers | `2-0`, `3-1` | `2.0`, `3.1`, `v2.0` |
| Filenames | `GUIDE-2-0-logging.md` | `logging-v2.md`, `logging_2_0.md` |
| Topics | `coding-convention` | `coding_convention`, `CodingConvention` |

### Registry Integration

The `registry.json` file maps logical ingredient names to file paths:

```json
{
  "ingredients": {
    "logging": { "path": "core/GUIDE-2-0-logging.md" },
    "python-space": { "path": "domain/SPACE-260110-AIPrompts-Python.md" },
    "conventions": { "path": "platform/python/GUIDE-3-0-conventions.md" },
    "gap-analysis": { "path": "workflows/WORKFLOW-gap-analysis-1-0.md" }
  }
}
```

### Folder Structure Context

Ingredient files are organized semantically:

| Folder | Purpose | Naming Strategy |
|--------|---------|-----------------|
| `core/` | Universal, tech-agnostic | Content versioning (e.g., `GUIDE-2-0-logging.md`) |
| `platform/` | Tech-stack specific | Content versioning or Type-prefixed |
| `workflows/` | Process automation | Type-prefixed (WORKFLOW-) |
| `domain/` | Project context | Type-prefixed (SPACE-) |
| `personal/` | Non-work prompts | Either strategy |

---

## Related Guides

- See **[GUIDE--Plan-Phase-Versioning--CORE.md](GUIDE--Plan-Phase-Versioning--CORE.md)** for versioning fundamentals
- See **[GUIDE--Plan-Phase-Versioning--BRANCHING.md](GUIDE--Plan-Phase-Versioning--BRANCHING.md)** for Git branch naming
- See **[GUIDE--Plan-Phase-Versioning--EXAMPLES.md](GUIDE--Plan-Phase-Versioning--EXAMPLES.md)** for migration guides

---

**Fragment Status:** This is the NAMING fragment covering file naming for plans and ingredients.
