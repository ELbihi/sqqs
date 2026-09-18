"""Background generation job (sections 8, 16, 17).

Walks the generation through the status flow, calls the AI layer, stores the
result asset, and marks COMPLETED (or FAILED). Runs under Celery in prod; the
API falls back to `.run()` inline when the broker is unavailable in dev.
"""
from app.core.db import SessionLocal
from app.models import Background, Character, Garment, Generation, GenerationAsset
from app.services.image_ai import generate_image
from app.services.video_ai import generate_video
from app.workers.celery_app_ref import task


@task(name="run_generation")
def run_generation(generation_id: str) -> str:
    db = SessionLocal()
    try:
        gen = db.get(Generation, generation_id)
        if gen is None:
            return "missing"

        def advance(status: str) -> None:
            gen.status = status
            db.add(gen)
            db.commit()

        try:
            advance("PROCESSING")
            recipe = {
                "character_id": gen.character_id,
                "garment_id": gen.garment_id,
                "background_id": gen.background_id,
                "pose": gen.pose,
                "instruction": gen.instruction,
                "params": gen.params or {},
            }

            # Resolve the selected assets so the provider can do a real try-on /
            # build a text prompt (sections 8-9).
            advance("PREPARING_CHARACTER")
            character = db.get(Character, gen.character_id) if gen.character_id else None
            if character:
                recipe["character_name"] = character.name
                recipe["character_photo_key"] = character.original_photo_key
                recipe["character_photos"] = character.photos
                recipe["appearance_metadata"] = character.appearance_metadata

            advance("PREPARING_GARMENT")
            garment_ids = (gen.params or {}).get("garment_ids")
            if garment_ids is None:
                garment_ids = [gen.garment_id] if gen.garment_id else []
            recipe["garments"] = []
            for garment_id in garment_ids:
                garment = db.get(Garment, garment_id)
                if garment is None or garment.owner_id != gen.owner_id:
                    raise ValueError("Selected clothing is no longer available")
                recipe["garments"].append({
                    "image_key": garment.original_image_key,
                    "category": garment.category or "clothing",
                    "description": " ".join(x for x in [garment.brand, garment.category, garment.name] if x),
                })
            recipe["garment_desc"] = "; ".join(g["description"] for g in recipe["garments"])

            background = db.get(Background, gen.background_id) if gen.background_id else None
            if background:
                recipe["scene"] = background.name
                recipe["scene_prompt"] = background.prompt
                recipe["scene_image_key"] = background.image_key

            advance("GENERATING")
            image_key = generate_image(recipe)

            advance("UPSCALING")
            db.add(GenerationAsset(generation_id=gen.id, kind="image", storage_key=image_key))

            if gen.output_type == "video":
                advance("GENERATING_VIDEO")
                video_key = generate_video(recipe, base_image_key=image_key)
                db.add(
                    GenerationAsset(generation_id=gen.id, kind="video", storage_key=video_key)
                )

            advance("COMPLETED")
            return "COMPLETED"
        except Exception as exc:  # noqa: BLE001
            gen.status = "FAILED"
            gen.error = str(exc)[:1000]
            db.add(gen)
            db.commit()
            return "FAILED"
    finally:
        db.close()
