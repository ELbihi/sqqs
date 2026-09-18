from typing import Literal

from pydantic import BaseModel, Field


class GenerationCreate(BaseModel):
    framing: Literal["close_up", "waist_up", "full_body", "wide"] = "full_body"
    output_type: Literal["image", "video"] = "image"  # image|video
    character_id: str | None = None
    garment_id: str | None = None  # Legacy single-item clients
    garment_ids: list[str] = Field(default_factory=list, max_length=6)
    background_id: str | None = None
    pose: str | None = None
    instruction: str | None = None
    project_id: str | None = None
    params: dict | None = None


class GenerationAssetOut(BaseModel):
    id: str
    kind: str
    storage_key: str

    class Config:
        from_attributes = True


class GenerationOut(BaseModel):
    id: str
    output_type: str
    status: str
    error: str | None = None
    credits_cost: int
    pose: str | None = None
    instruction: str | None = None
    assets: list[GenerationAssetOut] = []

    class Config:
        from_attributes = True
