"""MkDocs Metadata Enricher Plugin."""

import json
import logging
import os
import subprocess
from datetime import datetime
from typing import Optional

import pytz
from babel.dates import format_date
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin

log = logging.getLogger("mkdocs")


class MetadataEnricherPlugin(BasePlugin):
    """Plugin to enrich sitemap.xml and search index with git revision dates."""

    config_scheme = (
        ("enrich_sitemap", config_options.Type(bool, default=True)),
        ("enrich_search", config_options.Type(bool, default=True)),
        (
            "search_date_type",
            config_options.Choice(
                ["date", "datetime", "iso_date", "iso_datetime", "custom"],
                default="iso_date",
            ),
        ),
        ("search_custom_format", config_options.Type(str, default="%d. %B %Y")),
        ("search_timezone", config_options.Type(str, default="UTC")),
        ("search_locale", config_options.Type(str, default="en")),
    )

    def on_page_context(self, context, page, config, nav):
        """
        Inject git date into page context for sitemap enrichment.

        This hook reads the git revision date from page.meta (set by
        git-revision-date-localized-plugin) and updates page.update_date,
        which the default sitemap template respects.

        Args:
            context: Page rendering context.
            page: MkDocs page object.
            config: MkDocs config.
            nav: Navigation structure.

        Returns:
            The context object (unchanged).
        """
        if not self.config["enrich_sitemap"]:
            return context

        # Read raw ISO date from git-revision-date-localized-plugin
        git_date = page.meta.get("git_revision_date_localized_raw_iso_date")

        if git_date:
            # Update page.update_date so sitemap uses git date (YYYY-MM-DD only)
            page.update_date = git_date.split(" ")[0] if " " in git_date else git_date
            log.debug(f"Updated sitemap date for {page.file.src_path}: {page.update_date}")

        return context

    def on_post_build(self, config, **kwargs):
        """
        Enrich search index with formatted git revision dates after build.

        Reads search_index.json and injects formatted dates based on config.
        Queries git directly to extract full datetime, independent of
        git-revision-date-localized-plugin's type setting.

        Args:
            config: MkDocs configuration.
        """
        if not self.config["enrich_search"]:
            return

        site_dir = config["site_dir"]
        search_index_path = os.path.join(site_dir, "search", "search_index.json")

        if not os.path.exists(search_index_path):
            log.warning(
                "MetadataEnricher: search_index.json not found. "
                "Make sure the 'search' plugin is enabled."
            )
            return

        try:
            with open(search_index_path, encoding="utf-8") as f:
                search_index = json.load(f)

            docs_dir = config["docs_dir"]
            modified_count = 0

            for entry in search_index.get("docs", []):
                rel_url = entry["location"].split("#")[0]
                if rel_url.endswith("/"):
                    rel_url += "index.html"

                # Heuristic to find source file
                src_path_md = rel_url.replace(".html", ".md")
                full_path = os.path.join(docs_dir, src_path_md)

                formatted_date = self._get_formatted_date(full_path)
                if formatted_date:
                    entry["last_updated"] = formatted_date
                    modified_count += 1

            with open(search_index_path, "w", encoding="utf-8") as f:
                json.dump(search_index, f, separators=(",", ":"))

            log.info(
                f"MetadataEnricher: Added dates to {modified_count} entries " "in search_index.json"
            )

        except Exception as e:
            log.error(f"MetadataEnricher: Failed to process search index: {e}")

    def _get_git_datetime(self, filepath: str) -> Optional[datetime]:
        """
        Extract git commit datetime for a file.

        Queries git to get the last commit datetime in ISO format.
        Returns a timezone-aware datetime object in UTC.

        Args:
            filepath: Absolute path to the source file.

        Returns:
            Timezone-aware datetime object, or None if not found.
        """
        if not os.path.exists(filepath):
            return None

        try:
            # %ci = commit date, ISO 8601 format (includes timezone)
            cmd = ["git", "log", "-1", "--format=%ci", "--", filepath]
            result = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("utf-8").strip()

            if result:
                # Parse ISO format: "2021-04-27 13:11:28 +0200"
                dt = datetime.fromisoformat(result)
                # Ensure timezone-aware, convert to UTC for consistency
                if dt.tzinfo is None:
                    dt = pytz.UTC.localize(dt)
                else:
                    dt = dt.astimezone(pytz.UTC)
                return dt

            return None
        except Exception as e:
            log.debug(f"MetadataEnricher: Error getting git date for {filepath}: {e}")
            return None

    def _get_formatted_date(self, filepath: str) -> Optional[str]:
        """
        Get formatted git date for search index based on config.

        Args:
            filepath: Absolute path to the source file.

        Returns:
            Formatted date string, or None if date not found.
        """
        dt = self._get_git_datetime(filepath)
        if not dt:
            return None

        date_type = self.config["search_date_type"]
        timezone_name = self.config["search_timezone"]
        locale = self.config["search_locale"]

        try:
            # Convert to target timezone
            tz = pytz.timezone(timezone_name)
            dt_local = dt.astimezone(tz)

            if date_type == "iso_date":
                return dt_local.strftime("%Y-%m-%d")

            elif date_type == "iso_datetime":
                return dt_local.strftime("%Y-%m-%d %H:%M:%S")

            elif date_type == "date":
                # Localized date (e.g., "April 27, 2021")
                return format_date(dt_local, format="long", locale=locale)

            elif date_type == "datetime":
                # Localized datetime (e.g., "April 27, 2021 13:11:28")
                formatted_date = format_date(dt_local, format="long", locale=locale)
                time_str = dt_local.strftime("%H:%M:%S")
                return f"{formatted_date} {time_str}"

            elif date_type == "custom":
                # Use strftime with custom format
                custom_format = self.config["search_custom_format"]
                return dt_local.strftime(custom_format)

            return None

        except Exception as e:
            log.error(f"MetadataEnricher: Error formatting date for {filepath}: {e}")
            return None
