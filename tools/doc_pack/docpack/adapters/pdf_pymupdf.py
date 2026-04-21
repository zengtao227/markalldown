from __future__ import annotations

from pathlib import Path

from docpack.filters import (
    drop_repeated_edge_lines,
    iter_body_text_blocks,
    merge_markdown_fragments,
    strip_common_boilerplate,
)
from docpack.models import ImageArtifact, MissingDependencyError, PackOptions, PackResult, ProcessingError

from .pdf_markitdown_fallback import build_pack as build_pdf_markitdown_fallback_pack

try:
    import fitz
except ImportError:  # pragma: no cover - optional dependency
    fitz = None

try:
    import pymupdf4llm
except ImportError:  # pragma: no cover - optional dependency
    pymupdf4llm = None

try:
    from PIL import Image
except ImportError:  # pragma: no cover - optional dependency
    Image = None


def build_pack(options: PackOptions) -> PackResult:
    try:
        return _build_primary_pack(options)
    except ProcessingError:
        if not options.allow_pdf_fallback:
            raise
        return build_pdf_markitdown_fallback_pack(options)


def _build_primary_pack(options: PackOptions) -> PackResult:
    if fitz is None:
        raise MissingDependencyError(
            "PyMuPDF is not installed. Install dependencies from tools/doc_pack/requirements.txt."
        )

    document = fitz.open(options.source_path)
    total_pages = len(document)
    selected_pages = options.selected_units or list(range(1, total_pages + 1))
    selected_pages = [page for page in selected_pages if 1 <= page <= total_pages]
    if not selected_pages:
        raise ProcessingError("No pages remain after applying page-range selection.")

    page_texts: dict[int, str] = {}
    warnings: list[str] = []
    extraction_mode = "pymupdf4llm" if pymupdf4llm is not None else "pymupdf-blocks"

    for page_number in selected_pages:
        text, page_warning = _extract_page_markdown(document, page_number, options)
        page_texts[page_number] = text.strip()
        if page_warning:
            warnings.append(page_warning)

    page_texts = drop_repeated_edge_lines(page_texts)

    needs_review: list[int] = []
    page_stats: list[dict[str, float | int]] = []
    sections: list[str] = [f"# PDF Summary\n", f"Source: `{options.source_path.name}`\n"]

    for page_number in selected_pages:
        text = merge_markdown_fragments(strip_common_boilerplate(page_texts.get(page_number, "")))
        quality = _page_quality(text)
        page_stats.append(
            {
                "page": page_number,
                "characters": quality["characters"],
                "suspicious_ratio": quality["suspicious_ratio"],
            }
        )
        if quality["needs_review"]:
            needs_review.append(page_number)

        sections.extend(
            [
                f"## Page {page_number}",
                "",
                text or "_No extractable text._",
                "",
            ]
        )

    try:
        images = _export_page_images(document, options, selected_pages, needs_review)
    except MissingDependencyError as exc:
        warnings.append(str(exc))
        images = []
    document.close()

    if needs_review:
        warnings.append(
            "Some pages have low text density or suspicious OCR output. Review the referenced page images before relying on them."
        )

    return PackResult(
        backend="pdf-pymupdf",
        document_type="pdf",
        selected_units=selected_pages,
        content_markdown="\n".join(section.strip() for section in sections if section.strip()),
        warnings=warnings,
        filters_applied=[
            "strip_header_footer",
            "drop_repeated_edge_lines",
            "strip_common_boilerplate",
            "merge_markdown_fragments",
        ],
        needs_review_units=needs_review,
        images=images,
        metadata={
            "page_count": total_pages,
            "extraction_mode": extraction_mode,
            "page_stats": page_stats,
        },
    )


def _extract_page_markdown(document: object, page_number: int, options: PackOptions) -> tuple[str, str | None]:
    if pymupdf4llm is not None:
        try:
            markdown = _extract_with_pymupdf4llm(document, page_number, options)
        except ProcessingError as exc:
            markdown = ""
            warning = str(exc)
        else:
            warning = None
        if markdown:
            return markdown, warning

    page = document.load_page(page_number - 1)
    blocks = iter_body_text_blocks(page)
    return "\n\n".join(blocks), "Used PyMuPDF block fallback for page %s." % page_number if pymupdf4llm is not None else None


def _extract_with_pymupdf4llm(document: object, page_number: int, options: PackOptions) -> str:
    if fitz is None or pymupdf4llm is None:
        return ""

    temp_pdf = options.work_dir / f"page_{page_number:03d}.pdf"
    temp_doc = fitz.open()
    temp_doc.insert_pdf(document, from_page=page_number - 1, to_page=page_number - 1)
    temp_doc.save(temp_pdf)
    temp_doc.close()

    try:
        extracted = pymupdf4llm.to_markdown(str(temp_pdf))
    except Exception as exc:  # pragma: no cover - runtime integration guard
        raise ProcessingError(f"PyMuPDF4LLM failed on page {page_number}: {exc}") from exc

    if isinstance(extracted, str):
        return extracted
    for attribute in ("text_content", "markdown", "content"):
        value = getattr(extracted, attribute, None)
        if isinstance(value, str):
            return value
    return str(extracted)


def _page_quality(text: str) -> dict[str, float | int | bool]:
    compact = "".join(character for character in text if not character.isspace())
    characters = len(compact)
    suspicious = sum(1 for character in compact if character == "\ufffd" or ord(character) < 32)
    ratio = suspicious / characters if characters else 1.0
    needs_review = characters < 60 or ratio > 0.02
    return {
        "characters": characters,
        "suspicious_ratio": round(ratio, 4),
        "needs_review": needs_review,
    }


def _export_page_images(
    document: object,
    options: PackOptions,
    selected_pages: list[int],
    needs_review: list[int],
) -> list[ImageArtifact]:
    targets = sorted(set(options.image_units or needs_review))
    if not targets:
        return []
    if Image is None:
        raise MissingDependencyError(
            "Pillow is required for JPEG image export. Install dependencies from tools/doc_pack/requirements.txt."
        )

    artifacts: list[ImageArtifact] = []
    for page_number in targets:
        if page_number not in selected_pages:
            continue
        page = document.load_page(page_number - 1)
        scale = options.dpi / 72.0
        pixmap = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
        suffix = "jpg" if options.image_format == "jpeg" else "png"
        path = options.output_dir / "images" / f"page_{page_number:03d}_page.{suffix}"

        if options.image_format == "png":
            pixmap.save(str(path))
        else:
            image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
            image.save(path, format="JPEG", quality=85, optimize=True)

        artifacts.append(
            ImageArtifact(
                path=path,
                unit=page_number,
                kind="page",
                width=pixmap.width,
                height=pixmap.height,
            )
        )
    return artifacts
