# User Story 1: Development Environment & Infrastructure Setup

**Story ID:** STORY-001
**Epic:** EPIC-001 (AI Humanizer System)
**Priority:** Critical (Foundation)
**Estimated Effort:** 2 weeks (38 hours)
**Dependencies:** None

---

## User Story

**As a** developer setting up the AI Humanizer System
**I want** a complete development environment with all dependencies, tools, and configuration
**So that** I can begin developing and testing the humanization components without environment issues

---

## Description

Establish the complete development environment, dependency management, and infrastructure needed for all subsequent development. This includes Python environment setup, Claude Code integration, development tooling, and project structure.

This is the foundation story that must be completed before any other development work can begin.

---

## Acceptance Criteria

### Environment Setup

- [ ] Python 3.11.x virtual environment created and activated
- [ ] All dependencies installed without version conflicts:
  - spaCy 3.7.x with en_core_web_trf transformer model
  - transformers 4.35.x (GPT-2 base model)
  - bert-score 0.3.13
  - nltk 3.8.x with punkt tokenizer
  - Pydantic 2.5.x
  - structlog 24.1.x
  - ruff 0.2.x
  - mypy 1.8.x
  - pytest 8.0.x
- [ ] spaCy model downloaded and verified: `python -m spacy download en_core_web_trf`
- [ ] transformers models cached locally (GPT-2 base, BERT)
- [ ] NLTK data downloaded: `nltk.download('punkt')`

### Project Structure

- [ ] Directory structure matches architecture specification:
  ```
  ai-humanizer/
  ├── .humanizer/           # Runtime data (user papers, state)
  ├── src/
  │   ├── tools/            # 9 Python tools
  │   ├── models/           # Pydantic data models
  │   ├── utils/            # Shared utilities
  │   └── __init__.py
  ├── tests/
  │   ├── unit/
  │   ├── integration/
  │   ├── fixtures/
  │   └── conftest.py
  ├── docs/
  ├── scripts/
  ├── requirements.txt
  ├── pyproject.toml       # Ruff, mypy config
  ├── pytest.ini
  └── README.md
  ```

### Configuration Management

- [ ] Configuration system functional:
  - Environment variables loaded (.env file support)
  - Logging infrastructure operational (structlog JSON to stderr)
  - Debug utilities available
- [ ] Configuration files created:
  - `pyproject.toml` (ruff, mypy settings)
  - `pytest.ini` (test configuration)
  - `.env.template` (example environment variables)

### Development Tooling

- [ ] Code quality tools configured:
  - Ruff linting and formatting (line length: 100)
  - mypy type checking (strict mode)
  - Pre-commit hooks (optional but recommended)
- [ ] Testing infrastructure ready:
  - pytest configured
  - Test fixtures directory created
  - Sample test files demonstrate structure

### Sandbox Deployment Setup

- [ ] Virtual environment verified in Claude Code sandbox
- [ ] All Python tools executable via Bash tool
- [ ] JSON stdin/stdout communication tested
- [ ] File system access verified (.humanizer/ directory writable)
- [ ] Model caching verified (models persist across sessions)

### Documentation

- [ ] Installation guide created (README.md):
  - Windows setup instructions
  - macOS setup instructions
  - Linux setup instructions
  - Claude Code sandbox deployment guide
- [ ] Troubleshooting guide started:
  - Common dependency conflicts
  - spaCy model download issues
  - Environment activation problems
- [ ] Setup script created (`scripts/setup.sh` or `setup.py`):
  - Automates virtual environment creation
  - Installs all dependencies
  - Downloads required models
  - Verifies installation
  - Runs basic health checks

---

## Technical Specifications

### Python Version

- **Target:** Python 3.11.x
- **Rationale:** Modern type hints, match statements, stable LTS release
- **Compatibility:** Must work on Python 3.11.0 through 3.11.latest

### Dependency Versions (Exact Pinning)

```txt
# requirements.txt
spacy==3.7.4
en-core-web-trf @ https://github.com/explosion/spacy-models/releases/download/en_core_web_trf-3.7.3/en_core_web_trf-3.7.3-py3-none-any.whl
transformers==4.35.2
torch==2.1.2
bert-score==0.3.13
nltk==3.8.1
pydantic==2.5.3
structlog==24.1.0
ruff==0.2.2
mypy==1.8.0
pytest==8.0.2
pytest-cov==4.1.0
```

### Development Environment Requirements

**Hardware:**
- CPU: 4 cores minimum, 8 cores recommended
- RAM: 8 GB minimum, 16 GB recommended
- Storage: 5 GB free (ML models: 3 GB, papers: 50 MB)

**Software:**
- Operating System: Windows 10+, macOS 11+, Ubuntu 20.04+
- Python 3.11.x installed
- Git for version control
- Claude Code CLI (user's subscription)

### Configuration Files

**pyproject.toml:**
```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "N", "UP", "B", "C4", "SIM"]

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

---

## Tasks

### Task 1: Python Environment Setup (4 hours)

1. Install Python 3.11.x if not present
2. Create virtual environment: `python3.11 -m venv venv`
3. Activate virtual environment
4. Upgrade pip: `pip install --upgrade pip`
5. Install requirements: `pip install -r requirements.txt`
6. Verify installation: `pip list`

### Task 2: ML Model Downloads (2 hours)

1. Download spaCy transformer model: `python -m spacy download en_core_web_trf`
2. Verify spaCy model: `python -c "import spacy; nlp = spacy.load('en_core_web_trf'); print('✓ spaCy model loaded')"`
3. Download NLTK data: `python -c "import nltk; nltk.download('punkt')"`
4. Cache transformers models (auto-download on first use):
   - GPT-2 base: `transformers.GPT2LMHeadModel.from_pretrained('gpt2')`
   - BERT: `bert_score` will auto-download on first use

### Task 3: Project Structure Creation (2 hours)

1. Create directory structure (see Acceptance Criteria)
2. Create `__init__.py` files in all package directories
3. Create placeholder files:
   - `src/tools/term_protector.py` (stub)
   - `src/models/paper.py` (stub with Paper Pydantic model)
   - `tests/test_example.py` (sample test)
4. Create `.gitignore` (Python, venv, .humanizer/, etc.)

### Task 4: Configuration & Tooling (4 hours)

1. Create `pyproject.toml` with ruff and mypy configuration
2. Create `pytest.ini` with test settings
3. Create `.env.template` with example variables
4. Configure structlog logging
5. Create development utilities in `src/utils/`:
   - `json_io.py` (atomic writes, JSON serialization)
   - `logger.py` (structured logging setup)
   - `atomic_write.py` (atomic file writes pattern)

### Task 5: Claude Code Sandbox Integration (6 hours)

1. Test Python execution via Claude Code Bash tool:
   - Verify venv activation in sandbox
   - Test JSON stdin/stdout communication
   - Verify file I/O in sandbox environment
2. Create sandbox verification script:
   - Check Python version (3.11.x)
   - Test spaCy model loading
   - Test transformers model access
   - Test JSON serialization
3. Document Claude Code execution patterns:
   - How to run Python tools from orchestrator
   - Environment variable access
   - File path conventions in sandbox
4. Create troubleshooting guide for sandbox issues

### Task 6: Setup Automation & Documentation (8 hours)

1. Create automated setup script (`scripts/setup.sh`):
   ```bash
   #!/bin/bash
   # 1. Check Python version (3.11.x)
   # 2. Create virtual environment
   # 3. Install dependencies
   # 4. Download spaCy model
   # 5. Download NLTK data
   # 6. Create .humanizer/ directory structure
   # 7. Run verification tests
   # 8. Print success message with next steps
   ```
2. Write installation guide (README.md):
   - Prerequisites
   - Quick start (5 commands or less)
   - Platform-specific instructions
   - Claude Code sandbox setup
3. Write troubleshooting guide:
   - spaCy model download failures
   - Dependency version conflicts
   - Environment activation issues
   - Memory/storage requirements

### Task 7: Verification & Testing (12 hours)

1. Test installation on clean VMs:
   - Windows 10/11
   - macOS 11+
   - Ubuntu 20.04
2. Verify all dependencies load without errors
3. Run sample imports to test model loading:
   ```python
   import spacy
   import transformers
   import bert_score
   import nltk
   from pydantic import BaseModel

   # Load models
   nlp = spacy.load('en_core_web_trf')
   gpt2 = transformers.GPT2LMHeadModel.from_pretrained('gpt2')

   print("✓ All dependencies functional")
   ```
4. Create health check script
5. Document actual setup times per platform
6. Create quick reference card (cheat sheet)

---

## Risks & Mitigations

### Risk 1: Dependency Version Conflicts

**Probability:** Medium
**Impact:** High (blocks all development)

**Mitigation:**
- Use exact version pinning in requirements.txt
- Provide tested dependency snapshot (known working versions)
- Document conflict resolution steps
- Provide pre-tested requirements.txt for Claude Code sandbox

### Risk 2: spaCy/transformers Download Failures

**Probability:** Medium
**Impact:** Medium (delays setup)

**Mitigation:**
- Provide direct download links for spaCy models
- Document offline installation procedure
- Cache models in user's local directory for reuse
- Add retry logic to setup script with exponential backoff

### Risk 3: Large Model Download Times

**Probability:** High
**Impact:** Low (user frustration)

**Description:** spaCy transformer model (500 MB) + transformers models (500 MB) = 1 GB total

**Mitigation:**
- Warn user about download size and time (5-15 minutes)
- Provide progress indicators in setup script
- Offer option to download models separately
- Document caching behavior (only download once)

### Risk 4: Platform-Specific Issues

**Probability:** Medium
**Impact:** Medium (some users blocked)

**Mitigation:**
- Test on all 3 major platforms (Windows, macOS, Linux)
- Document platform-specific gotchas
- Provide platform-specific setup scripts
- Claude Code sandbox provides consistent environment across platforms

---

## Definition of Done

- [ ] Virtual environment created and all dependencies installed
- [ ] spaCy en_core_web_trf model downloaded and functional
- [ ] transformers models (GPT-2, BERT) cached locally
- [ ] Project directory structure matches architecture spec
- [ ] Configuration files created and functional
- [ ] Development tooling (ruff, mypy, pytest) operational
- [ ] Claude Code sandbox integration verified (Bash tool execution works)
- [ ] JSON stdin/stdout communication tested and working
- [ ] Installation guide tested on Windows, macOS, Linux
- [ ] Troubleshooting guide covers 5+ common issues
- [ ] Setup script automates installation (30-60 minute process)
- [ ] Health check verifies all components functional
- [ ] README.md provides clear getting started instructions
- [ ] Total setup time: 30-60 minutes (automated), <2 hours (manual)

---

## Testing Strategy

### Manual Verification

1. **Clean Environment Test:**
   - Start with fresh Python 3.11 installation
   - Run setup script
   - Verify no errors, all models download
   - Run health check script

2. **Platform Testing:**
   - Test on Windows 10/11 VM
   - Test on macOS 11+ machine
   - Test on Ubuntu 20.04 VM
   - Document platform-specific issues

3. **Dependency Loading Test:**
   ```python
   # test_dependencies.py
   import spacy
   import transformers
   import bert_score
   import nltk
   from pydantic import BaseModel
   import structlog

   def test_spacy():
       nlp = spacy.load('en_core_web_trf')
       doc = nlp("AISI 304 steel")
       assert len(doc) > 0

   def test_transformers():
       model = transformers.GPT2LMHeadModel.from_pretrained('gpt2')
       assert model is not None

   def test_nltk():
       tokens = nltk.word_tokenize("Test sentence")
       assert len(tokens) == 2
   ```

### Automated Tests

```python
# tests/test_environment.py
import pytest
import sys

def test_python_version():
    assert sys.version_info >= (3, 11)
    assert sys.version_info < (3, 12)

def test_required_packages():
    import spacy
    import transformers
    import bert_score
    import nltk
    import pydantic

def test_project_structure():
    import os
    assert os.path.exists('src/tools')
    assert os.path.exists('src/models')
    assert os.path.exists('tests')
```

---

## Success Metrics

- **Setup Time:** 30-60 minutes automated, <2 hours manual
- **Success Rate:** 95%+ of users complete setup without issues
- **Platform Coverage:** Works on Windows, macOS, Linux
- **Sandbox Integration:** Python tools executable via Claude Code Bash tool
- **JSON Communication:** stdin/stdout working for all test cases
- **Documentation Quality:** Users complete setup using only README.md
- **Dependency Stability:** Zero dependency conflicts in testing

---

## Related Documents

- Architecture: `docs/architecture.md` (Section 10: Infrastructure and Deployment)
- Epic: `docs/epic-ai-humanizer.md`
- PRD: `docs/prd.md` (Epic 1: Development Environment & Infrastructure Setup)

---

## Changelog

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-30 | John (PM) | Initial story creation from PRD Epic 1 |
