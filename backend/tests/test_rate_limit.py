import os
import unittest
from unittest.mock import Mock, patch
import httpx
os.environ['IMAGE_AI_API_KEY']='test'
from app.services.image_ai import ReplicateImageProvider

class RateLimitTests(unittest.TestCase):
 def test_retry_after_then_success(self):
  request=Mock(side_effect=[httpx.Response(429,headers={'Retry-After':'7'}),httpx.Response(200)])
  with patch('app.services.image_ai.time.sleep') as sleep:
   result=ReplicateImageProvider()._request_with_rate_limit(request)
  self.assertEqual(result.status_code,200);sleep.assert_called_once_with(7)
 def test_body_reset(self):
  request=Mock(side_effect=[httpx.Response(429,json={'detail':'Your rate limit resets in ~30s.'}),httpx.Response(200)])
  with patch('app.services.image_ai.time.sleep') as sleep:
   ReplicateImageProvider()._request_with_rate_limit(request)
  sleep.assert_called_once_with(31)
 def test_persistent_limit_stops(self):
  request=Mock(return_value=httpx.Response(429,headers={'Retry-After':'1'}))
  with patch('app.services.image_ai.time.sleep'),self.assertRaisesRegex(RuntimeError,'rate-limited'):
   ReplicateImageProvider()._request_with_rate_limit(request)
  self.assertEqual(request.call_count,4)
 def test_billing_not_retried(self):
  request=Mock(return_value=httpx.Response(402))
  self.assertEqual(ReplicateImageProvider()._request_with_rate_limit(request).status_code,402)
  request.assert_called_once()

if __name__=='__main__': unittest.main()
