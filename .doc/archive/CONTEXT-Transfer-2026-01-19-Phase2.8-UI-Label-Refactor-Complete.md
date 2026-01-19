# 🚀 Context Transfer: AiPrompts Asset Manager

## 📍 Where We Are (Status)

* **Current Phase:** Phase 2.8 - UI Refactor & Enhancements
* **Last Completed:** UI Repositioning (Renaming to "Teaching Paradigm", Test Updates, VS Code Tasks)
* **In Progress:** Context Transfer
* **Next Up:** Config Editor Enhancements (Double-click interaction, Quick View Popup)

## 📝 Task Status (`task.md` Snapshot)

```markdown
# Phase 2.8: UI Refactor & Enhancements

## Repositioning ("Teaching Paradigm")

- [x] Rename "Registry" -> "**Knowledge Base**" (or "Ideas") <!-- id: 0 -->
- [x] Rename "Config Editor" -> "**Profession Designer**" <!-- id: 1 -->
- [x] Rename "Build Agent" -> "**Agent Onboarding**" (or "Induction") <!-- id: 2 -->
- [x] Move Plan Files: `.agent/rules/*.md` -> `.doc/plans/` (exclude from registry) <!-- id: 3 -->

## Config Editor Enhancements

- [ ] Interaction: Double-click to move ingredients between lists <!-- id: 4 -->
- [ ] Feature: Quick View / "Ingredient Card" (Modal/Popup) <!-- id: 5 -->
  - [ ] Show H1 + H2 headings (TOC) <!-- id: 6 -->
  - [ ] Show first paragraph/summary <!-- id: 7 -->
  - [ ] "Cultured" viewing experience <!-- id: 8 -->

## Repository

- [ ] Columns should be sortable <!-- id: 9 -->

## Verification

- [x] Update existing tests for renamed components <!-- id: 10 -->
- [ ] Add tests for new interaction logic <!-- id: 11 -->
```

## 🧠 Key Context & Decisions

* **Design Paradigm:** "Teaching/Corporate" (Skill, Knowledge Base, Profession, Onboarding).
* **Code Refactoring:**
    * `main_window.py`: Tabs reordered (KB -> Profession -> Onboarding).
    * `config_panel.py`: "Config" strings changed to "Profession".
    * `build_panel.py`: Input/Output labels clarified.
* **Dev Environment:**
    * Added VS Code Task: "AssetManager: Run App" (runs `src/main.py`).
    * Fixed `ModuleNotFoundError` by running script directly instead of via `-m`.
* **Testing:** All 82 tests passed. (Tkinter `init.tcl` warnings ignored).

## 📂 Hot Files (To Open First)

* `c:/Git/AiPrompts/AssetManager/src/ui/config_panel.py` (Double-click & Popup work)
* `c:/Git/AiPrompts/AssetManager/src/ui/main_window.py`
* `c:/Git/AiPrompts/AssetManager/tests/test_config_panel.py`

## ⏭️ Prompt for Next Session

*(Copy and paste this into the new chat)*

> "I am continuing work on Phase 2.8 (UI Refactor & Enhancements). We have successfully repositioned the UI to the 'Teaching' paradigm (Knowledge Base, Profession, Onboarding) and verified it.
> Please review the attached `task.md` and the 'Hot Files' listed above.
>
> **Immediate Goal:** Implement the **Double-click to move items** and **Quick View popup** features in the Profession Designer (`config_panel.py`)."

## 🏗️ Visualization (Current State)

See `.doc/ARCH-2026-01-19-Teaching-Paradigm-Implemented.puml`
