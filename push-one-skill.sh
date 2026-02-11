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
  echo "SKIP $skill (exists)"
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

# Create GitHub repo and push
if gh repo create "$ORG/$skill" --public --description "Hanzo Bot skill: $skill (by $author)" --source . --push >"$log" 2>&1; then
  echo "OK   $skill"
else
  echo "FAIL $skill"
fi

cd /
rm -rf "$tmp"
