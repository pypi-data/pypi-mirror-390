"""Agent execution module."""

import os
import subprocess
import sys
from datetime import datetime

from .config import Agent


def clear_screen() -> None:
    """Clear the terminal screen."""
    # Use 'cls' on Windows, 'clear' on Unix-like systems
    os.system("cls" if os.name == "nt" else "clear")


def log_execution(agent: Agent, current_dir: str) -> None:
    """Log the agent execution to a log file in the agent's directory.

    Args:
    ----
        agent: The agent being executed
        current_dir: Current working directory from where selector was run

    """
    log_file = agent.full_path / "agent-execution.log"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_lines = [
        f"[{timestamp}] ====================================================",
        f"[{timestamp}] Agent: {agent.name}",
        f"[{timestamp}] Command: {agent.command}",
        f"[{timestamp}] Executed from: {current_dir}",
    ]

    if agent.env_vars:
        env_vars_str = ", ".join(agent.env_vars.keys())
        log_lines.append(f"[{timestamp}] Environment variables: {env_vars_str}")

    log_lines.append(f"[{timestamp}] ======== Executing Agent ========")
    log_lines.append("")  # Empty line for readability

    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write("\n".join(log_lines) + "\n")
    except Exception as e:
        print(f"Warning: Could not write to log file: {e}")


def execute_agent(agent: Agent) -> int:
    """Execute the selected agent with its environment variables.

    The command is executed in the current directory (not changed to agent's directory).
    Environment variables from the agent's .env are added to the process environment.

    Args:
    ----
        agent: The agent to execute

    Returns:
    -------
        Exit code from the agent process

    """
    # Get current directory before clearing screen
    current_dir = os.getcwd()

    # Log the execution
    log_execution(agent, current_dir)

    # Clear the screen
    clear_screen()

    # Display execution info
    print(f"\n{'=' * 60}")
    print(f"Starting: {agent.name}")
    print(f"Command: {agent.command}")
    print(f"Executed from: {current_dir}")
    if agent.env_vars:
        print(f"Environment variables: {', '.join(agent.env_vars.keys())}")
    print(f"{'=' * 60}\n")

    try:
        # Prepare environment: copy current environment and add agent's variables
        env = os.environ.copy()
        env.update(agent.env_vars)

        # Execute command in current directory with agent's environment
        # Use shell=True to support shell syntax in commands
        result = subprocess.run(
            agent.command,
            shell=True,
            env=env,
            # Inherit stdin, stdout, stderr to allow full interactivity
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

        return result.returncode

    except KeyboardInterrupt:
        print("\n\nAgent execution interrupted by user.")
        return 130  # Standard exit code for SIGINT

    except Exception as e:
        print(f"\nError executing agent: {e}")
        return 1
