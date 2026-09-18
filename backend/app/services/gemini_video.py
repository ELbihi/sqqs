"""Google Veo image-to-video through the Gemini API."""
import time
from app.services.framing import framing_prompt
from app.core.config import settings
from app.services.storage import storage

def generate_clip(recipe, base_image_key):
    from google import genai
    from google.genai import types
    if not settings.GEMINI_API_KEY:
        raise ValueError("Add GEMINI_API_KEY to backend/.env and restart the backend to enable Google video generation.")
    prompt = (f"Animate this image. Motion: {recipe.get('pose') or 'subtle natural movement'}. "
              f"{recipe.get('instruction') or ''}. Preserve the same person, all clothing details and location. "
              "One continuous shot, natural movement, stable identity, no outfit changes.")
    prompt += " " + framing_prompt(recipe) + " Maintain this camera distance throughout the clip, without zooming in."
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    operation = client.models.generate_videos(
        model=settings.GEMINI_VIDEO_MODEL,
        prompt=prompt,
        image=types.Image(image_bytes=storage.read_bytes(base_image_key), mime_type="image/png"),
        config=types.GenerateVideosConfig(aspect_ratio="9:16", duration_seconds=8),
    )
    deadline = time.monotonic() + settings.VIDEO_AI_TIMEOUT
    while not operation.done:
        if time.monotonic() >= deadline:
            raise TimeoutError("Google video generation timed out. Check the provider before submitting another request.")
        time.sleep(5)
        operation = client.operations.get(operation)
    if operation.error:
        raise RuntimeError("Google video generation failed. Check model access, billing and input eligibility in Google AI Studio.")
    clips = operation.response.generated_videos if operation.response else None
    if not clips:
        raise RuntimeError("Google returned no video. The input may have been filtered.")
    data = client.files.download(file=clips[0].video)
    if not data or data[4:8] != b"ftyp":
        raise RuntimeError("Google did not return a valid MP4 file")
    return data
