#!/bin/bash
# Push a single skill to hanzoskill org
# Usage: push-one-skill.sh <author/skill>

ORG="hanzoskill"
SKILLS_DIR="/Users/z/work/hanzo/bot/skills/skills"
TMPBASE="/tmp/hanzoskill-push"
LOGDIR="/tmp/hanzoskill-logs"
mkdir -p "$TMPBASE" "$LOGDIR"

entry="$1"
author=$(echo "$entry" | cut -d/ -f1)
skill=$(echo "$entry" | cut -d/ -f2)
src="$SKILLS_DIR/$author/$skill"
tmp="$TMPBASE/$skill-$$"
log="$LOGDIR/$skill.log"

# Skip if repo already exists
if gh repo view "$ORG/$skill" >/dev/null 2>&1; then
  echo "SKIP $skill"
  exit 0
fi

# Create temp git repo
rm -rf "$tmp"
mkdir -p "$tmp"
cp -a "$src"/. "$tmp"/

# Add author metadata
echo "Author: $author" > "$tmp/.author"

cd "$tmp"
git init -q
git checkout -q -b main
git add -A
git commit -q -m "Initial import of $skill skill (author: $author)"

# Create GitHub repo and push with retry
MAX_RETRIES=3
for attempt in $(seq 1 $MAX_RETRIES); do
  if gh repo create "$ORG/$skill" --public --description "Hanzo Bot skill: $skill (by $author)" --source . --push >"$log" 2>&1; then
    echo "OK   $skill"
    cd /
    rm -rf "$tmp"
    exit 0
  fi

  # Check if rate limited
  if grep -q "too many repositories\|rate limit\|secondary rate" "$log" 2>/dev/null; then
    sleep $((10 * attempt))
  else
    break
  fi
done

echo "FAIL $skill"
cd /
rm -rf "$tmp"
