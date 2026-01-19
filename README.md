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
- **Profession Designer** for visual ingredient selection using Available/Selected lists
- **Agent Onboarding** builder for generating `agent.config.json` files
- **Registry Management** with automatic metadata extraction from markdown files
- **File Sync** with bidirectional change detection and conflict resolution dialogs
- **Context Menu** actions: Quick View, Show in Explorer, Open with Editor

## 🏗️ Architecture

AIPromptManager uses clean architecture with separation of concerns:

- **Models**: Data structures (Ingredient, RegistrySchema, AgentConfig)
- **Repositories**: Data persistence (JSON file operations)
- **Services**: Business logic (RegistryService, AgentBuilder)
- **UI**: Tkinter-based desktop interface

See [.doc/architecture.md](.doc/architecture.md) for detailed diagrams.

## 🛠️ Technology Stack

- **Python 3.10+** with strict type hints
- **Tkinter** for native cross-platform UI
- **structlog** for structured logging
- **pytest** for testing (81 tests, 100% pass rate)
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

- **Repository**: https://github.com/zzt108/AIPromptManager
- **Issues**: https://github.com/zzt108/AIPromptManager/issues
- **Documentation**: [.doc/README-AIPromptManager.md](.doc/README-AIPromptManager.md)
