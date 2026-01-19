---
description: Perform a gap analysis between planned requirements and current implementation
version: "1.0"
---

1. **Identify Relevant Plans:**
    * Search for active plan documents in `.documentation/plans/` (or `.agent/workflows/` for legacy plans).
    * Look for the most recent `PLAN-*.md` file relevant to the current work.

2. **Identify Relevant Code:**
    * Identify the key source files modified or created for this plan.
    * *Self-Correction:* If no files are explicitly provided, check `task.md` or `implementation_plan.md` to see what was recently worked on.

3. **Perform Analysis:**
    * Compare the **Success Criteria** and **Requirements** from the Plan against the **Current Implementation** in the code.

4. **Generate Report:**
    * Create a response using the template below.

    **TEMPLATE:**

    # 🕵️ Gap Analysis: [Plan Name/Version]

    ## 📊 Implementation Status

    | Requirement / Feature | Status | Implementation Details |
    | :-- | :-- | :-- |
    | [Req Name] | [✅/⚠️/❌] | [Brief description of what is built vs missing] |
    | ... | ... | ... |

    ## 🧶 Unimplemented / Missing

    * [List specific missing features or logic gaps]
    * [List missing tests or validation steps]

    ## 🌳 Proposed Git Branches

    * *Based on `GUIDE--Plan-Phase-Versioning.md`*
    * `[branch-name]` - [Description of work covering the gap]

    ## 🏗️ Visualization (PlantUML)

    *Create a PlantUML diagram illustrating the current implementation state vs. the target state.*

    ```plantuml
    @startuml
    skinparam backgroundColor white
    skinparam defaultFontName Arial
    skinparam shadowing false

    ' Use standard styles from GUIDE--Documentation-Visualization-Standards-PlantUML.md
    skinparam rectangle<<complete>> {
        BackgroundColor #c8e6c9
        BorderColor #1b5e20
        FontColor #1b5e20
        BorderThickness 2
    }
    
    skinparam rectangle<<missing>> {
        BackgroundColor #ffcdd2
        BorderColor #b71c1c
        FontColor #b71c1c
        BorderThickness 2
        
    }

    rectangle "✅ Implemented Feature" <<complete>>
    rectangle "❌ Missing Feature" <<missing>>

    @enduml
    ```
