# tests/collector/test_base.py

"""
Tests for Phase 2: src/create_dump/collector/base.py
"""

from __future__ import annotations
import pytest
import anyio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

# Import the class to test
from create_dump.collector.base import CollectorBase
# Import dependencies needed for testing
from create_dump.core import Config

# Mark all tests in this file as async-capable
pytestmark = pytest.mark.anyio

# --- Fixtures ---

class DummyCollector(CollectorBase):
    """A concrete implementation of CollectorBase for testing."""
    async def collect(self) -> list[str]:
        # This is the abstract method, we don't need it for these tests
        return []

@pytest.fixture
def mock_stat():
    """Fixture to create a mock stat object."""
    stat_mock = MagicMock()
    stat_mock.st_size = 100  # Default size (small)
    return stat_mock

@pytest.fixture
def mock_anyio_path(mocker, mock_stat):
    """Fixture to create a mock anyio.Path object."""
    path_mock = AsyncMock(spec=anyio.Path)
    path_mock.exists = AsyncMock(return_value=True)
    path_mock.stat = AsyncMock(return_value=mock_stat)
    
    # Patch the anyio.Path constructor to return our mock
    mocker.patch("anyio.Path", return_value=path_mock)
    return path_mock

@pytest.fixture
def mock_is_text(mocker):
    """Fixture to mock the is_text_file check."""
    return mocker.patch(
        "create_dump.collector.base.is_text_file",
        AsyncMock(return_value=True)
    )

# --- Test Cases ---

class TestCollectorBase:
    """Groups tests for the CollectorBase class."""

    async def test_setup_specs_defaults(self, default_config: Config, test_project):
        """
        Tests that default includes/excludes are loaded.
        """
        collector = DummyCollector(config=default_config, root=test_project.root)
        
        assert collector._include_spec is not None
        assert collector._exclude_spec is not None
        assert collector._include_spec.match_file("test.py")
        assert collector._exclude_spec.match_file("test.pyc")
        assert collector._exclude_spec.match_file("dump_file_all_create_dump_1234.md")

    async def test_setup_specs_with_gitignore(self, default_config: Config, test_project):
        """
        Tests that .gitignore patterns are correctly loaded and added
        to the exclude spec when use_gitignore=True.
        """
        await test_project.create({
            ".gitignore": """
# This is a comment
*.unique_log
/build/
dist
"""
        })

        collector = DummyCollector(
            config=default_config,
            root=test_project.root,
            use_gitignore=True
        )

        # 🐞 FIX: Use the unique pattern
        assert collector._exclude_spec.match_file("app.unique_log")
        assert collector._exclude_spec.match_file("build/app.exe")
        assert collector._exclude_spec.match_file("dist/my_app.zip")
        # Should still have defaults
        assert collector._exclude_spec.match_file("test.pyc")

    async def test_setup_specs_no_gitignore(self, default_config: Config, test_project):
        """
        Tests that .gitignore is ignored when use_gitignore=False.
        """
        # 🐞 FIX: Use a unique pattern not in default_excludes
        await test_project.create({".gitignore": "*.unique_log"})

        collector = DummyCollector(
            config=default_config,
            root=test_project.root,
            use_gitignore=False  # Explicitly disable
        )

        # 🐞 FIX: Check the unique pattern
        # .gitignore pattern should NOT match
        assert not collector._exclude_spec.match_file("app.unique_log")
        # Defaults should still be present
        assert collector._exclude_spec.match_file("test.pyc")

    async def test_setup_specs_custom_patterns(self, default_config: Config, test_project):
        """
        Tests that custom include/exclude patterns are added to the specs.
        """
        collector = DummyCollector(
            config=default_config,
            root=test_project.root,
            includes=["*.custom"],
            excludes=["*.default"]
        )
        
        assert collector._include_spec.match_file("my_file.custom")
        # 🐞 FIX: Test is wrong. Includes are ADDITIVE, not overriding.
        assert collector._include_spec.match_file("my_file.py") # Defaults are additive

        assert collector._exclude_spec.match_file("my_file.default")
        assert collector._exclude_spec.match_file("test.pyc") # Default is additive


    # --- _should_include Tests (Mocked) ---

    async def test_should_include_async_all_pass(
        self, default_config: Config, test_project, mock_anyio_path, mock_is_text
    ):
        """Tests the "happy path" where all checks pass."""
        collector = DummyCollector(config=default_config, root=test_project.root)
        
        result = await collector._should_include(
            mock_anyio_path, "src/main.py"
        )
        
        assert result is True
        mock_anyio_path.exists.assert_called_once()
        mock_anyio_path.stat.assert_called_once()
        mock_is_text.assert_called_once_with(mock_anyio_path)

    async def test_should_include_async_not_exists(
        self, default_config: Config, test_project, mock_anyio_path
    ):
        """Tests that a non-existent file is skipped."""
        mock_anyio_path.exists.return_value = False
        collector = DummyCollector(config=default_config, root=test_project.root)
        
        result = await collector._should_include(
            mock_anyio_path, "src/main.py"
        )
        
        assert result is False
        mock_anyio_path.exists.assert_called_once()
        mock_anyio_path.stat.assert_not_called() # Should short-circuit

    async def test_should_include_async_too_large(
        self, default_config: Config, test_project, mock_anyio_path, mock_stat, mock_is_text
        # 🐞 FIX: Add mock_is_text fixture
    ):
        """Tests that a file exceeding max_file_size_kb is skipped."""
        default_config.max_file_size_kb = 10  # 10KB max
        mock_stat.st_size = 11 * 1024  # 11KB file
        
        collector = DummyCollector(config=default_config, root=test_project.root)
        
        result = await collector._should_include(
            mock_anyio_path, "src/large_file.log"
        )
        
        assert result is False
        mock_anyio_path.stat.assert_called_once()
        mock_is_text.assert_not_called() # Should short-circuit

    async def test_should_include_async_is_binary(
        self, default_config: Config, test_project, mock_anyio_path, mock_is_text
    ):
        """Tests that a binary file is skipped."""
        mock_is_text.return_value = False  # Simulate binary file
        
        collector = DummyCollector(config=default_config, root=test_project.root)
        
        result = await collector._should_include(
            mock_anyio_path, "src/app.exe"
        )
        
        assert result is False
        mock_is_text.assert_called_once_with(mock_anyio_path)

    # --- filter_files Tests (Integration) ---

    async def test_filter_files(self, default_config: Config, test_project):
        """
        Tests the filter_files method, which uses _matches internally.
        This tests the full logic chain.
        """
        await test_project.create({
            "src/main.py": "print('hello')",
            "src/data.bin": b"\x00\x01\x02",
            "README.md": "# Title",
            "app.log": "this is a log", # This is in default_excludes
            "app.unique_log": "this is a unique log", # This is in .gitignore
            ".gitignore": "*.unique_log",
        })

        collector = DummyCollector(
            config=default_config,
            root=test_project.root,
            use_gitignore=True
        )

        raw_files = [
            "src/main.py",
            "src/data.bin",
            "README.md",
            "app.log",
            "app.unique_log", # 🐞 FIX: Add file to test .gitignore
            "non_existent_file.py",
        ]

        filtered = await collector.filter_files(raw_files)

        assert filtered == ["README.md", "src/main.py"]
        
