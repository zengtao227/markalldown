from __future__ import annotations

from pathlib import Path

from docpack.models import PackOptions, PackResult


def _template_path() -> Path:
    return Path(__file__).resolve().parents[1] / "templates" / "prompt_template.md"


def render_prompt(options: PackOptions, result: PackResult, manifest: dict) -> str:
    template = _template_path().read_text(encoding="utf-8")
    image_lines = "\n".join(
        f"- `{artifact.path.relative_to(options.output_dir)}` from unit {artifact.unit}"
        for artifact in result.images
    )
    table_lines = "\n".join(
        f"- `{artifact.path.relative_to(options.output_dir)}` ({artifact.rows} rows x {artifact.columns} cols)"
        for artifact in result.tables
    )
    warning_lines = "\n".join(f"- {warning}" for warning in result.warnings)
    if not image_lines:
        image_lines = "- None"
    if not table_lines:
        table_lines = "- None"
    if not warning_lines:
        warning_lines = "- None"

    return template.format(
        source_name=options.source_path.name,
        backend=result.backend,
        selected_units=_format_units(result.selected_units),
        content_path="content.md",
        image_lines=image_lines,
        table_lines=table_lines,
        review_units=_format_units(result.needs_review_units) or "None",
        warning_lines=warning_lines,
        goal=options.analysis_goal.strip() or "Summarize the document using only the provided evidence.",
    )


def _format_units(units: list[int]) -> str:
    if not units:
        return ""
    return ", ".join(str(unit) for unit in units)
