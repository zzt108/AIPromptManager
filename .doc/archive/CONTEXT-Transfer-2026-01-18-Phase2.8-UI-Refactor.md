# 🚀 Context Transfer: AiPrompts Asset Manager

## 📍 Where We Are (Status)

* **Current Phase:** Phase 2.8 - UI Refactoring & Enhancements
* **Last Completed:** Phase 2.7 - ConfigPanel Implementation (Verified 86/86 tests)
* **In Progress:** Planning UI Refactor & Context Transfer
* **Next Up:** Implementing "Teaching" Paradigm Paradigm & Config Editor Enhancements

## 📝 Task Status (`task.md` Snapshot)

```markdown
# Phase 2.8: UI Refactor & Enhancements

## Repositioning ("Teaching Paradigm")
- [ ] Rename "Registry" -> "**Knowledge Base**" (or "Ideas")
- [ ] Rename "Config Editor" -> "**Profession Designer**"
- [ ] Rename "Build Agent" -> "**Agent Onboarding**" (or "Induction")
- [ ] Move Plan Files: `.agent/rules/*.md` -> `.doc/plans/` (exclude from registry)

## Config Editor Enhancements
- [ ] Interaction: Double-click to move ingredients between lists
- [ ] Feature: Quick View / "Ingredient Card" (Modal/Popup)
    - [ ] Show H1 + H2 headings (TOC)
    - [ ] Show first paragraph/summary
    - [ ] "Cultured" viewing experience

## Repository 
- [ ] columns should be sortable

## Verification
- [ ] Update existing tests for renamed components
- [ ] Add tests for new interaction logic
```

## 🧠 Key Context & Decisions

* **Design Pivot:** Moving from a "Cooking" metaphor (Ingredients/Recipes) to a **"Teaching/Corporate"** metaphor:
  * **Registry** -> **Knowledge Base** (The sum of all knowledge available).
  * **Config** -> **Profession** (Defining a specific role or job description).
  * **Build** -> **Onboarding/Induction** (Preparing the agent for its role).
* **File Organization:** Plan files are moving to `.doc/plans` to decongest the internal rules folder.
* **Testing:** We successfully fixed the `init.tcl` crashes by using module-scoped fixtures for Tkinter. adhere to this pattern for future UI tests.

## 📂 Hot Files (To Open First)

* `c:/Git/AiPrompts/AssetManager/src/ui/main_window.py` (Renaming Tabs)
* `c:/Git/AiPrompts/AssetManager/src/ui/config_panel.py` (Double-click & Popup)
* `c:/Git/AiPrompts/AssetManager/src/ui/registry_panel.py` (Renaming)
* `c:/Git/AiPrompts/.doc/plans/` (New home for plans)

## ⏭️ Prompt for Next Session

*(Copy and paste this into the new chat)*

> "I am continuing work on Phase 2.8 (UI Refactor & Enhancements). We have completed the functional ConfigPanel (Phase 2.7) and are now pivoting to the 'Teaching' paradigm.
> Please review the `task.md` and `implementation_plan.md`.
>
> **Immediate Goal:** Refactor the UI labels to match the new paradigm (Knowledge Base, Profession, Onboarding), move the plan files, and implement the Quick View popup in the Profession Designer."
