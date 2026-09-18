import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch, Mock
os.environ['DATABASE_URL']='sqlite://'
from app.services import gemini_video

class GeminiTests(unittest.TestCase):
 def test_missing_key(self):
  with patch.object(gemini_video.settings,'GEMINI_API_KEY',None):
   with self.assertRaisesRegex(ValueError,'GEMINI_API_KEY'): gemini_video.generate_clip({},'image')
 def test_image_motion_and_download(self):
  client=Mock()
  client.models.generate_videos.return_value=SimpleNamespace(done=True,error=None,response=SimpleNamespace(generated_videos=[SimpleNamespace(video='video')]))
  client.files.download.return_value=b'\x00\x00\x00\x18ftypisom'
  with patch.object(gemini_video.settings,'GEMINI_API_KEY','test'), patch('google.genai.Client',return_value=client), patch.object(gemini_video.storage,'read_bytes',return_value=b'image'):
   result=gemini_video.generate_clip({'pose':'walk'},'image')
  self.assertIn('walk',client.models.generate_videos.call_args.kwargs['prompt'])
  self.assertEqual(client.models.generate_videos.call_args.kwargs['config'].duration_seconds,8)
  from google.genai.models import _GenerateVideosConfig_to_mldev
  request = {}
  _GenerateVideosConfig_to_mldev(client.models.generate_videos.call_args.kwargs['config'], request)
  self.assertEqual(request['parameters']['aspectRatio'], '9:16')
  self.assertNotIn('resolution', request['parameters'])
  self.assertEqual(result[4:8],b'ftyp')

if __name__=='__main__': unittest.main()
