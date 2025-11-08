# Repository Guidelines

## Structure
- `src/countdown/` hosts the CLI (`__main__.py`, `timer.py`, `display.py`, `terminal.py`, `keys.py`, `glyphs.txt`); `tests/` mirrors each module.
- Tooling lives in `justfile`, `pyproject.toml`, and `noxfile.py`; see `CONTRIBUTING.rst` if you need the long-form tour.

## Workflow
- `just check` runs format + lint + pytest; treat it as the pre-push gate.
- `just test [-- -k expr]`, `just test-cov`, and `just test-all` cover targeted, coverage, and multi-Python runs.

## Style
- Use `just format` instead of manual tweaks; keep docstrings concise and only add type hints when they clarify intent.
