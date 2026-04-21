# Analysis Task

**Document**: `{source_name}`
**Backend**: `{backend}`
**Selected units**: `{selected_units}`

## Workflow Rules

- Stay local unless a NotebookLM upgrade trigger applies.
- Upgrade triggers include: `4+` related documents, repeated research loops against the same source set,
  comparison or contradiction tasks, briefing/study-guide synthesis, or theme extraction across sources.
- When NotebookLM is active, upload the original supported sources there first. This pack remains the local
  control, review, and final-delivery layer.

## Read Order

1. Read `manifest.json` and `{content_path}` first.
2. If you are using the combined workflow, read `{notebooklm_handoff_path}` and any returned `notebooklm_*.md` files next.
3. Inspect the referenced images only when they are relevant.
4. Inspect referenced tables only when the answer depends on row-level or numeric evidence.

## Available Artifacts

### Images
{image_lines}

### Tables
{table_lines}

## Quality Notes

- Needs review units: `{review_units}`
{warning_lines}

## Goal

{goal}

## If NotebookLM Was Used

- Treat NotebookLM output as source-grounded research input, not as the final deliverable by itself.
- Separate what came from NotebookLM from what you verified locally in this pack.
- If NotebookLM or the local pack does not support a claim with evidence, say `uncertain`.

## Output Structure

## Findings From Sources

## Analysis Steps

## Conclusion

## Gaps Not Covered By Sources

## Answer Constraints

- Cite the relevant page, slide, or table when making a factual claim.
- If evidence is insufficient, say `uncertain` and point to the missing artifact.
- Do not infer details that are not present in the generated pack.
