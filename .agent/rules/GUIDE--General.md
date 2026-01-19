---
trigger: model_decision
---

# 📄 **GUIDE-General.md** General Communication & Documentation Standards

## Document History

- 1.0 — 2025-10-12 — Initial general standards document.  
- 1.1 - 2025-11-08 - removed response structure and artifact selection menu. They are part of the space prompts now

## Content Structure Requirements

**Mantra: Simple, clean, working. Expand if needed.** 🔥

### Organization & Readability

- Use clear headers and logical section breaks
- Apply bullet points and minimal bolding for key concepts
- Create visual breaks for better readability (ADHD-friendly)
- Keep content concise; avoid fluff
- Break complex ideas into digestible chunks

### Examples & Explanations

- Provide 3 different examples for each concept when possible
- Use real-life analogies and anecdotes
- Include visual comparisons for abstract concepts
- Offer step-by-step implementation strategies

## Code Presentation Standards

### General Rules

- Always provide complete, working code blocks with proper syntax highlighting
- Include necessary using statements at the top of each code block
- New classes: Specify folder path and file name with each addition

### Full vs Partial Code

- Full code files must be labeled: `// ✅ FULL FILE VERSION`
- Partial code must include: `# ⚠️ PARTIAL CODE SNIPPET - Ask for complete file`

### **Code Modification Format**

#### **Core Rules**

- **Always label** Full code files: with`// ✅ FULL FILE VERSION`
- **Partial code** must include: `# ⚠️ PARTIAL CODE SNIPPET - Ask for complete file`
- Use **emoji markers**: ✅ NEW, ❌ REMOVE, 🔄 MODIFY
- Identify changes by **method/property names** + **"Search for"** patterns

#### **Multi-Change Strategy**

- Show changes **separately** with context (user requests full file for copy-paste)
- Avoid full files in initial response to conserve tokens

#### **Emoji Reference**

✅ NEW | ❌ REMOVE | 🔄 MODIFY | ⚠️ PARTIAL

### Additional Code Modification info

*"See PROMPT-Code-Modification-Format.md if attached, for detailed examples"*

## Testing Focus Areas

- Unit testing patterns and best practices
- Integration testing strategies and boundaries
- UI automation frameworks and patterns
- Test data management and mocking
- Test architecture and maintainability
- Use framework-appropriate element access patterns in tests

## Quality Assurance

- Always review the question before responding and keep answers targeted
- Ensure all elements create a cohesive reading experience with consistent style
- Prefer project-specific instructions over generic guidance

## Environment & Troubleshooting

### Terminal & Execution

- **PowerShell Hanging in VS Code**: If `cmd.exe` or terminal commands hang during test execution, switch the VS Code default terminal profile to **PowerShell**. This resolves IO blocking issues with cmd.exe.

#### Resolution / Workaround

**Switch the default terminal profile to PowerShell.**

Steps:

1. Open VS Code Terminal.
2. Click the dropdown arrow next to the `+` icon.
3. Select **"Select Default Profile"**.
4. Choose **"PowerShell"**.
5. Restart VS Code or kill existing terminals.
