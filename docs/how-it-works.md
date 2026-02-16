# How It Works

This page explains the enrichment pipeline and shows before/after comparisons.

## The Problem

When MkDocs builds your site, it generates two important files:

- **`sitemap.xml`** — used by search engines to discover and index your pages
- **`search/search_index.json`** — used by the built-in search to find content

By default, neither of these files contains accurate revision dates. The sitemap
may use the build date, and the search index contains no date information at all.

## The Solution

The plugin hooks into two MkDocs build events:

```mermaid
graph LR
    A[MkDocs Build] --> B[on_page_context]
    B --> C[Cache git dates per page]
    A --> D[on_post_build]
    D --> E[Enrich sitemap.xml]
    D --> F[Enrich search_index.json]
```

### Step 1: Collect git dates (`on_page_context`)

During the build, the plugin reads the git revision date that
`git-revision-date-localized-plugin` has already extracted and cached for each
page. It stores this date in an internal cache keyed by page path.

### Step 2: Enrich sitemap (`on_post_build`)

After the build completes, the plugin reads the generated `sitemap.xml` and
replaces or adds `<lastmod>` entries with the actual git commit dates.

### Step 3: Enrich search index (`on_post_build`)

The plugin reads `search/search_index.json` and prepends a formatted date
string to the `text` field of each search entry. This makes the date visible
in search results.

## Before & After

### Sitemap

**Before** (default MkDocs output):

```xml
<url>
  <loc>https://example.com/getting-started/</loc>
  <!-- No <lastmod> or uses build date -->
</url>
```

**After** (with metadata-enricher):

```xml
<url>
  <loc>https://example.com/getting-started/</loc>
  <lastmod>2025-11-03</lastmod>
</url>
```

### Search Index

**Before** (default MkDocs output):

```json
{
  "location": "getting-started/",
  "title": "Getting Started",
  "text": "Install and configure the plugin..."
}
```

**After** (with `search_date_type: datetime`, `search_locale: en`):

```json
{
  "location": "getting-started/",
  "title": "Getting Started",
  "text": "November 3, 2025 14:22:05 — Install and configure the plugin..."
}
```

The date appears as a prefix in the search text, making it visible when users
search your documentation.

## Integration with git-revision-date-localized

This plugin does **not** read git history itself during the page-rendering
phase. Instead, it relies on
[mkdocs-git-revision-date-localized-plugin](https://github.com/timvink/mkdocs-git-revision-date-localized-plugin)
to extract and set revision dates in each page's metadata. The metadata enricher
then reads these cached dates and uses them for sitemap and search enrichment.

For the search index fallback path (cache misses), the plugin queries git
directly using:

```bash
git log -1 --format=%aI -- <filepath>
```

This returns the author date of the last commit that touched the file, in ISO
8601 format.

## SEO Benefits

Search engines like Google use `<lastmod>` in sitemaps to:

- Prioritise crawling recently updated pages
- Display "last updated" dates in search results
- Assess content freshness

By providing accurate git-based dates instead of build dates, your
documentation appears more trustworthy and up-to-date to search engines.
