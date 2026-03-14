# AGENTS.md

## Purpose
`pay-street` is a local-first salary-content pipeline with a Python backend and a frontend admin app.

## Read First
- `PRD.md`
- `ARCH.md`
- `LOCAL_SETUP.md`
- `docs/agent-playbook.md`

## Working Rules
- Preserve the local-first, vendor-neutral architecture unless the task explicitly changes strategy.
- Keep backend contracts, worker behavior, and frontend admin flows synchronized when shared APIs change.
- Treat `.venv` execution and containerized local services as the default development model.
- In this repo's dirty worktree, stage only the files you intentionally changed.

## Validation
- `python -m pytest`
- `python -m uvicorn paystreet.app.main:app --reload`
- `cd frontend && npm run build`
