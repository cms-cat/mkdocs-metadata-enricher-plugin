# Configuration

All configuration options for mkdocs-metadata-enricher-plugin live under the
`metadata-enricher` key in your `mkdocs.yml`.

## Basic Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enrich_sitemap` | `bool` | `true` | Add git dates to `<lastmod>` tags in `sitemap.xml` |
| `enrich_search` | `bool` | `true` | Add formatted dates to search index entries |

## Search Index Date Formatting

These options control how dates appear in search results when `enrich_search: true`.
They do **not** affect sitemap formatting.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `search_date_type` | `str` | `iso_date` | Date format (see below) |
| `search_custom_format` | `str` | `%d. %B %Y` | Python strftime format (only used when `search_date_type: custom`) |
| `search_timezone` | `str` | `UTC` | [IANA timezone](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) for date display |
| `search_locale` | `str` | `en` | [Locale code](https://www.mkdocs.org/user-guide/localizing-your-theme/#supported-locales) for date localization |

### Date format types

!!! note "Sitemap format is fixed"
  `sitemap.xml` uses `<lastmod>` values in `YYYY-MM-DD` format (for example,
  `2025-04-27`) as expected by sitemap consumers. The `search_date_type`
  options below apply only to `search/search_index.json` output.

#### `iso_date` (default)

```
2025-04-27
```

#### `iso_datetime`

```
2025-04-27 13:11:28
```

#### `date`

With `search_locale: en`:

```
April 27, 2025
```

With `search_locale: de`:

```
27. April 2025
```

#### `datetime`

With `search_locale: en`:

```
April 27, 2025 13:11:28
```

#### `custom`

Use any Python [strftime format string](https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior):

```yaml
search_date_type: custom
search_custom_format: "%d/%m/%Y"
```

Result:

```
27/04/2025
```

## Full Example

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

## Minimal Example

If you only want sitemap enrichment and are happy with ISO date format in search:

```yaml
plugins:
  - search
  - git-revision-date-localized
  - metadata-enricher
```

All defaults will apply: `enrich_sitemap: true`, `enrich_search: true`,
`search_date_type: iso_date`, `search_timezone: UTC`, `search_locale: en`.

## Plugin ordering

!!! warning "Plugin order matters"
    `git-revision-date-localized` **must** appear before `metadata-enricher` in
    your plugin list. The metadata enricher reads the git dates that the
    revision date plugin sets on each page's metadata.
