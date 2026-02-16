"""MkDocs Metadata Enricher Plugin."""

from __future__ import annotations

import json
import logging
import os
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo

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

    def on_config(self, config, **kwargs):
        """
        Initialize caches at the start of the build.

        Args:
            config: MkDocs configuration.

        Returns:
            The config object (unchanged).
        """
        # Cache: src_path -> UTC datetime (populated in on_page_context)
        self._date_cache = {}
        # Map: dest_path (output URL) -> src_path (source file)
        self._path_map = {}
        return config

    def on_page_context(self, context, page, config, nav):
        """
        Inject git date into page context for sitemap enrichment.

        This hook reads the git revision date from page.meta (set by
        git-revision-date-localized-plugin) and updates page.update_date,
        which the default sitemap template respects. It also caches
        the datetime and path mapping for use in on_post_build.

        Args:
            context: Page rendering context.
            page: MkDocs page object.
            config: MkDocs config.
            nav: Navigation structure.

        Returns:
            The context object (unchanged).
        """
        # Cache the path mapping (dest_path -> src_path) for on_post_build
        if hasattr(page, "file") and page.file:
            self._path_map[page.file.dest_path] = page.file.src_path

        # Read raw ISO date from git-revision-date-localized-plugin
        git_date = page.meta.get("git_revision_date_localized_raw_iso_date")

        if git_date:
            # Cache the parsed datetime for on_post_build
            try:
                dt = datetime.fromisoformat(git_date)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=ZoneInfo("UTC"))
                else:
                    dt = dt.astimezone(ZoneInfo("UTC"))
                self._date_cache[page.file.src_path] = dt
            except ValueError:
                log.debug(
                    f"MetadataEnricher: Could not parse date '{git_date}' for {page.file.src_path}"
                )

            if self.config["enrich_sitemap"]:
                # Update page.update_date so sitemap uses git date (YYYY-MM-DD only)
                page.update_date = git_date.split(" ")[0] if " " in git_date else git_date
                log.debug(f"Updated sitemap date for {page.file.src_path}: {page.update_date}")

        return context

    def on_post_build(self, config, **kwargs):
        """
        Enrich search index with formatted git revision dates after build.

        Reads search_index.json and injects formatted dates. Uses cached
        dates from on_page_context when available, falling back to git
        subprocess for cache misses.

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

                # Resolve source path using cached mapping, fall back to heuristic
                src_path = self._path_map.get(rel_url)
                if src_path is None:
                    # Heuristic fallback
                    src_path = rel_url.replace(".html", ".md")
                    log.debug(
                        f"MetadataEnricher: No path mapping for '{rel_url}', "
                        f"using heuristic: {src_path}"
                    )

                # Try cached date first, fall back to git subprocess
                dt = self._date_cache.get(src_path)
                if dt:
                    formatted_date = self._format_datetime(dt)
                else:
                    full_path = os.path.join(docs_dir, src_path)
                    formatted_date = self._get_formatted_date(full_path)

                if formatted_date:
                    entry["last_updated"] = formatted_date
                    modified_count += 1

            with open(search_index_path, "w", encoding="utf-8") as f:
                json.dump(search_index, f, separators=(",", ":"))

            log.info(
                f"MetadataEnricher: Added dates to {modified_count} entries " "in search_index.json"
            )

        except (json.JSONDecodeError, KeyError, OSError) as e:
            log.error(f"MetadataEnricher: Failed to process search index: {e}")

    def _get_git_datetime(self, filepath: str) -> datetime | None:
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
                    dt = dt.replace(tzinfo=ZoneInfo("UTC"))
                else:
                    dt = dt.astimezone(ZoneInfo("UTC"))
                return dt

            return None
        except (subprocess.CalledProcessError, OSError, ValueError) as e:
            log.debug(f"MetadataEnricher: Error getting git date for {filepath}: {e}")
            return None

    def _get_formatted_date(self, filepath: str) -> str | None:
        """
        Get formatted git date for search index based on config.

        Fetches the git datetime for the given file and formats it.

        Args:
            filepath: Absolute path to the source file.

        Returns:
            Formatted date string, or None if date not found.
        """
        dt = self._get_git_datetime(filepath)
        if not dt:
            return None

        return self._format_datetime(dt)

    def _format_datetime(self, dt: datetime) -> str | None:
        """
        Format a datetime according to plugin config.

        Args:
            dt: Timezone-aware datetime object.

        Returns:
            Formatted date string, or None on error.
        """
        date_type = self.config["search_date_type"]
        timezone_name = self.config["search_timezone"]
        locale = self.config["search_locale"]

        try:
            # Convert to target timezone
            tz = ZoneInfo(timezone_name)
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

        except (KeyError, ValueError) as e:
            log.error(f"MetadataEnricher: Error formatting date: {e}")
            return None
