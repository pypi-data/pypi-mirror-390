#!/usr/bin/env python3
"""
Task model and operations.
"""

import json
import random
import string
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from .validators import TaskValidator, ValidationError


class Task:
    """Represents a kanban task."""

    def __init__(self,
                 id: Optional[str] = None,
                 status: str = "backlog",
                 body: str = "",
                 commit_hash: Optional[str] = None,
                 agent_response: str = "",
                 created_date: Optional[str] = None,
                 last_modified: Optional[str] = None,
                 feature_tags: Optional[List[str]] = None,
                 validate: bool = True,
                 config: Optional[dict] = None):
        """
        Initialize a task.

        Args:
            id: Task ID (auto-generated if not provided)
            status: Task status
            body: Task description
            commit_hash: Git commit hash
            agent_response: AI agent response
            created_date: Creation timestamp (auto-generated if not provided)
            last_modified: Last modification timestamp (auto-generated if not provided)
            feature_tags: List of feature tags
            validate: Whether to validate task data
            config: Configuration for validation
        """
        self.id = id or self._generate_id()
        self.status = status
        self.body = body
        self.commit_hash = commit_hash
        self.agent_response = agent_response
        self.created_date = created_date or self._get_timestamp()
        self.last_modified = last_modified or self._get_timestamp()
        self.feature_tags = feature_tags

        # Validate task if requested
        if validate:
            self._validate(config)

    def _validate(self, config: Optional[dict] = None):
        """Validate task data."""
        is_valid, error = TaskValidator.validate_task(self.to_dict(), config)
        if not is_valid:
            raise ValidationError(error)

    @staticmethod
    def _generate_id() -> str:
        """
        Generate a unique 6-character alphanumeric task ID.
        Ensures mix of letters and numbers (not only numeric).

        Returns:
            6-character ID with mix of letters and numbers
        """
        chars = string.ascii_letters + string.digits
        letters = string.ascii_letters
        digits = string.digits

        # Ensure at least 1 letter and 1 number
        task_id = [
            random.choice(letters),
            random.choice(digits),
            random.choice(chars),
            random.choice(chars),
            random.choice(chars),
            random.choice(chars)
        ]

        # Shuffle to randomize positions
        random.shuffle(task_id)
        return ''.join(task_id)

    @staticmethod
    def _get_timestamp() -> str:
        """
        Get current timestamp without timezone and milliseconds.

        Returns:
            Timestamp in YYYY-MM-DD HH:MM:SS format
        """
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "id": self.id,
            "status": self.status,
            "body": self.body,
            "commit_hash": self.commit_hash,
            "agent_response": self.agent_response,
            "created_date": self.created_date,
            "last_modified": self.last_modified,
            "feature_tags": self.feature_tags
        }

    def to_ndjson(self) -> str:
        """
        Convert task to NDJSON format (single line JSON).
        Uses ensure_ascii=False to handle Unicode properly.

        Returns:
            NDJSON string
        """
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any], validate: bool = True, config: Optional[dict] = None) -> 'Task':
        """
        Create task from dictionary.

        Args:
            data: Task dictionary
            validate: Whether to validate task data
            config: Configuration for validation

        Returns:
            Task instance
        """
        return cls(
            id=data.get('id'),
            status=data.get('status', 'backlog'),
            body=data.get('body', ''),
            commit_hash=data.get('commit_hash'),
            agent_response=data.get('agent_response', ''),
            created_date=data.get('created_date'),
            last_modified=data.get('last_modified'),
            feature_tags=data.get('feature_tags'),
            validate=validate,
            config=config
        )

    @classmethod
    def from_ndjson(cls, line: str, validate: bool = True, config: Optional[dict] = None) -> 'Task':
        """
        Create task from NDJSON line.

        Args:
            line: NDJSON line
            validate: Whether to validate task data
            config: Configuration for validation

        Returns:
            Task instance

        Raises:
            json.JSONDecodeError: If line is not valid JSON
            ValidationError: If task data is invalid
        """
        data = json.loads(line.strip())
        return cls.from_dict(data, validate=validate, config=config)

    def update(self, config: Optional[dict] = None, **kwargs):
        """
        Update task fields.

        Args:
            config: Configuration for validation
            **kwargs: Fields to update (status, agent_response, commit_hash, feature_tags, body)

        Raises:
            ValidationError: If updated data is invalid
        """
        allowed_updates = ['status', 'agent_response', 'commit_hash', 'feature_tags', 'body']

        # Validate status transition if changing status
        if 'status' in kwargs and config:
            workflow = config.get('status_workflow', {})
            if workflow.get('enforce_transitions', False):
                transitions = workflow.get('transitions', {})
                is_valid, error = TaskValidator.validate_status_transition(
                    self.status, kwargs['status'], transitions, True
                )
                if not is_valid:
                    raise ValidationError(error)

        # Update fields
        for key, value in kwargs.items():
            if key in allowed_updates:
                setattr(self, key, value)

        # Update last_modified timestamp
        self.last_modified = self._get_timestamp()

        # Validate updated task
        self._validate(config)

    def is_open(self) -> bool:
        """
        Check if task is open (has no agent_response).

        Returns:
            True if task is open (no agent response)
        """
        return not self.agent_response or self.agent_response.strip() == ""

    def has_tag(self, tag: str) -> bool:
        """
        Check if task has a specific tag.

        Args:
            tag: Tag to check for

        Returns:
            True if task has the tag
        """
        return self.feature_tags is not None and tag in self.feature_tags

    def add_tag(self, tag: str, config: Optional[dict] = None):
        """
        Add a tag to the task.

        Args:
            tag: Tag to add
            config: Configuration for validation

        Raises:
            ValidationError: If tag is invalid
        """
        if self.feature_tags is None:
            self.feature_tags = []

        if tag not in self.feature_tags:
            self.feature_tags.append(tag)
            self.last_modified = self._get_timestamp()

            # Validate tags
            max_tags = 20
            allowed_tags = None
            pattern = None

            if config:
                tag_config = config.get('feature_tags', {})
                max_tags = tag_config.get('max_tags_per_task', 20)
                allowed_tags = tag_config.get('allowed_tags')
                pattern_str = tag_config.get('validation_pattern')
                if pattern_str:
                    import re
                    pattern = re.compile(pattern_str)

            is_valid, error = TaskValidator.validate_tags(
                self.feature_tags, max_tags, allowed_tags, pattern
            )
            if not is_valid:
                # Remove the tag we just added
                self.feature_tags.remove(tag)
                raise ValidationError(error)

    def remove_tag(self, tag: str):
        """
        Remove a tag from the task.

        Args:
            tag: Tag to remove
        """
        if self.feature_tags and tag in self.feature_tags:
            self.feature_tags.remove(tag)
            self.last_modified = self._get_timestamp()

    def age_days(self) -> int:
        """
        Get task age in days.

        Returns:
            Number of days since task creation
        """
        created = datetime.fromisoformat(self.created_date.replace('Z', '+00:00'))
        now = datetime.now().astimezone()
        return (now - created).days

    def __repr__(self) -> str:
        """String representation of task."""
        body_preview = self.body[:50] + "..." if len(self.body) > 50 else self.body
        return f"Task(id={self.id}, status={self.status}, body='{body_preview}')"

    def __str__(self) -> str:
        """Human-readable string representation."""
        tags_str = f", tags={self.feature_tags}" if self.feature_tags else ""
        return f"[{self.id}] {self.status}: {self.body[:100]}{tags_str}"

    def __eq__(self, other) -> bool:
        """Check equality based on task ID."""
        if not isinstance(other, Task):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on task ID."""
        return hash(self.id)