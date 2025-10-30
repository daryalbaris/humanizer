# Code Review Guidelines - AI Humanizer System

**Version:** 1.0
**Date:** 2025-10-30
**Purpose:** Define code review process for quality and knowledge sharing

---

## Overview

Code reviews are mandatory for all code changes. They serve multiple purposes:
- **Quality Assurance**: Catch bugs and issues before merging
- **Knowledge Sharing**: Team members learn from each other
- **Consistency**: Ensure adherence to coding standards
- **Mentorship**: Junior developers learn from seniors

**Philosophy:** Reviews are collaborative, not confrontational. Focus on code, not the person.

---

## 1. Review Requirements

### 1.1 When Reviews Are Required

**Always required:**
- ✅ All pull requests to `main` or `develop` branches
- ✅ New features (STORY-xxx implementations)
- ✅ Bug fixes affecting core functionality
- ✅ Refactoring existing code
- ✅ Configuration changes (config.yaml, CI/CD)
- ✅ Documentation updates (if significant)

**May skip review (with Tech Lead approval):**
- Minor typo fixes in documentation
- README updates (grammar, links)
- Test data updates (fixtures)

### 1.2 Minimum Reviewers

**Standard:** 2 reviewers required
- At least **1 must be Tech Lead or Senior Developer**
- Other can be any team member

**For critical changes:** 3 reviewers
- Core system changes (orchestrator, state manager)
- Configuration changes affecting production
- Security-related changes

**For simple changes:** 1 reviewer (Tech Lead only)
- Documentation-only changes
- Test fixture additions
- Minor bug fixes (<10 lines)

### 1.3 Response Time

**Target Response Times:**
- **Initial acknowledgment**: Within 4 hours
- **Full review completion**: Within 24 hours (1 business day)
- **Follow-up on changes**: Within 12 hours

**Escalation:**
- If no response in 24 hours → Ping reviewer in chat
- If no response in 48 hours → Escalate to Tech Lead
- Urgent fixes (production issues) → Immediate review (1-2 hours)

---

## 2. Review Checklist

### 2.1 Mandatory Checks

Every reviewer must verify these items:

#### Code Quality ✅
- [ ] **Follows coding standards** (PEP 8, 120 char line length)
- [ ] **Type hints present** for all function signatures
- [ ] **Docstrings present** (Google style, all public functions)
- [ ] **No commented-out code** (delete or explain with TODO)
- [ ] **No hardcoded secrets** (API keys, passwords, tokens)
- [ ] **No print statements** (use logger instead)
- [ ] **Proper error handling** (specific exceptions, not bare `except:`)

#### Testing ✅
- [ ] **Unit tests added/updated** for new/changed code
- [ ] **Tests pass locally** (reviewer runs: `pytest tests/`)
- [ ] **Coverage ≥80%** (check: `pytest --cov=src`)
- [ ] **Edge cases tested** (empty input, None, invalid data)
- [ ] **Test names descriptive** (`test_function_scenario`)

#### Documentation ✅
- [ ] **README updated** (if public API changed)
- [ ] **Docstrings accurate** (match actual behavior)
- [ ] **Comments explain why**, not what
- [ ] **TODOs documented** (with date, name, issue link)

#### Functionality ✅
- [ ] **Code works as intended** (meets acceptance criteria)
- [ ] **No obvious bugs** (null checks, boundary conditions)
- [ ] **Handles errors gracefully** (doesn't crash on bad input)
- [ ] **Performance acceptable** (no obvious inefficiencies)

#### Git & Process ✅
- [ ] **PR title descriptive** (follows convention)
- [ ] **PR description complete** (what, why, how, testing)
- [ ] **Related story/issue linked** (STORY-xxx reference)
- [ ] **Branch up to date** with target branch
- [ ] **No merge conflicts**
- [ ] **CI pipeline passes** (lint, tests, coverage)

---

## 3. Review Workflow

### 3.1 As Pull Request Author

**Before requesting review:**

1. **Self-review first**
   ```bash
   # Run all checks locally
   flake8 src/
   black --check src/
   pytest tests/ --cov=src
   ```

2. **Write clear PR description**
   - What changed? (brief summary)
   - Why changed? (motivation, issue link)
   - How to test? (steps to verify)
   - Any risks? (breaking changes, dependencies)

3. **Tag appropriate reviewers**
   - Tech Lead (always)
   - Domain expert (if applicable)
   - Team member (for knowledge sharing)

4. **Mark draft if not ready**
   - Use "Draft PR" if work in progress
   - Convert to ready when complete

**After receiving feedback:**

1. **Respond to all comments**
   - Reply to each comment thread
   - Mark as "Resolved" when addressed
   - Explain if disagreeing (politely)

2. **Push changes**
   - New commits (don't force-push)
   - Reference comment in commit message

3. **Re-request review**
   - Click "Re-request review" button
   - Or comment: "@reviewer ready for re-review"

### 3.2 As Reviewer

**Initial review (within 24 hours):**

1. **Acknowledge PR**
   - Comment: "Reviewing, will have feedback by EOD"
   - Or add yourself as reviewer (GitHub)

2. **Checkout code locally**
   ```bash
   git fetch origin pull/123/head:pr-123
   git checkout pr-123
   ```

3. **Run tests and checks**
   ```bash
   pytest tests/ --cov=src
   flake8 src/
   ```

4. **Review code thoroughly**
   - Use GitHub's "Files changed" tab
   - Add inline comments for specific issues
   - Add summary comment for overall feedback

5. **Provide verdict**
   - **Approve**: Code is good, ready to merge
   - **Request changes**: Issues must be fixed
   - **Comment**: Suggestions, no blocking issues

**Follow-up review (within 12 hours):**

1. **Check author's responses**
   - Verify changes address feedback
   - Resolve comment threads

2. **Final approval**
   - Approve if all issues resolved
   - Merge (if you have permissions)

---

## 4. How to Provide Feedback

### 4.1 Be Constructive

**Good feedback characteristics:**
- **Specific**: Point to exact line/issue
- **Actionable**: Suggest how to fix
- **Kind**: Focus on code, not person
- **Educational**: Explain why (link to docs)

**Examples:**

✅ **Good:**
```
Line 42: This function is missing type hints.

Suggestion:
def process_text(text: str, config: dict) -> dict:
    ...

This helps catch bugs early and improves IDE support.
See: docs/coding-standards.md#type-hints
```

❌ **Bad:**
```
Line 42: No type hints
```

---

✅ **Good:**
```
Lines 15-30: This function is 50 lines long, consider breaking into smaller functions.

Suggestion:
- Extract validation logic into `validate_input()`
- Extract processing into `process_data()`
- Keep main function as orchestrator

This improves testability and readability.
Ref: docs/coding-standards.md#function-length (max 50 lines)
```

❌ **Bad:**
```
Too long, fix it
```

---

### 4.2 Use Comment Labels

**Label your comments for clarity:**

**Blocking issues (must fix):**
```
🚨 BLOCKER: Missing error handling for None input
This will crash if text is None. Add validation:
if not text:
    raise ValidationError("Text cannot be empty")
```

**Suggestions (nice to have):**
```
💡 SUGGESTION: Consider using f-string for better readability
Current: message = "Score: " + str(score)
Suggested: message = f"Score: {score}"
```

**Questions (seeking clarification):**
```
❓ QUESTION: Why use asyncio here?
The function doesn't seem to have any async operations.
Could this be a regular function instead?
```

**Praise (positive feedback):**
```
👍 NICE: Great error handling!
The fallback to lighter model is a smart approach.
```

**Learning opportunity:**
```
📚 TIL: I didn't know about this approach
This is clever! Can you add a comment explaining the algorithm?
```

### 4.3 Prioritize Feedback

**Order of importance:**

1. **Critical issues** (bugs, security, crashes)
   - Must be fixed before merge

2. **Standards violations** (PEP 8, missing tests)
   - Should be fixed for consistency

3. **Improvements** (refactoring, optimization)
   - Can be addressed in future PR

4. **Nits** (minor style, naming preferences)
   - Optional, don't block on these

**Example comment:**
```
CRITICAL: Memory leak on line 45
  - File handle not closed, use `with` statement

STANDARD: Missing docstring for public function `process_text()`
  - Add Google-style docstring

IMPROVEMENT: Consider caching this computation (line 67)
  - Would speed up repeated calls

NIT: Variable name `x` is not descriptive
  - `detection_score` would be clearer (optional)
```

---

## 5. Common Review Issues

### 5.1 Code Quality Issues

**Issue 1: Missing Type Hints**
```python
# ❌ Bad
def process(text, config):
    return result

# ✅ Fix
def process(text: str, config: dict) -> dict:
    return result

# Review comment
🚨 BLOCKER: Missing type hints (line 42)
Add type hints for all parameters and return value.
See: docs/coding-standards.md#type-hints
```

---

**Issue 2: Bare Except**
```python
# ❌ Bad
try:
    result = risky_operation()
except:
    pass

# ✅ Fix
try:
    result = risky_operation()
except (ValueError, KeyError) as e:
    logger.error(f"Operation failed: {e}")
    raise

# Review comment
🚨 BLOCKER: Bare except clause (line 67)
Catch specific exceptions, don't silently swallow all errors.
This could hide critical bugs like KeyboardInterrupt.
```

---

**Issue 3: Print Statements**
```python
# ❌ Bad
print(f"Processing text: {len(text)} chars")

# ✅ Fix
logger.info("Processing text", extra={"text_length": len(text)})

# Review comment
STANDARD: Use logger instead of print (line 23)
Print statements don't go to log files and can't be filtered.
```

---

**Issue 4: Hardcoded Values**
```python
# ❌ Bad
for i in range(7):  # Magic number
    if score < 0.15:  # What's special about 0.15?
        break

# ✅ Fix
MAX_ITERATIONS = 7
DETECTION_THRESHOLD = 0.15

for i in range(MAX_ITERATIONS):
    if score < DETECTION_THRESHOLD:
        break

# Review comment
IMPROVEMENT: Define constants at module level (lines 45, 47)
Magic numbers make code harder to maintain.
Extract to: MAX_ITERATIONS, DETECTION_THRESHOLD
```

---

### 5.2 Testing Issues

**Issue 1: No Tests**
```python
# Review comment
🚨 BLOCKER: No tests for new function `calculate_perplexity()`
Add unit tests covering:
- Valid input (happy path)
- Empty input (raises ValidationError)
- Invalid model name (raises ProcessingError)

Target: ≥80% coverage
```

---

**Issue 2: Tests Don't Cover Edge Cases**
```python
# ❌ Incomplete
def test_term_protector():
    result = protect("The steel was tested")
    assert result['status'] == 'success'

# ✅ Complete
def test_term_protector_valid_input():
    result = protect("The steel was tested")
    assert result['status'] == 'success'

def test_term_protector_empty_input():
    with pytest.raises(ValidationError):
        protect("")

def test_term_protector_none_input():
    with pytest.raises(ValidationError):
        protect(None)

# Review comment
STANDARD: Add edge case tests (test_term_protector.py)
Current test only covers happy path.
Please add tests for:
- Empty string input
- None input
- Very long input (>100K chars)
```

---

### 5.3 Documentation Issues

**Issue 1: Missing Docstring**
```python
# ❌ Bad
def calculate_perplexity(text: str, model: str = "gpt2") -> float:
    # Complex calculation...
    return ppl

# ✅ Fix
def calculate_perplexity(text: str, model: str = "gpt2") -> float:
    """Calculate GPT-2 perplexity score for text.

    Args:
        text: Input text to analyze
        model: GPT-2 model variant

    Returns:
        Perplexity score (20-150 typical range)

    Raises:
        ValidationError: If text is empty
    """
    # Implementation...

# Review comment
STANDARD: Missing docstring for public function (line 42)
Add Google-style docstring documenting:
- Purpose (what does this calculate?)
- Args (what inputs does it expect?)
- Returns (what does it return?)
- Raises (what errors can occur?)
```

---

## 6. Review Examples

### 6.1 Example 1: Feature Implementation

**PR:** Implement term_protector.py (STORY-002)

**Reviewer feedback:**

```markdown
## Overall
Good implementation! The core logic is solid. Main issues:
- Missing type hints in 2 places
- One potential bug with None handling
- Tests need edge cases

## Detailed Comments

### src/tools/term_protector.py

**Line 23: Missing type hint** 🚨 BLOCKER
```python
def _load_glossary(self, path):  # ← Add type hints
```
Should be:
```python
def _load_glossary(self, path: str) -> dict:
```

**Line 45: Potential None bug** 🚨 BLOCKER
```python
if term in text:  # ← What if term is None?
```
Add validation:
```python
if term and term in text:
```

**Line 67: Great error message!** 👍 NICE
The fallback suggestion in the error is very helpful:
```python
"Try: cp data/glossary.json.template data/glossary.json"
```

### tests/unit/test_term_protector.py

**Missing edge case tests** STANDARD
Please add tests for:
- [ ] Empty text input
- [ ] None input
- [ ] Very long text (>100K chars)
- [ ] Special characters in terms (°C, ±, etc.)

## Verdict
Request changes - please address 2 blockers, then I'll approve.
```

**Author response:**
```markdown
Thanks for the thorough review! Addressed all issues:

- ✅ Added type hints (line 23, and line 31 which I also missed)
- ✅ Added None check (line 45)
- ✅ Added 4 edge case tests (commit: abc123)

Re-requesting review.
```

---

### 6.2 Example 2: Bug Fix

**PR:** Fix: Handle empty glossary gracefully

**Reviewer feedback:**

```markdown
## Overall
Quick fix looks good! However, I noticed the root cause might be elsewhere.

## Comments

**Line 12: Fix works, but...** 💡 SUGGESTION
```python
if not glossary or len(glossary) == 0:
    logger.warning("Glossary is empty, no protection applied")
    return text
```

This fixes the symptom, but should we fail fast instead?
An empty glossary might indicate a configuration error.

Consider:
```python
if not glossary:
    raise ConfigError(
        "Glossary is empty. Check glossary.json structure."
    )
```

**Test coverage** ❓ QUESTION
Did you add a test for this case?
I don't see `test_term_protector_empty_glossary()`.

## Verdict
Approve, but please consider the failing-fast approach.
Also add a test if you have time.
```

---

## 7. Merge Process

### 7.1 Before Merge

**Author checklist:**
- [ ] All reviewer comments addressed
- [ ] All reviewers approved
- [ ] CI pipeline passes (green checkmark)
- [ ] Branch up to date with target
- [ ] No merge conflicts

**Reviewer checklist:**
- [ ] Changes reviewed and approved
- [ ] Tests pass
- [ ] Coverage ≥80%
- [ ] No critical issues remaining

### 7.2 Merge Strategy

**Preferred:** Squash and merge
- Combines all commits into one
- Keeps main branch history clean
- Easier to revert if needed

**Merge commit format:**
```
feat(term-protection): implement tier 1/2/3 protection (#42)

- Added tier-based protection logic
- Implemented context-aware rules
- Added 15 unit tests (95% coverage)

Closes STORY-002

Co-authored-by: Reviewer Name <email>
```

**Alternative:** Rebase and merge
- Use only if commits are clean and logical
- Each commit should be self-contained
- Rarely needed for this project

---

## 8. Review Anti-Patterns

### 8.1 What NOT to Do

**❌ Nitpicking without reasoning**
```
Line 23: Don't like this variable name
```
Better: Either explain why or skip it

---

**❌ Vague feedback**
```
This code is confusing
```
Better:
```
Lines 45-60 are hard to follow because:
1. Multiple nested loops
2. Variables named x, y, z
Suggest: Extract inner loop to `_process_item()` function
```

---

**❌ Personal preference wars**
```
I prefer map() over list comprehension
```
If both are valid, don't block on personal preference

---

**❌ Rubber-stamp approvals**
```
LGTM 👍
```
Always provide meaningful feedback, even if just praise

---

**❌ Reviewing line-by-line without context**
Focus on overall design first, then details

---

## 9. Review Metrics

### 9.1 Track These Metrics

**Individual metrics:**
- Average review time (target: <24 hours)
- Number of reviews completed
- Quality of feedback (helpful comments)

**Team metrics:**
- % PRs reviewed on time (target: >90%)
- Average time to merge (target: <48 hours)
- Defects caught in review (vs production)
- Review coverage (all code reviewed by 2+ people)

### 9.2 Continuous Improvement

**Monthly retrospective questions:**
- Are reviews taking too long?
- Are blockers being identified early?
- Is feedback actionable and kind?
- Are junior developers learning?
- Can we improve the checklist?

---

## 10. Tools and Automation

### 10.1 GitHub Review Features

**Use these features:**
- ✅ "Start a review" (batch comments)
- ✅ "Suggest changes" (propose code)
- ✅ "Request changes" (block merge)
- ✅ "Approve" (allow merge)
- ✅ Inline comments (specific lines)
- ✅ Resolve conversations (track progress)

### 10.2 Automated Checks

**CI pipeline checks (automatic):**
- Lint: flake8 passes
- Format: black compliance
- Tests: pytest passes
- Coverage: ≥75%

**Reviewer focuses on:**
- Logic correctness
- Design quality
- Test coverage (≥80%)
- Documentation
- User experience

---

## 11. Special Cases

### 11.1 Urgent Hotfixes

**Process for production bugs:**
1. Create PR with "HOTFIX" label
2. Tag Tech Lead immediately
3. Review within 1 hour (not 24)
4. Merge after 1 approval (not 2)
5. Follow up with post-mortem

**Reduced checklist:**
- ✅ Fix works (test in production-like environment)
- ✅ No obvious side effects
- ✅ Test added (can be quick integration test)
- Skip: Perfect code style, comprehensive docs

### 11.2 Large Refactorings

**For PRs >500 lines:**
1. **Pre-review discussion**
   - Discuss approach before implementation
   - Get Tech Lead approval on design

2. **Break into smaller PRs**
   - Part 1: Structure changes (no logic change)
   - Part 2: Logic changes (one module at a time)
   - Part 3: Tests and documentation

3. **Pair programming**
   - Consider pair programming instead of review
   - Real-time collaboration more efficient

---

## 12. Learning Resources

### Internal Resources
- `docs/coding-standards.md` - Code style guide
- `docs/architecture.md` - System design
- `docs/prd.md` - Product requirements

### External Resources
- [Google Code Review Guide](https://google.github.io/eng-practices/review/)
- [Conventional Comments](https://conventionalcomments.org/)
- [How to Review Code](https://mtlynch.io/human-code-reviews-1/)

---

## Summary Checklist

**For every PR review:**

1. **Initial pass (5-10 min)**
   - [ ] Read PR description
   - [ ] Check CI status (green?)
   - [ ] Scan changed files
   - [ ] Form initial impression

2. **Detailed review (20-30 min)**
   - [ ] Checkout code locally
   - [ ] Run tests
   - [ ] Review code logic
   - [ ] Check for standards violations
   - [ ] Verify tests cover changes

3. **Provide feedback (10-15 min)**
   - [ ] Leave inline comments
   - [ ] Write summary comment
   - [ ] Label: Approve / Request changes / Comment
   - [ ] Be kind and constructive

**Total time: 35-55 minutes per PR**

---

**Status:** ✅ Code Review Guidelines Complete
**Checklist Items:** 30+ checks
**Examples Provided:** Yes
**Anti-patterns Documented:** Yes

**Last Updated:** 2025-10-30
**Next:** Git Workflow Documentation (`docs/git-workflow.md`)
