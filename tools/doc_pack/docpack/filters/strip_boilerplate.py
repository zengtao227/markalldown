from __future__ import annotations

import re

_PATTERNS = [
    re.compile(pattern, flags=re.IGNORECASE)
    for pattern in (
        r"\ball rights reserved\b",
        r"\bconfidential\b",
        r"\bdo not distribute\b",
        r"\bcopyright\b",
        r"\bsafe harbor\b",
        r"\bforward-looking statements?\b",
        r"\btable of contents\b",
        r"\breferences\b",
    )
]


def strip_common_boilerplate(text: str) -> str:
    """Remove obvious low-value boilerplate lines without touching paragraphs."""

    cleaned: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and any(pattern.search(stripped) for pattern in _PATTERNS):
            continue
        cleaned.append(line)
    return "\n".join(cleaned).strip()
