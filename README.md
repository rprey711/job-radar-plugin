# Job Radar Plugin

Marketplace und Plugin `job-radar` für Cowork und Claude Code. Das Plugin gehört zu [Job Radar v2](https://github.com/rprey711/job-radar); Abläufe und Lernseiten kommen vom Server, hier liegen Slash-Befehle, Render-Skripte und Vorlagen.

Stand: im Bau (Plan 4). Installation und Entwicklung: siehe unten, wird mit Task 12 vervollständigt.

## Entwicklung

```bash
uv sync
uv run ruff check . && uv run ruff format --check .
uv run pytest
```
