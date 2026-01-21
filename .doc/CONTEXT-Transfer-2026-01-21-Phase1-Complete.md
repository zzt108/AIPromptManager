# 🚀 Context Transfer: AI Prompt Manager - Archive Service

## 📍 Where We Are (Status)

* **Current Phase:** Phase 3.4 (Archive/Restore Service Implementation)
* **Last Completed:** Phase 1: Archive/Restore Service Backend (Stateless Architecture)
* **In Progress:** Transitioning to Phase 2 (UI Implementation)
* **Next Up:** Implement "Show Archived" toggle and Context Menu in `RegistryPanel`

## 📝 Task Status (`task.md` Snapshot)

```markdown
# Tasks

- [x] Planning & Design
  - [x] Initial project research
  - [x] Clarify requirements (3 rounds of questions)
  - [x] Write technical implementation plan
  - [x] Add git branch names
- [x] Phase 1: Archive/Restore Service (`feature/archive-restore-service`)
- [ ] Phase 2: Archive/Restore UI (`feature/archive-restore-ui`)
- [ ] Phase 3: Move to Folder (`feature/move-to-folder`)
- [ ] Phase 4: H1 Edit in Quick View (`feature/quickview-h1-edit`)
- [ ] Phase 5: Settings Dialog (`feature/settings-dialog`)
- [ ] Phase 6: Compare/Merge Tool (`feature/compare-merge-tool`)
- [ ] Verification & Tests
```

## 🧠 Key Context & Decisions

* **Stateless Restore Architecture:** We revised the design to **NOT** store `original_path` in `registry.json` or the `Skill` model.
  * **Archive Location:** Files are moved to `.archive/{relative_path}`.
  * **Restore Logic:** The original path is derived purely by stripping the `.archive/` prefix.
  * **Benefit:** Robustness; works even if `registry.json` is lost or regenerated.
* **Service Layer:** `RegistryService` now has `archive_skills` and `restore_skills` methods.
* **Dependencies:** `SkillStatus.ARCHIVED` was added to the enum.
* **Plan Document:** The active plan is `doc/plans/PLAN-Phase3.4-NewFeatures.md`.

## 📂 Hot Files (To Open First)

* `src/services/registry_service.py` (Contains the new archive/restore logic)
* `src/models/skill.py` (Verified: `original_path` is NOT present)
* `src/models/skill_status.py`
* `tests/test_archive_service.py`
* `src/ui/registry_panel.py` (Target for Phase 2 UI work)

## ⏭️ Prompt for Next Session

> "I am continuing work on Phase 2 (Archive/Restore UI) of the AIPromptManager. We just completed Phase 1 (Backend Service) using a stateless directory-based architecture.
> Please review the attached `task.md` and the 'Hot Files' listed above.
>
> **Immediate Goal:** Implement the UI components for archiving: 'Show Archived' checkbox, 'Archive' context menu, and visual indicators in `RegistryPanel`."
