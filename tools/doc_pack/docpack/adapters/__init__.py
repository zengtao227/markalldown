from __future__ import annotations

from pathlib import Path
from typing import Callable

from docpack.models import PackOptions, PackResult

from .excel_smart import build_pack as build_excel_pack
from .office_markitdown import build_pack as build_office_pack
from .pdf_pymupdf import build_pack as build_pdf_pack
from .pptx_smart import build_pack as build_pptx_pack

Adapter = Callable[[PackOptions], PackResult]


def resolve_adapter(source_path: Path, allow_pdf_fallback: bool = True) -> Adapter:
    suffix = source_path.suffix.lower()

    if suffix == ".pdf":
        return build_pdf_pack
    if suffix in {".xlsx", ".xlsm", ".xltx", ".xltm"}:
        return build_excel_pack
    if suffix in {".pptx", ".pptm"}:
        return build_pptx_pack
    return build_office_pack
