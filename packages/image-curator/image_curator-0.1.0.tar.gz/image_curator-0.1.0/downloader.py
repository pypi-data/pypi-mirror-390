"""
Main downloader dispatcher module.

This module provides the central download_images function that dispatches
download requests to appropriate provider implementations.
"""

import logging
from typing import Dict, List, Optional

from image_sources import get_provider_class
from utils import get_api_key

logger = logging.getLogger(__name__)


def download_images(
    categories: List[str],
    num_images: int,
    output_dir: str,
    source: str,
    api_keys: Dict[str, str],
    extra_config: Optional[Dict] = None,
) -> None:
    """
    Download images for multiple categories using the specified source.

    This function dispatches to the appropriate provider implementation
    based on the source parameter.

    Args:
        categories: List of category/query strings to download images for
        num_images: Number of images to download per category
        output_dir: Base directory for saving downloaded images
        source: Image source provider name (e.g., "flickr")
        api_keys: Dictionary of API keys from config
        extra_config: Optional provider-specific configuration

    Raises:
        ValueError: If source is not supported or API key is missing
    """
    logger.info(
        f"Starting download session: {len(categories)} categories, "
        f"{num_images} images each, source={source}"
    )

    try:
        # Get API key for the source
        api_key = get_api_key(source, api_keys)

        # Get provider class and instantiate
        provider_class = get_provider_class(source)
        downloader = provider_class(api_key, extra_config)

        logger.info(f"Initialized {source} downloader")

        # Download for each category
        for category in categories:
            logger.info(f"Processing category: {category}")
            try:
                downloader.download(category, num_images, output_dir)
            except Exception as e:
                logger.error(
                    f"Failed to download images for category '{category}': {e}",
                    exc_info=True,
                )
                # Continue with next category instead of failing entirely

        logger.info("Download session completed")

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during download session: {e}", exc_info=True)
        raise
