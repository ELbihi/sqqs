"""Image AI layer (sections 8, 9).

The orchestrator combines specialized components: identity preservation, virtual
try-on, scene composition. V1 calls EXTERNAL providers behind this stable
interface (section: "Important architectural choice"), so a provider can be
swapped without touching the rest of the app.

Providers:
  - mock      : draws a placeholder, no paid API (default, for dev).
  - replicate : real models. Virtual try-on (person + garment) when both photos
                exist, otherwise text-to-image from a prompt built from the recipe.

Set IMAGE_AI_PROVIDER=replicate and IMAGE_AI_API_KEY=<replicate token> to enable.
"""
from __future__ import annotations

import io
import re
from email.utils import parsedate_to_datetime
import time

import httpx

from app.core.config import settings
from app.services.storage import storage
from app.services.framing import framing_prompt


def scene_prompt(recipe: dict) -> str:
    """Prompt for generating an EMPTY environment (no people) used as a scene."""
    desc = recipe.get("scene_prompt") or recipe.get("scene") or "a clean photographic studio backdrop"
    return (
        "Photorealistic photograph of an empty environment used as a fashion backdrop: "
        f"{desc}. No people, no mannequins, no text or watermark. "
        "Natural believable lighting, realistic depth and perspective, high detail, sharp focus."
    )


def aspect_of(recipe: dict, default: str = "3:4") -> str:
    """Aspect ratio chosen in the studio, passed through generation params."""
    return ((recipe.get("params") or {}).get("aspect_ratio")) or default


class ImageAIProvider:
    def generate(self, recipe: dict) -> bytes:  # pragma: no cover - interface
        raise NotImplementedError


# --------------------------------------------------------------------------- #
# Mock                                                                         #
# --------------------------------------------------------------------------- #
class MockImageProvider(ImageAIProvider):
    def generate(self, recipe: dict) -> bytes:
        from PIL import Image, ImageDraw

        img = Image.new("RGB", (768, 1024), (24, 24, 32))
        d = ImageDraw.Draw(img)
        lines = [
            "AI VIRTUAL STUDIO",
            "MOCK IMAGE",
            f"character: {recipe.get('character_name') or recipe.get('character_id') or '-'}",
            f"garment:   {recipe.get('garment_desc') or recipe.get('garment_id') or '-'}",
            f"scene:     {recipe.get('scene') or recipe.get('background_id') or '-'}",
            f"pose:      {recipe.get('pose') or '-'}",
        ]
        y = 60
        for ln in lines:
            d.text((40, y), ln, fill=(230, 230, 240))
            y += 40
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()


# --------------------------------------------------------------------------- #
# Replicate                                                                    #
# --------------------------------------------------------------------------- #
class ReplicateImageProvider(ImageAIProvider):
    """Calls Replicate's model-by-name endpoint with `Prefer: wait`, then polls
    until the prediction finishes, and returns the result image bytes."""

    BASE = "https://api.replicate.com/v1"

    def __init__(self) -> None:
        if not settings.IMAGE_AI_API_KEY:
            raise RuntimeError("IMAGE_AI_API_KEY (Replicate token) is not set.")
        self.token = settings.IMAGE_AI_API_KEY
        self.timeout = settings.IMAGE_AI_TIMEOUT

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Prefer": "wait",
        }

    def _request(self, client, method, url, **kwargs):
        # Retry only explicit throttling: a timeout may already have created a job.
        for attempt in range(4):
            response = client.request(method, url, **kwargs)
            if response.status_code != 429:
                response.raise_for_status()
                return response
            delay = 15 * (2 ** attempt)
            retry_after = response.headers.get("Retry-After")
            try:
                if retry_after:
                    try:
                        delay = float(retry_after)
                    except ValueError:
                        delay = parsedate_to_datetime(retry_after).timestamp() - time.time()
                else:
                    detail = str(response.json().get("detail", ""))
                    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:seconds?|s)\b", detail)
                    if match:
                        delay = float(match.group(1)) + 1
            except (ValueError, TypeError, AttributeError, OverflowError):
                pass
            if attempt == 3 or delay > 60:
                raise RuntimeError("Replicate is temporarily rate-limiting this account. Please wait a minute before generating again. If this persists, check your Replicate credit balance and account limits.")
            time.sleep(max(1, delay))

    def _run(self, model: str, model_input: dict) -> str:
        """Run `owner/name` and return the output image URL."""
        with httpx.Client(timeout=self.timeout) as client:
            resp = self._request(client, "POST",
                f"{self.BASE}/models/{model}/predictions",
                headers=self._headers(),
                json={"input": model_input},
            )
            resp.raise_for_status()
            pred = resp.json()

            # `Prefer: wait` may already return a terminal state; otherwise poll.
            deadline = time.time() + self.timeout
            while pred.get("status") not in ("succeeded", "failed", "canceled"):
                if time.time() > deadline:
                    raise TimeoutError("Replicate prediction timed out")
                time.sleep(1.5)
                get_url = pred.get("urls", {}).get("get")
                pred = self._request(client, "GET", get_url, headers=self._headers()).json()

            if pred.get("status") != "succeeded":
                raise RuntimeError(f"Replicate error: {pred.get('error') or pred.get('status')}")

            output = pred.get("output")
            if isinstance(output, list):
                output = output[0]
            if not output:
                raise RuntimeError("Replicate returned no output")
            return output

    def _build_prompt(self, recipe: dict) -> str:
        parts = ["photorealistic fashion photo of a person", framing_prompt(recipe)]
        if recipe.get("character_name"):
            parts.append(f"({recipe['character_name']})")
        if recipe.get("garment_desc"):
            parts.append(f"wearing {recipe['garment_desc']}")
        scene = recipe.get("scene_prompt") or recipe.get("scene")
        if scene:
            parts.append(f"in {scene}")
        if recipe.get("pose"):
            parts.append(f"pose: {recipe['pose']}")
        if recipe.get("instruction"):
            parts.append(recipe["instruction"])
        parts.append("realistic lighting, high detail, sharp focus")
        return ", ".join(parts)

    def generate(self, recipe: dict) -> bytes:
        if recipe.get("scene_only"):
            payload = {
                "prompt": scene_prompt(recipe),
                "output_format": "png",
                "aspect_ratio": aspect_of(recipe, "4:3"),
            }
            output_url = self._run(settings.IMAGE_AI_MODEL, payload)
            with httpx.Client(timeout=self.timeout) as client:
                img = client.get(output_url)
                img.raise_for_status()
                return img.content

        images = []
        directions = [self._build_prompt(recipe)]
        def add_reference(key, role):
            images.append(storage.data_uri(key))
            directions.append(f"Image {len(images)} is the reference for {role}.")

        if recipe.get("character_photo_key"):
            add_reference(recipe["character_photo_key"],
                          "person identity only: preserve face, hair and body proportions; replace their original clothing in the selected categories")

        garments = recipe.get("garments")
        if garments is None:
            garments = ([{"image_key": recipe["garment_image_key"], "category": "clothing"}]
                        if recipe.get("garment_image_key") else [])
        for garment in garments:
            if not garment.get("image_key"):
                raise ValueError("A selected clothing item has no reference photo. Upload its photo before generating.")
            add_reference(garment["image_key"],
                          f"selected {garment.get('category') or 'clothing'}: {garment.get('description') or ''}. "
                          "Dress the person in this exact item, matching its color, material, cut, fit and visible details. "
                          "Ignore the reference model's identity and background")
        if garments:
            directions.append("OUTFIT REQUIREMENT: Wear ALL selected clothing references together as one outfit. "
                              "Replace the person's existing items in those categories. Do not substitute other colors or styles, "
                              "omit an item, or display clothes beside the person. Keep unselected categories natural.")
        if recipe.get("scene_image_key"):
            add_reference(recipe["scene_image_key"], "background environment only; do not copy people or clothing from it")
        payload = {"prompt": "\n".join(directions), "output_format": "png",
                   "aspect_ratio": aspect_of(recipe, "3:4")}
        if images:
            payload["input_images"] = images
        output_url = self._run(settings.IMAGE_AI_MODEL, payload)

        with httpx.Client(timeout=self.timeout) as client:
            img = client.get(output_url)
            img.raise_for_status()
            return img.content


# --------------------------------------------------------------------------- #
# Google Gemini                                                               #
# --------------------------------------------------------------------------- #
class GeminiImageProvider(ImageAIProvider):
    """Google Gemini 2.5 Flash Image (free tier, no card). It accepts several
    input images, so it composes the character + garment + scene in one call:
    preserve the person's identity, dress them in the garment, place them in the
    chosen scene."""

    URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def __init__(self) -> None:
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not set.")
        self.key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_IMAGE_MODEL
        self.timeout = settings.IMAGE_AI_TIMEOUT

    def _image_part(self, key: str) -> dict:
        import base64
        import os

        ext = os.path.splitext(key)[1].lstrip(".").lower() or "png"
        mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp"}.get(ext, "png")
        data = base64.b64encode(storage.read_bytes(key)).decode("ascii")
        return {"inline_data": {"mime_type": f"image/{mime}", "data": data}}

    def _build_prompt(self, recipe: dict, has_person: bool, has_garment: bool) -> str:
        p = ["Generate ONE photorealistic full-body image."]
        if has_person:
            p.append("Use the person in the provided photo and preserve their face and identity exactly.")
        else:
            name = recipe.get("character_name")
            p.append(f"Create a realistic person{f' ({name})' if name else ''}.")
        if has_garment:
            p.append("Dress them in the garment shown in the garment photo, preserving its colors, logos, patterns and material.")
        elif recipe.get("garment_desc"):
            p.append(f"Dress them in {recipe['garment_desc']}.")
        scene = recipe.get("scene_prompt") or recipe.get("scene")
        if scene:
            p.append(f"Place them in this scene: {scene}, with matching lighting and shadows.")
        if recipe.get("pose"):
            p.append(f"Pose: {recipe['pose']}.")
        if recipe.get("instruction"):
            p.append(recipe["instruction"])
        p.append("Photorealistic, natural lighting, high detail, sharp focus.")
        return " ".join(p)

    def generate(self, recipe: dict) -> bytes:
        import base64

        person_key = recipe.get("character_photo_key")
        garment_key = recipe.get("garment_image_key")
        scene_key = recipe.get("scene_image_key")

        if recipe.get("scene_only"):
            parts: list[dict] = [{"text": scene_prompt(recipe)}]
        else:
            parts = [
                {"text": self._build_prompt(recipe, bool(person_key), bool(garment_key))}
            ]
            for key in (person_key, garment_key, scene_key):
                if key:
                    parts.append(self._image_part(key))

        body = {
            "contents": [{"parts": parts}],
            "generationConfig": {"responseModalities": ["IMAGE"]},
        }
        headers = {"x-goog-api-key": self.key, "Content-Type": "application/json"}

        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(self.URL.format(model=self.model), headers=headers, json=body)
            if resp.status_code >= 400:
                raise RuntimeError(f"Gemini error {resp.status_code}: {resp.text[:400]}")
            data = resp.json()

        try:
            for part in data["candidates"][0]["content"]["parts"]:
                blob = part.get("inline_data") or part.get("inlineData")
                if blob and blob.get("data"):
                    return base64.b64decode(blob["data"])
        except (KeyError, IndexError):
            pass
        raise RuntimeError(f"Gemini returned no image: {str(data)[:400]}")


# --------------------------------------------------------------------------- #
def get_image_provider() -> ImageAIProvider:
    provider = settings.IMAGE_AI_PROVIDER
    if provider == "gemini":
        return GeminiImageProvider()
    if provider == "replicate":
        return ReplicateImageProvider()
    return MockImageProvider()


def generate_image(recipe: dict) -> str:
    """Run the image pipeline, store the result, return its storage key."""
    provider = get_image_provider()
    data = provider.generate(recipe)
    key = storage.build_key("generations/images", "out.png")
    return storage.save_bytes(key, data)


def generate_scene_image(prompt: str, owner_id: str, aspect: str = "4:3") -> str:
    """Generate a standalone scene/background image and return its storage key."""
    provider = get_image_provider()
    data = provider.generate(
        {"scene_only": True, "scene_prompt": prompt, "params": {"aspect_ratio": aspect}}
    )
    key = storage.build_key(f"backgrounds/{owner_id}", "scene.png")
    return storage.save_bytes(key, data)
