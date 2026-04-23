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

4. If they do not exist, check whether `notebooklm_link.txt` exists in the pack directory.
   - If it exists: a notebook is already registered. Tell the user which notebook URL is linked and
     skip asking them to create a new one. Proceed directly to the upload and prompting steps.
   - If it does not exist: the user will need to create a notebook. After they do, they can either:
     - Save the URL manually: `echo "<url>" > notebooklm_link.txt`
     - Or re-run `pack.py` with `--notebook-url <url>` to register it automatically.

5. Use `notebooklm_handoff.md` as the source-of-truth for the NotebookLM stage.
   Tell the user:
   - which original source files should be uploaded to NotebookLM directly
   - whether `notebooklm_upload.txt` is only a supplement or a required fallback
   - what opening prompt and follow-up prompts should be pasted into NotebookLM
   Then ask them to copy the resulting NotebookLM outputs back into the same pack directory using:
   - `notebooklm_briefing.md`
   - `notebooklm_findings.md`
   - `notebooklm_link.txt` (if not already present)

6. Once those files exist, continue the final analysis grounded in:
   - local pack artifacts first
   - NotebookLM return files second

7. Be explicit about:
   - which conclusions came directly from local artifacts
   - which conclusions came from NotebookLM
   - which points remain uncertain or still need local verification
