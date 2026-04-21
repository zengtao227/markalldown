When the user asks for the full `markalldown + NotebookLM + Claude` workflow, do this:

1. Run:

```bash
./.venv/bin/python tools/doc_pack/pack.py "$ARGUMENTS"
```

2. Read the generated:
   - `manifest.json`
   - `content.md`
   - `prompt.md`
   - `notebooklm_handoff.md`

3. If `notebooklm_briefing.md` or `notebooklm_findings.md` already exist in the same pack directory, use them.

4. If they do not exist, tell the user exactly which files from `notebooklm_handoff.md` should be uploaded to
   NotebookLM and ask them to copy the resulting NotebookLM outputs back into the same pack directory using:
   - `notebooklm_briefing.md`
   - `notebooklm_findings.md`
   - `notebooklm_link.txt` (optional)

5. Once those files exist, continue the final analysis grounded in:
   - local pack artifacts first
   - NotebookLM return files second

6. Be explicit about which conclusions came directly from local artifacts and which came from NotebookLM.
