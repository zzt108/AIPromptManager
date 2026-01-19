# 🚀 Context Transfer: AiPrompts Asset Manager

**Date:** 2026-01-11  
**Phase:** 1 → 2 (Reorganization Complete, Build Tooling Next)

---

## 📍 Where We Are (Status)

- **Current Phase:** Phase 1 - Reorganize AiPrompts ✅ **COMPLETE**
- **Last Completed:** Semantic folder structure created and populated
- **In Progress:** Nothing (awaiting Phase 2 start)
- **Next Up:** Phase 2 - Build Tooling (`registry.json`, `AssetManager.py`)

---

## 📝 Task Status (`task.md` Snapshot)

```markdown
# AiPrompts Asset Manager - Phase 1 Implementation

## Phase 1: Reorganize AiPrompts ✅
- [x] Analyze current folder structure
- [x] Create new folder structure (`core/`, `platform/`, `workflows/`, `domain/`)
- [x] Copy files from `.agent/` to new locations
- [x] Move legacy folders (Work→domain/work, Private→domain/personal, Archive→archive)
- [x] Move `Private/Google` (was locked)
- [x] Verify all files copied correctly

## Phase 2: Build Tooling (NEXT)
- [ ] Create `registry.json` with initial mappings
- [ ] Create `global-instructions.md`
- [ ] Develop `AssetManager.py` (Python/tkinter or customtkinter)

## Phase 3: Client Integration (future)
- [ ] VecTool integration
```

---

## 🧠 Key Context & Decisions

### Architecture Goals
- **AiPrompts** = central prompt library, delivered via submodule
- **AssetManager.py** = Python UI tool for version management + build
- **`.agent/`** = build output target (Git-ignored in client projects)

### Phase 1 Decisions Made
1. **`.agent/` stays untouched** - it's Antigravity's config, COPY from it (don't move)
2. **`domain/` subdirs**: `personal/`, `work/`, `AIPrompts/`, project-specific folders
3. **`platform/` hierarchy**: Will have `python/` and `dotnet/` (with csharp/, winforms/, maui/, avalonia/, winui/)
4. **Naming convention**: `{TYPE}-{major}-{minor}-{topic}.md` (e.g., `GUIDE-2-0-logging.md`)
5. **`Configs/` stays at root** - infra files, not prompts

### New Folder Structure
```
AiPrompts/
├── core/                    # 8 universal GUIDEs
├── platform/
│   └── python/              # 1 Python GUIDE
├── workflows/               # 4 workflows (from .agent/workflows)
├── domain/
│   ├── personal/            # Games, Pplx, VecTool, Yi
│   ├── work/                # C#-LINX, C#-SFERA, work files
│   └── AIPrompts/           # SPACE-260111-AIPrompts-Python.md
├── Configs/                 # Stays (14 files)
└── archive/                 # Lowercase (was Archive/)
```

---

## 📂 Hot Files (To Open First)

- `c:\Git\AiPrompts\.doc\plans\PLAN-1-1-AiPrompts-AssetManager.md` - Master plan
- `c:\Git\AiPrompts\.doc\plans\PLAN-1-2-AiPrompts-Reorganization.md` - Phase 1 execution plan
- `c:\Git\AiPrompts\domain\AIPrompts\SPACE-260111-AIPrompts-Python.md` - Python standards for AssetManager
- `.agent/rules/GUIDE--coding-convention-python.md` - Python coding conventions

---

## 📋 Phase 2 Requirements

### 1. Create `registry.json`
Maps logical ingredient names to versioned files. Format:
```json
{
  "ingredients": {
    "logging": { "path": "core/GUIDE-2-0-logging.md" },
    "avalonia": { "path": "platform/dotnet/avalonia/GUIDE-3-0-conventions.md" },
    "global-instructions": { "path": "core/GUIDE-1-0-global-instructions.md" }
  }
}
```

### 2. Create `global-instructions.md`
Universal instructions that apply to all projects (must be explicit ingredient).

### 3. Develop `AssetManager.py`
Python UI application with:
- **Registry Management**: Add/edit/remove ingredients without manual JSON editing
- **Version Bumping**: Copy to new version OR update pointer to existing file
- **Build Agent**: One-click to populate `.agent/` from `agent.config.json`

Technology: Python with tkinter or customtkinter for UI.

---

## ⏭️ Prompt for Next Session

> "Continue AiPrompts Asset Manager implementation. **Phase 1 is complete** - we reorganized the repo into semantic folders (core/, platform/, workflows/, domain/).
> 
> **Start Phase 2**: Build the tooling layer:
> 1. Create `registry.json` to map ingredient names to file paths
> 2. Create `global-instructions.md` as a universal ingredient
> 3. Develop `AssetManager.py` - a Python UI tool for managing the registry and building `.agent/` folders
> 
> Reference the master plan at `PLAN-1-1-AiPrompts-AssetManager.md` and Python conventions at `domain/AIPrompts/SPACE-260111-AIPrompts-Python.md`."

---

## 🎯 Success Criteria for Phase 2

- [ ] `registry.json` created with initial mappings for all existing files
- [ ] `global-instructions.md` exists and is registered as an ingredient
- [ ] `AssetManager.py` runs and displays UI
- [ ] Can add/edit/remove registry entries via UI
- [ ] "Build Agent" button copies files to `.agent/` based on config

---

## 📊 Phase 1 Commit

**Branch:** `refactor-1-2-prompts-semantic-folders`

**Commit message:**
```
refactor(structure): reorganize to semantic folder layout

- TL;DR: Implements Phase 1 of Asset Manager plan -
  restructures repo into core/, platform/, workflows/,
  domain/ semantic folders for future tooling support
- Created core/ with 8 universal GUIDEs
- Created platform/python/ with Python coding conventions
- Created workflows/ by copying 4 workflow files
- Created domain/ with personal/, work/, AIPrompts/
- Moved legacy folders to new structure
- Added PLAN-1-2-AiPrompts-Reorganization.md
```
