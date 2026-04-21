When the user asks to preprocess a document for LLM analysis from this repository, run:

```bash
./.venv/bin/python tools/doc_pack/pack.py "$ARGUMENTS"
```

After the command succeeds:

1. Read `manifest.json`.
2. Read `content.md`.
3. Inspect only the images or tables referenced in the manifest when the question requires them.

Example:

```bash
/doc-pack "/Users/zengtao/Doc/solar/Zeng - S01464.pdf" --goal "Summarize the structure, extract key findings, and flag any pages that need image review."
```
