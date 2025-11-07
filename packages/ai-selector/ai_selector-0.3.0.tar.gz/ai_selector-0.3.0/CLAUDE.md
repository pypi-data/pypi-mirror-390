# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`ai-selector` is an interactive CLI tool for managing and executing multiple AI agents. Each agent is isolated in its own directory with separate dependencies and configuration. The project uses Python >=3.13 and is managed with `uv`.

**Agent Discovery**: Agents are automatically discovered by scanning for `.env` files in subdirectories of `AI_AGENTS_DIR`.

### Key Features
- Automatic agent discovery via `.env` files
- Interactive CLI menu using questionary
- Branded logo display with ANSI color support
- Agent commands configured via `ALIAS` variable in each agent's `.env`
- Environment variable support for agent directory location
- Automatic loading of agent-specific environment variables
- Execution from current directory (does not change to agent directory)
- Full interactive execution (stdin/stdout/stderr passthrough)
- Screen clearing before agent execution
- Execution logging to `agent-execution.log` in each agent's directory

## Development Commands

### Package Management
- `uv sync` - Install/sync dependencies from pyproject.toml
- `uv add <package>` - Add a new dependency
- `uv remove <package>` - Remove a dependency

### Running the Application
- `uv run main.py` - Execute the AI agent selector
- `uv run --project /path/to/ai-selector main.py` - Execute from any directory (use `--project` not `--directory`)
- First-time setup: `cp .env.example .env` and configure AI_AGENTS_DIR
- Each agent needs a `.env` file with an `ALIAS` variable

**Important**: When creating an alias or script to run ai-selector, use `--project` instead of `--directory`:
```bash
alias ai-selector='uv run --project /path/to/ai-selector /path/to/ai-selector/main.py'
```
This ensures the agent executes in your current working directory, not in the ai-selector project directory. Note that you must specify the full path to main.py as the second argument.

### Testing and Quality Assurance
The project uses a comprehensive testing and quality assurance setup:

**Quick Commands (using justfile):**
- `just test` - Run the full test suite (28 tests)
- `just lint` - Run ruff linter and formatter
- `just qa` - Run complete quality assurance (lint + type check + tests)

**Manual Commands:**
- `uv run pytest` - Run tests with pytest
- `uv run pytest --cov` - Run tests with coverage report
- `uv run ruff check .` - Check code with ruff linter
- `uv run ruff format .` - Format code with ruff
- `uv run mypy .` - Type check with mypy

**Pre-commit Hooks:**
The project uses pre-commit hooks that automatically run on every commit:
- Trailing whitespace removal
- End-of-file fixer
- YAML validation
- Ruff linting and formatting
- Mypy type checking

Install hooks: `pre-commit install`

**Test Structure:**
- `tests/test_config.py` - Tests for agent discovery and configuration (8 tests)
- `tests/test_selector.py` - Tests for interactive selection UI (6 tests)
- `tests/test_executor.py` - Tests for agent execution (8 tests)
- `tests/test_main.py` - Tests for main entry point (6 tests)

**Code Quality Standards:**
- Line length: 88 characters (ruff default)
- Type hints required for all function definitions (mypy strict mode)
- Docstrings required for public modules, classes, and functions
- Import sorting enforced (ruff isort)
- All tests must pass before commit (pre-commit hook)

## Architecture

### Module Structure

**Testing Philosophy:**
- All modules have comprehensive test coverage
- Tests use pytest with fixtures for setup/teardown
- Mocking is used extensively to isolate components
- Tests validate both success and error paths
- Type checking ensures runtime safety

**`main.py`** - Entry point that orchestrates the selection flow:
1. Discovers agents by scanning for `.env` files in `AI_AGENTS_DIR`
2. Presents interactive selection menu
3. Executes selected agent with its environment variables

**`src/config.py`** - Agent discovery and configuration:
- `Agent` dataclass: Represents an AI agent with name, command, env_vars, and env_file path
- `discover_agents()`: Scans AI_AGENTS_DIR for subdirectories containing `.env` files with `ALIAS`
- `get_agents_directory()`: Resolves AI_AGENTS_DIR from environment variable
- Type-safe with strict mypy checking; uses `cast()` to ensure proper type narrowing

**`src/selector.py`** - Interactive CLI:
- `display_logo()`: Displays the branded logo from `logo.txt` (ANSI colors supported)
- `select_agent()`: Presents questionary menu with agent names (sorted alphabetically)
- Custom styling for better UX
- Returns selected Agent or None if cancelled
- Logo is displayed before the agent selection menu with spacing for visual separation

**`src/executor.py`** - Agent execution:
- `clear_screen()`: Clears the terminal screen (platform-aware)
- `log_execution()`: Writes execution details to `agent-execution.log` in agent's directory
- `execute_agent()`: Main execution function that:
  1. Captures current working directory
  2. Logs execution details with timestamp
  3. Clears the screen
  4. Displays execution info
  5. Runs agent command with `shell=True` in **current directory**
  6. Merges agent's environment variables into process environment
  7. Inherits stdin/stdout/stderr for full interactivity

### Agent Configuration

Each agent is defined by its `.env` file located in `AI_AGENTS_DIR/<agent-name>/.env`:

```bash
# ALIAS: Command to execute (REQUIRED)
ALIAS=npx @anthropic-ai/claude-code

# Additional environment variables (OPTIONAL)
ANTHROPIC_API_KEY=sk-...
DEBUG=true
```

The `ALIAS` variable is extracted as the command; all other variables are loaded into the agent's execution environment.

### Selector Configuration

**`.env`** in the selector's root directory:
```bash
AI_AGENTS_DIR=~/ia  # Path to directory containing agent folders
```

### Agent Directory Structure

Expected structure in `AI_AGENTS_DIR`:
```
~/ia/
├── claude-code/
│   ├── .env                    # MUST contain ALIAS variable
│   ├── agent-execution.log     # Generated automatically on each run
│   ├── node_modules/
│   ├── package.json
│   └── ...
├── crush/
│   ├── .env                    # MUST contain ALIAS variable
│   ├── agent-execution.log     # Generated automatically on each run
│   ├── node_modules/
│   └── ...
```

**Only directories with `.env` files containing `ALIAS` are detected as agents.**

### Execution Logging

Each agent execution is logged to `agent-execution.log` in the agent's directory with:
- Timestamp (YYYY-MM-DD HH:MM:SS)
- Agent name
- Command executed
- Directory from which selector was run
- Environment variables loaded

Log entries are appended, creating a history of all executions.

## Important Implementation Notes

- Agent discovery is automatic - no manual configuration file needed
- Commands are executed with `shell=True` to support shell syntax
- Working directory is **NOT** changed - commands execute from current directory
- Agent .env variables are merged into execution environment
- Exit codes are properly propagated from agent processes
- KeyboardInterrupt (Ctrl+C) returns exit code 130
- Agents are sorted alphabetically in the selector menu
- Logo is displayed from `logo.txt` in project root (optional, gracefully skipped if missing)
- Logo supports ANSI escape codes for colored terminal output

## Development Workflow

**Before committing:**
1. Run `just qa` to ensure all quality checks pass
2. Pre-commit hooks will automatically run on `git commit`
3. If hooks fail, fix issues and re-stage changes
4. All 28 tests must pass

**Adding new features:**
1. Write tests first (TDD approach recommended)
2. Implement the feature
3. Ensure type hints are complete
4. Run `just qa` to validate
5. Update CLAUDE.md if architecture changes

**Code style:**
- Use type hints for all function parameters and return values
- Write descriptive docstrings (Google style)
- Keep functions focused and testable
- Mock external dependencies in tests
- Use `tmp_path` fixture for file system operations in tests
