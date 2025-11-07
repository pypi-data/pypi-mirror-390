#!/usr/bin/env python3
"""AI Agent Selector - Interactive CLI for selecting and running AI agents."""

import sys

from src.config import discover_agents
from src.executor import execute_agent
from src.selector import select_agent


def main() -> int:
    """Run the main application logic."""
    try:
        # Discover agents by scanning for .env files
        available_agents = discover_agents()

        if not available_agents:
            print("No agents found in the configured directory.")
            print("Agents must have a .env file with an ALIAS variable.")
            print("Check AI_AGENTS_DIR environment variable.")
            return 1

        # Show interactive selector
        selected_agent = select_agent(available_agents)

        if selected_agent is None:
            return 0  # User cancelled

        # Execute the selected agent (environment vars already loaded in Agent)
        exit_code = execute_agent(selected_agent)

        return exit_code

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1

    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        return 130

    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
