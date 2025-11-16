"""
Utility functions for file operations
"""

import os
import json
from pathlib import Path
from typing import Any, Dict


def ensure_dir(path: Path) -> Path:
    """Ensure directory exists, create if not"""
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_json(data: Dict[Any, Any], file_path: Path):
    """Save data as JSON file"""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_json(file_path: Path) -> Dict[Any, Any]:
    """Load JSON file"""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_file_size(file_path: Path) -> int:
    """Get file size in bytes"""
    return os.path.getsize(file_path)
