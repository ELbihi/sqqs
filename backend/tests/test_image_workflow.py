import os
import unittest
import tempfile
from types import SimpleNamespace
from unittest.mock import Mock, patch

os.environ['DATABASE_URL'] = 'sqlite://'
_storage_dir = tempfile.TemporaryDirectory()
os.environ['LOCAL_STORAGE_DIR'] = _storage_dir.name
os.environ['IMAGE_AI_API_KEY'] = 'test-token'

import httpx
from fastapi import HTTPException, BackgroundTasks
from pydantic import ValidationError
from app.services import image_ai
from app.api.generations import create_generation
from app.schemas.generation import GenerationCreate


class ImageWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.provider = image_ai.ReplicateImageProvider()

    def test_all_references_and_instructions_reach_provider(self):
        recipe = dict(character_photo_key='person', garment_image_key='shirt',
                      scene_image_key='beach', scene_prompt='sunset beach',
                      pose='cross arms', instruction='full body')
        with patch.object(image_ai.storage, 'data_uri', side_effect=lambda k: 'data:' + k):
            payload = self.provider._composition_input(recipe)
        self.assertEqual(payload['input_images'], ['data:person', 'data:shirt', 'data:beach'])
        for text in ['sunset beach', 'cross arms', 'full body', 'Image 1 is the person',
                     'Image 2 is the garment', 'Image 3 is the environment']:
            self.assertIn(text, payload['prompt'])

    def test_partial_references_are_not_discarded(self):
        for key in ['character_photo_key', 'garment_image_key', 'scene_image_key']:
            with self.subTest(key=key), patch.object(image_ai.storage, 'data_uri', return_value='data:ref'), \
                 patch.object(self.provider, '_run', return_value='https://example.com/out.png') as run, \
                 patch.object(image_ai.httpx, 'Client') as client:
                client.return_value.__enter__.return_value.get.return_value.content = b'image'
                self.assertEqual(self.provider.generate({key: 'ref', 'pose': 'standing'}), b'image')
                self.assertEqual(run.call_args.args[0], image_ai.settings.IMAGE_AI_COMPOSITION_MODEL)
                self.assertEqual(run.call_args.args[1]['input_images'], ['data:ref'])

    def test_text_only_keeps_scene_pose_and_instruction(self):
        with patch.object(self.provider, '_run', return_value='https://example.com/out.png') as run, \
             patch.object(image_ai.httpx, 'Client'):
            self.provider.generate(dict(scene='riad', pose='seated', instruction='wide shot'))
        self.assertEqual(run.call_args.args[0], image_ai.settings.IMAGE_AI_MODEL)
        for text in ['riad', 'seated', 'wide shot']:
            self.assertIn(text, run.call_args.args[1]['prompt'])

    def test_empty_provider_output_is_explicit_failure(self):
        with patch.object(image_ai.httpx, 'Client') as client:
            client.return_value.__enter__.return_value.post.return_value.json.return_value = {
                'status': 'succeeded', 'output': []}
            with self.assertRaisesRegex(RuntimeError, 'no output'):
                self.provider._run('owner/model', {})

    def test_poll_http_errors_are_reported(self):
        with patch.object(image_ai.httpx, 'Client') as client, patch.object(image_ai.time, 'sleep'):
            http = client.return_value.__enter__.return_value
            http.post.return_value.json.return_value = {'status': 'processing', 'id': '123'}
            http.get.return_value.raise_for_status.side_effect = httpx.HTTPStatusError(
                'failed', request=httpx.Request('GET', 'https://example.com'), response=httpx.Response(500))
            with self.assertRaises(httpx.HTTPStatusError):
                self.provider._run('owner/model', {})

    def test_foreign_or_missing_assets_rejected_before_charge(self):
        for field in ['character_id', 'garment_id', 'background_id', 'project_id']:
            for asset in [None, SimpleNamespace(owner_id='another-user')]:
                with self.subTest(field=field, asset=asset):
                    db = Mock()
                    db.get.return_value = asset
                    with patch('app.api.generations.credits.charge') as charge:
                        with self.assertRaises(HTTPException) as error:
                            create_generation(GenerationCreate(**{field: 'asset'}), BackgroundTasks(), SimpleNamespace(id='me'), db)
                        self.assertEqual(error.exception.status_code, 404)
                        charge.assert_not_called()
                        db.add.assert_not_called()

    def test_invalid_output_type_rejected(self):
        with self.assertRaises(ValidationError):
            GenerationCreate(output_type='unsupported')


if __name__ == '__main__':
    unittest.main()
