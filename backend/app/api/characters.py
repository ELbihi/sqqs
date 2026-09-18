import json
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models import Character, User
from app.schemas.assets import CharacterOut
from app.services.storage import storage

router = APIRouter(prefix="/characters", tags=["characters"])


@router.get("", response_model=list[CharacterOut])
def list_characters(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Character).filter(Character.owner_id == user.id).all()


@router.post("", response_model=CharacterOut, status_code=201)
def create_character(
    name: str = Form(...),
    source: str = Form("upload"),
    photo: UploadFile | None = File(None),
    photos: list[UploadFile] = File(default=[]),
    photo_labels: str = Form("[]"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    character = Character(owner_id=user.id, name=name, source=source)
    uploads = ([photo] if photo is not None else []) + list(photos)
    if len(uploads) > 12:
        raise HTTPException(422, "Choose up to 12 character photos")
    try:
        labels = json.loads(photo_labels)
        if not isinstance(labels, list) or any(not isinstance(x, str) or len(x) > 80 for x in labels):
            raise ValueError()
    except (ValueError, TypeError):
        raise HTTPException(422, "Invalid photo labels")
    references = []
    for index, upload in enumerate(uploads):
        if not (upload.content_type or "").startswith("image/"):
            raise HTTPException(422, "Please upload image files")
        key = storage.build_key(f"characters/{user.id}", upload.filename or "photo.jpg")
        storage.save_bytes(key, upload.file.read())
        references.append({"storage_key": key, "label": labels[index] if index < len(labels) else "Other"})
    if references:
        character.original_photo_key = references[0]["storage_key"]
        character.appearance_metadata = {"photos": references}
    db.add(character)
    db.commit()
    db.refresh(character)
    return character


@router.delete("/{character_id}", status_code=204)
def delete_character(
    character_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    obj = db.get(Character, character_id)
    if not obj or obj.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
    db.delete(obj)
    db.commit()
