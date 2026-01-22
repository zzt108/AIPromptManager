# AIPromptManager

> Teaching-focused Python tool for managing AI prompt libraries

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## 📖 Documentation

See [.doc/README-AIPromptManager.md](.doc/README-AIPromptManager.md) for comprehensive documentation including architecture diagrams, use cases, and detailed feature descriptions.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/zzt108/AIPromptManager.git
cd AIPromptManager

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -e .

# Run with sample data
python src/main.py

# Or point to your own prompt library
python src/main.py --data-dir c:\Path\To\YourPrompts
```

## ✨ Features

- **Knowledge Base** panel with filtering, sorting, and visibility toggles
- **Profession Designer** for visual skill selection using Available/Selected lists
- **Agent Onboarding** builder for generating `agent.config.json` files
- **Intelligent Metadata Extraction** from filename patterns, H1 headings, or YAML frontmatter
- **Status Indicators** (✓/⚠️/❌) showing file validity and parse status
- **YAML Support** for `.yaml` and `.yml` skill files
- **File Sync** with bidirectional change detection and conflict resolution dialogs
- **Archive/Restore** management for deprecated or unused skills (with structure preservation)
- **Compare Tool** integration for diffing skill versions (supports P4Merge, KDiff3, WinMerge, VS Code)
- **Move Files** organization into subfolders via context menu
- **Context Menu** actions: Quick View, Show in Explorer, Open with Editor, Open with Notepad, Move to Folder

## 🏗️ Architecture

AIPromptManager uses clean architecture with separation of concerns:

- **Models**: Data structures (Skill, RegistrySchema, AgentConfig)
- **Repositories**: Data persistence (JSON file operations)
- **Services**: Business logic (RegistryService, AgentBuilder)
- **UI**: Tkinter-based desktop interface

See [.doc/architecture.md](.doc/architecture.md) for detailed diagrams.

### Repository Separation

![Repository Separation](http://www.plantuml.com/plantuml/png/VOunJyCm48Lt_ufJfZAqtHbGAn0I0wW32q8Cr_YIc3e-w-uYL27-EsuJIf40J-_vVVVqLceeDlJHwIwaZ88zRB7UjS93yjSSMU2j2qPdkQS6XsYtdEm1UuAr18pEvNA6BK6rlji8zzdkCHKlC7jaZXSLl3iextcpjuuJh7EEeKOBd5x6GALUJj98JOlvEAjzua76OeNP3HgUAXkEdWIgFARB2b1XCZ-0HSsf2Uq8ZFgO-zAsHIMeXDgW9ll5gt8wOby_Xos_ROVv_Ee4mMMHwFLlSffLGAqn_GEEymetAAbpYOr0GjiPSFCz2WfxM3_tGI1pIAMw8o57oSFXngsA6lhu2G00)

### Application Architecture

![Application Architecture](http://www.plantuml.com/plantuml/png/TLDDRzim3BtxLmW-RHqoODSTXcB33WNQeLZsSHHecR65q690CSwoelzzSg2uYfUU7BxtcFT4KRTHGNG_K1MtFkn0O30xS5leSAr7GYFe5497M0W63knwuG6DoXwhAdUO-kUTkOSZIcsUAcCSGOpc0NpuxKFBXnDep3iJMB5XtfgFHdNx_bikColO-QXoj3i8I4dpFGEFKvr5ZiF6TxFaowai1StUKplpdwUgf2q7gz1OrqFei7tpDk7FrHpwmdBEhOAOC_yGnD7Z8JCRJufYCQIUhFWw_SvqxFbWUz-s6Em8CWLY9eJm2sG-zKOmzfQIRqgJKoft7Q4TVVID9w_75ogog7LC-o4iqnVJcBF329wW8Jmvf0JtwTFmdtD297IAxNLs0Ys6r9v7LIJEvi_56gnHHk-ms8N5MC-2fyML5vUzTZqEKFe3qUnzDL14jJvqWgt7y6fUcysAKGQM0SZ_HQl77Luvq0EtIFyVvsusUrbj6AOLYIePIFzu2Un0-mGyfaz6V3ndJNZ3J1aVKQBdaBjpfk8vtQnMYxUn8CjNSRdHgzMdvMLKXVeglwXD_Q4-kTGtTJ69wXP3kn_e7m00)

## 🛠️ Technology Stack

- **Python 3.10+** with strict type hints
- **Tkinter** for native cross-platform UI
- **structlog** for structured logging
- **pytest** for testing (201 tests, 100% pass rate)
- **mypy** for strict type checking (0 errors)

## 📦 Sample Data

The repository includes `sample_data/` with example prompts to demonstrate functionality. This serves as:

- **Working Demo**: Run the application immediately without setup
- **Template**: Starting point for creating your own prompt library

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

Apache License 2.0 - see [LICENSE](LICENSE) for details.

## 🔗 Links

- **Repository**: <https://github.com/zzt108/AIPromptManager>
- **Issues**: <https://github.com/zzt108/AIPromptManager/issues>
- **Documentation**: [.doc/README-AIPromptManager.md](.doc/README-AIPromptManager.md)
