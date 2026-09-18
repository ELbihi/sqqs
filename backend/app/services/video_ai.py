"""Generate real image-to-video clips through Replicate."""
import httpx
from app.services.framing import framing_prompt
from app.core.config import settings
from app.services.storage import storage
from app.services.image_ai import ReplicateImageProvider


class ReplicateVideoProvider(ReplicateImageProvider):
    def __init__(self):
        self.token = settings.VIDEO_AI_API_KEY or settings.IMAGE_AI_API_KEY
        self.timeout = settings.VIDEO_AI_TIMEOUT
        if not self.token:
            raise RuntimeError("Configure a Replicate API key for video generation")

    def generate_clip(self, recipe, base_image_key):
        motion = recipe.get("pose") or "Standing naturally with subtle breathing"
        instruction = recipe.get("instruction") or ""
        prompt = (
            f"Animate the person in the input photograph. Motion: {motion}. {instruction}. "
            "One continuous shot with smooth natural movement. Preserve the person's face, "
            "body proportions, every clothing item, fabric details and the background. "
            "No cuts, no outfit changes, no scene changes."
        )
        prompt += " " + framing_prompt(recipe) + " Maintain this framing throughout the clip."
        url = self._run(settings.VIDEO_AI_MODEL, {
            "image": storage.data_uri(base_image_key), "prompt": prompt,
            "num_frames": 81, "frames_per_second": 16,
            "resolution": "720p", "aspect_ratio": "9:16",
        })
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(url)
            response.raise_for_status()
            data = response.content
        if len(data) < 12 or data[4:8] != b"ftyp":
            raise RuntimeError("Video provider did not return an MP4 file")
        return data


def generate_video(recipe: dict, base_image_key: str | None = None) -> str:
    if settings.VIDEO_AI_PROVIDER == "gemini":
        if not base_image_key:
            raise ValueError("Video generation requires a starting image")
        from app.services.gemini_video import generate_clip
        data = generate_clip(recipe, base_image_key)
        return storage.save_bytes(storage.build_key("generations/videos", "out.mp4"), data)
    if settings.VIDEO_AI_PROVIDER != "replicate":
        raise RuntimeError("Real video requires VIDEO_AI_PROVIDER=replicate")
    if not base_image_key:
        raise ValueError("Video generation requires a starting image")
    data = ReplicateVideoProvider().generate_clip(recipe, base_image_key)
    key = storage.build_key("generations/videos", "out.mp4")
    return storage.save_bytes(key, data)
