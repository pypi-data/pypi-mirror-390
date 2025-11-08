"""
Kanban Task Manager

A dead simple shell-based kanban task manager for managing tasks through NDJSON files.

Main features:
- NDJSON storage with 8 task fields
- Configurable status workflows
- Feature tag system
- High-performance search with ripgrep
- LLM-optimized CLI interface
- Atomic file operations

Author: Feedback Shell Team
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Feedback Shell Team"

# Export main classes for easy importing
from .models import Task
from .config import Config
from .validators import TaskValidator, ValidationError

# Import other modules when they exist
try:
    from .storage import TaskStorage
except ImportError:
    TaskStorage = None

try:
    from .search import TaskSearch
except ImportError:
    TaskSearch = None

try:
    from .cli import main as cli_main
except ImportError:
    cli_main = None

__all__ = [
    "Task",
    "Config",
    "TaskValidator",
    "ValidationError",
]

# Add modules that exist
if TaskStorage:
    __all__.append("TaskStorage")
if TaskSearch:
    __all__.append("TaskSearch")
if cli_main:
    __all__.append("cli_main")