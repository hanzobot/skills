#!/bin/bash
# Push all skills to hanzoskill GitHub org as individual repos
# Usage: ./push-skills.sh [batch_start] [batch_size]

set -e

ORG="hanzoskill"
SKILLS_DIR="/Users/z/work/hanzo/bot/skills/skills"
TMPBASE="/tmp/hanzoskill-push"
LOGDIR="/tmp/hanzoskill-logs"
mkdir -p "$TMPBASE" "$LOGDIR"

BATCH_START=${1:-0}
BATCH_SIZE=${2:-100}
PARALLEL=${3:-8}

# Collect all skills
SKILLS=()
for author_dir in "$SKILLS_DIR"/*/; do
  author=$(basename "$author_dir")
  for skill_dir in "$author_dir"*/; do
    [ -d "$skill_dir" ] || continue
    skill=$(basename "$skill_dir")
    SKILLS+=("$author/$skill")
  done
done

TOTAL=${#SKILLS[@]}
echo "Total skills: $TOTAL"
echo "Batch: $BATCH_START to $((BATCH_START + BATCH_SIZE - 1))"

push_skill() {
  local entry="$1"
  local author=$(echo "$entry" | cut -d/ -f1)
  local skill=$(echo "$entry" | cut -d/ -f2)
  local src="$SKILLS_DIR/$author/$skill"
  local tmp="$TMPBASE/$skill"
  local log="$LOGDIR/$skill.log"

  # Skip if repo already exists
  if gh repo view "$ORG/$skill" &>/dev/null; then
    echo "SKIP $skill (exists)" | tee "$log"
    return 0
  fi

  # Create temp git repo
  rm -rf "$tmp"
  mkdir -p "$tmp"
  cp -a "$src"/. "$tmp"/

  # Add metadata
  echo "Author: $author" > "$tmp/.author"
  echo "Skill: $skill" >> "$tmp/.author"
  echo "Source: hanzoskill" >> "$tmp/.author"

  cd "$tmp"
  git init -q
  git checkout -q -b main
  git add -A
  git commit -q -m "Initial import of $skill skill (author: $author)"

  # Create GitHub repo and push
  if gh repo create "$ORG/$skill" --public --description "Hanzo Bot skill: $skill (by $author)" --source . --push &>"$log"; then
    echo "OK   $skill"
  else
    # If create failed but repo exists, just push
    git remote add origin "git@github.com:$ORG/$skill.git" 2>/dev/null || true
    if git push -u origin main -f &>>"$log"; then
      echo "PUSH $skill"
    else
      echo "FAIL $skill (see $log)"
    fi
  fi

  cd /
  rm -rf "$tmp"
}

export -f push_skill
export ORG SKILLS_DIR TMPBASE LOGDIR

# Process batch
END=$((BATCH_START + BATCH_SIZE))
[ $END -gt $TOTAL ] && END=$TOTAL

BATCH_SKILLS=()
for ((i=BATCH_START; i<END; i++)); do
  BATCH_SKILLS+=("${SKILLS[$i]}")
done

echo "Processing ${#BATCH_SKILLS[@]} skills with $PARALLEL parallel jobs..."
printf '%s\n' "${BATCH_SKILLS[@]}" | xargs -P "$PARALLEL" -I {} bash -c 'push_skill "$@"' _ {}

echo ""
echo "Batch complete. Check $LOGDIR for details."
echo "Repos created: $(gh repo list $ORG --limit 1000 --json name -q '.[].name' 2>/dev/null | wc -l)"
