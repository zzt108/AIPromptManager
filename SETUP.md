# AIPromptManager Setup

## 1. Create Virtual Environment

```cmd
cd AIPromptManager
python -m venv .venv
```

## 2. Activate Virtual Environment

```cmd
.venv\Scripts\activate
```

## 3. Install Dependencies

```cmd
pip install -e .
pip install -e ".[dev]"
```

## 4. VS Code Configuration

Create `.vscode/settings.json` in the project root folder with:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python.exe",
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "python.testing.pytestArgs": ["tests"],
    "python.linting.mypyEnabled": true,
    "python.linting.enabled": true,
    "python.formatting.provider": "black"
}
```

## 5. Verify Setup

```cmd
pytest --version
mypy --version
python --version
```

All should report their versions without errors.

## 6. Run Commands

**Run tests:**

```cmd
pytest tests/ -v
```

**Type check:**

```cmd
mypy --strict src/
```

**Format code:**

```cmd
black src/ tests/
```

---

## 7. Using VS Code Tasks (Recommended!) 🎯

Instead of typing commands, use VS Code's task runner:

**To run tasks:**

1. Press `Ctrl+Shift+P`
2. Type "Tasks: Run Task"
3. Choose from:
   - **pytest: Run All Tests** - Run all tests in tests/
   - **pytest: Run Current File** - Run tests in currently open file
   - **mypy: Type Check All** - Type check all of src/
   - **black: Format All Code** - Format src/ and tests/

**Keyboard shortcut:**

- `Ctrl+Shift+B` - Opens task menu

**Or use Terminal menu:**

- Click `Terminal` → `Run Task...` → Select task

All tasks use full paths to `.venv\Scripts\pytest.exe`, etc., so they work regardless of PATH issues! ✅
