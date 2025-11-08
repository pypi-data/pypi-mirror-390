#!/usr/bin/env python3
"""
Task Manager CLI - Complete Implementation
NDJSON-based Kanban task manager optimized for LLM usage.
"""

import sys
import os
import argparse
import json
from typing import List, Optional, Dict, Any
from pathlib import Path

from .config import Config, ConfigError
from .models import Task, ValidationError
from .storage import TaskStorage
from .search import TaskSearch, SearchFilters
from .validators import TaskValidator
from .merge import TaskMerger


# Exit codes
class ExitCode:
    """Standard exit codes."""
    SUCCESS = 0
    GENERAL_ERROR = 1
    INVALID_USAGE = 2
    CONFIG_ERROR = 3
    IO_ERROR = 4
    VALIDATION_ERROR = 5


class OutputFormatter:
    """Format output in different formats."""

    @staticmethod
    def format_tasks(tasks: List[Dict[str, Any]], output_format: str, pretty: bool = False) -> str:
        """
        Format task list for output.

        Args:
            tasks: List of task dictionaries
            output_format: Format type (ndjson, json, xml, table)
            pretty: Pretty print output

        Returns:
            Formatted string
        """
        if not tasks:
            return ""

        if output_format == 'ndjson':
            return '\n'.join(json.dumps(task, ensure_ascii=False) for task in tasks)

        elif output_format == 'json':
            indent = 2 if pretty else None
            return json.dumps(tasks, ensure_ascii=False, indent=indent)

        elif output_format == 'xml':
            lines = ['<?xml version="1.0" encoding="UTF-8"?>']
            lines.append('<tasks>')
            for task in tasks:
                lines.append('  <task>')
                for key, value in task.items():
                    if value is None:
                        lines.append(f'    <{key} />')
                    elif isinstance(value, list):
                        lines.append(f'    <{key}>')
                        for item in value:
                            lines.append(f'      <item>{OutputFormatter._escape_xml(str(item))}</item>')
                        lines.append(f'    </{key}>')
                    else:
                        lines.append(f'    <{key}>{OutputFormatter._escape_xml(str(value))}</{key}>')
                lines.append('  </task>')
            lines.append('</tasks>')
            return '\n'.join(lines)

        elif output_format == 'table':
            if not tasks:
                return ""

            # Simple table format
            lines = []
            lines.append(f"{'ID':<8} {'Status':<12} {'Body':<50} {'Tags':<20}")
            lines.append("-" * 90)

            for task in tasks:
                task_id = task.get('id', '')[:8]
                status = task.get('status', '')[:12]
                body = task.get('body', '')[:47] + ("..." if len(task.get('body', '')) > 47 else "")
                tags = ', '.join(task.get('feature_tags', []) or [])[:17] + ("..." if len(', '.join(task.get('feature_tags', []) or [])) > 17 else "")

                lines.append(f"{task_id:<8} {status:<12} {body:<50} {tags:<20}")

            return '\n'.join(lines)

        else:
            return json.dumps(tasks, ensure_ascii=False)

    @staticmethod
    def _escape_xml(text: str) -> str:
        """Escape XML special characters."""
        return (text.replace('&', '&amp;')
                    .replace('<', '&lt;')
                    .replace('>', '&gt;')
                    .replace('"', '&quot;')
                    .replace("'", '&#39;'))


class TaskCLI:
    """Main CLI application."""

    VERSION = "1.0.0"

    def __init__(self):
        """Initialize CLI."""
        self.config = None
        self.storage = None
        self.search = None
        self.parser = self._create_parser()

    def _get_command_name(self) -> str:
        """
        Detect the command name being used (juno-kanban, juno-feedback, or task).

        Returns:
            The command name as it appears in sys.argv[0]
        """
        import os
        import sys

        # Get the command name from sys.argv[0]
        command_path = sys.argv[0] if sys.argv else 'task'
        command_name = os.path.basename(command_path)

        # Handle different scenarios
        if command_name in ['juno-kanban', 'juno-feedback', 'kanban-juno']:
            return command_name
        elif command_name.endswith('.py'):
            # Direct Python execution, use 'task' as fallback
            return 'task'
        else:
            # Could be task script or other name
            return command_name

    def _create_parser(self) -> argparse.ArgumentParser:
        """
        Create argument parser with all commands and options.

        Returns:
            Configured ArgumentParser
        """
        # Detect the command name being used (juno-kanban, juno-feedback, or task)
        command_name = self._get_command_name()

        # Main parser
        parser = argparse.ArgumentParser(
            prog=command_name,
            description='NDJSON Kanban Task Manager - Optimized for LLM usage',
            epilog=f'Use "{command_name} COMMAND --help" for more information on a specific command',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

        # Global options
        parser.add_argument(
            '-c', '--config',
            metavar='PATH',
            help='Config file path (default: .juno_task/tasks/config.json)'
        )
        parser.add_argument(
            '-f', '--format',
            choices=['ndjson', 'json', 'xml', 'table'],
            metavar='FORMAT',
            help='Output format: ndjson, json, xml, table'
        )
        parser.add_argument(
            '-p', '--pretty',
            action='store_true',
            help='Pretty print output (for json/xml)'
        )
        parser.add_argument(
            '--raw',
            action='store_true',
            help='Output compact/raw format for machine processing'
        )
        parser.add_argument(
            '-v', '--verbose',
            action='store_true',
            help='Verbose output (show debug info)'
        )
        parser.add_argument(
            '--version',
            action='version',
            version=f'task {self.VERSION}'
        )

        # Subcommands
        subparsers = parser.add_subparsers(
            dest='command',
            help='Available commands',
            metavar='COMMAND'
        )

        # CREATE command
        create_parser = subparsers.add_parser(
            'create',
            help='Create a new task',
            description='Create a new task with specified body and optional metadata'
        )
        # Support both positional and --body flag for flexibility
        create_parser.add_argument('body', nargs='?', help='Task description/body (positional)')
        create_parser.add_argument('--body', dest='body_flag', help='Task description/body (--body flag)')
        create_parser.add_argument('--status', help='Initial status (default: from config)')
        create_parser.add_argument('--tags', nargs='*', help='Feature tags (letters/numbers/underscore/hyphen only, space-separated: --tags backend fix_auth OR comma-separated: --tags backend,fix_auth)')
        create_parser.add_argument('--commit', help='Git commit hash')

        # SEARCH command
        search_parser = subparsers.add_parser(
            'search',
            help='Search for tasks',
            description='Search for tasks using various filters'
        )
        search_parser.add_argument('--id', help='Filter by task ID')
        search_parser.add_argument('--status', nargs='*', help='Filter by status (space-separated: --status todo done OR comma-separated: --status todo,done)')
        search_parser.add_argument('--tag', nargs='*', help='Filter by tag (space-separated: --tag backend urgent OR comma-separated: --tag backend,urgent)')
        search_parser.add_argument('--exclude', nargs='*', help='Exclude tasks with these tags (space-separated: --exclude deprecated archived OR comma-separated: --exclude deprecated,archived)')
        search_parser.add_argument('--commit', help='Filter by commit hash')
        search_parser.add_argument('--body', help='Search in task body')
        search_parser.add_argument('--response', help='Search in agent response')
        search_parser.add_argument('--open', action='store_true', help='Show only open tasks (no agent response)')
        search_parser.add_argument('--recent', action='store_true', help='Sort by most recent')
        search_parser.add_argument('--limit', type=int, help='Max number of results (default: from config)')

        # GET command
        get_parser = subparsers.add_parser(
            'get',
            help='Get a specific task by ID',
            description='Retrieve a specific task by its ID'
        )
        get_parser.add_argument('id', help='Task ID')

        # SHOW command (alias for get)
        show_parser = subparsers.add_parser(
            'show',
            help='Get a specific task by ID (alias for get)',
            description='Retrieve a specific task by its ID (alias for get)'
        )
        show_parser.add_argument('id', help='Task ID')

        # UPDATE command
        update_parser = subparsers.add_parser(
            'update',
            help='Update a task',
            description='Update task fields (status, agent_response, commit_hash)'
        )
        update_parser.add_argument('id', help='Task ID')
        update_parser.add_argument('--status', help='New status')
        update_parser.add_argument('--response', help='Agent response')
        update_parser.add_argument('--commit', help='Git commit hash')
        update_parser.add_argument('--tags', nargs='*', help='Feature tags (letters/numbers/underscore/hyphen only, space-separated: --tags backend fix_auth OR comma-separated: --tags backend,fix_auth, replaces existing)')

        # ARCHIVE command (replaces delete/remove)
        archive_parser = subparsers.add_parser(
            'archive',
            help='Archive a task',
            description='Archive a task by setting its status to archive'
        )
        archive_parser.add_argument('id', help='Task ID to archive')

        # MARK command (new workflow command)
        mark_parser = subparsers.add_parser(
            'mark',
            help='Mark a task with status and response',
            description='Mark a task with new status and required agent response'
        )
        mark_parser.add_argument('status', help='New status to mark task as')
        mark_parser.add_argument('-ID', '--id', required=True, help='Task ID to mark')
        mark_parser.add_argument('--response', required=True, help='Agent response (required)')
        mark_parser.add_argument('--commit', help='Git commit hash (recommended)')

        # LIST command (alias for search)
        list_parser = subparsers.add_parser(
            'list',
            help='List tasks (alias for search)',
            description='List tasks with optional filters'
        )
        list_parser.add_argument('--status', nargs='*', help='Filter by status (space-separated: --status todo done OR comma-separated: --status todo,done)')
        list_parser.add_argument('--tag', nargs='*', help='Filter by tag (space-separated: --tag backend urgent OR comma-separated: --tag backend,urgent)')
        list_parser.add_argument('--exclude', nargs='*', help='Exclude tasks with these tags (space-separated: --exclude deprecated archived OR comma-separated: --exclude deprecated,archived)')
        list_parser.add_argument('--open', action='store_true', help='Show only open tasks')
        list_parser.add_argument('--recent', action='store_true', help='Sort by most recent')
        list_parser.add_argument('--limit', type=int, help='Max number of results')

        # MERGE command (new workflow command for combining task files)
        merge_parser = subparsers.add_parser(
            'merge',
            help='Merge multiple .juno_task directories',
            description='Merge tasks from multiple .juno_task directories into a target location'
        )
        merge_parser.add_argument(
            'sources',
            nargs='*',
            help='Source .juno_task directory paths to merge'
        )
        merge_parser.add_argument(
            '--into',
            required=True,
            metavar='TARGET',
            help='Target .juno_task directory path'
        )
        merge_parser.add_argument(
            '--strategy',
            choices=['keep-newer', 'keep-both'],
            default='keep-newer',
            help='Conflict resolution strategy (default: keep-newer)'
        )
        merge_parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview merge without making changes'
        )
        merge_parser.add_argument(
            '--find-all',
            action='store_true',
            help='Auto-discover all .juno_task directories under current directory'
        )

        return parser

    def _normalize_arguments(self, args: List[str]) -> List[str]:
        """
        Normalize command line arguments for case-insensitive handling.

        This method preprocesses arguments to handle case variations like:
        - -ID, -Id, -id, -iD -> -ID (preserve original short form)
        - --ID, --Id, --iD -> --id (normalize to lowercase)
        - -C, -c -> -c (normalize short flags to lowercase)
        - --STATUS, --Status -> --status (normalize long flags to lowercase)

        Args:
            args: Original command line arguments

        Returns:
            Normalized arguments with consistent case
        """
        normalized = []

        for arg in args:
            if arg.startswith('--'):
                # Long form arguments: normalize to lowercase
                if '=' in arg:
                    # Handle --arg=value format
                    flag, value = arg.split('=', 1)
                    normalized.append(f"{flag.lower()}={value}")
                else:
                    # Handle --arg format
                    normalized.append(arg.lower())
            elif arg.startswith('-') and len(arg) > 1:
                # Short form arguments: handle special cases
                if arg.upper() == '-ID':
                    # Special case: -ID variations should map to -ID (preserve uppercase for compatibility)
                    normalized.append('-ID')
                elif len(arg) == 2:
                    # Single character flags: normalize to lowercase
                    normalized.append(f"-{arg[1:].lower()}")
                else:
                    # Multi-character short flags: handle as-is
                    normalized.append(arg)
            else:
                # Not an argument flag, preserve as-is
                normalized.append(arg)

        return normalized

    def _init_components(self, config_path: Optional[str] = None):
        """Initialize configuration, storage, and search components."""
        try:
            self.config = Config(config_path)
            self.storage = TaskStorage(self.config)
            self.search = TaskSearch(self.config, self.storage)
        except ConfigError as e:
            print(f"Configuration error: {e}", file=sys.stderr)
            sys.exit(ExitCode.CONFIG_ERROR)
        except Exception as e:
            print(f"Initialization error: {e}", file=sys.stderr)
            sys.exit(ExitCode.GENERAL_ERROR)

    def _validate_project_root(self) -> bool:
        """
        Validate current location against project root detection rules.

        Returns:
            True if validation passes, False if it fails
        """
        try:
            is_valid, message, recommended_path = self.config.validate_current_location()

            if message:
                if is_valid:
                    # Warning case
                    print(message, file=sys.stderr)
                    print(f"TIP: You can set JUNO_TASK_ROOT={recommended_path} to override this behavior", file=sys.stderr)
                else:
                    # Error case
                    print(message, file=sys.stderr)
                    return False

            return is_valid

        except Exception as e:
            # If validation fails, log but don't block operation
            if self.config and hasattr(self.config, 'config') and \
               self.config.config.get('project_root', {}).get('enable_prevention', True):
                print(f"Warning: Project root validation error: {e}", file=sys.stderr)
            return True

    def _get_output_format(self, args: argparse.Namespace) -> str:
        """Get output format from args or config."""
        if args.format:
            return args.format
        elif self.config:
            return self.config.default_output_format
        else:
            return 'ndjson'

    def _truncate_task_bodies(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Truncate task bodies if they exceed the configured limit."""
        # Get truncation limit from environment variable
        truncate_limit = int(os.environ.get('JUNO_KANBAN_LIST_BODY_TRUNCATE_CHARS', '1200'))

        truncated_tasks = []
        for task in tasks:
            task_copy = task.copy()
            body = task_copy.get('body', '')

            if len(body) > truncate_limit:
                truncated_body = body[:truncate_limit]
                truncation_message = f"[Truncated full size: {len(body)} characters, use get command to read the full body]"
                task_copy['body'] = truncated_body + truncation_message

            truncated_tasks.append(task_copy)

        return truncated_tasks

    def _parse_comma_separated_values(self, values: Optional[List[str]]) -> Optional[List[str]]:
        """Parse comma-separated values from argument lists.

        Supports multiple syntaxes:
        - Space-separated: --status todo done
        - Comma-separated: --status todo,done
        - Mixed: --status todo,done archive

        Args:
            values: List of argument values from argparse (nargs='*')

        Returns:
            Flattened list of individual values, or None if input is None/empty
        """
        if not values:  # None or empty list
            return None

        result = []
        for value in values:
            # Split on commas, strip whitespace, filter out empty strings
            parts = [part.strip() for part in value.split(',') if part.strip()]
            result.extend(parts)

        return result if result else None

    def _format_output(self, tasks: List[Dict[str, Any]], args: argparse.Namespace) -> str:
        """Format output based on format and options."""
        output_format = self._get_output_format(args)

        # New jq-style formatting logic (v1.4.0)
        if hasattr(args, 'raw') and args.raw:
            # --raw flag: use compact output (old behavior)
            pretty = False
        elif args.format:
            # Explicit format specified: use existing pretty logic
            pretty = args.pretty
        else:
            # Default: pretty-printed JSON (new jq-style behavior)
            output_format = 'json'
            pretty = True

        return OutputFormatter.format_tasks(tasks, output_format, pretty)

    def cmd_create(self, args: argparse.Namespace) -> int:
        """Handle create command."""
        try:
            # Validate project root before creating tasks
            if not self._validate_project_root():
                return ExitCode.GENERAL_ERROR
            # Get body from either positional argument or --body flag
            body = args.body_flag if args.body_flag else args.body
            if not body:
                print("Error: Task body is required. Use either 'task create \"body text\"' or 'task create --body \"body text\"'", file=sys.stderr)
                return ExitCode.INVALID_USAGE

            # Prepare task data
            task_data = {
                'body': body,
            }

            if args.status:
                task_data['status'] = args.status
            elif self.config:
                task_data['status'] = self.config.default_status

            if args.tags:
                # Parse comma-separated tags (Issue 26)
                parsed_tags = self._parse_comma_separated_values(args.tags)
                task_data['feature_tags'] = parsed_tags

            if args.commit:
                task_data['commit_hash'] = args.commit

            # Create task
            task = self.storage.create_task(**task_data)

            # Output created task
            output = self._format_output([task.to_dict()], args)
            print(output)

            if args.verbose:
                print(f"Task {task.id} created successfully", file=sys.stderr)

            return ExitCode.SUCCESS

        except ValidationError as e:
            print(f"Validation error: {e}", file=sys.stderr)
            return ExitCode.VALIDATION_ERROR
        except Exception as e:
            print(f"Error creating task: {e}", file=sys.stderr)
            return ExitCode.GENERAL_ERROR

    def cmd_search(self, args: argparse.Namespace) -> int:
        """Handle search command."""
        try:
            # Handle nargs='*' with comma-separated support (Issue 26)
            status_filter = self._parse_comma_separated_values(args.status)
            if status_filter and len(status_filter) == 1:
                status_filter = status_filter[0]  # Single value - use as string for compatibility
            # else: multiple values - keep as list, or None if empty

            tag_filter = self._parse_comma_separated_values(args.tag)
            if tag_filter and len(tag_filter) == 1:
                tag_filter = tag_filter[0]  # Single value - use as string for compatibility
            # else: multiple values - keep as list, or None if empty

            exclude_tags_filter = self._parse_comma_separated_values(args.exclude)
            if exclude_tags_filter and len(exclude_tags_filter) == 1:
                exclude_tags_filter = exclude_tags_filter[0]  # Single value - use as string for compatibility
            # else: multiple values - keep as list, or None if empty

            # Build search filters
            filters = SearchFilters(
                id=args.id,
                status=status_filter,
                tag=tag_filter,
                exclude_tags=exclude_tags_filter,
                commit_hash=args.commit,
                body_text=args.body,
                response_text=args.response,
                open_only=args.open,
                recent=args.recent,
                limit=args.limit or (self.config.default_limit if self.config else 5)
            )

            # Perform search
            results = self.search.search(filters)

            # Check if any results found
            if not results:
                print("No results found")
                return ExitCode.SUCCESS

            # Output results
            output = self._format_output(results, args)
            print(output)

            if args.verbose:
                print(f"Found {len(results)} tasks", file=sys.stderr)

            return ExitCode.SUCCESS

        except Exception as e:
            print(f"Error searching tasks: {e}", file=sys.stderr)
            return ExitCode.GENERAL_ERROR

    def cmd_get(self, args: argparse.Namespace) -> int:
        """Handle get command."""
        try:
            task = self.search.search_by_id(args.id)

            if task:
                output = self._format_output([task], args)
                print(output)
                return ExitCode.SUCCESS
            else:
                print(f"Task not found: {args.id}", file=sys.stderr)
                return ExitCode.GENERAL_ERROR

        except Exception as e:
            print(f"Error getting task: {e}", file=sys.stderr)
            return ExitCode.GENERAL_ERROR

    def cmd_update(self, args: argparse.Namespace) -> int:
        """Handle update command."""
        try:
            # Validate project root before updating tasks
            if not self._validate_project_root():
                return ExitCode.GENERAL_ERROR
            # Build updates dictionary
            updates = {}
            if args.status:
                updates['status'] = args.status
            if args.response:
                updates['agent_response'] = args.response
            if args.commit:
                updates['commit_hash'] = args.commit
            if args.tags is not None:  # Allow empty list
                # Parse comma-separated tags (Issue 26)
                parsed_tags = self._parse_comma_separated_values(args.tags)
                updates['feature_tags'] = parsed_tags if parsed_tags is not None else []

            if not updates:
                print("No updates specified", file=sys.stderr)
                return ExitCode.INVALID_USAGE

            # Perform update
            success = self.storage.update_task(args.id, updates)

            if success:
                if args.verbose:
                    print(f"Task {args.id} updated successfully", file=sys.stderr)

                # Show updated task
                task = self.search.search_by_id(args.id)
                if task:
                    output = self._format_output([task], args)
                    print(output)

                return ExitCode.SUCCESS
            else:
                print(f"Task not found: {args.id}", file=sys.stderr)
                return ExitCode.GENERAL_ERROR

        except ValidationError as e:
            print(f"Validation error: {e}", file=sys.stderr)
            return ExitCode.VALIDATION_ERROR
        except Exception as e:
            print(f"Error updating task: {e}", file=sys.stderr)
            return ExitCode.GENERAL_ERROR

    def cmd_list(self, args: argparse.Namespace) -> int:
        """Handle list command - show tasks with prioritized sorting (open issues first) and summary stats."""
        try:
            # Create filters from user arguments with comma-separated support (Issue 26)
            # Parse comma-separated values and handle nargs='*' which returns empty list when no args provided
            status_filter = self._parse_comma_separated_values(getattr(args, 'status', None))
            if status_filter and len(status_filter) == 1:
                status_filter = status_filter[0]  # Single value - use as string for compatibility
            # else: multiple values - keep as list, or None if empty

            tag_filter = self._parse_comma_separated_values(getattr(args, 'tag', None))
            if tag_filter and len(tag_filter) == 1:
                tag_filter = tag_filter[0]  # Single value - use as string for compatibility
            # else: multiple values - keep as list, or None if empty

            exclude_tags_filter = self._parse_comma_separated_values(getattr(args, 'exclude', None))
            if exclude_tags_filter and len(exclude_tags_filter) == 1:
                exclude_tags_filter = exclude_tags_filter[0]  # Single value - use as string for compatibility
            # else: multiple values - keep as list, or None if empty

            user_filters = SearchFilters(
                id=None,
                status=status_filter,
                tag=tag_filter,
                exclude_tags=exclude_tags_filter,
                commit_hash=None,
                body_text=None,
                open_only=getattr(args, 'open', False),
                recent=getattr(args, 'recent', False),
                limit=1000  # Large limit to get all tasks for summary
            )

            # First get all tasks matching filters for summary statistics
            all_tasks = self.search.search(user_filters)

            # Check if any tasks exist
            if not all_tasks:
                if user_filters.status or user_filters.tag or user_filters.exclude_tags or user_filters.open_only:
                    print("No results found")
                else:
                    print("No tasks found")
                return ExitCode.SUCCESS

            # Now get limited set for display with prioritized sorting
            # Open issues (backlog, todo, in_progress) first by last_modified DESC,
            # then closed issues (done, archive) by last_modified DESC
            display_limit = args.limit or (self.config.default_limit if self.config else 5)

            # Create display filters with the same criteria but limited results
            display_filters = SearchFilters(
                id=None,
                status=status_filter,
                tag=tag_filter,
                exclude_tags=exclude_tags_filter,
                commit_hash=None,
                body_text=None,
                open_only=getattr(args, 'open', False),
                recent=getattr(args, 'recent', False),
                limit=display_limit
            )

            display_tasks = self.search.search_prioritized_list(display_limit, display_filters)

            # Apply body truncation for list command (Issue 25)
            truncated_tasks = self._truncate_task_bodies(display_tasks)

            # Output task results (limited set)
            output = self._format_output(truncated_tasks, args)
            print(output)

            # Show summary statistics based on all tasks
            self._show_summary_stats(all_tasks, args, displayed_count=len(display_tasks))

            if args.verbose:
                print(f"Showing {len(display_tasks)} of {len(all_tasks)} tasks", file=sys.stderr)

            return ExitCode.SUCCESS

        except Exception as e:
            print(f"Error listing tasks: {e}", file=sys.stderr)
            return ExitCode.GENERAL_ERROR

    def _show_summary_stats(self, tasks: List[Dict[str, Any]], args: argparse.Namespace, displayed_count: Optional[int] = None) -> None:
        """Show summary statistics of tasks by status."""
        # Count tasks by status
        status_counts = {}
        for task in tasks:
            status = task.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1

        # Get all possible statuses from config (to show zeros)
        all_statuses = ['backlog', 'todo', 'in_progress', 'done', 'archive']
        if self.config and hasattr(self.config, 'status_values'):
            all_statuses = self.config.status_values

        # Show summary (respect JSON output format)
        if args.format == 'json':
            # Add helper text to JSON format
            help_text = "Use --limit N to show more/fewer results"
            summary = {
                "summary": {
                    "total_tasks": len(tasks),
                    "displayed_tasks": displayed_count if displayed_count is not None else len(tasks),
                    "status_counts": {status: status_counts.get(status, 0) for status in all_statuses},
                    "help": help_text
                }
            }
            print(json.dumps(summary, indent=2 if args.pretty else None))
        else:
            print("\nSUMMARY:", file=sys.stderr)
            if displayed_count is not None and displayed_count != len(tasks):
                print(f"Displayed: {displayed_count} of {len(tasks)} total tasks", file=sys.stderr)
            else:
                print(f"Total tasks: {len(tasks)}", file=sys.stderr)
            print("Status breakdown:", file=sys.stderr)
            for status in all_statuses:
                count = status_counts.get(status, 0)
                print(f"  {status}: {count}", file=sys.stderr)

            # Show any unknown statuses
            for status, count in status_counts.items():
                if status not in all_statuses:
                    print(f"  {status}: {count}", file=sys.stderr)

            # Add helper text to stderr output
            print("", file=sys.stderr)  # Empty line for readability
            print("TIP: Use --limit N to show more/fewer results", file=sys.stderr)

    def cmd_archive(self, args: argparse.Namespace) -> int:
        """Handle archive command."""
        try:
            # Validate project root before archiving tasks
            if not self._validate_project_root():
                return ExitCode.GENERAL_ERROR
            # Check if task exists before archiving
            task = self.storage.find_task(args.id)
            if not task:
                print(f"Error: Task {args.id} not found", file=sys.stderr)
                return ExitCode.VALIDATION_ERROR

            # Update to archive status
            updated = self.storage.update_task(args.id, {'status': 'archive'})
            if updated:
                print(f"Task {args.id} archived successfully")
                if args.verbose:
                    print(f"Task {args.id} status set to archive", file=sys.stderr)
                return ExitCode.SUCCESS
            else:
                print(f"Error: Failed to archive task {args.id}", file=sys.stderr)
                return ExitCode.GENERAL_ERROR

        except Exception as e:
            print(f"Error archiving task: {e}", file=sys.stderr)
            return ExitCode.GENERAL_ERROR

    def cmd_mark(self, args: argparse.Namespace) -> int:
        """Handle mark command with required response."""
        try:
            # Validate project root before marking tasks
            if not self._validate_project_root():
                return ExitCode.GENERAL_ERROR
            # Check if task exists
            task = self.storage.find_task(args.id)
            if not task:
                print(f"Error: Task {args.id} not found", file=sys.stderr)
                return ExitCode.VALIDATION_ERROR

            # Prepare update data
            update_data = {
                'status': args.status,
                'agent_response': args.response
            }

            # Add commit hash if provided, otherwise remind user
            if args.commit:
                update_data['commit_hash'] = args.commit
            else:
                print("Commit Hash is empty, if you have committed something, please give commit hash as well", file=sys.stderr)

            # Update the task
            updated = self.storage.update_task(args.id, update_data)
            if updated:
                print(f"Task {args.id} marked as {args.status}")
                if args.verbose:
                    print(f"Task {args.id} updated with response and status", file=sys.stderr)
                return ExitCode.SUCCESS
            else:
                print(f"Error: Failed to mark task {args.id}", file=sys.stderr)
                return ExitCode.GENERAL_ERROR

        except Exception as e:
            print(f"Error marking task: {e}", file=sys.stderr)
            return ExitCode.GENERAL_ERROR

    def cmd_merge(self, args: argparse.Namespace) -> int:
        """Handle merge command."""
        try:
            # Initialize merger
            merger = TaskMerger(self.config)

            # Determine source paths
            if args.find_all:
                # Auto-discover .juno_task directories
                current_dir = str(Path.cwd())
                source_paths = merger.find_juno_task_directories(current_dir)
                if not source_paths:
                    print("No .juno_task directories found under current directory", file=sys.stderr)
                    return ExitCode.GENERAL_ERROR

                print(f"Found {len(source_paths)} .juno_task directories:")
                for path in source_paths:
                    print(f"  - {path}")
                print()
            else:
                # Use explicitly provided sources
                if not args.sources:
                    print("Error: No source paths provided. Use source paths or --find-all", file=sys.stderr)
                    return ExitCode.INVALID_USAGE

                source_paths = args.sources

            # Validate source paths
            for source_path in source_paths:
                if not os.path.exists(source_path):
                    print(f"Error: Source path does not exist: {source_path}", file=sys.stderr)
                    return ExitCode.IO_ERROR

                tasks_dir = os.path.join(source_path, 'tasks')
                if not os.path.exists(tasks_dir):
                    print(f"Error: Source path is not a valid .juno_task directory: {source_path}", file=sys.stderr)
                    return ExitCode.IO_ERROR

            # Validate target path
            target_path = args.into
            if os.path.exists(target_path) and not os.path.isdir(target_path):
                print(f"Error: Target path exists but is not a directory: {target_path}", file=sys.stderr)
                return ExitCode.IO_ERROR

            # Perform merge
            print(f"Merging {len(source_paths)} source(s) into {target_path}")
            print(f"Strategy: {args.strategy}")
            if args.dry_run:
                print("DRY RUN - No files will be modified")
            print()

            result = merger.merge_files(
                source_paths=source_paths,
                target_path=target_path,
                strategy=args.strategy,
                dry_run=args.dry_run
            )

            if result['success']:
                stats = result['statistics']
                print("MERGE RESULTS:")
                print(f"  Total sources processed: {stats['total_sources']}")
                print(f"  Conflicts found: {stats['conflicts_found']}")
                print(f"  Conflicts resolved: {stats['conflicts_resolved']}")
                print(f"  New tasks added: {stats['tasks_added']}")
                print(f"  Existing tasks kept: {stats['tasks_kept']}")
                print(f"  Final task count: {stats['final_task_count']}")

                if result['conflicts']:
                    print("\nCONFLICTS RESOLVED:")
                    for conflict in result['conflicts']:
                        print(f"  - {conflict}")

                if args.dry_run:
                    print("\nDRY RUN COMPLETE - No files were modified")
                    print("Run without --dry-run to perform the actual merge")
                else:
                    print(f"\nMerge completed successfully!")
                    print(f"Merged tasks are now available in: {target_path}")

                return ExitCode.SUCCESS
            else:
                print("Merge failed", file=sys.stderr)
                return ExitCode.GENERAL_ERROR

        except Exception as e:
            print(f"Error during merge: {e}", file=sys.stderr)
            return ExitCode.GENERAL_ERROR

    def show_help(self, args: argparse.Namespace) -> int:
        """Show help text optimized for LLMs with usage examples."""
        command_name = self._get_command_name()

        print("Shell-based Kanban Task Manager")
        print()
        print("COMMANDS:")
        print("  create  - Create a new task")
        print("  search  - Search for tasks")
        print("  get     - Get a specific task by ID")
        print("  update  - Update a task")
        print("  mark    - Mark a task with status and response")
        print("  archive - Archive a task (set status to archive)")
        print("  list    - List tasks")
        print("  merge   - Merge multiple .juno_task directories")
        print()
        print("USAGE EXAMPLES:")
        print("  # Create a task (two ways)")
        print(f"  {command_name} create \"Fix authentication bug\" --tags security backend")
        print(f"  {command_name} create --body \"Fix authentication bug\" --tags security backend")
        print()
        print("  # Search tasks")
        print(f"  {command_name} search --status backlog --limit 5")
        print(f"  {command_name} search --tag security --recent")
        print(f"  {command_name} search --open  # tasks without agent_response")
        print(f"  {command_name} list --exclude deprecated automatic-test  # exclude tags")
        print()
        print("  # Update task")
        print(f"  {command_name} update ABC123 --status in_progress")
        print(f"  {command_name} update ABC123 --response \"Working on it\"")
        print()
        print("  # Mark task (with required response)")
        print(f"  {command_name} mark todo -ID ABC123 --response \"Task completed\" --commit abc123")
        print()
        print("  # Archive task")
        print(f"  {command_name} archive ABC123")
        print()
        print("  # Get specific task")
        print(f"  {command_name} get ABC123")
        print()
        print("  # Merge .juno_task directories")
        print(f"  {command_name} merge ./sub1/.juno_task ./sub2/.juno_task --into ./.juno_task")
        print(f"  {command_name} merge --find-all --into ./.juno_task --dry-run")
        print(f"  {command_name} merge ./src/.juno_task --into . --strategy keep-both")
        print()

        # Show config info if available
        if self.config:
            print("CONFIGURATION:")
            available_statuses = ', '.join(self.config.status_values) if hasattr(self.config, 'status_values') else 'backlog, todo, in_progress, done, archive'
            print(f"  Available statuses: {available_statuses}")
            print(f"  Default status: {getattr(self.config, 'default_status', 'backlog')}")
            if hasattr(self.config, 'tag_pattern'):
                print(f"  Tag pattern: {self.config.tag_pattern}")
            print()

        print(f"Use '{command_name} COMMAND --help' for detailed help on any command")
        return ExitCode.SUCCESS

    def run(self, args: Optional[List[str]] = None) -> int:
        """
        Run the CLI application.

        Args:
            args: Command line arguments (default: sys.argv[1:])

        Returns:
            Exit code
        """
        try:
            # Check for shortcut syntax before parsing
            args_to_parse = args if args is not None else sys.argv[1:]

            if args_to_parse and len(args_to_parse) > 0 and not args_to_parse[0].startswith('-'):
                # Check if first argument is not a known command
                known_commands = ['create', 'search', 'get', 'show', 'update', 'list', 'archive', 'mark', 'merge']
                if args_to_parse[0] not in known_commands:
                    # Treat as shortcut: juno-kanban "task body" -> juno-kanban create "task body"
                    args_to_parse = ['create'] + args_to_parse

            # Preprocess arguments for case-insensitive handling
            args_to_parse = self._normalize_arguments(args_to_parse)

            parsed_args = self.parser.parse_args(args_to_parse)

            # Initialize components with config path
            self._init_components(parsed_args.config)

            # Handle commands
            if not parsed_args.command:
                # No command specified - show help
                return self.show_help(parsed_args)

            elif parsed_args.command == 'create':
                return self.cmd_create(parsed_args)

            elif parsed_args.command == 'search':
                return self.cmd_search(parsed_args)

            elif parsed_args.command == 'get':
                return self.cmd_get(parsed_args)

            elif parsed_args.command == 'show':
                return self.cmd_get(parsed_args)  # Alias for get command

            elif parsed_args.command == 'update':
                return self.cmd_update(parsed_args)

            elif parsed_args.command == 'list':
                return self.cmd_list(parsed_args)

            elif parsed_args.command == 'archive':
                return self.cmd_archive(parsed_args)

            elif parsed_args.command == 'mark':
                return self.cmd_mark(parsed_args)

            elif parsed_args.command == 'merge':
                return self.cmd_merge(parsed_args)

            else:
                print(f"Unknown command: {parsed_args.command}", file=sys.stderr)
                return ExitCode.INVALID_USAGE

        except KeyboardInterrupt:
            print("\nInterrupted", file=sys.stderr)
            return ExitCode.GENERAL_ERROR

        except BrokenPipeError:
            # Handle broken pipe (e.g., piping to head)
            return ExitCode.SUCCESS

        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            if hasattr(parsed_args, 'verbose') and parsed_args.verbose:
                import traceback
                traceback.print_exc()
            return ExitCode.GENERAL_ERROR


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the CLI.

    Args:
        args: Command line arguments (default: sys.argv[1:])

    Returns:
        Exit code
    """
    cli = TaskCLI()
    return cli.run(args)


if __name__ == '__main__':
    sys.exit(main())