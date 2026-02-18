# Copilot Instructions for `dummy_project_ai`

## Repository snapshot (source of truth)
- The repository currently contains only `README.md` with the project title.
- There are no application source directories (`src/`, `app/`, etc.) yet.
- There are no detected build/test manifests (`package.json`, `pyproject.toml`, `Makefile`, `Dockerfile`, CI workflows).

## Architecture assumptions
- Treat this codebase as an initial bootstrap, not an existing implementation.
- Do not describe services, modules, or data flows as if they already exist.
- If asked to implement features, first infer or confirm the intended stack from user instructions, then scaffold only what is requested.

## Agent workflow in this repo
- Start every task by checking current files rather than assuming framework defaults.
- Before suggesting commands, verify matching config/manifests exist in the repo.
- Keep changes minimal and explicit because there is no established project structure yet.

## Project-specific conventions discovered
- `README.md` is currently the only documented project artifact; keep it aligned with major setup changes.
- Prefer introducing one clear structure at a time (for example, one language/runtime scaffold), instead of mixed multi-stack bootstrapping.
- When adding first-time tooling (lint/test/build), include runnable commands and required files in the same change.

## Integration and dependency guidance
- No external integrations are currently declared in-repo.
- Add dependencies only when directly required by the requested feature.
- For any new integration, document configuration location and local run steps in `README.md`.

## Definition of “done” for future agent changes
- New structure is discoverable from the repository tree.
- Commands referenced by the agent are executable from checked-in files.
- `README.md` reflects the actual setup introduced by the change.
- Update this file when repository architecture/workflows become concrete.
