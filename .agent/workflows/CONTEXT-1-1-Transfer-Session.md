---
description: Create a unified plan and context summary to continue work in a new conversation
version: "1.0"
---

1. **Analyze Current State:**
    * Review `task.md` to see completed vs. pending items.
    * Review the active Phase Plan (e.g., `PLAN-*.md`) to identify the current milestone.
    * Identify any uncommitted changes or active "work in progress".

2. **Gather Context:**
    * Identify crucial recent decisions, design changes, or rule updates (e.g., "We just switched to LogCtx").
    * List key files that are currently "hot" (being edited).

3. **Generate Transfer Document:**
    * Create a response using the template below. This document is designed to be copy-pasted into the *next* conversation's prompt.

    **TEMPLATE:**

    # 🚀 Context Transfer: [Project Name]

    ## 📍 Where We Are (Status)

    * **Current Phase:** [Phase Name/Version]
    * **Last Completed:** [Step X: Description]
    * **In Progress:** [Step Y: Description]
    * **Next Up:** [Step Z: Description]

    ## 📝 Task Status (`task.md` Snapshot)

    ```markdown
    [Insert copy of current task.md content]
    ```

    ## 🧠 Key Context & Decisions

    * **Frameworks:** [e.g., Avalonia 11, LogCtx, NUnit]
    * **Recent Changes:** [e.g., "Just finished refactoring MDHandler to use LogCtx"]
    * **Active Rules:** [Reference relevant .agent/rules files]

    ## 📂 Hot Files (To Open First)

    * `[Path/To/File1.cs]`
    * `[Path/To/File2.md]`

    ## ⏭️ Prompt for Next Session

    *(Copy and paste this into the new chat)*

    > "I am continuing work on [Phase Name]. We just completed [Step X] and are ready to start [Step Y].
    > Please review the attached `task.md` and the 'Hot Files' listed above.
    >
    > **Immediate Goal:** [Brief description of next task]"

    ## 🏗️ Visualization (Current State)

    *Create `PlantUML` diagram(s) showing the current architectural state or workflow status.*
    this should be a standalone md document in .doc folder with plantuml diagrams
