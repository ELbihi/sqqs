# Deploy — free tier (Vercel + Render + Cloudflare R2)

Frontend on Vercel, API on Render, Postgres on Render, generated images on
Cloudflare R2. Everything below has a free plan.

The browser only ever talks to the Vercel domain: `next.config.mjs` proxies
`/api/*` and `/media/*` to the API, so there is no CORS setup to worry about.

---

## 1. Push to GitHub

```bash
cd C:\Users\bbihi\Desktop\saas
git init
git add .
git status            # confirm NO .env and NO studio.db are listed
git commit -m "AI Virtual Studio"
git branch -M main
git remote add origin https://github.com/<you>/<repo>.git
git push -u origin main
```

Keep the repo **private** while testing.

## 2. Cloudflare R2 (image storage)

Render's free plan has no persistent disk — without this, every generated image
disappears when the service restarts.

1. Cloudflare dashboard → **R2** → *Create bucket* (e.g. `studio-media`).
2. **Manage R2 API Tokens** → create a token with *Object Read & Write*.
3. Note: Access Key ID, Secret Access Key, and the endpoint
   `https://<account-id>.r2.cloudflarestorage.com`.

## 3. Render (API + Postgres)

1. **New → Blueprint**, select the repo. It reads `render.yaml` and creates the
   web service plus a free Postgres instance.
2. Fill in the variables marked *sync: false*:

| Variable | Value |
|---|---|
| `FRONTEND_ORIGIN` | `https://<your-app>.vercel.app` (fill after step 4) |
| `IMAGE_AI_PROVIDER` | `replicate` |
| `IMAGE_AI_API_KEY` | your Replicate token |
| `IMAGE_AI_MODEL` | the model you use |
| `S3_ENDPOINT_URL` | `https://<account-id>.r2.cloudflarestorage.com` |
| `S3_BUCKET` | `studio-media` |
| `S3_ACCESS_KEY` / `S3_SECRET_KEY` | from step 2 |

3. Deploy, then check `https://<service>.onrender.com/health`.

## 4. Vercel (frontend)

1. **Add New → Project**, import the repo.
2. **Root Directory: `frontend`** (important).
3. Environment variable:

| Variable | Value |
|---|---|
| `BACKEND_URL` | `https://<service>.onrender.com` |

4. Deploy. Then go back to Render and set `FRONTEND_ORIGIN` to the Vercel URL.

Send the Vercel URL to whoever is testing.

---

## Known limits of the free tier

- **Render free sleeps after 15 min idle** — the first request then takes
  30–50 s. A generation started right after a wake-up can feel very slow.
- **Free Postgres expires after 90 days** — fine for a test, not for real users.
- **Generations cost real money** on your Replicate account. Anyone with the
  link can spend your credits, so only share it with people you trust, and keep
  the signup credits low (`FREE_SIGNUP_CREDITS`).
- Tables are auto-created at startup (`create_all`). Move to Alembic migrations
  before this carries data you care about.
