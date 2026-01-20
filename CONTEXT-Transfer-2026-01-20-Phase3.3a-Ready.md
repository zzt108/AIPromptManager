# 🚀 Context Transfer: AIPromptManager

## 📍 Where We Are (Status)

* **Current Phase:** Phase 3.3a (Ready for Implementation)
* **Last Completed:** Planning Phase 3.3a (Filesystem View) & Architectural Definition for Phase 3.4
* **In Progress:** Starting Implementation of Phase 3.3a
* **Next Up:** Implement `Skill.status`, Intelligent Metadata Extractor, and UI Status Indicators

## 📝 Task Status (`task.md` Snapshot)

```markdown
# Phase 3.3a: Registry Filesystem View (Immediate)

## Problem
Files that don't match naming conventions silently disappear during refresh. Users can't see what files exist on disk vs what's tracked in registry.

## Tasks

### Implementation
- [ ] Add `status` field to `Skill` model ("valid", "unrecognized", "parse_error")
- [ ] Create intelligent metadata extractor (filename → H1 → frontmatter → defaults)
- [ ] Update `refresh_registry()` to track ALL .md files (permissive mode)
- [ ] Update UI to show status indicators (✓, ⚠️, ❌)
- [ ] Add status details tooltip/column

### Testing
- [ ] Test with files matching conventions
- [ ] Test with non-matching filenames
- [ ] Test with intelligent extraction strategies
```

## 🧠 Key Context & Decisions

* **Registry Logic (Phase 3.3a):**
  * **Permissive Mode:** Registry will track ALL `.md` files in scan directories.
  * **Status Fields:** New `status` ("valid", "unrecognized", "parse_error") and `status_detail` fields in `Skill` model.
  * **Intelligent Extraction:** 1. Filename Pattern -> 2. H1 Version Pattern -> 3. Frontmatter -> 4. Defaults.
  * **UI:** Color-coded rows (Black=Valid, Orange=Unrecognized, Red=Error).

* **Future Architecture (Phase 3.4 - Planned):**
  * **Structure:** `.apm/` folder in library repo will hold `professions/` and `domains/`.
  * **Profession:** Defines Core + Platform skills (e.g., `backend-developer.profession.json`).
  * **Domain:** Defines Profession + Domain skills (e.g., `i-ching-python.domain.json` extends backend-dev).
  * **Project Config:** User projects reference a specific Domain file.

## 📂 Hot Files (To Open First)

* `src/models/skill.py` (Add status fields)
* `src/services/registry_service.py` (Implement `_extract_metadata_intelligently`)
* `src/ui/registry_panel.py` (Add UI indicators)
* `tests/test_registry_service.py` (New extraction tests)

## ⏭️ Prompt for Next Session
>
> "I am continuing work on AIPromptManager Phase 3.3a. We have completed the planning and architectural review.
> Please review the attached `task.md`, `implementation_plan.md` and the 'Hot Files'.
>
> **Immediate Goal:** Start the implementation of Phase 3.3a:
>
> 1. Update `Skill` model with `status` fields.
> 2. Implement `_extract_metadata_intelligently` in `RegistryService`.
> 3. Verify with new unit tests."

## 🏗️ Visualization (Current State)

See [State 2026-01-20](file:///c:/Git/AIPromptManager/doc/plans/state_20260120_transfer.md)
