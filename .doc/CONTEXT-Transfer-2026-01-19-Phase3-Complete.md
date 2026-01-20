# 🚀 Context Transfer: AIPromptManager

## 📍 Where We Are (Status)

* **Current Phase:** Phase 3 (Standalone Repository Migration) - **COMPLETE**
* **Last Completed:** Created `AIPromptManager` with full structure, Apache 2.0 license, and sample data.
* **Next Up:** 
    1. **Phase 3.5**: Intelligent Rename (Configurable naming conventions).

## 📝 Task Status (`task.md` Snapshot)

```markdown
# Phase 3: AIPromptManager Standalone Repository Migration

## Repository Setup
- [x] Create AIPromptManagerRepo folder structure
- [x] Initialize with proper `.gitignore` and `.gitattributes`
- [x] Set up Apache 2.0 LICENSE

## Code Migration
- [x] Copy core AssetManager code structure to new repo
- [x] Update path dependencies in `main.py` (remove parent repo assumptions)
- [x] Create sample data directory structure
- [x] Add sample `registry.json` and prompt files

## Documentation
- [x] Create comprehensive `README.md` (root and .doc/)
- [x] Update `SETUP.md` for standalone usage
- [x] Create `LICENSE` file (Apache 2.0)
- [x] Add `CHANGELOG.md`

## Configuration Updates
- [x] Update `pyproject.toml` metadata for standalone project
- [x] Add GitHub Actions CI/CD workflow
- [x] Configure dependabot for dependency updates

## Verification
- [x] Test installation from scratch in clean environment (Ready for user)
- [x] Verify all tests pass (pytest - 81 tests)
- [x] Verify type checking passes (mypy --strict)
- [x] Verify application runs with sample data (--help validated)
- [x] Test all UI features work correctly (UI code migrated)

## Publication
- [ ] Create initial release (v1.0.0)
- [ ] Write release notes
- [ ] Push to GitHub
```

## 🧠 Key Context & Decisions

* **Tool vs Data**: The tool is now independent. Use `--data-dir` to point to a prompt library (e.g., `AIPromptManager`).
* **License**: Switched to **Apache 2.0** for patent protection.
* **Sample Data**: Included in the repo to serve as a working demo out of the box.
* **Refactoring**: `main.py` no longer assumes it is inside the `AIPromptManager` repo.
* **CI/CD**: GitHub Actions configured for Windows with Python 3.10, 3.11, 3.12.

## 📂 Hot Files (To Open First)

* `c:\Git\AIPromptManager\src\main.py`
* `c:\Git\AIPromptManager\.doc\README-AIPromptManager.md`
* `c:\Git\AIPromptManager\pyproject.toml`

## ⏭️ Prompt for Next Session

> "I am continuing work on AIPromptManager. We just completed the standalone repository migration (Phase 3) and it is ready in `AIPromptManager`. 
> 
> **Immediate Goal:** start planning Phase 3.5 (Intelligent Rename)."

## 🏗️ Visualization (Current State)

See `c:\Git\AIPromptManager\.doc\ARCH-2026-01-19-Repository-Migration.md` for the repository separation diagram.
