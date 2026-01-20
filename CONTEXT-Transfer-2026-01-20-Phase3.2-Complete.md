# 🚀 Context Transfer: AI Prompt Manager

## 📍 Where We Are (Status)

* **Current Phase:** Phase 3.2 (Completed) / Entering Phase 3.3 (Refinement)
* **Last Completed:** Terminology Refactoring (Ingredient -> Skill)
* **In Progress:** Investigating Registry Refresh issues (silent file skipping)
* **Next Up:** Fix "Silent Skip" bug in Registry Refresh / UI Feedback

## 📝 Task Status (`task.md` Snapshot)

```markdown
# Phase 3.2: Terminology Refactoring
- [x] Rename `models/ingredient.py` to `models/skill.py`
- [x] Rename `Ingredient` class to `Skill`
# ... (All Phase 3.2 items checked)

# Phase 3.3: Refinement & Bug Fixes
- [ ] Feature: Surface Registry Scan Errors in UI (Fix "Silent Skip")
- [ ] Verification: Check regex patterns against actual file system
```

## 🧠 Key Context & Decisions

* **Terminology:** Globally switched from "Ingredient" to "Skill".
* **Backward Compatibility:** JSON files still use `"ingredients"` key.
* **Architecture Issue:** `RegistryService.refresh_registry` catches `ValueError` (pattern mismatch) and adds to `result.errors`, but the UI (`RegistryPanel`) ignores these errors, leading to "silent failures" where files disappear.
* **Regex Pattern:** Currently `[a-zA-Z0-9_]+` (case-insensitive via character class). Confirmed correct for mixed case, but need to surface *why* it fails on specific files.

## 📂 Hot Files (To Open First)

* `src/services/registry_service.py` (Logic for refresh and error catching)
* `src/ui/registry_panel.py` (UI that needs to display the errors)
* `src/services/naming_service.py` (Filename pattern logic)

## ⏭️ Prompt for Next Session

> "I am continuing work on AIPromptManager. We just completed the Terminology Refactoring (Phase 3.2) and identifying a bug in the Registry Refresh.
> Please review the attached `task.md` and the 'Hot Files' listed above.
>
> **Immediate Goal:** Fix the 'Silent Skip' issue in Registry Refresh. The `RegistryService` returns errors, but the `RegistryPanel` doesn't show them. We need to:
>
> 1. Update `RegistryPanel` to inspect `result.errors`.
> 2. add the errors to the registry with a status 'error' and display differently in the UI
> 3. Verify why the user's specific files are being skipped."

## 🏗️ Visualization (Current State)

See [Registry Refresh Flow State](file:///c:/Git/AIPromptManager/doc/plans/state_20260120.md)
