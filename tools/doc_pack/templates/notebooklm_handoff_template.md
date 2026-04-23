# NotebookLM Handoff

**Source**: `{source_name}`
**Path**: `{source_path}`
**Backend**: `{backend}`
**Selected units**: `{selected_units}`
**Gateway mode**: `{gateway_mode}`
**Recommended notebook title**: `{notebook_title}`

## Research Theme

{research_theme}

## Current Connection Rule

- This repository does not use an official NotebookLM API today.
- Use this file as the handoff packet for the human operator or a future gateway adapter.
- The current stable path is: upload sources in the NotebookLM UI, ask the prepared prompts, then save the
  results back into this pack.

## Notebook Link (Connection Bridge)

`notebooklm_link.txt` is the persistent connection between this pack and a specific NotebookLM notebook.
Claude reads this file to know which notebook to query in the combined workflow.

To register a notebook URL:

- **At pack creation time**: pass `--notebook-url <url>` to `pack.py` — the file is written automatically.
- **After the fact**: manually save the URL:
  `echo "https://notebooklm.google.com/notebook/<id>" > notebooklm_link.txt`

If `notebooklm_link.txt` already exists in this pack, Claude will use that notebook without prompting you
to create a new one.

For split corpora (multiple sub-notebooks), list one URL per line — lines starting with `#` are comments.
Claude will use `cross_notebook_query` automatically when multiple IDs are present.

## What To Upload To NotebookLM

{notebooklm_sources}

## Opening Prompt To Paste Into NotebookLM

```text
{opening_prompt}
```

## Follow-up Prompts

{follow_up_prompts}

## Keep Local For Claude/Codex

### Images
{image_lines}

### Tables
{table_lines}

## Quality Warnings

{warning_lines}

## Return Files

After using NotebookLM, copy or export the results back into this same pack directory as:

- `notebooklm_briefing.md`
- `notebooklm_findings.md`
- `notebooklm_link.txt` (optional shared notebook URL)

## Final Goal

{goal}
