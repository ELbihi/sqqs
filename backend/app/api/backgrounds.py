from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models import Background, User
from app.schemas.assets import BackgroundOut
from app.services import credits
from app.services.image_ai import generate_scene_image
from app.services.storage import storage


class SceneGenerateIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    prompt: str = Field(min_length=3, max_length=1000)
    aspect_ratio: str = "4:3"

router = APIRouter(prefix="/backgrounds", tags=["backgrounds"])

# Section 12 - predefined scene library
SCENE_LIBRARY = [
    "White product studio",
    "Luxury hotel",
    "Beach",
    "Tokyo street",
    "Paris street",
    "Office",
    "Gym",
    "Fashion runway",
    "Moroccan riad",
    "Desert",
]


@router.get("/library")
def scene_library():
    return {"scenes": SCENE_LIBRARY}


@router.post("/generate", response_model=BackgroundOut, status_code=201)
def generate_scene(
    body: SceneGenerateIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a scene from a text prompt using the configured image provider.
    Costs the same as a standard image because it burns real inference."""
    cost = credits.cost_for("image", "standard")
    if credits.get_balance(db, user) < cost:
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, "Insufficient credits")

    try:
        key = generate_scene_image(body.prompt, user.id, body.aspect_ratio)
    except Exception as exc:  # surface provider errors to the UI
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"Scene generation failed: {exc}")

    bg = Background(
        owner_id=user.id, name=body.name, source="ai", prompt=body.prompt, image_key=key
    )
    db.add(bg)
    db.flush()
    credits.charge(db, user, cost, "scene_generation", ref_id=bg.id)
    db.commit()
    db.refresh(bg)
    return bg


@router.get("", response_model=list[BackgroundOut])
def list_backgrounds(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Background).filter(Background.owner_id == user.id).all()


@router.post("", response_model=BackgroundOut, status_code=201)
def create_background(
    name: str = Form(...),
    source: str = Form("library"),
    prompt: str | None = Form(None),
    image: UploadFile | None = File(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bg = Background(owner_id=user.id, name=name, source=source, prompt=prompt)
    if image is not None:
        key = storage.build_key(f"backgrounds/{user.id}", image.filename or "bg.jpg")
        storage.save_bytes(key, image.file.read())
        bg.image_key = key
    db.add(bg)
    db.commit()
    db.refresh(bg)
    return bg


@router.delete("/{background_id}", status_code=204)
def delete_background(
    background_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    obj = db.get(Background, background_id)
    if not obj or obj.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
    db.delete(obj)
    db.commit()
