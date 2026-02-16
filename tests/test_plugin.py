"""Unit tests for metadata enricher plugin."""

import json
import os
import subprocess
from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest

from mkdocs_metadata_enricher_plugin.plugin import MetadataEnricherPlugin


@pytest.mark.unit
class TestPluginConfig:
    """Test plugin configuration."""

    def test_default_config(self, plugin):
        """Test default configuration values."""
        assert plugin.config["enrich_sitemap"] is True
        assert plugin.config["enrich_search"] is True
        assert plugin.config["search_date_type"] == "iso_date"
        assert plugin.config["search_timezone"] == "UTC"
        assert plugin.config["search_locale"] == "en"

    def test_custom_config(self):
        """Test setting custom configuration."""
        plugin = MetadataEnricherPlugin()
        plugin.config = {
            "enrich_sitemap": False,
            "enrich_search": True,
            "search_date_type": "datetime",
            "search_custom_format": "%Y-%m-%d",
            "search_timezone": "Europe/Amsterdam",
            "search_locale": "nl",
        }

        assert plugin.config["enrich_sitemap"] is False
        assert plugin.config["search_date_type"] == "datetime"
        assert plugin.config["search_timezone"] == "Europe/Amsterdam"
        assert plugin.config["search_locale"] == "nl"


@pytest.mark.unit
class TestSitemapEnrichment:
    """Test sitemap enrichment via on_page_context."""

    def test_on_page_context_with_git_date(self, plugin, mock_page):
        """Test that git date is injected into page.update_date."""
        mock_page.meta["git_revision_date_localized_raw_iso_date"] = "2021-04-27"

        context = plugin.on_page_context({}, mock_page, {}, None)

        assert mock_page.update_date == "2021-04-27"
        assert context == {}

    def test_on_page_context_with_git_datetime(self, plugin, mock_page):
        """Test that git datetime extracts date part only for sitemap."""
        mock_page.meta["git_revision_date_localized_raw_iso_date"] = "2021-04-27 13:11:28"

        plugin.on_page_context({}, mock_page, {}, None)

        assert mock_page.update_date == "2021-04-27"

    def test_on_page_context_without_git_date(self, plugin, mock_page):
        """Test that page.update_date is not changed if no git date."""
        original_date = None
        mock_page.update_date = original_date

        plugin.on_page_context({}, mock_page, {}, None)

        assert mock_page.update_date is None

    def test_on_page_context_disabled(self, plugin, mock_page):
        """Test that sitemap enrichment can be disabled."""
        plugin.config["enrich_sitemap"] = False
        mock_page.meta["git_revision_date_localized_raw_iso_date"] = "2021-04-27"

        plugin.on_page_context({}, mock_page, {}, None)

        assert mock_page.update_date is None


@pytest.mark.unit
class TestGitDateExtraction:
    """Test _get_git_datetime method."""

    def test_get_git_datetime_success(self, plugin, docs_dir):
        """Test successful git datetime extraction."""
        filepath = os.path.join(docs_dir, "index.md")

        with patch("subprocess.check_output") as mock_cmd:
            mock_cmd.return_value = b"2021-04-27 13:11:28 +0000"

            dt = plugin._get_git_datetime(filepath)

            assert dt is not None
            assert dt.year == 2021
            assert dt.month == 4
            assert dt.day == 27
            assert dt.hour == 13
            assert dt.minute == 11

    def test_get_git_datetime_no_file(self, plugin):
        """Test handling of non-existent file."""
        result = plugin._get_git_datetime("/nonexistent/file.md")

        assert result is None

    def test_get_git_datetime_git_error(self, plugin, docs_dir):
        """Test handling of git error."""
        filepath = os.path.join(docs_dir, "index.md")

        with patch("subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "git")):
            result = plugin._get_git_datetime(filepath)

            assert result is None

    def test_get_git_datetime_empty_result(self, plugin, docs_dir):
        """Test handling of empty git result."""
        filepath = os.path.join(docs_dir, "index.md")

        with patch("subprocess.check_output") as mock_cmd:
            mock_cmd.return_value = b""

            result = plugin._get_git_datetime(filepath)

            assert result is None


@pytest.mark.unit
class TestDateFormatting:
    """Test _get_formatted_date method."""

    @patch("mkdocs_metadata_enricher_plugin.plugin.MetadataEnricherPlugin._get_git_datetime")
    def test_format_iso_date(self, mock_git, plugin, docs_dir):
        """Test iso_date format."""
        filepath = os.path.join(docs_dir, "index.md")
        dt = datetime(2021, 4, 27, 13, 11, 28, tzinfo=ZoneInfo("UTC"))
        mock_git.return_value = dt

        plugin.config["search_date_type"] = "iso_date"
        result = plugin._get_formatted_date(filepath)

        assert result == "2021-04-27"

    @patch("mkdocs_metadata_enricher_plugin.plugin.MetadataEnricherPlugin._get_git_datetime")
    def test_format_iso_datetime(self, mock_git, plugin, docs_dir):
        """Test iso_datetime format."""
        filepath = os.path.join(docs_dir, "index.md")
        dt = datetime(2021, 4, 27, 13, 11, 28, tzinfo=ZoneInfo("UTC"))
        mock_git.return_value = dt

        plugin.config["search_date_type"] = "iso_datetime"
        result = plugin._get_formatted_date(filepath)

        assert result == "2021-04-27 13:11:28"

    @patch("mkdocs_metadata_enricher_plugin.plugin.MetadataEnricherPlugin._get_git_datetime")
    def test_format_custom(self, mock_git, plugin, docs_dir):
        """Test custom format."""
        filepath = os.path.join(docs_dir, "index.md")
        dt = datetime(2021, 4, 27, 13, 11, 28, tzinfo=ZoneInfo("UTC"))
        mock_git.return_value = dt

        plugin.config["search_date_type"] = "custom"
        plugin.config["search_custom_format"] = "%d/%m/%Y"
        result = plugin._get_formatted_date(filepath)

        assert result == "27/04/2021"

    @patch("mkdocs_metadata_enricher_plugin.plugin.MetadataEnricherPlugin._get_git_datetime")
    def test_format_date_localized(self, mock_git, plugin, docs_dir):
        """Test date format with localization."""
        filepath = os.path.join(docs_dir, "index.md")
        dt = datetime(2021, 4, 27, 13, 11, 28, tzinfo=ZoneInfo("UTC"))
        mock_git.return_value = dt

        plugin.config["search_date_type"] = "date"
        plugin.config["search_locale"] = "en"
        result = plugin._get_formatted_date(filepath)

        assert "April" in result or "27" in result

    @patch("mkdocs_metadata_enricher_plugin.plugin.MetadataEnricherPlugin._get_git_datetime")
    def test_format_datetime_localized(self, mock_git, plugin, docs_dir):
        """Test datetime format with localization."""
        filepath = os.path.join(docs_dir, "index.md")
        dt = datetime(2021, 4, 27, 13, 11, 28, tzinfo=ZoneInfo("UTC"))
        mock_git.return_value = dt

        plugin.config["search_date_type"] = "datetime"
        plugin.config["search_locale"] = "en"
        result = plugin._get_formatted_date(filepath)

        assert "13:11:28" in result

    @patch("mkdocs_metadata_enricher_plugin.plugin.MetadataEnricherPlugin._get_git_datetime")
    def test_format_with_timezone_conversion(self, mock_git, plugin, docs_dir):
        """Test date formatting with timezone conversion."""
        filepath = os.path.join(docs_dir, "index.md")
        # UTC datetime
        dt = datetime(2021, 4, 27, 2, 0, 0, tzinfo=ZoneInfo("UTC"))
        mock_git.return_value = dt

        plugin.config["search_date_type"] = "iso_datetime"
        plugin.config["search_timezone"] = "Europe/Amsterdam"  # UTC+2 in April
        result = plugin._get_formatted_date(filepath)

        # Should be converted to local time (UTC+2)
        assert "2021-04-27 04:00:00" in result

    @patch("mkdocs_metadata_enricher_plugin.plugin.MetadataEnricherPlugin._get_git_datetime")
    def test_format_no_git_date(self, mock_git, plugin, docs_dir):
        """Test handling when no git date is available."""
        filepath = os.path.join(docs_dir, "index.md")
        mock_git.return_value = None

        result = plugin._get_formatted_date(filepath)

        assert result is None


@pytest.mark.unit
class TestSearchIndexEnrichment:
    """Test on_post_build method."""

    def test_on_post_build_missing_index(self, plugin, mkdocs_config):
        """Test handling of missing search index."""
        # Remove search index
        search_index_path = os.path.join(mkdocs_config["site_dir"], "search", "search_index.json")
        os.remove(search_index_path)

        # Should log warning but not raise
        with patch("mkdocs_metadata_enricher_plugin.plugin.log") as mock_log:
            plugin.on_post_build(mkdocs_config)
            mock_log.warning.assert_called()

    def test_on_post_build_disabled(self, plugin, mkdocs_config):
        """Test that search enrichment can be disabled."""
        plugin.config["enrich_search"] = False
        search_index_path = os.path.join(mkdocs_config["site_dir"], "search", "search_index.json")

        original_content = open(search_index_path).read()
        plugin.on_post_build(mkdocs_config)
        new_content = open(search_index_path).read()

        # Index should be unchanged
        assert original_content == new_content

    @patch("mkdocs_metadata_enricher_plugin.plugin.MetadataEnricherPlugin._get_formatted_date")
    def test_on_post_build_adds_dates(self, mock_format, plugin, mkdocs_config):
        """Test that dates are added to search index."""
        mock_format.return_value = "2021-04-27"

        plugin.on_post_build(mkdocs_config)

        search_index_path = os.path.join(mkdocs_config["site_dir"], "search", "search_index.json")
        with open(search_index_path) as f:
            index = json.load(f)

        # All docs should have last_updated
        for doc in index["docs"]:
            assert "last_updated" in doc
            assert doc["last_updated"] == "2021-04-27"


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_malformed_search_index(self, plugin, mkdocs_config):
        """Test handling of malformed JSON in search index."""
        search_index_path = os.path.join(mkdocs_config["site_dir"], "search", "search_index.json")
        with open(search_index_path, "w") as f:
            f.write("{invalid json")

        with patch("mkdocs_metadata_enricher_plugin.plugin.log") as mock_log:
            plugin.on_post_build(mkdocs_config)
            mock_log.error.assert_called()

    def test_empty_docs_list(self, plugin, mkdocs_config):
        """Test handling of search index with empty docs list."""
        search_index_path = os.path.join(mkdocs_config["site_dir"], "search", "search_index.json")
        with open(search_index_path, "w") as f:
            json.dump({"docs": [], "config": {}}, f)

        # Should not raise
        plugin.on_post_build(mkdocs_config)

        with open(search_index_path) as f:
            index = json.load(f)
        assert index["docs"] == []

    def test_search_entry_with_anchor_fragment(self, plugin, mkdocs_config):
        """Test that anchor fragments in locations are stripped."""
        search_index_path = os.path.join(mkdocs_config["site_dir"], "search", "search_index.json")
        with open(search_index_path, "w") as f:
            json.dump(
                {
                    "docs": [
                        {
                            "location": "/page1/#section-1",
                            "title": "Section 1",
                            "text": "Content",
                        }
                    ],
                    "config": {},
                },
                f,
            )

        with patch(
            "mkdocs_metadata_enricher_plugin.plugin.MetadataEnricherPlugin._get_formatted_date"
        ) as mock_format:
            mock_format.return_value = "2021-04-27"
            plugin.on_post_build(mkdocs_config)

        with open(search_index_path) as f:
            index = json.load(f)
        assert index["docs"][0]["last_updated"] == "2021-04-27"

    def test_invalid_timezone(self, plugin, docs_dir):
        """Test that invalid timezone logs an error."""
        filepath = os.path.join(docs_dir, "index.md")
        dt = datetime(2021, 4, 27, 13, 11, 28, tzinfo=ZoneInfo("UTC"))

        plugin.config["search_timezone"] = "Invalid/Timezone"

        with patch("mkdocs_metadata_enricher_plugin.plugin.log") as mock_log:
            result = plugin._format_datetime(dt)
            assert result is None
            mock_log.error.assert_called()

    def test_on_page_context_caches_date(self, plugin, mock_page):
        """Test that on_page_context populates the date cache."""
        mock_page.meta["git_revision_date_localized_raw_iso_date"] = "2021-04-27"
        mock_page.file.src_path = "index.md"
        mock_page.file.dest_path = "index.html"

        plugin.on_page_context({}, mock_page, {}, None)

        assert "index.md" in plugin._date_cache
        assert plugin._path_map["index.html"] == "index.md"

    def test_on_page_context_caches_even_when_sitemap_disabled(self, plugin, mock_page):
        """Test that caching happens even when enrich_sitemap is False."""
        plugin.config["enrich_sitemap"] = False
        mock_page.meta["git_revision_date_localized_raw_iso_date"] = "2021-04-27"
        mock_page.file.src_path = "index.md"
        mock_page.file.dest_path = "index.html"

        plugin.on_page_context({}, mock_page, {}, None)

        # Caching still happens
        assert "index.md" in plugin._date_cache
        # But update_date is not set
        assert mock_page.update_date is None
