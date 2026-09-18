# Image workflow

When `IMAGE_AI_PROVIDER=replicate`, recipes with any reference photo now use
`black-forest-labs/flux-2-pro`. The request includes the character, garment and
uploaded scene images in a numbered order, plus the scene description, pose and
custom instructions. Missing references are omitted. Recipes without photos
continue to use `IMAGE_AI_MODEL` for text-to-image generation.

Configuration in `backend/.env`:

```dotenv
IMAGE_AI_PROVIDER=replicate
IMAGE_AI_API_KEY=your-replicate-token
IMAGE_AI_COMPOSITION_MODEL=black-forest-labs/flux-2-pro
```

Restart the API and any Celery worker after configuration changes. The default
mock provider remains available for development. Existing credentials are not
changed by this update. The composition model must support `input_images`,
`prompt`, `aspect_ratio` and `output_format` with the FLUX.2 Pro schema.

Reference: https://replicate.com/black-forest-labs/flux-2-pro/api/schema

Each live generation uses the provider account's paid inference. The existing
credit prices have not been recalculated for this model. Identity, garment
fidelity and pose accuracy need visual evaluation on real outputs; passing
references to the provider does not guarantee exact reproduction.

All selected asset and project IDs are checked for ownership before charging
credits. Invalid output types are rejected. Provider polling now reports HTTP
failures and empty outputs explicitly.

Run regression tests from `backend` with its dependencies installed:

```sh
python -m unittest discover -s tests -v
```

Tests mock external AI calls and do not incur inference charges. Video generation,
payment processing and synchronous queue fallback are unchanged.
