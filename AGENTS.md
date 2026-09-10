# AGENTS.md

Guidelines for AI coding agents working in this repository.

## Ponytail discipline (mandatory)

Before adding code, prove it needs to exist. Reuse existing Django/Python/provider
functionality before abstracting. One line before fifty. One module before three
services. Do not implement speculative future requirements. After each milestone,
review the diff and delete unnecessary code. Be lazy about implementation, never
about correctness, security, validation, tenant isolation, or data integrity.

Decision ladder:

1. Does this need to exist at all? (YAGNI)
2. Already in this codebase? Reuse it.
3. Does the standard library do it?
4. Does a native platform/provider feature do it?
5. Does an already-installed dependency do it?
6. Can it be one line? One line.
7. Only then, the minimum code that works.

## Non-negotiables

- Tenant isolation is structural: every tenant view must resolve an organization and
  scope queries by it. Never leak data across organizations.
- Validate at trust boundaries: webhook signatures (Twilio, QStash), internal API
  bearer tokens, upload type/size limits.
- Jobs and webhooks are idempotent; never double-process.
- Twilio credentials are encrypted at rest via `apps.core.crypto`.
- No comments that restate obvious code. No dead code, no unused imports.
- No Celery, no Temporal, no Kubernetes, no vector DB unless a concrete requirement
  forces it. Groq is the default for STT/LLM/TTS.

## Commands

```bash
cd backend
uv sync
.venv/bin/python manage.py makemigrations
.venv/bin/python manage.py migrate
.venv/bin/python manage.py test
.venv/bin/python manage.py seed_demo
```