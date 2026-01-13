#!/usr/bin/env python
"""Django's command-line utility for administrative tasks.

This file adds `/src` to `sys.path` so the project package located
in `/src` can be imported as `hotel`.
"""
import os
import sys
from pathlib import Path


def main():
    """Run administrative tasks."""
    # ensure /src is on sys.path so `import hotel` finds src/hotel
    repo_root = Path(__file__).resolve().parent
    src_path = str(repo_root / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hotel.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
