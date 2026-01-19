---
description: Analyze staged changes and generate a conventional commit message and branch name
---

# Generate a conventional commit message

1. Run the following command to get the current staged changes:

   ```bash
   git diff --cached
   ```

2. **Analyze the output.**
   - If the output clearly shows the diffs, proceed to step 3.
   - **CRITICAL FAIL-SAFE:** If the command fails, returns empty output, or you are unsure:
     a. Run `git status` to retrieve the list of modified/staged files.
     b. Use `view_file` to inspect the *actual content* of these files.
     c. **NEVER** guess the changes based on conversation history. You MUST verify the actual changes on disk before generating the message.

3. Generate a response using the following template and rules:

    Analyze the Git changes and provide in English a concise, descriptive commit message that explains the purpose and impact of these changes.
    Ignore all white space changes. Focus on the 'what' and 'why' rather than the 'how'. Include any relevant issue numbers or references.
    Propose a meaningful git branch name based on current changes and the versioning conventions.

    Format the response as a conventional commit message following these strict formatting rules.
    **CRITICAL:** You MUST wrap the final output in a markdown code block (```) so that the formatting characters (+, -) are preserved and not rendered as bullets.

    **FORMAT REQUIREMENTS:**
    - fence answer in ```asciidoc
    - Subject line: max 50 chars (conventional format: type(scope): description)
    - No empty lines before first dash
    - Body: bullet points starting with plus and space (+ )
    - Line wrap: max 72 chars per line (break at word boundaries)
    - First bullet: TL;DR summary of overall purpose
    - Following bullets: specific changes with context
    - Use 2-space indentation for continuation lines
    - No empty lines between bullets

    **EXAMPLE OUTPUT:**

    ``` asciidoc
    Recommended branch name: feature-2-3-test-feedback-ui
    ---
    feat(test): improve test feedback and UI

    + TL;DR: Improves test result reporting, simplifies
      UI logic, and makes drag-and-drop tests more robust
      by removing reflection
    + Enhanced TestRunnerHandler to provide granular user
      feedback based on test exit codes (Success, Warning,
      Error) by replacing if-else with switch statement
    ```
