#!/usr/bin/env python3
"""
NDJSON file storage operations.
"""

import os
import json
import fcntl
import glob
import tempfile
from typing import List, Iterator, Optional, Dict, Any
from pathlib import Path
from datetime import datetime

from .models import Task
from .config import Config


class TaskStorage:
    """Manages task storage in NDJSON files."""

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize storage.

        Args:
            config: Configuration object (will create default if None)
        """
        self.config = config or Config()
        self.base_path = self.config.storage_base_path
        self.file_pattern = self.config.storage_file_pattern
        self.default_file = self.config.default_file

        # Ensure base directory exists
        os.makedirs(self.base_path, exist_ok=True)

    def get_files(self, pattern: Optional[str] = None) -> List[str]:
        """
        Get all task files matching pattern.

        Args:
            pattern: Glob pattern for files (default: from config)

        Returns:
            List of file paths
        """
        if pattern is None:
            pattern = self.file_pattern

        search_pattern = os.path.join(self.base_path, pattern)
        return sorted(glob.glob(search_pattern, recursive=True))

    def get_default_filepath(self) -> str:
        """Get full path to default task file."""
        return os.path.join(self.base_path, self.default_file)

    def read_tasks(self, filepath: str, skip_errors: bool = True) -> Iterator[Dict[str, Any]]:
        """
        Read tasks from NDJSON file.

        Args:
            filepath: Path to NDJSON file
            skip_errors: Continue on parse errors

        Yields:
            Task dictionaries
        """
        if not os.path.exists(filepath):
            return

        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    task = json.loads(line)
                    yield task
                except json.JSONDecodeError as e:
                    if skip_errors:
                        print(f"Warning: Parse error at {filepath}:{line_num}: {e}")
                        continue
                    else:
                        raise ValueError(f"Parse error at {filepath}:{line_num}: {e}")

    def read_all_tasks(self, file_pattern: Optional[str] = None) -> Iterator[Dict[str, Any]]:
        """
        Read all tasks from all matching files.

        Args:
            file_pattern: Glob pattern for files (default: from config)

        Yields:
            Task dictionaries
        """
        for filepath in self.get_files(file_pattern):
            yield from self.read_tasks(filepath)

    def find_task(self, task_id: str, file_pattern: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Find a specific task by ID.

        Args:
            task_id: Task ID to find
            file_pattern: Files to search (default: from config)

        Returns:
            Task dictionary or None if not found
        """
        for task in self.read_all_tasks(file_pattern):
            if task.get('id') == task_id:
                return task
        return None

    def find_task_file(self, task_id: str, file_pattern: Optional[str] = None) -> Optional[str]:
        """
        Find which file contains a specific task.

        Args:
            task_id: Task ID to find
            file_pattern: Files to search (default: from config)

        Returns:
            File path containing the task or None if not found
        """
        for filepath in self.get_files(file_pattern):
            for task in self.read_tasks(filepath):
                if task.get('id') == task_id:
                    return filepath
        return None

    def write_task(self, task: Task, filepath: Optional[str] = None):
        """
        Append task to NDJSON file (atomic operation).

        Args:
            task: Task object
            filepath: Target file (default: default task file)
        """
        if filepath is None:
            filepath = self.get_default_filepath()

        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath) or self.base_path, exist_ok=True)

        # Atomic write with file lock
        with open(filepath, 'a', encoding='utf-8') as f:
            # Acquire exclusive lock
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                ndjson_line = task.to_ndjson()
                f.write(ndjson_line + '\n')
                f.flush()
                os.fsync(f.fileno())
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def create_task(self, **kwargs) -> Task:
        """
        Create and store a new task.

        Args:
            **kwargs: Task creation arguments

        Returns:
            Created task object
        """
        # Add config for validation
        task = Task(config=self.config.to_dict(), **kwargs)
        self.write_task(task)
        return task

    def update_task(self, task_id: str, updates: Dict[str, Any], file_pattern: Optional[str] = None) -> bool:
        """
        Update task in NDJSON files.

        Strategy: Read all tasks, update matching task, rewrite file.

        Args:
            task_id: Task ID to update
            updates: Fields to update
            file_pattern: Files to search (default: from config)

        Returns:
            True if task was updated, False if not found
        """
        for filepath in self.get_files(file_pattern):
            tasks = list(self.read_tasks(filepath))
            updated = False

            for i, task_dict in enumerate(tasks):
                if task_dict['id'] == task_id:
                    # Create Task object for validation
                    task = Task.from_dict(task_dict, validate=False, config=self.config.to_dict())

                    # Update task using Task.update() method for validation
                    task.update(config=self.config.to_dict(), **updates)

                    # Convert back to dict
                    tasks[i] = task.to_dict()
                    updated = True
                    break

            if updated:
                # Rewrite file
                self._rewrite_file(filepath, tasks)
                return True

        return False

    def _rewrite_file(self, filepath: str, tasks: List[Dict[str, Any]]):
        """
        Rewrite NDJSON file with updated tasks (atomic operation).

        Args:
            filepath: File to rewrite
            tasks: List of task dictionaries
        """
        # Create temp file in same directory for atomic rename
        temp_fd, temp_file = tempfile.mkstemp(
            suffix='.tmp',
            prefix='.task_',
            dir=os.path.dirname(filepath) or self.base_path
        )

        try:
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                # Acquire exclusive lock
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    for task in tasks:
                        ndjson_line = json.dumps(task, ensure_ascii=False)
                        f.write(ndjson_line + '\n')
                    f.flush()
                    os.fsync(f.fileno())
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)

            # Atomic rename
            os.replace(temp_file, filepath)

        except Exception:
            # Clean up temp file on error
            try:
                os.unlink(temp_file)
            except OSError:
                pass
            raise

    def delete_task(self, task_id: str, file_pattern: Optional[str] = None) -> bool:
        """
        Delete task from NDJSON files.

        Args:
            task_id: Task ID to delete
            file_pattern: Files to search (default: from config)

        Returns:
            True if task was deleted, False if not found
        """
        for filepath in self.get_files(file_pattern):
            tasks = list(self.read_tasks(filepath))
            original_count = len(tasks)

            # Filter out task
            tasks = [t for t in tasks if t['id'] != task_id]

            if len(tasks) < original_count:
                # Task was found and removed
                self._rewrite_file(filepath, tasks)
                return True

        return False

    def count_tasks(self, file_pattern: Optional[str] = None) -> int:
        """
        Count total number of tasks.

        Args:
            file_pattern: Files to search (default: from config)

        Returns:
            Total task count
        """
        count = 0
        for _ in self.read_all_tasks(file_pattern):
            count += 1
        return count

    def get_tasks_by_status(self, status: str, file_pattern: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all tasks with specific status.

        Args:
            status: Status to filter by
            file_pattern: Files to search (default: from config)

        Returns:
            List of task dictionaries
        """
        return [task for task in self.read_all_tasks(file_pattern) if task.get('status') == status]

    def get_open_tasks(self, file_pattern: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all open tasks (no agent_response).

        Args:
            file_pattern: Files to search (default: from config)

        Returns:
            List of task dictionaries
        """
        return [
            task for task in self.read_all_tasks(file_pattern)
            if not task.get('agent_response') or task.get('agent_response', '').strip() == ''
        ]

    def get_recent_tasks(self, limit: int = 5, file_pattern: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get most recently modified tasks.

        Args:
            limit: Maximum number of tasks to return
            file_pattern: Files to search (default: from config)

        Returns:
            List of task dictionaries sorted by last_modified (newest first)
        """
        tasks = list(self.read_all_tasks(file_pattern))

        # Sort by last_modified timestamp (newest first)
        tasks.sort(key=lambda t: t.get('last_modified', ''), reverse=True)

        return tasks[:limit]

    def get_tasks_with_tag(self, tag: str, file_pattern: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all tasks with specific tag.

        Args:
            tag: Tag to filter by
            file_pattern: Files to search (default: from config)

        Returns:
            List of task dictionaries
        """
        return [
            task for task in self.read_all_tasks(file_pattern)
            if task.get('feature_tags') and tag in task.get('feature_tags', [])
        ]

    def get_tasks_with_commit(self, commit_hash: str, file_pattern: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all tasks with specific commit hash.

        Args:
            commit_hash: Commit hash to filter by
            file_pattern: Files to search (default: from config)

        Returns:
            List of task dictionaries
        """
        return [
            task for task in self.read_all_tasks(file_pattern)
            if task.get('commit_hash') == commit_hash
        ]

    def get_file_info(self) -> List[Dict[str, Any]]:
        """
        Get information about all task files.

        Returns:
            List of file info dictionaries
        """
        files_info = []
        for filepath in self.get_files():
            if os.path.exists(filepath):
                stat = os.stat(filepath)
                task_count = sum(1 for _ in self.read_tasks(filepath))

                files_info.append({
                    'path': filepath,
                    'size_bytes': stat.st_size,
                    'size_mb': round(stat.st_size / (1024 * 1024), 2),
                    'task_count': task_count,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })

        return files_info

    def __repr__(self) -> str:
        """String representation."""
        return f"TaskStorage(base_path='{self.base_path}', pattern='{self.file_pattern}')"