# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-02-15

### Added

- Initial release of mkdocs-metadata-enricher plugin
- **Sitemap enrichment**: Automatically updates sitemap `<lastmod>` dates with git revision dates
- **Search index enrichment**: Adds formatted git dates to search result entries
- **Flexible date formatting**: Support for `date`, `datetime`, `iso_date`, `iso_datetime`, and `custom` formats
- **Timezone support**: Display dates in any timezone
- **Locale support**: Localized date formatting for different languages
- **Independent formatting**: Search index dates formatted independently from page display dates
- **Theme agnostic**: Works with any MkDocs theme
- **Comprehensive test suite**: Unit and integration tests with pytest
- **GitHub Actions CI**: Automated testing on Python 3.9–3.12
- **Trusted PyPI publishing**: OIDC-based trusted publishing workflow

### Dependencies

- mkdocs >= 1.0
- mkdocs-git-revision-date-localized-plugin >= 0.14.0
- babel >= 2.12.0
- pytz

### Requirements

- Python >= 3.9
- Git (for version control and read access to commit history)
