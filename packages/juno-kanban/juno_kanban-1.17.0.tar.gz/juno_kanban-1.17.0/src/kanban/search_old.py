#!/usr/bin/env python3
"""
Search implementation with ripgrep integration and Python fallback.
"""

import subprocess
import shutil
import json
import re
import glob
import os
from typing import List, Dict, Optional, Any, Iterator
from dataclasses import dataclass

from .config import Config
from .storage import TaskStorage


def check_ripgrep() -> bool:
    """
    Check if ripgrep is installed.

    Returns:
        True if ripgrep is available
    """
    return shutil.which('rg') is not None


def get_ripgrep_version() -> Optional[str]:
    """
    Get ripgrep version.

    Returns:
        Version string or None
    """
    try:
        result = subprocess.run(
            ['rg', '--version'],
            capture_output=True,
            text=True,
            check=True
        )
        # Output: ripgrep 13.0.0
        return result.stdout.split('\n')[0].split()[1]
    except (subprocess.CalledProcessError, FileNotFoundError, IndexError):
        return None


@dataclass
class SearchFilters:
    """Search filter criteria."""
    id: Optional[str] = None
    status: Optional[str] = None
    tag: Optional[str] = None
    commit_hash: Optional[str] = None
    body_text: Optional[str] = None
    open_only: bool = False
    recent: bool = False
    limit: int = 5
    case_sensitive: bool = False


class RipgrepSearch:
    """High-performance search using ripgrep."""

    def __init__(self, base_path: str, file_pattern: str = "*.ndjson"):
        """
        Initialize ripgrep search.

        Args:
            base_path: Base directory for task files
            file_pattern: File pattern to search
        """
        self.base_path = base_path
        self.file_pattern = file_pattern
        self.rg_available = check_ripgrep()

    def _get_files(self) -> List[str]:
        """Get list of files to search."""
        search_pattern = os.path.join(self.base_path, self.file_pattern)
        return sorted(glob.glob(search_pattern, recursive=True))

    def search_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Search for task by exact ID using ripgrep.

        Args:
            task_id: Task ID to find

        Returns:
            Task dict or None
        """
        if not self.rg_available:
            return None

        # Pattern: "id": "a1b2c3" (with space after colon)
        pattern = f'"id": "{task_id}"'

        files = self._get_files()
        if not files:
            return None

        try:
            result = subprocess.run(
                [
                    'rg',
                    '--no-heading',
                    '--no-line-number',
                    '--max-count', '1',  # Stop after first match
                    '--fixed-strings',  # Literal string match
                    pattern
                ] + files,
                capture_output=True,
                text=True,
                check=False  # Don't raise on non-zero exit (no match)
            )

            if result.returncode == 0 and result.stdout:
                line = result.stdout.strip()
                return json.loads(line)

            return None

        except (subprocess.CalledProcessError, json.JSONDecodeError):
            return None

    def search_by_status(self, status: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for tasks by status using ripgrep.

        Args:
            status: Status to filter
            limit: Max results

        Returns:
            List of task dicts
        """
        if not self.rg_available:
            return []

        # Pattern: "status": "in_progress" (with space after colon)
        pattern = f'"status": "{status}"'

        files = self._get_files()
        if not files:
            return []

        try:
            result = subprocess.run(
                [
                    'rg',
                    '--no-heading',
                    '--no-line-number',
                    '--max-count', str(limit),
                    '--fixed-strings',
                    pattern
                ] + files,
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0 and result.stdout:
                tasks = []
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        try:
                            task = json.loads(line)
                            tasks.append(task)
                        except json.JSONDecodeError:
                            continue
                return tasks[:limit]

            return []

        except subprocess.CalledProcessError:
            return []

    def search_by_tag(self, tag: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for tasks by tag using ripgrep.

        Args:
            tag: Tag to filter
            limit: Max results

        Returns:
            List of task dicts
        """
        if not self.rg_available:
            return []

        # Pattern: search for tag in feature_tags field (with space after colon)
        pattern = f'"feature_tags": \\[.*"{tag}".*\\]'

        try:
            result = subprocess.run(
                [
                    'rg',
                    '--no-heading',
                    '--no-line-number',
                    '--max-count', str(limit),
                    pattern,
                    f'{self.base_path}/{self.file_pattern}'
                ],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0 and result.stdout:
                tasks = []
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        try:
                            task = json.loads(line)
                            # Verify tag is actually in the list (regex can be imprecise)
                            if task.get('feature_tags') and tag in task['feature_tags']:
                                tasks.append(task)
                        except json.JSONDecodeError:
                            continue
                return tasks[:limit]

            return []

        except subprocess.CalledProcessError:
            return []

    def search_by_commit(self, commit_hash: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for tasks by commit hash using ripgrep.

        Args:
            commit_hash: Commit hash to filter
            limit: Max results

        Returns:
            List of task dicts
        """
        if not self.rg_available:
            return []

        # Pattern: "commit_hash": "abc123" (with space after colon)
        pattern = f'"commit_hash": "{commit_hash}"'

        try:
            result = subprocess.run(
                [
                    'rg',
                    '--no-heading',
                    '--no-line-number',
                    '--max-count', str(limit),
                    '--fixed-strings',
                    pattern,
                    f'{self.base_path}/{self.file_pattern}'
                ],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0 and result.stdout:
                tasks = []
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        try:
                            task = json.loads(line)
                            tasks.append(task)
                        except json.JSONDecodeError:
                            continue
                return tasks[:limit]

            return []

        except subprocess.CalledProcessError:
            return []

    def search_in_body(self, text: str, limit: int = 5, case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """
        Search for text in task body using ripgrep.

        Args:
            text: Text to search for
            limit: Max results
            case_sensitive: Case sensitive search

        Returns:
            List of task dicts
        """
        if not self.rg_available:
            return []

        args = [
            'rg',
            '--no-heading',
            '--no-line-number',
            '--max-count', str(limit),
        ]

        if not case_sensitive:
            args.append('--ignore-case')

        # Search for text in the body field (with space after colon)
        pattern = f'"body": "[^"]*{re.escape(text)}[^"]*"'
        args.extend([pattern, f'{self.base_path}/{self.file_pattern}'])

        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0 and result.stdout:
                tasks = []
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        try:
                            task = json.loads(line)
                            tasks.append(task)
                        except json.JSONDecodeError:
                            continue
                return tasks[:limit]

            return []

        except subprocess.CalledProcessError:
            return []


class PythonSearch:
    """Python-based search fallback."""

    def __init__(self, storage: TaskStorage):
        """
        Initialize Python search.

        Args:
            storage: TaskStorage instance
        """
        self.storage = storage

    def search_all(self, filters: SearchFilters) -> List[Dict[str, Any]]:
        """
        Search using Python with all filters.

        Args:
            filters: Search criteria

        Returns:
            List of task dicts
        """
        tasks = []

        # Get all tasks
        for task in self.storage.read_all_tasks():
            if self._matches_filters(task, filters):
                tasks.append(task)

            # Limit early to avoid processing too many
            if len(tasks) >= filters.limit * 2:  # Get more for sorting
                break

        # Apply sorting and final limit
        if filters.recent:
            tasks.sort(key=lambda t: t.get('last_modified', ''), reverse=True)

        return tasks[:filters.limit]

    def _matches_filters(self, task: Dict[str, Any], filters: SearchFilters) -> bool:
        """
        Check if task matches all filters.

        Args:
            task: Task dictionary
            filters: Search criteria

        Returns:
            True if task matches all filters
        """
        # ID filter
        if filters.id and task.get('id') != filters.id:
            return False

        # Status filter
        if filters.status and task.get('status') != filters.status:
            return False

        # Tag filter
        if filters.tag:
            tags = task.get('feature_tags', [])
            if not tags or filters.tag not in tags:
                return False

        # Commit hash filter
        if filters.commit_hash and task.get('commit_hash') != filters.commit_hash:
            return False

        # Body text filter
        if filters.body_text:
            body = task.get('body', '')
            if filters.case_sensitive:
                if filters.body_text not in body:
                    return False
            else:
                if filters.body_text.lower() not in body.lower():
                    return False

        # Open tasks filter
        if filters.open_only:
            agent_response = task.get('agent_response', '').strip()
            if agent_response:
                return False

        return True


class TaskSearch:
    """Main search interface with automatic backend selection."""

    def __init__(self, config: Optional[Config] = None, storage: Optional[TaskStorage] = None):
        """
        Initialize task search.

        Args:
            config: Configuration object
            storage: TaskStorage instance
        """
        self.config = config or Config()
        self.storage = storage or TaskStorage(self.config)

        # Initialize search backends
        self.ripgrep = RipgrepSearch(
            self.config.storage_base_path,
            self.config.storage_file_pattern
        )
        self.python_search = PythonSearch(self.storage)

        # Check ripgrep availability
        self.ripgrep_available = self.ripgrep.rg_available

    def search(self, filters: SearchFilters) -> List[Dict[str, Any]]:
        """
        Search tasks using optimal backend.

        Args:
            filters: Search criteria

        Returns:
            List of task dictionaries
        """
        # For single ID lookup, try ripgrep first
        if filters.id and not any([filters.status, filters.tag, filters.commit_hash,
                                   filters.body_text, filters.open_only, filters.recent]):
            if self.ripgrep_available:
                result = self.ripgrep.search_by_id(filters.id)
                return [result] if result else []

        # For simple single-field searches, try ripgrep
        if self.ripgrep_available and not filters.open_only and not filters.recent:
            if filters.status and not any([filters.id, filters.tag, filters.commit_hash, filters.body_text]):
                return self.ripgrep.search_by_status(filters.status, filters.limit)

            if filters.tag and not any([filters.id, filters.status, filters.commit_hash, filters.body_text]):
                return self.ripgrep.search_by_tag(filters.tag, filters.limit)

            if filters.commit_hash and not any([filters.id, filters.status, filters.tag, filters.body_text]):
                return self.ripgrep.search_by_commit(filters.commit_hash, filters.limit)

            if filters.body_text and not any([filters.id, filters.status, filters.tag, filters.commit_hash]):
                return self.ripgrep.search_in_body(filters.body_text, filters.limit, filters.case_sensitive)

        # Fall back to Python search for complex queries
        return self.python_search.search_all(filters)

    def search_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Quick ID lookup."""
        filters = SearchFilters(id=task_id, limit=1)
        results = self.search(filters)
        return results[0] if results else None

    def search_by_status(self, status: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Quick status search."""
        filters = SearchFilters(status=status, limit=limit)
        return self.search(filters)

    def search_by_tag(self, tag: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Quick tag search."""
        filters = SearchFilters(tag=tag, limit=limit)
        return self.search(filters)

    def search_open_tasks(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get open tasks (no agent response)."""
        filters = SearchFilters(open_only=True, limit=limit)
        return self.search(filters)

    def search_recent_tasks(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent tasks."""
        filters = SearchFilters(recent=True, limit=limit)
        return self.search(filters)

    def get_info(self) -> Dict[str, Any]:
        """Get search backend information."""
        return {
            'ripgrep_available': self.ripgrep_available,
            'ripgrep_version': get_ripgrep_version() if self.ripgrep_available else None,
            'backend': 'ripgrep + python' if self.ripgrep_available else 'python only',
            'base_path': self.config.storage_base_path,
            'file_pattern': self.config.storage_file_pattern
        }