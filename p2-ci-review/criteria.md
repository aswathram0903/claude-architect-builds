# Review criteria (team standard)

Report ONLY these three kinds of problem:
1. bug: the code does something different from what its name, docstring or tests say.
2. error-handling: an error can be raised or swallowed in a way the caller cannot handle.
3. security: untrusted input reaches something dangerous.

Do NOT report: style, naming, formatting, missing docstrings, missing type hints, "consider" suggestions, or anything you are not sure is a real problem.

For every finding give: file, line, category, one sentence on what goes wrong, one sentence fix.
If nothing meets these criteria, return no findings. No findings is a good result.
