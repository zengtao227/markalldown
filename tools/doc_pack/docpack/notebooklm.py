from __future__ import annotations

from pathlib import Path

from docpack.models import PackOptions, PackResult

WORD_COUNT_WARNING_THRESHOLD = 200_000

DIRECT_UPLOAD_EXTENSIONS = {
    ".avif",
    ".bmp",
    ".csv",
    ".docx",
    ".epub",
    ".gif",
    ".heic",
    ".heif",
    ".ico",
    ".jpe",
    ".jpeg",
    ".jpg",
    ".jp2",
    ".md",
    ".mp3",
    ".pdf",
    ".png",
    ".pptx",
    ".tif",
    ".tiff",
    ".txt",
    ".wav",
    ".webp",
}


def render_upload_text(result: PackResult) -> str:
    return result.content_markdown.strip() + "\n"


def render_handoff(options: PackOptions, result: PackResult, manifest: dict) -> str:
    template = _template_path().read_text(encoding="utf-8")

    recommended_sources = []
    if _supports_direct_upload(options.source_path):
        recommended_sources.append(f"- Required: original source `{options.source_path}`")
        recommended_sources.append(
            "- Optional supplement: `notebooklm_upload.txt` only if you want a cleaned text-only fallback view."
        )
    else:
        recommended_sources.append(
            f"- Original local file `{options.source_path.name}` is not a preferred direct NotebookLM upload type in this workflow."
        )
        recommended_sources.append("- Required fallback: `notebooklm_upload.txt`")
        if options.source_path.suffix.lower() == ".xlsx":
            recommended_sources.append(
                "- If the spreadsheet needs to live inside NotebookLM, export the relevant sheets to `csv` or move them into Google Sheets first."
            )
        if options.source_path.suffix.lower() in {".html", ".htm"}:
            recommended_sources.append(
                "- Prefer the public web URL over the local HTML file when the same content is available online."
            )

    if result.images:
        recommended_sources.append(
            "- Keep page-perfect image inspection local in Claude/Codex unless you intentionally add selected images as separate NotebookLM sources."
        )
    if result.tables:
        recommended_sources.append(
            "- For synthesis tasks: consider uploading the extracted CSV files from `tables/` as supplementary"
            " sources — Markdown tables are ~28% more retrievable in RAG than embedded PDF cells."
        )
        recommended_sources.append(
            "- For row-level exact reasoning: keep CSV work local in Claude/Codex, not in NotebookLM."
        )

    word_count = len(result.content_markdown.split())
    if word_count > WORD_COUNT_WARNING_THRESHOLD:
        recommended_sources.append(
            f"⚠️ Large document: {word_count:,} words in content.md. "
            "NotebookLM retrieval accuracy can degrade above ~200k words. "
            "Consider splitting into thematic sub-notebooks (20–30 sources each) "
            "to maintain source-grounded accuracy."
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
    follow_up_prompts = "\n".join(
        [
            f"1. `Answer this task using only the notebook sources: {options.analysis_goal.strip() or 'Summarize the document using only the provided evidence.'}`",
            "2. `List the main findings by source and identify contradictions or unresolved questions.`",
            "3. `Identify which pages, charts, sections, or sheets still need direct human review before action.`",
            "4. `Summarize what should be handed back to Claude/Codex for final execution.`",
        ]
    )

    return template.format(
        source_name=options.source_path.name,
        source_path=options.source_path,
        backend=result.backend,
        selected_units=_format_units(result.selected_units) or "All selected units in this pack",
        gateway_mode="manual-notebooklm-gateway",
        notebook_title=f"{options.source_path.stem} research",
        research_theme=options.analysis_goal.strip()
        or "Summarize the document using only the provided evidence.",
        notebooklm_sources="\n".join(recommended_sources),
        opening_prompt=_opening_prompt(options),
        follow_up_prompts=follow_up_prompts,
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


def _supports_direct_upload(source_path: Path) -> bool:
    return source_path.suffix.lower() in DIRECT_UPLOAD_EXTENSIONS


def read_all_notebook_ids(pack_dir: Path) -> list[str]:
    """Return all notebook IDs from notebooklm_link.txt.

    Supports multi-notebook splits: one URL per line, lines starting with # are comments.
    Use this when a corpus was split across thematic sub-notebooks.
    """
    link_file = pack_dir / "notebooklm_link.txt"
    if not link_file.exists():
        return []
    ids = []
    for line in link_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        notebook_id = line.rstrip("/").split("/")[-1]
        if notebook_id:
            ids.append(notebook_id)
    return ids


def read_notebook_id(pack_dir: Path) -> str | None:
    """Return the first notebook ID from notebooklm_link.txt, or None if not registered."""
    ids = read_all_notebook_ids(pack_dir)
    return ids[0] if ids else None


def _opening_prompt(options: PackOptions) -> str:
    goal = options.analysis_goal.strip() or "Summarize the document using only the provided evidence."
    return "\n".join(
        [
            f"Research theme: {goal}",
            "",
            "Rules:",
            "1. Use only the notebook sources.",
            "2. Cite evidence for every non-trivial claim.",
            "3. If evidence is missing, say uncertain.",
            "4. Do not invent details that are not grounded in the sources.",
            "5. When quoting, use only exact text found in the sources.",
            "   If a 100% verbatim match cannot be located, write [Quote Not Found] instead of paraphrasing.",
            "",
            "Return sections:",
            "## Findings From Sources",
            "## Analysis Steps",
            "## Conclusion",
            "## Gaps Not Covered By Sources",
        ]
    )
