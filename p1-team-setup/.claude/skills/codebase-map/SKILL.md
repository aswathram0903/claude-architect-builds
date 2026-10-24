---
name: codebase-map
description: Map an unfamiliar Python codebase. Use when the user asks what a codebase contains, where something lives, or how modules connect.
context: fork
allowed-tools: Read, Grep, Glob
---
Explore the codebase in the current folder.

Return ONLY this, under 15 lines:
- Modules: one line each, what it does
- Entry points: functions a caller would use first
- Tests: which modules have tests, which do not
- One risk you noticed, with the file name

Do not edit any file.
