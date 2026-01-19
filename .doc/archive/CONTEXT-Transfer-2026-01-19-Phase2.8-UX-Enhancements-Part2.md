# 🚀 Context Transfer: AiPrompts Asset Manager

## 📍 Where We Are (Status)

* **Current Phase:** Phase 2.8 - UI Refactor & Enhancements
* **Last Completed:** 
    * **Profession Designer Enhancements**: Double-click to move, Filter box, Quick View popup, Tooltips.
    * **Global UX**: Tab tooltips explaining the "Teaching Paradigm".
* **In Progress:** Transitioning to Knowledge Base panel improvements.
* **Next Up:** Knowledge Base Enhancements (Visibility toggle, Filtering, Quick View parity).

## 📝 Task Status (`task.md` Snapshot)

```markdown
# Phase 2.8: UI Refactor & Enhancements

## Repositioning ("Teaching Paradigm")

- [x] Rename "Registry" -> "**Knowledge Base**" <!-- id: 0 -->
- [x] Rename "Config Editor" -> "**Profession Designer**" <!-- id: 1 -->
- [x] Rename "Build Agent" -> "**Agent Onboarding**" <!-- id: 2 -->
- [x] Move Plan Files: `.agent/rules/*.md` -> `.doc/plans/` <!-- id: 3 -->

## Config Editor Enhancements

- [x] Interaction: Double-click to move ingredients between lists <!-- id: 4 -->
- [x] Feature: Quick View / "Ingredient Card" (Modal/Popup) <!-- id: 5 -->
  - [x] Show H1 + H2 headings (TOC) <!-- id: 6 -->
  - [x] Show first paragraph/summary <!-- id: 7 -->
- [x] Feature: Verbose Tooltips for tabs and controls <!-- id: 9 -->
- [x] Free text filter for Knowledge Base in Designer <!-- id: 10 -->

## Knowledge Base Panel (Next)

- [ ] Visibility Toggle: Hide/Enable prompt files (multi-selection) <!-- id: 14 -->
- [ ] UI Feedback: Greyed out & italic for hidden files <!-- id: 15 -->
- [ ] Feature: parity Quick View panel <!-- id: 16 -->
- [ ] Feature: Filter box with Clear (X) button <!-- id: 17 -->
- [ ] Context Menus: "Show in Explorer", "Open with default editor" <!-- id: 18 -->

## Repository

- [ ] Columns should be sortable <!-- id: 11 -->
```

## 🧠 Key Context & Decisions

* **Teaching Paradigm**: Knowledge Base (All sources) -> Profession Designer (Role selection) -> Agent Onboarding (Induction).
* **Quick View Logic**: Uses markdown parsing (H1, first para, H2 list) in a `Toplevel` popup.
* **Filter Logic**: Free text search against ingredient names.
* **New Idea**: "Visibility Toggle" will allow users to declutter their Knowledge Base. Hidden items shouldn't appear in the Profession Designer.

## 📂 Hot Files (To Open First)

* `AssetManager/src/ui/registry_panel.py` (Main target for next session)
* `AssetManager/src/ui/config_panel.py` (For clear buttons and filter parity)
* `AssetManager/src/services/registry_service.py` (For visibility state management)
* `AssetManager/src/models/ingredient.py` (Add `is_enabled` field)

## ⏭️ Prompt for Next Session

*(Copy and paste this into the new chat)*

> "I am starting a new interactive design session for Phase 2.8. We just completed the Profession Designer enhancements.
> 
> **Immediate Goal:** Enhance the **Knowledge Base** tab with visibility toggles (hide/enable files), a filter box with a clear button, and Quick View parity. Also, add 'Show in Explorer' and 'Open with Editor' to context menus.
>
> Please review the attached `task.md` and the 'Hot Files' listed above."

## 🏗️ Visualization (Current State)

See `.doc/ARCH-2026-01-19-Phase2.8-UI-Complete.puml` (to be updated)
