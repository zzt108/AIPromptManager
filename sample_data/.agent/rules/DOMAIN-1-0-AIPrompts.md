# SPACE-1-0-AIPrompts: AI Prompt Repository Organization

This repository contains structured AI prompts, knowledge files, and coding conventions for use with AI assistants (Gemini, Cursor, Perplexity, etc.).

---

## Directory Structure

```
prompts/
├── core/                    # Shared, cross-project resources
│   ├── GUIDE-*             # Coding conventions, best practices
│   └── global-*.md         # Universal instructions
├── platform/               # Platform-specific knowledge
│   ├── python/             # Python coding conventions
│   ├── dotnet/             # C#, WinUI, Avalonia, MAUI
│   └── kotlin/             # Kotlin/Android
└── domain/                 # Project-specific contexts
    ├── AIPromptManager/    # This tool's development space
    ├── personal/           # Personal projects
    ├── work/               # Work-related projects
    └── Google/             # Google tool configurations
```

---

## File Naming Conventions

### Pattern: `{TYPE}-{VERSION}-{DESCRIPTION}.md`

**Version formats (both are valid):**

- **Semantic**: `GUIDE-1-3-General.md` → major=1, minor=3
- **Date-based**: `SPACE-260120-ProjectName.md` → YYMMDD format

**Examples:**

```
GUIDE-1-5-visualization-plantuml-core.md   # Semantic version
SPACE-260111-AIPromptManager-Python.md     # Date-based version
PROMPT-1-0-TestResultFix.md                # One-shot task prompt
```

### Supported Types

| Type | Alias | Purpose | Example |
|------|-------|---------|---------|
| `GUIDE` | `SKILL` | Reusable knowledge, coding conventions | `GUIDE-1-3-CodingConvention-Python.md` |
| `SPACE` | `DOMAIN` | Project-specific AI instructions | `SPACE-260120-MyProject.md` |
| `PROMPT` | - | One-shot task prompts | `PROMPT-1-0-FixTestResults.md` |
| `WORKFLOW` | - | Step-by-step procedures | `WORKFLOW-1-0-DeploymentSteps.md` |

**Subtypes:** Use underscore for subtypes: `GUIDE_CC-1-0-Python.md` (CC = Coding Convention)

---

## File Content Structure

### Required: H1 Heading

Every file MUST have an H1 heading that describes its purpose:

```markdown
# Python Coding Conventions & Standards

Content follows...
```

### Optional: Frontmatter (for future tooling)

```yaml
---
type: GUIDE
version: 1.3
description: Python coding conventions for desktop apps
---
```

---

## Creating New Files

**When to create a new version:**

- Breaking changes → increment major: `GUIDE-2-0-...`
- New features/additions → increment minor: `GUIDE-1-4-...`
- For date-based: use today's date: `SPACE-260121-...`

**When to create a new file:**

- Different project/domain → new file under `domain/{project}/`
- Different platform → new file under `platform/{name}/`
- Different topic → new file with descriptive name

---

## File Organization Rules

1. **Platform-agnostic knowledge** → `core/`
2. **Language/framework-specific** → `platform/{name}/`
3. **Project-specific contexts** → `domain/{project}/`
4. **One SPACE per project** (or per major version)
5. **Keep older versions** for reference (don't delete)

---

## Integration with AI Tools

**For Perplexity Spaces:** Copy SPACE file content to Space Instructions

**For Gemini/Cursor:** Reference files via `.agent/rules/` symlinks or copies

**For Claude/ChatGPT:** Attach relevant files to conversations

---

## Notes

- All files are markdown (`.md`)
- Use descriptive basenames (avoid generic names like "v2")
- Prefer kebab-case for descriptions: `visualization-plantuml-core`
- Maximum 80-char line width in code blocks
