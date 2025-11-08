#!/usr/bin/env python3
"""
Task file merging operations and conflict resolution.
"""

import os
import json
import shutil
import tempfile
from typing import List, Dict, Any, Optional, Tuple, Set, Iterator
from pathlib import Path
from datetime import datetime
from collections import defaultdict

from .models import Task
from .storage import TaskStorage
from .config import Config


class MergeConflict:
    """Represents a task ID conflict during merge."""

    def __init__(self, task_id: str, source_task: Dict[str, Any],
                 target_task: Dict[str, Any], source_path: str, target_path: str):
        self.task_id = task_id
        self.source_task = source_task
        self.target_task = target_task
        self.source_path = source_path
        self.target_path = target_path

    def get_newer_task(self) -> Tuple[Dict[str, Any], str]:
        """Return the task with newer last_modified date."""
        source_modified = self.source_task.get('last_modified', '')
        target_modified = self.target_task.get('last_modified', '')

        if source_modified > target_modified:
            return self.source_task, 'source'
        else:
            return self.target_task, 'target'

    def __str__(self) -> str:
        return f"Conflict for task {self.task_id}: {self.source_path} vs {self.target_path}"


class TaskMerger:
    """Handles merging of multiple task files with conflict resolution."""

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize merger.

        Args:
            config: Configuration object
        """
        self.config = config or Config()

    def find_juno_task_directories(self, root_path: str) -> List[str]:
        """
        Find all .juno_task directories under root_path.

        Args:
            root_path: Root directory to search

        Returns:
            List of .juno_task directory paths
        """
        juno_task_dirs = []

        for root, dirs, files in os.walk(root_path):
            if '.juno_task' in dirs:
                juno_task_path = os.path.join(root, '.juno_task')
                # Check if it has a tasks subdirectory
                tasks_path = os.path.join(juno_task_path, 'tasks')
                if os.path.exists(tasks_path):
                    juno_task_dirs.append(juno_task_path)

        return sorted(juno_task_dirs)

    def collect_tasks_from_sources(self, source_paths: List[str]) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, str]]:
        """
        Collect all tasks from source paths.

        Args:
            source_paths: List of .juno_task directory paths

        Returns:
            Tuple of (tasks_dict, task_sources_dict) where:
            - tasks_dict: {task_id: task_data}
            - task_sources_dict: {task_id: source_path}
        """
        all_tasks = {}
        task_sources = {}

        for source_path in source_paths:
            tasks_dir = os.path.join(source_path, 'tasks')
            if not os.path.exists(tasks_dir):
                continue

            # Create temporary config for this source
            # We need to create a config with modified storage path
            source_config_dict = self.config.to_dict().copy()
            source_config_dict['storage']['base_path'] = tasks_dir

            # Create temporary config from modified dict
            temp_config = Config(auto_create=False)
            temp_config.config = source_config_dict

            # Create storage instance for this source
            storage = TaskStorage(temp_config)

            # Read all tasks from this source
            for task_dict in storage.read_all_tasks():
                task_id = task_dict.get('id')
                if not task_id:
                    continue

                if task_id in all_tasks:
                    # We have a duplicate - we'll handle this in conflict resolution
                    pass

                all_tasks[task_id] = task_dict
                task_sources[task_id] = source_path

        return all_tasks, task_sources

    def detect_conflicts(self, source_paths: List[str], target_path: str) -> List[MergeConflict]:
        """
        Detect ID conflicts between source paths and target.

        Args:
            source_paths: List of source .juno_task directories
            target_path: Target .juno_task directory

        Returns:
            List of merge conflicts
        """
        conflicts = []

        # Get existing tasks in target
        target_tasks_dir = os.path.join(target_path, 'tasks')
        if os.path.exists(target_tasks_dir):
            # Create temporary config for target
            target_config_dict = self.config.to_dict().copy()
            target_config_dict['storage']['base_path'] = target_tasks_dir

            target_config = Config(auto_create=False)
            target_config.config = target_config_dict
            target_storage = TaskStorage(target_config)

            target_tasks = {task['id']: task for task in target_storage.read_all_tasks() if 'id' in task}
        else:
            target_tasks = {}

        # Check for conflicts with each source
        for source_path in source_paths:
            source_tasks_dir = os.path.join(source_path, 'tasks')
            if not os.path.exists(source_tasks_dir):
                continue

            # Create temporary config for this source
            source_config_dict = self.config.to_dict().copy()
            source_config_dict['storage']['base_path'] = source_tasks_dir

            source_config = Config(auto_create=False)
            source_config.config = source_config_dict
            source_storage = TaskStorage(source_config)

            for source_task in source_storage.read_all_tasks():
                task_id = source_task.get('id')
                if not task_id:
                    continue

                if task_id in target_tasks:
                    conflict = MergeConflict(
                        task_id=task_id,
                        source_task=source_task,
                        target_task=target_tasks[task_id],
                        source_path=source_path,
                        target_path=target_path
                    )
                    conflicts.append(conflict)

        return conflicts

    def resolve_conflicts_keep_newer(self, conflicts: List[MergeConflict]) -> Dict[str, Dict[str, Any]]:
        """
        Resolve conflicts by keeping the task with newer last_modified.

        Args:
            conflicts: List of conflicts to resolve

        Returns:
            Dict of resolved tasks {task_id: task_data}
        """
        resolved = {}

        for conflict in conflicts:
            newer_task, source = conflict.get_newer_task()
            resolved[conflict.task_id] = newer_task

        return resolved

    def resolve_conflicts_keep_both(self, conflicts: List[MergeConflict]) -> Dict[str, Dict[str, Any]]:
        """
        Resolve conflicts by keeping both tasks (rename source task IDs).

        Args:
            conflicts: List of conflicts to resolve

        Returns:
            Dict of all tasks with renamed IDs {task_id: task_data}
        """
        resolved = {}

        for conflict in conflicts:
            # Keep target task as-is
            resolved[conflict.task_id] = conflict.target_task

            # Create new ID for source task
            new_id = self._generate_new_id(conflict.task_id, resolved.keys())
            source_task_copy = conflict.source_task.copy()
            source_task_copy['id'] = new_id
            source_task_copy['last_modified'] = datetime.now().isoformat()

            resolved[new_id] = source_task_copy

        return resolved

    def _generate_new_id(self, original_id: str, existing_ids: Set[str]) -> str:
        """
        Generate a new unique ID based on original ID.

        Args:
            original_id: Original task ID
            existing_ids: Set of existing IDs to avoid

        Returns:
            New unique ID
        """
        # Try appending _1, _2, etc.
        counter = 1
        while True:
            new_id = f"{original_id}_{counter}"
            if new_id not in existing_ids:
                return new_id
            counter += 1

            # Safety limit
            if counter > 1000:
                # Fallback to generating completely new ID
                return Task.generate_id()

    def merge_files(self, source_paths: List[str], target_path: str,
                   strategy: str = 'keep-newer', dry_run: bool = False) -> Dict[str, Any]:
        """
        Merge task files from multiple sources into target.

        Args:
            source_paths: List of source .juno_task directory paths
            target_path: Target .juno_task directory path
            strategy: Conflict resolution strategy ('keep-newer', 'keep-both', 'interactive')
            dry_run: If True, don't actually modify files

        Returns:
            Merge result summary
        """
        # Ensure target directory structure exists
        target_tasks_dir = os.path.join(target_path, 'tasks')
        if not dry_run:
            os.makedirs(target_tasks_dir, exist_ok=True)

        # Detect conflicts
        conflicts = self.detect_conflicts(source_paths, target_path)

        # Collect all tasks
        all_source_tasks, task_sources = self.collect_tasks_from_sources(source_paths)

        # Get existing target tasks
        if os.path.exists(target_tasks_dir):
            # Create temporary config for target
            target_config_dict = self.config.to_dict().copy()
            target_config_dict['storage']['base_path'] = target_tasks_dir

            target_config = Config(auto_create=False)
            target_config.config = target_config_dict
            target_storage = TaskStorage(target_config)
            target_tasks = {task['id']: task for task in target_storage.read_all_tasks() if 'id' in task}
        else:
            target_tasks = {}

        # Resolve conflicts based on strategy
        if strategy == 'keep-newer':
            resolved_conflicts = self.resolve_conflicts_keep_newer(conflicts)
        elif strategy == 'keep-both':
            resolved_conflicts = self.resolve_conflicts_keep_both(conflicts)
        else:
            raise ValueError(f"Unsupported strategy: {strategy}")

        # Build final task set
        final_tasks = target_tasks.copy()

        # Add resolved conflict tasks
        final_tasks.update(resolved_conflicts)

        # Add non-conflicting source tasks
        conflict_ids = {c.task_id for c in conflicts}
        for task_id, task_data in all_source_tasks.items():
            if task_id not in conflict_ids and task_id not in target_tasks:
                final_tasks[task_id] = task_data

        # Count statistics
        stats = {
            'total_sources': len(source_paths),
            'conflicts_found': len(conflicts),
            'conflicts_resolved': len(resolved_conflicts),
            'tasks_added': len(all_source_tasks) - len(conflicts),
            'tasks_kept': len(target_tasks),
            'final_task_count': len(final_tasks),
            'strategy_used': strategy,
            'dry_run': dry_run
        }

        if not dry_run:
            # Write merged tasks to target
            self._write_merged_tasks(target_tasks_dir, final_tasks)

            # Create backup of source directories (optional)
            if getattr(self.config.config, 'storage', {}).get('backup_enabled', False):
                self._backup_sources(source_paths)

        return {
            'success': True,
            'conflicts': [str(c) for c in conflicts],
            'statistics': stats,
            'final_tasks': list(final_tasks.keys()) if dry_run else None
        }

    def _write_merged_tasks(self, target_tasks_dir: str, tasks: Dict[str, Dict[str, Any]]):
        """
        Write merged tasks to target directory.

        Args:
            target_tasks_dir: Target tasks directory
            tasks: Tasks to write {task_id: task_data}
        """
        target_file = os.path.join(target_tasks_dir, 'backlog.ndjson')

        # Create backup if file exists
        if os.path.exists(target_file):
            backup_file = f"{target_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(target_file, backup_file)

        # Write all tasks to NDJSON file
        with open(target_file, 'w', encoding='utf-8') as f:
            for task_data in tasks.values():
                json_line = json.dumps(task_data, ensure_ascii=False)
                f.write(json_line + '\n')

    def _backup_sources(self, source_paths: List[str]):
        """
        Create backups of source directories before merge.

        Args:
            source_paths: Source paths to backup
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        for source_path in source_paths:
            backup_path = f"{source_path}.backup.{timestamp}"
            if not os.path.exists(backup_path):
                shutil.copytree(source_path, backup_path)