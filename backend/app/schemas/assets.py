from pydantic import BaseModel, Field


class CharacterCreate(BaseModel):
    name: str
    source: str = "upload"
    appearance_metadata: dict | None = None


class CharacterPhotoOut(BaseModel):
    storage_key: str
    label: str = "Other"


class CharacterOut(BaseModel):
    id: str
    name: str
    source: str
    original_photo_key: str | None = None
    photos: list[CharacterPhotoOut] = Field(default_factory=list)

    class Config:
        from_attributes = True


class GarmentCreate(BaseModel):
    name: str
    category: str | None = None
    brand: str | None = None


class GarmentOut(BaseModel):
    id: str
    name: str
    category: str | None = None
    brand: str | None = None
    original_image_key: str | None = None

    class Config:
        from_attributes = True


class BackgroundCreate(BaseModel):
    name: str
    source: str = "library"
    prompt: str | None = None


class BackgroundOut(BaseModel):
    id: str
    name: str
    source: str
    image_key: str | None = None
    prompt: str | None = None

    class Config:
        from_attributes = True
