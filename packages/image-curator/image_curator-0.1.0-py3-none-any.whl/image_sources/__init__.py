"""
Image source providers package.

This package contains modules for different image source providers.
Each provider implements a downloader class with a common interface.
"""

from typing import Dict, Type

# Provider registry for future extensibility
PROVIDERS: Dict[str, str] = {
    "flickr": "image_sources.flickr.FlickrDownloader",
}


def get_provider_class(source: str) -> Type:
    """
    Get the provider class for a given source.

    Args:
        source: Name of the image source provider

    Returns:
        The provider class

    Raises:
        ValueError: If the source is not supported
    """
    if source not in PROVIDERS:
        raise ValueError(
            f"Unsupported source: {source}. Available sources: {list(PROVIDERS.keys())}"
        )

    module_path, class_name = PROVIDERS[source].rsplit(".", 1)
    module = __import__(module_path, fromlist=[class_name])
    return getattr(module, class_name)


__all__ = ["PROVIDERS", "get_provider_class"]
