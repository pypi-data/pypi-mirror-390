from unittest.mock import MagicMock, patch

import pytest

from src.config import Agent
from src.executor import execute_agent


@pytest.fixture
def mock_agent() -> Agent:
    """Fixture for a mock agent."""
    return Agent(
        name="test_agent",
        command="echo 'hello'",
        env_vars={"MY_VAR": "my_value"},
    )


@patch("src.executor.clear_screen")
@patch("src.executor.log_execution")
@patch("subprocess.run")
def test_execute_agent_success(
    mock_run: MagicMock,
    mock_log_execution: MagicMock,
    mock_clear_screen: MagicMock,
    mock_agent: Agent,
) -> None:
    """Test execute_agent successfully runs a command."""
    mock_run.return_value.returncode = 0

    return_code = execute_agent(mock_agent)

    assert return_code == 0
    mock_clear_screen.assert_called_once()
    mock_log_execution.assert_called_once()
    mock_run.assert_called_once()


@patch("src.executor.clear_screen")
@patch("src.executor.log_execution")
@patch("subprocess.run")
def test_execute_agent_failure(
    mock_run: MagicMock,
    mock_log_execution: MagicMock,
    mock_clear_screen: MagicMock,
    mock_agent: Agent,
) -> None:
    """Test execute_agent handles a command failure."""
    mock_run.return_value.returncode = 1

    return_code = execute_agent(mock_agent)

    assert return_code == 1


@patch("src.executor.clear_screen")
@patch("src.executor.log_execution")
@patch("subprocess.run", side_effect=KeyboardInterrupt)
def test_execute_agent_keyboard_interrupt(
    mock_run: MagicMock,
    mock_log_execution: MagicMock,
    mock_clear_screen: MagicMock,
    mock_agent: Agent,
) -> None:
    """Test execute_agent handles KeyboardInterrupt."""
    return_code = execute_agent(mock_agent)

    assert return_code == 130


@patch("src.executor.clear_screen")
@patch("src.executor.log_execution")
@patch("subprocess.run", side_effect=Exception("test_error"))
def test_execute_agent_exception(
    mock_run: MagicMock,
    mock_log_execution: MagicMock,
    mock_clear_screen: MagicMock,
    mock_agent: Agent,
) -> None:
    """Test execute_agent handles exceptions during command execution."""
    return_code = execute_agent(mock_agent)

    assert return_code == 1


@patch("builtins.open", side_effect=Exception("test_error"))
def test_log_execution_exception(
    mock_open: MagicMock, capsys: pytest.CaptureFixture
) -> None:
    """Test that log_execution handles exceptions when writing to the log file."""
    from pathlib import Path

    from src.executor import log_execution

    mock_agent = MagicMock()
    mock_agent.full_path = Path("/test/path")
    mock_agent.name = "test_agent"
    mock_agent.command = "echo hello"
    mock_agent.env_vars = {}

    log_execution(mock_agent, "/test/dir")

    captured = capsys.readouterr()
    assert "Warning: Could not write to log file: test_error" in captured.out


@patch("os.system")
def test_clear_screen(mock_system: MagicMock) -> None:
    """Test that clear_screen calls os.system with the correct command."""
    from src.executor import clear_screen

    clear_screen()
    mock_system.assert_called_once_with("clear")


@patch("os.system")
def test_clear_screen_windows(
    mock_system: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that clear_screen calls os.system with the correct command on Windows."""
    from src.executor import clear_screen

    monkeypatch.setattr("os.name", "nt")
    clear_screen()
    mock_system.assert_called_once_with("cls")


@patch("builtins.open")
def test_log_execution_no_env_vars(
    mock_open: MagicMock, capsys: pytest.CaptureFixture
) -> None:
    """Test that log_execution works correctly when agent.env_vars is empty."""
    from pathlib import Path

    from src.executor import log_execution

    mock_agent = MagicMock()
    mock_agent.full_path = Path("/test/path")
    mock_agent.name = "test_agent"
    mock_agent.command = "echo hello"
    mock_agent.env_vars = {}

    log_execution(mock_agent, "/test/dir")

    mock_open.assert_called_once_with(
        Path("/test/path/agent-execution.log"), "a", encoding="utf-8"
    )
