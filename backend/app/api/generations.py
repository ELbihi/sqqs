from fastapi import BackgroundTasks, APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models import Background, Character, Garment, Generation, Project, User
from app.schemas.generation import GenerationCreate, GenerationOut
from app.services import credits

router = APIRouter(prefix="/generations", tags=["generations"])


@router.get("", response_model=list[GenerationOut])
def list_generations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(Generation)
        .filter(Generation.owner_id == user.id)
        .order_by(Generation.created_at.desc())
        .all()
    )


@router.get("/{generation_id}", response_model=GenerationOut)
def get_generation(
    generation_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    obj = db.get(Generation, generation_id)
    if not obj or obj.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
    return obj


@router.post("", response_model=GenerationOut, status_code=202)
def create_generation(
    body: GenerationCreate,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Section 16: create a generation record, charge credits, enqueue the job,
    and immediately return a generation ID with status QUEUED."""
    from app.core.config import settings
    if (settings.IMAGE_AI_PROVIDER == "gemini" or (body.output_type == "video" and settings.VIDEO_AI_PROVIDER == "gemini")) and not settings.GEMINI_API_KEY:
        raise HTTPException(503, "Google generation is not configured. Add GEMINI_API_KEY to backend/.env and restart the backend.")
    garment_ids = list(dict.fromkeys(body.garment_ids or ([body.garment_id] if body.garment_id else [])))
    for garment_id in garment_ids:
        garment = db.get(Garment, garment_id)
        if garment is None or garment.owner_id != user.id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Selected clothing not found")
    # Store the validated selection in existing recipe JSON for old databases.
    params = dict(body.params or {})
    params["garment_ids"] = garment_ids
    params["framing"] = body.framing

    # Validate all references before charging credits or sending media to AI.
    for model, asset_id in (
        (Character, body.character_id), (Garment, body.garment_id),
        (Background, body.background_id), (Project, body.project_id),
    ):
        if asset_id is not None:
            asset = db.get(model, asset_id)
            if asset is None or asset.owner_id != user.id:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "Selected asset not found")

    tier = "hd" if (body.params or {}).get("hd") else "standard"
    cost = credits.cost_for(body.output_type, tier if body.output_type == "image" else "5s")
    if credits.get_balance(db, user) < cost:
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, "Insufficient credits")

    gen = Generation(
        owner_id=user.id,
        project_id=body.project_id,
        output_type=body.output_type,
        status="QUEUED",
        credits_cost=cost,
        character_id=body.character_id,
        garment_id=garment_ids[0] if garment_ids else None,
        background_id=body.background_id,
        pose=body.pose,
        instruction=body.instruction,
        params=params,
    )
    db.add(gen)
    db.flush()
    credits.charge(db, user, cost, "generation", ref_id=gen.id)
    db.commit()
    db.refresh(gen)

    # Section 16: async worker via Celery/Redis. In dev (USE_CELERY=False) we run
    # the job inline so no broker is required; the mock pipeline returns instantly.
    from app.core.config import settings
    from app.workers.tasks import run_generation

    if settings.USE_CELERY:
        try:
            run_generation.delay(gen.id)
        except Exception:
            background_tasks.add_task(run_generation.run, gen.id)
    else:
        background_tasks.add_task(run_generation.run, gen.id)

    db.refresh(gen)
    return gen
