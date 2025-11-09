"""AutoSubtitle API Client."""

import time
from typing import Optional, Dict, Any, Callable, BinaryIO, Union
import requests
from .errors import AutoSubtitleError

DEFAULT_BASE_URL = "https://api.autosubtitle.net"


class AutoSubtitleClient:
    """Client for interacting with the AutoSubtitle API."""

    def __init__(self, api_key: str, base_url: str = DEFAULT_BASE_URL):
        """
        Initialize the AutoSubtitle client.

        Args:
            api_key: Your AutoSubtitle API key
            base_url: Base URL for the API (default: https://api.autosubtitle.net)
        """
        if not api_key:
            raise ValueError("API key is required")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request data (for form data)
            files: Files to upload (for multipart/form-data)

        Returns:
            JSON response as dictionary

        Raises:
            AutoSubtitleError: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
        headers = {"X-API-Key": self.api_key}

        try:
            if files:
                response = requests.request(
                    method, url, headers=headers, data=data, files=files, timeout=300
                )
            else:
                response = requests.request(
                    method, url, headers=headers, json=data, timeout=60
                )
        except requests.exceptions.RequestException as e:
            raise AutoSubtitleError(f"Network error: {str(e)}") from e

        if not response.ok:
            try:
                error_data = response.json()
                error_message = error_data.get(
                    "message", f"HTTP {response.status_code}: {response.reason}"
                )
                error_code = error_data.get("code")
            except ValueError:
                error_message = f"HTTP {response.status_code}: {response.reason}"
                error_code = None

            raise AutoSubtitleError(
                error_message, status=response.status_code, code=error_code
            )

        return response.json()

    def create_subtitle(
        self,
        video_url: Optional[str] = None,
        video_file: Optional[Union[BinaryIO, bytes]] = None,
        language: Optional[str] = None,
        font_name: Optional[str] = None,
        font_size: Optional[int] = None,
        font_weight: Optional[str] = None,
        font_color: Optional[str] = None,
        highlight_color: Optional[str] = None,
        stroke_width: Optional[int] = None,
        stroke_color: Optional[str] = None,
        background_color: Optional[str] = None,
        background_opacity: Optional[float] = None,
        position: Optional[str] = None,
        y_offset: Optional[int] = None,
        words_per_subtitle: Optional[int] = None,
        enable_animation: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Create a subtitle generation job.

        Args:
            video_url: URL of the video to process
            video_file: Video file (file object or bytes)
            language: Subtitle language (e.g., 'en', 'tr')
            font_name: Font name (e.g., 'Montserrat')
            font_size: Font size (20-200)
            font_weight: Font weight ('normal', 'bold', 'light')
            font_color: Font color (hex code)
            highlight_color: Highlight color (hex code)
            stroke_width: Stroke width
            stroke_color: Stroke color (hex code)
            background_color: Background color (hex code)
            background_opacity: Background opacity (0.0-1.0)
            position: Position ('top', 'center', 'bottom')
            y_offset: Y-axis offset
            words_per_subtitle: Words per subtitle
            enable_animation: Enable animation

        Returns:
            Response with transaction details

        Raises:
            AutoSubtitleError: If the request fails
            ValueError: If neither video_url nor video_file is provided
        """
        if not video_url and not video_file:
            raise ValueError("Either video_url or video_file must be provided")

        data = {}
        files = None

        if video_url:
            data["upload_method"] = "url"
            data["video_url"] = video_url
        elif video_file:
            data["upload_method"] = "file"
            if isinstance(video_file, bytes):
                files = {"video": ("video.mp4", video_file, "video/mp4")}
            else:
                files = {"video": video_file}

        # Add subtitle options
        if language:
            data["language"] = language
        if font_name:
            data["font_name"] = font_name
        if font_size is not None:
            data["font_size"] = str(font_size)
        if font_weight:
            data["font_weight"] = font_weight
        if font_color:
            data["font_color"] = font_color
        if highlight_color:
            data["highlight_color"] = highlight_color
        if stroke_width is not None:
            data["stroke_width"] = str(stroke_width)
        if stroke_color:
            data["stroke_color"] = stroke_color
        if background_color:
            data["background_color"] = background_color
        if background_opacity is not None:
            data["background_opacity"] = str(background_opacity)
        if position:
            data["position"] = position
        if y_offset is not None:
            data["y_offset"] = str(y_offset)
        if words_per_subtitle is not None:
            data["words_per_subtitle"] = str(words_per_subtitle)
        if enable_animation is not None:
            data["enable_animation"] = str(enable_animation)

        return self._request("POST", "/api/subtitles", data=data, files=files)

    def get_transactions(self) -> Dict[str, Any]:
        """
        Get all subtitle transactions.

        Returns:
            Response with list of transactions

        Raises:
            AutoSubtitleError: If the request fails
        """
        return self._request("GET", "/api/subtitles")

    def get_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """
        Get a specific transaction by ID.

        Args:
            transaction_id: Transaction ID

        Returns:
            Response with transaction details

        Raises:
            AutoSubtitleError: If the request fails
            ValueError: If transaction_id is not provided
        """
        if not transaction_id:
            raise ValueError("Transaction ID is required")
        return self._request("GET", f"/api/subtitles/{transaction_id}")

    def get_billing_summary(self) -> Dict[str, Any]:
        """
        Get billing summary and usage information.

        Returns:
            Response with billing summary

        Raises:
            AutoSubtitleError: If the request fails
        """
        return self._request("GET", "/api/billing/summary")

    def wait_for_transaction(
        self,
        transaction_id: str,
        interval: int = 2000,
        timeout: int = 300000,
        on_progress: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> Dict[str, Any]:
        """
        Wait for a transaction to complete.

        Args:
            transaction_id: Transaction ID to wait for
            interval: Polling interval in milliseconds (default: 2000)
            timeout: Maximum wait time in milliseconds (default: 300000 = 5 minutes)
            on_progress: Callback function called on each poll with transaction data

        Returns:
            Completed transaction

        Raises:
            AutoSubtitleError: If the transaction fails or times out
        """
        start_time = time.time() * 1000  # Convert to milliseconds
        interval_seconds = interval / 1000  # Convert to seconds

        while True:
            response = self.get_transaction(transaction_id)
            transaction = response.get("transaction", {})

            if on_progress:
                on_progress(transaction)

            status = transaction.get("status")
            if status == "completed":
                return transaction

            if status == "failed":
                error_message = transaction.get("error_message", "Transaction failed")
                raise AutoSubtitleError(error_message, status=500)

            elapsed = (time.time() * 1000) - start_time
            if elapsed > timeout:
                raise AutoSubtitleError(
                    "Transaction timeout: exceeded maximum wait time", status=408
                )

            time.sleep(interval_seconds)

