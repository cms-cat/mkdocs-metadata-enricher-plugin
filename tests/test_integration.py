"""Integration tests for metadata enricher plugin."""

import json
import os
import subprocess
import tempfile
from pathlib import Path

import pytest


@pytest.mark.integration
class TestIntegration:
    """Integration tests with actual mkdocs build."""

    def test_basic_mkdocs_build(self):
        """Test plugin with a minimal mkdocs build."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize git repo for git history
            subprocess.run(
                ["git", "init"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )

            # Create minimal mkdocs project
            docs_dir = os.path.join(tmpdir, "docs")
            os.makedirs(docs_dir)

            # Create markdown files
            Path(os.path.join(docs_dir, "index.md")).write_text(
                """# Home

Welcome to the test site.
"""
            )
            Path(os.path.join(docs_dir, "about.md")).write_text(
                """# About

This is the about page.
"""
            )

            # Commit files to git
            subprocess.run(
                ["git", "add", "."],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "commit", "-m", "Initial commit"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )

            # Create mkdocs.yml
            mkdocs_yml = os.path.join(tmpdir, "mkdocs.yml")
            Path(mkdocs_yml).write_text(
                """site_name: Test Site
site_url: https://example.com/
docs_dir: docs
site_dir: site

plugins:
  - search
  - git-revision-date-localized:
      type: iso_date
      enable_creation_date: false
  - metadata-enricher:
      enrich_sitemap: true
      enrich_search: true
      search_date_type: iso_date
"""
            )

            # Run mkdocs build
            result = subprocess.run(
                ["mkdocs", "build"],
                cwd=tmpdir,
                capture_output=True,
                text=True,
            )

            # Verify build succeeded
            assert result.returncode == 0, f"Build failed: {result.stderr}"

            # Verify search index was enriched
            search_index_path = os.path.join(tmpdir, "site", "search", "search_index.json")
            assert os.path.exists(search_index_path), "search_index.json not found"

            with open(search_index_path) as f:
                index = json.load(f)

            # Check that dates were added
            for doc in index.get("docs", []):
                # Should have last_updated field
                assert "last_updated" in doc, f"Missing last_updated in {doc}"

            # Verify sitemap exists
            sitemap_path = os.path.join(tmpdir, "site", "sitemap.xml")
            assert os.path.exists(sitemap_path), "sitemap.xml not found"

            # Verify sitemap contains lastmod dates
            with open(sitemap_path) as f:
                sitemap_content = f.read()
                assert "<lastmod>" in sitemap_content, "No lastmod in sitemap"
