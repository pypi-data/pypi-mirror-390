"""
Main entry point for the Flickr image downloader CLI.

This module provides a command-line interface for downloading images
with configurable options that can override config.py defaults.
"""

import argparse
import logging
import sys
from typing import List

import config
from downloader import download_images


def setup_logging(level: int = logging.INFO) -> None:
    """
    Configure logging for the application.

    Args:
        level: Logging level (default: INFO)
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Download images from Flickr based on category searches",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py
  python main.py --source flickr --limit 10
  python main.py --categories "sunsets,mountains,wildlife"
  python main.py --limit 5 --out my_images --safe_search 1
  python main.py --license 4 --content_type 1
        """,
    )

    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help=f"Image source to use (default: {config.SOURCE})",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help=f"Number of images per category (default: {config.NUM_IMAGES})",
    )

    parser.add_argument(
        "--out",
        type=str,
        default=None,
        help=f"Output directory (default: {config.OUTPUT_DIR})",
    )

    parser.add_argument(
        "--categories",
        type=str,
        default=None,
        help=f"Comma-separated categories (default: {','.join(config.CATEGORIES)})",
    )

    parser.add_argument(
        "--safe_search",
        type=int,
        choices=[1, 2, 3],
        default=None,
        help=f"Flickr safe search level: 1=safe, 2=moderate, 3=restricted "
        f"(default: {config.FLICKR_CONFIG.get('safe_search', 1)})",
    )

    parser.add_argument(
        "--license",
        type=str,
        default=None,
        help=f"Flickr license filter (e.g., '4', '5', 'any') "
        f"(default: {config.FLICKR_CONFIG.get('license', 'any')})",
    )

    parser.add_argument(
        "--content_type",
        type=int,
        choices=[1, 2, 3],
        default=None,
        help=f"Flickr content type: 1=photos, 2=screenshots, 3=other "
        f"(default: {config.FLICKR_CONFIG.get('content_type', 1)})",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging (DEBUG level)",
    )

    return parser.parse_args()


def parse_categories(categories_str: str) -> List[str]:
    """
    Parse comma-separated categories string into list.

    Args:
        categories_str: Comma-separated string of categories

    Returns:
        List of category strings
    """
    return [cat.strip() for cat in categories_str.split(",") if cat.strip()]


def main() -> None:
    """
    Main entry point for the CLI application.
    """
    args = parse_arguments()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level)

    logger = logging.getLogger(__name__)
    logger.info("Flickr Image Downloader started")

    # Load config with CLI overrides
    source = args.source if args.source is not None else config.SOURCE
    num_images = args.limit if args.limit is not None else config.NUM_IMAGES
    output_dir = args.out if args.out is not None else config.OUTPUT_DIR
    categories = (
        parse_categories(args.categories) if args.categories is not None else config.CATEGORIES
    )

    # Build provider-specific config with CLI overrides
    flickr_config = config.FLICKR_CONFIG.copy()
    if args.safe_search is not None:
        flickr_config["safe_search"] = args.safe_search
    if args.license is not None:
        flickr_config["license"] = args.license
    if args.content_type is not None:
        flickr_config["content_type"] = args.content_type

    # Select appropriate provider config
    provider_config = flickr_config if source == "flickr" else {}

    # Log configuration
    logger.info("Configuration:")
    logger.info("  Source: %s", source)
    logger.info("  Categories: %s", categories)
    logger.info("  Images per category: %s", num_images)
    logger.info("  Output directory: %s", output_dir)
    if source == "flickr":
        logger.info("  Flickr safe_search: %s", flickr_config.get("safe_search"))
        logger.info("  Flickr license: %s", flickr_config.get("license"))
        logger.info("  Flickr content_type: %s", flickr_config.get("content_type"))

    try:
        # Start download
        download_images(
            categories=categories,
            num_images=num_images,
            output_dir=output_dir,
            source=source,
            api_keys=config.API_KEYS,
            extra_config=provider_config,
        )

        logger.info("All downloads completed successfully")

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.warning("Download interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
