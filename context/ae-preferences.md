# AE Preferences

These are AE-house defaults. All ds-* skills read this file and apply these preferences unless the project's `context/project.md` explicitly overrides them.

## Python
- Version: 3.13+
- Package manager: `uv` with workspace layout (`uv.lock`, `pyproject.toml` per package)
- Linting: `ruff` - rules E, F, I, B, UP, SIM; line-length 100; double quotes (`ruff format`)
- Type checking: `pyright` strict mode; `reportMissingTypeStubs = "none"` for untyped third-party libs
- API framework: FastAPI with Pydantic v2 schemas; `uvicorn` for serving

## Code structure
- `src/` layout with uv workspace packages
- Data directories follow Cookiecutter Data Science v2: `data/raw/`, `data/interim/`, `data/processed/`
- Notebooks in `notebooks/` for exploration only - production code lives in `src/`

## Azure stack
- LLM deployments: Azure AI Foundry (default); prompt flow for orchestration
- Classical/DL deployments: Azure ML Managed Endpoints (online) or Batch Endpoints
- Experiment tracking: MLflow (primary), W&B (alternative for research-heavy projects)
- IaC: Terraform with `azurerm` provider >= 4.26.0
  - AE naming: `<abbrev>-<client>-<project>-<region>-<env>` (e.g. `rg-ae-myproject-weu-dev`)
  - Managed Identity over connection strings - no SQL admin passwords in code
  - State backend: Azure Storage, one state file per environment
- CI/CD: Azure DevOps pipelines (`.azure-pipelines/`)
- Observability: Azure Monitor + Application Insights; OpenTelemetry instrumentation for APIs

## Data & ML
- Data versioning: DVC with Azure Blob Storage as remote
- Feature store: Azure ML Feature Store (managed) or Feast (open-source)
- Hyperparameter optimization: Optuna (default)

## Governance
- Responsible AI impact assessment (`/ds-fairness`) required before any production deployment
- Fairness report (`reports/responsible-ai-assessment-<date>.md`) must exist before `/ds-deploy` runs

## Skill state protocol

All ds-* skills follow this protocol.

### On start — read step (add to "Before you start")

- Read `context/skill-state.md` if it exists.
  - Check the **Run log** for which skills have already run and what they produced.
  - Check the **Artifact index** for file paths of existing outputs (don't re-derive paths from disk).
  - Check **Recommended next steps** — use it as orientation, not a mandate.

### On completion — write step (add as final step before "done")

Append a new row to the **Run log** table:

```
| <YYYY-MM-DD> | `/<skill-name>` | `<path1>`, `<path2>` | <one-line summary of what was done or flagged> |
```

Overwrite the **Artifact index** with current known artifact paths (merge with existing rows — don't delete rows written by other skills).

Overwrite **Recommended next steps** with a short, opinionated recommendation:

```
Last run: `/<skill-name>` on <date>.
Suggested next: `/<next-skill>` — <one sentence why>.
Alternatives: `/<alt1>` if <condition>, `/<alt2>` if <condition>.
```
