from __future__ import annotations

from pathlib import Path

from docpack.models import PackOptions, PackResult


def render_upload_text(result: PackResult) -> str:
    return result.content_markdown.strip() + "\n"


def render_handoff(options: PackOptions, result: PackResult, manifest: dict) -> str:
    template = _template_path().read_text(encoding="utf-8")

    recommended_sources = ["- Required: `notebooklm_upload.txt`"]
    if result.document_type == "pdf":
        recommended_sources.append(
            f"- Optional but recommended for visual grounding: original source `{options.source_path}`"
        )
    if result.images:
        recommended_sources.append(
            "- If NotebookLM still misses visual details, keep image review local in Claude/Codex using `images/`."
        )
    if result.tables:
        recommended_sources.append(
            "- Keep detailed CSV reasoning local. Use NotebookLM for summary-level questions, not row-perfect spreadsheet work."
        )

    warning_lines = "\n".join(f"- {warning}" for warning in result.warnings) or "- None"
    image_lines = "\n".join(
        f"- `{artifact.path.relative_to(options.output_dir)}` from unit {artifact.unit}"
        for artifact in result.images
    ) or "- None"
    table_lines = "\n".join(
        f"- `{artifact.path.relative_to(options.output_dir)}` ({artifact.rows} rows x {artifact.columns} cols)"
        for artifact in result.tables
    ) or "- None"

    return template.format(
        source_name=options.source_path.name,
        source_path=options.source_path,
        backend=result.backend,
        selected_units=_format_units(result.selected_units) or "All selected units in this pack",
        notebooklm_sources="\n".join(recommended_sources),
        image_lines=image_lines,
        table_lines=table_lines,
        warning_lines=warning_lines,
        goal=options.analysis_goal.strip() or "Summarize the document using only the provided evidence.",
    )


def _template_path() -> Path:
    return Path(__file__).resolve().parents[1] / "templates" / "notebooklm_handoff_template.md"


def _format_units(units: list[int]) -> str:
    if not units:
        return ""
    return ", ".join(str(unit) for unit in units)
