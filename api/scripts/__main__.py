#!/usr/bin/env python
"""Convenience entrypoint so `python scripts/seed_from_json.py` works from api/."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.seed_from_json import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())