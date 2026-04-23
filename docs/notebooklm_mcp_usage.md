# NotebookLM MCP Usage

## 1. Goal

The recommended operating model is:

- install NotebookLM once for `Claude` and `Codex`
- keep the MCP server available globally
- activate NotebookLM only in projects that actually need it
- tell the project which notebook to use with `notebooklm_link.txt`

This avoids forcing NotebookLM into unrelated work while still making it available as a reusable research
source.

## 2. One-Time Install

Install the package and authenticate the local profile:

```bash
pip install notebooklm-mcp-cli
nlm login
```

`nlm login` opens Chrome, reads the current authenticated NotebookLM session, and stores a local profile.

## 3. Claude Code Setup

### Recommended command

```bash
claude mcp add -s user notebooklm "$(which notebooklm-mcp)"
```

Why `-s user` matters:

- `local` scope only affects the current project
- `user` scope makes NotebookLM available in all future Claude projects and sessions

### Verify the setup

Run:

```bash
claude mcp get notebooklm
```

Expected result:

- `Scope: User config`
- `Status: Connected`

If you already added a project-local NotebookLM server earlier, remove it and re-add it at user scope:

```bash
claude mcp remove notebooklm -s local
claude mcp add -s user notebooklm "$(which notebooklm-mcp)"
```

## 4. Codex Setup

Run:

```bash
codex mcp add notebooklm -- "$(which notebooklm-mcp)"
```

Verify:

```bash
codex mcp get notebooklm
```

Expected result: `enabled: true` and `transport: stdio`.

## 5. Project Activation

NotebookLM should not run on every project by default.

Activate it only when one of these is true:

- you explicitly ask to use NotebookLM
- you provide a NotebookLM URL or notebook ID in the task
- the current project already contains a relevant `notebooklm_link.txt`

Recommended locations:

- project root: `notebooklm_link.txt`
- pack-specific location: `*_llm_pack/notebooklm_link.txt`

Example:

```bash
echo "https://notebooklm.google.com/notebook/<id>" > notebooklm_link.txt
```

Or register the notebook during pack creation:

```bash
./.venv/bin/python tools/doc_pack/pack.py "/path/to/source.pdf" \
  --goal "State the analysis task." \
  --notebook-url "https://notebooklm.google.com/notebook/<id>"
```

If a project uses multiple notebooks, put one URL per line. Lines starting with `#` are comments.

## 6. How Claude Should Use NotebookLM

When Claude sees a relevant notebook link or explicit NotebookLM instruction, the normal flow is:

1. read the local pack first: `manifest.json`, `content.md`, `prompt.md`
2. resolve the notebook from `notebooklm_link.txt` or the user message
3. use `notebook_describe` first when notebook scope is unclear or when multiple notebooks are linked
4. use `notebook_query` for comparison, synthesis, contradiction checks, recurring corpus questions, or
   broad research
5. use `source_get_content` to verify exact quotes, numbers, and contract terms when precision matters
6. use `cross_notebook_query` when the corpus is intentionally split across multiple notebooks
7. if the result materially affected the work, preserve a local audit trail in the pack
8. finish the answer in Claude, clearly separating:
   - what came from local artifacts
   - what came from NotebookLM
   - what remains unverified

Claude should stay local when the task is page-accurate extraction, exact spreadsheet reasoning, or a
sensitive workflow that should not leave the machine.

## 7. Example Claude Requests

Examples that should activate NotebookLM:

- `Use the notebook linked in notebooklm_link.txt and compare these proposals.`
- `Use this notebook https://notebooklm.google.com/notebook/<id> and tell me the contradictions.`
- `Before answering, query NotebookLM for prior findings on this project.`

Examples that should stay local:

- `Check page 9 of this contract and quote the exact clause.`
- `Audit these spreadsheet rows and compute the exact totals.`

## 8. What To Save Back Into The Pack

When NotebookLM materially influenced the work, it is still useful to preserve a local audit trail in the
pack:

- `notebooklm_link.txt`
- `notebooklm_briefing.md`
- `notebooklm_findings.md`

This keeps later Claude/Codex sessions reproducible even if they do not re-query NotebookLM immediately.
