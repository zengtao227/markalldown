from __future__ import annotations

import re


def merge_markdown_fragments(text: str) -> str:
    """Merge wrapped text lines while preserving common Markdown structure."""

    merged: list[str] = []
    paragraph = ""

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            if paragraph:
                merged.append(paragraph)
                paragraph = ""
            merged.append("")
            continue

        if _is_structural_line(stripped):
            if paragraph:
                merged.append(paragraph)
                paragraph = ""
            merged.append(stripped)
            continue

        if not paragraph:
            paragraph = stripped
        elif paragraph.endswith("-") and not paragraph.endswith("--"):
            paragraph = paragraph[:-1] + stripped
        else:
            paragraph = f"{paragraph} {stripped}"

    if paragraph:
        merged.append(paragraph)

    text = "\n".join(merged)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _is_structural_line(line: str) -> bool:
    return (
        line.startswith(("#", "-", "*", ">", "|"))
        or bool(re.match(r"^\d+\.\s+", line))
        or bool(re.match(r"^[A-Z][A-Z0-9 _-]{1,40}:$", line))
    )
