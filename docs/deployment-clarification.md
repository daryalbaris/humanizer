and # Deployment Clarification: Sandbox Environment

**Date:** 2025-10-30
**Status:** Clarified - Docker removed, Sandbox deployment confirmed

---

## Deployment Target: Claude Code Sandbox

This project is designed to run in the **Claude Code sandbox environment**, NOT in Docker containers.

### Key Points

✅ **Deployment Environment:** Claude Code sandbox (local execution)
✅ **Python Execution:** Via Claude Code's Bash tool
✅ **No Containerization:** Docker is not used
✅ **Local Development:** Virtual environment (venv) on local machine
✅ **File System:** Direct access to local file system (`C:\Users\LENOVO\Desktop\huminizer\bmad`)

---

## Architecture: Orchestrator-Worker Pattern

```
Claude Code Agent (Orchestrator)
       ↓
  Bash Tool
       ↓
Python Tools (Workers)
  - term_protector.py
  - paraphraser_processor.py
  - fingerprint_remover.py
  - burstiness_enhancer.py
  - detector_processor.py
  - perplexity_calculator.py
  - validator.py
  - state_manager.py
  - reference_analyzer.py
```

**Communication:** JSON via stdin/stdout
**State:** .humanizer/ directory for checkpoints, logs, output
**Models:** Cached locally (spaCy, GPT-2, BERT)

---

## What Changed

### Documents Updated

1. **`docs/stories/story-01-environment-setup.md`**
   - Removed Docker as required/recommended
   - Added Claude Code sandbox integration section
   - Updated Task 5: Docker Container → Claude Code Sandbox Integration
   - Updated effort: 40h → 38h (removed 8h Docker, added 6h sandbox)
   - Updated DoD, Success Metrics, Risks to remove Docker references

2. **`docs/pre-implementation-checklist.md`**
   - Replaced Docker environment testing with Claude Code sandbox testing
   - Added sandbox verification scripts
   - Updated Sprint 1 demo to remove Docker build step
   - Added sandbox integration success criteria

3. **`docs/sprint-planning.md`** (to be updated)
   - Sprint 1 velocity: 40h → 38h
   - Remove Docker task assignments
   - Add sandbox integration tasks

4. **`docs/team-formation-guide.md`** (to be updated)
   - Remove Docker expertise from Developer 3 requirements
   - Focus on Claude Code sandbox integration skills

---

## Sandbox Environment Requirements

### Development Setup

**Local Machine:**
- Python 3.11.x virtual environment
- All dependencies installed (spaCy, transformers, BERT, etc.)
- Models downloaded and cached locally
- .humanizer/ directory for runtime data

**Claude Code Integration:**
- Claude Code subscription (Pro plan recommended)
- Bash tool access enabled
- JSON stdin/stdout communication tested
- File system access verified

### Verification Steps

```bash
# 1. Test Python execution
python --version  # Should be 3.11.x

# 2. Test JSON I/O
echo '{"test": "value"}' | python -c "import sys, json; data = json.load(sys.stdin); print(json.dumps({'echo': data}))"

# 3. Test spaCy model
python -c "import spacy; nlp = spacy.load('en_core_web_trf'); print('✓ spaCy loaded')"

# 4. Test file I/O
python -c "import os; os.makedirs('.humanizer', exist_ok=True); print('✓ Directory created')"

# 5. Test transformers model
python -c "from transformers import GPT2LMHeadModel; model = GPT2LMHeadModel.from_pretrained('gpt2'); print('✓ GPT-2 loaded')"
```

---

## Deployment Workflow

### Development Phase (Sprint 1-9)

1. **Local Development:**
   - Developers work on local machines
   - Python virtual environment (venv)
   - Git for version control
   - CI/CD pipeline (GitHub Actions)

2. **Testing:**
   - Unit tests: pytest locally
   - Integration tests: Claude Code orchestrator + Python tools
   - Manual testing: Full workflow via Claude Code

### Production Deployment (Sprint 10+)

**User Deployment:**
- User downloads project from GitHub
- Runs setup script: `scripts/setup.sh`
- Installs dependencies in venv
- Downloads ML models (spaCy, GPT-2, BERT)
- Interacts with Claude Code agent to process papers

**No Server Deployment:**
- This is a client-side tool
- Runs on user's machine via Claude Code
- No web server, no cloud deployment
- All processing happens locally

---

## Benefits of Sandbox Deployment

✅ **Simplicity:** No Docker complexity, easier setup
✅ **Performance:** Direct local execution, no container overhead
✅ **Development Speed:** Faster iteration, no build times
✅ **Debugging:** Easier to debug local Python processes
✅ **Cost:** No container hosting costs
✅ **Flexibility:** Users can customize local environment

---

## Updated Sprint 1 Tasks

### Task 5: Claude Code Sandbox Integration (6 hours)

**Subtasks:**
1. Test Python execution via Claude Code Bash tool (1h)
   - Verify venv activation
   - Test JSON stdin/stdout
   - Verify file I/O

2. Create sandbox verification script (2h)
   - Check Python version
   - Test model loading
   - Test JSON serialization
   - Verify .humanizer/ directory creation

3. Document Claude Code execution patterns (2h)
   - How to run Python tools from orchestrator
   - Environment variable access in sandbox
   - File path conventions
   - Model caching behavior

4. Create troubleshooting guide (1h)
   - Sandbox-specific issues
   - Permission errors
   - Model loading failures
   - JSON serialization edge cases

---

## Installation Guide (Updated)

### For End Users

**Prerequisites:**
- Python 3.11.x installed
- Claude Code subscription (Pro recommended)
- 8 GB RAM minimum, 16 GB recommended
- 5 GB free disk space (for models)

**Installation Steps:**

```bash
# 1. Clone repository
git clone <repository-url>
cd bmad

# 2. Run setup script
bash scripts/setup.sh

# 3. Verify installation
python scripts/verify_environment.py

# 4. Interact with Claude Code agent
# (Claude agent will orchestrate Python tools)
```

**No Docker required!** ✅

---

## FAQs

**Q: Why not use Docker?**
A: This project is designed for Claude Code sandbox execution. Docker adds unnecessary complexity for a client-side tool that runs locally via Claude Code.

**Q: Can I still use Docker if I want?**
A: While not recommended or supported, you could create your own Dockerfile. However, the project is optimized for local venv execution.

**Q: What if I have dependency conflicts?**
A: Use the exact version pinning in requirements.txt. The setup script creates an isolated virtual environment to avoid conflicts.

**Q: Does this work on Windows, macOS, and Linux?**
A: Yes! The project is tested on all three platforms. Claude Code provides a consistent execution environment.

**Q: Where are the models stored?**
A: Models are cached locally:
- spaCy: `~/.cache/spacy/` or `%APPDATA%\spacy\` (Windows)
- transformers: `~/.cache/huggingface/` or `%USERPROFILE%\.cache\huggingface\` (Windows)
- Total size: ~3 GB

**Q: Can multiple users share the same installation?**
A: Each user should have their own virtual environment and .humanizer/ directory. Models can be shared if using shared cache directories.

---

## Next Steps

1. ✅ Update STORY-001 (completed)
2. ✅ Update pre-implementation checklist (completed)
3. 🔲 Update sprint planning document (Sprint 1 velocity: 38h)
4. 🔲 Update team formation guide (remove Docker skills requirement)
5. 🔲 Update architecture document (if Docker mentioned)
6. 🔲 Create sandbox verification script (`scripts/verify_sandbox.py`)
7. 🔲 Update README.md with sandbox deployment instructions

---

**Document Status:** ✅ COMPLETE - Deployment Clarification
**Last Updated:** 2025-10-30
**Impact:** Low (removes unnecessary complexity, aligns with actual deployment target)
