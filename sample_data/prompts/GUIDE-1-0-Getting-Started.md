---
version: "1.0"
type: GUIDE
---

# Getting Started with AIPromptManager

This guide helps you understand how to use AIPromptManager to manage your AI prompt library.

## What is AIPromptManager?

AIPromptManager is a desktop application built with Python and Tkinter that helps you:

- **Organize** your AI prompts in a centralized registry
- **Select** which prompts to include in different projects
- **Build** agent configuration files automatically
- **Manage** versions and visibility of prompts

## Quick Start

### 1. Run the Application

```bash
python src/main.py
```

The application will launch using the `sample_data` directory by default.

### 2. Explore the Knowledge Base

The **Knowledge Base** tab shows all available prompts:

- **Filter**: Type in the filter box to search by name or path
- **Sort**: Click column headers to sort
- **Show/Hide**: Right-click items to toggle visibility
- **Quick View**: Right-click → Quick View to preview content

### 3. Create a Profession

The **Profession Designer** tab lets you select prompts for a project:

- **Available** list shows all enabled prompts
- **Selected** list shows chosen prompts
- Use arrow buttons to move items between lists
- Drag and drop to reorder selected items

### 4. Build Agent Configuration

The **Agent Onboarding** tab generates the final output:

- Select a profession config file (JSON)
- Choose an output directory
- Click **Build Agent** to create `.agent/rules/` folder
- The tool will sync files and detect conflicts

## Tips

- Hidden prompts (greyed out in Knowledge Base) won't appear in Profession Designer
- Use the "Show Hidden" toggle to see all items
- Right-click on items for context actions (Show in Explorer, Open with Editor)

## Next Steps

- Create your own prompts in the `sample_data/prompts/` folder
- Modify `conventions.json` to customize naming patterns
- Point the tool at your own prompt library using `--data-dir`

For more details, see the comprehensive documentation in `.doc/README-AIPromptManager.md`.
