import os
import base64
import io
import unittest
from unittest.mock import patch
from PIL import Image
os.environ['DATABASE_URL']='sqlite://'
from app.services.gemini_image import GeminiImageProvider
from app.services.image_ai import get_image_provider
from app.core.config import settings

class GoogleImagesTests(unittest.TestCase):
 def test_references_and_png(self):
  buf=io.BytesIO();Image.new('RGB',(2,2)).save(buf,format='JPEG')
  result={'candidates':[{'content':{'parts':[{'inlineData':{'mimeType':'image/jpeg','data':base64.b64encode(buf.getvalue()).decode()}}]}}]}
  with patch.object(settings,'GEMINI_API_KEY','test'),patch('app.services.image_ai.storage.data_uri',return_value='data:image/png;base64,aGVsbG8='),patch('app.services.gemini_image.httpx.Client') as client:
   http=client.return_value.__enter__.return_value
   http.post.return_value.status_code=200;http.post.return_value.json.return_value=result
   data=GeminiImageProvider().generate({'character_photo_key':'person','pose':'walk','params':{'framing':'wide'}})
   self.assertTrue(data.startswith(b'\x89PNG'))
   payload=http.post.call_args.kwargs['json']
   self.assertEqual(payload['generationConfig']['responseFormat']['image']['aspectRatio'], 'ASPECT_RATIO_THREE_BY_FOUR')
   self.assertEqual(len(payload['contents'][0]['parts']),2)
   self.assertIn('45 percent',payload['contents'][0]['parts'][0]['text'])
   self.assertIn('googleapis.com',http.post.call_args.args[0])
 def test_provider_needs_no_replicate_key(self):
  with patch.object(settings,'IMAGE_AI_PROVIDER','gemini'),patch.object(settings,'GEMINI_API_KEY','test'),patch.object(settings,'IMAGE_AI_API_KEY',None):
   self.assertIsInstance(get_image_provider(),GeminiImageProvider)

if __name__=='__main__': unittest.main()
