# markalldown Agent Workflow

## Combined Workflow Rule

When a user asks for document research, document analysis, or multi-source synthesis, use the combined
`markalldown + NotebookLM + Claude/Codex` workflow unless the user explicitly says to stay local.

## Standard Flow

1. Run `tools/doc_pack/pack.py` to create a `*_llm_pack/` directory.
2. Read `manifest.json`, `content.md`, and `prompt.md`.
3. If the task is multi-document research, contradiction checking, theme extraction, or briefing creation,
   also read `notebooklm_handoff.md` and use the NotebookLM stage.
4. NotebookLM integration in this repository is file-based. There is no official NotebookLM API wired into
   this repo today.
5. After the NotebookLM stage, look for these optional return files in the same pack directory:
   - `notebooklm_briefing.md`
   - `notebooklm_findings.md`
   - `notebooklm_link.txt`
6. Final analysis should be grounded in local pack artifacts first, then NotebookLM return artifacts if
   they exist.

## Skip NotebookLM

Skip the NotebookLM stage when:

- the task is deterministic extraction from a single document
- the user only wants local processing
- the document is highly sensitive and should not leave the local workflow
- the answer depends on exact row-level spreadsheet details better handled from local CSV artifacts

## Use NotebookLM

Prefer NotebookLM when:

- there are many related documents
- the user wants a briefing or study-guide style synthesis
- the task depends on comparing claims across sources
- the source contains charts, diagrams, or complex visual references that benefit from source-grounded QA
