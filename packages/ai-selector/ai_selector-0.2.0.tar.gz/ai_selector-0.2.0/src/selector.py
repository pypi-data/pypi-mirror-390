"""Interactive agent selector using questionary."""

from pathlib import Path
from typing import cast

import questionary
from questionary import Style

from .config import Agent

# Custom style for the selector
custom_style = Style(
    [
        ("qmark", "fg:#673ab7 bold"),  # Question mark
        ("question", "bold"),  # Question text
        ("answer", "fg:#f44336 bold"),  # Selected answer
        ("pointer", "fg:#673ab7 bold"),  # Pointer
        ("highlighted", "fg:#673ab7 bold"),  # Highlighted choice
        ("selected", "fg:#cc5454"),  # Selected choice
        ("separator", "fg:#cc5454"),  # Separator
        ("instruction", ""),  # Instructions
        ("text", ""),  # Plain text
        ("disabled", "fg:#858585 italic"),  # Disabled choices
    ]
)


def display_logo() -> None:
    """Display the AI Selector logo from logo.txt file."""
    # Get project root directory (parent of src)
    project_root = Path(__file__).parent.parent
    logo_path = project_root / "logo.txt"

    try:
        with open(logo_path, "r", encoding="utf-8") as f:
            logo = f.read()
            print(logo)
            print()  # Add blank line after logo for spacing
    except FileNotFoundError:
        # Silently continue if logo file doesn't exist
        pass


def select_agent(agents: list[Agent]) -> Agent | None:
    """Display an interactive menu to select an agent.

    Args:
    ----
        agents: List of available agents

    Returns:
    -------
        Selected Agent or None if cancelled

    """
    if not agents:
        print("No agents available.")
        return None

    # Display logo
    display_logo()

    # Sort agents by name for consistent display
    agents = sorted(agents, key=lambda a: a.name)

    # Create choices using agent names
    choices = [{"name": agent.name, "value": agent} for agent in agents]

    try:
        selected = cast(
            Agent | None,
            questionary.select(
                "Select an AI agent:",
                choices=choices,
                style=custom_style,
                use_shortcuts=True,
                use_arrow_keys=True,
            ).ask(),
        )

        return selected

    except KeyboardInterrupt:
        print("\nSelection cancelled.")
        return None
