# CI/CD AI Guardrails

Lightweight guardrails for CI/CD: scans diffs/PRs for **secrets**, **risky dependency changes**, and **missing tests**. Uses **heuristics-first** rules with optional **LLM enrichment** for explanations. Exposes both a **CLI** (pre-commit) and an **API** (FastAPI).

## Why this project
Small teams need simple, reliable checks that prevent avoidable incidents (leaked secrets, accidental downgrades, untested changes). This project demonstrates practical guardrails that fit into developer workflows without heavy infra.

## Features
- **Secrets scan** (common tokens/keys by regex)
- **Dependency checks** (downgrades / suspicious version jumps)
- **Test coverage smell** (code touched but tests untouched)
- **CLI** for local dev / pre-commit
- **FastAPI** endpoint for CI services

![CI](https://github.com/pushkarsambhus/ci-cd-ai-guardrails/actions/workflows/ci.yml/badge.svg)

## Quick start (CLI)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run a local scan on a diff text
python -m app.cli --repo web --diff "$(git diff HEAD~1)"
```

## Quick start (API)
```bash
uvicorn app.api:app --reload
curl -X POST http://127.0.0.1:8000/scan -H "Content-Type: application/json"   -d '{"repo":"web","diff":"modified app.py\n+API_KEY=abc123\n-requests==2.31.0\n+requests==2.20.0\n"}'
```

## GitHub Action (example)
Add to `.github/workflows/guardrails.yml`:
```yaml
name: guardrails
on: [pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - name: Run guardrails
        run: python -m app.cli --repo "${{ github.repository }}" --diff "$(git diff origin/${{ github.base_ref }}...HEAD)"
```

## Project structure
```
app/
  api.py      # FastAPI: POST /scan
  scanner.py  # rules engine (secrets, deps, tests) + optional LLM
  cli.py      # command-line interface
tests/
  test_scanner.py
.github/workflows/
  ci.yml
examples/
  sample_diff.txt
```

## License
MIT
