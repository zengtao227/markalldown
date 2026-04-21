#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from docpack.adapters import resolve_adapter
from docpack.models import MissingDependencyError, PackOptions, PackResult, ProcessingError
from docpack.notebooklm import render_handoff as render_notebooklm_handoff
from docpack.notebooklm import render_upload_text as render_notebooklm_upload_text
from docpack.prompting import render_prompt
from docpack.utils import ensure_dir, parse_page_spec, sha256_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build an LLM-friendly pack from PDF, Office, spreadsheet, or slide documents."
    )
    parser.add_argument("source", help="Source document path.")
    parser.add_argument(
        "--output-root",
        help="Directory that will receive <stem>_llm_pack. Defaults to the source parent directory.",
    )
    parser.add_argument(
        "--page-range",
        help="Optional page or slide selection, for example 1-5,8,10-12.",
    )
    parser.add_argument(
        "--image-pages",
        help="Pages or slides to export as images. Defaults to adapter-specific behavior.",
    )
    parser.add_argument(
        "--image-format",
        choices=("jpeg", "png"),
        default="jpeg",
        help="Image export format. Default: jpeg.",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=150,
        help="Image DPI. Default: 150.",
    )
    parser.add_argument(
        "--hd",
        action="store_true",
        help="Use 300 DPI unless --dpi is explicitly provided.",
    )
    parser.add_argument(
        "--ocr-engine",
        default="auto",
        help="OCR engine label to record in the manifest. Default: auto.",
    )
    parser.add_argument(
        "--goal",
        default="Read the cleaned markdown first, then inspect referenced artifacts and answer only the stated task.",
        help="Analysis goal or instruction to prefill into prompt.md.",
    )
    parser.add_argument(
        "--preview-rows",
        type=int,
        default=5,
        help="Preview rows per spreadsheet sheet. Default: 5.",
    )
    parser.add_argument(
        "--disable-pdf-fallback",
        action="store_true",
        help="Do not fall back to MarkItDown when the primary PDF backend fails.",
    )
    return parser


def build_options(args: argparse.Namespace) -> PackOptions:
    source_path = Path(args.source).expanduser().resolve()
    if not source_path.exists():
        raise ProcessingError(f"Source file does not exist: {source_path}")

    output_root = (
        Path(args.output_root).expanduser().resolve()
        if args.output_root
        else source_path.parent
    )
    output_dir = output_root / f"{source_path.stem}_llm_pack"
    ensure_dir(output_dir)
    ensure_dir(output_dir / "images")
    ensure_dir(output_dir / "tables")

    dpi = args.dpi
    if args.hd and args.dpi == 150:
        dpi = 300

    try:
        selected_units = parse_page_spec(args.page_range)
        image_units = parse_page_spec(args.image_pages)
    except ValueError as exc:
        raise ProcessingError(str(exc)) from exc

    return PackOptions(
        source_path=source_path,
        output_dir=output_dir,
        work_dir=output_dir / ".work",
        selected_units=selected_units,
        image_units=image_units,
        image_format=args.image_format,
        dpi=dpi,
        ocr_engine=args.ocr_engine,
        analysis_goal=args.goal.strip(),
        preview_rows=max(1, args.preview_rows),
        allow_pdf_fallback=not args.disable_pdf_fallback,
    )


def build_manifest(options: PackOptions, result: PackResult) -> dict:
    return {
        "schema_version": "0.1",
        "created_at": result.created_at,
        "source": {
            "path": str(options.source_path),
            "name": options.source_path.name,
            "sha256": sha256_file(options.source_path),
            "document_type": result.document_type,
            "selected_units": result.selected_units,
        },
        "processing": {
            "backend": result.backend,
            "ocr_engine": options.ocr_engine,
            "filters": result.filters_applied,
            "needs_review_units": result.needs_review_units,
            "warnings": result.warnings,
            "metadata": result.metadata,
        },
        "artifacts": {
            "content": "content.md",
            "prompt": "prompt.md",
            "images": [artifact.to_manifest(options.output_dir) for artifact in result.images],
            "tables": [artifact.to_manifest(options.output_dir) for artifact in result.tables],
            "notebooklm": {
                "upload": "notebooklm_upload.txt",
                "handoff": "notebooklm_handoff.md",
                "expected_returns": [
                    "notebooklm_briefing.md",
                    "notebooklm_findings.md",
                    "notebooklm_link.txt",
                ],
            },
        },
    }


def write_pack(options: PackOptions, result: PackResult) -> None:
    manifest = build_manifest(options, result)
    prompt_text = render_prompt(options, result, manifest)
    notebooklm_upload_text = render_notebooklm_upload_text(result)
    notebooklm_handoff_text = render_notebooklm_handoff(options, result, manifest)

    (options.output_dir / "content.md").write_text(result.content_markdown.strip() + "\n", encoding="utf-8")
    (options.output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (options.output_dir / "prompt.md").write_text(prompt_text, encoding="utf-8")
    (options.output_dir / "notebooklm_upload.txt").write_text(notebooklm_upload_text, encoding="utf-8")
    (options.output_dir / "notebooklm_handoff.md").write_text(notebooklm_handoff_text, encoding="utf-8")


def print_summary(options: PackOptions, result: PackResult) -> None:
    print(f"Pack created: {options.output_dir}")
    print(f"Backend: {result.backend}")
    print(f"Content: {options.output_dir / 'content.md'}")
    if result.images:
        print(f"Images: {len(result.images)}")
    if result.tables:
        print(f"Tables: {len(result.tables)}")
    if result.needs_review_units:
        print(f"Needs review: {result.needs_review_units}")
    if result.warnings:
        print("Warnings:")
        for warning in result.warnings:
            print(f"- {warning}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        options = build_options(args)
        adapter = resolve_adapter(options.source_path, allow_pdf_fallback=options.allow_pdf_fallback)
        result = adapter(options)
        write_pack(options, result)
        print_summary(options, result)
        return 0
    except (MissingDependencyError, ProcessingError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
