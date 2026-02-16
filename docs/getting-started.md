# Getting Started

Install and configure **mkdocs-metadata-enricher-plugin** in under 2 minutes.

## Installation

=== "pip"

    ```bash
    pip install mkdocs-metadata-enricher-plugin
    ```

=== "uv"

    ```bash
    uv add mkdocs-metadata-enricher-plugin
    ```

This will also install the required dependency
[mkdocs-git-revision-date-localized-plugin](https://github.com/timvink/mkdocs-git-revision-date-localized-plugin).

## Configuration

Add the plugin to your `mkdocs.yml`. The **order matters** — the git revision
date plugin must run _before_ the metadata enricher:

```yaml
plugins:
  - search

  # Must run BEFORE metadata-enricher to provide git data
  - git-revision-date-localized:
      type: date
      enable_creation_date: false

  # Enriches sitemap & search index with git dates
  - metadata-enricher:
      enrich_sitemap: true
      enrich_search: true
      search_date_type: datetime
      search_locale: en
```

## Build your docs

```bash
mkdocs build
```

That's it! Your `sitemap.xml` will now contain accurate `<lastmod>` dates and
your search index will show when each page was last updated.

## Verify it works

After building, you can inspect the results:

### Sitemap

Open `site/sitemap.xml` and look for `<lastmod>` entries:

```xml
<url>
  <loc>https://example.com/my-page/</loc>
  <lastmod>2025-11-03</lastmod>
</url>
```

### Search index

Open `site/search/search_index.json` and look for dates in the `text` field of
each entry. With `search_date_type: datetime`, you'll see something like:

```json
{
  "location": "my-page/",
  "title": "My Page",
  "text": "April 27, 2025 13:11:28 — Page content here..."
}
```

## Next steps

- [Configuration](configuration.md) — customise date formats, timezones, and locales
- [How It Works](how-it-works.md) — understand the enrichment pipeline
