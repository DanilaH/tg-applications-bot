# Release Checklist

This document contains checklists to ensure the quality and security of the application before merging code or presenting the demo.

## Checks Before Merge

- [ ] Code has been checked with Ruff: `python -m ruff check .`
- [ ] Tests passed successfully: `python -m pytest`
- [ ] Dependency consistency check passed: `python -m pip check`
- [ ] No trailing whitespace or unresolved merge conflicts: `git diff --check`
- [ ] No untracked files that should be committed: `rg "\?\?" src tests README.md .env.example docs Dockerfile docker-compose.yml .dockerignore`

## Checks Before Demo

- [ ] Docker configuration is valid: `docker compose config`
- [ ] Docker image builds successfully: `docker compose build` or `docker build .`
- [ ] Manual QA process has been executed using the scenarios outlined in [MANUAL_QA.md](./MANUAL_QA.md).

## Secrets Checklist

To avoid accidental exposure of sensitive information, ensure the following are **NOT** committed to the repository:

- [ ] `.env` file containing real values.
- [ ] Real Telegram Bot Tokens.
- [ ] Real Telegram Chat IDs.
- [ ] The actual SQLite database file (`bookings.sqlite3`).
