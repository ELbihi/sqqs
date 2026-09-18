from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models import Garment, User
from app.schemas.assets import GarmentOut
from app.services.storage import storage

router = APIRouter(prefix="/clothes", tags=["clothes"])


@router.get("", response_model=list[GarmentOut])
def list_garments(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Garment).filter(Garment.owner_id == user.id).all()


@router.post("", response_model=GarmentOut, status_code=201)
def create_garment(
    name: str = Form(...),
    category: str | None = Form(None),
    brand: str | None = Form(None),
    image: UploadFile | None = File(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    garment = Garment(owner_id=user.id, name=name, category=category, brand=brand)
    if image is not None:
        key = storage.build_key(f"garments/{user.id}", image.filename or "garment.jpg")
        storage.save_bytes(key, image.file.read())
        garment.original_image_key = key
    db.add(garment)
    db.commit()
    db.refresh(garment)
    return garment


@router.delete("/{garment_id}", status_code=204)
def delete_garment(
    garment_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    obj = db.get(Garment, garment_id)
    if not obj or obj.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
    db.delete(obj)
    db.commit()
