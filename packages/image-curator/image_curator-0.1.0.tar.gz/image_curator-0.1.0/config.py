"""
Configuration file for the Flickr image downloader.

This module contains all user-configurable settings including categories,
output directories, API keys, and provider-specific options.
"""

# Categories to download images for
CATEGORIES = ["sunsets", "mountains", "wildlife"]

# Number of images to download per category
NUM_IMAGES = 10

# Output directory for downloaded images
OUTPUT_DIR = "downloads"

# Which provider to use now
SOURCE = "flickr"

# API keys (primary) with optional .env fallback
API_KEYS = {"flickr": "your_flickr_api_key_here"}

# Flickr-specific configuration options
FLICKR_CONFIG = {
    "license": "any",  # e.g. "4", "5", "any" for all licenses
    "safe_search": 1,  # 1 = safe, 2 = moderate, 3 = restricted
    "content_type": 1,  # 1 = photos only, 2 = screenshots, 3 = other
}
