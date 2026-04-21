# markalldown + NotebookLM + Claude/Codex SOP

## 1. Purpose

This SOP defines a standard document workflow for research and analysis:

1. `markalldown` cleans and normalizes raw sources into a local `*_llm_pack/`.
2. `NotebookLM` handles multi-source exploration, briefings, and source-grounded synthesis.
3. `Claude` or `Codex` performs the final task using the local pack plus any NotebookLM return artifacts.

This design exists because NotebookLM is useful for source-grounded research, but it is not the same
thing as a local, automatable document pre-processor.

## 2. Decision Tree

### Local-only path

Use only `markalldown -> Claude/Codex` when:

- the task is a single-document extraction or review
- the user needs deterministic output
- the document is too sensitive for NotebookLM
- exact spreadsheet row handling matters more than research synthesis

### Combined path

Use `markalldown -> NotebookLM -> Claude/Codex` when:

- the task spans many documents
- the user wants a briefing, study guide, or thematic synthesis
- contradiction detection across sources matters
- charts, figures, or diagrams need source-grounded question answering

## 3. Standard Operating Procedure

### Step 1. Local intake with markalldown

Run:

```bash
./.venv/bin/python tools/doc_pack/pack.py "/path/to/source.pdf" --goal "State the actual analysis task."
```

This creates:

- `content.md`
- `manifest.json`
- `prompt.md`
- `images/`
- `tables/`
- `notebooklm_upload.txt`
- `notebooklm_handoff.md`

### Step 2. Decide what goes to NotebookLM

#### Send original source when NotebookLM supports it and visual grounding matters

- original `PDF`
- website URLs
- Google Docs / Google Slides if you already work in Google formats

#### Send markalldown output when the original format is noisy or unsupported

- `DOCX` -> upload `notebooklm_upload.txt`
- `XLSX` -> upload `notebooklm_upload.txt`; keep detailed CSV work local
- `PPTX` -> upload `notebooklm_upload.txt`; if the slides are visually important, also convert/export to PDF first
- OCR-cleaned or boilerplate-stripped material -> upload `notebooklm_upload.txt`

### Step 3. NotebookLM notebook scope

Use one notebook per project or question set.

Do not mix unrelated projects in one notebook. NotebookLM cannot reason across multiple notebooks at the
same time, so notebook boundaries should follow real project boundaries.

### Step 4. NotebookLM prompt sequence

Start with these prompts inside NotebookLM:

1. `Create a briefing document for this project. Keep it grounded in the sources and cite evidence.`
2. `List the main claims or findings by source, and highlight any contradictions or unresolved questions.`
3. `Identify charts, diagrams, or sections that still need direct human review.`
4. `Summarize what should be handed back to Claude/Codex for final execution.`

Use follow-up prompts like:

- `What is still uncertain?`
- `Which source sections matter most for implementation?`
- `Where do the sources disagree?`
- `What should be verified against the original pages before acting on this?`

### Step 5. Save NotebookLM outputs back into the pack

After the NotebookLM stage, copy results back into the same `*_llm_pack/` using these filenames:

- `notebooklm_briefing.md`
- `notebooklm_findings.md`
- `notebooklm_link.txt` for a public or shared notebook URL when relevant

This keeps the workflow file-based and makes it usable by both Claude and Codex.

### Step 6. Final Claude/Codex stage

Final analysis or execution should read in this order:

1. `manifest.json`
2. `content.md`
3. `prompt.md`
4. `notebooklm_briefing.md` if present
5. `notebooklm_findings.md` if present
6. referenced `images/` or `tables/` only when needed

The final prompt should clearly say:

- what question remains
- whether NotebookLM was used
- what exact output is needed
- what uncertainty threshold is acceptable

## 4. Tool-Specific Integration

### Claude Code

Claude Code should use repository commands:

- `/doc-pack` for local pack generation
- `/doc-research` for the combined workflow

NotebookLM itself is not directly automated here through an official API. Claude Code should treat
NotebookLM as a human-in-the-loop research stage and resume once return artifacts are available locally.

### Codex

Codex should follow `AGENTS.md` in this repository.

Codex integration is also file-based:

1. create or read the `*_llm_pack/`
2. use `notebooklm_handoff.md` when the NotebookLM stage is needed
3. continue only after `notebooklm_briefing.md` or `notebooklm_findings.md` are available

### Future path

If Google later provides a stable NotebookLM API or a supported automation path, replace the manual
handoff step with MCP or browser automation. Until then, keep NotebookLM as a bounded research stage,
not as a hidden dependency.

## 5. Current Product Constraints

- NotebookLM works per notebook and cannot access multiple notebooks simultaneously.
- Private and public notebook sharing exist, depending on account type and plan.
- Public sharing is currently restricted for some account types.
- NotebookLM is strong for source-grounded synthesis, but should not replace local structured artifacts.
