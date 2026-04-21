from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ProcessingError(RuntimeError):
    """Base error for document packing failures."""


class MissingDependencyError(ProcessingError):
    """Raised when an optional runtime dependency is required but unavailable."""


@dataclass(slots=True)
class ImageArtifact:
    path: Path
    unit: int
    kind: str = "page"
    width: int | None = None
    height: int | None = None
    note: str | None = None

    def to_manifest(self, output_dir: Path) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "path": str(self.path.relative_to(output_dir)),
            "unit": self.unit,
            "kind": self.kind,
        }
        if self.width is not None:
            payload["width"] = self.width
        if self.height is not None:
            payload["height"] = self.height
        if self.note:
            payload["note"] = self.note
        return payload


@dataclass(slots=True)
class TableArtifact:
    path: Path
    name: str
    rows: int
    columns: int
    note: str | None = None

    def to_manifest(self, output_dir: Path) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "path": str(self.path.relative_to(output_dir)),
            "name": self.name,
            "rows": self.rows,
            "columns": self.columns,
        }
        if self.note:
            payload["note"] = self.note
        return payload


@dataclass(slots=True)
class PackOptions:
    source_path: Path
    output_dir: Path
    work_dir: Path
    selected_units: list[int] | None = None
    image_units: list[int] | None = None
    image_format: str = "jpeg"
    dpi: int = 150
    ocr_engine: str = "auto"
    analysis_goal: str = ""
    preview_rows: int = 5
    allow_pdf_fallback: bool = True


@dataclass(slots=True)
class PackResult:
    backend: str
    document_type: str
    selected_units: list[int]
    content_markdown: str
    metadata: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    filters_applied: list[str] = field(default_factory=list)
    needs_review_units: list[int] = field(default_factory=list)
    images: list[ImageArtifact] = field(default_factory=list)
    tables: list[TableArtifact] = field(default_factory=list)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    )
