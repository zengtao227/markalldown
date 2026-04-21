from __future__ import annotations

from docpack.models import PackOptions, PackResult

from .office_markitdown import build_pdf_fallback_pack


def build_pack(options: PackOptions) -> PackResult:
    return build_pdf_fallback_pack(options)
