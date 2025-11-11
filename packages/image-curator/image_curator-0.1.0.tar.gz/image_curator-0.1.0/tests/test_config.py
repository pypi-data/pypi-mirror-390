"""
Tests for configuration module.

Verifies that config.py contains all required constants with correct types.
"""


def test_config_imports():
    """Test that config module can be imported."""
    import config

    assert config is not None


def test_config_has_required_constants():
    """Test that all required configuration constants exist."""
    import config

    # Check required constants exist
    assert hasattr(config, "CATEGORIES")
    assert hasattr(config, "NUM_IMAGES")
    assert hasattr(config, "OUTPUT_DIR")
    assert hasattr(config, "SOURCE")
    assert hasattr(config, "API_KEYS")
    assert hasattr(config, "FLICKR_CONFIG")


def test_config_types():
    """Test that configuration values have correct types."""
    import config

    assert isinstance(config.CATEGORIES, list)
    assert isinstance(config.NUM_IMAGES, int)
    assert isinstance(config.OUTPUT_DIR, str)
    assert isinstance(config.SOURCE, str)
    assert isinstance(config.API_KEYS, dict)
    assert isinstance(config.FLICKR_CONFIG, dict)


def test_categories_not_empty():
    """Test that categories list is not empty."""
    import config

    assert len(config.CATEGORIES) > 0
    assert all(isinstance(cat, str) for cat in config.CATEGORIES)


def test_num_images_positive():
    """Test that NUM_IMAGES is a positive integer."""
    import config

    assert config.NUM_IMAGES > 0


def test_api_keys_structure():
    """Test that API_KEYS has expected structure."""
    import config

    assert "flickr" in config.API_KEYS
    assert isinstance(config.API_KEYS["flickr"], str)


def test_flickr_config_structure():
    """Test that FLICKR_CONFIG has expected keys."""
    import config

    assert "license" in config.FLICKR_CONFIG
    assert "safe_search" in config.FLICKR_CONFIG
    assert "content_type" in config.FLICKR_CONFIG

    # Check types
    assert isinstance(config.FLICKR_CONFIG["license"], str)
    assert isinstance(config.FLICKR_CONFIG["safe_search"], int)
    assert isinstance(config.FLICKR_CONFIG["content_type"], int)


def test_flickr_config_valid_values():
    """Test that FLICKR_CONFIG values are valid."""
    import config

    # safe_search should be 1, 2, or 3
    assert config.FLICKR_CONFIG["safe_search"] in [1, 2, 3]

    # content_type should be 1, 2, or 3
    assert config.FLICKR_CONFIG["content_type"] in [1, 2, 3]
