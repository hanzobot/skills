#!/usr/bin/env bash
# Bot Update Plus - Update functions
# Version: 2.1.1

# Global tracking
BOT_UPDATED=false
SKILLS_UPDATED=0

# Fix pnpm launcher script bug (pnpm doesn't update the launcher after upgrade)
fix_pnpm_launcher() {
  local bot_bin=$(which bot 2>/dev/null)

  if [[ -z "$bot_bin" ]]; then
    return 0
  fi

  # Check if bot works
  if bot --version &>/dev/null; then
    return 0  # Works fine, no fix needed
  fi

  log_warning "Detected pnpm launcher bug, fixing..."

  # Find the pnpm global directory
  local pnpm_global_dir=$(dirname "$bot_bin")/global/5/.pnpm

  if [[ ! -d "$pnpm_global_dir" ]]; then
    log_warning "Could not find pnpm global directory"
    return 1
  fi

  # Find the latest bot version directory
  local latest_bot_dir=$(ls -d "$pnpm_global_dir"/bot@* 2>/dev/null | sort -V | tail -1)

  if [[ -z "$latest_bot_dir" ]]; then
    log_warning "Could not find bot installation"
    return 1
  fi

  local latest_bot_name=$(basename "$latest_bot_dir")

  # Extract the old version from the launcher script
  local old_version=$(grep -oE 'bot@[^/]+' "$bot_bin" | head -1)

  if [[ -z "$old_version" ]] || [[ "$old_version" == "$latest_bot_name" ]]; then
    return 0  # Already correct or can't determine
  fi

  # Fix the launcher script
  log_info "Updating launcher: $old_version → $latest_bot_name"
  sed -i '' "s|$old_version|$latest_bot_name|g" "$bot_bin" 2>/dev/null

  # Verify fix worked
  if bot --version &>/dev/null; then
    log_success "pnpm launcher fixed"
    log_to_file "Fixed pnpm launcher: $old_version -> $latest_bot_name"
  else
    log_warning "Could not fix pnpm launcher automatically"
  fi

  return 0
}

# Detect package manager used to install bot
detect_package_manager() {
  # Check if bot is in a pnpm global path
  local bot_path=$(which bot 2>/dev/null)

  if [[ "$bot_path" == *"pnpm"* ]]; then
    echo "pnpm"
  elif [[ "$bot_path" == *"yarn"* ]]; then
    echo "yarn"
  elif [[ "$bot_path" == *"bun"* ]]; then
    echo "bun"
  elif command_exists pnpm && pnpm list -g bot 2>/dev/null | grep -q bot; then
    echo "pnpm"
  elif command_exists yarn && yarn global list 2>/dev/null | grep -q bot; then
    echo "yarn"
  elif command_exists bun && bun pm ls -g 2>/dev/null | grep -q bot; then
    echo "bun"
  elif command_exists npm; then
    echo "npm"
  else
    echo "unknown"
  fi
}

# Update Bot binary
update_bot() {
  if [[ "$DRY_RUN" == true ]]; then
    log_dry_run "Would update Bot"
    return 0
  fi

  log_info "Updating Bot..."

  if ! command_exists bot; then
    log_error "bot command not found"
    return 1
  fi

  local current_version
  current_version=$(bot --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+(-[0-9]+)?' | head -1 || echo "unknown")
  log_info "Current version: $current_version"
  log_to_file "Bot current version: $current_version"

  # Detect package manager
  local pkg_manager=$(detect_package_manager)
  log_info "Package manager: $pkg_manager"

  # Run appropriate update command
  local update_success=false
  case "$pkg_manager" in
    pnpm)
      log_info "Running: pnpm add -g bot@latest"
      if pnpm add -g bot@latest 2>&1; then
        update_success=true
      fi
      ;;
    npm)
      log_info "Running: npm install -g bot@latest"
      if npm install -g bot@latest 2>&1; then
        update_success=true
      fi
      ;;
    yarn)
      log_info "Running: yarn global add bot@latest"
      if yarn global add bot@latest 2>&1; then
        update_success=true
      fi
      ;;
    bun)
      log_info "Running: bun add -g bot@latest"
      if bun add -g bot@latest 2>&1; then
        update_success=true
      fi
      ;;
    *)
      log_warning "Unknown package manager, trying bot update..."
      if bot update 2>&1; then
        update_success=true
      fi
      ;;
  esac

  if [[ "$update_success" != true ]]; then
    log_error "Bot update failed"
    log_to_file "ERROR: Bot update failed"
    return 1
  fi

  # Fix pnpm launcher script if needed (pnpm bug workaround)
  if [[ "$pkg_manager" == "pnpm" ]]; then
    fix_pnpm_launcher
  fi

  # Check new version
  local new_version
  new_version=$(bot --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+(-[0-9]+)?' | head -1 || echo "unknown")

  if [[ "$current_version" != "$new_version" ]]; then
    log_success "Bot updated: $current_version → $new_version"
    log_to_file "Bot updated: $current_version -> $new_version"
    BOT_UPDATED=true
  else
    log_info "Bot is already up to date ($current_version)"
  fi

  return 0
}

# Update all skills
update_skills() {
  if [[ "$DRY_RUN" == true ]]; then
    log_dry_run "Would update skills"
    log_info "Checking for skill updates..."
    update_git_skills
    return 0
  fi

  log_info "Updating all skills..."
  log_to_file "Starting skills update"

  # Use claudhub if available
  if command_exists claudhub; then
    log_info "Updating skills via claudhub..."
    claudhub update --all 2>/dev/null || log_warning "claudhub update failed, trying git..."
  fi

  # Always run git skill update
  update_git_skills
}

# Update skills via git pull
update_git_skills() {
  local skills_dirs_json=$(get_skills_dirs)

  while IFS= read -r dir_config; do
    local dir_path=$(echo "$dir_config" | jq -r '.path')
    dir_path=$(expand_path "$dir_path")
    local dir_label=$(echo "$dir_config" | jq -r '.label')
    local dir_update=$(echo "$dir_config" | jq -r '.update')

    if [[ "$dir_update" != "true" ]]; then
      log_info "Skipping $dir_label (update disabled)"
      continue
    fi

    if [[ ! -d "$dir_path" ]]; then
      log_warning "Skills directory not found: $dir_path ($dir_label)"
      continue
    fi

    log_info "Checking skills in: $dir_path ($dir_label)"

    for skill_dir in "$dir_path"/*/; do
      [[ -d "$skill_dir/.git" ]] || continue

      update_single_skill "$skill_dir" "$dir_label"
    done
  done < <(echo "$skills_dirs_json" | jq -c '.[]')
}

# Update a single skill via git
update_single_skill() {
  local skill_dir="$1"
  local source_label="$2"
  local skill_name=$(basename "$skill_dir")

  cd "$skill_dir" || return 1

  # Check if excluded
  if is_excluded "$skill_name"; then
    log_info "Skipping excluded skill: $skill_name"
    return 0
  fi

  # Check for local changes
  if [[ -n "$(git status --porcelain 2>/dev/null)" ]]; then
    log_warning "$skill_name has local changes, skipping"
    return 0
  fi

  if [[ "$DRY_RUN" == true ]]; then
    # Check if updates available
    git fetch --quiet 2>/dev/null
    local behind=$(git rev-list --count HEAD..@{u} 2>/dev/null || echo "0")
    if [[ "$behind" -gt 0 ]]; then
      log_dry_run "Would update $skill_name ($behind commits behind)"
    fi
    return 0
  fi

  log_info "Updating: $skill_name"
  local current_commit=$(git rev-parse --short HEAD)

  if ! git pull --quiet 2>/dev/null; then
    log_error "$skill_name update failed, rolling back..."
    git reset --hard --quiet "$current_commit"
    return 1
  fi

  local new_commit=$(git rev-parse --short HEAD)
  if [[ "$current_commit" != "$new_commit" ]]; then
    log_success "$skill_name updated ($current_commit → $new_commit)"
    log_to_file "Updated $skill_name: $current_commit -> $new_commit"
    SKILLS_UPDATED=$((SKILLS_UPDATED + 1))
  else
    log_info "$skill_name already up to date"
  fi

  return 0
}

# Check for available updates (without applying)
check_updates() {
  local updates_available=0

  log_info "Checking for updates..."
  echo ""

  # Check Bot version
  if command_exists bot; then
    local current_version=$(bot --version 2>/dev/null | head -1 || echo "unknown")
    local latest_version="unknown"

    # Try to get latest version
    if command_exists npm; then
      latest_version=$(npm view bot version 2>/dev/null || echo "unknown")
    elif command_exists pnpm; then
      latest_version=$(pnpm view bot version 2>/dev/null || echo "unknown")
    fi

    echo -e "  ${BLUE}Bot${NC}"
    echo "    Installed: $current_version"

    if [[ "$latest_version" != "unknown" ]]; then
      echo "    Latest:    $latest_version"
      if [[ "$current_version" != "$latest_version" ]]; then
        echo -e "    ${YELLOW}→ Update available${NC}"
        updates_available=1
      else
        echo -e "    ${GREEN}✓ Up to date${NC}"
      fi
    else
      echo -e "    Latest:    ${YELLOW}Unable to check${NC}"
    fi
    echo ""
  fi

  # Check skills
  local skills_dirs_json=$(get_skills_dirs)
  local skills_with_updates=0
  local skills_checked=0

  echo -e "  ${BLUE}Skills${NC}"

  while IFS= read -r dir_config; do
    local dir_path=$(echo "$dir_config" | jq -r '.path')
    dir_path=$(expand_path "$dir_path")
    local dir_label=$(echo "$dir_config" | jq -r '.label')
    local dir_update=$(echo "$dir_config" | jq -r '.update')

    [[ "$dir_update" != "true" ]] && continue
    [[ ! -d "$dir_path" ]] && continue

    for skill_dir in "$dir_path"/*/; do
      [[ -d "$skill_dir/.git" ]] || continue

      local skill_name=$(basename "$skill_dir")

      if is_excluded "$skill_name"; then
        echo -e "    ${BLUE}○${NC} $skill_name (excluded)"
        continue
      fi

      skills_checked=$((skills_checked + 1))
      cd "$skill_dir"

      # Fetch to check for updates
      git fetch --quiet 2>/dev/null || continue

      local behind=$(git rev-list --count HEAD..@{u} 2>/dev/null || echo "0")
      if [[ "$behind" -gt 0 ]]; then
        echo -e "    ${YELLOW}↓${NC} $skill_name ($behind commits behind)"
        skills_with_updates=$((skills_with_updates + 1))
        updates_available=1
      fi
    done
  done < <(echo "$skills_dirs_json" | jq -c '.[]')

  if [[ $skills_checked -eq 0 ]]; then
    echo -e "    ${YELLOW}No Git-based skills found${NC}"
  elif [[ $skills_with_updates -eq 0 ]]; then
    echo -e "    ${GREEN}✓ All $skills_checked skills up to date${NC}"
  else
    echo -e "    ${YELLOW}$skills_with_updates of $skills_checked skills have updates${NC}"
  fi

  echo ""

  if [[ $updates_available -eq 1 ]]; then
    log_info "Run 'bot-update-plus update' to apply updates"
  else
    log_success "Everything is up to date!"
  fi

  return 0
}
