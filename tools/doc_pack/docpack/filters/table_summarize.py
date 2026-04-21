from __future__ import annotations

from typing import Iterable


def render_markdown_table(headers: list[str], rows: Iterable[list[str]]) -> str:
    sanitized_headers = [_sanitize_cell(cell) for cell in headers]
    body_rows = [[_sanitize_cell(cell) for cell in row] for row in rows]
    if not sanitized_headers:
        return ""

    lines = [
        "| " + " | ".join(sanitized_headers) + " |",
        "| " + " | ".join("---" for _ in sanitized_headers) + " |",
    ]
    for row in body_rows:
        padded = row + [""] * max(0, len(sanitized_headers) - len(row))
        lines.append("| " + " | ".join(padded[: len(sanitized_headers)]) + " |")
    return "\n".join(lines)


def format_numeric_summaries(summaries: dict[str, dict[str, float]]) -> list[str]:
    lines: list[str] = []
    for column, stats in summaries.items():
        count = int(stats["count"])
        average = stats["sum"] / count if count else 0.0
        lines.append(
            f"`{column}`: count={count}, min={stats['min']:.4g}, max={stats['max']:.4g}, avg={average:.4g}"
        )
    return lines


def _sanitize_cell(value: object) -> str:
    text = "" if value is None else str(value)
    return text.replace("\n", " ").replace("|", "\\|").strip()
