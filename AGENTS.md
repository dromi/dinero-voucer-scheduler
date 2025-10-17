# Repository Guidelines

## Project Structure & Module Organization
Source lives at the repo root. `connect_dinero.py` is the single entry point that handles auth, voucher creation, and booking. `run_connect_dinero.sh` is a convenience wrapper for exporting credentials before executing the script. Dependency metadata sits in `pyproject.toml`, while runtime pins are in `requirements.txt` and `uv.lock`. Add future modules under a dedicated package directory (for example `dinero_scheduler/`) and keep any test assets grouped under `tests/`.

## Build, Test, and Development Commands
```bash
python -m venv .venv && source .venv/bin/activate  # create an isolated env
pip install -r requirements.txt                   # install runtime deps
python connect_dinero.py --voucher-date 2024-01-01 \
  --description "Sample voucher" --amount 100      # run the verifier
./run_connect_dinero.sh                            # helper that sets env vars
```
Use `uv pip sync uv.lock` if you prefer parity with the checked-in lockfile.

## Coding Style & Naming Conventions
Target Python 3.12 and follow PEP 8 with 4-space indentation. Keep functions small, prefer type hints, and reuse the existing dataclass patterns for shared state. Name new modules and packages with `snake_case`; reserve `CamelCase` for classes and `UPPER_SNAKE_CASE` for constants such as additional API URLs. Keep side-effecting code inside `main()` so that helper functions remain import-friendly for testing.

## Testing Guidelines
No automated tests ship yet. When adding them, use `pytest`, store cases under `tests/`, and mirror the module structure (`tests/test_connect_dinero.py`). Focus on isolating HTTP logic via mocked `requests` sessions, and add integration checks that exercise real credentials only when secrets can be supplied safely. For manual runs, ensure all required `DINERO_*` environment variables are exported before invoking the script.

## Commit & Pull Request Guidelines
Follow the existing Git history: short, imperative subject lines (e.g., `Add manual voucher booking`) and optional body paragraphs for motivation. Reference related issues in the body when available, and group unrelated changes into separate commits. Pull requests should include: a concise summary of the change, how it was verified (commands run, manual steps), any screenshots of CLI output when relevant, and notes about configuration updates.

## Security & Configuration Tips
Never hard-code Dinero credentials; rely on environment variables or secrets managers. Rotate `DINERO_API_KEY` promptly if it was used during local tests. When sharing sample commands, redact organization IDs and voucher GUIDs. If you script recurring jobs, store credentials outside the repository (for example, in CI secrets) and document any new environment variables in `README.md`.
