import os
import unittest
from unittest.mock import patch, Mock
from types import SimpleNamespace
os.environ['DATABASE_URL']='sqlite://'
os.environ['IMAGE_AI_API_KEY']='test'
from app.services.image_ai import ReplicateImageProvider, storage
from app.schemas.generation import GenerationCreate
from app.api.generations import create_generation
from fastapi import HTTPException, BackgroundTasks
from pydantic import ValidationError

class MultiTests(unittest.TestCase):
 def test_outfit_references(self):
  recipe={'character_photo_key':'person','scene_image_key':'scene','garments':[{'image_key':'pants','category':'pants','description':'wide jeans'},{'image_key':'cap','category':'cap','description':'red cap'}]}
  with patch.object(storage,'data_uri',side_effect=lambda k:k):
   result=ReplicateImageProvider()._composition_input(recipe)
  self.assertEqual(result['input_images'],['person','scene','pants','cap'])
  self.assertIn('ONLY the pants',result['prompt'])
  self.assertIn('ONLY the cap',result['prompt'])
 def test_limit(self):
  with self.assertRaises(ValidationError): GenerationCreate(garment_ids=['x']*7)
 def test_each_owner_checked(self):
  db=Mock(); db.get.side_effect=[SimpleNamespace(owner_id='me'),SimpleNamespace(owner_id='other')]
  with self.assertRaises(HTTPException):
   create_generation(GenerationCreate(garment_ids=['pants','cap']),BackgroundTasks(),SimpleNamespace(id='me'),db)
  db.add.assert_not_called()

if __name__=='__main__': unittest.main()
