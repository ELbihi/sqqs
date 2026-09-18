# AI Virtual Studio — MVP (V1)

Combine **who** + **wearing what** + **where** + **doing what**, then let AI
generate a realistic image (or, later, video).

This repo scaffolds the **V1** from the architecture doc: responsive web app +
authentication + AI Studio + reusable character / garment / scene assets +
image generation + async job queue + generation history + basic credits.

```
saas/
├── backend/     FastAPI + SQLAlchemy + Celery (orchestrator)
├── frontend/    Next.js 15 (App Router) + TypeScript + Tailwind
└── docker-compose.yml   Postgres + Redis for local dev
```

## Stack (section 21)

| Layer        | Tech                                   |
|--------------|----------------------------------------|
| Web          | Next.js 15, TypeScript, Tailwind       |
| Backend      | Python, FastAPI, SQLAlchemy            |
| DB / cache   | PostgreSQL, Redis                      |
| Jobs         | Celery                                 |
| Storage      | S3-compatible (local disk in dev)      |
| Auth         | JWT (email + password)                 |
| Image/Video AI | External providers behind an interface (mock in dev) |

The backend is an **orchestrator**: it manages product logic and calls AI
services rather than embedding inference in request handlers. Swap the mock
providers in `backend/app/services/image_ai.py` / `video_ai.py` for real APIs
without touching the rest of the app.

---

## 1. Start infrastructure

```bash
docker compose up -d        # Postgres on :5432, Redis on :6379
```

No Docker? Install Postgres + Redis locally and update `backend/.env`.

## 2. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                # edit SECRET_KEY etc.
uvicorn app.main:app --reload                       # http://localhost:8000
```

API docs: http://localhost:8000/docs
Health:   http://localhost:8000/health

### Async worker (optional in dev)

If Redis is running, process generations in the background:

```bash
cd backend && source .venv/bin/activate
celery -A app.workers.celery_app.celery_app worker --loglevel=info
```

If the broker is down, the API automatically runs the generation **inline**, so
the studio still works with just the API running.

## 3. Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev                                         # http://localhost:3000
```

Open http://localhost:3000, create an account (you get free signup credits),
then go to **AI Studio**.

---

## How the core flow works (sections 16–17)

1. User builds a recipe in **AI Studio** (character + clothes + scene + pose).
2. `POST /generations` creates a record, charges credits, enqueues the job, and
   returns a generation ID with status `QUEUED`.
3. The worker walks the status flow
   `QUEUED → PROCESSING → PREPARING_CHARACTER → PREPARING_GARMENT → GENERATING → UPSCALING → COMPLETED`
   (or `FAILED`), stores the result asset, and updates the DB.
4. The studio polls `GET /generations/{id}` and shows the image/video when done.

## Data model (sections 10, 11, 14)

`users, characters, garments, backgrounds, projects, generations,
generation_assets, credit_ledger`. Media bytes live in object storage; the DB
holds metadata, ownership, storage keys and generation state.

In dev the tables are auto-created on startup. For production, switch to Alembic
migrations (already in `requirements.txt`).

## Going to production

- Replace mock AI providers with real image/video APIs.
- Move storage to S3 (set `S3_*` in `.env`).
- Replace the dev `POST /billing/credits/purchase` top-up with Stripe checkout + webhooks.
- Use Alembic migrations instead of `create_all`.
- Add OAuth (Google/Apple) sign-in (section 18).

## Roadmap (section 23)

- **V1 (this repo):** image studio, assets, queue, history, basic credits.
- **V2:** image-to-video generation + motion control.
- **V3:** subscriptions, asset libraries, projects, teams, API access.
- **V4:** Shopify integration, catalog import, batch/ad generation, brand workspaces.
