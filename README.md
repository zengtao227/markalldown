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

Run:

```bash
python3 tools/doc_pack/pack.py /path/to/file.pdf --goal "Summarize message flow and call out contradictions."
```
