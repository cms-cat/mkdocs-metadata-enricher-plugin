"""Pytest fixtures for metadata enricher tests."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def docs_dir(temp_dir):
    """Create a docs directory with sample markdown files."""
    docs_path = os.path.join(temp_dir, "docs")
    os.makedirs(docs_path)

    # Create sample markdown files
    Path(os.path.join(docs_path, "index.md")).write_text("# Welcome\n\nHome page.")
    Path(os.path.join(docs_path, "page1.md")).write_text("# Page 1\n\nTest content.")

    subdir = os.path.join(docs_path, "subfolder")
    os.makedirs(subdir)
    Path(os.path.join(subdir, "page2.md")).write_text("# Page 2\n\nNested page.")

    return docs_path


@pytest.fixture
def site_dir(temp_dir):
    """Create a site directory with search index."""
    site_path = os.path.join(temp_dir, "site")
    search_path = os.path.join(site_path, "search")
    os.makedirs(search_path)

    # Create sample search index
    search_index = {
        "docs": [
            {
                "location": "/",
                "title": "Home",
                "text": "Welcome home",
            },
            {
                "location": "/page1/",
                "title": "Page 1",
                "text": "Page 1 content",
            },
            {
                "location": "/subfolder/page2/",
                "title": "Page 2",
                "text": "Page 2 content",
            },
        ],
        "config": {
            "lang": "en",
            "prebuild_index": False,
        },
    }

    search_index_path = os.path.join(search_path, "search_index.json")
    with open(search_index_path, "w") as f:
        json.dump(search_index, f)

    return site_path


@pytest.fixture
def mkdocs_config(docs_dir, site_dir):
    """Create a mkdocs config dict with real paths."""
    return {
        "docs_dir": docs_dir,
        "site_dir": site_dir,
    }


@pytest.fixture
def mock_page():
    """Create a mock page object."""
    page = MagicMock()
    page.meta = {}
    page.file = MagicMock()
    page.file.src_path = "index.md"
    page.update_date = None
    return page


@pytest.fixture
def plugin():
    """Create a metadata enricher plugin instance with initialized config."""
    from mkdocs_metadata_enricher.plugin import MetadataEnricherPlugin

    plugin = MetadataEnricherPlugin()
    # Initialize config with defaults
    plugin.config = {
        "enrich_sitemap": True,
        "enrich_search": True,
        "search_date_type": "iso_date",
        "search_custom_format": "%d. %B %Y",
        "search_timezone": "UTC",
        "search_locale": "en",
    }
    return plugin
