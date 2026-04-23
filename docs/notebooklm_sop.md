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

### Source Size Warning

Two independent thresholds can degrade NotebookLM retrieval quality:

1. **Word count**: when a single document exceeds ~200,000 words, the vector index begins to flatten
   and the model may fill gaps with training data rather than source text.
   `pack.py` warns automatically when this is crossed.

2. **Source file count**: when a notebook accumulates more than ~30 sources (regardless of word count),
   per-source retrieval density drops. Free plan hard-caps at 50 sources; Pro at 300.
   Recommended ceiling for reliable retrieval: **20–30 sources per notebook**.

Mitigation for both: split large corpora into thematic sub-notebooks. Use `cross_notebook_query`
(available in `notebooklm-mcp-cli`) to aggregate results across split notebooks.

When a corpus is split, record all notebook URLs in `notebooklm_link.txt` — one URL per line,
lines starting with `#` are treated as comments.

## 5. Current Connection Model

There is still no first-party NotebookLM API embedded inside `markalldown` itself.

However, direct automation is available today through `notebooklm-mcp-cli`, which provides both an MCP
server and the `nlm` CLI. The recommended operating model is:

- install NotebookLM MCP once for `Claude` and `Codex`
- keep it available globally
- activate it only for projects that actually need NotebookLM
- route each project to its own notebook with `notebooklm_link.txt`

The stable connection surface is now:

- `notebooklm_handoff.md` carries the notebook title, research theme, upload strategy, opening prompt, and
  follow-up prompts
- `notebooklm_link.txt` is the project-specific connection bridge — it stores the notebook URL so
  Claude/Codex know which notebook to query. Register it by passing `--notebook-url <url>` to `pack.py`,
  or save the URL manually after creating the notebook.
- when direct MCP is available, Claude/Codex can query NotebookLM themselves
- when direct MCP is unavailable, the same pack still supports a manual NotebookLM handoff

Recommended connection modes:

1. `Project-scoped direct MCP`:
   Claude/Codex have NotebookLM installed globally, but they use it only when the user explicitly asks,
   provides a notebook URL or ID, or the current project contains a relevant `notebooklm_link.txt`.
2. `Shared notebook`:
   The user keeps a project notebook in NotebookLM and reuses it across research sessions. The project
   points to that notebook through `notebooklm_link.txt`.
3. `Manual gateway fallback`:
   The user opens NotebookLM, uploads sources, pastes prepared prompts, and saves results back into the
   pack when MCP is not available.
4. `Official API`:
   Preferred long-term state if Google exposes a first-party stable API with auth guarantees.

Key MCP usage patterns:

- `notebook_describe`: returns an AI-generated summary of a notebook's content and keywords — use this to
  understand each sub-notebook's scope before routing queries in a split corpus.
- `source_get_content`: returns raw source text — use this to verify exact quotes before citing them in
  final output. Write `[Quote Not Found]` if the verbatim match cannot be located.
- `cross_notebook_query`: aggregates results across multiple sub-notebooks.

Detailed setup and user-facing workflow live in `docs/notebooklm_mcp_usage.md`.

## 6. Claude And Codex Setup

### Step 1. Install and authenticate once

Run:

```bash
pip install notebooklm-mcp-cli
nlm login
```

This authenticates the local `nlm` profile against the Google account that can access the target
NotebookLM notebooks.

### Step 2. Register NotebookLM MCP in Claude Code

Recommended Claude command:

```bash
claude mcp add -s user notebooklm "$(which notebooklm-mcp)"
```

Verification:

```bash
claude mcp get notebooklm
```

Expected outcome: `Scope: User config` and `Status: Connected`.

### Step 3. Register NotebookLM MCP in Codex

Recommended Codex command:

```bash
codex mcp add notebooklm -- "$(which notebooklm-mcp)"
```

Verification:

```bash
codex mcp get notebooklm
```

Expected outcome: the `notebooklm` server is listed as enabled with `transport: stdio`.

### Step 4. Activate NotebookLM only in relevant projects

Preferred triggers:

- the user explicitly asks to use NotebookLM
- the user provides a notebook URL or notebook ID
- the project root contains `notebooklm_link.txt`
- the relevant `*_llm_pack/` directory contains `notebooklm_link.txt`

Recommended link registration:

```bash
echo "https://notebooklm.google.com/notebook/<id>" > notebooklm_link.txt
```

Or at pack creation time:

```bash
./.venv/bin/python tools/doc_pack/pack.py "/path/to/source.pdf" \
  --goal "State the analysis task." \
  --notebook-url "https://notebooklm.google.com/notebook/<id>"
```

When multiple notebooks are needed, put one URL per line in `notebooklm_link.txt`. Lines starting with
`#` are comments.

## 7. Standard Operating Procedure

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

Preferred direct mode:

1. resolve the notebook from `notebooklm_link.txt`, explicit user input, or the pack metadata
2. if there are multiple notebooks, call `notebook_describe` first to understand scope
3. query the notebook directly from Claude/Codex
4. use `source_get_content` to verify exact quotes, numbers, and contract language when precision matters
5. if the corpus is split, use `cross_notebook_query` for synthesis

Fallback manual mode inside NotebookLM:

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

## 8. Three Disciplines

These rules are mandatory when NotebookLM is used:

1. `NotebookLM is a read-only research desk.`
   Do not treat it as the system of record for agent state or hidden reasoning.
2. `Conclusions must stay grounded in sources.`
   If a result has no citation or no clear source support, treat it as unverified.
3. `Final delivery belongs to Claude/Codex.`
   NotebookLM helps read and synthesize sources; the local agent still produces the final answer or action.

## 9. Mode Boundaries

Two working modes are allowed:

- `Ephemeral research mode`:
  One pack, one notebook, one question set. This is the default for `markalldown`.
- `Persistent knowledge base mode`:
  A long-lived notebook reused across many sessions. This is allowed operationally, but it is not the core
  responsibility of `markalldown` itself.

## 10. Future Adapter Boundary

If Google later provides a stable NotebookLM or Gemini notebooks API, replace the manual gateway with a
real adapter without changing the high-level workflow:

- the local pack remains the control plane
- NotebookLM remains the research plane
- the gateway changes from `manual` to `API` or `MCP`
