# Vibeout — AI Voice Calling Platform

Multi-tenant SaaS: connect your Twilio account, import numbers, upload leads (CSV), generate **grounded call-ready context** per lead (Groq LLM), review/approve, then run outbound AI voice calls via Twilio → LiveKit → Groq STT/LLM/TTS.

## Stack

Django (ASGI) · PostgreSQL (Neon) · Upstash Redis · Backblaze B2 (S3) · Upstash QStash · Twilio · LiveKit · Groq · React + Vite

## Structure

- `backend/` — Django control-plane API (`config/` settings, `apps/` modules)
- `frontend/` — React SPA

## Quick start

**Backend**
```bash
cd backend
uv sync
cp .env.example .env      # fill in secrets
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_demo   # demo org + sample leads
.venv/bin/python manage.py runserver
```
Jobs run **inline** in dev (auto when `DJANGO_DEBUG=true`). For real async QStash: set `QSTASH_INLINE=false`, `PUBLIC_BASE_URL` to a public tunnel (`cloudflared tunnel --url http://localhost:8000`).

**Frontend**
```bash
cd frontend
npm install
npm run dev               # http://localhost:5173
```

**Tests**
```bash
cd backend
DATABASE_URL="sqlite:////tmp/test.sqlite3" .venv/bin/python manage.py test
```