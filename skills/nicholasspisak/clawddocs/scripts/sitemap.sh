#!/bin/bash
# Sitemap generator - shows all docs by category
echo "Fetching Bot documentation sitemap..."

# Categories structure based on docs.hanzo.bot
CATEGORIES=(
  "start"
  "gateway"
  "providers"
  "concepts"
  "tools"
  "automation"
  "cli"
  "platforms"
  "nodes"
  "web"
  "install"
  "reference"
)

for cat in "${CATEGORIES[@]}"; do
  echo "📁 /$cat/"
done
