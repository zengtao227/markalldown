# markalldown Agent Workflow

## Default Rule

Stay local by default.

Use only `markalldown -> Claude/Codex` when the task is a single-document extraction, a deterministic
review, a sensitive local-only workflow, or exact spreadsheet reasoning.

## Upgrade To NotebookLM

Upgrade to the combined workflow when any of these are true:

- there are many related sources or a clearly large corpus
- the user wants comparison, contradiction checking, synthesis, briefing, or theme extraction
- the same source set will be queried repeatedly
- the task is more about reading a corpus than extracting one exact answer from one file

## Standard Flow

1. Run `tools/doc_pack/pack.py` to create a `*_llm_pack/` directory.
2. Read `manifest.json`, `content.md`, and `prompt.md`.
3. If the NotebookLM stage is needed, read `notebooklm_handoff.md`.
4. NotebookLM integration in this repository is currently a handoff workflow. There is no official
   NotebookLM API wired into this repo today.
5. When NotebookLM is active, upload original supported sources there first. Treat `notebooklm_upload.txt`
   as a supplement or fallback, not the default source.
6. After the NotebookLM stage, look for these optional return files in the same pack directory:
   - `notebooklm_briefing.md`
   - `notebooklm_findings.md`
   - `notebooklm_link.txt`
7. Final analysis should distinguish:
   - what came from local pack artifacts
   - what came from NotebookLM
   - what remains unverified

## NotebookLM Disciplines

- NotebookLM is a read-only research desk, not the system of record for hidden agent state.
- Conclusions from NotebookLM should stay source-grounded.
- Final delivery still belongs to Claude/Codex using local artifacts plus NotebookLM return files.
