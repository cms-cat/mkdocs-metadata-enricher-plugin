# mkdocs-metadata-enricher

[![PyPI - Version](https://img.shields.io/pypi/v/mkdocs-metadata-enricher)](https://pypi.org/project/mkdocs-metadata-enricher/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mkdocs-metadata-enricher)](https://pypi.org/project/mkdocs-metadata-enricher/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A [MkDocs](https://www.mkdocs.org/) plugin that enriches your **sitemap.xml** and **search index** with git revision dates. It automatically injects the last commit date for each page based on git history, making your sitemap SEO-friendly and search results more informative.

## Features

- 🔄 **Sitemap enrichment**: Automatically updates sitemap `<lastmod>` dates with git revision dates
- 🔍 **Search index enrichment**: Adds formatted git dates to search results
- 📅 **Flexible date formatting**: Choose from `date`, `datetime`, `iso_date`, `iso_datetime`, or custom formats
- 🌍 **Timezone & locale support**: Display dates in any timezone and language
- 🎯 **Theme agnostic**: Works with any MkDocs theme
- ⚡ **Independent formatting**: Search index dates are formatted independently from page display dates
- 🔗 **Seamless integration**: Works alongside `mkdocs-git-revision-date-localized-plugin`

## Installation

Install the plugin using pip:

```bash
pip install mkdocs-metadata-enricher
```

Or with uv:

```bash
uv add mkdocs-metadata-enricher
```

## Quick Start

### 1. Enable the plugin in `mkdocs.yml`

```yaml
plugins:
  - search

  # Must run BEFORE metadata-enricher to provide git data
  - git-revision-date-localized:
      type: date
      enable_creation_date: false

  # Our plugin for enriching sitemap & search index
  - metadata-enricher:
      enrich_sitemap: true
      enrich_search: true
      search_date_type: datetime
      search_locale: en
```

### 2. Build your docs as usual

```bash
mkdocs build
```

That's it! Your `sitemap.xml` and search index will now include git revision dates.

## Configuration

### Basic Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enrich_sitemap` | bool | `True` | Add git dates to sitemap.xml `<lastmod>` tags |
| `enrich_search` | bool | `True` | Add formatted dates to search index entries |

### Search Index Date Formatting

When `enrich_search: true`, you can customize how dates appear in search results:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `search_date_type` | str | `iso_date` | Date format: `date`, `datetime`, `iso_date`, `iso_datetime`, or `custom` |
| `search_custom_format` | str | `%d. %B %Y` | Python strftime format when `search_date_type: custom` |
| `search_timezone` | str | `UTC` | [Timezone](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) for date display (e.g., `Europe/Amsterdam`) |
| `search_locale` | str | `en` | [Locale code](https://www.mkdocs.org/user-guide/localizing-your-theme/#supported-locales) for date localization (e.g., `en`, `de`, `fr`) |

### Date Format Examples

#### `search_date_type: iso_date` (default)
```
2021-04-27
```

#### `search_date_type: iso_datetime`
```
2021-04-27 13:11:28
```

#### `search_date_type: date` with `search_locale: en`
```
April 27, 2021
```

#### `search_date_type: datetime` with `search_locale: en`
```
April 27, 2021 13:11:28
```

#### `search_date_type: custom` with `search_custom_format: "%d/%m/%Y"`
```
27/04/2021
```

## Full Configuration Example

```yaml
site_name: My Documentation
docs_dir: docs
site_dir: site

plugins:
  - search

  - git-revision-date-localized:
      type: date
      timezone: Europe/Amsterdam
      locale: en

  - metadata-enricher:
      enrich_sitemap: true
      enrich_search: true
      search_date_type: datetime
      search_timezone: Europe/Amsterdam
      search_locale: en
      search_custom_format: "%d. %B %Y"  # Only used if search_date_type: custom
```

## Why Use This Plugin?

### Problem
Out-of-the-box MkDocs generates sitemaps and search indexes with build dates, not actual revision dates. This is suboptimal for:
- **SEO**: Search engines prefer pages with accurate `<lastmod>` timestamps
- **User experience**: Users want to know when docs were actually updated
- **Search results**: Search indexes don't show update information

### Solution
This plugin:
1. Extracts the **actual last commit date** for each page from git history
2. Injects it into `sitemap.xml` for SEO benefits
3. Formats and adds it to the search index so users see up-to-date info
4. Works independently with flexible date formatting

## Requirements

- **MkDocs** >= 1.0
- **Python** >= 3.9
- **Git** (for reading commit history)
- **mkdocs-git-revision-date-localized-plugin** >= 0.14.0

## Supports

- Python 3.9, 3.10, 3.11, 3.12
- MkDocs themes: Material, ReadTheDocs, any theme

## Contributing

Contributions are welcome! See [DEVELOPMENT.md](DEVELOPMENT.md) for how to set up your development environment.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Related Projects

- [mkdocs-git-revision-date-localized-plugin](https://github.com/timvink/mkdocs-git-revision-date-localized-plugin) - Displays git revision dates on pages
- [mkdocs-material](https://squidfunk.github.io/mkdocs-material/) - Material Design theme for MkDocs
