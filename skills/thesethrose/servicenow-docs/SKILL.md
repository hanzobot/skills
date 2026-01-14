---
name: servicenow-docs
description: Search and retrieve ServiceNow documentation, release notes, API references, and platform guides. Fetches content from docs.servicenow.com via the Zoomin API.
metadata:
  clawdbot:
    emoji: "📘"
    read_when:
      - Answering questions about ServiceNow features, APIs, or scripting
      - Looking up release notes or patch information
      - Finding documentation for GlideRecord, GlideAjax, workflows, etc.
      - Researching ServiceNow platform capabilities
---

# ServiceNow Documentation Skill

Search and retrieve documentation from docs.servicenow.com. This skill provides access to ServiceNow's entire documentation library including API references, release notes, scripting guides, and platform features.

## When to Use

Use this skill when the user asks about:
- ServiceNow API documentation (GlideRecord, GlideAjax, GlideQuery, etc.)
- Release notes, patches, or new features
- Platform configuration or administration
- Scripting patterns or best practices
- Accessibility, UI, or user preferences
- Any ServiceNow product or feature documentation

## Tools

### servicenow_search
Search the ServiceNow documentation database.

**Args:**
- `query` (string, required) - Search terms (e.g., "GlideRecord", "accessibility preferences", "patch notes")
- `limit` (number, default: 10) - Maximum results to return
- `version` (string, optional) - Filter by version (e.g., "Washington DC", "Zurich", "Yokohama")

**Example:**
```json
{"query": "GlideAjax client script", "limit": 5}
```

### servicenow_get_article
Fetch the full content of a documentation article.

**Args:**
- `url` (string, required) - The article URL (automatically converted from Zoomin to docs.servicenow.com)

**Example:**
```json
{"url": "https://docs.servicenow.com/bundle/zurich-release-notes/page/release-notes/quality/zurich-patch-5.html"}
```

### servicenow_list_versions
List available ServiceNow documentation versions/releases.

**Args:** None required

### servicenow_latest_release
Get release notes for the latest ServiceNow version (automatically detects most recent).

**Args:** None required

## URL Handling

- **Search API:** Uses Zoomin API (servicenow-be-prod.servicenow.com) for searching
- **User-facing URLs:** Automatically converted to docs.servicenow.com for readability
- **Article content:** Fetched via the Zoomin API endpoint with proper headers

## Example Usage

User: "What are the accessibility preferences in ServiceNow?"
→ Use servicenow_search to find accessibility documentation
→ Use servicenow_get_article to fetch the full content
→ Summarize the preferences for the user

User: "Tell me about the latest ServiceNow patch"
→ Use servicenow_latest_release to get the most recent release notes
→ Fetch and summarize the patch details

## APIs Used

- **Zoomin Search API:** `https://servicenow-be-prod.servicenow.com/search`
- **Content Source:** docs.servicenow.com (accessed via Zoomin API)
