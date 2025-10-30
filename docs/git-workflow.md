# Git Workflow - AI Humanizer System

**Version:** 1.0
**Date:** 2025-10-30
**Purpose:** Define Git branching strategy and commit conventions

---

## Overview

This document defines how we use Git for version control, including:
- Branching strategy (what branches exist, when to create them)
- Commit message format (how to write good commits)
- Pull request process (how to merge code)
- Branch protection rules (what's required before merging)

**Philosophy:** Keep main branch stable, develop in isolation, merge frequently.

---

## 1. Branching Strategy

### 1.1 Branch Types

```
main (production-ready)
  ↑
develop (integration)
  ↑
feature/STORY-XXX-description (new features)
  ↑
bugfix/issue-123-description (bug fixes)
```

#### **main** Branch
- **Purpose:** Production-ready code only
- **Protection:** Highest level
  - Requires 2 approvals
  - CI must pass
  - No direct commits (must PR)
  - No force push
- **Who can merge:** Tech Lead only
- **Deployment:** Auto-deploys to production (if applicable)

#### **develop** Branch
- **Purpose:** Integration branch for features
- **Protection:** High level
  - Requires 2 approvals
  - CI must pass
  - No direct commits (must PR)
- **Who can merge:** Tech Lead or Senior Developers
- **Deployment:** Auto-deploys to staging (if applicable)

#### **feature/** Branches
- **Format:** `feature/STORY-XXX-description`
- **Purpose:** New feature development
- **Examples:**
  - `feature/STORY-002-term-protection`
  - `feature/STORY-003-paraphrasing-engine`
  - `feature/STORY-007-orchestrator-prompt`
- **Lifetime:** Deleted after merge
- **Branch from:** `develop`
- **Merge to:** `develop`

#### **bugfix/** Branches
- **Format:** `bugfix/issue-123-description`
- **Purpose:** Non-urgent bug fixes
- **Examples:**
  - `bugfix/issue-42-memory-leak`
  - `bugfix/issue-67-logging-format`
- **Lifetime:** Deleted after merge
- **Branch from:** `develop`
- **Merge to:** `develop`

#### **hotfix/** Branches
- **Format:** `hotfix/critical-issue-description`
- **Purpose:** Urgent production fixes
- **Examples:**
  - `hotfix/detection-score-crash`
  - `hotfix/api-timeout`
- **Lifetime:** Deleted after merge
- **Branch from:** `main`
- **Merge to:** `main` AND `develop` (two PRs)

#### **release/** Branches (optional)
- **Format:** `release/v1.0.0`
- **Purpose:** Prepare for production release
- **Process:**
  1. Branch from `develop`
  2. Final testing, bug fixes only
  3. Merge to `main` with tag
  4. Merge back to `develop`
- **Use:** Only for major releases

---

### 1.2 Branching Workflow

**Standard Feature Development:**

```bash
# 1. Start from latest develop
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/STORY-002-term-protection

# 3. Develop & commit
git add src/tools/term_protector.py
git commit -m "feat(term-protection): implement tier 1 protection"

# 4. Push to remote
git push origin feature/STORY-002-term-protection

# 5. Create Pull Request (via GitHub/GitLab UI)
#    - Base: develop
#    - Head: feature/STORY-002-term-protection
#    - Title: "feat(term-protection): Implement tier 1/2/3 protection"
#    - Link: STORY-002

# 6. After approval & merge, delete branch
git checkout develop
git pull origin develop
git branch -d feature/STORY-002-term-protection
```

**Hotfix Workflow:**

```bash
# 1. Branch from main
git checkout main
git pull origin main
git checkout -b hotfix/detection-score-crash

# 2. Fix bug
git add src/tools/detector_processor.py
git commit -m "fix(detector): handle None detection score"

# 3. Create PR to main
#    - Get immediate review (1 hour)
#    - Merge after 1 approval

# 4. Also merge to develop
git checkout develop
git pull origin develop
git merge hotfix/detection-score-crash
git push origin develop

# 5. Delete branch
git branch -d hotfix/detection-score-crash
```

---

## 2. Commit Message Format

### 2.1 Convention

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Example:**
```
feat(term-protection): implement tier 2 context-aware protection

Added context-aware protection for tier 2 terms with synonym handling.
Protected terms can now be paraphrased if meaning preserved.

Closes STORY-002
```

### 2.2 Type

**Required types:**

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(orchestrator): add translation chain` |
| `fix` | Bug fix | `fix(validator): correct BERTScore threshold` |
| `docs` | Documentation only | `docs(readme): update installation steps` |
| `style` | Code style (formatting, no logic change) | `style(utils): format with black` |
| `refactor` | Code refactoring (no feature/bug change) | `refactor(term-protector): extract helper` |
| `test` | Add/update tests | `test(term-protector): add edge cases` |
| `chore` | Maintenance (build, CI, dependencies) | `chore(deps): update spaCy to 3.7.3` |
| `perf` | Performance improvement | `perf(perplexity): cache model loading` |

### 2.3 Scope

**Component names:**

- `orchestrator` - Orchestrator prompt and logic
- `term-protection` - Term protector tool
- `paraphraser` - Paraphraser processor
- `fingerprints` - Fingerprint remover
- `burstiness` - Burstiness enhancer
- `detector` - Detector processor
- `perplexity` - Perplexity calculator
- `validator` - Validation tool
- `state` - State manager
- `utils` - Utility modules
- `config` - Configuration files
- `ci` - CI/CD pipeline
- `docs` - Documentation
- `tests` - Test files
- `deps` - Dependencies

### 2.4 Subject

**Rules:**
- Use imperative mood ("add" not "added" or "adds")
- Don't capitalize first letter
- No period at end
- Max 72 characters
- Be specific but concise

**Good examples:**
```
feat(term-protection): add tier 3 minimal protection
fix(validator): handle missing BERTScore model
docs(api): document JSON schemas for all tools
test(burstiness): add test for sentence merging
```

**Bad examples:**
```
Fixed bug                           (too vague)
feat(term-protection): Added.       (past tense, period)
FEAT(TERM-PROTECTION): ADD FEATURE  (all caps)
feat: added the new term protection feature that was requested (too long)
```

### 2.5 Body

**When to add body:**
- Change is non-trivial (>10 lines)
- Need to explain *why*, not what
- Multiple changes in one commit

**Format:**
- Wrap at 72 characters
- Blank line after subject
- Explain motivation, context, approach
- Use bullet points for multiple items

**Example:**
```
feat(orchestrator): implement early termination logic

Early termination stops iteration if improvement <2% between iterations.
This saves processing time when further improvements are unlikely.

Implementation:
- Track detection score change between iterations
- Compare to threshold (config.yaml: early_termination_improvement)
- Exit loop and save final checkpoint

Refs STORY-007
```

### 2.6 Footer

**Purpose:** Link to issues, breaking changes, co-authors

**Examples:**
```
Closes STORY-002
Closes #42
Refs #67

BREAKING CHANGE: Config format changed, update config.yaml

Co-authored-by: Jane Doe <jane@example.com>
```

---

## 3. Commit Best Practices

### 3.1 Commit Frequency

**Do:**
- ✅ Commit often (every logical change)
- ✅ Commit complete units of work
- ✅ Commit before switching tasks

**Don't:**
- ❌ Commit broken code
- ❌ Commit WIP with "wip" message
- ❌ Mix multiple unrelated changes

**Example workflow:**
```bash
# Good: Multiple focused commits
git commit -m "feat(term-protection): add tier 1 protection"
git commit -m "feat(term-protection): add tier 2 context rules"
git commit -m "test(term-protection): add unit tests"
git commit -m "docs(term-protection): update docstrings"

# Bad: One giant commit
git commit -m "implement term protection"
```

### 3.2 Commit Size

**Target:** 50-200 lines per commit

**Small commits:**
- Easier to review
- Easier to revert
- Clearer history

**When commits get large (>500 lines):**
- Break into multiple commits
- Use `git add -p` (interactive staging)

### 3.3 Amending Commits

**Use `--amend` for:**
- Fixing typos in last commit
- Adding forgotten files to last commit
- **Only if not pushed yet!**

```bash
# Fix typo in last commit
git commit --amend -m "feat(term-protection): correct tier 1 handling"

# Add forgotten file to last commit
git add tests/test_term_protector.py
git commit --amend --no-edit
```

**⚠️ Warning:** Never amend commits that are already pushed to shared branches!

---

## 4. Pull Request Process

### 4.1 Creating a Pull Request

**Before creating PR:**

```bash
# 1. Rebase on latest develop (avoid merge commits)
git checkout develop
git pull origin develop
git checkout feature/STORY-002-term-protection
git rebase develop

# 2. Run all checks locally
flake8 src/
black --check src/
pytest tests/ --cov=src

# 3. Push to remote
git push origin feature/STORY-002-term-protection
```

**PR Title Format:**
```
<type>(<scope>): <subject>

Example:
feat(term-protection): Implement tier 1/2/3 protection system
fix(validator): Correct BERTScore threshold comparison
docs(architecture): Update component interaction diagrams
```

**PR Description Template:**
See `.github/PULL_REQUEST_TEMPLATE.md` (created separately)

### 4.2 PR Review Process

1. **Author creates PR** → Tags reviewers
2. **Reviewers review** → Leave comments
3. **Author addresses feedback** → Push new commits
4. **Reviewers re-review** → Approve
5. **Author merges** → Squash and merge (preferred)
6. **Author deletes branch** → Cleanup

### 4.3 Merge Strategies

**Squash and Merge (Preferred):**
- Combines all commits into one
- Clean linear history
- Easy to revert entire feature

```bash
# GitHub does this automatically when you click "Squash and merge"
# Resulting commit:
feat(term-protection): Implement tier 1/2/3 protection (#42)

- Added tier 1 absolute protection
- Added tier 2 context-aware protection
- Added tier 3 minimal protection
- 15 unit tests added (95% coverage)

Closes STORY-002
```

**Merge Commit (Rare):**
- Preserves all commits
- Use only if commits are clean and meaningful
- Creates merge commit

**Rebase and Merge (Avoid):**
- Rewrites history
- Can cause confusion
- Not recommended for this project

---

## 5. Branch Protection Rules

### 5.1 Main Branch Protection

**Settings (configure in GitHub/GitLab):**

```yaml
Branch: main
Protection:
  - ✅ Require pull request before merging
  - ✅ Require 2 approvals
  - ✅ Dismiss stale approvals when new commits pushed
  - ✅ Require review from code owners (Tech Lead)
  - ✅ Require status checks to pass (CI pipeline)
  - ✅ Require branches to be up to date
  - ✅ Require conversation resolution
  - ✅ Require signed commits (optional)
  - ✅ Include administrators (no exceptions)
  - ✅ Restrict push access (Tech Lead only)
  - ✅ Restrict force pushes (none allowed)
  - ✅ Restrict deletions (cannot delete main)
```

### 5.2 Develop Branch Protection

**Settings:**

```yaml
Branch: develop
Protection:
  - ✅ Require pull request before merging
  - ✅ Require 2 approvals
  - ✅ Require status checks to pass (CI pipeline)
  - ✅ Require branches to be up to date
  - ✅ Restrict force pushes (none allowed)
```

### 5.3 Feature Branch Protection

**Settings:**
- No protection (free development)
- Delete after merge (automatic cleanup)

---

## 6. Common Git Operations

### 6.1 Update Feature Branch with Latest Develop

```bash
# Option 1: Rebase (preferred - cleaner history)
git checkout feature/STORY-002-term-protection
git fetch origin
git rebase origin/develop

# If conflicts, resolve them:
# 1. Fix conflicts in files
# 2. git add <resolved-files>
# 3. git rebase --continue

# Force push (only if not merged yet)
git push origin feature/STORY-002-term-protection --force-with-lease

# Option 2: Merge (if already pushed and reviewed)
git checkout feature/STORY-002-term-protection
git fetch origin
git merge origin/develop
git push origin feature/STORY-002-term-protection
```

### 6.2 Undo Last Commit (Not Pushed)

```bash
# Undo commit, keep changes
git reset --soft HEAD~1

# Undo commit, discard changes
git reset --hard HEAD~1
```

### 6.3 Undo Pushed Commit

```bash
# Create revert commit (safe, preserves history)
git revert HEAD
git push origin feature/STORY-002-term-protection

# Or revert specific commit
git revert abc123
git push origin feature/STORY-002-term-protection
```

### 6.4 Interactive Rebase (Clean Up Commits)

```bash
# Clean up last 3 commits before PR
git rebase -i HEAD~3

# In editor:
pick abc123 feat(term-protection): add tier 1
squash def456 fix typo
squash ghi789 update tests

# Result: 3 commits → 1 commit
```

### 6.5 Cherry-Pick Commit

```bash
# Copy commit from another branch
git checkout develop
git cherry-pick abc123  # Commit SHA from feature branch
```

### 6.6 Stash Changes

```bash
# Save work in progress
git stash save "WIP: term protection refactoring"

# List stashes
git stash list

# Apply stash
git stash apply stash@{0}

# Apply and remove from stash list
git stash pop
```

---

## 7. Git Troubleshooting

### 7.1 Merge Conflicts

**When it happens:**
- Two branches modify same file
- Automatic merge fails

**How to resolve:**

```bash
# 1. Start merge/rebase
git merge develop
# or
git rebase develop

# 2. Git shows conflicts:
Auto-merging src/tools/term_protector.py
CONFLICT (content): Merge conflict in src/tools/term_protector.py

# 3. Open file, look for conflict markers:
<<<<<<< HEAD
# Your changes
def process(text: str) -> dict:
=======
# Their changes
def process(text: str, config: dict) -> dict:
>>>>>>> develop

# 4. Resolve conflict (keep one, both, or combine)
def process(text: str, config: dict) -> dict:
    # Combined both changes

# 5. Mark as resolved
git add src/tools/term_protector.py

# 6. Continue merge/rebase
git merge --continue
# or
git rebase --continue
```

### 7.2 Accidentally Committed to Wrong Branch

```bash
# You committed to develop instead of feature branch
git checkout develop

# Option 1: Move commits to new branch
git branch feature/STORY-002-term-protection  # Create branch with current commits
git reset --hard origin/develop  # Reset develop to remote
git checkout feature/STORY-002-term-protection  # Switch to new branch

# Option 2: Cherry-pick to correct branch
git log  # Find commit SHA (abc123)
git checkout feature/STORY-002-term-protection
git cherry-pick abc123
git checkout develop
git reset --hard HEAD~1  # Remove wrong commit
```

### 7.3 Pushed Secret/Sensitive Data

```bash
# ⚠️ URGENT: Remove sensitive data from history

# 1. Remove file from history (USE WITH CAUTION!)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch config/.env" \
  --prune-empty --tag-name-filter cat -- --all

# 2. Force push (requires branch protection bypass)
git push origin --force --all

# 3. Notify team (all must re-clone)

# 4. Rotate compromised secrets immediately
# 5. Add to .gitignore to prevent recurrence
```

**Prevention:**
- Always use `.gitignore` for secrets
- Use `.env.template` (not `.env`)
- Use pre-commit hooks to block secrets

---

## 8. Git Hooks

### 8.1 Pre-Commit Hook

**Purpose:** Run checks before allowing commit

**Setup:**
```bash
# Install pre-commit framework
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
        language_version: python3.10

  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
        args: ['--max-line-length=120']

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-added-large-files
        args: ['--maxkb=1000']
EOF

# Install hooks
pre-commit install

# Now runs automatically on git commit
```

### 8.2 Pre-Push Hook

**Purpose:** Run tests before allowing push

```bash
# Create .git/hooks/pre-push
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash

echo "Running tests before push..."
pytest tests/ --cov=src --cov-fail-under=75

if [ $? -ne 0 ]; then
    echo "Tests failed! Push aborted."
    exit 1
fi

echo "Tests passed!"
EOF

chmod +x .git/hooks/pre-push
```

---

## 9. Git Workflow Diagram

```
┌──────────┐
│   main   │ ← Production-ready (v1.0, v1.1, etc.)
└────┬─────┘
     │
     │ ← hotfix (urgent only)
     │
┌────▼─────┐
│ develop  │ ← Integration branch
└────┬─────┘
     │
     ├─► feature/STORY-002-term-protection
     │       │
     │       ├─ commit: feat(term-protection): add tier 1
     │       ├─ commit: feat(term-protection): add tier 2
     │       └─ commit: test(term-protection): add tests
     │       │
     │       └─► Pull Request → Code Review → Merge → develop
     │
     ├─► feature/STORY-003-paraphrasing-engine
     │       └─► Pull Request → Code Review → Merge → develop
     │
     └─► bugfix/issue-42-memory-leak
             └─► Pull Request → Code Review → Merge → develop

Once all features for v1.0 complete:
develop → Pull Request → Code Review → Merge → main (tagged v1.0.0)
```

---

## 10. Quick Reference

### Common Commands

```bash
# Create feature branch
git checkout -b feature/STORY-XXX-description

# Commit
git add .
git commit -m "feat(scope): subject"

# Push
git push origin feature/STORY-XXX-description

# Update from remote
git pull origin develop

# Rebase on develop
git rebase origin/develop

# Squash last 3 commits
git rebase -i HEAD~3

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Stash changes
git stash save "message"
git stash pop

# View commit history
git log --oneline --graph --all

# Check branch status
git status
git branch -a
```

---

## Summary

**Remember:**
1. **Never commit directly to main or develop**
2. **Use feature branches** for all work
3. **Write meaningful commit messages** (type, scope, subject)
4. **Create PRs for all changes** (no exceptions)
5. **Get 2 approvals** before merging
6. **Squash and merge** to keep history clean
7. **Delete branches** after merging
8. **Keep branches up to date** with develop

**Need help?**
- Read the docs: `docs/git-workflow.md` (this file)
- Ask Tech Lead
- Git book: https://git-scm.com/book

---

**Status:** ✅ Git Workflow Complete
**Branching Strategy:** Defined
**Commit Conventions:** Specified
**Common Operations:** Documented
**Troubleshooting:** Provided

**Last Updated:** 2025-10-30
**Next:** CI/CD Pipeline (`.github/workflows/ci.yml`)
