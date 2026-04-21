from __future__ import annotations

from collections import Counter


def iter_body_text_blocks(page: object, top_ratio: float = 0.05, bottom_ratio: float = 0.05) -> list[str]:
    """Extract text blocks from the central body region of a PyMuPDF page."""

    rect = page.rect
    rect_type = rect.__class__
    clip = rect_type(
        rect.x0,
        rect.y0 + rect.height * top_ratio,
        rect.x1,
        rect.y1 - rect.height * bottom_ratio,
    )

    blocks = page.get_text("blocks", clip=clip, sort=True) or []
    body_lines: list[str] = []
    for block in blocks:
        if len(block) < 5:
            continue
        text = str(block[4]).strip()
        if text:
            body_lines.append(text)
    return body_lines


def drop_repeated_edge_lines(page_texts: dict[int, str], min_repeat: int = 3) -> dict[int, str]:
    """Remove repeated leading and trailing lines across many pages."""

    first_lines = Counter()
    last_lines = Counter()
    normalized_by_page: dict[int, list[str]] = {}

    for unit, text in page_texts.items():
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        normalized_by_page[unit] = lines
        if lines:
            first_lines[lines[0]] += 1
            last_lines[lines[-1]] += 1

    repeated_first = {line for line, count in first_lines.items() if count >= min_repeat}
    repeated_last = {line for line, count in last_lines.items() if count >= min_repeat}

    cleaned: dict[int, str] = {}
    for unit, lines in normalized_by_page.items():
        updated = list(lines)
        if updated and updated[0] in repeated_first:
            updated = updated[1:]
        if updated and updated[-1] in repeated_last:
            updated = updated[:-1]
        cleaned[unit] = "\n".join(updated).strip()
    return cleaned
