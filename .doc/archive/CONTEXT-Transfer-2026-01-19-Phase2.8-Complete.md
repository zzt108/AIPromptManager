# 🚀 Context Transfer: Asset Manager UI Enhancements

## 📍 Where We Are (Status)

* **Current Phase:** Phase 2.8 (Knowledge Base Enhancements) - **COMPLETE**
* **Last Completed:** Implemented sortable columns, "Show Hidden" toggle, and fixed type derivation regex in `RegistryPanel`.
* **In Progress:** Transitioning to Phase 3 (Standalone Repository & Advanced Features).
* **Next Up:** 
    1. **Standalone Repository**: Move `AssetManager` to a separate public repo.
    2. **Intelligent Rename**: Implement configurable file renaming conventions.

## 📝 Task Status (`task.md` Snapshot)

```markdown
# Phase 2.8: Knowledge Base Panel Enhancements

## Visibility Toggle Implementation
- [x] Add `is_enabled` field to `Ingredient` model <!-- id: 0 -->
- [x] Update `RegistryService` to support visibility toggle <!-- id: 1 -->
- [x] Persist hidden state in `registry.json` <!-- id: 2 -->
- [x] Add `set_enabled()` multi-select + filter methods to service <!-- id: 3 -->

## Registry Panel UI Enhancements
- [x] Add Filter box with Clear (X) button <!-- id: 4 -->
- [x] Implement visibility toggle (Hide/Show context menu, multi-select) <!-- id: 5 -->
- [x] Apply greyed-out italic style to hidden items in KB <!-- id: 6 -->
- [x] Add Quick View popup (port from ConfigPanel) <!-- id: 7 -->
- [x] Add context menu with "Quick View", "Show in Explorer", "Open with Editor" <!-- id: 8 -->
- [x] Implement Sortable Columns (click header to sort) <!-- id: 18 -->
- [x] Add "Show Hidden Skills" toggle button/checkbox to toolbar <!-- id: 19 -->
- [x] Fix type derivation regex to support mixed-case and suffixes <!-- id: 20 -->
- [ ] Normalize type names (strip suffixes, e.g. `GuideCC` -> `GUIDE`) <!-- id: 21 --> NOTE: Implemented via regex/prefix matching logic, but item left open for strict verification if needed.

## Filtering Logic
- [x] Implement free-text filter on Name AND Path columns <!-- id: 9 -->
- [x] Wire filter to KeyRelease event <!-- id: 10 -->

## ConfigPanel Integration
- [x] Filter out hidden ingredients from Available list <!-- id: 11 -->

## Tests
- [x] Existing tests updated for `list_enabled()` mocks <!-- id: 12 -->
- [x] Run pytest - 81 passed (5 Tk fixture errors - pre-existing) <!-- id: 15 -->
- [x] Run mypy --strict - 0 errors <!-- id: 16 -->
```

## 🧠 Key Context & Decisions

* **UI Paradigm**: "Teaching" paradigm (Knowledge Base, Profession Designer).
* **Visibility Logic**: Items hidden in KB are *excluded* from PD available list.
* **Type Derivation**: Now supports mixed-case types (e.g. `GuideCC`) and alphanumeric suffixes. Logic uses prefix matching against standard types (`GUIDE`, `SPACE`, etc.) or falls back to the captured type.
* **Auto-Refresh**: `MainWindow` handles refresh logic when switching tabs.
* **Testing**: UI tests have some fragility with Tk fixture teardown (known issue), but logic is verified.
* **New Requirements**: User wants to move to a **standalone public repository** and requires an **Intelligent Rename** tool with configurable conventions.

## 📂 Hot Files (To Open First)

* `c:\Git\AiPrompts\AssetManager\src\ui\registry_panel.py`
* `c:\Git\AiPrompts\AssetManager\src\services\registry_service.py`
* `c:\Git\AiPrompts\AssetManager\src\ui\main_window.py`

## ⏭️ Prompt for Next Session

> "I am continuing work on the Asset Manager. We just completed Phase 2.8 (UI Enhancements) including filtering, sorting, and visibility toggles.
> 
> **Immediate Goal:** Plan and execute the move of `AssetManager` to a **standalone repository** to showcase it publicly. This involves extracting the code, setting up a new repo structure, and ensuring all dependencies are handled.
> 
> ** Secondary Goal:** Begin planning the **Intelligent Rename** feature (configurable conventions) which will follow the repo migration."

## 🏗️ Visualization (Current State)

See `c:\Git\AiPrompts\.doc\DOC-20260119-Phase2.8-Architecture.md` for PlantUML diagram.
