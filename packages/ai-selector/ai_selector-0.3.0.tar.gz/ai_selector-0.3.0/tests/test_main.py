from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

from src.main import main


@pytest.fixture
def mock_dependencies() -> (
    Generator[tuple[MagicMock, MagicMock, MagicMock], None, None]
):
    """Fixture for mocking main function dependencies."""
    with (
        patch("src.main.discover_agents") as mock_discover,
        patch("src.main.select_agent") as mock_select,
        patch("src.main.execute_agent") as mock_execute,
    ):
        yield mock_discover, mock_select, mock_execute


def test_main_no_agents_found(
    mock_dependencies: tuple[MagicMock, MagicMock, MagicMock],
) -> None:
    """Test main function when no agents are found."""
    mock_discover, _, _ = mock_dependencies
    mock_discover.return_value = []

    result = main()

    assert result == 1
    mock_discover.assert_called_once()


def test_main_agent_selected_and_executed(
    mock_dependencies: tuple[MagicMock, MagicMock, MagicMock],
) -> None:
    """Test main function when an agent is selected and executed."""
    mock_discover, mock_select, mock_execute = mock_dependencies
    mock_agent = MagicMock()
    mock_discover.return_value = [mock_agent]
    mock_select.return_value = mock_agent
    mock_execute.return_value = 0

    result = main()

    assert result == 0
    mock_discover.assert_called_once()
    mock_select.assert_called_once_with([mock_agent])
    mock_execute.assert_called_once_with(mock_agent)


def test_main_agent_selection_cancelled(
    mock_dependencies: tuple[MagicMock, MagicMock, MagicMock],
) -> None:
    """Test main function when agent selection is cancelled."""
    mock_discover, mock_select, _ = mock_dependencies
    mock_agent = MagicMock()
    mock_discover.return_value = [mock_agent]
    mock_select.return_value = None

    result = main()

    assert result == 0
    mock_discover.assert_called_once()
    mock_select.assert_called_once_with([mock_agent])


def test_main_file_not_found_error(
    mock_dependencies: tuple[MagicMock, MagicMock, MagicMock],
) -> None:
    """Test main function handles FileNotFoundError."""
    mock_discover, _, _ = mock_dependencies
    mock_discover.side_effect = FileNotFoundError("test_error")

    result = main()

    assert result == 1


def test_main_keyboard_interrupt(
    mock_dependencies: tuple[MagicMock, MagicMock, MagicMock],
) -> None:
    """Test main function handles KeyboardInterrupt."""
    mock_discover, _, _ = mock_dependencies
    mock_discover.side_effect = KeyboardInterrupt

    result = main()

    assert result == 130


def test_main_exception(
    mock_dependencies: tuple[MagicMock, MagicMock, MagicMock],
) -> None:
    """Test main function handles a generic Exception."""
    mock_discover, mock_select, mock_execute = mock_dependencies
    mock_discover.side_effect = Exception("test_error")

    result = main()

    assert result == 1
