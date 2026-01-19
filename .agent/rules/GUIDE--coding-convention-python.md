---
trigger: model_decision
---

# Python Coding Conventions & Standards for Desktop Applications

---

## Document History

- **1.0** (2026-01-11): Initial Python coding standards for AiPrompts AssetManager project

---

## Purpose & Scope

This guide defines Python development standards for desktop applications in the AiPrompts ecosystem, focusing on clean architecture, strict typing, and structured logging.

**Target Platform:** Python 3.10+ desktop applications (Windows primary, cross-platform compatible)

**Key Technologies:** customtkinter (UI), structlog (logging), pytest (testing)

---

## Language & Framework

- **Language:** Python 3.10+ (modern type hints with `|` union syntax)
- **Style Guide:** PEP-8 with Black formatter defaults
- **UI Framework:** customtkinter for modern desktop interfaces
- **Logging:** structlog for structured logging to SEQ
- **Testing:** pytest with NUnit-style test organization
- **Principles:** SOLID, Repository pattern, Service layer abstraction

---

## Testing Standards

- **Framework:** pytest
- **Assertions:** Native Python assertions (pytest introspection)
- **Mocking:** unittest.mock or pytest-mock
- **Strategy:** 
  - Unit tests for services and business logic
  - Integration tests for file I/O and external dependencies
  - Use `tmp_path` fixture for filesystem testing
  - Mock external services and UI components

**Required imports template:**

```python
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
```

### Testing Services

```python
import pytest
from pathlib import Path
from services.registry_service import RegistryService

@pytest.fixture
def mock_registry_path(tmp_path: Path) -> Path:
    """Create a temporary registry.json for testing."""
    registry = tmp_path / "registry.json"
    registry.write_text('{"ingredients": {}}')
    return registry

def test_add_ingredient_success(mock_registry_path: Path) -> None:
    """Test adding a new ingredient to registry."""
    # Arrange
    service = RegistryService(mock_registry_path)
    ingredient_path = mock_registry_path.parent / "GUIDE-2-0-logging.md"
    ingredient_path.write_text("# Logging Standards")
    
    # Act
    service.add_ingredient("logging", ingredient_path)
    
    # Assert
    assert "logging" in service.get_all_ingredients()

def test_add_duplicate_raises_error(mock_registry_path: Path) -> None:
    """Test that duplicate ingredients raise ValueError."""
    service = RegistryService(mock_registry_path)
    ingredient_path = mock_registry_path.parent / "GUIDE-2-0-logging.md"
    ingredient_path.write_text("# Logging")
    
    service.add_ingredient("logging", ingredient_path)
    
    with pytest.raises(ValueError, match="already exists"):
        service.add_ingredient("logging", ingredient_path)
```

---

## Logging Standards

> **Unified structlog patterns** for Python projects

### Python-Specific Notes

- Use `structlog` for all logging (not built-in `logging` module)
- Configure JSON rendering for SEQ ingestion
- Use structured context binding for operation tracking
- Log to console (dev) and SEQ (if available) with graceful fallback

### Configuration

```python
import structlog
from structlog.processors import JSONRenderer

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()
```

### Usage Patterns

```python
# Structured logging with context
logger.info(
    "ingredient_added",
    ingredient_name="logging",
    file_path="core/GUIDE-2-0-logging.md",
    version="2.0"
)

# Bind context for multiple operations
log = logger.bind(operation="build_agent", config_path=str(config_file))
log.info("build_started", ingredient_count=5)
# ... operations ...
log.info("build_completed", files_copied=5)

# Error logging with exception info
try:
    registry.add_ingredient(name, path)
except ValueError as e:
    logger.error(
        "invalid_ingredient",
        ingredient_name=name,
        error=str(e),
        exc_info=True
    )
```

---

## Naming Conventions

### General Rules

- **Modules/Packages:** `snake_case` (e.g., `registry_service.py`, `json_repository.py`)
- **Classes:** `PascalCase` (e.g., `RegistryService`, `Ingredient`)
- **Functions/Methods:** `snake_case` (e.g., `add_ingredient`, `get_all_items`)
- **Variables:** `snake_case` (e.g., `ingredient_path`, `user_name`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `MAX_FILE_SIZE`, `DEFAULT_REGISTRY_PATH`)
- **Private members:** Prefix with single underscore (e.g., `_internal_method`, `_cache`)
- **Type variables:** `PascalCase` with `T` suffix (e.g., `ItemT`, `ConfigT`)

### Project Structure

```
AssetManager/
├── main.py                  # Entry point
├── ui/
│   ├── __init__.py
│   ├── main_window.py       # Main application window
│   └── panels/
│       ├── registry_panel.py
│       └── build_panel.py
├── services/
│   ├── __init__.py
│   ├── registry_service.py  # Business logic
│   └── agent_builder.py
├── repositories/
│   ├── __init__.py
│   └── json_repository.py   # File I/O abstraction
├── models/
│   ├── __init__.py
│   ├── ingredient.py        # Data classes
│   └── agent_config.py
└── tests/
    ├── conftest.py
    ├── test_registry_service.py
    └── test_agent_builder.py
```

---

## Type Hints (CRITICAL)

**Strict typing required** for all public APIs. Python 3.10+ allows modern union syntax.

### Core Rules

1. Use `from __future__ import annotations` for forward references
2. Prefer built-in generics: `list[str]`, `dict[str, Any]` (not `typing.List`, `typing.Dict`)
3. Use `Path` from `pathlib` instead of `str` for file paths
4. Mark optional returns explicitly: `str | None` (not implicit)
5. Use `Any` sparingly and document when unavoidable

### Examples

```python
from __future__ import annotations
from pathlib import Path
from typing import Any

# ✅ GOOD - Explicit types
def get_ingredient(name: str) -> dict[str, Any] | None:
    """Retrieve ingredient metadata from registry."""
    ...

class Registry:
    def __init__(self, path: Path) -> None:
        self._data: dict[str, dict[str, Any]] = {}
    
    def add_ingredient(self, name: str, file_path: Path) -> None:
        ...
    
    def list_ingredients(self) -> list[str]:
        return list(self._data.keys())

# ❌ BAD - No type hints
def get_ingredient(name):
    ...
```

### Type Checking

Run `mypy` in strict mode:

```bash
mypy --strict src/
```

---

## Docstrings

Use **Google-style docstrings** for all public classes and functions.

### Format

```python
def extract_h1_heading(markdown_path: Path) -> str:
    """Extract the first H1 heading from a markdown file.
    
    Args:
        markdown_path: Absolute path to the .md file
        
    Returns:
        The H1 heading text (without the '#' prefix)
        
    Raises:
        FileNotFoundError: If markdown_path doesn't exist
        ValueError: If no H1 heading found in file
    """
    if not markdown_path.exists():
        raise FileNotFoundError(f"File not found: {markdown_path}")
    
    content = markdown_path.read_text(encoding="utf-8")
    # ... implementation ...
```

### Class Documentation

```python
class RegistryService:
    """Manages ingredient registry operations.
    
    This service provides CRUD operations for the registry.json file,
    including versioning support and validation.
    
    Attributes:
        registry_path: Path to the registry.json file
    """
    
    def __init__(self, registry_path: Path) -> None:
        """Initialize the registry service.
        
        Args:
            registry_path: Path to registry.json
            
        Raises:
            FileNotFoundError: If registry_path doesn't exist
        """
        self.registry_path = registry_path
```

---

## Import Organization

Group imports in three sections: standard library, third-party, local.

```python
# Standard library
import json
import logging
from pathlib import Path
from typing import Any

# Third-party
import structlog
from customtkinter import CTk, CTkButton

# Local
from models.ingredient import Ingredient
from services.registry_service import RegistryService
```

**Rules:**
- Alphabetize within each group
- Avoid wildcard imports (`from module import *`)
- Use absolute imports for clarity
- Prefer explicit imports over importing entire modules

---

## Error Handling

### Three-Tier Strategy

1. **Validation:** Early checks at function boundaries
2. **Business Logic:** Service-layer exceptions with context
3. **UI:** User-friendly error dialogs

```python
# Service layer
class RegistryService:
    def add_ingredient(self, name: str, file_path: Path) -> None:
        """Add an ingredient to the registry.
        
        Raises:
            FileNotFoundError: If file_path doesn't exist
            ValueError: If ingredient name already exists
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Ingredient file not found: {file_path}")
        
        if name in self._registry.ingredients:
            raise ValueError(f"Ingredient '{name}' already exists")
        
        # ... operation ...

# UI layer
def on_add_clicked(self) -> None:
    """Handle add button click."""
    try:
        self._service.add_ingredient(name, path)
        messagebox.showinfo("Success", "Ingredient added!")
    except FileNotFoundError as e:
        messagebox.showerror("File Not Found", str(e))
    except ValueError as e:
        messagebox.showerror("Invalid Input", str(e))
```

### Best Practices

- **Fail fast:** Validate inputs early
- **Contextual exceptions:** Include relevant data in error messages
- **Never swallow exceptions silently**
- **Log before raising:** Use structured logging for debugging

---

## File I/O Conventions

**Always use `Path` objects** from `pathlib`.

```python
from pathlib import Path

# ✅ GOOD
def copy_ingredient(src: Path, dest: Path) -> None:
    """Copy ingredient file to destination."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(src.read_text(encoding="utf-8"))

# ❌ BAD
def copy_ingredient(src: str, dest: str) -> None:
    ...
```

### Error Handling for I/O

```python
try:
    content = ingredient_path.read_text(encoding="utf-8")
except FileNotFoundError:
    logger.error("ingredient_not_found", path=str(ingredient_path))
    raise
except PermissionError:
    logger.error("permission_denied", path=str(ingredient_path))
    raise
except UnicodeDecodeError:
    logger.error("encoding_error", path=str(ingredient_path))
    raise
```

---

## Coding Style

### Black Formatter Defaults

- **Line length:** 88 characters (Black default)
- **Indentation:** 4 spaces (no tabs)
- **Quotes:** Double quotes for strings (Black default)
- **Trailing commas:** Required for multi-line collections

### Code Organization

```python
# One public type per file
# Internal helpers can be co-located when tightly coupled

class RegistryService:
    """Main service class."""
    
    def __init__(self, path: Path) -> None:
        self._path = path
        self._cache: dict[str, Any] = {}
    
    # Public methods first
    def add_ingredient(self, name: str, path: Path) -> None:
        """Public API."""
        self._validate_name(name)
        self._write_to_registry(name, path)
    
    # Private methods after
    def _validate_name(self, name: str) -> None:
        """Internal validation."""
        if not name:
            raise ValueError("Name cannot be empty")
    
    def _write_to_registry(self, name: str, path: Path) -> None:
        """Internal I/O operation."""
        ...
```

### Nullability

- Enable type checking with strict mode
- Use `| None` for optional values
- Never return `None` implicitly - declare it in return type

---

## Dependency Management

- Use **constructor injection** for services and repositories
- **Abstract external dependencies** (filesystem, network, UI) with interfaces
- Keep third-party libraries **behind abstractions** for testability
- Avoid global state and singletons

```python
class AgentBuilder:
    """Builds .agent folders from registry."""
    
    def __init__(
        self,
        registry_service: RegistryService,
        file_repository: FileRepository
    ) -> None:
        """Initialize with injected dependencies.
        
        Args:
            registry_service: Service for registry operations
            file_repository: Repository for file I/O
        """
        self._registry = registry_service
        self._files = file_repository
```

---

## Async/Await (If Needed)

For I/O-bound operations in future phases:

```python
import asyncio
from pathlib import Path

async def load_large_file_async(path: Path) -> str:
    """Load file asynchronously.
    
    Args:
        path: Path to file
        
    Returns:
        File contents
    """
    # Use asyncio.to_thread for blocking I/O
    content = await asyncio.to_thread(path.read_text, encoding="utf-8")
    return content
```

**Rules:**
- Suffix async functions with `_async`
- Never block the event loop with synchronous I/O
- Use `asyncio.to_thread()` for CPU-bound work

---

## Data Classes

Use `@dataclass` for simple data containers:

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Ingredient:
    """Represents a single ingredient in the registry."""
    name: str
    path: Path
    description: str = ""  # Auto-extracted from H1
    version: str = "1.0"
    
    def __post_init__(self) -> None:
        """Validate after initialization."""
        if not self.path.exists():
            raise FileNotFoundError(f"Path not found: {self.path}")
```

**When to use:**
- Data transfer objects (DTOs)
- Configuration containers
- Model objects without complex behavior

**When NOT to use:**
- Services with business logic
- Classes with many methods
- Objects requiring complex initialization

---

## Mantra

**"Clean architecture, clear errors, comprehensive logging. Type everything strictly. Build simple, then expand if needed."** 🐍🔥

**Development Philosophy:**
- **SOLID over clever:** Prefer clear separation over terse code
- **Fail loudly:** Raise exceptions early with context
- **Log everything:** Structured logs are debugging superpowers
- **Test business logic:** Services and repositories must have tests
- **Iterate UI:** Build minimal viable interface first

---

## Appendix: Quick Checklist

### Code Reviews

- [ ] All public functions have type hints
- [ ] Google-style docstrings for public APIs
- [ ] Imports organized (stdlib → third-party → local)
- [ ] Exceptions carry context
- [ ] Structured logging used with operation context
- [ ] Tests added for new business logic
- [ ] `Path` objects used for file paths (not `str`)
- [ ] Black formatter applied
- [ ] mypy strict mode passes

### Releases

- [ ] All tests pass (`pytest tests/`)
- [ ] Type checking passes (`mypy --strict src/`)
- [ ] Code formatted (`black src/ tests/`)
-[] SEQ dashboard queries updated (if logging changed)

---

**"Type safe, test driven, log structured. Keep Python clean and explicit."** 🚀
