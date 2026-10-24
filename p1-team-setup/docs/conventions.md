# Team Coding Conventions

1. **Naming:** `snake_case` for functions and variables, `PascalCase` for classes, `UPPER_CASE` for constants.
2. **Type hints:** Annotate all function parameters and return types.
3. **Docstrings:** Every public function and class gets a one-line docstring in the imperative mood.
4. **Error handling:** Raise specific exceptions (`ValueError`, `KeyError`) with a clear message; never use bare `except`.
5. **Test naming:** Name tests `test_<unit>_<behaviour>`, e.g. `test_cancel_order_unknown_id_raises_key_error`.
