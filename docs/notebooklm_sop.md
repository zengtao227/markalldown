# markalldown + NotebookLM + Claude/Codex SOP

## 1. Core Model

This workflow has three layers:

1. `markalldown` is the local control plane.
   It creates a reproducible `*_llm_pack/`, records what was processed, and preserves local evidence for
   exact review.
2. `NotebookLM` is the source-grounded research plane.
   It is where large, supported source sets are explored, compared, and summarized.
3. `Claude` or `Codex` is the final execution plane.
   The agent uses the local pack plus any NotebookLM return artifacts to produce the final answer or work
   product.

The important boundary is this:

- `markalldown` reduces local input noise and preserves deterministic artifacts.
- `NotebookLM` reduces repeated research-token waste across many supported sources.

## 2. Stay Local By Default

Use only `markalldown -> Claude/Codex` when:

- the task is a single-document extraction, review, or implementation task
- the answer must stay deterministic and page-accurate
- the document is too sensitive to upload to NotebookLM
- the work depends on exact spreadsheet rows, formulas, or cell-level reasoning
- the user wants direct local processing only

Typical examples:

- `Summarize the key clauses in this one contract.`
- `Check pages 8-12 for contradictions.`
- `Find anomalies in this CSV/XLSX and show the exact rows.`

## 3. Upgrade To NotebookLM

Upgrade to the combined workflow when any of these are true:

- there are `4+` related documents or a clearly large source set
- you expect `3+` rounds of questions against the same source set
- the task is about `comparison`, `briefing`, `theme extraction`, `consensus`, `contradictions`, or
  `research gaps`
- the main work is reading and cross-referencing a corpus, not extracting one exact answer from one file
- the notebook should become a reusable research surface for the same project or topic

Typical examples:

- `Compare 12 proposals and tell me the main differences and hidden conflicts.`
- `Create a briefing across these reports and list unresolved questions.`
- `Read this literature set and identify consensus, disagreement, and next steps.`

## 4. Source Policy

When NotebookLM is active, the default rule is:

- upload original supported sources directly into NotebookLM
- keep the local pack as the control plane and final verification layer

This is the preferred behavior because NotebookLM already supports many source types directly on desktop,
including `docx`, `md`, `txt`, `pdf`, `csv`, `pptx`, `images`, `audio`, `web URLs`, and `epub`.

Use local pack outputs such as `notebooklm_upload.txt` only when:

- the original local format is not a preferred NotebookLM upload type
- you need a cleaned or stripped text-only fallback
- you want to supplement the original source with a normalized text view

Keep these tasks local even in the combined workflow:

- exact row-level spreadsheet reasoning
- page-perfect image review
- final implementation decisions that require deterministic local evidence

## 5. Current Connection Model

There is no official NotebookLM API wired into this repository today.

That means Claude/Codex do not directly call NotebookLM as a tool in the current implementation. The
current stable connection is a `handoff packet`:

- `notebooklm_handoff.md` carries the notebook title, research theme, upload strategy, opening prompt, and
  follow-up prompts
- the user, or a future automation layer, performs the NotebookLM UI actions
- NotebookLM outputs are copied back into the local pack for Claude/Codex to consume

Current connection modes:

1. `Manual gateway`:
   The user opens NotebookLM, uploads sources, pastes the prepared prompts, and saves the results back.
2. `Shared notebook`:
   The user keeps a project notebook in NotebookLM and shares or reuses it across research sessions.
   Claude/Codex still consume the notebook indirectly through exported notes, copied answers, or shared
   links.
3. `Browser automation`:
   Possible in the future, but experimental and not part of the core workflow.
4. `Official API / MCP adapter`:
   Preferred future state if Google exposes a stable API.

## 6. Standard Operating Procedure

### Step 1. Create the local control pack

Run:

```bash
./.venv/bin/python tools/doc_pack/pack.py "/path/to/source.pdf" --goal "State the actual analysis task."
```

This creates a local `*_llm_pack/` with:

- `content.md`
- `manifest.json`
- `prompt.md`
- `images/`
- `tables/`
- `notebooklm_upload.txt`
- `notebooklm_handoff.md`

This step does not mean NotebookLM must consume the cleaned markdown. It creates the local audit trail and
the handoff packet.

### Step 2. If NotebookLM is needed, upload original supported sources directly

Preferred NotebookLM inputs:

- the original local source file when its type is supported
- web URLs when the source is already on the web
- Google-native sources when the work already lives in Drive

Use `notebooklm_upload.txt` only as a supplement or fallback.

Examples:

- `PDF`, `DOCX`, `MD`, `TXT`, `CSV`, `PPTX`, `image`, `audio`, and `ePub`:
  upload the original file to NotebookLM first
- `XLSX`:
  keep exact work local; if needed in NotebookLM, export relevant sheets to `CSV` or move them to Google
  Sheets first
- noisy OCR or heavily boilerplate-stripped content:
  the original file can still go to NotebookLM, but `notebooklm_upload.txt` may be added as a fallback view

### Step 3. Use the handoff packet to carry the research theme

`notebooklm_handoff.md` is the current interface between the local agent workflow and NotebookLM.

It should tell the NotebookLM operator:

- what notebook to create or reuse
- what sources to upload
- what the research theme is
- what opening prompt to ask first
- what follow-up prompts to ask next
- what files should be copied back into the pack

### Step 4. Run the NotebookLM research stage

Inside NotebookLM:

1. create or open the notebook
2. upload the original supported sources
3. paste the opening prompt from `notebooklm_handoff.md`
4. ask the follow-up prompts
5. save or export the resulting notes, findings, or link

### Step 5. Save NotebookLM outputs back into the pack

Copy results back into the same `*_llm_pack/` using:

- `notebooklm_briefing.md`
- `notebooklm_findings.md`
- `notebooklm_link.txt`

This keeps the workflow reproducible for both Claude and Codex.

### Step 6. Final Claude/Codex stage

Final analysis or execution should read in this order:

1. `manifest.json`
2. `content.md`
3. `prompt.md`
4. `notebooklm_handoff.md` when NotebookLM was part of the workflow
5. `notebooklm_briefing.md` if present
6. `notebooklm_findings.md` if present
7. referenced `images/` or `tables/` only when needed

The final prompt should be explicit about:

- the remaining question
- whether NotebookLM was used
- which conclusions came from NotebookLM
- which points still require local verification

## 7. Three Disciplines

These rules are mandatory when NotebookLM is used:

1. `NotebookLM is a read-only research desk.`
   Do not treat it as the system of record for agent state or hidden reasoning.
2. `Conclusions must stay grounded in sources.`
   If a result has no citation or no clear source support, treat it as unverified.
3. `Final delivery belongs to Claude/Codex.`
   NotebookLM helps read and synthesize sources; the local agent still produces the final answer or action.

## 8. Mode Boundaries

Two working modes are allowed:

- `Ephemeral research mode`:
  One pack, one notebook, one question set. This is the default for `markalldown`.
- `Persistent knowledge base mode`:
  A long-lived notebook reused across many sessions. This is allowed operationally, but it is not the core
  responsibility of `markalldown` itself.

## 9. Future Adapter Boundary

If Google later provides a stable NotebookLM or Gemini notebooks API, replace the manual gateway with a
real adapter without changing the high-level workflow:

- the local pack remains the control plane
- NotebookLM remains the research plane
- the gateway changes from `manual` to `API` or `MCP`
