import mimetypes
from pathlib import Path

from fastapi import FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import auth, backgrounds, billing, characters, clothes, generations, projects
from app.core.config import settings
from app.core.db import Base, engine
from app.services.storage import storage
import app.models  # noqa: F401  (register models)

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    # Dev convenience: create tables. In prod use Alembic migrations.
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME, "image_provider": settings.IMAGE_AI_PROVIDER, "video_provider": settings.VIDEO_AI_PROVIDER}


api = settings.API_V1_PREFIX
app.include_router(auth.router, prefix=api)
app.include_router(characters.router, prefix=api)
app.include_router(clothes.router, prefix=api)
app.include_router(backgrounds.router, prefix=api)
app.include_router(projects.router, prefix=api)
app.include_router(generations.router, prefix=api)
app.include_router(billing.router, prefix=api)

# Media serving.
# Local dev: static files from disk. Deployed with S3/R2 configured (hosts like
# Render have no persistent disk): stream the object through the API so the
# /media/<key> URLs stay identical in both environments.
if storage.use_s3:

    @app.get("/media/{key:path}")
    def media(key: str):
        try:
            data = storage.read_bytes(key)
        except Exception:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
        content_type = mimetypes.guess_type(key)[0] or "application/octet-stream"
        return Response(content=data, media_type=content_type,
                        headers={"Cache-Control": "public, max-age=31536000"})

else:
    _media_dir = Path(settings.LOCAL_STORAGE_DIR)
    _media_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/media", StaticFiles(directory=str(_media_dir)), name="media")
