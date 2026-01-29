#!/bin/bash
# Council Environment Discovery

# Database path
COUNCIL_DB=${COUNCIL_DB:-"$HOME/.bot/council.db"}

# Graphiti URL (for Memory Bridge)
GRAPHITI_URL=$(bot config get skills.graphiti.baseUrl 2>/dev/null || echo "")
GRAPHITI_URL=${GRAPHITI_URL:-"http://localhost:8001"}

echo "COUNCIL_DB=$COUNCIL_DB"
echo "GRAPHITI_URL=$GRAPHITI_URL"
