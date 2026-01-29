# Publishing Guide for Bot Update Skill

## Pre-Publication Checklist

- [x] Remove personal data (paths, agent names, etc.)
- [x] Set author to pasogott
- [x] MIT License included
- [x] Dynamic workspace detection (no hardcoded paths)
- [x] Generic examples in documentation
- [x] All scripts executable
- [x] package.json configured
- [x] .skills.json configured
- [x] README with installation instructions

## Files Ready for Publication

```
/tmp/bot-update-publish/
├── backup-bot-dryrun.sh     # Dry run preview
├── backup-bot-full.sh       # Full backup
├── restore-bot.sh           # Restore
├── validate-setup.sh             # Validation
├── check-upstream.sh             # Update checker
├── config.json                   # Skill config
├── package.json                  # npm metadata
├── .skills.json               # Skills metadata
├── LICENSE                       # MIT License
├── README.md                     # Quick start
├── SKILL.md                      # Full documentation
├── UPDATE_CHECKLIST.md          # Step-by-step guide
└── QUICK_REFERENCE.md           # Command cheat sheet
```

## Publishing to npm

### 1. Prepare npm package

```bash
cd /tmp/bot-update-publish

# Verify package.json
cat package.json

# Test installation locally
npm pack
```

### 2. Publish to npm

```bash
# Login to npm (if not already)
npm login

# Publish (scoped package)
npm publish --access public
```

### 3. Verify publication

```bash
# Check package page
open https://www.npmjs.com/package/@bot/skill-update

# Test installation
npm install -g @bot/skill-update
```

## Publishing to Skills

### 1. Create repository

```bash
# Option A: Create new repo
gh repo create pasogott/bot-skill-update --public

# Option B: Fork Bot repo and add as subdirectory
# Follow Skills contribution guidelines
```

### 2. Push to repository

```bash
cd /tmp/bot-update-publish

# Initialize git
git init
git add .
git commit -m "Initial release: Bot Update Skill v1.0.0

Features:
- Dynamic workspace detection
- Multi-agent support
- Dry run preview
- Full backup & restore
- Git integration
- Validation checks

Author: Pascal Schott (@pasogott)
License: MIT"

# Push to GitHub
git remote add origin https://github.com/pasogott/bot-skill-update.git
git branch -M main
git push -u origin main
```

### 3. Submit to Skills

Visit https://skills.com and follow submission process:

1. Navigate to "Submit Skill"
2. Provide repository URL
3. Skills will read `.skills.json` automatically
4. Review and submit

## Installation Instructions for Users

### Via Skills (Recommended)

```bash
bot skills install bot-update
```

### Via npm

```bash
npm install -g @bot/skill-update

# Link to skills directory
ln -s /usr/local/lib/node_modules/@bot/skill-update ~/.skills/bot-update
```

### Manual Installation

```bash
git clone https://github.com/pasogott/bot-skill-update.git ~/.skills/bot-update
chmod +x ~/.skills/bot-update/*.sh
```

## Post-Publication

### 1. Create GitHub Release

```bash
# Tag release
git tag -a v1.0.0 -m "Release v1.0.0

Features:
- Dynamic workspace detection
- Multi-agent support
- Dry run preview
- Full backup & restore
- Git integration
- Validation checks"

git push origin v1.0.0

# Create release on GitHub
gh release create v1.0.0 \
  --title "v1.0.0 - Initial Release" \
  --notes "First public release of Bot Update Skill"
```

### 2. Announce

- Post on Bot Discord/Community
- Tweet/share if applicable
- Add to Bot skills documentation

### 3. Monitor

- Watch GitHub issues
- Respond to npm feedback
- Update documentation as needed

## Version Bumping (Future)

### Update version

```bash
# Edit package.json version
# Edit .skills.json version
# Edit config.json version

# Commit
git commit -am "Bump version to 1.1.0"

# Tag
git tag v1.1.0
git push origin v1.1.0

# Publish
npm version patch  # or minor, major
npm publish
```

## Maintenance Checklist

- [ ] Keep aligned with Bot breaking changes
- [ ] Test with new Bot releases
- [ ] Update documentation
- [ ] Respond to issues
- [ ] Add new features based on feedback

## Repository Structure

```
bot-skill-update/
├── .github/
│   └── workflows/
│       └── test.yml          # CI/CD
├── backup-bot-dryrun.sh
├── backup-bot-full.sh
├── restore-bot.sh
├── validate-setup.sh
├── check-upstream.sh
├── config.json
├── package.json
├── .skills.json
├── LICENSE
├── README.md
├── SKILL.md
├── UPDATE_CHECKLIST.md
├── QUICK_REFERENCE.md
└── .gitignore
```

## Quality Checks Before Release

- [ ] All scripts have shebang (`#!/bin/bash`)
- [ ] All scripts are executable (`chmod +x`)
- [ ] No hardcoded personal paths
- [ ] No sensitive data (keys, tokens, etc.)
- [ ] Documentation is clear and generic
- [ ] Examples use placeholder data
- [ ] License is properly attributed
- [ ] package.json is valid
- [ ] .skills.json is valid

## Contact

**Author**: Pascal Schott  
**GitHub**: [@pasogott](https://github.com/pasogott)  
**Issues**: Report via GitHub Issues  
**License**: MIT

---

Ready to publish! 🚀
