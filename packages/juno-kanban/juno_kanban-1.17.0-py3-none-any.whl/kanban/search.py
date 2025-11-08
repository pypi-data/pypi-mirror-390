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
import sys
from typing import List, Dict, Optional, Any, Iterator, Union
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
    status: Optional[Union[str, List[str]]] = None  # Support both single value and list
    tag: Optional[Union[str, List[str]]] = None     # Support both single value and list
    exclude_tags: Optional[Union[str, List[str]]] = None  # Support both single value and list for exclusion
    commit_hash: Optional[str] = None
    body_text: Optional[str] = None
    response_text: Optional[str] = None  # Search in agent_response field
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

    def _run_ripgrep(self, pattern: str, limit: int = None, fixed_strings: bool = True) -> List[str]:
        """
        Run ripgrep with common options.

        Args:
            pattern: Search pattern
            limit: Max results (None for no limit - Issue 28: needed for proper sorting)
            fixed_strings: Use literal string matching

        Returns:
            List of matching lines
        """
        if not self.rg_available:
            return []

        files = self._get_files()
        if not files:
            return []

        args = [
            'rg',
            '--no-heading',
            '--no-line-number',
        ]

        # Only add --max-count if limit is specified (Issue 28: avoid pre-sorting limits)
        if limit is not None:
            args.extend(['--max-count', str(limit)])

        if fixed_strings:
            args.append('--fixed-strings')

        args.extend([pattern] + files)

        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0 and result.stdout:
                return [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]

            return []

        except subprocess.CalledProcessError:
            return []

    def search_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Search for task by exact ID using ripgrep.

        Args:
            task_id: Task ID to find

        Returns:
            Task dict or None
        """
        # Pattern: "id": "a1b2c3" (with space after colon)
        pattern = f'"id": "{task_id}"'
        lines = self._run_ripgrep(pattern, limit=1)

        if lines:
            try:
                return json.loads(lines[0])
            except json.JSONDecodeError:
                pass
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
        # Pattern: "status": "in_progress" (with space after colon)
        pattern = f'"status": "{status}"'
        # Issue 28: Get all results first, then sort and limit
        lines = self._run_ripgrep(pattern, limit=None)

        tasks = []
        for line in lines:
            try:
                task = json.loads(line)
                tasks.append(task)
            except json.JSONDecodeError:
                continue

        # Sort by last_modified DESC for consistent ordering (Issue 28)
        tasks.sort(key=lambda t: t.get('last_modified', ''), reverse=True)
        return tasks[:limit]

    def search_by_tag(self, tag: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for tasks by tag using ripgrep.

        Args:
            tag: Tag to filter
            limit: Max results

        Returns:
            List of task dicts
        """
        # Pattern: search for tag in feature_tags field (with space after colon)
        pattern = f'"feature_tags": \\[.*"{tag}".*\\]'
        # Issue 28: Get all results first, then sort and limit
        lines = self._run_ripgrep(pattern, limit=None, fixed_strings=False)

        tasks = []
        for line in lines:
            try:
                task = json.loads(line)
                # Verify tag is actually in the list (regex can be imprecise)
                if task.get('feature_tags') and tag in task['feature_tags']:
                    tasks.append(task)
            except json.JSONDecodeError:
                continue

        # Sort by last_modified DESC for consistent ordering (Issue 28)
        tasks.sort(key=lambda t: t.get('last_modified', ''), reverse=True)
        return tasks[:limit]

    def search_by_commit(self, commit_hash: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for tasks by commit hash using ripgrep.

        Args:
            commit_hash: Commit hash to filter
            limit: Max results

        Returns:
            List of task dicts
        """
        # Pattern: "commit_hash": "abc123" (with space after colon)
        pattern = f'"commit_hash": "{commit_hash}"'
        # Issue 28: Get all results first, then sort and limit
        lines = self._run_ripgrep(pattern, limit=None)

        tasks = []
        for line in lines:
            try:
                task = json.loads(line)
                tasks.append(task)
            except json.JSONDecodeError:
                continue

        # Sort by last_modified DESC for consistent ordering (Issue 28)
        tasks.sort(key=lambda t: t.get('last_modified', ''), reverse=True)
        return tasks[:limit]

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
        # Search for text in the body field (with space after colon)
        pattern = f'"body": "[^"]*{re.escape(text)}[^"]*"'

        if not self.rg_available:
            return []

        files = self._get_files()
        if not files:
            return []

        args = [
            'rg',
            '--no-heading',
            '--no-line-number',
        ]

        # Issue 28: Don't use --max-count to allow proper sorting

        if not case_sensitive:
            args.append('--ignore-case')

        args.extend([pattern] + files)

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

                # Sort by last_modified DESC for consistent ordering (Issue 28)
                tasks.sort(key=lambda t: t.get('last_modified', ''), reverse=True)
                return tasks[:limit]

            return []

        except subprocess.CalledProcessError:
            return []

    def search_in_response(self, text: str, limit: int = 5, case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """
        Search for text in agent_response field using ripgrep.

        Args:
            text: Text to search for
            limit: Max results
            case_sensitive: Case sensitive search

        Returns:
            List of task dicts
        """
        # Search for text in the agent_response field (with space after colon)
        pattern = f'"agent_response": "[^"]*{re.escape(text)}[^"]*"'

        if not self.rg_available:
            return []

        files = self._get_files()
        if not files:
            return []

        args = [
            'rg',
            '--no-heading',
            '--no-line-number',
        ]

        # Issue 28: Don't use --max-count to allow proper sorting

        if not case_sensitive:
            args.append('--ignore-case')

        args.extend([pattern] + files)

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

                # Sort by last_modified DESC for consistent ordering (Issue 28)
                tasks.sort(key=lambda t: t.get('last_modified', ''), reverse=True)
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
        # Always sort by last_modified DESC for consistent ordering (Issue 28)
        tasks.sort(key=lambda t: t.get('last_modified', ''), reverse=True)

        return tasks[:filters.limit]

    def search_all_prioritized(self, filters: SearchFilters) -> List[Dict[str, Any]]:
        """
        Search using Python with prioritized sorting for list command.

        Shows open issues (backlog, todo, in_progress) first sorted by last_modified DESC,
        then closed issues (done, archive) sorted by last_modified DESC.

        Args:
            filters: Search criteria

        Returns:
            List of task dicts with prioritized sorting
        """
        tasks = []

        # Get all tasks that match filters
        for task in self.storage.read_all_tasks():
            if self._matches_filters(task, filters):
                tasks.append(task)

        # Apply prioritized sorting
        def get_sort_key(task):
            status = task.get('status', 'unknown')
            last_modified = task.get('last_modified', '')

            # Define priority groups
            open_statuses = ['backlog', 'todo', 'in_progress']
            closed_statuses = ['done', 'archive']

            if status in open_statuses:
                # Open issues get priority 0, sorted by last_modified DESC
                return (0, -hash(last_modified) if last_modified else 0)
            elif status in closed_statuses:
                # Closed issues get priority 1, sorted by last_modified DESC
                return (1, -hash(last_modified) if last_modified else 0)
            else:
                # Unknown statuses get priority 2
                return (2, -hash(last_modified) if last_modified else 0)

        # Sort by priority group first, then by last_modified DESC within each group
        tasks.sort(key=lambda t: (
            0 if t.get('status') in ['backlog', 'todo', 'in_progress'] else 1,
            t.get('last_modified', ''),
        ), reverse=False)  # Priority ascending, but we'll reverse last_modified separately

        # Now sort within each group by last_modified DESC
        open_tasks = [t for t in tasks if t.get('status') in ['backlog', 'todo', 'in_progress']]
        closed_tasks = [t for t in tasks if t.get('status') in ['done', 'archive']]
        other_tasks = [t for t in tasks if t.get('status') not in ['backlog', 'todo', 'in_progress', 'done', 'archive']]

        # Sort each group by last_modified DESC
        open_tasks.sort(key=lambda t: t.get('last_modified', ''), reverse=True)
        closed_tasks.sort(key=lambda t: t.get('last_modified', ''), reverse=True)
        other_tasks.sort(key=lambda t: t.get('last_modified', ''), reverse=True)

        # Combine in priority order
        prioritized_tasks = open_tasks + closed_tasks + other_tasks

        return prioritized_tasks[:filters.limit]

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

        # Status filter (supports single value or list for OR logic)
        if filters.status:
            task_status = task.get('status')
            if isinstance(filters.status, list):
                if task_status not in filters.status:
                    return False
            else:
                if task_status != filters.status:
                    return False

        # Tag filter (supports single value or list for OR logic)
        if filters.tag:
            task_tags = task.get('feature_tags', [])
            if not task_tags:
                return False

            if isinstance(filters.tag, list):
                # Check if any of the filter tags match any of the task tags
                if not any(filter_tag in task_tags for filter_tag in filters.tag):
                    return False
            else:
                # Single tag filter
                if filters.tag not in task_tags:
                    return False

        # Tag exclusion filter (supports single value or list for OR logic)
        if filters.exclude_tags:
            task_tags = task.get('feature_tags', [])
            if task_tags:  # Only check if task has tags
                if isinstance(filters.exclude_tags, list):
                    # Exclude if any of the exclude tags match any of the task tags
                    if any(exclude_tag in task_tags for exclude_tag in filters.exclude_tags):
                        return False
                else:
                    # Single exclude tag
                    if filters.exclude_tags in task_tags:
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

        # Response text filter
        if filters.response_text:
            response = task.get('agent_response', '')
            if filters.case_sensitive:
                if filters.response_text not in response:
                    return False
            else:
                if filters.response_text.lower() not in response.lower():
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
        if filters.id and not any([filters.status, filters.tag, filters.exclude_tags, filters.commit_hash,
                                   filters.body_text, filters.response_text, filters.open_only, filters.recent]):
            if self.ripgrep_available:
                result = self.ripgrep.search_by_id(filters.id)
                return [result] if result else []

        # For simple single-field searches, try ripgrep (only for string values, not lists)
        # NOTE: Exclude optimizations if exclude_tags is present - need Python filtering
        if self.ripgrep_available and not filters.open_only and not filters.recent and not filters.exclude_tags:
            if filters.status and isinstance(filters.status, str) and not any([filters.id, filters.tag, filters.commit_hash, filters.body_text, filters.response_text]):
                return self.ripgrep.search_by_status(filters.status, filters.limit)

            if filters.tag and isinstance(filters.tag, str) and not any([filters.id, filters.status, filters.commit_hash, filters.body_text, filters.response_text]):
                return self.ripgrep.search_by_tag(filters.tag, filters.limit)

            if filters.commit_hash and not any([filters.id, filters.status, filters.tag, filters.body_text, filters.response_text]):
                return self.ripgrep.search_by_commit(filters.commit_hash, filters.limit)

            if filters.body_text and not any([filters.id, filters.status, filters.tag, filters.commit_hash, filters.response_text]):
                return self.ripgrep.search_in_body(filters.body_text, filters.limit, filters.case_sensitive)

            if filters.response_text and not any([filters.id, filters.status, filters.tag, filters.commit_hash, filters.body_text]):
                return self.ripgrep.search_in_response(filters.response_text, filters.limit, filters.case_sensitive)

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

    def search_prioritized_list(self, limit: int = 5, filters: Optional[SearchFilters] = None) -> List[Dict[str, Any]]:
        """
        Get tasks with prioritized sorting for list command.

        Shows open issues (backlog, todo, in_progress) first sorted by last_modified DESC,
        then closed issues (done, archive) sorted by last_modified DESC.

        Args:
            limit: Maximum number of tasks to return
            filters: Optional search filters to apply

        Returns:
            List of tasks with prioritized sorting
        """
        if filters is None:
            filters = SearchFilters(limit=limit)
        else:
            # Update the limit in the provided filters
            filters.limit = limit
        return self.python_search.search_all_prioritized(filters)

    def get_info(self) -> Dict[str, Any]:
        """Get search backend information."""
        return {
            'ripgrep_available': self.ripgrep_available,
            'ripgrep_version': get_ripgrep_version() if self.ripgrep_available else None,
            'backend': 'ripgrep + python' if self.ripgrep_available else 'python only',
            'base_path': self.config.storage_base_path,
            'file_pattern': self.config.storage_file_pattern
        }