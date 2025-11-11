"""
Flickr image downloader implementation.

This module provides the FlickrDownloader class for downloading images
from Flickr using their REST API with configurable search parameters.
"""

import logging
from typing import Dict, List, Optional

import requests
from tqdm import tqdm

from utils import (
    download_file,
    ensure_directory,
    http_get_with_retry,
    sanitize_filename,
    validate_license,
)

logger = logging.getLogger(__name__)


class FlickrDownloader:
    """
    Download images from Flickr using the REST API.

    This class handles searching for photos on Flickr and downloading them
    to local storage with proper error handling and rate limiting.
    """

    BASE_URL = "https://www.flickr.com/services/rest/"

    def __init__(self, api_key: str, config: Optional[Dict] = None):
        """
        Initialize the Flickr downloader.

        Args:
            api_key: Flickr API key
            config: Optional configuration dictionary with Flickr-specific settings
        """
        self.api_key = api_key
        self.config = config or {}
        self.license = validate_license(self.config.get("license", "any"))
        self.safe_search = self.config.get("safe_search", 1)
        self.content_type = self.config.get("content_type", 1)

        logger.debug(
            f"Initialized FlickrDownloader with safe_search={self.safe_search}, "
            f"content_type={self.content_type}, license={self.license}"
        )

    def _build_search_params(self, query: str, per_page: int) -> Dict:
        """
        Build API parameters for photo search.

        Args:
            query: Search query string
            per_page: Number of results per page

        Returns:
            Dictionary of API parameters
        """
        params = {
            "method": "flickr.photos.search",
            "api_key": self.api_key,
            "text": query,
            "per_page": per_page,
            "format": "json",
            "nojsoncallback": 1,
            "content_type": self.content_type,
            "safe_search": self.safe_search,
            "media": "photos",
            "sort": "relevance",
            "extras": "url_c,url_o,url_l,url_m",  # Request various size URLs
        }

        # Only add license filter if not "any"
        if self.license is not None:
            params["license"] = self.license

        return params

    def _search_photos(self, query: str, num_images: int) -> List[Dict]:
        """
        Search for photos on Flickr.

        Args:
            query: Search query string
            num_images: Number of images to retrieve

        Returns:
            List of photo dictionaries from API response

        Raises:
            requests.exceptions.RequestException: If API request fails
            ValueError: If API returns an error response
        """
        params = self._build_search_params(query, num_images)

        try:
            response = http_get_with_retry(self.BASE_URL, params=params)
            data = response.json()

            if data.get("stat") != "ok":
                error_msg = data.get("message", "Unknown error")
                raise ValueError(f"Flickr API error: {error_msg}")

            photos = data.get("photos", {}).get("photo", [])
            total = data.get("photos", {}).get("total", 0)

            logger.info(
                f"Found {len(photos)} photos for query '{query}' " f"(total available: {total})"
            )

            return photos

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to search Flickr for '{query}': {e}")
            raise
        except (ValueError, KeyError) as e:
            logger.error(f"Failed to parse Flickr response for '{query}': {e}")
            raise

    def _get_photo_url(self, photo: Dict) -> Optional[str]:
        """
        Extract the best available photo URL from photo data.

        Tries to get the largest available size, falling back to smaller sizes.

        Args:
            photo: Photo dictionary from Flickr API

        Returns:
            URL string or None if no URL available
        """
        # Try different sizes in order of preference
        for url_key in ["url_o", "url_l", "url_c", "url_m"]:
            if url_key in photo and photo[url_key]:
                return photo[url_key]

        # Fallback: construct URL from photo info
        # https://live.staticflickr.com/{server-id}/{id}_{secret}_c.jpg
        try:
            server = photo.get("server")
            photo_id = photo.get("id")
            secret = photo.get("secret")

            if server and photo_id and secret:
                # Use 'c' size (800px) as default
                url = f"https://live.staticflickr.com/{server}/{photo_id}_{secret}_c.jpg"
                logger.debug(f"Constructed fallback URL for photo {photo_id}")
                return url
        except (KeyError, TypeError) as e:
            logger.warning(f"Could not construct photo URL: {e}")

        return None

    def download(self, query: str, num_images: int, output_dir: str) -> None:
        """
        Download images for a given query.

        Args:
            query: Search query string (category name)
            num_images: Number of images to download
            output_dir: Base output directory path
        """
        logger.info(f"Starting download for category '{query}' ({num_images} images)")

        try:
            # Search for photos
            photos = self._search_photos(query, num_images)

            if not photos:
                logger.warning(f"No photos found for query '{query}'")
                return

            # Create category subdirectory
            sanitized_query = sanitize_filename(query)
            category_dir = ensure_directory(f"{output_dir}/{sanitized_query}")

            # Download photos with progress bar
            successful = 0
            failed = 0

            with tqdm(total=len(photos), desc=f"Downloading {query}", unit="image") as pbar:
                for index, photo in enumerate(photos, start=1):
                    photo_url = self._get_photo_url(photo)

                    if not photo_url:
                        logger.warning(f"No URL available for photo {photo.get('id', 'unknown')}")
                        failed += 1
                        pbar.update(1)
                        continue

                    # Build filename: category_index__photoid.jpg
                    photo_id = photo.get("id", f"unknown_{index}")
                    extension = photo_url.split(".")[-1].split("?")[0]  # Handle query params
                    if extension not in ["jpg", "jpeg", "png", "gif"]:
                        extension = "jpg"

                    filename = f"{sanitized_query}_{index:03d}__{photo_id}.{extension}"
                    output_path = category_dir / filename

                    # Skip if file already exists
                    if output_path.exists():
                        logger.debug(f"Skipping existing file: {filename}")
                        successful += 1
                        pbar.update(1)
                        continue

                    # Download the image
                    if download_file(photo_url, output_path):
                        successful += 1
                    else:
                        failed += 1

                    pbar.update(1)

            logger.info(f"Completed '{query}': {successful} successful, {failed} failed")

        except (requests.exceptions.RequestException, ValueError) as e:
            logger.error(f"Download failed for category '{query}': {e}")
        except Exception as e:
            logger.error(f"Unexpected error downloading '{query}': {e}", exc_info=True)
