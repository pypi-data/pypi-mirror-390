# 🗃️ Project Code Dump

**Generated:** 2025-11-10T14:19:10+00:00 UTC
**Version:** 10.0.0
**Git Branch:** main | **Commit:** 4ad3a99

---

## Table of Contents

1. [collector/git_diff.py](#collector-git-diff-py)
2. [collector/walk.py](#collector-walk-py)
3. [archiver.py](#archiver-py)
4. [archive/pruner.py](#archive-pruner-py)
5. [cleanup.py](#cleanup-py)
6. [cli/single.py](#cli-single-py)
7. [collector/base.py](#collector-base-py)
8. [collector/git_ls.py](#collector-git-ls-py)
9. [archive/core.py](#archive-core-py)
10. [archive/finder.py](#archive-finder-py)
11. [core.py](#core-py)
12. [helpers.py](#helpers-py)
13. [cli/rollback.py](#cli-rollback-py)
14. [cli/main.py](#cli-main-py)
15. [archive/packager.py](#archive-packager-py)
16. [cli/batch.py](#cli-batch-py)
17. [logging.py](#logging-py)
18. [scanning.py](#scanning-py)
19. [rollback/engine.py](#rollback-engine-py)
20. [rollback/parser.py](#rollback-parser-py)
21. [single.py](#single-py)
22. [path_utils.py](#path-utils-py)
23. [metrics.py](#metrics-py)
24. [system.py](#system-py)
25. [processor.py](#processor-py)
26. [version.py](#version-py)
27. [orchestrator.py](#orchestrator-py)
28. [watch.py](#watch-py)
29. [writing/checksum.py](#writing-checksum-py)
30. [writing/json.py](#writing-json-py)
31. [writing/markdown.py](#writing-markdown-py)
32. [workflow/single.py](#workflow-single-py)

---

## collector/git_diff.py

<a id='collector-git-diff-py'></a>

```python
# src/create_dump/collector/git_diff.py

"""The 'git diff' collection strategy."""

from __future__ import annotations

from pathlib import Path
from typing import List

from ..logging import logger
from ..system import get_git_diff_files
from .base import CollectorBase


class GitDiffCollector(CollectorBase):
    """Collects files using 'git diff --name-only'."""

    def __init__(self, diff_since: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.diff_since = diff_since

    async def collect(self) -> List[str]:
        """Run 'git diff' and filter the results."""
        logger.debug("Collecting files via 'git diff'", ref=self.diff_since)
        raw_files_list = await get_git_diff_files(self.root, self.diff_since)
        if not raw_files_list:
            logger.warning("'git diff' returned no files.", ref=self.diff_since)
            return []

        logger.debug(f"Git found {len(raw_files_list)} raw files. Applying filters...")
        return await self.filter_files(raw_files_list)
```

---

## collector/walk.py

<a id='collector-walk-py'></a>

```python
# src/create_dump/collector/walk.py

"""The standard asynchronous directory walk collector."""

from __future__ import annotations

from pathlib import Path
from typing import AsyncGenerator, List

import anyio

from ..logging import logger
from .base import CollectorBase


class WalkCollector(CollectorBase):
    """Collects files using a recursive async walk."""

    async def _collect_recursive(self, rel_dir: Path) -> AsyncGenerator[Path, None]:
        """Recursive async generator for subdirs."""
        full_dir = anyio.Path(self.root / rel_dir)
        try:
            async for entry in full_dir.iterdir():
                if await entry.is_dir():
                    if entry.name in self.config.excluded_dirs:
                        continue
                    new_rel_dir = Path(entry).relative_to(self.root)
                    async for p in self._collect_recursive(new_rel_dir):
                        yield p
                elif await entry.is_file():
                    rel_path = Path(entry).relative_to(self.root)
                    if await self._matches(rel_path):
                        yield rel_path
        except OSError as e:
            logger.warning("Failed to scan directory", path=str(full_dir), error=str(e))

    async def collect(self) -> List[str]:
        """Walk and filter files efficiently."""
        logger.debug("Collecting files via standard async walk")
        files_list_internal: List[str] = []
        anyio_root = anyio.Path(self.root)
        
        try:
            async for entry in anyio_root.iterdir():
                if await entry.is_dir():
                    if entry.name in self.config.excluded_dirs:
                        continue
                    async for rel_path in self._collect_recursive(
                        Path(entry).relative_to(self.root)
                    ):
                        files_list_internal.append(rel_path.as_posix())
                elif await entry.is_file():
                    rel_path = Path(entry).relative_to(self.root)
                    if await self._matches(rel_path):
                        files_list_internal.append(rel_path.as_posix())
        except OSError as e:
            logger.error("Failed to scan root directory", path=str(self.root), error=str(e))
            return [] # Cannot proceed if root is unreadable

        files_list_internal.sort()
        return files_list_internal
```

---

## archiver.py

<a id='archiver-py'></a>

```python
# src/create_dump/archiver.py

"""
Orchestrator for the archiving workflow.

Coordinates Finder, Packager, and Pruner components to manage the
archive lifecycle (find, zip, clean, prune).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional, Tuple, Dict

import anyio  # ⚡ REFACTOR: Import anyio
# ⚡ REFACTOR: Import async cleanup
from .cleanup import safe_delete_paths
from .core import Config, load_config, DEFAULT_DUMP_PATTERN
from .path_utils import confirm
from .logging import logger  # ⚡ REFACTOR: Import from logging
# ⚡ REFACTOR: Import new SRP components
from .archive import ArchiveFinder, ArchivePackager, ArchivePruner

__all__ = ["ArchiveManager"]


class ArchiveManager:
    """Orchestrates finding, packaging, and pruning of archives."""

    def __init__(
        self,
        root: Path,
        timestamp: str,
        keep_latest: bool = True,
        keep_last: Optional[int] = None,
        clean_root: bool = False,
        search: bool = False,
        include_current: bool = True,
        no_remove: bool = False,
        dry_run: bool = False,
        yes: bool = False,
        verbose: bool = False,
        md_pattern: Optional[str] = None,
        archive_all: bool = False,
        archive_format: str = "zip",
    ):
        self.root = root.resolve()
        self.timestamp = timestamp
        self.search = search or archive_all
        self.archive_all = archive_all
        self.dry_run = dry_run
        self.yes = yes
        self.clean_root = clean_root
        self.no_remove = no_remove
        
        # Load and validate config (sync, fine)
        cfg = load_config()
        self.md_pattern = md_pattern or cfg.dump_pattern
        if md_pattern and not re.match(r'.*_all_create_dump_', self.md_pattern):
            logger.warning("Loose md_pattern provided; enforcing canonical: %s", DEFAULT_DUMP_PATTERN)
            self.md_pattern = DEFAULT_DUMP_PATTERN

        # Setup directories (sync, fine)
        self.archives_dir = self.root / "archives"
        self.archives_dir.mkdir(exist_ok=True)
        self.quarantine_dir = self.archives_dir / "quarantine"
        self.quarantine_dir.mkdir(exist_ok=True)
        
        # Instantiate SRP components (sync, fine)
        self.finder = ArchiveFinder(
            root=self.root,
            md_pattern=self.md_pattern,
            search=self.search,
            verbose=verbose,
            dry_run=dry_run,
            quarantine_dir=self.quarantine_dir,
        )
        
        self.packager = ArchivePackager(
            root=self.root,
            archives_dir=self.archives_dir,
            quarantine_dir=self.quarantine_dir,
            timestamp=self.timestamp,
            keep_latest=keep_latest,
            verbose=verbose,
            dry_run=dry_run,
            yes=yes,
            clean_root=clean_root,
            no_remove=no_remove,
            archive_format=archive_format,
         
        )
        
        self.pruner = ArchivePruner(
            archives_dir=self.archives_dir,
            keep_last=keep_last,
            verbose=verbose,
        )

    # ⚡ REFACTOR: Converted to async
    async def run(self, current_outfile: Optional[Path] = None) -> Dict[str, Optional[Path]]:
        """Orchestrate: find, package, clean, prune."""
        
        # 1. Find pairs
        # ⚡ REFACTOR: Await async finder
        pairs = await self.finder.find_dump_pairs()
        if not pairs:
            logger.info("No pairs for archiving.")
            await self.pruner.prune()  # Prune even if no new pairs
            return {}

        archive_paths: Dict[str, Optional[Path]] = {}
        all_to_delete: List[Path] = []

        # 2. Package pairs
        if not self.archive_all:
            # ⚡ REFACTOR: Await async packager
            archive_paths, to_delete = await self.packager.handle_single_archive(pairs)
            all_to_delete.extend(to_delete)
        else:
            groups = self.packager.group_pairs_by_prefix(pairs)
            # ⚡ REFACTOR: Await async packager
            archive_paths, to_delete = await self.packager.handle_grouped_archives(groups)
            all_to_delete.extend(to_delete)

        # 3. Clean (Deferred bulk delete)
        if self.clean_root and all_to_delete and not self.no_remove and not self.dry_run:
            prompt = f"Delete {len(all_to_delete)} archived files across groups?" if self.archive_all else f"Clean {len(all_to_delete)} root files post-archive?"
            
            # ⚡ REFACTOR: Run blocking 'confirm' in a thread
            user_confirmed = self.yes or await anyio.to_thread.run_sync(confirm, prompt)
            
            if user_confirmed:
                # ⚡ REFACTOR: Call async delete
                await safe_delete_paths(
                    all_to_delete, self.root, dry_run=False, assume_yes=self.yes
                )
                logger.info("Deferred delete: Cleaned %d files post-validation", len(all_to_delete))

        # 4. Prune
        # ⚡ REFACTOR: Await async pruner
        await self.pruner.prune()

        # 5. Handle symlink (no-op for now)
        if current_outfile:
            pass  # Logic for symlinking latest remains here if needed

        return archive_paths
    
    # ⚡ REFACTOR: Removed synchronous run method
```

---

## archive/pruner.py

<a id='archive-pruner-py'></a>

```python
# src/create_dump/archive/pruner.py

"""Component responsible for pruning old archives based on retention policies."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional, List

import anyio
from ..cleanup import safe_delete_paths
from ..logging import logger


class ArchivePruner:
    """Prunes old archives to enforce retention (e.g., keep last N)."""

    def __init__(
        self,
        archives_dir: Path,
        keep_last: Optional[int],
        verbose: bool,
    ):
        self.archives_dir = archives_dir
        self.keep_last = keep_last
        self.verbose = verbose

    async def prune(self) -> None:
        """Prune archives to last N by mtime in a non-blocking way."""
        if self.keep_last is None:
            return
        
        # ⚡ REFACTOR: Generalize pattern to match all supported archive formats
        archive_pattern = re.compile(
            r".*_all_create_dump_\d{8}_\d{6}(\.zip|\.tar\.gz|\.tar\.bz2)$"
        )
        anyio_archives_dir = anyio.Path(self.archives_dir)
        
        # Use async rglob for non-blocking directory traversal
        # ⚡ REFACTOR: Renamed variable for clarity
        archive_files: List[anyio.Path] = []
        async for p in anyio_archives_dir.rglob("*"):
            if archive_pattern.match(p.name):
                archive_files.append(p)
        
        num_to_keep = self.keep_last
        if len(archive_files) > num_to_keep:
            
            # Run blocking stat() calls in a thread pool for sorting
            async def get_mtime(p: anyio.Path) -> float:
                stat_res = await p.stat()
                return stat_res.st_mtime

            # Create a list of (mtime, path) tuples to sort
            path_mtimes = []
            # ⚡ REFACTOR: Use renamed variable
            for p in archive_files:
                path_mtimes.append((await get_mtime(p), p))
            
            # Sort by mtime (ascending: oldest first)
            path_mtimes.sort(key=lambda x: x[0])
            
            num_to_prune = max(0, len(path_mtimes) - num_to_keep)
            
            # Get original pathlib.Path objects for deletion compatibility
            to_prune_paths = [Path(p) for _, p in path_mtimes[:num_to_prune]]
            
            # Call async delete with safety guards
            deleted, _ = await safe_delete_paths(
                to_prune_paths, self.archives_dir, dry_run=False, assume_yes=True
            )
            
            logger.info("Pruned %d old archives (keeping last %d)", deleted, self.keep_last)
            if self.verbose:
                logger.debug("Pruned archives: %s", [p.name for p in to_prune_paths])
```

---

## cleanup.py

<a id='cleanup-py'></a>

```python
# src/create_dump/cleanup.py

"""Safe, auditable cleanup of files/directories with dry-run and prompts."""

from __future__ import annotations

import shutil
from pathlib import Path
# ⚡ REFACTOR: Import AsyncGenerator, Union, and collections.abc
from typing import List, Tuple, AsyncGenerator, Union
import collections.abc

import anyio
# ⚡ REFACTOR: Import async finder and new async safe_is_within
from .path_utils import (
    confirm,
    find_matching_files, safe_is_within
)
from .logging import logger

# ⚡ REFACTOR: Removed safe_delete_paths and safe_cleanup
__all__ = ["safe_delete_paths", "safe_cleanup"]


# ⚡ REFACTOR: Removed synchronous safe_delete_paths function


async def safe_delete_paths(
    # ⚡ REFACTOR: Accept either a List (for existing callers) or an AsyncGenerator
    paths: Union[List[Path], AsyncGenerator[Path, None]], 
    root: Path, 
    dry_run: bool, 
    assume_yes: bool
) -> Tuple[int, int]:
    """Delete files or directories in a safe, async manner."""
    deleted_files = deleted_dirs = 0
    
    # ⚡ REFACTOR: Convert root to anyio.Path once
    anyio_root = anyio.Path(root)
    
    # ⚡ REFACTOR: Create a unified async iterator to handle both types
    async def async_iter(paths_iterable):
        if isinstance(paths_iterable, collections.abc.AsyncGenerator):
            async for p_gen in paths_iterable:
                yield p_gen
        else: # It's a List
            for p_list in paths_iterable:
                yield p_list

    # ⚡ REFACTOR: Use the unified iterator
    async for p in async_iter(paths):
        # 1. 🐞 FIX: Use the original anyio.Path object for all async I/O
        anyio_p = anyio.Path(p)

        # 2. 🐞 FIX: Use the new async safety check
        if not await safe_is_within(anyio_p, anyio_root):
            # Log using the original path for clarity
            logger.warning(f"Skipping path outside root: {p}")
            continue

        # 3. Use the original, async-capable anyio_p for I/O
        if await anyio_p.is_file():
            if dry_run:
                logger.info(f"[dry-run] would delete file: {p}")
            else:
                try:
                    await anyio_p.unlink()
                    logger.info(f"Deleted file: {p}")
                    deleted_files += 1
                # ⚡ REFACTOR: Narrow exception scope
                except OSError as e:
                    logger.error(f"Failed to delete file {p}: {e}")
                    
        elif await anyio_p.is_dir():
            if not assume_yes and not dry_run:
                ok = await anyio.to_thread.run_sync(
                    confirm, f"Remove directory tree: {p}?"
                )
                if not ok:
                    continue
            if dry_run:
                logger.info(f"[dry-run] would remove directory: {p}")
            else:
                try:
                    # 🐞 FIX: Wrap sync shutil.rmtree in thread pool (anyio.Path lacks rmtree)
                    await anyio.to_thread.run_sync(shutil.rmtree, anyio_p)
                    logger.info(f"Removed directory: {p}")
                    deleted_dirs += 1
                # ⚡ REFACTOR: Narrow exception scope
                except OSError as e:
                    logger.error(f"Failed to remove directory {p}: {e}")
    return deleted_files, deleted_dirs


# ⚡ REFACTOR: Removed synchronous safe_cleanup function


# ⚡ REFACTOR: New async version of safe_cleanup
async def safe_cleanup(root: Path, pattern: str, dry_run: bool, assume_yes: bool, verbose: bool) -> None:
    """Standalone async cleanup of matching paths."""
    # ⚡ REFACTOR: find_matching_files is now a generator
    matches_gen = find_matching_files(root, pattern)
    
    # ⚡ REFACTOR: We must 'peek' at the generator to see if it's empty
    try:
        first_match = await anext(matches_gen)
    except StopAsyncIteration:
        logger.info("No matching files found for cleanup.")
        return

    if verbose:
        # ⚡ REFACTOR: We can no longer give an exact count without memory cost.
        logger.info(f"Found paths to clean (starting with: {first_match.name}).")
    if dry_run:
        logger.info("Dry-run: Skipping deletions.")
        return

    user_confirmed = assume_yes or await anyio.to_thread.run_sync(
        confirm, "Delete all matching files?"
    )
    if user_confirmed:
        # ⚡ REFACTOR: Chain the peeked item back onto the generator
        async def final_gen() -> AsyncGenerator[Path, None]:
            yield first_match
            async for p in matches_gen:
                yield p

        deleted_files, deleted_dirs = await safe_delete_paths(
            final_gen(), root, dry_run=False, assume_yes=assume_yes
        )
        logger.info(f"Cleanup complete: {deleted_files} files, {deleted_dirs} dirs deleted")
```

---

## cli/single.py

<a id='cli-single-py'></a>

```python
# src/create_dump/cli/single.py

"""'single' command implementation for the CLI."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from typer import Exit
import anyio  # ⚡ REFACTOR: Import anyio

# ⚡ REFACTOR: Import the new ASYNC workflow function
from ..single import run_single
# ⚡ REFACTOR: Import from new logging module
from ..logging import setup_logging


def single(
    ctx: typer.Context,  # 🐞 FIX: Add Context argument
    # Core Arguments
    root: Path = typer.Argument(Path("."), help="Root directory to scan [default: . (cwd)]."),

    # Output & Format
    dest: Optional[Path] = typer.Option(None, "--dest", help="Destination dir for output (default: root)."),
    no_toc: bool = typer.Option(False, "--no-toc", help="Omit table of contents."),
    tree_toc: bool = typer.Option(False, "--tree-toc", help="Render Table of Contents as a file tree."),
    format: str = typer.Option("md", "--format", help="Output format (md or json)."),
    compress: bool = typer.Option(False, "-c", "--compress", help="Gzip the output file."),

    # Processing
    progress: Optional[bool] = typer.Option(None, "-p", "--progress/--no-progress", help="Show processing progress."),
    allow_empty: bool = typer.Option(False, "--allow-empty", help="Succeed on 0 files (default: fail)."),
    metrics_port: int = typer.Option(8000, "--metrics-port", help="Prometheus export port [default: 8000]."),

    # Filtering & Collection
    exclude: str = typer.Option("", "--exclude", help="Comma-separated exclude patterns."),
    include: str = typer.Option("", "--include", help="Comma-separated include patterns."),
    max_file_size: Optional[int] = typer.Option(None, "--max-file-size", help="Max file size in KB."),
    use_gitignore: bool = typer.Option(True, "--use-gitignore/--no-use-gitignore", help="Incorporate .gitignore excludes [default: true]."),
    git_meta: bool = typer.Option(True, "--git-meta/--no-git-meta", help="Include Git branch/commit [default: true]."),
    max_workers: int = typer.Option(16, "--max-workers", help="Concurrency level [default: 16]."),
    
    # ⚡ NEW: v8 feature flags
    watch: bool = typer.Option(False, "--watch", help="Run in live-watch mode, redumping on file changes."),
    git_ls_files: bool = typer.Option(False, "--git-ls-files", help="Use 'git ls-files' for file collection (fast, accurate)."),
    diff_since: Optional[str] = typer.Option(None, "--diff-since", help="Only dump files changed since a specific git ref (e.g., 'main')."),
    scan_secrets: bool = typer.Option(False, "--scan-secrets", help="Scan files for secrets. Fails dump if secrets are found."),
    hide_secrets: bool = typer.Option(False, "--hide-secrets", help="Redact found secrets (requires --scan-secrets)."),

    # Archiving (Unified)
    archive: bool = typer.Option(False, "-a", "--archive", help="Archive prior dumps into ZIP (unified workflow)."),
    archive_all: bool = typer.Option(False, "--archive-all", help="Archive dumps grouped by prefix (e.g., src_, tests_) into separate ZIPs."),
    archive_search: bool = typer.Option(False, "--archive-search", help="Search project-wide for dumps."),
    archive_include_current: bool = typer.Option(True, "--archive-include-current/--no-archive-include-current", help="Include this run in archive [default: true]."),
    archive_no_remove: bool = typer.Option(False, "--archive-no-remove", help="Preserve originals post-archiving."),
    archive_keep_latest: bool = typer.Option(True, "--archive-keep-latest/--no-archive-keep-latest", help="Keep latest dump live or archive all (default: true; use =false to disable)."),
    archive_keep_last: Optional[int] = typer.Option(None, "--archive-keep-last", help="Keep last N archives."),
    archive_clean_root: bool = typer.Option(False, "--archive-clean-root", help="Clean root post-archive."),
    archive_format: str = typer.Option("zip", "--archive-format", help="Archive format (zip, tar.gz, tar.bz2)."),

    # Controls (Standardized)
    yes: bool = typer.Option(False, "-y", "--yes", help="Assume yes for prompts and deletions [default: false]."),
    dry_run: bool = typer.Option(False, "-d", "--dry-run", help="Simulate without writing files (default: off)."),
    no_dry_run: bool = typer.Option(False, "-nd", "--no-dry-run", help="Run for real (disables simulation) [default: false]."),
    verbose: Optional[bool] = typer.Option(None, "-v", "--verbose", help="Enable debug logging."),
    quiet: Optional[bool] = typer.Option(None, "-q", "--quiet", help="Suppress output (CI mode)."),
):
    """Create a single code dump in the specified directory.
    ...
    """
    if not root.is_dir():
        raise typer.BadParameter(f"Root '{root}' is not a directory. Use '.' for cwd or a valid path.")

    # ⚡ NEW: Validation for v8 flags
    if git_ls_files and diff_since:
        raise typer.BadParameter("--git-ls-files and --diff-since are mutually exclusive.")
    
    if hide_secrets and not scan_secrets:
        raise typer.BadParameter("--hide-secrets requires --scan-secrets to be enabled.")

    effective_dry_run = dry_run and not no_dry_run
    
    # 🐞 FIX: Get verbose/quiet values from the *main* context
    # This ensures `create-dump -v` (no command) works
    main_params = ctx.find_root().params
    
    # 🐞 FIX: Logic to correctly determine verbosity, giving command-level precedence
    # and ensuring quiet wins.
    if quiet is True:
        verbose_val = False
        quiet_val = True
    elif verbose is True:
        verbose_val = True
        quiet_val = False
    else: # Neither was set at the command level, so inherit from main
        verbose_val = main_params.get('verbose', False)
        quiet_val = main_params.get('quiet', False)
        
        # Final sanity check if inheriting: quiet wins
        if quiet_val:
            verbose_val = False

    # 🐞 FIX: Re-run setup_logging in case 'single' was called directly
    setup_logging(verbose=verbose_val, quiet=quiet_val)
    
    # 🐞 FIX: Add logic to correctly determine progress, mirroring verbose/quiet
    if progress is True:
        progress_val = True
    elif progress is False:
        progress_val = False
    else: # Not set at command level, inherit from main
        progress_val = main_params.get('progress', True) # Default to True from main
    
    effective_progress = progress_val and not quiet_val

    # ⚡ REFACTOR: Call the async function using anyio.run
    try:
        anyio.run(
            run_single,
            root,
            effective_dry_run,
            yes,
            no_toc,
            tree_toc,
            compress,
            format,
            exclude,
            include,
            max_file_size,
            use_gitignore,
            git_meta,
            effective_progress,
            max_workers,
            archive,
            archive_all,
            archive_search,
            archive_include_current,
            archive_no_remove,
            archive_keep_latest,
            archive_keep_last,
            archive_clean_root,
            archive_format,
            allow_empty,
            metrics_port,
            verbose_val,  # 🐞 FIX: Pass the correct flag value
            quiet_val,    # 🐞 FIX: Pass the correct flag value
            dest,
            # ⚡ NEW: Pass v8 flags to the orchestrator
            watch,
            git_ls_files,
            diff_since,
            scan_secrets,
            hide_secrets,
        )
    except Exit as e:
        if getattr(e, "exit_code", None) == 0 and dry_run:
            return  # Graceful exit for dry run
        raise
```

---

## collector/base.py

<a id='collector-base-py'></a>

```python
# src/create_dump/collector/base.py

"""Base class for collection strategies."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import AsyncGenerator, List, Optional

import anyio
from pathspec import PathSpec
from pathspec.patterns.gitwildmatch import GitWildMatchPatternError

from ..core import Config
from ..helpers import is_text_file, parse_patterns
from ..logging import logger


class CollectorBase(ABC):
    """Abstract base class for file collection strategies."""

    def __init__(
        self,
        config: Config,
        includes: List[str] = None,
        excludes: List[str] = None,
        use_gitignore: bool = False,
        root: Path = Path("."),
    ):
        self.config = config
        self.root = root.resolve()
        self.includes = includes or []
        self.excludes = excludes or []
        self.use_gitignore = use_gitignore
        
        self._include_spec: Optional[PathSpec] = None
        self._exclude_spec: Optional[PathSpec] = None
        self._setup_specs()  # Sync setup is OK on init

    def _setup_specs(self) -> None:
        """Build include/exclude specs with defaults."""
        default_includes = self.config.default_includes + [
            "*.py", "*.sh", "*.ini", "*.txt", "*.md", "*.yml", "*.yaml",
            "*.toml", "*.cfg", "*.json", "Dockerfile", ".flake8",
            ".pre-commit-config.yaml",
        ]
        all_includes = default_includes + (self.includes or [])

        default_excludes = self.config.default_excludes + [
            "*.log", "*.pem", "*.key", "*.db", "*.sqlite", "*.pyc", "*.pyo",
            ".env*", "bot_config.json", "*config.json", "*secrets*",
            "__init__.py", "*_all_create_dump_*", "*_all_create_dump_*.md*",
            "*_all_create_dump_*.gz*", "*_all_create_dump_*.sha256",
            "*_all_create_dump_*.zip",
        ]
        all_excludes = default_excludes + (self.excludes or [])

        if self.use_gitignore:
            gitignore_path = self.root / ".gitignore"
            if gitignore_path.exists():
                with gitignore_path.open("r", encoding="utf-8") as f:
                    git_patterns = [
                        line.strip()
                        for line in f
                        if line.strip() and not line.startswith("#")
                    ]
                all_excludes.extend(git_patterns)
                logger.debug("Gitignore integrated", patterns=len(git_patterns))

        self._include_spec = parse_patterns(all_includes)
        self._exclude_spec = parse_patterns(all_excludes)

    async def _matches(self, rel_path: Path) -> bool:
        """Check include/exclude and filters."""
        rel_posix = rel_path.as_posix()
        
        if self._exclude_spec and self._exclude_spec.match_file(rel_posix):
            # ⚡ NEW: Add verbose logging
            logger.debug(f"File excluded by pattern: {rel_posix}")
            return False
        
        is_included = (
            not self._include_spec or
            self._include_spec.match_file(rel_posix) or 
            self._include_spec.match_file(rel_path.name)
        )
        if not is_included:
            # ⚡ NEW: Add verbose logging
            logger.debug(f"File not in include list: {rel_posix}")
            return False

        full_path = anyio.Path(self.root / rel_path)
        return await self._should_include(full_path, rel_posix)

    # ⚡ REFACTOR: Pass rel_posix for better logging
    async def _should_include(self, full_path: anyio.Path, rel_posix: str) -> bool:
        """Final size/text check."""
        try:
            if not await full_path.exists():
                logger.debug(f"Skipping non-existent file: {rel_posix}")
                return False
                
            stat = await full_path.stat()
            if (
                self.config.max_file_size_kb
                and stat.st_size > self.config.max_file_size_kb * 1024
            ):
                # ⚡ NEW: Add verbose logging
                logger.debug(f"File exceeds max size: {rel_posix}")
                return False
            
            is_text = await is_text_file(full_path)
            if not is_text:
                # ⚡ NEW: Add verbose logging
                logger.debug(f"File skipped (binary): {rel_posix}")
                return False
            
            # ⚡ NEW: Add verbose logging for success
            logger.debug(f"File included: {rel_posix}")
            return True

        except OSError as e:
            logger.warning(f"File check failed (OSError): {rel_posix}", error=str(e))
            return False

    async def filter_files(self, raw_files: List[str]) -> List[str]:
        """Shared filtering logic for git-based strategies."""
        filtered_files_list: List[str] = []
        for file_str in raw_files:
            try:
                rel_path = Path(file_str)
                if rel_path.is_absolute():
                    if not file_str.startswith(str(self.root)):
                         logger.warning("Skipping git path outside root", path=file_str)
                         continue
                    rel_path = rel_path.relative_to(self.root)
                
                if await self._matches(rel_path):
                    filtered_files_list.append(rel_path.as_posix())
            except Exception as e:
                logger.warning("Skipping file due to error", path=file_str, error=str(e))

        filtered_files_list.sort()
        return filtered_files_list

    @abstractmethod
    async def collect(self) -> List[str]:
        """Collect all raw file paths based on the strategy."""
        raise NotImplementedError
```

---

## collector/git_ls.py

<a id='collector-git-ls-py'></a>

```python
# src/create_dump/collector/git_ls.py

"""The 'git ls-files' collection strategy."""

from __future__ import annotations

from typing import List

from ..logging import logger
from ..system import get_git_ls_files
from .base import CollectorBase


class GitLsCollector(CollectorBase):
    """Collects files using 'git ls-files'."""

    async def collect(self) -> List[str]:
        """Run 'git ls-files' and filter the results."""
        logger.debug("Collecting files via 'git ls-files'")
        raw_files_list = await get_git_ls_files(self.root)
        if not raw_files_list:
            logger.warning("'git ls-files' returned no files.")
            return []
        
        logger.debug(f"Git found {len(raw_files_list)} raw files. Applying filters...")
        return await self.filter_files(raw_files_list)
```

---

## archive/core.py

<a id='archive-core-py'></a>

```python
# src/create_dump/archive/core.py

"""Core utilities and exceptions for the archive components."""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..logging import logger  # ⚡ FIX: Added missing logger import

class ArchiveError(ValueError):
    """Custom error for archive operations."""


def extract_group_prefix(filename: str) -> Optional[str]:
    """Extract group prefix from filename, e.g., 'tests' from 'tests_all_create_dump_*.md'."""
    match = re.match(r'^(.+?)_all_create_dump_\d{8}_\d{6}\.md$', filename)
    if match:
        group = match.group(1)
        if re.match(r'^[a-zA-Z0-9_-]+$', group):
            return group
    return None


def extract_timestamp(filename: str) -> datetime:
    """Extract timestamp from filename (e.g., _20251028_041318)."""
    match = re.search(r'_(\d{8}_\d{6})', filename)
    if match:
        try:
            return datetime.strptime(match.group(1), '%Y%m%d_%H%M%S')
        except ValueError:
            logger.warning("Malformed timestamp in filename: %s", filename)
    return datetime.min


def _safe_arcname(path: Path, root: Path) -> str:
    """Sanitize arcname to prevent zip-slip."""
    try:
        rel = path.relative_to(root).as_posix()
        if ".." in rel.split("/") or rel.startswith("/"):
            raise ValueError(f"Invalid arcname with traversal: {rel}")
        if not path.is_file():
            raise ValueError(f"Invalid arcname: not a file - {path}")
        return rel
    except ValueError as e:
        if "is not in the subpath" in str(e):
            raise ValueError(f"Invalid arcname: {str(e)}") from e
        logger.warning("Skipping unsafe path for ZIP: %s (%s)", path, e)
        raise
```

---

## archive/finder.py

<a id='archive-finder-py'></a>

```python
# src/create_dump/archive/finder.py

"""Component responsible for finding valid MD/SHA dump pairs."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import List, Optional, Tuple, AsyncGenerator

import anyio
# ⚡ REFACTOR: Import the async version of the safety check
from ..path_utils import safe_is_within
from ..logging import logger


class ArchiveFinder:
    """Finds valid dump pairs, respecting search scope and quarantining orphans."""

    def __init__(
        self,
        root: Path,
        md_pattern: str,
        search: bool,
        verbose: bool,
        dry_run: bool,
        quarantine_dir: Path,
    ):
        self.root = root
        self.md_pattern = md_pattern
        self.search = search
        self.verbose = verbose
        self.dry_run = dry_run
        self.quarantine_dir = quarantine_dir
        
        # ⚡ REFACTOR: Store anyio.Path versions for async checks
        self.anyio_root = anyio.Path(self.root)
        self.anyio_quarantine_dir = anyio.Path(self.quarantine_dir)

    # ⚡ REFACTOR: Converted to async generator
    async def _walk_files(self) -> AsyncGenerator[anyio.Path, None]:
        """
        Walks root directory and yields all file Paths.
        Respects self.search (recursive) vs. flat (scandir).
        """
        # ⚡ REFACTOR: Use instance-level anyio_root
        if self.search:
            # Recursive search
            async for p in self.anyio_root.rglob("*"):
                if await p.is_file():
                    yield p
        else:
            # Flat search
            async for p in self.anyio_root.iterdir():
                if await p.is_file():
                    yield p

    # ⚡ REFACTOR: Converted to async
    async def find_dump_pairs(self) -> List[Tuple[Path, Optional[Path]]]:
        """Find MD/SHA pairs; search if enabled; quarantine orphans."""
        md_regex = re.compile(self.md_pattern)
        pairs = []

        # ⚡ REFACTOR: Renamed 'p' to 'anyio_p' for clarity
        async for anyio_p in self._walk_files():
            # Create a sync pathlib.Path for non-I/O operations
            p_pathlib = Path(anyio_p)
            
            # 🐞 FIX: Prevent recursive loop by ignoring the quarantine dir
            # ⚡ REFACTOR: (Target 1) Use await and async check
            if await safe_is_within(anyio_p, self.anyio_quarantine_dir):
                continue

            if not md_regex.search(p_pathlib.name):
                continue
            
            # 🐞 FIX: This check is critical. Only process .md files.
            if not p_pathlib.name.endswith('.md'):
                if self.verbose:
                    logger.debug("Skipping non-MD match: %s", p_pathlib.name)
                continue
            
            # ⚡ REFACTOR: (Target 2) Use await and async check
            if not await safe_is_within(anyio_p, self.anyio_root):
                continue
            
            # Use pathlib for sync suffix logic
            sha_pathlib = p_pathlib.with_suffix(".sha256")
            
            # ⚡ REFACTOR: Use anyio.Path for async .exists() check
            anyio_sha = anyio.Path(sha_pathlib)
            sha_exists = await anyio_sha.exists()
            
            # ⚡ REFACTOR: (Target 3) Re-structured logic for async check
            sha_path = None  # Default to None
            if sha_exists:
                if await safe_is_within(anyio_sha, self.anyio_root):
                    sha_path = sha_pathlib  # Success, store the sync path
                else:
                    logger.debug("Ignoring .sha256 file outside root", path=str(sha_pathlib))

            if not sha_path:
                if not self.dry_run:
                    # Ensure quarantine dir exists before moving
                    await self.anyio_quarantine_dir.mkdir(exist_ok=True)
                    quarantine_path = self.quarantine_dir / p_pathlib.name
                    # ⚡ REFACTOR: Use async rename on the anyio.Path object 'anyio_p'
                    await anyio_p.rename(quarantine_path)
                    logger.warning("Quarantined orphan MD: %s -> %s", p_pathlib, quarantine_path)
                else:
                    logger.warning("[dry-run] Would quarantine orphan MD: %s", p_pathlib)
                continue
            
            # Store the sync pathlib.Path in the list
            pairs.append((p_pathlib, sha_path))

        if self.verbose:
            logger.debug("Found %d pairs (recursive=%s)", len(pairs), self.search)
        return sorted(pairs, key=lambda x: x[0].name)
```

---

## core.py

<a id='core-py'></a>

```python
# src/create_dump/core.py

"""Core models and configuration.

Pydantic models for validation, config loading.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator

from .logging import logger  # ⚡ REFACTOR: Corrected import from .utils
import toml

# Canonical pattern for dump artifacts (imported/used by modules)
DEFAULT_DUMP_PATTERN = r".*_all_create_dump_\d{8}_\d{6}\.(md(\.gz)?|sha256)$"


class Config(BaseModel):
    """Validated config with env support."""

    default_includes: List[str] = Field(default_factory=list)
    default_excludes: List[str] = Field(default_factory=list)
    use_gitignore: bool = True
    git_meta: bool = True
    max_file_size_kb: Optional[int] = Field(None, ge=0)
    dest: Optional[Path] = Field(None, description="Default output destination (CLI --dest overrides)")
    dump_pattern: str = Field(DEFAULT_DUMP_PATTERN, description="Canonical regex for dump artifacts")
    excluded_dirs: List[str] = Field(
        default_factory=lambda: [
            "__pycache__", ".git", ".venv", "venv", "myenv", ".mypy_cache",
            ".pytest_cache", ".idea", "node_modules", "build", "dist",
            "vendor", ".gradle", ".tox", "eggs", ".egg-info",
        ]
    )
    metrics_port: int = Field(8000, ge=1, le=65535)

    # ⚡ NEW: v8 feature flags
    git_ls_files: bool = Field(False, description="Use 'git ls-files' for file collection.")
    scan_secrets: bool = Field(False, description="Enable secret scanning.")
    hide_secrets: bool = Field(False, description="Redact found secrets (requires scan_secrets=True).")


    @field_validator("max_file_size_kb", mode="before")
    @classmethod
    def non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError("must be non-negative")
        return v

    @field_validator("dest", mode="before")
    @classmethod
    def validate_dest(cls, v):
        if v is not None:
            try:
                path = Path(v)
                if not path.name:
                    logger.warning("Empty dest path; defaulting to None.")
                    return None
                return path
            except Exception as e:
                logger.warning("Invalid dest path '%s': %s; defaulting to None.", v, e)
                return None
        return v

    @field_validator("dump_pattern", mode="after")
    @classmethod
    def validate_dump_pattern(cls, v):
        if not v or not re.match(r'.*_all_create_dump_', v):
            logger.warning("Loose or invalid dump_pattern '%s'; enforcing default: %s", v, DEFAULT_DUMP_PATTERN)
            return DEFAULT_DUMP_PATTERN
        return v


class GitMeta(BaseModel):
    branch: Optional[str] = None
    commit: Optional[str] = None


class DumpFile(BaseModel):
    path: str
    language: Optional[str] = None
    temp_path: Optional[Path] = None
    error: Optional[str] = None


# 🐞 FIX: Add `_cwd` parameter for testability
def load_config(path: Optional[Path] = None, _cwd: Optional[Path] = None) -> Config:
    """Loads config from [tool.create-dump] in TOML files."""
    config_data: Dict[str, Any] = {}
    
    # 🐞 FIX: Use provided _cwd for testing, or default to Path.cwd()
    cwd = _cwd or Path.cwd()

    possible_paths = (
        [path]
        if path
        else [
            Path.home() / ".create_dump.toml", # 1. Home dir
            cwd / ".create_dump.toml",         # 2. CWD .create_dump.toml
            cwd / "create_dump.toml",          # 3. CWD create_dump.toml
            cwd / "pyproject.toml",          # 4. CWD pyproject.toml
        ]
    )
    
    for conf_path in possible_paths:
        if conf_path.exists():
            try:
                full_data = toml.load(conf_path)
                config_data = full_data.get("tool", {}).get("create-dump", {})
                if config_data:  # Stop if we find it
                    logger.debug("Config loaded", path=conf_path, keys=list(config_data.keys()))
                    break
            except (toml.TomlDecodeError, OSError) as e:
                logger.warning("Config load failed", path=conf_path, error=str(e))
    return Config(**config_data)


# ⚡ REFACTOR: Removed generate_default_config() function.
# This logic is now handled by the interactive wizard in cli/main.py.
```

---

## helpers.py

<a id='helpers-py'></a>

```python
# src/create_dump/helpers.py

"""Stateless, general-purpose helper functions."""

from __future__ import annotations

import os
import re
import uuid
from os import scandir  # Explicit import
from pathlib import Path
from typing import Dict, List

import anyio  # ⚡ NEW: Import for async path operations
from pathspec import PathSpec
from pathspec.patterns.gitwildmatch import GitWildMatchPatternError

from .logging import logger

# Constants
CHUNK_SIZE = 8192
BINARY_THRESHOLD = 0.05


def slugify(path: str) -> str:
    """Convert path to safe anchor slug."""
    p = Path(path)
    clean = p.as_posix().lstrip("./").lower()
    return re.sub(r"[^a-z0-9]+", "-", clean).strip("-")


def get_language(filename: str) -> str:
    """Detect file language from extension/basename."""
    # ⚡ FIX: Strip leading '.' from basename for special file matching
    basename = Path(filename).name.lower().lstrip('.')
    
    if basename == "dockerfile":
        return "dockerfile"
    if basename == "dockerignore":
        return "ini"
    
    ext = Path(filename).suffix.lstrip(".").lower()
    mapping: Dict[str, str] = {
        "py": "python", "sh": "bash", "yml": "yaml", "yaml": "yaml",
        "ini": "ini", "cfg": "ini", "toml": "toml", "json": "json",
        "txt": "text", "md": "markdown", "js": "javascript", "ts": "typescript",
        "html": "html", "css": "css", "jsx": "jsx", "tsx": "tsx", "vue": "vue",
        "sql": "sql", "go": "go", "rs": "rust", "java": "java", "c": "c",
        "cpp": "cpp", "rb": "ruby", "php": "php", "pl": "perl", "scala": "scala",
        "kt": "kotlin", "swift": "swift", "dart": "dart", "csv": "csv",
        "xml": "xml", "r": "r", "jl": "julia", "ex": "elixir", "exs": "elixir",
        "lua": "lua", "hs": "haskell", "ml": "ocaml", "scm": "scheme",
        "zig": "zig", "carbon": "carbon", "mojo": "mojo", "verse": "verse",
    }
    return mapping.get(ext, "text")


# ⚡ REFACTOR: Removed synchronous is_text_file function


# ⚡ NEW: Async version of is_text_file
async def is_text_file(path: anyio.Path) -> bool:
    """Async Heuristic: Check if file is text-based."""
    try:
        async with await path.open("rb") as f:
            chunk = await f.read(CHUNK_SIZE)
            if len(chunk) == 0:
                return True
            if b"\x00" in chunk:
                return False
            decoded = chunk.decode("utf-8", errors="replace")
            invalid_ratio = decoded.count("\ufffd") / len(decoded)
            return invalid_ratio <= BINARY_THRESHOLD
    except (OSError, UnicodeDecodeError):
        return False


def parse_patterns(patterns: List[str]) -> PathSpec:
    """Parse glob patterns safely."""
    try:
        return PathSpec.from_lines("gitwildmatch", patterns)
    except GitWildMatchPatternError as e:
        logger.error("Invalid pattern", patterns=patterns, error=str(e))
        raise ValueError(f"Invalid patterns: {patterns}") from e


def _unique_path(path: Path) -> Path:
    """Generate unique path with UUID suffix."""
    if not os.path.exists(path):
        return path

    stem, suffix = path.stem, path.suffix
    counter = 0
    while True:
        u = uuid.uuid4()
        hex_attr = getattr(u, "hex", "")
        hex_val = hex_attr() if callable(hex_attr) else hex_attr
        hex8 = str(hex_val)[:8]

        if counter == 0:
            unique_stem = f"{stem}_{hex8}"
        else:
            unique_stem = f"{stem}_{counter}_{hex8}"

        candidate = path.parent / f"{unique_stem}{suffix}"
        if not Path.exists(candidate):
            return candidate
        counter += 1
```

---

## cli/rollback.py

<a id='cli-rollback-py'></a>

```python
# src/create_dump/cli/rollback.py

"""
'rollback' command implementation for the CLI.

Rehydrates a project structure from a specified .md dump file.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Optional

import anyio
import typer

# ⚡ REFACTOR: Import setup_logging
from ..logging import logger, styled_print, setup_logging
from ..path_utils import confirm
from ..rollback.engine import RollbackEngine
from ..rollback.parser import MarkdownParser

# --- Rollback-specific Helpers ---

async def _calculate_sha256(file_path: anyio.Path) -> str:
    """Calculates the SHA256 hash of a file."""
    hasher = hashlib.sha256()
    async with await file_path.open("rb") as f:
        while True:
            chunk = await f.read(8192)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()

async def _find_most_recent_dump(root: Path) -> Optional[Path]:
    """Finds the most recent .md dump file in the root."""
    latest_file: Optional[Path] = None
    latest_mtime: float = -1.0
    
    anyio_root = anyio.Path(root)
    # We use glob here, as find_matching_files is a generator
    # and we need to stat all files to find the latest.
    async for file in anyio_root.glob("*_all_create_dump_*.md"):
        try:
            stat = await file.stat()
            if stat.st_mtime > latest_mtime:
                latest_mtime = stat.st_mtime
                latest_file = Path(file) # Store as sync Path
        except OSError as e:
            logger.warning("Could not stat file", path=str(file), error=str(e))
            continue
    return latest_file

async def _verify_integrity(md_file: Path) -> bool:
    """Verifies the SHA256 hash of the .md file."""
    sha_file = md_file.with_suffix(".sha256")
    anyio_sha_path = anyio.Path(sha_file)
    anyio_md_path = anyio.Path(md_file)

    if not await anyio_sha_path.exists():
        logger.error(f"Integrity check failed: Missing checksum file for {md_file.name}")
        styled_print(f"[red]Error:[/red] Missing checksum file: [blue]{sha_file.name}[/blue]")
        return False
    
    try:
        # 1. Read the expected hash
        sha_content = await anyio_sha_path.read_text()
        expected_hash = sha_content.split()[0].strip()

        # 2. Calculate the actual hash
        actual_hash = await _calculate_sha256(anyio_md_path)

        # 3. Compare
        if actual_hash == expected_hash:
            logger.info("Integrity verified (SHA256 OK)", file=md_file.name)
            return True
        else:
            logger.error(
                "Integrity check FAILED: Hashes do not match",
                file=md_file.name,
                expected=expected_hash,
                actual=actual_hash
            )
            styled_print(f"[red]Error: Integrity check FAILED. File is corrupt.[/red]")
            styled_print(f"  Expected: {expected_hash}")
            styled_print(f"  Got:      {actual_hash}")
            return False
    except Exception as e:
        logger.error(f"Integrity check error: {e}", file=md_file.name)
        styled_print(f"[red]Error during integrity check:[/red] {e}")
        return False

# --- Async Main Logic ---

async def async_rollback(
    root: Path,
    file_to_use: Optional[Path],
    yes: bool,
    dry_run: bool,
    quiet: bool
):
    """The main async logic for the rollback command."""
    
    # 1. DISCOVERY
    md_file: Optional[Path] = None
    if file_to_use:
        if not await anyio.Path(file_to_use).exists():
            styled_print(f"[red]Error:[/red] Specified file not found: {file_to_use}")
            raise typer.Exit(code=1)
        md_file = file_to_use
    else:
        if not quiet:
            styled_print("[cyan]Scanning for most recent dump file...[/cyan]")
        md_file = await _find_most_recent_dump(root)
        if not md_file:
            styled_print("[red]Error:[/red] No `*_all_create_dump_*.md` files found in this directory.")
            raise typer.Exit(code=1)
    
    if not quiet:
        styled_print(f"Found dump file: [blue]{md_file.name}[/blue]")

    # 2. INTEGRITY VERIFICATION
    if not quiet:
        styled_print("Verifying file integrity (SHA256)...")
    is_valid = await _verify_integrity(md_file)
    if not is_valid:
        raise typer.Exit(code=1)
    
    if not quiet:
        styled_print("[green]Integrity verified.[/green]")

    # 3. PREPARATION & CONFIRMATION
    target_folder_name = md_file.stem
    # Your specified safe output directory
    output_dir = root.resolve() / "all_create_dump_rollbacks" / target_folder_name
    
    if not yes and not dry_run:
        prompt = f"Rehydrate project structure to [blue]./{output_dir.relative_to(root.resolve())}[/blue]?"
        user_confirmed = await anyio.to_thread.run_sync(confirm, prompt)
        if not user_confirmed:
            styled_print("[red]Rollback cancelled by user.[/red]")
            raise typer.Exit()
    elif dry_run and not quiet:
            styled_print(f"[cyan]Dry run:[/cyan] Would rehydrate files to [blue]./{output_dir.relative_to(root.resolve())}[/blue]")

    # 4. EXECUTION
    parser = MarkdownParser(md_file)
    engine = RollbackEngine(output_dir, dry_run=dry_run)
    created_files = await engine.rehydrate(parser)

    # 5. SUMMARY
    if not dry_run and not quiet:
        styled_print(f"[green]✅ Rollback complete.[/green] {len(created_files)} files created in [blue]{output_dir}[/blue]")
    elif dry_run and not quiet:
        styled_print(f"[green]✅ Dry run complete.[/green] Would have created {len(created_files)} files.")

# --- Typer Command Definition ---

# ⚡ REFACTOR: Removed 'rollback_app' Typer instance.
# The 'rollback' function is now a plain function to be registered in main.py.

def rollback(
    ctx: typer.Context,
    root: Path = typer.Argument(
        Path("."),
        help="Project root to scan for dumps and write rollback to.",
        show_default=True
    ),
    file: Optional[Path] = typer.Option(
        None,
        "--file",
        help="Specify a dump file to use (e.g., my_dump.md). Default: find latest.",
        show_default=False
    ),
    # ⚡ REFACTOR: Add all 6 consistent flags in order
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Assume yes for prompts and deletions [default: false]."
    ),
    dry_run: bool = typer.Option(
        False,
        "-d",
        "--dry-run",
        help="Simulate without writing files (default: off)."
    ),
    no_dry_run: bool = typer.Option(
        False, 
        "-nd", 
        "--no-dry-run", 
        help="Run for real (disables simulation) [default: false]."
    ),
    verbose: Optional[bool] = typer.Option(
        None, 
        "-v", 
        "--verbose", 
        help="Enable debug logging."
    ),
    quiet: Optional[bool] = typer.Option(
        None, 
        "-q", 
        "--quiet", 
        help="Suppress output (CI mode)."
    ),
):
    """
    Rolls back a create-dump .md file to a full project structure.
    """
    # ⚡ REFACTOR: Add logic block from cli/single.py
    main_params = ctx.find_root().params
    
    effective_dry_run = dry_run and not no_dry_run

    if quiet is True:
        verbose_val = False
        quiet_val = True
    elif verbose is True:
        verbose_val = True
        quiet_val = False
    else: # Neither was set at the command level, so inherit from main
        verbose_val = main_params.get('verbose', False)
        quiet_val = main_params.get('quiet', False)
        
        # Final sanity check if inheriting: quiet wins
        if quiet_val:
            verbose_val = False

    # Re-run setup_logging in case 'rollback' was called directly
    setup_logging(verbose=verbose_val, quiet=quiet_val)
    
    try:
        anyio.run(
            async_rollback,
            root,
            file,
            yes,
            effective_dry_run, # Pass resolved value
            quiet_val          # Pass resolved value
        )
    except (FileNotFoundError, ValueError) as e:
        # These are caught by the parser/engine and logged
        styled_print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        # Catch any other unexpected error
        logger.error("Unhandled rollback error", error=str(e), exc_info=True)
        styled_print(f"[red]An unexpected error occurred:[/red] {e}")
        raise typer.Exit(code=1)
```

---

## cli/main.py

<a id='cli-main-py'></a>

```python
# src/create_dump/cli/main.py

"""
Main CLI Entry Point.

Defines the main 'app' and orchestrates the 'single' and 'batch' commands.
"""

from __future__ import annotations

import typer
from typing import Optional
from pathlib import Path

# ⚡ REFACTOR: Removed generate_default_config import
from ..core import load_config
# ⚡ REFACTOR: Corrected imports from new modules
from ..logging import setup_logging, styled_print
from ..version import VERSION

# ⚡ REFACTOR: Import commands and command groups from submodules
from .single import single
from .batch import batch_app
# ✨ NEW: Import the rollback function directly
from .rollback import rollback


app = typer.Typer(
    name="create-dump",
    add_completion=True,
    pretty_exceptions_enable=True,
    help="Enterprise-grade code dump utility for projects and monorepos.",
    context_settings={"help_option_names": ["-h", "--help"]},
)


# ⚡ NEW: Helper function for the interactive --init wizard
def _run_interactive_init() -> str:
    """Runs an interactive wizard to build the config file content."""
    styled_print("\n[bold]Welcome to the `create-dump` interactive setup![/bold]")
    styled_print("This will create a `create_dump.toml` file in your current directory.\n")
    
    # Header for the TOML file
    lines = [
        "# Configuration for create-dump",
        "# You can also move this content to [tool.create-dump] in pyproject.toml",
        "[tool.create-dump]",
        ""
    ]
    
    # 1. Ask for 'dest' path
    dest_path = typer.prompt(
        "Default output destination? (e.g., './dumps'). [Press Enter to skip]",
        default="",
        show_default=False,
    )
    if dest_path:
        # Ensure path is formatted for TOML (forward slashes)
        sane_path = Path(dest_path).as_posix()
        lines.append(f'# Default output destination. Overridden by --dest.')
        lines.append(f'dest = "{sane_path}"')
        lines.append("")

    # 2. Ask for 'use_gitignore'
    use_gitignore = typer.confirm(
        "Use .gitignore to automatically exclude files?", 
        default=True
    )
    lines.append("# Use .gitignore files to automatically exclude matching files.")
    lines.append(f"use_gitignore = {str(use_gitignore).lower()}")
    lines.append("")

    # 3. Ask for 'git_meta'
    git_meta = typer.confirm(
        "Include Git branch and commit hash in the header?", 
        default=True
    )
    lines.append("# Include Git branch and commit hash in the header.")
    lines.append(f"git_meta = {str(git_meta).lower()}")
    lines.append("")

    # 4. Ask for 'scan_secrets'
    scan_secrets = typer.confirm(
        "Enable secret scanning? (Recommended: false, unless you configure --hide-secrets)", 
        default=False
    )
    lines.append("# Enable secret scanning. Add 'hide_secrets = true' to redact them.")
    lines.append(f"scan_secrets = {str(scan_secrets).lower()}")
    lines.append("")

    return "\n".join(lines)


@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    # --- App Controls ---
    version: bool = typer.Option(False, "-V", "--version", help="Show version and exit."),
    init: bool = typer.Option(
        False, 
        "--init", 
        help="Run interactive wizard to create 'create_dump.toml'.",
        is_eager=True,  # Handle this before any command
    ),
    config: Optional[str] = typer.Option(None, "--config", help="Path to TOML config file."),
    
    # --- ⚡ REFACTOR: Grouped SRE/Control Flags ---
    yes: bool = typer.Option(False, "-y", "--yes", help="Assume yes for prompts and deletions [default: false]."),
    dry_run: bool = typer.Option(False, "-d", "--dry-run", help="Simulate without writing files (default: off)."),
    no_dry_run: bool = typer.Option(False, "-nd", "--no-dry-run", help="Run for real (disables simulation) [default: false]."),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Enable debug logging [default: false]."),
    quiet: bool = typer.Option(False, "-q", "--quiet", help="Suppress output (CI mode) [default: false]."),
    
    # --- Default Command ('single') Flags ---
    dest: Optional[Path] = typer.Option(None, "--dest", help="Destination dir for output (default: root)."),
    no_toc: bool = typer.Option(False, "--no-toc", help="Omit table of contents."),
    tree_toc: bool = typer.Option(False, "--tree-toc", help="Render Table of Contents as a file tree."),
    format: str = typer.Option("md", "--format", help="Output format (md or json)."),
    compress: bool = typer.Option(False, "-c", "--compress", help="Gzip the output file."),
    progress: bool = typer.Option(True, "-p", "--progress/--no-progress", help="Show processing progress."),
    allow_empty: bool = typer.Option(False, "--allow-empty", help="Succeed on 0 files (default: fail)."),
    metrics_port: int = typer.Option(8000, "--metrics-port", help="Prometheus export port [default: 8000]."),
    exclude: str = typer.Option("", "--exclude", help="Comma-separated exclude patterns."),
    include: str = typer.Option("", "--include", help="Comma-separated include patterns."),
    max_file_size: Optional[int] = typer.Option(None, "--max-file-size", help="Max file size in KB."),
    use_gitignore: bool = typer.Option(True, "--use-gitignore/--no-use-gitignore", help="Incorporate .gitignore excludes [default: true]."),
    git_meta: bool = typer.Option(True, "--git-meta/--no-git-meta", help="Include Git branch/commit [default: true]."),
    max_workers: int = typer.Option(16, "--max-workers", help="Concurrency level [default: 16]."),
    watch: bool = typer.Option(False, "--watch", help="Run in live-watch mode, redumping on file changes."),
    git_ls_files: bool = typer.Option(False, "--git-ls-files", help="Use 'git ls-files' for file collection (fast, accurate)."),
    diff_since: Optional[str] = typer.Option(None, "--diff-since", help="Only dump files changed since a specific git ref (e.g., 'main')."),
    scan_secrets: bool = typer.Option(False, "--scan-secrets", help="Scan files for secrets. Fails dump if secrets are found."),
    hide_secrets: bool = typer.Option(False, "--hide-secrets", help="Redact found secrets (requires --scan-secrets)."),
    archive: bool = typer.Option(False, "-a", "--archive", help="Archive prior dumps into ZIP (unified workflow)."),
    archive_all: bool = typer.Option(False, "--archive-all", help="Archive dumps grouped by prefix (e.g., src_, tests_) into separate ZIPs."),
    archive_search: bool = typer.Option(False, "--archive-search", help="Search project-wide for dumps."),
    archive_include_current: bool = typer.Option(True, "--archive-include-current/--no-archive-include-current", help="Include this run in archive [default: true]."),
    archive_no_remove: bool = typer.Option(False, "--archive-no-remove", help="Preserve originals post-archiving."),
    archive_keep_latest: bool = typer.Option(True, "--archive-keep-latest/--no-archive-keep-latest", help="Keep latest dump live or archive all (default: true; use =false to disable)."),
    archive_keep_last: Optional[int] = typer.Option(None, "--archive-keep-last", help="Keep last N archives."),
    archive_clean_root: bool = typer.Option(False, "--archive-clean-root", help="Clean root post-archive."),
    archive_format: str = typer.Option("zip", "--archive-format", help="Archive format (zip, tar.gz, tar.bz2)."),
):
    """Create Markdown code dumps from source files.

    Defaults to 'single' mode if no subcommand provided.
    """
    
    # Setup logging immediately
    setup_logging(verbose=verbose, quiet=quiet)

    if version:
        styled_print(f"create-dump v{VERSION}")
        raise typer.Exit()

    if init:
        config_path = Path("create_dump.toml")
        if config_path.exists():
            styled_print(f"[yellow]⚠️ Config file 'create_dump.toml' already exists.[/yellow]")
            raise typer.Exit(code=1)
        
        try:
            config_content = _run_interactive_init()
            config_path.write_text(config_content)
            styled_print(f"\n[green]✅ Success![/green] Default config file created at [blue]{config_path.resolve()}[/blue]")
        except IOError as e:
            styled_print(f"[red]❌ Error:[/red] Could not write config file: {e}")
            raise typer.Exit(code=1)
        
        raise typer.Exit(code=0)  # Exit after creating file

    load_config(Path(config) if config else None)
    
    if ctx.invoked_subcommand is None:
        root_arg = ctx.args[0] if ctx.args else Path(".")
        
        # ⚡ FIX: Must pass ALL duplicated flags to the invoked command
        ctx.invoke(
            single, 
            ctx=ctx,  
            root=root_arg, 
            dest=dest,
            no_toc=no_toc,
            tree_toc=tree_toc,
            format=format,
            compress=compress,
            progress=progress,
            allow_empty=allow_empty,
            metrics_port=metrics_port,
            exclude=exclude,
            include=include,
            max_file_size=max_file_size,
            use_gitignore=use_gitignore,
            git_meta=git_meta,
            max_workers=max_workers,
            watch=watch,
            git_ls_files=git_ls_files,
            diff_since=diff_since,
            scan_secrets=scan_secrets,
            hide_secrets=hide_secrets,
            archive=archive,
            archive_all=archive_all,
            archive_search=archive_search,
            archive_include_current=archive_include_current,
            archive_no_remove=archive_no_remove,
            archive_keep_latest=archive_keep_latest,
            archive_keep_last=archive_keep_last,
            archive_clean_root=archive_clean_root,
            archive_format=archive_format,
            yes=yes,
            dry_run=dry_run,
            no_dry_run=no_dry_run,
            verbose=verbose,
            quiet=quiet
        )


# ⚡ REFACTOR: Register the imported 'single' command
app.command()(single)

# ⚡ REFACTOR: Register the imported 'batch' app
app.add_typer(batch_app, name="batch")

# ✨ NEW: Register the rollback function as a standard command
app.command(name="rollback", help="Rehydrate a project structure from a create-dump file.")(rollback)
```

---

## archive/packager.py

<a id='archive-packager-py'></a>

```python
# src/create_dump/archive/packager.py

"""Component responsible for grouping, sorting, and packaging (zipping) archives."""

from __future__ import annotations

import zipfile
import tarfile  # ⚡ NEW: Import tarfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple, Dict

import anyio
from ..cleanup import safe_delete_paths
from ..path_utils import confirm
from ..helpers import _unique_path
from ..logging import logger
from .core import ArchiveError, extract_group_prefix, extract_timestamp, _safe_arcname


class ArchivePackager:
    """Handles logic for grouping, sorting by date, and creating ZIP archives."""

    def __init__(
        self,
        root: Path,
        archives_dir: Path,
        quarantine_dir: Path,
        timestamp: str,
        keep_latest: bool,
        verbose: bool,
        dry_run: bool,
        yes: bool,
        clean_root: bool,
        no_remove: bool,
        archive_format: str = "zip",  # ⚡ NEW: Add format
    ):
        self.root = root
        self.archives_dir = archives_dir
        self.quarantine_dir = quarantine_dir
        self.timestamp = timestamp
        self.keep_latest = keep_latest
        self.verbose = verbose
        self.dry_run = dry_run
        self.yes = yes
        self.clean_root = clean_root
        self.no_remove = no_remove
        
        # ⚡ NEW: Store format and get correct extension
        self.archive_format = archive_format
        if archive_format == "tar.gz":
            self.archive_ext = ".tar.gz"
        elif archive_format == "tar.bz2":
            self.archive_ext = ".tar.bz2"
        else:
            self.archive_format = "zip"  # Default to zip
            self.archive_ext = ".zip"

    # ⚡ REFACTOR: Renamed to _create_archive_sync
    # 🐞 FIX: Corrected type hint from Path to str
    def _create_archive_sync(self, files_to_archive: List[Path], zip_name: str) -> Tuple[Optional[Path], List[Path]]:
        """Create archive; dedupe, compression-aware, unique naming; validate integrity."""
        if not files_to_archive:
            logger.info("No files to archive for %s", zip_name)
            return None, []

        valid_files = [p for p in files_to_archive if p is not None]
        if not valid_files:
            logger.info("No valid files to archive after filtering orphans for %s", zip_name)
            return None, []

        base_archive = self.archives_dir / zip_name
        archive_name = _unique_path(base_archive)
        to_archive = sorted(list(set(valid_files)))

        try:
            # ⚡ REFACTOR: Branch logic based on format
            if self.archive_format == "zip":
                with zipfile.ZipFile(archive_name, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
                    for p in to_archive:
                        arcname = _safe_arcname(p, self.root)
                        comp_type = zipfile.ZIP_STORED if p.suffix in {".gz", ".zip", ".bz2"} else zipfile.ZIP_DEFLATED
                        z.write(p, arcname=arcname, compress_type=comp_type)
                
                # ⚡ REFACTOR: Validation is zip-specific
                with zipfile.ZipFile(archive_name, 'r') as z:
                    badfile = z.testzip()
                    if badfile is not None:
                        raise ArchiveError(f"Corrupt file in ZIP: {badfile}")
                logger.info("ZIP integrity validated successfully for %s", zip_name)

            else:  # Handle 'tar.gz' and 'tar.bz2'
                tar_mode = "w:gz" if self.archive_format == "tar.gz" else "w:bz2"
                with tarfile.open(archive_name, tar_mode) as tar:
                    for p in to_archive:
                        arcname = _safe_arcname(p, self.root)
                        tar.add(p, arcname=arcname)
                logger.info("TAR integrity validated (creation successful) for %s", zip_name)
        
        except (ArchiveError, tarfile.TarError, zipfile.BadZipFile, Exception) as e:
            logger.error("Archive creation/validation failed for %s: %s. Rolling back.", zip_name, e)
            archive_name.unlink(missing_ok=True)
            raise

        size = archive_name.stat().st_size
        logger.info("Archive %s created: %s (%d bytes, %d files)", self.archive_format.upper(), archive_name, size, len(to_archive))
        return archive_name, to_archive

    async def _create_archive(
        self, files_to_archive: List[Path], zip_name: str
    ) -> Tuple[Optional[Path], List[Path]]:
        """Runs the sync _create_archive_sync in a thread pool to avoid blocking."""
        # ⚡ REFACTOR: Call renamed sync method
        return await anyio.to_thread.run_sync(
            self._create_archive_sync, files_to_archive, zip_name
        )

    def group_pairs_by_prefix(self, pairs: List[Tuple[Path, Optional[Path]]]) -> Dict[str, List[Tuple[Path, Optional[Path]]]]:
        groups: Dict[str, List[Tuple[Path, Optional[Path]]]] = {}
        for pair in pairs:
            prefix = extract_group_prefix(pair[0].name)
            if prefix:
                if prefix not in groups:
                    groups[prefix] = []
                groups[prefix].append(pair)
            else:
                if 'default' not in groups:
                    groups['default'] = []
                groups['default'].append(pair)
        if self.verbose:
            for group, group_pairs in groups.items():
                logger.debug("Grouped %d pairs under '%s'", len(group_pairs), group)
        return groups

    async def handle_single_archive(
        self, pairs: List[Tuple[Path, Optional[Path]]]
    ) -> Tuple[Dict[str, Optional[Path]], List[Path]]:
        
        archive_paths: Dict[str, Optional[Path]] = {}
        to_delete: List[Path] = []

        live_pair = None
        historical = pairs
        if self.keep_latest:
            def key_func(p):
                ts = extract_timestamp(p[0].name)
                if ts == datetime.min:
                    ts = datetime.fromtimestamp(p[0].stat().st_mtime)
                    if self.verbose:
                        logger.debug("Fallback to mtime for sorting: %s", p[0].name)
                return (-ts.timestamp(), p[0].name)
            sorted_pairs = sorted(pairs, key=key_func)
            
            if not sorted_pairs:
                return archive_paths, to_delete 
                
            live_pair = sorted_pairs[0]
            historical = sorted_pairs[1:]
            if self.verbose:
                logger.info(
                    "Retained latest pair (ts=%s): %s",
                    extract_timestamp(live_pair[0].name),
                    live_pair[0].name,
                )

        if len(historical) == 0:
            return archive_paths, to_delete
        
        files_to_archive = [p for pair in historical for p in pair if p is not None]
        num_historical_pairs = len(historical)
        num_files = len(files_to_archive)
        if self.verbose:
            logger.info("Archiving %d pairs (%d files)", num_historical_pairs, num_files)

        # ⚡ REFACTOR: Use self.archive_ext for the correct file extension
        base_archive_name = f"{self.root.name}_dumps_archive_{self.timestamp}{self.archive_ext}"

        if self.dry_run:
            logger.info("[dry-run] Would create archive: %s", base_archive_name)
            archive_path = None
        else:
            archive_path, archived_files = await self._create_archive(
                files_to_archive, base_archive_name
            )
            to_delete.extend(archived_files)

        archive_paths['default'] = archive_path
 
        if self.clean_root and not self.no_remove:
            to_clean = files_to_archive
            if self.keep_latest and live_pair:
                live_paths = [live_pair[0]]
                if live_pair[1] is not None:
                    live_paths.append(live_pair[1])
                to_clean = [p for p in files_to_archive if p not in live_paths]
            prompt = f"Clean {len(to_clean)} root files post-archive?"
            
            user_confirmed = self.yes or await anyio.to_thread.run_sync(confirm, prompt)
            
            if user_confirmed:
                await safe_delete_paths(
                    to_clean, self.root, dry_run=self.dry_run, assume_yes=self.yes
                )
                if not self.dry_run:
                    logger.info("Cleaned %d root files", len(to_clean))


        return archive_paths, to_delete

    async def handle_grouped_archives(
        self, groups: Dict[str, List[Tuple[Path, Optional[Path]]]]
    ) -> Tuple[Dict[str, Optional[Path]], List[Path]]:
        
        archive_paths: Dict[str, Optional[Path]] = {}
        to_delete: List[Path] = []

        for group, group_pairs in groups.items():
            if self.verbose:
                logger.info("Processing group: %s (%d pairs)", group, len(group_pairs))

            if group == 'default' and len(group_pairs) > 0:
                logger.warning("Skipping 'default' group (%d pairs): Quarantining unmatchable MDs", len(group_pairs))
                for pair in group_pairs:
                    md, sha_opt = pair[0], pair[1]
                    if not self.dry_run:
                        await anyio.Path(self.quarantine_dir).mkdir(exist_ok=True)
                        if await anyio.Path(md).exists():
                            quarantine_md = self.quarantine_dir / md.name
                            await anyio.to_thread.run_sync(md.rename, quarantine_md)
                            logger.debug("Quarantined unmatchable MD: %s -> %s", md, quarantine_md)
                        if sha_opt and await anyio.Path(sha_opt).exists() and sha_opt != md:
                            quarantine_sha = self.quarantine_dir / sha_opt.name
                            await anyio.to_thread.run_sync(sha_opt.rename, quarantine_sha)
                            logger.debug("Quarantined unmatchable SHA: %s -> %s", sha_opt, quarantine_sha)
                    else:
                        logger.warning("[dry-run] Would quarantine unmatchable pair: %s / %s", md, sha_opt)
                continue
            
            live_pair = None
            historical = group_pairs
            if self.keep_latest:
                def key_func(p):
                    ts = extract_timestamp(p[0].name)
                    if ts == datetime.min:
                        ts = datetime.fromtimestamp(p[0].stat().st_mtime)
                        if self.verbose:
                            logger.debug("Fallback to mtime for sorting in %s: %s", group, p[0].name)
                    return (-ts.timestamp(), p[0].name)
                sorted_pairs = sorted(group_pairs, key=key_func)
                
                if not sorted_pairs:
                    continue 
                
                live_pair = sorted_pairs[0]
                historical = sorted_pairs[1:]
                if self.verbose and live_pair:
                    logger.info(
                        "Retained latest pair in %s (ts=%s): %s",
                        group,
                        extract_timestamp(live_pair[0].name),
                        live_pair[0].name,
                    )

            if len(historical) == 0:
                logger.info("No historical pairs for group %s.", group)
                continue
            
            files_to_archive = [p for pair in historical for p in pair if p is not None]
            num_historical_pairs = len(historical)
            num_files = len(files_to_archive)
            if self.verbose:
                logger.info("Archiving %d pairs (%d files) for group %s", num_historical_pairs, num_files, group)

            # ⚡ REFACTOR: Use self.archive_ext for the correct file extension
            base_archive_name = f"{group}_all_create_dump_{self.timestamp}{self.archive_ext}"
            
            if self.dry_run:
                logger.info("[dry-run] Would create archive for %s: %s", group, base_archive_name)
                archive_path = None
            else:
                archive_path, archived_files = await self._create_archive(
                    files_to_archive, base_archive_name
                )
                to_delete.extend(archived_files)

            archive_paths[group] = archive_path

        return archive_paths, to_delete
```

---

## cli/batch.py

<a id='cli-batch-py'></a>

```python
# src/create_dump/cli/batch.py

"""'batch' command group implementation for the CLI."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

import typer
import anyio  # ⚡ REFACTOR: Import anyio

# ⚡ REFACTOR: Import async versions of cleanup and orchestrator
from ..cleanup import safe_cleanup
from ..core import DEFAULT_DUMP_PATTERN
from ..orchestrator import run_batch
# ⚡ REFACTOR: Import from new logging module
from ..logging import setup_logging
from ..archiver import ArchiveManager


# Create a separate Typer for the batch group
batch_app = typer.Typer(no_args_is_help=True, context_settings={"help_option_names": ["-h", "--help"]})


@batch_app.callback()
def batch_callback(
    # Controls (Standardized; dry-run default ON for safety)
    dry_run: bool = typer.Option(True, "-d", "--dry-run", help="Perform a dry-run (default: ON for batch)."),
    dest: Optional[Path] = typer.Option(None, "--dest", help="Global destination dir for outputs (default: root)."),
):
    """Batch operations: Run dumps across subdirectories with cleanup and centralization.

    Examples:
        $ create-dump batch run --dirs src,tests --archive-all -y  # Batch dumps + grouped archive, skip prompts
        $ create-dump batch clean --pattern '.*dump.*' -y -nd  # Real cleanup of olds
    """
    # Logging is now set by the main_callback or the subcommand.
    pass


def split_dirs(dirs_str: str) -> List[str]:
    """Split comma-separated dirs string into list, stripping whitespace."""
    if not dirs_str:
        return [".", "packages", "services"]
    split = [d.strip() for d in dirs_str.split(',') if d.strip()]
    if not split:
        return [".", "packages", "services"]
    return split


@batch_app.command()
def run(
    ctx: typer.Context,  # Inject ctx to access callback params
    # Core Arguments
    root: Path = typer.Argument(Path("."), help="Root project path."),

    # Output & Processing
    dest: Optional[Path] = typer.Option(None, "--dest", help="Destination dir for centralized outputs (default: root; inherits from batch)."),
    dirs: str = typer.Option(".,packages,services", "--dirs", help="Subdirectories to process (comma-separated, relative to root) [default: .,packages,services]."),
    pattern: str = typer.Option(DEFAULT_DUMP_PATTERN, "--pattern", help="Regex to identify dump files [default: canonical pattern]."),
    format: str = typer.Option("md", "--format", help="Output format (md or json)."),
    accept_prompts: bool = typer.Option(True, "--accept-prompts/--no-accept-prompts", help='Auto-answer "y" to single-dump prompts [default: true].'),
    compress: bool = typer.Option(False, "-c", "--compress", help="Gzip outputs [default: false]."),
    max_workers: int = typer.Option(4, "--max-workers", help="Workers per subdir dump (global concurrency limited) [default: 4]."),

    # Archiving (Unified)
    archive: bool = typer.Option(False, "-a", "--archive", help="Archive prior dumps into ZIP (unified workflow)."),
    archive_all: bool = typer.Option(False, "--archive-all", help="Archive dumps grouped by prefix (e.g., src_, tests_) into separate ZIPs."),
    archive_search: bool = typer.Option(False, "--archive-search", help="Search project-wide for dumps."),
    archive_include_current: bool = typer.Option(True, "--archive-include-current/--no-archive-include-current", help="Include this batch in archive [default: true]."),
    archive_no_remove: bool = typer.Option(False, "--archive-no-remove", help="Preserve originals post-archiving."),
    archive_keep_latest: bool = typer.Option(True, "--archive-keep-latest/--no-archive-keep-latest", help="Keep latest dump live or archive all (default: true; use =false to disable)."),
    archive_keep_last: Optional[int] = typer.Option(None, "--archive-keep-last", help="Keep last N archives."),
    archive_clean_root: bool = typer.Option(False, "--archive-clean-root", help="Clean root post-archive."),
    archive_format: str = typer.Option("zip", "--archive-format", help="Archive format (zip, tar.gz, tar.bz2)."),

    # Controls (Standardized)
    yes: bool = typer.Option(False, "-y", "--yes", help="Assume yes for deletions and prompts [default: false]."),
    dry_run: Optional[bool] = typer.Option(None, "-d", "--dry-run", help="Simulate without writing files (overrides batch default)."),
    no_dry_run: bool = typer.Option(False, "-nd", "--no-dry-run", help="Run for real (disables inherited dry-run) [default: false]."),
    verbose: Optional[bool] = typer.Option(None, "-v", "--verbose", help="Enable debug logging."),
    quiet: Optional[bool] = typer.Option(None, "-q", "--quiet", help="Suppress output (CI mode)."),
):
    """Run dumps in multiple subdirectories, cleanup olds, and centralize files.

    Examples:
        $ create-dump batch run src/ --dest central/ --dirs api,web -c -y -nd  # Real batch to central dir
    """
    # 1. Get flags from all 3 levels
    parent_params = ctx.parent.params
    main_params = ctx.find_root().params
    
    # 2. Resolve dry_run (safe by default)
    # Start with the batch-level default
    effective_dry_run = parent_params.get('dry_run', True)
    # If the *command* flag is set, it wins
    if dry_run is True:
        effective_dry_run = True
    # --no-dry-run always wins
    if no_dry_run is True:
        effective_dry_run = False

    # 3. Resolve verbose/quiet (inheriting from root)
    if quiet is True:
        verbose_val = False
        quiet_val = True
    elif verbose is True:
        verbose_val = True
        quiet_val = False
    else: # Neither was set at the command level, so inherit from main
        verbose_val = main_params.get('verbose', False)
        quiet_val = main_params.get('quiet', False)
        if quiet_val:
            verbose_val = False

    # 4. Re-run logging setup
    setup_logging(verbose=verbose_val, quiet=quiet_val)
    
    subdirs = split_dirs(dirs)
    
    # 5. Call async function
    anyio.run(
        run_batch,
        root,
        subdirs,
        pattern,
        effective_dry_run,
        yes, # 'yes' is simple, just pass it
        accept_prompts,
        compress,
        format,
        max_workers,
        verbose_val, # Pass resolved value
        quiet_val,   # Pass resolved value
        dest or parent_params.get('dest'), # Pass inherited value
        archive,
        archive_all,
        archive_search,
        archive_include_current,
        archive_no_remove,
        archive_keep_latest,
        archive_keep_last,
        archive_clean_root,
        archive_format,
    )


@batch_app.command()
def clean(
    ctx: typer.Context,
    # Core Arguments
    root: Path = typer.Argument(Path("."), help="Root project path."),
    pattern: str = typer.Argument(DEFAULT_DUMP_PATTERN, help="Regex for old dumps to delete [default: canonical pattern]."),

    # Controls (Standardized)
    yes: bool = typer.Option(False, "-y", "--yes", help="Skip confirmations for deletions [default: false]."),
    dry_run: Optional[bool] = typer.Option(None, "-d", "--dry-run", help="Simulate without writing files (overrides batch default)."),
    no_dry_run: bool = typer.Option(False, "-nd", "--no-dry-run", help="Run for real (disables inherited dry-run) [default: false]."),
    verbose: Optional[bool] = typer.Option(None, "-v", "--verbose", help="Enable debug logging."),
    quiet: Optional[bool] = typer.Option(None, "-q", "--quiet", help="Suppress output (CI mode)."),
) -> None:
    """Cleanup old dump files/directories without running new dumps.

    Examples:
        $ create-dump batch clean . '.*old_dump.*' -y -nd -v  # Real verbose cleanup
    """
    # 1. Get flags from all 3 levels
    parent_params = ctx.parent.params
    main_params = ctx.find_root().params

    # 2. Resolve dry_run
    effective_dry_run = parent_params.get('dry_run', True)
    if dry_run is True:
        effective_dry_run = True
    if no_dry_run is True:
        effective_dry_run = False

    # 3. Resolve verbose/quiet
    if quiet is True:
        verbose_val = False
        quiet_val = True
    elif verbose is True:
        verbose_val = True
        quiet_val = False
    else:
        verbose_val = main_params.get('verbose', False)
        quiet_val = main_params.get('quiet', False)
        if quiet_val:
            verbose_val = False

    # 4. Re-run logging setup
    setup_logging(verbose=verbose_val, quiet=quiet_val)
    
    # 5. Call async function
    anyio.run(
        safe_cleanup,
        root,
        pattern,
        effective_dry_run,
        yes,
        verbose_val # Pass resolved value
    )


@batch_app.command()
def archive(
    ctx: typer.Context,
    # Core Arguments
    root: Path = typer.Argument(Path("."), help="Root project path."),
    pattern: str = typer.Argument(r".*_all_create_dump_\d{8}_\d{6}\.(md(\.gz)?)$", help="Regex for MD dumps [default: canonical MD subset]."),

    # Archiving (Unified; elevated as primary focus)
    archive_search: bool = typer.Option(False, "--archive-search", help="Recursive search for dumps [default: false]."),
    archive_all: bool = typer.Option(False, "--archive-all", help="Archive dumps grouped by prefix (e.g., src_, tests_) into separate ZIPs [default: false]."),
    archive_keep_latest: bool = typer.Option(True, "--archive-keep-latest/--no-archive-keep-latest", help="Keep latest dump live or archive all (default: true; use =false to disable)."),
    archive_keep_last: Optional[int] = typer.Option(None, "--archive-keep-last", help="Keep last N archives (unified flag)."),
    archive_clean_root: bool = typer.Option(False, "--archive-clean-root", help="Clean root post-archive (unified flag) [default: false]."),

    # Controls (Standardized)
    yes: bool = typer.Option(False, "-y", "--yes", help="Skip confirmations [default: false]."),
    dry_run: Optional[bool] = typer.Option(None, "-d", "--dry-run", help="Simulate without writing files (overrides batch default)."),
    no_dry_run: bool = typer.Option(False, "-nd", "--no-dry-run", help="Run for real (disables simulation) [default: false]."),
    verbose: Optional[bool] = typer.Option(None, "-v", "--verbose", help="Enable debug logging."),
    quiet: Optional[bool] = typer.Option(None, "-q", "--quiet", help="Suppress output (CI mode)."),
) -> None:
    """Archive existing dump pairs into ZIP; optional clean/prune (unified with single mode).

    Examples:
        $ create-dump batch archive monorepo/ '.*custom' --archive-all -y -v  # Grouped archive, verbose, skip prompts
    """
    # 1. Get flags from all 3 levels
    parent_params = ctx.parent.params
    main_params = ctx.find_root().params
    
    # Get archive_format from root
    inherited_archive_format = main_params.get('archive_format', 'zip')

    # 2. Resolve dry_run
    effective_dry_run = parent_params.get('dry_run', True)
    if dry_run is True:
        effective_dry_run = True
    if no_dry_run is True:
        effective_dry_run = False
    
    # 3. Resolve verbose/quiet
    if quiet is True:
        verbose_val = False
        quiet_val = True
    elif verbose is True:
        verbose_val = True
        quiet_val = False
    else:
        verbose_val = main_params.get('verbose', False)
        quiet_val = main_params.get('quiet', False)
        if quiet_val:
            verbose_val = False
    
    # 4. Re-run logging setup
    setup_logging(verbose=verbose_val, quiet=quiet_val)
    
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    
    manager = ArchiveManager(
        root, timestamp, archive_keep_latest, archive_keep_last, archive_clean_root,
        search=archive_search,
        dry_run=effective_dry_run, 
        yes=yes, 
        verbose=verbose_val, # Pass resolved value
        md_pattern=pattern,
        archive_all=archive_all,
        archive_format=inherited_archive_format # Pass inherited format
    )
    
    # 5. Call async function
    anyio.run(manager.run)  # No current_outfile for batch
```

---

## logging.py

<a id='logging-py'></a>

```python
# src/create_dump/logging.py

"""Manages logging, console output, and Rich integration."""

from __future__ import annotations

import logging
import re
import structlog

# Rich
HAS_RICH = False
console = None
Progress = None
SpinnerColumn = None
TextColumn = None
try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn

    console = Console()
    HAS_RICH = True
except ImportError:
    pass

# Define logger EARLY to avoid circular imports
logger = structlog.get_logger("create_dump")


def styled_print(text: str, nl: bool = True, **kwargs) -> None:
    """Prints text using Rich if available, falling back to plain print."""
    end = "" if not nl else "\n"
    if HAS_RICH and console is not None:
        console.print(text, end=end, **kwargs)
    else:
        clean_text = re.sub(r"\[/?[^\]]+\]", "", text)
        print(clean_text, end=end, **kwargs)


def setup_logging(verbose: bool = False, quiet: bool = False) -> None:
    """Configure structured logging once."""
    level = "DEBUG" if verbose else "WARNING" if quiet else "INFO"
    processors = [
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    if HAS_RICH:
        try:
            from structlog.dev import ConsoleRenderer
            processors.append(ConsoleRenderer(pad_event_to=40))
        except ImportError:
            processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.processors.JSONRenderer())

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    logging.basicConfig(level=level, force=True)
```

---

## scanning.py

<a id='scanning-py'></a>

```python
# src/create_dump/scanning.py

"""Secret scanning and redaction middleware."""

from __future__ import annotations

import logging
from typing import List, Dict, Any

import anyio
# 🐞 FIX: Import `to_thread` to create a private symbol
from anyio import to_thread
from detect_secrets.core import scan
from detect_secrets.core.potential_secret import PotentialSecret

from .core import DumpFile
from .logging import logger
from .metrics import ERRORS_TOTAL

# 🐞 FIX: Create a private, patchable symbol for run_sync
_run_sync = to_thread.run_sync


class SecretScanner:
    """Processor middleware to scan for and optionally redact secrets."""

    def __init__(self, hide_secrets: bool = False):
        self.hide_secrets = hide_secrets
        # 🐞 FIX: Remove all plugin and config initialization.
        # It is no longer needed for v1.5.0.

    async def _scan_for_secrets(self, file_str_path: str) -> List[PotentialSecret]:
        """Runs detect-secrets in a thread pool with correct settings."""
        
        def scan_in_thread():
            # 🐞 FIX: Get the "detect-secrets" logger and temporarily
            # silence it to suppress the "No plugins" spam.
            ds_logger = logging.getLogger("detect-secrets")
            original_level = ds_logger.level
            ds_logger.setLevel(logging.CRITICAL)
            
            try:
                # 🐞 FIX: Call scan_file with only the path.
                # v1.5.0 handles its own default plugin initialization
                # internally and does not accept a `plugins` argument.
                results = scan.scan_file(file_str_path)
                
                # 🐞 FIX: Convert the generator to a list *inside* the thread
                return list(results)
            finally:
                # Always restore the original log level
                ds_logger.setLevel(original_level)

        try:
            # 🐞 FIX: Call the new module-level `_run_sync`
            scan_results_list = await _run_sync(
                scan_in_thread
            )
            # The return value is now already a list
            return scan_results_list
        except Exception as e:
            # Log the error but don't fail the whole dump, just this file
            logger.error("Secret scan failed", path=file_str_path, error=str(e))
            return [] # Return empty list on scan error

    async def _redact_secrets(self, temp_path: anyio.Path, secrets: List[PotentialSecret]) -> None:
        """Reads the temp file, redacts secret lines, and overwrites it."""
        try:
            # 1. Get line numbers (detect-secrets is 1-indexed)
            line_numbers_to_redact = {s.line_number for s in secrets}

            # 2. Read lines
            original_content = await temp_path.read_text()
            lines = original_content.splitlines()

            # 3. Redact
            new_lines = []
            for i, line in enumerate(lines, 1):
                if i in line_numbers_to_redact:
                    # Find the specific secret type for this line
                    secret_type = next((s.type for s in secrets if s.line_number == i), "Unknown")
                    new_lines.append(f"***SECRET_REDACTED*** (Line {i}, Type: {secret_type})")
                else:
                    new_lines.append(line)
            
            # 4. Write back
            await temp_path.write_text("\n".join(new_lines))
        except Exception as e:
            logger.error("Failed to redact secrets", path=str(temp_path), error=str(e))
            # If redaction fails, write a generic error to be safe
            await temp_path.write_text(f"*** ERROR: SECRET REDACTION FAILED ***\n{e}")

    async def process(self, dump_file: DumpFile) -> None:
        """
        Public method to run the scan/redact logic on a processed file.
        Modifies `dump_file` in place if an error occurs.
        """
        if not dump_file.temp_path or dump_file.error:
            # File failed before this middleware (e.g., read error)
            return

        temp_anyio_path = anyio.Path(dump_file.temp_path)
        temp_file_str = str(dump_file.temp_path)
        
        secrets = await self._scan_for_secrets(temp_file_str)

        if secrets:
            if self.hide_secrets:
                # Redact the file and continue
                await self._redact_secrets(temp_anyio_path, secrets)
                logger.warning("Redacted secrets", path=dump_file.path)
            else:
                # Fail the file
                await temp_anyio_path.unlink(missing_ok=True)
                ERRORS_TOTAL.labels(type="secret").inc()
                logger.error("Secrets detected", path=dump_file.path)
                dump_file.error = "Secrets Detected" # Modify the object
                dump_file.temp_path = None # Clear the temp path
```

---

## rollback/engine.py

<a id='rollback-engine-py'></a>

```python
# src/create_dump/rollback/engine.py

"""
Consumes a MarkdownParser and rehydrates the project structure to disk.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

import anyio

from ..logging import logger
from .parser import MarkdownParser
# ✨ NEW: Import the robust, async-native path safety check
from ..path_utils import safe_is_within


class RollbackEngine:
    """
    Consumes a parser and writes the file structure to a target directory.
    """

    def __init__(self, root_output_dir: Path, dry_run: bool = False):
        """
        Initializes the engine.

        Args:
            root_output_dir: The *base* directory to write files into
                             (e.g., .../all_create_dump_rollbacks/my_dump_name_.../)
            dry_run: If True, will only log actions instead of writing.
        """
        self.root_output_dir = root_output_dir
        self.dry_run = dry_run
        self.anyio_root = anyio.Path(self.root_output_dir)

    async def rehydrate(self, parser: MarkdownParser) -> List[Path]:
        """
        Consumes the parser and writes files to the target directory.

        Args:
            parser: An initialized MarkdownParser instance.

        Returns:
            A list of the `pathlib.Path` objects that were created.
        """
        created_files: List[Path] = []
        
        logger.info(
            "Starting rehydration",
            target_directory=str(self.root_output_dir),
            dry_run=self.dry_run
        )

        async for rel_path_str, content in parser.parse_dump_file():
            try:
                # 🔒 SECURITY: Prevent path traversal attacks
                # ♻️ REFACTOR: Replaced weak ".." check with robust safe_is_within
                
                target_path = self.anyio_root / rel_path_str
                
                # The new, robust check handles symlinks and all traversal types
                # by resolving the path *before* checking if it's within the root.
                if not await safe_is_within(target_path, self.anyio_root):
                    logger.warning(
                        "Skipping unsafe path: Resolves outside root",
                        path=rel_path_str,
                        resolved_to=str(target_path)
                    )
                    continue
                
                # Ensure parent directory exists
                if not self.dry_run:
                    await target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write the file
                if self.dry_run:
                    logger.info(f"[dry-run] Would rehydrate file to: {target_path}")
                else:
                    await target_path.write_text(content)
                    logger.debug(f"Rehydrated file: {target_path}")
                
                # ⚡ FIX: Append to created_files *only on success*
                created_files.append(Path(target_path))
                
            except Exception as e:
                logger.error(
                    "Failed to rehydrate file",
                    path=rel_path_str,
                    error=str(e)
                )
        
        logger.info(
            "Rehydration complete",
            files_created=len(created_files)
        )
        return created_files
```

---

## rollback/parser.py

<a id='rollback-parser-py'></a>

~~~python
# src/create_dump/rollback/parser.py

"""
Parses a create-dump Markdown file to extract file paths and content.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import AsyncGenerator, List, Tuple

import anyio

from ..logging import logger


class MarkdownParser:
    """
    Reads a .md dump file and parses it into a stream of
    (relative_path, content) tuples for rehydration.
    """

    def __init__(self, file_path: Path):
        self.file_path = file_path
        # Regex to find file headers, e.g., ## src/main.py
        self.header_regex = re.compile(r"^## (.*)$")
        # Regex to find code fences (both ``` and ~~~)
        self.fence_regex = re.compile(r"^(```|~~~)($|\w+)")
        # Regex to find and skip error blocks
        self.error_regex = re.compile(r"^> ⚠️ \*\*Failed:\*\*")

    async def parse_dump_file(self) -> AsyncGenerator[Tuple[str, str], None]:
        """
        Parses the dump file and yields tuples of (relative_path, content).
        """
        current_path: str | None = None
        content_lines: List[str] = []
        capturing = False
        current_fence: str | None = None

        try:
            async with await anyio.Path(self.file_path).open("r", encoding="utf-8") as f:
                async for line in f:
                    if capturing:
                        # Check for closing fence
                        if line.strip() == current_fence:
                            if current_path:
                                # Yield the complete file
                                yield (current_path, "".join(content_lines))
                            
                            # Reset state, wait for next header
                            capturing = False
                            current_path = None
                            content_lines = []
                            current_fence = None
                        else:
                            content_lines.append(line)
                    else:
                        # Not capturing, look for a new file header
                        header_match = self.header_regex.match(line.strip())
                        if header_match:
                            # Found a new file. Reset state and store path.
                            current_path = header_match.group(1).strip()
                            content_lines = []
                            capturing = False
                            current_fence = None
                            continue

                        # If we have a path, look for the opening fence
                        if current_path:
                            # Skip error blocks
                            if self.error_regex.match(line.strip()):
                                logger.warning(f"Skipping failed file in dump: {current_path}")
                                current_path = None # Reset, this file failed
                                continue

                            fence_match = self.fence_regex.match(line.strip())
                            if fence_match:
                                capturing = True
                                current_fence = fence_match.group(1) # Store fence type
                                # Do not append the fence line itself

        except FileNotFoundError:
            logger.error(f"Rollback failed: Dump file not found at {self.file_path}")
            raise
        except Exception as e:
            logger.error(f"Rollback failed: Error parsing dump file: {e}")
            raise
~~~

---

## single.py

<a id='single-py'></a>

```python
# src/create_dump/single.py

"""
Single dump runner.

This file is the "glue" layer that connects the CLI flags
from `cli/single.py` to the core orchestration logic.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import anyio
from typer import Exit

# ⚡ REFACTOR: Import new orchestration and watch modules
from .workflow.single import SingleRunOrchestrator
from .watch import FileWatcher
from .logging import styled_print


async def run_single(
    root: Path,
    dry_run: bool,
    yes: bool,
    no_toc: bool,
    tree_toc: bool,
    compress: bool,
    format: str,
    exclude: str,
    include: str,
    max_file_size: Optional[int],
    use_gitignore: bool,
    git_meta: bool,
    progress: bool,
    max_workers: int,
    archive: bool,
    archive_all: bool,
    archive_search: bool,
    archive_include_current: bool,
    archive_no_remove: bool,
    archive_keep_latest: bool,
    archive_keep_last: Optional[int],
    archive_clean_root: bool,
    archive_format: str,
    allow_empty: bool,
    metrics_port: int,
    verbose: bool,
    quiet: bool,
    dest: Optional[Path] = None,
    # ⚡ NEW: v8 feature flags
    watch: bool = False,
    git_ls_files: bool = False,
    diff_since: Optional[str] = None,
    scan_secrets: bool = False,
    hide_secrets: bool = False,
) -> None:
    
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"Invalid root: {root}")

    # Normalize cwd once at the start
    await anyio.to_thread.run_sync(os.chdir, root)
    
    # ⚡ REFACTOR: Handle `yes` logic for watch mode
    # If --watch is on, we don't want prompts on subsequent runs.
    effective_yes = yes or watch

    # ⚡ REFACTOR: Instantiate the orchestrator
    orchestrator = SingleRunOrchestrator(
        root=root,
        dry_run=dry_run,
        yes=effective_yes, # Pass the combined value
        no_toc=no_toc,
        tree_toc=tree_toc,
        compress=compress,
        format=format,
        exclude=exclude,
        include=include,
        max_file_size=max_file_size,
        use_gitignore=use_gitignore,
        git_meta=git_meta,
        progress=progress,
        max_workers=max_workers,
        archive=archive,
        archive_all=archive_all,
        archive_search=archive_search,
        archive_include_current=archive_include_current,
        archive_no_remove=archive_no_remove,
        archive_keep_latest=archive_keep_latest,
        archive_keep_last=archive_keep_last,
        archive_clean_root=archive_clean_root,
        archive_format=archive_format,
        allow_empty=allow_empty,
        metrics_port=metrics_port,
        verbose=verbose,
        quiet=quiet,
        dest=dest,
        git_ls_files=git_ls_files,
        diff_since=diff_since,
        scan_secrets=scan_secrets,
        hide_secrets=hide_secrets,
    )

    # ⚡ REFACTOR: Top-level control flow
    if watch:
        if not quiet:
            styled_print("[green]Running initial dump...[/green]")
        
        try:
            await orchestrator.run()
        except Exit as e:
            if getattr(e, "exit_code", None) == 0 and dry_run:
                 # Handle dry_run exit for the *initial* run
                 return
            raise # Re-raise other exits
        
        if not quiet:
            styled_print(f"\n[cyan]Watching for file changes in {root}... (Press Ctrl+C to stop)[/cyan]")
        
        watcher = FileWatcher(root=root, dump_func=orchestrator.run, quiet=quiet)
        await watcher.start()
    else:
        try:
            await orchestrator.run()
        except Exit as e:
            if getattr(e, "exit_code", None) == 0 and dry_run:
                # Handle dry_run exit
                return
            raise
```

---

## path_utils.py

<a id='path-utils-py'></a>

```python
# src/create_dump/path_utils.py

"""Shared utilities for path safety, discovery, and user confirmation."""

from __future__ import annotations

import logging
import re
from pathlib import Path
# ⚡ REFACTOR: Import AsyncGenerator
from typing import List, AsyncGenerator

import anyio  # ⚡ REFACTOR: Import anyio
from .logging import logger  # ⚡ REFACTOR: Import from logging

# ⚡ REFACTOR: Removed safe_is_within and find_matching_files
__all__ = ["safe_is_within", "confirm", "find_matching_files"]


# ⚡ REFACTOR: Removed synchronous safe_is_within function


# ⚡ NEW: Async version of safe_is_within for anyio.Path
async def safe_is_within(path: anyio.Path, root: anyio.Path) -> bool:
    """
    Async check if path is safely within root (relative/escape-proof).
    Handles anyio.Path objects by awaiting .resolve().
    """
    try:
        # 1. Await resolution for both paths
        resolved_path = await path.resolve()
        resolved_root = await root.resolve()
        
        # 2. Perform the check on the resulting sync pathlib.Path objects
        return resolved_path.is_relative_to(resolved_root)
    except AttributeError:
        # Fallback for Python < 3.9
        resolved_path = await path.resolve()
        resolved_root = await root.resolve()
        return str(resolved_path).startswith(str(resolved_root) + "/")


# ⚡ REFACTOR: Removed synchronous find_matching_files function


# ⚡ REFACTOR: New async version of find_matching_files
async def find_matching_files(root: Path, regex: str) -> AsyncGenerator[Path, None]:
    """Async glob files matching regex within root."""
    pattern = re.compile(regex)
    anyio_root = anyio.Path(root)
    # ⚡ REFACTOR: Yield paths directly instead of building a list
    async for p in anyio_root.rglob("*"):
        if pattern.search(p.name):
            yield Path(p)  # Yield as pathlib.Path


def confirm(prompt: str) -> bool:
    """Prompt user for yes/no; handles interrupt gracefully."""
    try:
        ans = input(f"{prompt} [y/N]: ").strip().lower()
    except KeyboardInterrupt:
        print()
        return False
    return ans in ("y", "yes")
```

---

## metrics.py

<a id='metrics-py'></a>

```python
# src/create_dump/metrics.py

"""Defines Prometheus metrics and the metrics server."""

from __future__ import annotations

from contextlib import contextmanager
from prometheus_client import Counter, Histogram, start_http_server

# Port
DEFAULT_METRICS_PORT = 8000

# Metrics
DUMP_DURATION = Histogram(
    "create_dump_duration_seconds",
    "Dump duration",
    buckets=[1, 5, 30, 60, 300, float("inf")],
    labelnames=["collector"],  # ⚡ REFACTOR: Add collector label
)
# 🐞 FIX: Add _total suffix for Prometheus convention
FILES_PROCESSED = Counter("create_dump_files_total", "Files processed", ["status"])
# 🐞 FIX: Add _total suffix for Prometheus convention
ERRORS_TOTAL = Counter("create_dump_errors_total", "Errors encountered", ["type"])
ROLLBACKS_TOTAL = Counter("create_dump_rollbacks_total", "Batch rollbacks", ["reason"])

# ✨ NEW: Add metric for archive creation
ARCHIVES_CREATED_TOTAL = Counter(
    "create_dump_archives_total",
    "Archives created",
    ["format"],
)


@contextmanager
def metrics_server(port: int = DEFAULT_METRICS_PORT):
    """Start configurable metrics server with auto-cleanup."""
    if port > 0:
        start_http_server(port)
    try:
        yield
    finally:
        pass  # Server runs in a daemon thread
```

---

## system.py

<a id='system-py'></a>

```python
# src/create_dump/system.py

"""Handles system-level interactions: signals, subprocesses, cleanup."""

from __future__ import annotations

import atexit
import os
import signal
import subprocess
import sys
import tempfile
from contextlib import ExitStack
from pathlib import Path
# ⚡ REFACTOR: Import List and Tuple
from typing import Any, Optional, List, Tuple
import asyncio  # ⚡ NEW: Import asyncio

import tenacity
# ⚡ FIX: Removed all deprecated anyio subprocess imports

from .core import GitMeta
from .logging import logger

# Constants
DEFAULT_MAX_WORKERS = min(16, (os.cpu_count() or 4) * 2)

# Globals for cleanup (thread-safe via ExitStack)
_cleanup_stack = ExitStack()
_temp_dir: Optional[tempfile.TemporaryDirectory] = None


class CleanupHandler:
    """Graceful shutdown on signals."""

    def __init__(self):
        signal.signal(signal.SIGINT, self._handler)
        signal.signal(signal.SIGTERM, self._handler)
        atexit.register(self._cleanup)

    def _handler(self, signum: int, frame: Any) -> None:
        logger.info("Shutdown signal received", signal=signum)
        self._cleanup()
        sys.exit(130 if signum == signal.SIGINT else 143)

    def _cleanup(self) -> None:
        global _temp_dir
        if _temp_dir:
            _temp_dir.cleanup()
        _cleanup_stack.close()


handler = CleanupHandler()  # Global handler


@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_exponential(multiplier=1, min=1, max=10),
    reraise=True,
)
def get_git_meta(root: Path) -> Optional[GitMeta]:
    """Fetch git metadata with timeout."""
    try:
        cmd_branch = ["git", "rev-parse", "--abbrev-ref", "HEAD"]
        cmd_commit = ["git", "rev-parse", "--short", "HEAD"]
        branch = (
            subprocess.check_output(
                cmd_branch, cwd=root, stderr=subprocess.DEVNULL, timeout=10
            )
            .decode()
            .strip()
        )
        commit = (
            subprocess.check_output(
                cmd_commit, cwd=root, stderr=subprocess.DEVNULL, timeout=10
            )
            .decode()
            .strip()
        )
        return GitMeta(branch=branch, commit=commit)
    except (
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        FileNotFoundError,
    ):
        logger.debug("Git meta unavailable", root=root)
        return None


# ⚡ NEW: Internal helper for running asyncio subprocesses
async def _run_async_cmd(cmd: List[str], cwd: Path) -> Tuple[str, str, int]:
    """
    Run a command asynchronously and return (stdout, stderr, returncode).
    """
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=cwd,  # ⚡ Run in the specified root directory
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout_bytes, stderr_bytes = await proc.communicate()

    return (
        stdout_bytes.decode().strip(),
        stderr_bytes.decode().strip(),
        proc.returncode,
    )


# ⚡ REFACTOR: Rewritten to use asyncio.subprocess
async def get_git_ls_files(root: Path) -> List[str]:
    """Run 'git ls-files' asynchronously and return the file list."""
    cmd = ["git", "ls-files", "-co", "--exclude-standard"]
    try:
        stdout, stderr, code = await _run_async_cmd(cmd, cwd=root)
        
        if code != 0:
            logger.error(
                "git ls-files failed", 
                retcode=code, 
                error=stderr
            )
            return []
            
        return [line.strip() for line in stdout.splitlines() if line.strip()]

    except Exception as e:
        logger.error("Failed to run git ls-files", error=str(e))
        return []


# ⚡ REFACTOR: Rewritten to use asyncio.subprocess
async def get_git_diff_files(root: Path, ref: str) -> List[str]:
    """Run 'git diff --name-only' asynchronously and return the file list."""
    cmd = ["git", "diff", "--name-only", ref]
    try:
        stdout, stderr, code = await _run_async_cmd(cmd, cwd=root)
        
        if code != 0:
            logger.error(
                "git diff failed", 
                ref=ref,
                retcode=code, 
                error=stderr
            )
            return []

        return [line.strip() for line in stdout.splitlines() if line.strip()]
        
    except Exception as e:
        logger.error("Failed to run git diff", ref=ref, error=str(e))
        return []
```

---

## processor.py

<a id='processor-py'></a>

```python
# src/create_dump/processor.py

"""
File Processing Component.

Reads all source files and saves their raw content to temporary files
for later consumption by formatters (Markdown, JSON, etc.).
"""

from __future__ import annotations

import uuid
from pathlib import Path
# ⚡ REFACTOR: Import List, Optional, Callable, Awaitable, Protocol
from typing import List, Optional, Any, Callable, Awaitable, Protocol

import anyio
from anyio.abc import TaskStatus

# ⚡ REFACTOR: Removed all detect-secrets imports

from .core import DumpFile
from .helpers import CHUNK_SIZE, get_language
from .logging import (
    HAS_RICH, Progress, SpinnerColumn, TextColumn, console, logger
)
from .metrics import FILES_PROCESSED, ERRORS_TOTAL
from .system import DEFAULT_MAX_WORKERS


# ⚡ NEW: Define a simple Protocol for middleware
class ProcessorMiddleware(Protocol):
    async def process(self, dump_file: DumpFile) -> None:
        """Processes a DumpFile. Can modify it in-place."""
        ...


class FileProcessor:
    """
    Reads source files concurrently and stores their content in temp files.
    """

    # ⚡ REFACTOR: Update __init__ to accept middleware
    def __init__(
        self, 
        temp_dir: str, 
        middlewares: List[ProcessorMiddleware] | None = None
    ):
        self.temp_dir = temp_dir
        self.files: List[DumpFile] = []
        self.middlewares = middlewares or []
        
    # ⚡ REFACTOR: Removed _scan_for_secrets
    # ⚡ REFACTOR: Removed _redact_secrets

    async def process_file(self, file_path: str) -> DumpFile:
        """Concurrently read and write file content to temp (streamed)."""
        temp_anyio_path: Optional[anyio.Path] = None
        dump_file: Optional[DumpFile] = None
        
        try:
            temp_filename = f"{uuid.uuid4().hex}.tmp"
            temp_anyio_path = anyio.Path(self.temp_dir) / temp_filename
            
            lang = get_language(file_path)
            
            async with await anyio.Path(file_path).open("r", encoding="utf-8", errors="replace") as src, \
                       await temp_anyio_path.open("w", encoding="utf-8") as tmp:
                
                peek = await src.read(CHUNK_SIZE)
                if peek:
                    # ⚡ REFACTOR: Write only the raw content.
                    await tmp.write(peek)
                    while chunk := await src.read(CHUNK_SIZE):
                        await tmp.write(chunk)
            
            # Create the successful DumpFile object
            dump_file = DumpFile(path=file_path, language=lang, temp_path=Path(temp_anyio_path))

            # ⚡ NEW: Run middleware chain
            for middleware in self.middlewares:
                await middleware.process(dump_file)
                if dump_file.error:
                    # Middleware failed this file (e.g., secrets found)
                    # The middleware is responsible for logging and metrics
                    return dump_file

            FILES_PROCESSED.labels(status="success").inc()
            return dump_file
        
        except Exception as e:
            if temp_anyio_path is not None:
                await temp_anyio_path.unlink(missing_ok=True)
            
            ERRORS_TOTAL.labels(type="process").inc()
            
            logger.error("File process error", path=file_path, error=str(e))
            # Return an error DumpFile
            return DumpFile(path=file_path, error=str(e))

    async def dump_concurrent(
        self,
        files_list: List[str],
        progress: bool = False,
        max_workers: int = DEFAULT_MAX_WORKERS,
    ) -> List[DumpFile]:
        """
        Parallel temp file creation with progress.
        
        Returns the list of processed DumpFile objects.
        """
        
        limiter = anyio.Semaphore(max_workers)
        self.files = [] # Ensure list is fresh for this run

        async def _process_wrapper(
            file_path: str, 
            prog: Optional[Progress] = None, 
            task_id: Optional[TaskStatus] = None
        ):
            """Wrapper to handle timeouts, limiting, and progress bar."""
            async with limiter:
                try:
                    with anyio.fail_after(60):  # 60-second timeout
                        result = await self.process_file(file_path)
                        self.files.append(result)
                except TimeoutError:
                    ERRORS_TOTAL.labels(type="timeout").inc()
                    self.files.append(DumpFile(path=file_path, error="Timeout"))
                except Exception as e:
                    ERRORS_TOTAL.labels(type="process").inc()
                    self.files.append(DumpFile(path=file_path, error=f"Unhandled exception: {e}"))
                finally:
                    if prog and task_id is not None:
                        prog.advance(task_id)

        async with anyio.create_task_group() as tg:
            if progress and HAS_RICH and console:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as prog:
                    task_id = prog.add_task("Processing files...", total=len(files_list))
                    for f in files_list:
                        tg.start_soon(_process_wrapper, f, prog, task_id)
            else:
                for f in files_list:
                    tg.start_soon(_process_wrapper, f, None, None)
        
        # Return the processed files list
        return self.files
```

---

## version.py

<a id='version-py'></a>

```python
# src/create_dump/version.py

"""Version module (single source of truth)."""

# ⚡ REFACTOR: Use __version__ for build tools
__version__ = "10.0.0"

# ⚡ REFACTOR: Keep VERSION for internal compatibility
VERSION = __version__
```

---

## orchestrator.py

<a id='orchestrator-py'></a>

```python
# src/create_dump/orchestrator.py

"""Batch orchestration: Multi-subdir dumps, centralization, compression, cleanup."""

from __future__ import annotations

import re
import sys
import uuid
import shutil
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple, Union

import anyio

from .archiver import ArchiveManager
# ⚡ FIX: Import the renamed async function
from .cleanup import safe_delete_paths
from .core import Config, load_config, DEFAULT_DUMP_PATTERN
# ⚡ FIX: Import the renamed async functions
from .path_utils import confirm, find_matching_files, safe_is_within
# ⚡ FIX: Import the renamed async function
from .single import run_single
from .logging import logger, styled_print
from .metrics import DUMP_DURATION, ROLLBACKS_TOTAL

# ⚡ FIX: Renamed __all__
__all__ = ["run_batch"]


class AtomicBatchTxn:
    """Atomic staging for batch outputs: commit/rollback via rename/rmtree."""

    def __init__(self, root: Path, dest: Optional[Path], run_id: str, dry_run: bool):
        self.root = root
        self.dest = dest
        self.run_id = run_id
        self.dry_run = dry_run
        self.staging: Optional[anyio.Path] = None

    async def __aenter__(self) -> Optional[anyio.Path]:
        if self.dry_run:
            self.staging = None
            return None
        
        staging_parent = self.root / "archives" if not self.dest else (
            self.dest.resolve() if self.dest.is_absolute() else self.root / self.dest
        )
        
        anyio_staging_parent = anyio.Path(staging_parent)
        anyio_root = anyio.Path(self.root)
        if not await safe_is_within(anyio_staging_parent, anyio_root):
            raise ValueError("Staging parent outside root boundary")

        self.staging = anyio.Path(staging_parent / f".staging-{self.run_id}")
        await self.staging.mkdir(parents=True, exist_ok=True)
        return self.staging

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if not self.staging:
            return
        if exc_type is None:
            final_name = self.staging.name.replace(".staging-", "")
            final_path = self.staging.parent / final_name
            await self.staging.rename(final_path)
            logger.info("Batch txn committed: %s -> %s", self.staging, final_path)
        else:
            try:
                await anyio.to_thread.run_sync(shutil.rmtree, self.staging)
            except OSError:
                pass
            # ⚡ FIX: Call .labels() before .inc() for Prometheus
            ROLLBACKS_TOTAL.labels(reason=str(exc_val)[:100]).inc()
            logger.error("Batch txn rolled back due to: %s", exc_val)


@asynccontextmanager
async def atomic_batch_txn(root: Path, dest: Optional[Path], run_id: str, dry_run: bool):
    txn = AtomicBatchTxn(root, dest, run_id, dry_run)
    staging = await txn.__aenter__()
    try:
        yield staging
    finally:
        await txn.__aexit__(*sys.exc_info())


# ⚡ RENAMED: Function
async def _centralize_outputs(
    dest_path: Union[anyio.Path, Path],
    root: Path,
    successes: List[Path],
    compress: bool,
    yes: bool,
    dump_pattern: str
) -> None:
    if isinstance(dest_path, Path):
        dest_path = anyio.Path(dest_path)
    await dest_path.mkdir(parents=True, exist_ok=True)
    moved = 0
    
    # ⚡ FIX: This regex must match *all* artifacts, not just .md
    # We'll use the .md pattern to find the *base* and then move its .sha256
    md_regex = re.compile(dump_pattern)
    anyio_root = anyio.Path(root)

    for sub_root in successes:
        anyio_sub_root = anyio.Path(sub_root)
        # Find only the .md files first
        all_md_files = [
            f async for f in anyio_sub_root.glob("*.md") 
            if await f.is_file() and md_regex.match(f.name)
        ]

        for md_file_path in all_md_files:
            sha_file_path = md_file_path.with_suffix(".sha256")
            
            # Create a list of files to move for this pair
            files_to_move = [md_file_path]
            if await sha_file_path.exists():
                files_to_move.append(sha_file_path)
            else:
                # This check is now redundant because validate_batch_staging will catch it,
                # but it's good practice to log here.
                logger.warning("Missing SHA256 for dump, moving .md only", path=str(md_file_path))

            for file_path in files_to_move:
                if not await safe_is_within(file_path, anyio_root):
                    logger.warning("Skipping unsafe dump artifact: %s", file_path)
                    continue

                target = dest_path / file_path.name
                if await target.exists():
                    await target.unlink()
                await file_path.rename(target)
                
                if file_path.suffix == ".md":
                    moved += 1 # Count pairs
                
                to_type = "staging" if "staging" in str(dest_path) else "dest"
                logger.info("Moved dump artifact to %s: %s -> %s", to_type, file_path, target)

    logger.info("Centralized %d dump pairs to %s", moved, dest_path)


async def validate_batch_staging(staging: anyio.Path, pattern: str) -> bool:
    """Validate: All MD have SHA, non-empty."""
    dump_regex = re.compile(pattern)
    md_files = []
    async for f in staging.rglob("*"):
        if await f.is_file() and dump_regex.match(f.name) and f.suffix == ".md":
            md_files.append(f)
    if not md_files:
        return False
    has_sha = True
    for f in md_files:
        sha_path = f.with_suffix(".sha256")
        if not await sha_path.exists():
            has_sha = False
            logger.error("Validation failed: Missing SHA256", md_file=str(f))
            break
    return has_sha


# ⚡ RENAMED: Function
async def run_batch(
    root: Path,
    subdirs: List[str],
    pattern: str,
    dry_run: bool,
    yes: bool,
    accept_prompts: bool,
    compress: bool,
    max_workers: int,
    verbose: bool,
    quiet: bool,
    dest: Optional[Path] = None,
    archive: bool = False,
    archive_all: bool = False,
    archive_search: bool = False,
    archive_include_current: bool = True,
    archive_no_remove: bool = False,
    archive_keep_latest: bool = True,
    archive_keep_last: Optional[int] = None,
    archive_clean_root: bool = False,
    atomic: bool = True,
) -> None:
    root = root.resolve()
    cfg = load_config()

    if not re.match(r'.*_all_create_dump_', pattern):
        logger.warning("Enforcing canonical pattern: %s", cfg.dump_pattern)
        pattern = cfg.dump_pattern

    atomic = not dry_run and atomic

    # Common: Resolve sub_roots & pre-cleanup
    sub_roots = []
    for sub in subdirs:
        sub_path = root / sub
        if await anyio.Path(sub_path).exists():
            sub_roots.append(sub_path)
    if not sub_roots:
        logger.warning("No valid subdirs: %s", subdirs)
        return

    # ⚡ FIX: Consume the async generator from find_matching_files into a list.
    matches = [p async for p in find_matching_files(root, pattern)]
    
    if matches and not dry_run and not archive_all:
        if yes or await anyio.to_thread.run_sync(confirm, "Delete old dumps?"):
            # ⚡ FIX: Call renamed async function
            deleted, _ = await safe_delete_paths(matches, root, dry_run, yes)
            if verbose:
                logger.info("Pre-cleanup: %d deleted", deleted)

    successes: List[Path] = []
    failures: List[Tuple[Path, str]] = []

    async def _run_single_wrapper(sub_root: Path):
        try:
            # ⚡ FIX: Call renamed async function
            await run_single(
                root=sub_root, dry_run=dry_run, yes=accept_prompts or yes, no_toc=False,
                compress=compress, exclude="", include="", max_file_size=cfg.max_file_size_kb,
                use_gitignore=cfg.use_gitignore, git_meta=cfg.git_meta, progress=False,
                max_workers=16, archive=False, archive_all=False, archive_search=False,
                archive_include_current=archive_include_current, archive_no_remove=archive_no_remove,
                archive_keep_latest=archive_keep_latest, archive_keep_last=archive_keep_last,
                archive_clean_root=archive_clean_root, allow_empty=True, metrics_port=0,
                verbose=verbose, quiet=quiet,
            )
            successes.append(sub_root)
            if not quiet:
                styled_print(f"[green]✅ Dumped {sub_root}[/green]")
        except Exception as e:
            failures.append((sub_root, str(e)))
            logger.error("Subdir failed", subdir=sub_root, error=str(e))
            if not quiet:
                styled_print(f"[red]❌ Failed {sub_root}: {str(e).split('from e')[-1].strip()}[/red]")

    # ⚡ FIX: Add 'collector' label for metrics
    with DUMP_DURATION.labels(collector="batch").time():
        limiter = anyio.Semaphore(max_workers)
        async with anyio.create_task_group() as tg:
            for sub_root in sub_roots:
                async def limited_wrapper(sub_root=Path(sub_root)):
                    async with limiter:
                        await _run_single_wrapper(sub_root)
                tg.start_soon(limited_wrapper)

    if not successes:
        logger.info("No successful dumps.")
        return

    run_id = uuid.uuid4().hex[:8]
    if atomic:
        async with atomic_batch_txn(root, dest, run_id, dry_run) as staging:
            if staging is None:
                return  # Dry run complete

            await _centralize_outputs(staging, root, successes, compress, yes, pattern)
            
            if not await validate_batch_staging(staging, pattern):
                # Raise validation error *before* archiving
                raise ValueError("Validation failed: Incomplete dumps")

            if archive or archive_all:
                timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
                staging_path = Path(staging)
                manager = ArchiveManager(
                    root=staging_path,
                    timestamp=timestamp, keep_latest=archive_keep_latest, keep_last=archive_keep_last,
                    clean_root=archive_clean_root, search=archive_search,
                    include_current=archive_include_current, no_remove=archive_no_remove,
                    dry_run=dry_run, yes=yes, verbose=verbose, md_pattern=pattern, archive_all=archive_all,
                )
                archive_results = await manager.run()
                if verbose:
                    logger.debug("Archiving in staging: search=%s, all=%s", archive_search, archive_all)
                if archive_results and any(archive_results.values()):
                    groups = ', '.join(k for k, v in archive_results.items() if v)
                    logger.info("Archived: %s", groups)
                    if not quiet:
                        styled_print(f"[green]📦 Archived: {groups}[/green]")
                else:
                    logger.info("No dumps for archiving.")
            
    else: # Not atomic
        if dry_run:
            logger.info("[dry-run] Would centralize files to non-atomic dest.")
            return

        central_dest = dest or root / "archives"
        await _centralize_outputs(central_dest, root, successes, compress, yes, pattern)
        
        if not await validate_batch_staging(anyio.Path(central_dest), pattern):
            logger.warning("Validation failed: Incomplete dumps in non-atomic destination.")
            # Do not raise, as this is non-transactional

        if archive or archive_all:
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            manager = ArchiveManager(
                root=root, timestamp=timestamp, keep_latest=archive_keep_latest, keep_last=archive_keep_last,
                clean_root=archive_clean_root, search=archive_search, include_current=archive_include_current,
                no_remove=archive_no_remove, dry_run=dry_run, yes=yes, verbose=verbose,
                md_pattern=pattern, archive_all=archive_all,
            )
            archive_results = await manager.run()
            if archive_results and any(archive_results.values()):
                groups = ', '.join(k for k, v in archive_results.items() if v)
                logger.info("Archived: %s", groups)
                if not quiet:
                    styled_print(f"[green]📦 Archived: {groups}[/green]")
            else:
                logger.info("No dumps for archiving.")

    logger.info("Batch complete: %d/%d successes", len(successes), len(sub_roots))
    if failures and verbose:
        for sub_root, err in failures:
            logger.error("Failure: %s - %s", sub_root, err)
    if not quiet:
        styled_print(f"[green]✅ Batch: {len(successes)}/{len(sub_roots)}[/green]")
```

---

## watch.py

<a id='watch-py'></a>

```python
# src/create_dump/watch.py

"""File watcher and debouncing logic."""

from __future__ import annotations
from pathlib import Path
from typing import Callable, Awaitable

import anyio
from anyio import Event

from .logging import logger, styled_print


class FileWatcher:
    """Runs an async file watcher with debouncing."""
    
    DEBOUNCE_MS = 500  # 500ms debounce window 

    def __init__(self, root: Path, dump_func: Callable[[], Awaitable[None]], quiet: bool):
        self.root = root
        self.dump_func = dump_func
        self.quiet = quiet
        self.debounce_event = Event()

    async def _debouncer(self):
        """Waits for an event, then sleeps, then runs the dump."""
        while True:
            await self.debounce_event.wait()
            
            # 🐞 FIX: An anyio.Event is not cleared on wait().
            # We must re-create the event to reset its state and
            # prevent the loop from re-triggering immediately.
            self.debounce_event = Event()
            
            await anyio.sleep(self.DEBOUNCE_MS / 1000)
            
            if not self.quiet:
                styled_print(f"\n[yellow]File change detected, running dump...[/yellow]")
            try:
                await self.dump_func()
            except Exception as e:
                # Log error but don't kill the watcher 
                logger.error("Error in watched dump run", error=str(e))
                if not self.quiet:
                    styled_print(f"[red]Error in watched dump: {e}[/red]")

    async def start(self):
        """Starts the file watcher and debouncer."""
        try:
            async with anyio.create_task_group() as tg:
                tg.start_soon(self._debouncer)
                
                # Use anyio's native async watcher 
                async for _ in anyio.Path(self.root).watch(recursive=True):
                    self.debounce_event.set()
        except KeyboardInterrupt:
            if not self.quiet:
                styled_print("\n[cyan]Watch mode stopped.[/cyan]")
```

---

## writing/checksum.py

<a id='writing-checksum-py'></a>

```python
# src/create_dump/writing/checksum.py

"""Checksum generation and writing logic."""

from __future__ import annotations

import hashlib
from pathlib import Path
import tenacity
import anyio  # ⚡ REFACTOR: Import anyio
from ..helpers import CHUNK_SIZE  # Refactored import


class ChecksumWriter:
    """Secure checksum with retries."""

    @tenacity.retry(stop=tenacity.stop_after_attempt(3), wait=tenacity.wait_fixed(1))
    # ⚡ REFACTOR: Converted to async
    async def write(self, path: Path) -> str:
        """
        Calculates the SHA256 checksum of a file and writes it to a .sha256 file.
        
        NOTE: Doctest was removed as it does not support async functions.
        This logic must be tested with pytest-anyio.
        """
        sha = hashlib.sha256()
        anyio_path = anyio.Path(path)
        
        # ⚡ REFACTOR: Use async file open and read
        async with await anyio_path.open("rb") as f:
            while True:
                chunk = await f.read(CHUNK_SIZE)
                if not chunk:
                    break
                sha.update(chunk)
                
        checksum = f"{sha.hexdigest()}  {path.name}"
        
        # ⚡ REFACTOR: Use async file write
        anyio_checksum_file = anyio.Path(path.with_suffix(".sha256"))
        await anyio_checksum_file.write_text(checksum + "\n")
        
        return checksum
```

---

## writing/json.py

<a id='writing-json-py'></a>

```python
# src/create_dump/writing/json.py

"""JSON writing logic.
Consumes processed files and formats them as JSON.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any

import anyio

from ..core import DumpFile, GitMeta
from ..helpers import CHUNK_SIZE
from ..logging import logger


class JsonWriter:
    """Streams JSON output from processed temp files."""

    def __init__(self, outfile: Path):
        self.outfile = outfile
        self.files: List[DumpFile] = []  # Stored for metrics

    async def write(
        self, 
        files: List[DumpFile], 
        git_meta: Optional[GitMeta], 
        version: str
    ) -> None:
        """Writes the final JSON file from the list of processed files."""
        self.files = files  # Store for metrics
        
        data: Dict[str, Any] = {
            "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "version": version,
            "git_meta": git_meta.model_dump() if git_meta else None,
            "files": []
        }

        for df in self.files:
            if df.error:
                data["files"].append({
                    "path": df.path,
                    "language": df.language,
                    "error": df.error,
                    "content": None
                })
            elif df.temp_path:
                try:
                    content = await self._read_temp_file(df.temp_path)
                    data["files"].append({
                        "path": df.path,
                        "language": df.language,
                        "error": None,
                        "content": content
                    })
                except Exception as e:
                    logger.error("Failed to read temp file for JSON dump", path=df.path, error=str(e))
                    data["files"].append({
                        "path": df.path,
                        "language": df.language,
                        "error": f"Failed to read temp file: {e}",
                        "content": None
                    })

        await self._write_json(data)

    async def _read_temp_file(self, temp_path: Path) -> str:
        """Reads the raw content from a temp file."""
        return await anyio.Path(temp_path).read_text(encoding="utf-8", errors="replace")

    async def _write_json(self, data: Dict[str, Any]) -> None:
        """Writes the data dictionary to the output file atomically."""
        temp_out = anyio.Path(self.outfile.with_suffix(".tmp"))
        try:
            # Run blocking json.dumps in a thread
            # 🐞 FIX: Wrap the call in a lambda to pass the keyword argument
            json_str = await anyio.to_thread.run_sync(
                lambda: json.dumps(data, indent=2)
            )
            
            async with await temp_out.open("w", encoding="utf-8") as f:
                await f.write(json_str)
            
            await temp_out.rename(self.outfile)
            logger.info("JSON written atomically", path=self.outfile)
        except Exception:
            if await temp_out.exists():
                await temp_out.unlink()
            raise
```

---

## writing/markdown.py

<a id='writing-markdown-py'></a>

~~~python
# src/create_dump/writing/markdown.py

"""Markdown writing logic.
Consumes processed files and formats them as Markdown.
"""

from __future__ import annotations

import datetime
import uuid
from datetime import timezone
from pathlib import Path
from typing import List, Optional, Dict, Any

import anyio

from ..core import DumpFile, GitMeta
from ..helpers import CHUNK_SIZE, get_language, slugify
from ..logging import logger
from ..version import VERSION


class MarkdownWriter:
    """Streams Markdown output from processed temp files."""

    def __init__(
        self,
        outfile: Path,
        no_toc: bool,
        tree_toc: bool,
    ):
        self.outfile = outfile
        self.no_toc = no_toc
        self.tree_toc = tree_toc
        self.files: List[DumpFile] = []  # Stored for metrics
        self.git_meta: Optional[GitMeta] = None
        self.version: str = VERSION

    async def write(
        self, 
        files: List[DumpFile], 
        git_meta: Optional[GitMeta], 
        version: str
    ) -> None:
        """Writes the final Markdown file from the list of processed files."""
        self.files = files  # Store for metrics
        self.git_meta = git_meta
        self.version = version
        
        await self._write_md_streamed()

    async def _write_md_streamed(self) -> None:
        """Stream final MD from temps atomically."""
        temp_out = anyio.Path(self.outfile.with_suffix(".tmp"))
        try:
            async with await temp_out.open("w", encoding="utf-8") as out:
                now = datetime.datetime.now(timezone.utc)
                
                await out.write("# 🗃️ Project Code Dump\n\n")
                await out.write(f"**Generated:** {now.isoformat(timespec='seconds')} UTC\n")
                await out.write(f"**Version:** {self.version}\n")
                if self.git_meta:
                    await out.write(
                        f"**Git Branch:** {self.git_meta.branch} | **Commit:** {self.git_meta.commit}\n"
                    )
                await out.write("\n---\n\n")

                if not self.no_toc:
                    await out.write("## Table of Contents\n\n")
                    
                    valid_files = [df for df in self.files if not df.error and df.temp_path]
                    
                    if self.tree_toc:
                        file_tree: Dict[str, Any] = {}
                        for df in valid_files:
                            parts = df.path.split('/')
                            current_level = file_tree
                            for part in parts[:-1]:
                                current_level = current_level.setdefault(part, {})
                            current_level[parts[-1]] = df
                        
                        await self._render_tree_level(out, file_tree)
                    else:
                        for idx, df in enumerate(valid_files, 1):
                            anchor = slugify(df.path)
                            await out.write(f"{idx}. [{df.path}](#{anchor})\n")
                            
                    await out.write("\n---\n\n")

                for df in self.files:
                    if df.error:
                        await out.write(
                            f"## {df.path}\n\n> ⚠️ **Failed:** {df.error}\n\n---\n\n"
                        )
                    elif df.temp_path:
                        lang = get_language(df.path)
                        has_backtick = False  # Check content for backticks
                        
                        # Read temp file to check for backticks
                        temp_content = await anyio.Path(df.temp_path).read_text(encoding="utf-8", errors="replace")
                        if "```" in temp_content:
                            has_backtick = True
                        
                        fence = "~~~" if has_backtick else "```"
                        
                        anchor = slugify(df.path)
                        await out.write(f"## {df.path}\n\n<a id='{anchor}'></a>\n\n")
                        
                        # Write fence and content
                        await out.write(f"{fence}{lang}\n")
                        await out.write(temp_content)
                        await out.write(f"\n{fence}\n\n---\n\n")

            await temp_out.rename(self.outfile)
            logger.info("MD written atomically", path=self.outfile)
        except Exception:
            if await temp_out.exists():
                await temp_out.unlink()
            raise
        finally:
            # NOTE: Final temp file cleanup is handled by the `temp_dir`
            # context manager in `single.py`.
            pass

    async def _render_tree_level(
        self,
        out_stream: anyio.abc.Stream,
        level_dict: dict,
        prefix: str = "",
    ):
        """Recursively writes the file tree to the output stream."""
        
        # Sort items so files appear before sub-directories
        sorted_items = sorted(level_dict.items(), key=lambda item: isinstance(item[1], dict))
        
        for i, (name, item) in enumerate(sorted_items):
            is_last = (i == len(sorted_items) - 1)
            connector = "└── " if is_last else "├── "
            line = f"{prefix}{connector}{name}"
            
            if isinstance(item, dict):  # It's a directory
                await out_stream.write(f"{line}\n")
                # 🐞 FIX: Use regular spaces, not non-breaking spaces
                new_prefix = prefix + ("    " if is_last else "│   ")
                await self._render_tree_level(out_stream, item, new_prefix)
            else:  # It's a DumpFile
                anchor = slugify(item.path)
                await out_stream.write(f"{line} ([link](#{anchor}))\n")
~~~

---

## workflow/single.py

<a id='workflow-single-py'></a>

```python
# src/create_dump/workflow/single.py

"""The core single-run orchestration logic."""

from __future__ import annotations

import gzip
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List, Optional
from typer import Exit

import anyio

# Local project imports
from ..archiver import ArchiveManager
from ..collector import get_collector
from ..core import Config, GitMeta, load_config
# ⚡ REFACTOR: Import the async safety check
from ..path_utils import safe_is_within
from ..helpers import _unique_path
from ..logging import logger, styled_print
from ..metrics import DUMP_DURATION, metrics_server
from ..system import get_git_meta
from ..processor import FileProcessor, ProcessorMiddleware
from ..writing import ChecksumWriter, MarkdownWriter, JsonWriter
from ..version import VERSION
from ..scanning import SecretScanner


class SingleRunOrchestrator:
    """Orchestrates a complete, single dump run."""

    def __init__(
        self,
        root: Path,
        dry_run: bool,
        yes: bool,
        no_toc: bool,
        tree_toc: bool,
        compress: bool,
        format: str,
        exclude: str,
        include: str,
        max_file_size: Optional[int],
        use_gitignore: bool,
        git_meta: bool,
        progress: bool,
        max_workers: int,
        archive: bool,
        archive_all: bool,
        archive_search: bool,
        archive_include_current: bool,
        archive_no_remove: bool,
        archive_keep_latest: bool,
        archive_keep_last: Optional[int],
        archive_clean_root: bool,
        archive_format: str,
        allow_empty: bool,
        metrics_port: int,
        verbose: bool,
        quiet: bool,
        dest: Optional[Path] = None,
        git_ls_files: bool = False,
        diff_since: Optional[str] = None,
        scan_secrets: bool = False,
        hide_secrets: bool = False,
    ):
        # Store all parameters as instance attributes
        self.root = root
        self.dry_run = dry_run
        self.yes = yes
        self.no_toc = no_toc
        self.tree_toc = tree_toc
        self.compress = compress
        self.format = format
        self.exclude = exclude
        self.include = include
        self.max_file_size = max_file_size
        self.use_gitignore = use_gitignore
        self.git_meta = git_meta
        self.progress = progress
        self.max_workers = max_workers
        self.archive = archive
        self.archive_all = archive_all
        self.archive_search = archive_search
        self.archive_include_current = archive_include_current
        self.archive_no_remove = archive_no_remove
        self.archive_keep_latest = archive_keep_latest
        self.archive_keep_last = archive_keep_last
        self.archive_clean_root = archive_clean_root
        self.archive_format = archive_format
        self.allow_empty = allow_empty
        self.metrics_port = metrics_port
        self.verbose = verbose
        self.quiet = quiet
        self.dest = dest
        self.git_ls_files = git_ls_files
        self.diff_since = diff_since
        self.scan_secrets = scan_secrets
        self.hide_secrets = hide_secrets
        
        # ⚡ REFACTOR: Store anyio.Path version of root
        self.anyio_root = anyio.Path(self.root)

    
    # ⚡ FIX: Removed 'async' keyword. This must be a sync function.
    def _get_total_size_sync(self, files: List[str]) -> int:
        """Helper to run blocking stat() calls in a thread."""
        size = 0
        for f in files:
            try:
                # This is a blocking call, which is why the func is run in a thread
                size += (self.root / f).stat().st_size
            except FileNotFoundError:
                pass  # File may have vanished, skip
        return size

    def _compress_file_sync(self, in_file: Path, out_file: Path):
        """Blocking helper to gzip a file."""
        with open(in_file, "rb") as f_in, gzip.open(out_file, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    async def run(self):
        """The core logic for a single dump run."""
        
        # Load config on each run, in case it changed
        cfg = load_config()
        if self.max_file_size is not None:
            cfg.max_file_size_kb = self.max_file_size

        # Apply config defaults for new flags
        # CLI flags take precedence (if True), otherwise use config file
        
        effective_git_ls_files = self.git_ls_files or cfg.git_ls_files
        effective_scan_secrets = self.scan_secrets or cfg.scan_secrets
        effective_hide_secrets = self.hide_secrets or cfg.hide_secrets

        includes = [p.strip() for p in self.include.split(",") if p.strip()]
        excludes = [p.strip() for p in self.exclude.split(",") if p.strip()]

        # ⚡ FIX: Use the 'get_collector' factory function
        collector = get_collector(
            config=cfg, 
            includes=includes, 
            excludes=excludes, 
            use_gitignore=self.use_gitignore, 
            root=self.root,
            git_ls_files=effective_git_ls_files,
            diff_since=self.diff_since, # diff_since is CLI-only, not in config
        )
        files_list = await collector.collect()

        if not files_list:
            msg = "⚠️ No matching files found; skipping dump."
            logger.warning(msg)
            if self.verbose:
                logger.debug("Excludes: %s, Includes: %s", excludes, includes)
            if not self.quiet:
                styled_print(f"[yellow]{msg}[/yellow]")
            if not self.allow_empty:
                raise Exit(code=1)
            return

        # ⚡ FIX: This call is now correct, as it's passing a sync func
        total_size = await anyio.to_thread.run_sync(self._get_total_size_sync, files_list)

        logger.info(
            "Collection complete",
            count=len(files_list),
            total_size_kb=total_size / 1024,
            root=str(self.root),
        )
        if not self.quiet:
            styled_print(
                f"[green]📄 Found {len(files_list)} files ({total_size / 1024:.1f} KB total).[/green]"
            )

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        foldername = self.root.name or "project"
        
        file_ext = "json" if self.format == "json" else "md"
        branded_name = Path(f"{foldername}_all_create_dump_{timestamp}.{file_ext}")
        
        output_dest = self.root
        if self.dest:
            output_dest = self.dest.resolve()
            if not output_dest.is_absolute():
                output_dest = self.root / self.dest
            
            # ⚡ REFACTOR: (Target 1) Use await and async check
            anyio_output_dest = anyio.Path(output_dest)
            if not await safe_is_within(anyio_output_dest, self.anyio_root):
                logger.warning("Absolute dest outside root; proceeding with caution.")
            await anyio_output_dest.mkdir(parents=True, exist_ok=True)
        
        base_outfile = output_dest / branded_name
        
        prompt_outfile = await anyio.to_thread.run_sync(_unique_path, base_outfile)

        if not self.yes and not self.dry_run and not self.quiet:
            styled_print(
                f"Proceed with dump to [blue]{prompt_outfile}[/blue]? [yellow](y/n)[/yellow]",
                nl=False,
            )
            user_input = await anyio.to_thread.run_sync(input, "")
            if not user_input.lower().startswith("y"):
                styled_print("[red]Cancelled.[/red]")
                raise Exit(code=1)

        try:
            if self.dry_run:
                styled_print("[green]✅ Dry run: Would process listed files.[/green]")
                if not self.quiet:
                    for p in files_list:
                        styled_print(f" - {p}")
                raise Exit(code=0)


            outfile = await anyio.to_thread.run_sync(_unique_path, base_outfile)
            gmeta = await anyio.to_thread.run_sync(get_git_meta, self.root) if self.git_meta else None

            temp_dir = TemporaryDirectory()
            try:
                processed_files: List[DumpFile] = []
                
                # ⚡ FIX: Determine collector label BEFORE starting timer
                if self.diff_since:
                    collector_label = "git_diff"
                elif effective_git_ls_files: # Use the same var as collector
                    collector_label = "git_ls"
                else:
                    collector_label = "walk"
                
                with metrics_server(port=self.metrics_port):
                    # ⚡ FIX: Apply the label to the metric
                    with DUMP_DURATION.labels(collector=collector_label).time():
                        
                        # ⚡ REFACTOR: Step 1 - Build middleware
                        middlewares: List[ProcessorMiddleware] = []
                        if effective_scan_secrets:
                            middlewares.append(
                                SecretScanner(hide_secrets=effective_hide_secrets)
                            )
                        
                        # ⚡ REFACTOR: Step 2 - Process files
                        processor = FileProcessor(
                            temp_dir.name,
                            middlewares=middlewares, # Pass middleware list
                        )
                        processed_files = await processor.dump_concurrent(
                            files_list, self.progress, self.max_workers
                        )
                        
                        # Step 3 - Format output
                        if self.format == "json":
                            writer = JsonWriter(outfile)
                            await writer.write(processed_files, gmeta, VERSION)
                        else:
                            writer = MarkdownWriter(
                                outfile, 
                                self.no_toc, 
                                self.tree_toc,
                            )
                            await writer.write(processed_files, gmeta, VERSION)

                # Step 4 - Compress
                if self.compress:
                    gz_outfile = outfile.with_suffix(f".{file_ext}.gz")
                    await anyio.to_thread.run_sync(self._compress_file_sync, outfile, gz_outfile)
                    
                    await anyio.Path(outfile).unlink()
                    outfile = gz_outfile
                    logger.info("Output compressed", path=str(outfile))

                # Step 5 - Checksum
                checksum_writer = ChecksumWriter()
                checksum = await checksum_writer.write(outfile)
                if not self.quiet:
                    styled_print(f"[blue]{checksum}[/blue]")

                # Step 6 - Archive
                if self.archive or self.archive_all:
                    manager = ArchiveManager(
                        root=self.root,
                        timestamp=timestamp,
                        keep_latest=self.archive_keep_latest,
                        keep_last=self.archive_keep_last,
                        clean_root=self.archive_clean_root,
                        search=self.archive_search,
                        include_current=self.archive_include_current,
                        no_remove=self.archive_no_remove,
                        dry_run=self.dry_run,
                        yes=self.yes,
                        verbose=self.verbose,
                        md_pattern=cfg.dump_pattern,
                        archive_all=self.archive_all,
                        archive_format=self.archive_format, 
                    )
                    archive_results = await manager.run(current_outfile=outfile)
                    if archive_results:
                        groups = ', '.join(k for k, v in archive_results.items() if v)
                        if not self.quiet:
                            styled_print(f"[green]Archived groups: {groups}[/green]")
                        logger.info("Archiving complete", groups=groups)
                    else:
                        msg = "ℹ️ No prior dumps found for archiving."
                        if not self.quiet:
                            styled_print(f"[yellow]{msg}[/yellow]")
                        logger.info(msg)

                # Final metrics
                success_count = sum(1 for f in processed_files if not f.error)
                logger.info(
                    "Dump summary",
                    success=success_count,
                    errors=len(processed_files) - success_count,
                    output=str(outfile),
                )
            finally:
                await anyio.to_thread.run_sync(temp_dir.cleanup)

        except Exit as e:
            # Re-raise to be handled by the caller
            raise
```

---

