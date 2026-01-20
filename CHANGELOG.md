# Changelog

All notable changes to AIPromptManager will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-01-20

### Features

- **Intelligent Metadata Extraction** - Automatic skill metadata parsing using priority system:
  - Filename pattern matching (e.g., `SKILL-1-0-Name.md`)
  - H1 heading extraction from file content
  - YAML frontmatter parsing
  - Sensible defaults for unrecognized files
- **Status Indicators** - Visual file status in Knowledge Base:
  - ✓ Valid files matching conventions
  - ⚠️ Unrecognized files (non-standard naming)
  - ❌ Parse errors (malformed files)
- **YAML Support** - Registry now scans `.yaml` and `.yml` files alongside `.md`
- **Open with Notepad** - New context menu option for quick text editing
- **SkillStatus Enum** - Type-safe status handling replacing magic strings

### Improvements

- Permissive registry mode shows ALL markdown files, not just convention-matching ones
- Enhanced test coverage (81 → 201 tests)
- Improved mypy type annotations throughout codebase

### Technical

- Added `SkillStatus` enum in `src/models/skill_status.py`
- Extended `Skill` model with `status` and `status_detail` fields
- Refactored `refresh_registry()` for permissive file scanning

---

## [1.0.0] - 2026-01-19

### Initial Public Release

#### Features

- **Knowledge Base Panel** with sortable columns, filtering, and visibility toggles
- **Profession Designer** with Available/Selected list management for skills
- **Agent Onboarding** builder for generating `agent.config.json` files
- **Registry Management** with automatic scanning and metadata extraction
- **File Sync** with bidirectional timestamp comparison and conflict detection
- **Interactive Dialogs** for handling update available and local changes scenarios
- **Quick View** popups for inspecting skill contents
- **Context Menu** actions: Show in Explorer, Open with Default Editor
- **Visibility Management** with persistent state in registry.json
- **Multi-select Operations** for bulk hide/show actions
- **Teaching Paradigm** UI terminology (Knowledge Base, Profession Designer, Agent Onboarding)

#### Architecture

- Clean separation: Models, Repositories, Services, UI layers
- Full test coverage with pytest (201 tests)
- Strict type checking with mypy (0 errors)
- Structured logging with structlog
- Plain tkinter for cross-platform compatibility

#### Technical Details

- Python 3.10+ support
- Apache 2.0 license
- Command-line argument support (`--data-dir`)
- Sample data included for immediate demo capability

[1.1.0]: https://github.com/zzt108/AIPromptManager/releases/tag/v1.1.0
[1.0.0]: https://github.com/zzt108/AIPromptManager/releases/tag/v1.0.0
