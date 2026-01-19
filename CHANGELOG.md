# Changelog

All notable changes to AIPromptManager will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-19

### Initial Public Release

#### Features
- **Knowledge Base Panel** with sortable columns, filtering, and visibility toggles
- **Profession Designer** with Available/Selected list management for ingredients
- **Agent Onboarding** builder for generating `agent.config.json` files
- **Registry Management** with automatic scanning and metadata extraction
- **File Sync** with bidirectional timestamp comparison and conflict detection
- **Interactive Dialogs** for handling update available and local changes scenarios
- **Quick View** popups for inspecting ingredient contents
- **Context Menu** actions: Show in Explorer, Open with Default Editor
- **Visibility Management** with persistent state in registry.json
- **Multi-select Operations** for bulk hide/show actions
- **Teaching Paradigm** UI terminology (Knowledge Base, Profession Designer, Agent Onboarding)

#### Architecture
- Clean separation: Models, Repositories, Services, UI layers
- Full test coverage with pytest (81 tests)
- Strict type checking with mypy (0 errors)
- Structured logging with structlog
- Plain tkinter for cross-platform compatibility

#### Technical Details
- Python 3.10+ support
- Apache 2.0 license
- Command-line argument support (`--data-dir`)
- Sample data included for immediate demo capability

[1.0.0]: https://github.com/zzt108/AIPromptManager/releases/tag/v1.0.0
