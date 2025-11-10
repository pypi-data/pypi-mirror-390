"""Version information for ToDoWrite CLI."""

from __future__ import annotations

import sys
from pathlib import Path

# Navigate from: cli_package/src/todowrite_cli/version.py -> project root
current_file = Path(__file__)
project_root = current_file.parent.parent.parent.parent

# Try to import from shared_version.py at project root
if (project_root / "shared_version.py").exists():
    sys.path.insert(0, str(project_root))
    from shared_version import __author__, __email__, __version__
else:
    # Fallback for when shared_version.py is not available
    __version__ = "0.4.1"
    __author__ = "D Deryl Downey"
    __email__ = "dderyldowney@gmail.com"

__all__ = ["__author__", "__email__", "__version__"]
