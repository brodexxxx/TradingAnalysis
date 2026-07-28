# AGENTS.md

## Purpose
This file guides automated and human contributors working in this repository.

## Repository Overview
- Python-based trading analysis toolkit for technical analysis and prediction.
- Main analysis workflow: `trading_analysis.py`.
- Web API: `app.py` (Flask).
- Dashboard UI: `streamlit_app.py` and `dashboard.py`.
- Tests: `test_*.py` files in the repository root.

## Environment Setup
1. Install runtime dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. (Optional) Install expanded/dev dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

## Common Run Commands
- Run core analysis:
  ```bash
  python trading_analysis.py
  ```
- Run Flask API locally:
  ```bash
  python app.py
  ```
- Run Streamlit dashboard:
  ```bash
  streamlit run streamlit_app.py
  ```

## Validation
- Run tests:
  ```bash
  python -m pytest
  ```
- If `pytest` is unavailable, install it in your environment before running tests.

## Contribution Rules
- Keep changes focused and minimal.
- Avoid unrelated refactors in the same change.
- Do not commit secrets, credentials, or API tokens.
- Preserve existing behavior unless the task explicitly requires changes.
- Prefer updating existing modules over introducing new dependencies.

## Notes
- Repository may contain local artifacts such as `.db`, `.csv`, `.pkl`, and generated image files; avoid unnecessary churn to these files.
