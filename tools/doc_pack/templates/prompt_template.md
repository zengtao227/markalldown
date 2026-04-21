# Analysis Task

**Document**: `{source_name}`
**Backend**: `{backend}`
**Selected units**: `{selected_units}`

## Read Order

1. Read `{content_path}` first.
2. Inspect the referenced images only when they are relevant.
3. Inspect referenced tables only when the answer depends on row-level or numeric evidence.

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

## Answer Constraints

- Cite the relevant page, slide, or table when making a factual claim.
- If evidence is insufficient, say `uncertain` and point to the missing artifact.
- Do not infer details that are not present in the generated pack.
