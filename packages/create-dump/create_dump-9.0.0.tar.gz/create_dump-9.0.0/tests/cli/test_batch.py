# tests/cli/test_batch.py

"""
Tests for src/create_dump/cli/batch.py
"""

from __future__ import annotations
import pytest
from typer.testing import CliRunner
from unittest.mock import MagicMock, patch, AsyncMock
from pathlib import Path

# Import the app to test
from create_dump.cli.main import app
# Import the helper function to test directly
from create_dump.cli.batch import split_dirs
from create_dump.core import DEFAULT_DUMP_PATTERN

# Mark all tests in this file as async-capable
pytestmark = pytest.mark.anyio


@pytest.fixture
def cli_runner() -> CliRunner:
    """Provides a Typer CliRunner instance."""
    return CliRunner()


@pytest.fixture(autouse=True)
def mock_cli_deps(mocker):
    """
    Mocks all heavy dependencies called by the batch CLI commands.
    """
    # Mock the `anyio.run` call in `cli/batch.py`
    mock_anyio_run = mocker.patch(
        "create_dump.cli.batch.anyio.run",
        new_callable=MagicMock
    )

    # Mock ArchiveManager instantiation in `cli/batch.py`
    mock_manager_instance = MagicMock()
    mock_manager_instance.run = AsyncMock()  # Mock the async run method
    mock_manager_class = mocker.patch(
        "create_dump.cli.batch.ArchiveManager",
        return_value=mock_manager_instance
    )

    # Mock config loading (from main)
    mocker.patch("create_dump.cli.main.load_config")

    # Mock logging setup
    mock_setup_logging = mocker.patch("create_dump.cli.batch.setup_logging")
    # 🐞 FIX: Also mock logging in main, as it's called by the app
    mocker.patch("create_dump.cli.main.setup_logging")


    return {
        "anyio_run": mock_anyio_run,
        "ArchiveManager_class": mock_manager_class,
        "ArchiveManager_instance": mock_manager_instance,
        "setup_logging": mock_setup_logging,
    }


class TestSplitDirs:
    """Tests the split_dirs helper function."""

    def test_split_dirs_default_string(self):
        """Test with the default string from typer.Option."""
        assert split_dirs(".,packages,services") == [".", "packages", "services"]

    def test_split_dirs_empty_string(self):
        """Test that an empty string falls back to defaults."""
        assert split_dirs("") == [".", "packages", "services"]

    def test_split_dirs_all_empty(self):
        """Test that a string of commas falls back to defaults."""
        assert split_dirs(",,,") == [".", "packages", "services"]

    def test_split_dirs_custom(self):
        """Test a standard custom list."""
        assert split_dirs("src,tests") == ["src", "tests"]

    def test_split_dirs_with_whitespace(self):
        """Test that whitespace is correctly stripped."""
        assert split_dirs("  src , tests, app  ") == ["src", "tests", "app"]


class TestBatchCli:
    """Tests for the 'batch' command group."""

    def test_batch_callback_defaults(
        self, cli_runner: CliRunner, mock_cli_deps: dict
    ):
        """
        Test Case 1: (Callback Defaults)
        Validates that the callback sets defaults correctly, especially dry_run=True.
        """
        mock_run = mock_cli_deps["anyio_run"]

        # 🐞 FIX: Use isolated_filesystem
        with cli_runner.isolated_filesystem():
            result = cli_runner.invoke(app, ["batch", "run", "."])

        assert result.exit_code == 0
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0]
        assert call_args[4] is True  # Check effective_dry_run (arg 4)

    def test_batch_callback_no_dry_run(
        self, cli_runner: CliRunner, mock_cli_deps: dict
    ):
        """
        Test Case 2: (Callback Override)
        Validates that --no-dry-run correctly overrides the callback's default.
        """
        mock_run = mock_cli_deps["anyio_run"]

        # 🐞 FIX: Use isolated_filesystem
        with cli_runner.isolated_filesystem():
            result = cli_runner.invoke(app, ["batch", "run", ".", "--no-dry-run"])

        assert result.exit_code == 0
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0]
        assert call_args[4] is False  # Check effective_dry_run (arg 4)

    def test_run_command_flags(
        self, cli_runner: CliRunner, mock_cli_deps: dict
    ):
        """
        Test Case 3: (run command)
        Validates all flags for 'batch run' are passed to anyio.run.
        """
        mock_run = mock_cli_deps["anyio_run"]

        # 🐞 FIX: Use isolated_filesystem
        with cli_runner.isolated_filesystem() as temp_dir:
            result = cli_runner.invoke(app, [
                "batch", "run", ".",
                "--dirs", "src,tests",
                "--pattern", ".*.log",
                "--format", "json",
                "--max-workers", "10",
                "--archive-all",
                "--archive-format", "tar.gz",
                "-y",
                "--no-dry-run"
            ])

        assert result.exit_code == 0
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0]

        assert call_args[0].__name__ == "run_batch"
        # 🐞 FIX: Assert against the Path object `.`
        assert call_args[1] == Path(".")       # root
        assert call_args[2] == ["src", "tests"]      # subdirs
        assert call_args[3] == ".*.log"              # pattern
        assert call_args[4] is False                 # effective_dry_run
        assert call_args[5] is True                  # yes
        assert call_args[8] == "json"                # format
        assert call_args[9] == 10                    # max_workers
        assert call_args[14] is True                 # archive_all
        # 🐞 FIX: Corrected index from 20 to 21
        assert call_args[21] == "tar.gz"             # archive_format

    def test_run_command_dest_inheritance(
        self, cli_runner: CliRunner, mock_cli_deps: dict
    ):
        """
        Test Case 4: (run command --dest)
        Validates that 'run' inherits --dest from the 'batch' callback.
        """
        mock_run = mock_cli_deps["anyio_run"]

        # 🐞 FIX: Use isolated_filesystem
        with cli_runner.isolated_filesystem():
            result = cli_runner.invoke(app, [
                "batch", "--dest", "global/dest", "run", "."
            ])

        assert result.exit_code == 0
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0]

        # 🐞 FIX: Wrap in Path() to robustly compare str vs Path
        assert Path(call_args[12]) == Path("global/dest")

    def test_run_command_dest_override(
        self, cli_runner: CliRunner, mock_cli_deps: dict
    ):
        """
        Test Case 5: (run command --dest)
        Validates that 'run' --dest overrides the 'batch' --dest.
        """
        mock_run = mock_cli_deps["anyio_run"]

        # 🐞 FIX: Use isolated_filesystem
        with cli_runner.isolated_filesystem():
            result = cli_runner.invoke(app, [
                "batch", "--dest", "global/dest",
                "run", "--dest", "local/dest", "."
            ])

        assert result.exit_code == 0
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0]
        assert call_args[12] == Path("local/dest")

    def test_clean_command_flags(
        self, cli_runner: CliRunner, mock_cli_deps: dict
    ):
        """
        Test Case 6: (clean command)
        Validates all flags for 'batch clean' are passed to anyio.run.
        """
        mock_run = mock_cli_deps["anyio_run"]

        # 🐞 FIX: Use isolated_filesystem
        with cli_runner.isolated_filesystem() as temp_dir:
            # 🐞 FIX: Pass pattern as a positional argument, not an option
            result = cli_runner.invoke(app, [
                "batch", "clean", ".",
                ".*.log",
                "-y",
                "--no-dry-run"
            ])

        # 🐞 FIX: The exit code should now be 0
        assert result.exit_code == 0
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0]

        assert call_args[0].__name__ == "safe_cleanup"
        # 🐞 FIX: Assert against the Path object `.`
        assert call_args[1] == Path(".") # root
        assert call_args[2] == ".*.log"          # pattern
        assert call_args[3] is False             # effective_dry_run
        assert call_args[4] is True              # yes
        # 🐞 FIX: Assert new default 'verbose=False' from main_callback
        assert call_args[5] is False             # verbose (default from main)

    # -----------------
    # 🐞 NEW TESTS START HERE
    # -----------------
    
    def test_archive_command_flags(
        self, cli_runner: CliRunner, mock_cli_deps: dict
    ):
        """
        Action Plan 1: Test `batch archive` Subcommand (lines 200-230).
        Validates flags are passed to ArchiveManager and anyio.run.
        """
        mock_run = mock_cli_deps["anyio_run"]
        mock_manager_class = mock_cli_deps["ArchiveManager_class"]
        mock_manager_instance = mock_cli_deps["ArchiveManager_instance"]
        
        with cli_runner.isolated_filesystem():
            result = cli_runner.invoke(app, [
                "batch", "archive", ".",
                "--archive-all",
                "--archive-search",
                "--no-archive-keep-latest",
                "--archive-keep-last", "7",
                "--archive-clean-root",
                "-y",
                "--no-dry-run"
            ])
        
        assert result.exit_code == 0
        
        # 1. Assert ArchiveManager was instantiated correctly
        mock_manager_class.assert_called_once()
        
        # ⚡ FIX: Get both positional and keyword args
        call_args = mock_manager_class.call_args
        pos_args = call_args[0]
        call_kwargs = call_args[1]

        # ⚡ FIX: Assert positional 'root' argument
        assert pos_args[0] == Path(".")
        # pos_args[1] is the timestamp
        assert isinstance(pos_args[1], str) 
        # ⚡ FIX: Assert positional 'archive_keep_latest'
        assert pos_args[2] is False 
        # ⚡ FIX: Assert positional 'archive_keep_last'
        assert pos_args[3] == 7
        # ⚡ FIX: Assert positional 'archive_clean_root'
        assert pos_args[4] is True
        
        # ⚡ FIX: Assert keyword arguments
        assert call_kwargs["archive_all"] is True
        assert call_kwargs["search"] is True
        assert call_kwargs["yes"] is True
        assert call_kwargs["dry_run"] is False
        assert call_kwargs["archive_format"] == "zip" # Default from main
        
        # 2. Assert anyio.run was called with the manager's run method
        mock_run.assert_called_once_with(mock_manager_instance.run)

    def test_run_command_quiet_flag(
        self, cli_runner: CliRunner, mock_cli_deps: dict
    ):
        """
        Test Coverage for line 104: `if inherited_quiet: ...` in run()
        """
        mock_run = mock_cli_deps["anyio_run"]
        mock_logging = mock_cli_deps["setup_logging"]

        with cli_runner.isolated_filesystem():
            # Invoke `create-dump -q batch run .`
            result = cli_runner.invoke(app, ["-q", "batch", "run", "."])

        assert result.exit_code == 0
        
        # 1. Assert setup_logging was called with quiet=True, verbose=False
        mock_logging.assert_called_with(verbose=False, quiet=True)
        
        # 2. Assert the correct flags were passed to the async function
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0]
        assert call_args[10] is False # inherited_verbose
        assert call_args[11] is True  # inherited_quiet

    def test_clean_command_quiet_flag(
        self, cli_runner: CliRunner, mock_cli_deps: dict
    ):
        """
        Test Coverage for line 163: `if inherited_quiet: ...` in clean()
        """
        mock_run = mock_cli_deps["anyio_run"]
        mock_logging = mock_cli_deps["setup_logging"]

        with cli_runner.isolated_filesystem():
            # Invoke `create-dump -q batch clean .`
            result = cli_runner.invoke(app, ["-q", "batch", "clean", "."])

        assert result.exit_code == 0
        
        # 1. Assert setup_logging was called with quiet=True, verbose=False
        mock_logging.assert_called_with(verbose=False, quiet=True)
        
        # 2. Assert the correct flags were passed to the async function
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0]
        assert call_args[5] is False # inherited_verbose

    def test_archive_command_archive_format_inheritance(
        self, cli_runner: CliRunner, mock_cli_deps: dict
    ):
        """
        Test `batch archive` inherits archive_format from main.
        """
        mock_manager_class = mock_cli_deps["ArchiveManager_class"]
        
        with cli_runner.isolated_filesystem():
            # Set --archive-format at the root level
            result = cli_runner.invoke(app, [
                "--archive-format", "tar.gz", 
                "batch", "archive", "."
            ])
        
        assert result.exit_code == 0
        
        # Assert ArchiveManager was instantiated with the inherited format
        mock_manager_class.assert_called_once()
        call_kwargs = mock_manager_class.call_args[1]
        assert call_kwargs["archive_format"] == "tar.gz"