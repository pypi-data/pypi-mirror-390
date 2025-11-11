"""
Utility functions for the image downloader.

Provides helpers for API key loading, filename sanitization, directory
management, and HTTP requests with retry logic.
"""

import logging
import os
import re
from pathlib import Path
from typing import Dict, Optional

import requests
from dotenv import load_dotenv
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

# Load environment variables from .env file if present
load_dotenv()

logger = logging.getLogger(__name__)


def get_api_key(source: str, config_keys: Dict[str, str]) -> str:
    """
    Get API key for a given source from config or environment.

    Tries config.API_KEYS first, then falls back to environment variables.

    Args:
        source: The name of the image source (e.g., "flickr")
        config_keys: Dictionary of API keys from config.py

    Returns:
        The API key as a string

    Raises:
        ValueError: If no API key is found in config or environment
    """
    # First try config
    key = config_keys.get(source)
    if key and key != f"your_{source}_api_key_here":
        return key

    # Fallback to environment variable
    env_var = f"{source.upper()}_API_KEY"
    key = os.getenv(env_var)
    if key:
        logger.info(f"Using {source} API key from environment variable {env_var}")
        return key

    raise ValueError(
        f"No API key found for {source}. Please set it in config.py "
        f"or as environment variable {env_var}"
    )


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a string to be safe for use as a filename.

    Removes or replaces characters that are not safe for filesystems.

    Args:
        filename: The original filename string

    Returns:
        A sanitized filename safe for all common filesystems
    """
    # First strip to check if we have actual content
    filename = filename.strip()
    if not filename or filename == ".":
        return "image"

    # Replace spaces with underscores
    filename = filename.replace(" ", "_")
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', "", filename)
    # Remove leading/trailing dots and whitespace
    filename = filename.strip(". ")
    # Limit length to 200 characters (leaving room for extensions)
    filename = filename[:200]
    # Ensure we have something left
    return filename if filename else "image"


def ensure_directory(path: str) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Path to the directory

    Returns:
        Path object for the directory

    Raises:
        OSError: If directory creation fails
    """
    dir_path = Path(path)
    try:
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory exists: {dir_path}")
        return dir_path
    except OSError as e:
        logger.error(f"Failed to create directory {dir_path}: {e}")
        raise


def validate_license(license_value: str) -> Optional[str]:
    """
    Validate and process license filter value.

    Args:
        license_value: License string from config ("any" or numeric string)

    Returns:
        None if "any", otherwise the original value for API parameter
    """
    if license_value.lower() == "any":
        return None
    return license_value


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((requests.exceptions.RequestException,)),
    reraise=True,
)
def http_get_with_retry(
    url: str, params: Optional[Dict] = None, timeout: int = 30
) -> requests.Response:
    """
    Perform HTTP GET request with automatic retry and exponential backoff.

    Args:
        url: The URL to fetch
        params: Optional query parameters
        timeout: Request timeout in seconds

    Returns:
        Response object

    Raises:
        requests.exceptions.RequestException: If all retry attempts fail
    """
    try:
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as e:
        logger.warning(f"HTTP error {e.response.status_code} for {url}: {e}")
        raise
    except requests.exceptions.RequestException as e:
        logger.warning(f"Request failed for {url}: {e}")
        raise


def download_file(url: str, output_path: Path) -> bool:
    """
    Download a file from a URL to a local path.

    Args:
        url: URL of the file to download
        output_path: Path where the file should be saved

    Returns:
        True if download succeeded, False otherwise
    """
    try:
        response = http_get_with_retry(url, timeout=60)
        with open(output_path, "wb") as f:
            f.write(response.content)
        logger.debug(f"Downloaded: {output_path.name}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download {url}: {e}")
        return False
    except OSError as e:
        logger.error(f"Failed to write file {output_path}: {e}")
        return False
