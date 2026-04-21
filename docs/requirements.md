# markalldown Requirements And Plan

## 1. Goal

Build a unified document pre-processing pipeline that turns PDF, DOCX, PPTX, XLSX, and related files
into a compact `*_llm_pack/` directory that is cheaper and more reliable for LLM analysis.

## 2. Primary Requirements

1. Do not send raw PDF or Office files directly to Codex or Claude by default.
2. Produce a normalized output bundle with cleaned markdown, selected images, structured metadata, and
   an agent-facing prompt.
3. Keep the backend replaceable so the caller is not coupled to `fitz` or any single converter.
4. Optimize for token reduction through filtering, not only file-format conversion.
5. Make the core pipeline a standalone Python CLI so multiple agent environments can reuse it.

## 3. Backend Strategy

### PDF

- Primary backend: `PyMuPDF + PyMuPDF4LLM`
- Responsibilities:
  - page-aware extraction
  - OCR-capable extraction path through `PyMuPDF4LLM`
  - page image export
  - quality checks and `needs_review` flags
- Constraint: treat this stack as a high-risk dependency for license review if the project moves beyond
  personal local workflows.

### Office / Generic Formats

- Default backend: `MarkItDown`
- Suitable for:
  - `docx`
  - `html`
  - `csv`
  - `tsv`
  - `xml`
  - `zip`
  - other formats already supported by MarkItDown

### XLSX

- Do not inline full spreadsheets as Markdown tables by default.
- Use a smart adapter that:
  - exports each sheet to CSV under `tables/`
  - includes only columns, preview rows, and numeric summaries in `content.md`

### PPTX

- Extract text slide by slide.
- Detect low-text slides and export images when possible.
- Prefer a lightweight implementation first; image export may depend on `LibreOffice` being available.

## 4. Output Structure

```text
<stem>_llm_pack/
  manifest.json
  content.md
  prompt.md
  images/
  tables/
```

### manifest.json

Must include:

- source file path
- source SHA256
- timestamp
- selected backend
- page or slide scope
- image artifacts
- table artifacts
- warnings
- `needs_review` page list

### prompt.md

Must be prefilled with:

- source summary
- extraction scope
- generated artifacts
- quality warnings
- the user-supplied analysis goal

## 5. Filtering Strategy

Token optimization should emphasize:

1. header and footer suppression
2. repeated line removal
3. boilerplate removal
4. paragraph reflow
5. table summarization instead of full inlining

## 6. Delivery Plan

### Phase 1

- CLI entrypoint
- unified manifest model
- PDF adapter
- Office adapter
- XLSX smart adapter
- PPTX smart adapter
- basic filters
- Claude command draft

### Phase 2

- richer OCR quality checks
- figure and chart detection
- MCP wrapper
- Codex skill wrapper
- regression tests with sample documents
