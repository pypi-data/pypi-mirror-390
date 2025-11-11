# Image Curator

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/ghostcipher1/image-curator/workflows/CI/badge.svg)](https://github.com/ghostcipher1/image-curator/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/image-curator.svg)](https://badge.fury.io/py/image-curator)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A production-ready, modular Python application for curating and downloading images from multiple sources based on configurable category searches. Currently supports **Flickr** with an extensible plugin architecture designed for easy addition of new image sources.

> **💡 Note on Flickr API:** As of 2024, Flickr API requires a paid Pro subscription. We're planning to add support for free alternatives like **Unsplash** and **Pexels** soon. Contributions welcome!

## Features

- **Multi-source support**: Currently supports Flickr, easily extensible to other platforms
- **Category-based downloads**: Define categories in config and download images for each
- **Smart filtering**: Control license type, safe search, and content type
- **Progress tracking**: Real-time progress bars with tqdm
- **Robust error handling**: Automatic retries with exponential backoff
- **Clean file organization**: Images saved in per-category subdirectories with sanitized names
- **Flexible configuration**: Override settings via CLI or config file
- **Plugin architecture**: Add new image sources without modifying core code
- **Production-quality**: Type hints, comprehensive logging, and full test coverage

## Project Structure

```
image-curator/
├── config.py                 # User configuration
├── downloader.py            # Main dispatcher logic
├── image_sources/           # Provider plugins
│   ├── __init__.py         # Provider registry
│   └── flickr.py           # Flickr implementation
├── utils.py                # Helper functions
├── main.py                 # CLI entry point
├── requirements.txt        # Dependencies
├── README.md              # This file
├── LICENSE                # MIT License
└── tests/                 # Test suite
    ├── test_config.py
    ├── test_flickr_downloader.py
    └── __init__.py
```

## Requirements

- Python 3.8 or higher
- Flickr API key (**Note:** As of 2024, Flickr API requires a paid subscription - see setup details below)

## Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install image-curator
```

### Option 2: Install from Source

#### 1. Clone the repository

```bash
git clone https://github.com/ghostcipher1/image-curator.git
cd image-curator
```

#### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

#### 3. Install dependencies

```bash
pip install -r requirements.txt
# Or install in development mode
pip install -e .
```

## Configuration

### Get a Flickr API Key

**Important:** As of 2024, Flickr API access requires a paid Flickr Pro subscription ($8.25/month or $71.99/year).

1. **Subscribe to Flickr Pro:** Visit [Flickr Pro](https://www.flickr.com/account/upgrade/pro) and subscribe
2. **Request API Key:** Go to [Flickr App Garden](https://www.flickr.com/services/apps/create/)
3. Click "Request an API Key"
4. Choose "Apply for a Non-Commercial Key" (for personal use) or "Commercial Key" (for business use)
5. Fill out the form:
   - App name: "Image Curator"
   - App description: "Personal image collection and curation tool"
6. Copy your **API Key** (you don't need the secret for this application)

### Configure Your API Key

**Option A: Edit config.py** (recommended for personal use)

```python
API_KEYS = {
    "flickr": "your_actual_flickr_api_key_here"
}
```

**Option B: Use environment variable** (recommended for production)

Create a `.env` file in the project root:

```bash
FLICKR_API_KEY=your_actual_flickr_api_key_here
```

Or export it in your shell:

```bash
export FLICKR_API_KEY=your_actual_flickr_api_key_here
```

## Configuration

Edit [config.py](config.py) to customize your downloads:

```python
# Categories to download images for
CATEGORIES = ["sunsets", "mountains", "wildlife"]

# Number of images to download per category
NUM_IMAGES = 10

# Output directory for downloaded images
OUTPUT_DIR = "downloads"

# Which provider to use
SOURCE = "flickr"

# Flickr-specific options
FLICKR_CONFIG = {
    "license": "any",      # License filter (see below)
    "safe_search": 1,      # 1=safe, 2=moderate, 3=restricted
    "content_type": 1      # 1=photos, 2=screenshots, 3=other
}
```

### Flickr License Options

The `license` parameter filters results by license type:

- `"any"` - All licenses (default)
- `"0"` - All Rights Reserved
- `"4"` - Attribution License (CC BY)
- `"5"` - Attribution-ShareAlike License (CC BY-SA)
- `"6"` - Attribution-NoDerivs License (CC BY-ND)
- `"7"` - No known copyright restrictions
- `"8"` - United States Government Work
- `"9"` - Public Domain Dedication (CC0)
- `"10"` - Public Domain Mark

For Creative Commons images suitable for reuse, consider licenses `4`, `5`, `6`, `9`, or `10`.

## Usage

### Basic usage (uses config.py settings)

```bash
python main.py
```

### Download specific number of images

```bash
python main.py --limit 20
```

### Override categories

```bash
python main.py --categories "cats,dogs,birds"
```

### Specify output directory

```bash
python main.py --out my_images
```

### Filter by Creative Commons license

```bash
python main.py --license 4
```

### Combined options

```bash
python main.py --categories "nature,landscapes" --limit 15 --safe_search 1 --license any
```

### Enable verbose logging

```bash
python main.py --verbose
```

### Full CLI options

```
usage: main.py [-h] [--source SOURCE] [--limit LIMIT] [--out OUT]
               [--categories CATEGORIES] [--safe_search {1,2,3}]
               [--license LICENSE] [--content_type {1,2,3}] [--verbose]

Options:
  --source SOURCE            Image source to use (default: flickr)
  --limit LIMIT             Number of images per category (default: 10)
  --out OUT                 Output directory (default: downloads)
  --categories CATEGORIES   Comma-separated categories
  --safe_search {1,2,3}     Flickr safe search level
  --license LICENSE         Flickr license filter (e.g., '4', '5', 'any')
  --content_type {1,2,3}    Flickr content type: 1=photos, 2=screenshots, 3=other
  --verbose, -v             Enable verbose logging (DEBUG level)
```

## Output Structure

Images are organized in subdirectories by category:

```
downloads/
├── sunsets/
│   ├── sunsets_001__12345678.jpg
│   ├── sunsets_002__23456789.jpg
│   └── ...
├── mountains/
│   ├── mountains_001__34567890.jpg
│   └── ...
└── wildlife/
    └── ...
```

Filename format: `{category}_{index}__{photo_id}.{ext}`

## Testing

Run the test suite:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=. --cov-report=html
```

Run specific test file:

```bash
pytest tests/test_flickr_downloader.py -v
```

Tests use mocked API responses and do not make real network calls.

## Important Legal & Ethical Notes

### Respect Flickr's Terms of Service

- This tool uses the official Flickr API
- Follow [Flickr's API Terms of Use](https://www.flickr.com/services/api/tos/)
- Respect rate limits (3600 queries per hour per API key)
- Do not use this tool for scraping or bulk downloading beyond reasonable personal use

### Check Image Licenses

- **Always check the license** before using downloaded images
- Creative Commons licenses have specific requirements (attribution, etc.)
- "All Rights Reserved" means you cannot use the image without permission
- This tool downloads images but **does not grant you usage rights**
- See [Creative Commons License Types](https://creativecommons.org/licenses/) for details

### Respect Photographers

- Give proper attribution when required by license
- Consider donating or purchasing prints from photographers whose work you use
- Do not claim others' work as your own

## Extensibility

The architecture is designed to support multiple image sources. To add a new provider:

1. Create `image_sources/new_provider.py`
2. Implement a class with `__init__(api_key, config)` and `download(query, num_images, output_dir)`
3. Register in `image_sources/__init__.py` PROVIDERS dict
4. Add provider-specific config to [config.py](config.py)

Example skeleton:

```python
# image_sources/new_provider.py
class NewProviderDownloader:
    def __init__(self, api_key: str, config: dict = None):
        self.api_key = api_key
        self.config = config or {}

    def download(self, query: str, num_images: int, output_dir: str) -> None:
        # Implement search and download logic
        pass
```

## Troubleshooting

### "No API key found for flickr"

- Ensure you've set your API key in [config.py](config.py) or as environment variable `FLICKR_API_KEY`

### "Flickr API error: Invalid API Key"

- Check that your API key is correct and active
- Verify it's not expired on [Flickr App Garden](https://www.flickr.com/services/api/keys/)

### "No photos found for query"

- Try different search terms
- Adjust license/safe_search filters (some combinations return fewer results)
- Check Flickr.com directly to verify photos exist for your query

### Rate limit errors

- Flickr allows 3600 API calls per hour
- Reduce `NUM_IMAGES` or wait before retrying

### Connection/timeout errors

- Check your internet connection
- Increase timeout in [utils.py](utils.py) `http_get_with_retry` function
- Retry the download (tool automatically retries with backoff)

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for new functionality
4. Ensure all tests pass (`pytest`)
5. Follow PEP 8 style guidelines
6. Commit with clear messages
7. Push to your branch
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Flickr API](https://www.flickr.com/services/api/) for providing free access to their photo database
- All photographers who share their work on Flickr

## Disclaimer

This tool is provided as-is for educational and personal use. Users are responsible for:
- Complying with Flickr's Terms of Service
- Respecting image licenses and copyright
- Obtaining necessary permissions for commercial use
- Proper attribution where required

The authors assume no liability for misuse of downloaded images.
