"""
Simple utilities for project setup.
"""
import sys
from pathlib import Path


def setup_project_path():
    """
    Add the project root to sys.path so catrxneng can be imported from anywhere.
    """
    # Find the catrxneng directory by walking up
    current = Path.cwd()
    while current.name != 'catrxneng' and current.parent != current:
        current = current.parent

    if current.name == 'catrxneng':
        project_root = current.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        return project_root

    # Fallback: assume we're somewhere under the project
    # Try going up 2-3 levels
    for levels in range(1, 4):
        candidate = Path.cwd()
        for _ in range(levels):
            candidate = candidate.parent
        if (candidate / 'catrxneng').exists():
            if str(candidate) not in sys.path:
                sys.path.insert(0, str(candidate))
            return candidate

    return None