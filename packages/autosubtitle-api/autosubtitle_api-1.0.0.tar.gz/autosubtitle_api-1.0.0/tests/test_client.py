"""Unit tests for AutoSubtitleClient (with mocking)."""

import unittest
from unittest.mock import Mock, patch, mock_open
import json
from autosubtitle import AutoSubtitleClient, AutoSubtitleError


class TestAutoSubtitleClient(unittest.TestCase):
    """Unit tests for AutoSubtitleClient."""

    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test-api-key"
        self.client = AutoSubtitleClient(self.api_key)

    @patch("autosubtitle.client.requests.request")
    def test_create_subtitle_with_url(self, mock_request):
        """Test creating subtitle with video URL."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "message": "Subtitle generation started successfully.",
            "transaction": {
                "id": "test-id",
                "status": "processing",
            },
        }
        mock_request.return_value = mock_response

        response = self.client.create_subtitle(
            video_url="https://example.com/video.mp4",
            language="en",
            font_name="Montserrat",
        )

        self.assertEqual(response["transaction"]["id"], "test-id")
        self.assertEqual(response["transaction"]["status"], "processing")
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        self.assertEqual(call_args[0][0], "POST")
        self.assertIn("/api/subtitles", call_args[0][1])
        self.assertEqual(call_args[1]["headers"]["X-API-Key"], self.api_key)

    @patch("autosubtitle.client.requests.request")
    def test_create_subtitle_with_file(self, mock_request):
        """Test creating subtitle with video file."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "message": "Subtitle generation started successfully.",
            "transaction": {"id": "test-id", "status": "processing"},
        }
        mock_request.return_value = mock_response

        video_bytes = b"fake video content"
        response = self.client.create_subtitle(video_file=video_bytes)

        self.assertEqual(response["transaction"]["id"], "test-id")
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        self.assertIn("files", call_args[1])
        self.assertIn("video", call_args[1]["files"])

    def test_create_subtitle_no_source(self):
        """Test creating subtitle without video source."""
        with self.assertRaises(ValueError) as context:
            self.client.create_subtitle()
        self.assertIn("Either video_url or video_file", str(context.exception))

    @patch("autosubtitle.client.requests.request")
    def test_get_transactions(self, mock_request):
        """Test getting all transactions."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "projects": [
                {"id": "id1", "status": "completed"},
                {"id": "id2", "status": "processing"},
            ]
        }
        mock_request.return_value = mock_response

        response = self.client.get_transactions()

        self.assertIn("projects", response)
        self.assertEqual(len(response["projects"]), 2)
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        self.assertEqual(call_args[0][0], "GET")
        self.assertIn("/api/subtitles", call_args[0][1])

    @patch("autosubtitle.client.requests.request")
    def test_get_transaction(self, mock_request):
        """Test getting a specific transaction."""
        transaction_id = "test-transaction-id"
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "transaction": {"id": transaction_id, "status": "completed"}
        }
        mock_request.return_value = mock_response

        response = self.client.get_transaction(transaction_id)

        self.assertEqual(response["transaction"]["id"], transaction_id)
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        self.assertEqual(call_args[0][0], "GET")
        self.assertIn(f"/api/subtitles/{transaction_id}", call_args[0][1])

    def test_get_transaction_no_id(self):
        """Test getting transaction without ID."""
        with self.assertRaises(ValueError) as context:
            self.client.get_transaction("")
        self.assertIn("Transaction ID is required", str(context.exception))

    @patch("autosubtitle.client.requests.request")
    def test_get_billing_summary(self, mock_request):
        """Test getting billing summary."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "plan": {"id": 1, "name": "Free", "is_free": True},
            "usage": {"used": 10, "limit": 100},
        }
        mock_request.return_value = mock_response

        response = self.client.get_billing_summary()

        self.assertIn("plan", response)
        self.assertEqual(response["plan"]["id"], 1)
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        self.assertEqual(call_args[0][0], "GET")
        self.assertIn("/api/billing/summary", call_args[0][1])

    @patch("autosubtitle.client.requests.request")
    def test_api_error_handling(self, mock_request):
        """Test API error handling."""
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.reason = "Not Found"
        mock_response.json.return_value = {"message": "Transaction not found"}
        mock_request.return_value = mock_response

        with self.assertRaises(AutoSubtitleError) as context:
            self.client.get_transaction("invalid-id")

        self.assertEqual(context.exception.status, 404)
        self.assertIn("Transaction not found", str(context.exception))

    @patch("autosubtitle.client.requests.request")
    def test_network_error(self, mock_request):
        """Test network error handling."""
        import requests

        mock_request.side_effect = requests.exceptions.ConnectionError("Connection failed")

        with self.assertRaises(AutoSubtitleError) as context:
            self.client.get_transactions()

        self.assertIn("Network error", str(context.exception))

    @patch("autosubtitle.client.requests.request")
    @patch("autosubtitle.client.time.sleep")
    @patch("autosubtitle.client.time.time")
    def test_wait_for_transaction_completed(self, mock_time, mock_sleep, mock_request):
        """Test waiting for transaction completion."""
        # Mock time to control elapsed time
        # time.time() is called: start_time, then elapsed check in loop
        call_times = []
        
        def time_side_effect():
            call_times.append(len(call_times))
            # Start time: 1000ms
            if len(call_times) == 1:
                return 1.0  # Start time in seconds
            # First elapsed check: 2.0s (1000ms elapsed)
            elif len(call_times) == 2:
                return 2.0
            # Second elapsed check: 3.0s (2000ms elapsed, but transaction completed)
            else:
                return 3.0

        mock_time.side_effect = time_side_effect

        # First call: processing, second call: completed
        mock_response1 = Mock()
        mock_response1.ok = True
        mock_response1.json.return_value = {
            "transaction": {"id": "test-id", "status": "processing"}
        }

        mock_response2 = Mock()
        mock_response2.ok = True
        mock_response2.json.return_value = {
            "transaction": {"id": "test-id", "status": "completed"}
        }

        mock_request.side_effect = [mock_response1, mock_response2]

        on_progress = Mock()
        result = self.client.wait_for_transaction(
            "test-id", interval=1000, timeout=10000, on_progress=on_progress
        )

        self.assertEqual(result["status"], "completed")
        self.assertGreaterEqual(on_progress.call_count, 1)

    @patch("autosubtitle.client.requests.request")
    @patch("autosubtitle.client.time.sleep")
    @patch("autosubtitle.client.time.time")
    def test_wait_for_transaction_failed(self, mock_time, mock_sleep, mock_request):
        """Test waiting for failed transaction."""
        mock_time.side_effect = [1000, 2000]

        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "transaction": {
                "id": "test-id",
                "status": "failed",
                "error_message": "Processing failed",
            }
        }
        mock_request.return_value = mock_response

        with self.assertRaises(AutoSubtitleError) as context:
            self.client.wait_for_transaction("test-id", interval=1000, timeout=10000)

        self.assertIn("Processing failed", str(context.exception))
        self.assertEqual(context.exception.status, 500)

    @patch("autosubtitle.client.requests.request")
    @patch("autosubtitle.client.time.sleep")
    @patch("autosubtitle.client.time.time")
    def test_wait_for_transaction_timeout(self, mock_time, mock_sleep, mock_request):
        """Test transaction timeout."""
        # Mock time to simulate timeout
        mock_time.side_effect = [1000, 2000, 12000]  # Start, first poll, timeout

        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "transaction": {"id": "test-id", "status": "processing"}
        }
        mock_request.return_value = mock_response

        with self.assertRaises(AutoSubtitleError) as context:
            self.client.wait_for_transaction("test-id", interval=1000, timeout=5000)

        self.assertIn("timeout", str(context.exception).lower())
        self.assertEqual(context.exception.status, 408)

    def test_client_initialization_no_api_key(self):
        """Test client initialization without API key."""
        with self.assertRaises(ValueError) as context:
            AutoSubtitleClient("")
        self.assertIn("API key is required", str(context.exception))

    @patch("autosubtitle.client.requests.request")
    def test_custom_base_url(self, mock_request):
        """Test client with custom base URL."""
        custom_url = "https://custom-api.example.com"
        client = AutoSubtitleClient(self.api_key, base_url=custom_url)

        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"plan": {"id": 1}}
        mock_request.return_value = mock_response

        client.get_billing_summary()

        call_args = mock_request.call_args
        self.assertIn(custom_url, call_args[0][1])


if __name__ == "__main__":
    unittest.main()

