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

4. If they do not exist, use `notebooklm_handoff.md` as the source-of-truth for the current NotebookLM stage.
   Tell the user:
   - which original source files should be uploaded to NotebookLM directly
   - whether `notebooklm_upload.txt` is only a supplement or a required fallback
   - what opening prompt and follow-up prompts should be pasted into NotebookLM
   Then ask them to copy the resulting NotebookLM outputs back into the same pack directory using:
   - `notebooklm_briefing.md`
   - `notebooklm_findings.md`
   - `notebooklm_link.txt` (optional)

5. Once those files exist, continue the final analysis grounded in:
   - local pack artifacts first
   - NotebookLM return files second

6. Be explicit about:
   - which conclusions came directly from local artifacts
   - which conclusions came from NotebookLM
   - which points remain uncertain or still need local verification
