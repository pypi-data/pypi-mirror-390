"""
Tests for Flickr downloader implementation.

Uses mocked responses to test the FlickrDownloader class without
making real API calls.
"""

from unittest.mock import Mock, patch

import pytest
import requests

from image_sources.flickr import FlickrDownloader
from utils import get_api_key, sanitize_filename, validate_license


class TestUtils:
    """Tests for utility functions."""

    def test_sanitize_filename_basic(self):
        """Test basic filename sanitization."""
        assert sanitize_filename("hello world") == "hello_world"
        assert sanitize_filename("test/file") == "testfile"
        assert sanitize_filename("test:file") == "testfile"

    def test_sanitize_filename_unsafe_chars(self):
        """Test removal of unsafe characters."""
        unsafe = 'test<>:"/\\|?*file'
        result = sanitize_filename(unsafe)
        assert "<" not in result
        assert ">" not in result
        assert ":" not in result
        assert '"' not in result
        assert "/" not in result
        assert "\\" not in result
        assert "|" not in result
        assert "?" not in result
        assert "*" not in result

    def test_sanitize_filename_length_limit(self):
        """Test filename length is limited."""
        long_name = "a" * 300
        result = sanitize_filename(long_name)
        assert len(result) <= 200

    def test_sanitize_filename_empty(self):
        """Test handling of empty or whitespace-only input."""
        assert sanitize_filename("") == "image"
        assert sanitize_filename("   ") == "image"
        assert sanitize_filename("...") == "image"

    def test_validate_license_any(self):
        """Test license validation for 'any'."""
        assert validate_license("any") is None
        assert validate_license("ANY") is None
        assert validate_license("Any") is None

    def test_validate_license_numeric(self):
        """Test license validation for numeric values."""
        assert validate_license("4") == "4"
        assert validate_license("5") == "5"
        assert validate_license("0") == "0"

    def test_get_api_key_from_config(self):
        """Test API key retrieval from config."""
        config_keys = {"flickr": "test_key_123"}
        key = get_api_key("flickr", config_keys)
        assert key == "test_key_123"

    def test_get_api_key_missing(self):
        """Test error when API key is missing."""
        config_keys = {"flickr": "your_flickr_api_key_here"}
        with patch("utils.os.getenv", return_value=None):
            with pytest.raises(ValueError, match="No API key found"):
                get_api_key("flickr", config_keys)

    @patch("utils.os.getenv")
    def test_get_api_key_from_env(self, mock_getenv):
        """Test API key retrieval from environment."""
        mock_getenv.return_value = "env_key_456"
        config_keys = {"flickr": "your_flickr_api_key_here"}
        key = get_api_key("flickr", config_keys)
        assert key == "env_key_456"


class TestFlickrDownloader:
    """Tests for FlickrDownloader class."""

    @pytest.fixture
    def downloader(self):
        """Create a FlickrDownloader instance for testing."""
        config = {
            "license": "any",
            "safe_search": 1,
            "content_type": 1,
        }
        return FlickrDownloader(api_key="test_api_key", config=config)

    def test_init(self, downloader):
        """Test FlickrDownloader initialization."""
        assert downloader.api_key == "test_api_key"
        assert downloader.safe_search == 1
        assert downloader.content_type == 1
        assert downloader.license is None  # "any" becomes None

    def test_init_with_numeric_license(self):
        """Test initialization with numeric license."""
        config = {"license": "4"}
        downloader = FlickrDownloader(api_key="test_key", config=config)
        assert downloader.license == "4"

    def test_build_search_params(self, downloader):
        """Test API parameter building."""
        params = downloader._build_search_params("sunsets", 10)

        assert params["method"] == "flickr.photos.search"
        assert params["api_key"] == "test_api_key"
        assert params["text"] == "sunsets"
        assert params["per_page"] == 10
        assert params["format"] == "json"
        assert params["nojsoncallback"] == 1
        assert params["content_type"] == 1
        assert params["safe_search"] == 1
        assert params["media"] == "photos"
        assert params["sort"] == "relevance"
        assert "license" not in params  # "any" license

    def test_build_search_params_with_license(self):
        """Test API parameters with specific license."""
        config = {"license": "4"}
        downloader = FlickrDownloader(api_key="test_key", config=config)
        params = downloader._build_search_params("test", 5)

        assert params["license"] == "4"

    def test_get_photo_url_from_extras(self, downloader):
        """Test photo URL extraction from extras."""
        photo = {
            "id": "12345",
            "url_o": "https://example.com/original.jpg",
            "url_c": "https://example.com/medium.jpg",
        }

        url = downloader._get_photo_url(photo)
        assert url == "https://example.com/original.jpg"

    def test_get_photo_url_fallback(self, downloader):
        """Test photo URL construction fallback."""
        photo = {
            "id": "12345",
            "server": "5678",
            "secret": "abcdef",
        }

        url = downloader._get_photo_url(photo)
        assert url == "https://live.staticflickr.com/5678/12345_abcdef_c.jpg"

    def test_get_photo_url_none(self, downloader):
        """Test photo URL when no data available."""
        photo = {"id": "12345"}
        url = downloader._get_photo_url(photo)
        assert url is None

    @patch("image_sources.flickr.http_get_with_retry")
    def test_search_photos_success(self, mock_http_get, downloader):
        """Test successful photo search."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "stat": "ok",
            "photos": {
                "photo": [
                    {"id": "1", "server": "100", "secret": "abc"},
                    {"id": "2", "server": "200", "secret": "def"},
                ],
                "total": 100,
            },
        }
        mock_http_get.return_value = mock_response

        photos = downloader._search_photos("sunsets", 10)

        assert len(photos) == 2
        assert photos[0]["id"] == "1"
        assert photos[1]["id"] == "2"
        mock_http_get.assert_called_once()

    @patch("image_sources.flickr.http_get_with_retry")
    def test_search_photos_api_error(self, mock_http_get, downloader):
        """Test handling of API errors."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "stat": "fail",
            "message": "Invalid API Key",
        }
        mock_http_get.return_value = mock_response

        with pytest.raises(ValueError, match="Invalid API Key"):
            downloader._search_photos("test", 10)

    @patch("image_sources.flickr.http_get_with_retry")
    def test_search_photos_network_error(self, mock_http_get, downloader):
        """Test handling of network errors."""
        mock_http_get.side_effect = requests.exceptions.RequestException("Network error")

        with pytest.raises(requests.exceptions.RequestException):
            downloader._search_photos("test", 10)

    @patch("image_sources.flickr.download_file")
    @patch("image_sources.flickr.ensure_directory")
    @patch("image_sources.flickr.http_get_with_retry")
    def test_download_success(
        self, mock_http_get, mock_ensure_dir, mock_download_file, downloader, tmp_path
    ):
        """Test successful download workflow."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "stat": "ok",
            "photos": {
                "photo": [
                    {
                        "id": "12345",
                        "server": "5678",
                        "secret": "abcdef",
                        "url_c": "https://example.com/photo1.jpg",
                    },
                    {
                        "id": "23456",
                        "server": "6789",
                        "secret": "ghijkl",
                        "url_c": "https://example.com/photo2.jpg",
                    },
                ],
                "total": 2,
            },
        }
        mock_http_get.return_value = mock_response

        # Mock directory creation
        category_dir = tmp_path / "sunsets"
        mock_ensure_dir.return_value = category_dir

        # Mock successful downloads
        mock_download_file.return_value = True

        # Execute download
        downloader.download("sunsets", 2, str(tmp_path))

        # Verify API was called
        mock_http_get.assert_called_once()

        # Verify directory was created
        mock_ensure_dir.assert_called_once()

        # Verify download_file was called for each photo
        assert mock_download_file.call_count == 2

    @patch("image_sources.flickr.http_get_with_retry")
    def test_download_no_photos(self, mock_http_get, downloader):
        """Test download when no photos are found."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "stat": "ok",
            "photos": {
                "photo": [],
                "total": 0,
            },
        }
        mock_http_get.return_value = mock_response

        # Should not raise an error, just log warning
        downloader.download("nonexistent", 10, "downloads")

    @patch("image_sources.flickr.download_file")
    @patch("image_sources.flickr.ensure_directory")
    @patch("image_sources.flickr.http_get_with_retry")
    def test_download_partial_failure(
        self, mock_http_get, mock_ensure_dir, mock_download_file, downloader, tmp_path
    ):
        """Test download with some failures."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "stat": "ok",
            "photos": {
                "photo": [
                    {"id": "1", "url_c": "https://example.com/photo1.jpg"},
                    {"id": "2", "url_c": "https://example.com/photo2.jpg"},
                ],
                "total": 2,
            },
        }
        mock_http_get.return_value = mock_response

        # Mock directory
        mock_ensure_dir.return_value = tmp_path / "test"

        # First download succeeds, second fails
        mock_download_file.side_effect = [True, False]

        # Should complete without raising exception
        downloader.download("test", 2, str(tmp_path))

        assert mock_download_file.call_count == 2


class TestProviderRegistry:
    """Tests for provider registry."""

    def test_get_provider_class_flickr(self):
        """Test getting Flickr provider class."""
        from image_sources import get_provider_class

        provider_class = get_provider_class("flickr")
        assert provider_class == FlickrDownloader

    def test_get_provider_class_invalid(self):
        """Test error for invalid provider."""
        from image_sources import get_provider_class

        with pytest.raises(ValueError, match="Unsupported source"):
            get_provider_class("invalid_provider")
