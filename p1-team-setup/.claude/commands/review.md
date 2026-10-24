---
description: Review one file against the team checklist
argument-hint: [file path]
allowed-tools: Read, Grep
---
Review $ARGUMENTS against this checklist. Report only real problems.

1. Every function has type hints.
2. Errors are raised with a clear message, never silently ignored.
3. Names follow docs/conventions.md.

For each problem give: line number, rule number, one-sentence fix.
If there are no problems, say "No issues found".
