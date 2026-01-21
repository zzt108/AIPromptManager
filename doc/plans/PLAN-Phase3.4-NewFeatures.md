# Implementation Plan: Phase 3.4 (New Features)

## Overview

| Feature | Complexity | Priority |
|---------|-----------|----------|
| Archive/Restore Prompts | Medium | 1 |
| Move Files to Folder | Medium | 2 |
| H1 Edit in Quick View | Low | 3 |
| Compare with Merge Tool | High | 4 |
| Settings Dialog | Medium | 4 |

---

## 1. Archive/Restore Prompts

### Proposed Changes

#### [MODIFY] [skill_status.py](file:///c:/Git/AIPromptManager/src/models/skill_status.py)

- Add `ARCHIVED = "archived"` to `SkillStatus` enum

#### [MODIFY] [registry_service.py](file:///c:/Git/AIPromptManager/src/services/registry_service.py)

- Add `archive_skills(names: list[str]) -> int` method
  - Move files to `./Archive/{original_relative_path}`
  - Update skill status to `ARCHIVED`
- Add `restore_skills(names: list[str]) -> int` method
  - Move files back to original path (calculated from relative path in Archive)
  - Update status back to `VALID`
- Update `refresh_registry()` to scan `Archive/` folder

#### [MODIFY] [skill.py](file:///c:/Git/AIPromptManager/src/models/skill.py)

#### [MODIFY] [registry_panel.py](file:///c:/Git/AIPromptManager/src/ui/registry_panel.py)

- Add "Show Archived" checkbox in toolbar
- Add 📦 icon for archived files, blue color tag
- Add context menu: "Archive Selected" / "Restore Selected"
- Confirmation dialog for multi-select archive only

---

## 2. Move Files to Folder

### Proposed Changes

#### [MODIFY] [registry_service.py](file:///c:/Git/AIPromptManager/src/services/registry_service.py)

- Add `move_skills(names: list[str], dest_folder: str) -> int`
  - Move files preserving filename
  - Update registry path

#### [NEW] [move_dialog.py](file:///c:/Git/AIPromptManager/src/ui/dialogs/move_dialog.py)

- Folder picker with dropdown: `core`, `platform`, `domain`, `workflows`, `Archive`
- Or browse for custom folder within repo

#### [MODIFY] [registry_panel.py](file:///c:/Git/AIPromptManager/src/ui/registry_panel.py)

- Add context menu: "Move to Folder..."

---

## 3. H1 Edit in Quick View

### Proposed Changes

#### [MODIFY] [registry_panel.py](file:///c:/Git/AIPromptManager/src/ui/registry_panel.py) `_show_quick_view()`

- Replace title label with editable `ttk.Entry`
- Pre-fill with existing H1 or generate suggestion from filename
- Add "Save H1" button
- Add "Open in Editor" and "Open in Notepad" buttons
- On save: insert/replace H1 in file (after frontmatter if present)

#### [MODIFY] [config_panel.py](file:///c:/Git/AIPromptManager/src/ui/config_panel.py)

- Same changes to Quick View there

---

## 4. Compare with Merge Tool

### Proposed Changes

#### [NEW] [settings.json](file:///c:/Git/AIPromptManager/sample_data/.apm/settings.json)

```json
{
  "merge_tool": {
    "name": "p4merge",
    "path": "C:\\Program Files\\Perforce\\p4merge.exe",
    "args_2way": "{left} {right}",
    "args_3way": "{base} {left} {right}"
  }
}
```

#### [NEW] [compare_dialog.py](file:///c:/Git/AIPromptManager/src/ui/dialogs/compare_dialog.py)

- Drag-drop listbox to assign file roles
- For 2 files: Left, Right
- For 3 files: Left, Right, Base (common ancestor)
- OK button launches merge tool

#### [NEW] [settings_dialog.py](file:///c:/Git/AIPromptManager/src/ui/dialogs/settings_dialog.py)

- Merge tool configuration
- Dropdown with presets: P4Merge, KDiff3, WinMerge, VS Code
- Each preset auto-fills path and args
- Manual path override

**Default tool paths (Windows):**

| Tool | Default Path | 2-way Args | 3-way Args |
|------|-------------|------------|------------|
| P4Merge | `C:\Program Files\Perforce\p4merge.exe` | `{left} {right}` | `{base} {left} {right}` |
| KDiff3 | `C:\Program Files\KDiff3\kdiff3.exe` | `{left} {right}` | `{base} {left} {right}` |
| WinMerge | `C:\Program Files\WinMerge\WinMergeU.exe` | `{left} {right}` | `{left} {right} {base}` |
| VS Code | `code` | `--diff {left} {right}` | N/A (2-way only) |

#### [MODIFY] [registry_panel.py](file:///c:/Git/AIPromptManager/src/ui/registry_panel.py)

- Add context menu: "Compare Selected..." (enabled for 2-3 files)
- Launch compare dialog

#### [MODIFY] [main_window.py](file:///c:/Git/AIPromptManager/src/ui/main_window.py)

- Add Settings menu: File → Settings → Configure Merge Tool...

---

## Verification Plan

### Automated Tests

- `test_archive_restore.py`: Archive/restore file operations
- `test_move_skills.py`: Move operations
- `test_h1_edit.py`: H1 insert/replace logic
- `test_compare_dialog.py`: Role assignment logic

### Manual Verification

- Test archive/restore cycle with multi-select
- Test H1 edit with files with/without frontmatter
- Test merge tool launch with configured tools

---

## Execution Order

| Phase | Description | Branch Name |
|-------|-------------|-------------|
| 1 | `SkillStatus.ARCHIVED` + archive/restore in service | `feature/archive-restore-service` |
| 2 | Archive UI in registry_panel | `feature/archive-restore-ui` |
| 3 | Move feature (service + dialog + UI) | `feature/move-to-folder` |
| 4 | H1 edit in Quick View | `feature/quickview-h1-edit` |
| 5 | Settings infrastructure + dialog | `feature/settings-dialog` |
| 6 | Compare dialog + merge tool launch | `feature/compare-merge-tool` |
