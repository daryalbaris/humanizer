# Pull Request

## 📋 Description
<!-- Provide a brief description of the changes in this PR -->



## 🔗 Related Story/Issue
<!-- Link to the story or issue this PR addresses -->
- Closes: STORY-XXX or #issue-number
- Related: (optional links to related PRs or issues)


## 🔨 Changes Made
<!-- List the key changes in this PR -->
- [ ] Change 1
- [ ] Change 2
- [ ] Change 3


## 🧪 Testing
<!-- Describe how these changes were tested -->

### Test Coverage
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated (if applicable)
- [ ] All tests pass locally (`pytest tests/`)
- [ ] Coverage meets or exceeds 80% for new code

### Manual Testing
<!-- Describe manual testing performed -->
1. Test scenario 1
2. Test scenario 2

**Test Environment:**
- Python version:
- OS:
- Dependencies installed: Yes/No


## 📸 Screenshots (if applicable)
<!-- Add screenshots for UI changes or visual outputs -->



## ✅ Review Checklist
<!-- Confirm the following before requesting review -->

### Code Quality
- [ ] Code follows PEP 8 style guide (120 char line length)
- [ ] Type hints added for all function signatures
- [ ] Docstrings added (Google-style format) for all public functions
- [ ] No hardcoded secrets or API keys
- [ ] No commented-out code (unless explicitly documented why)
- [ ] Logging added for key operations (JSON format)
- [ ] Error handling implemented (with appropriate custom exceptions)

### Testing & Quality
- [ ] Unit tests added for new functionality
- [ ] Edge cases covered in tests
- [ ] Test names are descriptive (test_<function>_<scenario>_<expected>)
- [ ] No flake8 warnings (`flake8 src/`)
- [ ] Code formatted with black (`black src/`)
- [ ] Type checking passes (`mypy src/` - optional but recommended)

### Documentation
- [ ] README.md updated (if user-facing changes)
- [ ] Docstrings accurate and complete
- [ ] Configuration changes documented in config/config.yaml comments
- [ ] Data format changes reflected in docs/data-formats.md

### Functionality
- [ ] Feature works as intended
- [ ] No regressions introduced
- [ ] Handles edge cases gracefully
- [ ] Performance impact considered (if applicable)

### Git & Process
- [ ] PR description is clear and complete
- [ ] Commit messages follow convention (`<type>(<scope>): <subject>`)
- [ ] Branch is up-to-date with develop
- [ ] No merge conflicts
- [ ] CI pipeline passes (lint, test, coverage)


## 🚨 Breaking Changes
<!-- List any breaking changes and migration steps -->
- [ ] This PR contains breaking changes

**Breaking changes:**
-


## 📝 Additional Notes
<!-- Any additional context, decisions, or trade-offs made -->



## 👥 Reviewers
<!-- Tag reviewers using @username -->
@reviewer1 @reviewer2

---

**Definition of Done:**
- [ ] Code reviewed by at least 2 team members
- [ ] All CI checks pass (lint, format, test, coverage ≥75%)
- [ ] Documentation updated
- [ ] Tests pass locally and in CI
- [ ] No unresolved review comments
- [ ] Ready to merge to develop branch
