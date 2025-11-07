"""Configuration management for AI Agent Selector."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import cast

from dotenv import dotenv_values, load_dotenv


@dataclass
class Agent:
    """Represents an AI agent configuration."""

    name: str  # Directory name (e.g., "claude-code")
    command: str  # Command from ALIAS variable
    env_vars: dict[str, str] = field(default_factory=dict)  # Environment variables
    env_file: Path = field(default_factory=Path)  # Path to .env file

    @property
    def full_path(self) -> Path:
        """Get the full path to the agent directory."""
        agents_dir = get_agents_directory()
        return agents_dir / self.name


def get_agents_directory() -> Path:
    """Get the agents directory from environment variable."""
    # Load .env from ai-selector project root (not current working directory)
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    load_dotenv(env_file)

    agents_dir = os.getenv("AI_AGENTS_DIR", "~/ia")
    path = Path(agents_dir).expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(
            f"Agents directory not found: {path}\n"
            f"Please set AI_AGENTS_DIR environment variable or create the directory."
        )

    return path


def discover_agents() -> list[Agent]:
    """Discover all agents by scanning for .env files in AI_AGENTS_DIR.

    An agent is any subdirectory that contains a .env file with an ALIAS variable.

    Returns
    -------
        List of discovered Agent objects

    """
    agents_dir = get_agents_directory()
    agents: list[Agent] = []

    # Scan all subdirectories
    for item in agents_dir.iterdir():
        if not item.is_dir():
            continue

        env_file = item / ".env"
        if not env_file.exists():
            continue

        # Load the .env file
        try:
            env_vars = dotenv_values(env_file)

            # Check for ALIAS variable
            alias = env_vars.get("ALIAS")
            if not alias:
                print(f"Warning: {item.name}/.env has no ALIAS variable, skipping")
                continue

            env_vars_only = cast(
                dict[str, str],
                {k: v for k, v in env_vars.items() if k != "ALIAS" and v is not None},
            )

            agent = Agent(
                name=item.name,
                command=alias,
                env_vars=env_vars_only,
                env_file=env_file,
            )
            agents.append(agent)

        except Exception as e:
            print(f"Warning: Could not load {item.name}/.env: {e}")
            continue

    return agents
