When the user asks to preprocess a document for LLM analysis, run:

```bash
python3 tools/doc_pack/pack.py "$ARGUMENTS"
```

After the command succeeds:

1. Read `manifest.json`.
2. Read `content.md`.
3. Inspect only the images or tables referenced in the manifest when the question requires them.
