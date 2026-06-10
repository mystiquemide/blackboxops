# Contributing to BlackBoxOps

Thanks for your interest in improving BlackBoxOps.

## Development setup

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash; use .venv/bin/activate on Linux/macOS
pip install -r requirements.txt
npm install
```

Run the app locally:

```bash
# Terminal 1 - API
USE_MOCK_SPLUNK=true USE_MOCK_AUTH=true uvicorn app.main:app --reload --port 8000

# Terminal 2 - React UI
npm run dev
```

## Before you open a pull request

Run the full check suite and make sure everything passes:

```bash
python -m pytest tests/ -q
python -m compileall app scripts tests -q
npm run lint
npm run build
```

## Pull request guidelines

- Keep PRs focused on one change.
- Add or update tests for behavior changes, the policy engine and adapter paths are fully tested and should stay that way.
- The policy engine is fail-closed by design. Changes that weaken that posture need a strong justification in the PR description.
- No secrets, tokens, or real Splunk hostnames in code, tests, or fixtures.
- Match the existing code style; ESLint and the existing module layout are the reference.

## Reporting bugs and requesting features

Use the issue templates. For security issues, do not open a public issue, see [SECURITY.md](SECURITY.md).
