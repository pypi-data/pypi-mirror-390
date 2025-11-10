# Deployment Guide

This guide explains how to deploy new versions of DeepAgents using the automated deployment system.

## 🚀 Deployment Rules

**IMPORTANT**: Follow these rules for all deployments:

1. **Commit message is REQUIRED** - Always describe what changed
2. **Version type defaults to `patch`** - Most changes should be patches
3. **Use descriptive commit messages** - They become part of the release notes
4. **One deployment per change** - Don't batch unrelated changes

## 📋 Quick Deployment

Use the `deploy.sh` script for automated deployments:

```bash
# Patch version (DEFAULT) - bug fixes, small changes
./deploy.sh "Fix SubAgentMiddleware initialization bug"

# Same as above (patch is default)
./deploy.sh "Fix SubAgentMiddleware initialization bug" patch

# Minor version - new features, backwards compatible
./deploy.sh "Add new planning prompt templates" minor

# Major version - breaking changes, API changes  
./deploy.sh "Remove deprecated middleware parameter" major
```

## 📋 What the Deploy Script Does

The script performs these steps **automatically**:

1. **Validates input** - Checks commit message is provided and version type is valid
2. **Commits changes** - Stages and commits all uncommitted changes with your message
3. **Bumps version** - Updates version number in `pyproject.toml` and `src/copilotagent/__init__.py`
4. **Pushes changes** - Pushes the commit to remote repository
5. **Creates and pushes tag** - Creates version tag (e.g., `v0.1.5`) and pushes it
6. **Creates GitHub release** - Automatically creates a GitHub release (if `gh` CLI available)
7. **Triggers PyPI deployment** - Release creation triggers automatic PyPI publishing

**All in one command!** ✨

## 🔄 Automated Workflow

### The Process Flow

```
1. Developer runs deploy.sh
   ↓
2. Script commits changes and bumps version
   ↓  
3. Script pushes tag (e.g., v0.1.5)
   ↓
4. GitHub Action detects tag push
   ↓
5. Auto-release workflow creates GitHub release
   ↓
6. Release creation triggers PyPI workflow
   ↓
7. Package published to PyPI automatically
```

### GitHub Workflows

- **`auto-release.yml`** - Creates releases when version tags are pushed
- **`pypi.yml`** - Publishes to PyPI when releases are created

## 🛠️ Requirements

### For deploy.sh script:
- `bump-my-version` (auto-installed if missing)
- `gh` CLI (optional, for automatic release creation)
- Git repository with remote origin

### For GitHub Actions:
- Repository secrets:
  - `PYPI_API_TOKEN` - Your PyPI API token

## 📦 Version Types

| Type | When to Use | Example Change | Version Change |
|------|-------------|----------------|----------------|
| **patch** *(default)* | Bug fixes, small improvements, documentation | Fix initialization bug | 0.1.4 → 0.1.5 |
| **minor** | New features, backwards compatible changes | Add new middleware | 0.1.4 → 0.2.0 |
| **major** | Breaking changes, API changes | Remove deprecated feature | 0.1.4 → 1.0.0 |

### 🎯 **When in doubt, use `patch`** - it's the safe default for most changes.

## 🎯 Usage Examples

### Most Common: Bug Fixes & Small Changes (patch - default)
```bash
./deploy.sh "Fix SubAgentMiddleware initialization bug"
./deploy.sh "Update documentation with new examples"  
./deploy.sh "Improve error handling in FilesystemMiddleware"
```

### New Features (minor - requires explicit specification)
```bash
./deploy.sh "Add initial_state parameter to PlanningMiddleware" minor
./deploy.sh "Add new cloud subagent support" minor
./deploy.sh "Add ITP-Princeton planning prompts" minor
```

### Breaking Changes (major - requires explicit specification)
```bash
./deploy.sh "Remove deprecated async_create_deep_agent" major
./deploy.sh "Refactor middleware API for better usability" major
./deploy.sh "Change create_deep_agent signature" major
```

### 💡 **Remember**: If you don't specify a version type, it defaults to `patch`!

## 🔍 Monitoring Deployments

### Check Status
- **GitHub Actions**: https://github.com/yourusername/copilotagent/actions
- **PyPI Package**: https://pypi.org/project/copilotagent/
- **Releases**: https://github.com/yourusername/copilotagent/releases

### Verify Deployment
```bash
# Check latest version on PyPI
pip index versions copilotagent

# Install latest version
pip install --upgrade copilotagent

# Verify in Python
python -c "import copilotagent; print(copilotagent.__version__)"
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Deploy script fails with "Not in a git repository"
```bash
# Make sure you're in the project root
cd /path/to/baseCopilotAgent
./deploy.sh "Your message"
```

#### 2. PyPI deployment fails
- Check repository secrets are set correctly
- Verify PyPI API token in GitHub Settings → Secrets

#### 3. GitHub release not created
- Install GitHub CLI: `brew install gh` (macOS) or download from github.com/cli/cli
- Login: `gh auth login`

#### 4. Version not bumped correctly
- Check `pyproject.toml` has correct bumpversion configuration
- Verify both `pyproject.toml` and `src/copilotagent/__init__.py` are updated

### Manual Release Creation

If automatic release creation fails:

1. Go to https://github.com/yourusername/copilotagent/releases/new
2. Select the tag created by deploy.sh (e.g., `v0.1.5`)
3. Set title: `Release v0.1.5`
4. Add release notes
5. Click "Publish release"

This will trigger the PyPI deployment automatically.

## 🔧 Script Configuration

### Customizing deploy.sh

The script can be modified to:
- Change default branch (currently `main`)
- Modify release note templates
- Add additional validation steps
- Integrate with other tools

### Environment Variables

```bash
# Optional: Set default branch
export DEFAULT_BRANCH="main"

# Optional: GitHub repository
export GITHUB_REPOSITORY="yourusername/copilotagent"
```

## 📝 Best Practices

1. **Test before deploying** - Run tests locally first
2. **Write clear commit messages** - They become release notes
3. **Use semantic versioning** - Choose version type carefully
4. **Monitor deployments** - Check GitHub Actions and PyPI
5. **Keep changelog updated** - The script generates automatic changelogs

## 🔄 Rollback Process

If you need to rollback a deployment:

1. **Remove the tag**:
   ```bash
   git tag -d v0.1.5
   git push origin :refs/tags/v0.1.5
   ```

2. **Delete the release** (optional):
   ```bash
   gh release delete v0.1.5
   ```

3. **Revert version changes**:
   ```bash
   git revert HEAD
   git push origin main
   ```

Note: PyPI packages cannot be deleted, only yanked from the index.

---

## 🎉 Ready to Deploy!

Your automated deployment system is ready. Just run:

```bash
./deploy.sh "Your awesome new feature"
```

And watch the magic happen! 🚀


