import os
import unittest
from unittest.mock import patch
os.environ['DATABASE_URL']='sqlite://'
os.environ['IMAGE_AI_API_KEY']='test'
from app.services.video_ai import ReplicateVideoProvider

class VideoTests(unittest.TestCase):
 def test_motion_and_start_image(self):
  provider=ReplicateVideoProvider()
  with patch('app.services.video_ai.storage.data_uri',return_value='data:image/png;base64,test'), patch.object(provider,'_run',return_value='https://example.com/video.mp4') as run, patch('app.services.video_ai.httpx.Client') as client:
   client.return_value.__enter__.return_value.get.return_value.content=b'\x00\x00\x00\x18ftypisom'+b'\x00'*20
   result=provider.generate_clip({'pose':'Walk forward','instruction':'turn left'},'start.png')
   payload=run.call_args.args[1]
   self.assertEqual(payload['image'],'data:image/png;base64,test')
   self.assertIn('Walk forward',payload['prompt']);self.assertIn('turn left',payload['prompt'])
   self.assertEqual(result[4:8],b'ftyp')
 def test_fake_video_rejected(self):
  provider=ReplicateVideoProvider()
  with patch('app.services.video_ai.storage.data_uri',return_value='image'), patch.object(provider,'_run',return_value='https://example.com/video.mp4'), patch('app.services.video_ai.httpx.Client') as client:
   client.return_value.__enter__.return_value.get.return_value.content=b'not a video'
   with self.assertRaisesRegex(RuntimeError,'MP4'): provider.generate_clip({},'start.png')

if __name__=='__main__': unittest.main()
