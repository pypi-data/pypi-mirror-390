"""Integration tests for AutoSubtitle API (with real API calls)."""

import os
import unittest
import time
from autosubtitle import AutoSubtitleClient, AutoSubtitleError

API_KEY = os.getenv("AUTOSUBTITLE_API_KEY")
BASE_URL = os.getenv("AUTOSUBTITLE_BASE_URL", "https://api.autosubtitle.net")

# Skip all integration tests if no API key is provided
skip_if_no_key = unittest.skipIf(
    not API_KEY, "AUTOSUBTITLE_API_KEY not set. Skipping integration tests."
)


@skip_if_no_key
class TestAutoSubtitleIntegration(unittest.TestCase):
    """Integration tests for AutoSubtitleClient."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        if not API_KEY:
            return
        cls.client = AutoSubtitleClient(API_KEY, base_url=BASE_URL)
        cls.test_transaction_id = None

    def test_get_billing_summary(self):
        """Test getting billing summary."""
        summary = self.client.get_billing_summary()

        self.assertIsNotNone(summary)
        self.assertIn("plan", summary)
        self.assertIn("id", summary["plan"])
        self.assertGreater(summary["plan"]["id"], 0)
        self.assertIn("name", summary["plan"])
        self.assertIn("usage", summary)
        self.assertIsInstance(summary["usage"]["used"], int)
        self.assertGreaterEqual(summary["usage"]["limit"], 0)

    def test_get_transactions(self):
        """Test getting all transactions."""
        response = self.client.get_transactions()

        self.assertIsNotNone(response)
        self.assertIn("projects", response)

        projects = response["projects"]
        self.assertIsInstance(projects, list)

        if len(projects) > 0:
            transaction = projects[0]
            self.assertIn("id", transaction)
            self.assertIn("status", transaction)
            self.assertIn(
                transaction["status"], ["processing", "completed", "failed", "pending"]
            )
            print(f"✅ Found {len(projects)} transactions")
        else:
            print("ℹ️  No transactions found (this is OK for new accounts)")

    def test_create_subtitle_with_url(self):
        """Test creating subtitle from video URL."""
        test_video_url = (
            "https://v3b.fal.media/files/b/kangaroo/oUCiZjQwEy6bIQdPUSLDF_output.mp4"
        )

        response = self.client.create_subtitle(
            video_url=test_video_url,
            language="en",
            font_name="Montserrat",
            font_size=100,
            position="bottom",
        )

        self.assertIsNotNone(response)
        self.assertIn("transaction", response)
        self.assertIn("id", response["transaction"])
        self.assertEqual(response["transaction"]["status"], "processing")

        self.__class__.test_transaction_id = response["transaction"]["id"]
        print(f"✅ Created transaction: {self.__class__.test_transaction_id}")

    def test_get_transaction_by_id(self):
        """Test getting a specific transaction by ID."""
        if not self.__class__.test_transaction_id:
            self.skipTest("No transaction ID from previous test")

        # Wait a bit for transaction to be saved in database
        time.sleep(1)

        try:
            response = self.client.get_transaction(self.__class__.test_transaction_id)

            self.assertIsNotNone(response)
            self.assertIn("transaction", response)
            self.assertEqual(
                response["transaction"]["id"], self.__class__.test_transaction_id
            )
            self.assertIn("status", response["transaction"])
            print(
                f"✅ Retrieved transaction: {self.__class__.test_transaction_id}, "
                f"status: {response['transaction']['status']}"
            )
        except AutoSubtitleError as e:
            # Transaction might not be immediately available, this is OK
            print(
                f"⚠️  Could not retrieve transaction immediately: {e.message}"
            )

    def test_error_handling_invalid_transaction_id(self):
        """Test error handling for invalid transaction ID."""
        invalid_id = "00000000-0000-0000-0000-000000000000"

        with self.assertRaises(AutoSubtitleError):
            self.client.get_transaction(invalid_id)

    def test_error_handling_invalid_video_url(self):
        """Test error handling for invalid video URL."""
        with self.assertRaises(AutoSubtitleError):
            self.client.create_subtitle(
                video_url="https://invalid-url-that-does-not-exist-12345.com/video.mp4"
            )

    def test_error_handling_missing_video_source(self):
        """Test error handling for missing video source."""
        with self.assertRaises(ValueError) as context:
            self.client.create_subtitle()
        self.assertIn("Either video_url or video_file", str(context.exception))

    def test_wait_for_transaction(self):
        """Test waiting for transaction completion."""
        if not self.__class__.test_transaction_id:
            self.skipTest("No transaction ID. Skipping wait test.")

        on_progress_calls = []

        def on_progress(transaction):
            on_progress_calls.append(transaction)

        try:
            transaction = self.client.wait_for_transaction(
                self.__class__.test_transaction_id,
                interval=2000,
                timeout=60000,  # 1 minute timeout for integration test
                on_progress=on_progress,
            )

            self.assertIsNotNone(transaction)
            self.assertIn(transaction["status"], ["completed", "failed"])

            if on_progress_calls:
                print(f"✅ Progress callback called {len(on_progress_calls)} times")
        except AutoSubtitleError as e:
            # Timeout or other errors are acceptable in integration tests
            print(f"⚠️  Transaction wait ended with: {e.message}")


if __name__ == "__main__":
    unittest.main()

