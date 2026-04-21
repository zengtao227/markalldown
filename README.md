# markalldown

`markalldown` is a document pre-processing project for Codex, Claude, and other LLM agents.

Instead of feeding raw PDF or Office files directly into a model, it builds a normalized `*_llm_pack/`
directory with:

- `content.md` for cleaned text
- `images/` for key pages or low-text slides
- `tables/` for extracted CSV artifacts
- `manifest.json` for processing metadata
- `prompt.md` for agent-ready analysis instructions

Current design:

- `PDF` -> `PyMuPDF + PyMuPDF4LLM`
- `DOCX / HTML / CSV / ZIP / generic Office` -> `MarkItDown`
- `XLSX` -> smart CSV-oriented adapter
- `PPTX` -> text extraction plus optional slide images
- `NotebookLM` -> optional source-grounded research stage after local pack creation

Run:

```bash
./.venv/bin/python tools/doc_pack/pack.py /path/to/file.pdf --goal "Summarize message flow and call out contradictions."
```

Setup:

```bash
python3 -m venv .venv
./.venv/bin/pip install -r tools/doc_pack/requirements.txt
```

Claude Code:

```bash
/doc-pack "/path/to/file.pdf" --goal "Summarize the document and flag anything uncertain."
```

Combined workflow:

```bash
/doc-research "/path/to/file.pdf" --goal "Create a grounded briefing, then return the final answer for execution."
```

After each pack run, `markalldown` also generates:

- `notebooklm_upload.txt`
- `notebooklm_handoff.md`

Use those files to bridge the local pack into NotebookLM, then copy NotebookLM outputs back as:

- `notebooklm_briefing.md`
- `notebooklm_findings.md`
- `notebooklm_link.txt`
