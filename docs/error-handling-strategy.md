# Error Handling Strategy - AI Humanizer System

**Version:** 1.0
**Date:** 2025-10-30
**Purpose:** Define comprehensive error handling approach for robustness and reliability

---

## Overview

This document defines the error handling strategy for the AI Humanizer System, ensuring:
- **Robustness**: System handles errors gracefully without crashing
- **Recoverability**: Checkpoints allow resume from failure points
- **Transparency**: Clear error messages guide users to solutions
- **Debuggability**: Structured logs enable quick troubleshooting

---

## Error Categories

### 1. ValidationError

**When:** Input validation fails (missing field, wrong type, out of range)

**Severity:** Medium (can be fixed by user)

**Response:** Return error immediately, don't process

**Example Scenarios:**
- Missing required field in JSON input
- Wrong data type (string instead of number)
- Value out of acceptable range (perplexity < 0)
- Empty text input
- Invalid file path format

**Error Response:**
```json
{
  "status": "error",
  "error": {
    "type": "ValidationError",
    "message": "Field 'text' is required but missing",
    "details": {
      "field": "text",
      "expected_type": "string",
      "received": null,
      "fix": "Provide non-empty 'text' field in input JSON"
    }
  },
  "metadata": {
    "tool": "term_protector",
    "timestamp": "2025-10-30T10:00:00Z"
  }
}
```

**Handling Strategy:**
- ✅ Validate all inputs before processing
- ✅ Provide specific field names and expected values
- ✅ Suggest fixes ("Provide 'text' field", "Use 0-1 range for confidence")
- ❌ Don't retry automatically (user must fix input)

---

### 2. ProcessingError

**When:** Runtime processing fails (model error, calculation failure, unexpected exception)

**Severity:** High (may require retry or fallback)

**Response:** Retry with exponential backoff, then fail gracefully

**Example Scenarios:**
- spaCy model fails to load
- GPT-2 out of memory
- BERTScore calculation timeout
- Paraphrasing produces invalid output
- Sentence parsing error

**Error Response:**
```json
{
  "status": "error",
  "error": {
    "type": "ProcessingError",
    "message": "Failed to load spaCy model: en_core_web_trf not found",
    "details": {
      "model_name": "en_core_web_trf",
      "error_code": "MODEL_NOT_FOUND",
      "suggested_fix": "Run: python -m spacy download en_core_web_trf",
      "fallback_available": true,
      "fallback_model": "en_core_web_sm"
    },
    "traceback": "Traceback (most recent call last):\n  File..."
  },
  "metadata": {
    "tool": "term_protector",
    "timestamp": "2025-10-30T10:00:00Z"
  }
}
```

**Handling Strategy:**
- ✅ Retry with exponential backoff (1s, 2s, 4s, 8s, 16s max)
- ✅ Use fallback if available (lighter model, simpler algorithm)
- ✅ Save checkpoint before failing (allow resume)
- ✅ Include full traceback in debug mode
- ❌ Don't retry indefinitely (max 5 attempts)

---

### 3. ConfigError

**When:** Configuration file missing or invalid

**Severity:** Critical (system cannot start)

**Response:** Fail immediately with clear fix instructions

**Example Scenarios:**
- `config/config.yaml` not found
- YAML syntax error
- Missing required configuration field
- Invalid value in configuration (negative max_iterations)

**Error Response:**
```json
{
  "status": "error",
  "error": {
    "type": "ConfigError",
    "message": "Configuration file not found: config/config.yaml",
    "details": {
      "expected_path": "config/config.yaml",
      "searched_paths": [
        "config/config.yaml",
        "./config/config.yaml",
        "/absolute/path/config/config.yaml"
      ],
      "suggested_fix": "Create config.yaml from template: cp config/config.yaml.template config/config.yaml"
    }
  },
  "metadata": {
    "tool": "config_loader",
    "timestamp": "2025-10-30T10:00:00Z"
  }
}
```

**Handling Strategy:**
- ✅ Check configuration on startup
- ✅ Provide exact paths searched
- ✅ Suggest using template file
- ✅ Validate all required fields present
- ❌ Don't use defaults if critical fields missing

---

### 4. FileNotFoundError

**When:** Required data file missing (glossary, patterns, checkpoint)

**Severity:** High (may block processing)

**Response:** Fail with clear file location, suggest creation

**Example Scenarios:**
- Glossary file not found
- Pattern database missing
- Checkpoint file doesn't exist (for resume)
- Reference text missing

**Error Response:**
```json
{
  "status": "error",
  "error": {
    "type": "FileNotFoundError",
    "message": "Glossary file not found: data/glossary.json",
    "details": {
      "file_path": "data/glossary.json",
      "file_type": "glossary",
      "required": true,
      "suggested_fix": "Create glossary.json with at least tier1 terms. See docs/data-formats.md for structure."
    }
  },
  "metadata": {
    "tool": "term_protector",
    "timestamp": "2025-10-30T10:00:00Z"
  }
}
```

**Handling Strategy:**
- ✅ Check file exists before reading
- ✅ Provide absolute and relative paths
- ✅ Suggest file creation steps
- ✅ Link to documentation for file format
- ❌ Don't create files automatically (user responsibility)

---

### 5. APIError

**When:** External API call fails (Originality.ai, translation service)

**Severity:** Medium-High (may have retry or fallback)

**Response:** Retry with backoff, use fallback if available

**Example Scenarios:**
- Originality.ai rate limit exceeded
- Network timeout
- API key invalid
- Service temporarily unavailable

**Error Response:**
```json
{
  "status": "error",
  "error": {
    "type": "APIError",
    "message": "Originality.ai API request failed: Rate limit exceeded",
    "details": {
      "api": "originality.ai",
      "endpoint": "/api/v1/detect",
      "status_code": 429,
      "retry_after_seconds": 60,
      "retries_attempted": 3,
      "fallback_available": false
    }
  },
  "metadata": {
    "tool": "detector_processor",
    "timestamp": "2025-10-30T10:00:00Z"
  }
}
```

**Handling Strategy:**
- ✅ Retry with exponential backoff (respect Retry-After header)
- ✅ Log all API errors for monitoring
- ✅ Use fallback detection method if available
- ✅ Cache successful responses to reduce API calls
- ⚠️ Warn user about rate limits before exhausting quota

---

## Retry Logic

### Exponential Backoff Strategy

**Formula:** `delay = min(base_delay * 2^attempt, max_delay)`

**Parameters:**
- `base_delay`: 1 second
- `max_delay`: 16 seconds
- `max_attempts`: 5

**Implementation:**

```python
import time
from typing import Callable, Any, Optional

def retry_with_backoff(
    func: Callable,
    max_attempts: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 16.0,
    exceptions: tuple = (Exception,)
) -> Any:
    """
    Retry function with exponential backoff.

    Args:
        func: Function to retry
        max_attempts: Maximum retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay between retries
        exceptions: Tuple of exceptions to catch

    Returns:
        Function result if successful

    Raises:
        Last exception if all retries fail
    """
    last_exception = None

    for attempt in range(max_attempts):
        try:
            return func()
        except exceptions as e:
            last_exception = e

            if attempt < max_attempts - 1:
                delay = min(base_delay * (2 ** attempt), max_delay)
                logger.warning(
                    f"Attempt {attempt + 1}/{max_attempts} failed, "
                    f"retrying in {delay}s: {str(e)}"
                )
                time.sleep(delay)
            else:
                logger.error(
                    f"All {max_attempts} attempts failed: {str(e)}"
                )

    raise last_exception
```

**Usage Example:**

```python
# Retry spaCy model loading
def load_spacy_model():
    return spacy.load("en_core_web_trf")

try:
    nlp = retry_with_backoff(
        load_spacy_model,
        max_attempts=3,
        exceptions=(OSError, IOError)
    )
except Exception as e:
    # All retries failed, use fallback
    logger.error(f"Failed to load spaCy model: {e}")
    nlp = spacy.load("en_core_web_sm")  # Fallback
```

---

## Fallback Behavior

### Graceful Degradation vs Hard Failure

**Decision Tree:**

```
Error Occurs
    │
    ├─ Can we continue with reduced functionality?
    │   YES → Graceful Degradation
    │   │      ├─ Use lighter model
    │   │      ├─ Skip optional component
    │   │      ├─ Use cached result
    │   │      └─ Continue with warning
    │   │
    │   NO  → Hard Failure
    │          ├─ Save checkpoint
    │          ├─ Log error details
    │          └─ Exit with error code
```

### Graceful Degradation Scenarios

**Scenario 1: Model Loading Failure**
```python
# Try primary model, fallback to lighter model
try:
    nlp = spacy.load("en_core_web_trf")  # 500 MB, accurate
except:
    logger.warning("Primary spaCy model unavailable, using fallback")
    nlp = spacy.load("en_core_web_sm")   # 13 MB, less accurate
```

**Scenario 2: GPU Unavailable**
```python
# Try GPU, fallback to CPU
device = "cuda" if torch.cuda.is_available() else "cpu"
if device == "cpu":
    logger.warning("GPU unavailable, using CPU (slower)")
model.to(device)
```

**Scenario 3: BERTScore Too Slow**
```python
# If BERTScore takes >60s, skip and warn
try:
    bertscore = calculate_bertscore(text1, text2, timeout=60)
except TimeoutError:
    logger.warning("BERTScore timed out, skipping validation")
    bertscore = None  # Continue without BERTScore
```

### Hard Failure Scenarios

**Scenario 1: Critical Data Missing**
```python
# Cannot proceed without glossary
if not os.path.exists(glossary_path):
    raise FileNotFoundError(
        f"Critical file missing: {glossary_path}. "
        "Cannot protect technical terms without glossary."
    )
```

**Scenario 2: Invalid Configuration**
```python
# Cannot run with invalid max_iterations
if config["max_iterations"] < 1:
    raise ConfigError(
        f"Invalid max_iterations: {config['max_iterations']}. "
        "Must be >= 1."
    )
```

**Scenario 3: Semantic Similarity Too Low**
```python
# Stop if paraphrasing corrupted meaning
if bertscore < 0.70:  # Critical threshold
    raise ProcessingError(
        f"Paraphrasing corrupted meaning (BERTScore: {bertscore:.2f}). "
        "Cannot continue - semantic drift too high."
    )
```

---

## Error Logging Format

### Structured JSON Logs

**Format:**
```json
{
  "timestamp": "2025-10-30T10:00:00.123Z",
  "level": "ERROR",
  "tool": "term_protector",
  "error_type": "ProcessingError",
  "message": "Failed to load spaCy model",
  "details": {
    "model_name": "en_core_web_trf",
    "error_code": "MODEL_NOT_FOUND",
    "attempt": 3,
    "max_attempts": 5
  },
  "traceback": "Traceback (most recent call last)...",
  "context": {
    "paper_id": "paper_abc123",
    "iteration": 2,
    "checkpoint_id": "paper_abc123_iter2"
  }
}
```

**Implementation:**

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Format log records as JSON."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "tool": record.name,
            "message": record.getMessage()
        }

        # Add exception info if present
        if record.exc_info:
            log_data["traceback"] = self.formatException(record.exc_info)

        # Add custom fields
        if hasattr(record, "error_type"):
            log_data["error_type"] = record.error_type
        if hasattr(record, "details"):
            log_data["details"] = record.details
        if hasattr(record, "context"):
            log_data["context"] = record.context

        return json.dumps(log_data)

# Configure logger
logger = logging.getLogger("term_protector")
handler = logging.FileHandler(".humanizer/logs/errors.log")
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
```

**Usage:**

```python
try:
    nlp = spacy.load("en_core_web_trf")
except Exception as e:
    logger.error(
        "Failed to load spaCy model",
        extra={
            "error_type": "ProcessingError",
            "details": {
                "model_name": "en_core_web_trf",
                "error_code": "MODEL_NOT_FOUND"
            },
            "context": {
                "paper_id": paper_id,
                "iteration": iteration
            }
        },
        exc_info=True
    )
```

---

## User-Facing Error Messages

### Principles

1. **Actionable**: Tell user what to do, not just what went wrong
2. **Clear**: Avoid technical jargon, use plain language
3. **Specific**: Include exact file paths, field names, values
4. **Helpful**: Suggest fixes, provide documentation links

### Good vs Bad Error Messages

**❌ Bad:**
```
Error: Failed to process
```

**✅ Good:**
```
Error: Glossary file not found at 'data/glossary.json'

To fix this issue:
1. Create glossary.json from template:
   cp data/glossary.json.template data/glossary.json

2. Or download from:
   https://github.com/your-repo/blob/main/data/glossary.json

For glossary format, see: docs/data-formats.md#glossary-format
```

---

**❌ Bad:**
```
ValidationError: Invalid input
```

**✅ Good:**
```
Validation Error: Field 'text' cannot be empty

Your input:
{
  "text": "",
  "glossary_path": "data/glossary.json"
}

Required: 'text' must be a non-empty string containing the paper to humanize.

Example:
{
  "text": "The austenitic stainless steel was tested...",
  "glossary_path": "data/glossary.json"
}
```

---

**❌ Bad:**
```
ProcessingError: Model error
```

**✅ Good:**
```
Processing Error: spaCy model 'en_core_web_trf' not found

This model is required for term protection. To download:

1. Activate virtual environment:
   source venv/bin/activate  (Linux/Mac)
   venv\Scripts\activate     (Windows)

2. Download model:
   python -m spacy download en_core_web_trf

3. Verify installation:
   python -c "import spacy; spacy.load('en_core_web_trf')"

Model size: 500 MB, download time: ~2-5 minutes

Alternative (faster): Use lighter model en_core_web_sm (13 MB)
Edit config.yaml: spacy_model: "en_core_web_sm"
```

---

## Error Recovery Strategies

### 1. Checkpoint-Based Recovery

**Strategy:** Save state before risky operations, resume on failure

```python
def process_iteration(iteration: int, text: str, config: dict):
    """Process one iteration with checkpoint recovery."""

    checkpoint_id = f"paper_{paper_id}_iter{iteration}"

    try:
        # Save checkpoint before processing
        state_manager.save({
            "iteration": iteration,
            "text": text,
            "config": config,
            "timestamp": datetime.utcnow().isoformat()
        }, checkpoint_id)

        # Risky processing
        result = perform_risky_processing(text, config)

        return result

    except Exception as e:
        logger.error(f"Iteration {iteration} failed: {e}")

        # Checkpoint allows resume from this point
        print(f"✓ State saved as checkpoint: {checkpoint_id}")
        print(f"To resume: load_checkpoint('{checkpoint_id}')")

        raise  # Re-raise for upstream handling
```

### 2. Partial Success Handling

**Strategy:** Save partial results, continue with what worked

```python
def process_batch(texts: list) -> tuple:
    """Process batch, return successes and failures separately."""

    successes = []
    failures = []

    for i, text in enumerate(texts):
        try:
            result = process_text(text)
            successes.append((i, result))
        except Exception as e:
            logger.warning(f"Text {i} failed: {e}")
            failures.append((i, str(e)))

    # Return both successes and failures
    return {
        "successes": successes,
        "failures": failures,
        "success_rate": len(successes) / len(texts)
    }
```

### 3. Progressive Fallback Chain

**Strategy:** Try multiple approaches, fallback gracefully

```python
def calculate_perplexity(text: str) -> float:
    """Calculate perplexity with fallback chain."""

    # Try 1: GPT-2 Medium (most accurate)
    try:
        return calculate_with_model(text, "gpt2-medium")
    except MemoryError:
        logger.warning("GPT-2 Medium OOM, trying GPT-2")

    # Try 2: GPT-2 (less memory)
    try:
        return calculate_with_model(text, "gpt2")
    except Exception:
        logger.warning("GPT-2 failed, using approximation")

    # Try 3: Approximation (always works)
    return approximate_perplexity(text)
```

---

## Testing Error Handling

### Unit Test Examples

```python
import pytest
from tools.term_protector import TermProtector

def test_validation_error_missing_field():
    """Test ValidationError on missing required field."""

    protector = TermProtector()

    # Missing 'text' field
    invalid_input = {
        "glossary_path": "data/glossary.json"
    }

    with pytest.raises(ValidationError) as exc_info:
        protector.process(invalid_input)

    assert "Field 'text' is required" in str(exc_info.value)
    assert exc_info.value.details["field"] == "text"

def test_file_not_found_error():
    """Test FileNotFoundError for missing glossary."""

    protector = TermProtector()

    invalid_input = {
        "text": "Sample text",
        "glossary_path": "nonexistent/glossary.json"
    }

    with pytest.raises(FileNotFoundError) as exc_info:
        protector.process(invalid_input)

    assert "glossary.json" in str(exc_info.value)

def test_retry_logic():
    """Test exponential backoff retry logic."""

    attempts = []

    def flaky_function():
        attempts.append(time.time())
        if len(attempts) < 3:
            raise ProcessingError("Temporary failure")
        return "success"

    result = retry_with_backoff(flaky_function, max_attempts=5)

    assert result == "success"
    assert len(attempts) == 3

    # Check exponential backoff: ~1s, ~2s between attempts
    delay1 = attempts[1] - attempts[0]
    delay2 = attempts[2] - attempts[1]
    assert 0.9 < delay1 < 1.1  # ~1 second
    assert 1.8 < delay2 < 2.2  # ~2 seconds
```

---

## Best Practices

### 1. Fail Fast, Fail Clearly

```python
# ✅ Good: Validate early, fail immediately
def process(text: str, glossary_path: str):
    if not text:
        raise ValidationError("Text cannot be empty")
    if not os.path.exists(glossary_path):
        raise FileNotFoundError(f"Glossary not found: {glossary_path}")

    # Now process with confidence
    return do_processing(text, glossary_path)

# ❌ Bad: Start processing, fail halfway through
def process(text: str, glossary_path: str):
    result = expensive_operation(text)  # Wastes time
    glossary = load_glossary(glossary_path)  # Fails here
    return combine(result, glossary)
```

### 2. Include Context in Errors

```python
# ✅ Good: Include context for debugging
try:
    result = process_text(text)
except Exception as e:
    raise ProcessingError(
        f"Failed to process text (length: {len(text)}, "
        f"iteration: {iteration}, paper_id: {paper_id})"
    ) from e

# ❌ Bad: Generic error without context
try:
    result = process_text(text)
except Exception as e:
    raise ProcessingError("Processing failed") from e
```

### 3. Log Before and After Risky Operations

```python
# ✅ Good: Log entry and exit
logger.info(f"Loading spaCy model: {model_name}")
try:
    nlp = spacy.load(model_name)
    logger.info(f"✓ Model loaded successfully: {model_name}")
except Exception as e:
    logger.error(f"✗ Failed to load model: {model_name}: {e}")
    raise

# ❌ Bad: Only log on failure
try:
    nlp = spacy.load(model_name)
except Exception as e:
    logger.error(f"Failed: {e}")
```

### 4. Use Custom Exception Classes

```python
# ✅ Good: Custom exceptions with structured data
class ValidationError(Exception):
    def __init__(self, message: str, field: str, expected_type: str):
        self.message = message
        self.field = field
        self.expected_type = expected_type
        super().__init__(message)

# ❌ Bad: Generic exceptions
raise Exception("Validation failed")
```

### 5. Always Clean Up Resources

```python
# ✅ Good: Use context managers
with open(file_path, 'r') as f:
    data = json.load(f)
# File automatically closed, even if exception occurs

# ❌ Bad: Manual cleanup (may not execute)
f = open(file_path, 'r')
data = json.load(f)  # If this fails, file not closed
f.close()
```

---

## Error Monitoring

### Metrics to Track

1. **Error Rate**: Errors per 100 papers processed
2. **Error Types**: Distribution (ValidationError, ProcessingError, etc.)
3. **Retry Success Rate**: % of retries that succeed
4. **Mean Time to Recovery**: Average time to fix errors
5. **Critical Errors**: Errors requiring immediate attention

### Alert Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| Error rate | >5% | >10% |
| ProcessingError rate | >2% | >5% |
| API failures | >3/hour | >10/hour |
| Checkpoint failures | >1% | >3% |

---

**Status:** ✅ Error Handling Strategy Complete
**Error Types Defined:** 5 categories
**Retry Logic:** Exponential backoff implemented
**Recovery Strategies:** 3 approaches documented
**Testing Examples:** Provided

**Last Updated:** 2025-10-30
**Next:** Coding Standards (`docs/coding-standards.md`)
