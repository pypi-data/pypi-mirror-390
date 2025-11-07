# Interactive task selector (uses gum if available, falls back to list)
_default:
    #!/usr/bin/env bash
    set -euo pipefail
    if ! command -v gum &> /dev/null; then
        just --list
        echo ""
        echo "💡 Tip: Install 'gum' for an interactive task selector."
        exit 0
    fi
    SELECTED=$(just --list --unsorted --list-heading "" | \
               sed 's/^[[:space:]]*//' | \
               gum choose --header "Select a task to run:" --height 15)
    if [[ -n "${SELECTED}" ]]; then
        TASK_NAME=$(echo "${SELECTED}" | awk '{print $1}')
        echo "Running: just ${TASK_NAME}"
        just "${TASK_NAME}"
    fi

# Run all QA tools (linting and testing)
qa: lint test

# Run linters (ruff and mypy)
lint:
    uv run ruff check .
    uv run mypy .

# Format the code
format:
    uv run ruff format .

# Run tests
test:
    uv run pytest

# Run the application
run:
    uv run ai-selector

# Install pre-commit hooks
pre-commit-install:
    pre-commit install

# Build the project
build:
    uv build

# Publish the project
publish:
    uv publish

# Clean temporary files
clean:
    find . -type f -name '*.pyc' -delete
    find . -type d -name '__pycache__' -delete
    rm -rf .mypy_cache .ruff_cache dist
