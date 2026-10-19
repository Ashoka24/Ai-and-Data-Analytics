# Repository structure

Projects are kept in descriptively named folders at the repository root so that the portfolio is easy to browse without opening a generic numbered-project directory.

## Project folder conventions

Each project should include, where relevant:

- `README.md` — the question, data provenance, methods, run instructions, outputs and limitations.
- `data/` — small, licensed sample data or instructions for obtaining larger datasets.
- `scripts/` — repeatable analysis code.
- `sql/` — queries used in the analysis.
- `tests/` — checks for input validation and key calculations.
- `figures/` — workflow diagrams or figures used in the README.
- `docs/` — project-specific technical notes.

Repository-wide documentation belongs in this folder, and automation belongs in `.github/workflows/`. Keep generated outputs, local environments, secrets and restricted datasets out of version control.

## Adding a project

Create a descriptively named folder at the root, document data provenance and limitations, include a reproducible run path, add focused tests, and update the project table in the root README. Do not report model metrics or results until they have been generated and checked.
