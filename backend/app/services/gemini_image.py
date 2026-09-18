"""Google image generation using the shared studio reference recipe."""
import base64
import io
import httpx
from PIL import Image
from app.core.config import settings
from app.services.image_ai import ReplicateImageProvider


class GeminiImageProvider(ReplicateImageProvider):
    # Inherit only recipe construction; no Replicate credentials or calls are used.
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("Configure GEMINI_API_KEY for Google image generation")

    def generate(self, recipe):
        composition = self._composition_input(recipe)
        parts = [{"text": composition["prompt"]}]
        for uri in composition["input_images"]:
            header, encoded = uri.split(",", 1)
            parts.append({"inline_data": {"mime_type": header[5:].split(";")[0], "data": encoded}})
        payload = {
            "contents": [{"role": "user", "parts": parts}],
            "generationConfig": {
                "responseModalities": ["TEXT", "IMAGE"],
                "responseFormat": {"image": {"aspectRatio": "ASPECT_RATIO_THREE_BY_FOUR"}},
            },
        }
        with httpx.Client(timeout=settings.IMAGE_AI_TIMEOUT) as client:
            response = client.post(
                f"https://generativelanguage.googleapis.com/v1/models/{settings.GEMINI_IMAGE_MODEL}:generateContent",
                headers={"x-goog-api-key": settings.GEMINI_API_KEY}, json=payload,
            )
            if response.status_code in (401, 403):
                raise RuntimeError("Google image access denied. Check your Gemini key and model access.")
            if response.status_code in (402, 429):
                try:
                    detail = response.json().get('error', {}).get('message', 'Quota exceeded')
                except ValueError:
                    detail = 'Quota exceeded'
                detail = str(detail).replace(settings.GEMINI_API_KEY, '[redacted]')
                raise RuntimeError('Google image quota: ' + detail[:850])
            if response.status_code == 400:
                try:
                    detail = response.json().get('error', {}).get('message', 'Invalid image request')
                except ValueError:
                    detail = 'Invalid image request'
                detail = str(detail).replace(settings.GEMINI_API_KEY, '[redacted]')
                raise RuntimeError('Google rejected the image request: ' + detail[:700])
            response.raise_for_status()
            result = response.json()
        for candidate in result.get("candidates", []):
            for part in (candidate.get("content") or {}).get("parts", []):
                if part.get("thought"):
                    continue
                inline = part.get("inlineData") or part.get("inline_data") or {}
                mime = inline.get("mimeType") or inline.get("mime_type") or ""
                if mime.startswith("image/") and inline.get("data"):
                    data = base64.b64decode(inline["data"], validate=True)
                    # Store genuine PNG bytes for the subsequent video request.
                    with Image.open(io.BytesIO(data)) as image:
                        output = io.BytesIO()
                        image.save(output, format="PNG")
                        return output.getvalue()
        raise RuntimeError("Google returned no image. Try adjusting the inputs or instructions; the request may have been filtered.")
