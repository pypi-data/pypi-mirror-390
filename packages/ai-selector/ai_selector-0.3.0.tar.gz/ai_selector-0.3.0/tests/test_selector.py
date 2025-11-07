from unittest.mock import MagicMock, patch

import pytest

from src.config import Agent
from src.selector import select_agent


@pytest.fixture
def mock_agents() -> list[Agent]:
    """Fixture for a list of mock agents."""
    return [
        Agent(name="agent1", command="command1"),
        Agent(name="agent2", command="command2"),
    ]


@patch("src.selector.display_logo")
@patch("questionary.select")
def test_select_agent_selected(
    mock_select: MagicMock, mock_display_logo: MagicMock, mock_agents: list[Agent]
) -> None:
    """Test select_agent when an agent is selected."""
    mock_select.return_value.ask.return_value = mock_agents[0]

    selected_agent = select_agent(mock_agents)

    assert selected_agent == mock_agents[0]
    mock_display_logo.assert_called_once()
    mock_select.assert_called_once()


@patch("builtins.open")
def test_display_logo_success(
    mock_open: MagicMock, capsys: pytest.CaptureFixture
) -> None:
    """Test that display_logo successfully displays the logo."""
    from src.selector import display_logo

    mock_open.return_value.__enter__.return_value.read.return_value = "test_logo"
    display_logo()
    captured = capsys.readouterr()
    assert "test_logo" in captured.out


@patch("src.selector.display_logo")
@patch("questionary.select")
def test_select_agent_cancelled(
    mock_select: MagicMock, mock_display_logo: MagicMock, mock_agents: list[Agent]
) -> None:
    """Test select_agent when the selection is cancelled."""
    mock_select.return_value.ask.return_value = None

    selected_agent = select_agent(mock_agents)

    assert selected_agent is None
    mock_display_logo.assert_called_once()
    mock_select.assert_called_once()


@patch("src.selector.display_logo")
def test_select_agent_no_agents(mock_display_logo: MagicMock) -> None:
    """Test select_agent with no agents."""
    selected_agent = select_agent([])

    assert selected_agent is None
    mock_display_logo.assert_not_called()


@patch("builtins.open", side_effect=FileNotFoundError)
def test_display_logo_file_not_found(mock_open: MagicMock) -> None:
    """Test that display_logo handles FileNotFoundError."""
    from src.selector import display_logo

    # This should not raise an exception
    display_logo()


@patch("src.selector.display_logo")
@patch("questionary.select", side_effect=KeyboardInterrupt)
def test_select_agent_keyboard_interrupt(
    mock_select: MagicMock, mock_display_logo: MagicMock, mock_agents: list[Agent]
) -> None:
    """Test select_agent handles KeyboardInterrupt."""
    selected_agent = select_agent(mock_agents)

    assert selected_agent is None
    mock_display_logo.assert_called_once()
