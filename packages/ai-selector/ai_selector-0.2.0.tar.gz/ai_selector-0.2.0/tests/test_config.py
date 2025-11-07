from pathlib import Path

import pytest

from src.config import Agent, discover_agents, get_agents_directory


@pytest.fixture
def mock_agent_dir(tmp_path: Path) -> Path:
    """Create a temporary directory with mock agent configurations."""
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()

    # Agent 1: Valid configuration
    agent1_dir = agents_dir / "agent1"
    agent1_dir.mkdir()
    (agent1_dir / ".env").write_text("ALIAS=command1\nVAR1=value1")

    # Agent 2: No ALIAS
    agent2_dir = agents_dir / "agent2"
    agent2_dir.mkdir()
    (agent2_dir / ".env").write_text("VAR2=value2")

    # Agent 3: Empty .env file
    agent3_dir = agents_dir / "agent3"
    agent3_dir.mkdir()
    (agent3_dir / ".env").touch()

    # Not a directory
    (agents_dir / "not_a_dir").touch()

    # Directory without .env file
    (agents_dir / "no_env_file").mkdir()

    return agents_dir


def test_get_agents_directory_success(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Test get_agents_directory successfully retrieves the path."""
    monkeypatch.setenv("AI_AGENTS_DIR", str(tmp_path))
    assert get_agents_directory() == tmp_path


def test_get_agents_directory_not_found(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Test get_agents_directory raises FileNotFoundError."""
    non_existent_dir = tmp_path / "non_existent"
    monkeypatch.setenv("AI_AGENTS_DIR", str(non_existent_dir))
    with pytest.raises(FileNotFoundError):
        get_agents_directory()


def test_discover_agents(monkeypatch: pytest.MonkeyPatch, mock_agent_dir: Path) -> None:
    """Test discover_agents finds valid agents."""
    monkeypatch.setattr("src.config.get_agents_directory", lambda: mock_agent_dir)

    agents = discover_agents()

    assert len(agents) == 1
    agent = agents[0]
    assert isinstance(agent, Agent)
    assert agent.name == "agent1"
    assert agent.command == "command1"
    assert agent.env_vars == {"VAR1": "value1"}


def test_get_agents_directory_default(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Test get_agents_directory returns the default path."""
    monkeypatch.delenv("AI_AGENTS_DIR", raising=False)
    monkeypatch.setattr("src.config.load_dotenv", lambda *args, **kwargs: None)

    # Create a temporary directory to use as the default
    default_dir = tmp_path / "ia"
    default_dir.mkdir()

    # Mock Path.expanduser to return our temporary directory
    original_expanduser = Path.expanduser

    def mock_expanduser(self: Path) -> Path:
        if str(self) == "~/ia":
            return default_dir
        return original_expanduser(self)

    monkeypatch.setattr(Path, "expanduser", mock_expanduser)
    assert get_agents_directory() == default_dir


def test_discover_agents_no_alias(
    monkeypatch: pytest.MonkeyPatch, mock_agent_dir: Path
) -> None:
    """Test discover_agents skips agents without an ALIAS variable."""
    monkeypatch.setattr("src.config.get_agents_directory", lambda: mock_agent_dir)
    # Only agent1 has an ALIAS
    (mock_agent_dir / "agent2" / ".env").write_text("VAR2=value2")
    agents = discover_agents()
    assert len(agents) == 1
    assert agents[0].name == "agent1"


def test_discover_agents_invalid_env_file(
    monkeypatch: pytest.MonkeyPatch, mock_agent_dir: Path, capsys: pytest.CaptureFixture
) -> None:
    """Test discover_agents handles invalid .env files."""
    monkeypatch.setattr("src.config.get_agents_directory", lambda: mock_agent_dir)
    # Create an invalid .env file
    (mock_agent_dir / "agent3" / ".env").write_text("ALIAS=")
    agents = discover_agents()
    assert len(agents) == 1
    assert agents[0].name == "agent1"
    captured = capsys.readouterr()
    assert "Warning: agent3/.env has no ALIAS variable, skipping" in captured.out


def test_discover_agents_dotenv_exception(
    monkeypatch: pytest.MonkeyPatch, mock_agent_dir: Path, capsys: pytest.CaptureFixture
) -> None:
    """Test that discover_agents handles exceptions from dotenv_values."""
    monkeypatch.setattr("src.config.get_agents_directory", lambda: mock_agent_dir)

    def raise_exception(*args: object, **kwargs: object) -> None:
        raise Exception("dotenv_error")

    monkeypatch.setattr("src.config.dotenv_values", raise_exception)

    agents = discover_agents()

    assert len(agents) == 0
    captured = capsys.readouterr()
    assert "Warning: Could not load agent1/.env: dotenv_error" in captured.out


def test_agent_full_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Test the full_path property of the Agent class."""
    monkeypatch.setattr("src.config.get_agents_directory", lambda: tmp_path)
    agent = Agent(name="test_agent", command="echo hello")
    assert agent.full_path == tmp_path / "test_agent"
