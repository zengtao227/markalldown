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
4. NotebookLM integration defaults to a file-based handoff workflow. An MCP adapter is also available:
   `pip install notebooklm-mcp-cli` exposes tools including `notebook_query`, `source_add`, and
   `notebook_create`. Register the notebook URL in `notebooklm_link.txt` to link a specific notebook.
   - Keep `notebooklm-mcp-cli` disabled by default in Claude Code settings. Activate it selectively
     only when running `doc-research` tasks to avoid spending context on 35 idle tool definitions.
   - Generative tasks (`studio_create`, `research_start`) are async: call → receive `requestId` →
     poll status every 30–60 s → fetch result. Do not block the conversation thread waiting inline.
   - When a corpus is split across multiple sub-notebooks, use `cross_notebook_query` for aggregation.
     `notebooklm_link.txt` supports one URL per line (lines starting with `#` are comments).
   - Quote verification (when MCP is active): use `source_get_content` to confirm exact quotes
     before citing them in final output. Write `[Quote Not Found]` for any unverifiable quote.
   - Multi-notebook routing: use `notebook_describe` on each sub-notebook to understand its scope
     before routing targeted queries; use `cross_notebook_query` for cross-notebook synthesis.
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
