# mkdocs-metadata-enricher-plugin

**Enrich your MkDocs sitemap and search index with real git revision dates.**

---

[![PyPI - Version](https://img.shields.io/pypi/v/mkdocs-metadata-enricher-plugin)](https://pypi.org/project/mkdocs-metadata-enricher-plugin/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mkdocs-metadata-enricher-plugin)](https://pypi.org/project/mkdocs-metadata-enricher-plugin/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/cms-cat/mkdocs-metadata-enricher-plugin/blob/main/LICENSE)

## What does this plugin do?

Out-of-the-box, MkDocs generates sitemaps and search indexes with **build-time dates** — not the dates your pages were actually last updated. This is suboptimal for:

- **SEO** — search engines prefer pages with accurate `<lastmod>` timestamps
- **User experience** — readers want to know when documentation was actually changed
- **Search results** — the built-in search index doesn't show any update information

**mkdocs-metadata-enricher-plugin** fixes this by:

1. Extracting the **actual last commit date** for each page from git history
2. Injecting it into `sitemap.xml` as proper `<lastmod>` entries
3. Adding formatted dates to search index entries so users see when content was last updated

!!! tip "See it in action"
    Try the **search** on this site — each result shows a last-updated date pulled from git history. You can also inspect the [sitemap.xml](https://cms-cat.github.io/mkdocs-metadata-enricher-plugin/sitemap.xml) to see `<lastmod>` dates.

## Features

| Feature | Description |
|---------|-------------|
| 🔄 **Sitemap enrichment** | Adds git revision dates to `<lastmod>` tags in `sitemap.xml` |
| 🔍 **Search enrichment** | Shows formatted git dates in search results |
| 📅 **Flexible formatting** | `date`, `datetime`, `iso_date`, `iso_datetime`, or `custom` strftime |
| 🌍 **Timezone & locale** | Display dates in any timezone and language |
| 🎯 **Theme agnostic** | Works with Material, ReadTheDocs, or any MkDocs theme |
| ⚡ **Independent formatting** | Search dates are formatted independently from page display dates |

## Quick links

- [Getting Started](getting-started.md) — install and configure in under 2 minutes
- [Configuration](configuration.md) — all options with examples
- [How It Works](how-it-works.md) — technical details and before/after comparisons
- [GitHub Repository](https://github.com/cms-cat/mkdocs-metadata-enricher-plugin) — source code and issue tracker

## Requirements

- **Python** >= 3.9
- **MkDocs** >= 1.0
- **Git** (for reading commit history)
- [mkdocs-git-revision-date-localized-plugin](https://github.com/timvink/mkdocs-git-revision-date-localized-plugin) >= 0.14.0
