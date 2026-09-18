import os
import io
import unittest
from unittest.mock import Mock, patch
from types import SimpleNamespace
os.environ['DATABASE_URL']='sqlite://'
os.environ['IMAGE_AI_API_KEY']='test'
from starlette.datastructures import UploadFile, Headers
from app.api.characters import create_character
from app.models import Character
from app.services.image_ai import ReplicateImageProvider

class CharacterPhotoTests(unittest.TestCase):
 def test_multiple_uploads_and_labels(self):
  uploads=[UploadFile(io.BytesIO(b'image'), filename=f'{n}.png', headers=Headers({'content-type':'image/png'})) for n in range(2)]
  with patch('app.api.characters.storage') as storage:
   storage.build_key.side_effect=['front.png','back.png']
   character=create_character(name='Test',source='upload',photo=None,photos=uploads,photo_labels='["Front","Back"]',user=SimpleNamespace(id='me'),db=Mock())
  self.assertEqual(character.original_photo_key,'front.png')
  self.assertEqual([p['label'] for p in character.photos],['Front','Back'])
 def test_legacy_character(self):
  c=Character(original_photo_key='old.png')
  self.assertEqual(c.photos,[{'storage_key':'old.png','label':'Main'}])
 def test_provider_preserves_outfit_slots(self):
  recipe={'character_photo_key':'main','character_photos':[{'storage_key':'main','label':'Front'},{'storage_key':'back','label':'Back'}], 'garments':[{'image_key':str(n),'category':'item','description':'item'} for n in range(6)]}
  with patch('app.services.image_ai.storage.data_uri',side_effect=lambda key:key):
   result=ReplicateImageProvider()._composition_input(recipe)
  self.assertEqual(len(result['input_images']),8)
  self.assertEqual(result['input_images'][-1],'back')
  self.assertIn('SAME person',result['prompt'])

if __name__=='__main__': unittest.main()
