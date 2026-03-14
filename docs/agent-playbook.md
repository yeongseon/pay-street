# Agent Playbook

## Source Of Truth
- `PRD.md` for product scope and content pipeline goals.
- `ARCH.md` for system architecture and component boundaries.
- `LOCAL_SETUP.md` for the required local-first execution model.
- `pyproject.toml` and `frontend/package.json` for runnable commands.

## Repository Map
- `paystreet/` backend application, workers, and providers.
- `frontend/` admin UI.
- `tests/` backend test coverage.
- Docker files and compose files define local service orchestration.

## Change Workflow
1. Decide whether the change affects backend APIs, worker pipelines, providers, or frontend views.
2. Keep `.venv`-based commands and local service assumptions consistent with `LOCAL_SETUP.md`.
3. Update docs when provider choices, runtime topology, or API surface changes.
4. Because unrelated edits already exist in this repo, stage only the new agent-doc files.

## Validation
- `python -m pip install -e ".[dev]"`
- `python -m pytest`
- `python -m uvicorn paystreet.app.main:app --reload`
- `cd frontend && npm install && npm run build`
