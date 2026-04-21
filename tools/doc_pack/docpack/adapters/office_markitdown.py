from __future__ import annotations

from pathlib import Path
from typing import Any

from docpack.filters import merge_markdown_fragments, strip_common_boilerplate
from docpack.models import MissingDependencyError, PackOptions, PackResult

try:
    from markitdown import MarkItDown
except ImportError:  # pragma: no cover - optional dependency
    MarkItDown = None


def build_pack(options: PackOptions) -> PackResult:
    return _build_with_markitdown(options, backend_name="markitdown")


def build_pdf_fallback_pack(options: PackOptions) -> PackResult:
    warnings = []
    if options.selected_units:
        warnings.append("MarkItDown PDF fallback ignores page-range selection and processed the whole document.")
    result = _build_with_markitdown(options, backend_name="markitdown-pdf-fallback")
    result.document_type = "pdf"
    result.warnings.extend(warnings)
    return result


def _build_with_markitdown(options: PackOptions, backend_name: str) -> PackResult:
    if MarkItDown is None:
        raise MissingDependencyError(
            "MarkItDown is not installed. Install dependencies from tools/doc_pack/requirements.txt."
        )

    converter = MarkItDown()
    converted = converter.convert(str(options.source_path))
    raw_text = _extract_markdown_text(converted)
    cleaned_text = merge_markdown_fragments(strip_common_boilerplate(raw_text))

    return PackResult(
        backend=backend_name,
        document_type=_detect_document_type(options.source_path),
        selected_units=options.selected_units or [],
        content_markdown=cleaned_text,
        filters_applied=["strip_common_boilerplate", "merge_markdown_fragments"],
        metadata={
            "extension": options.source_path.suffix.lower(),
            "character_count": len(cleaned_text),
        },
    )


def _extract_markdown_text(converted: Any) -> str:
    for attribute in ("text_content", "markdown", "content"):
        value = getattr(converted, attribute, None)
        if isinstance(value, str) and value.strip():
            return value
    if isinstance(converted, str):
        return converted
    return str(converted)


def _detect_document_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".doc", ".docx", ".odt"}:
        return "document"
    if suffix in {".html", ".htm", ".xml"}:
        return "markup"
    if suffix in {".csv", ".tsv"}:
        return "tabular-text"
    if suffix == ".pdf":
        return "pdf"
    return "generic"
