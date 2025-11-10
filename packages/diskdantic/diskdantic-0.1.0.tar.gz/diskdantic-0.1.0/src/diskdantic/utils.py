from __future__ import annotations

import re
from typing import Any

SLUG_PATTERN = re.compile(r"[^a-z0-9]+")


def slugify(value: Any) -> str:
    """Normalize a value into a filesystem-friendly slug."""
    text = str(value).strip().lower()
    text = SLUG_PATTERN.sub("-", text)
    text = text.strip("-")
    return text or "item"
