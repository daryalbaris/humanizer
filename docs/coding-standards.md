# Coding Standards - AI Humanizer System

**Version:** 1.0
**Date:** 2025-10-30
**Purpose:** Define code quality standards for consistency and maintainability

---

## Overview

All code in the AI Humanizer System must follow these standards to ensure:
- **Consistency**: Code looks like it was written by one person
- **Maintainability**: Easy to understand and modify
- **Quality**: Fewer bugs, better performance
- **Collaboration**: Easier code reviews and team work

**Base Standard:** PEP 8 (Python Enhancement Proposal 8) with modifications

---

## 1. Python Style Guide

### 1.1 Line Length

**Rule:** Maximum 120 characters per line

**Rationale:** Balance between readability and screen real estate (PEP 8 default is 79, we extend for modern screens)

```python
# ✅ Good: Fits within 120 characters
result = some_function(param1, param2, param3, param4)

# ✅ Good: Split long lines with parentheses
result = some_function(
    very_long_parameter_name_1,
    very_long_parameter_name_2,
    very_long_parameter_name_3
)

# ❌ Bad: Exceeds 120 characters
result = some_function(very_long_parameter_name_1, very_long_parameter_name_2, very_long_parameter_name_3, very_long_parameter_name_4, very_long_parameter_name_5)
```

### 1.2 Indentation

**Rule:** 4 spaces per indentation level (NO TABS)

```python
# ✅ Good: 4 spaces
def my_function():
    if condition:
        do_something()

# ❌ Bad: 2 spaces or tabs
def my_function():
  if condition:
      do_something()
```

### 1.3 Blank Lines

**Rule:**
- 2 blank lines before top-level functions and classes
- 1 blank line before methods inside a class
- 1 blank line to separate logical sections within functions

```python
# ✅ Good: Proper spacing
import os


def function_one():
    pass


def function_two():
    pass


class MyClass:

    def method_one(self):
        pass

    def method_two(self):
        pass
```

### 1.4 Imports

**Rule:** Group imports in this order, separated by blank lines:
1. Standard library imports
2. Related third-party imports
3. Local application/library imports

```python
# ✅ Good: Organized imports
import os
import sys
from typing import Dict, List, Optional

import spacy
import torch
from transformers import GPT2LMHeadModel

from utils.json_io import read_json, write_json
from utils.config_loader import load_config
```

**Forbidden:**
```python
# ❌ Bad: Wildcard imports
from transformers import *

# ❌ Bad: Multiple imports on one line
import os, sys, json
```

---

## 2. Type Hints

### 2.1 Policy

**Rule:** Type hints **required** for all function signatures

**Rationale:** Catch bugs early, improve IDE support, document expected types

```python
# ✅ Good: Full type hints
def term_protector(
    text: str,
    glossary_path: str,
    protection_tier: str = "auto"
) -> Dict[str, Any]:
    """Protect technical terms in text."""
    pass

# ❌ Bad: No type hints
def term_protector(text, glossary_path, protection_tier="auto"):
    pass
```

### 2.2 Common Type Hints

```python
from typing import Dict, List, Optional, Union, Tuple, Any, Callable

# Basic types
name: str = "Alice"
age: int = 30
score: float = 95.5
is_valid: bool = True

# Collections
terms: List[str] = ["austenite", "martensite"]
config: Dict[str, Any] = {"max_iterations": 7}
result: Optional[str] = None  # Can be None

# Functions
def callback(x: int) -> str:
    return str(x)

handler: Callable[[int], str] = callback

# Multiple return values
def parse_response(text: str) -> Tuple[bool, str]:
    return True, "Success"

# Union types (multiple allowed types)
def process(value: Union[str, int, None]) -> str:
    return str(value)
```

### 2.3 Type Checking (Optional)

**Tool:** `mypy` (enforced in CI if enabled)

```bash
# Run type checking
mypy src/

# Expected output
Success: no issues found in 15 source files
```

---

## 3. Docstrings

### 3.1 Format

**Rule:** Google-style docstrings for all public functions and classes

**Structure:**
```python
def function_name(param1: str, param2: int) -> Dict[str, Any]:
    """One-line summary (max 79 chars).

    More detailed description if needed. Can be multiple paragraphs.
    Explain what the function does, not how it does it.

    Args:
        param1: Description of param1 (don't repeat type, it's in signature)
        param2: Description of param2

    Returns:
        Dictionary with 'status' and 'data' keys. Example:
        {
            'status': 'success',
            'data': {...}
        }

    Raises:
        ValidationError: If param1 is empty
        FileNotFoundError: If referenced file doesn't exist

    Examples:
        >>> result = function_name("text", 5)
        >>> print(result['status'])
        success
    """
    pass
```

### 3.2 Examples

**Function Docstring:**
```python
def calculate_perplexity(text: str, model: str = "gpt2") -> float:
    """Calculate GPT-2 perplexity score for text.

    Perplexity measures how "surprised" the language model is by the text.
    Lower perplexity indicates more predictable (AI-like) text.
    Higher perplexity indicates less predictable (human-like) text.

    Args:
        text: Input text to analyze (must be non-empty)
        model: GPT-2 model variant ("gpt2", "gpt2-medium", "gpt2-large")

    Returns:
        Perplexity score (typically 20-150)
        - AI-generated: 20-50 (low perplexity)
        - Human-written: 75-150 (high perplexity)

    Raises:
        ValidationError: If text is empty
        ProcessingError: If model fails to load

    Examples:
        >>> ppl = calculate_perplexity("The steel was tested.")
        >>> print(f"Perplexity: {ppl:.1f}")
        Perplexity: 87.3
    """
    pass
```

**Class Docstring:**
```python
class TermProtector:
    """Protect technical terms during paraphrasing.

    This class replaces technical terms with placeholders to prevent
    paraphrasing from corrupting domain-specific terminology.

    Attributes:
        glossary: Dictionary of protected terms (loaded from JSON)
        protection_tier: Current protection level ("tier1", "tier2", "tier3")

    Examples:
        >>> protector = TermProtector("data/glossary.json")
        >>> result = protector.protect("The AISI 304 steel was tested.")
        >>> print(result['protected_text'])
        The __TERM_001__ steel was tested.
    """

    def __init__(self, glossary_path: str):
        """Initialize TermProtector.

        Args:
            glossary_path: Path to glossary JSON file

        Raises:
            FileNotFoundError: If glossary file doesn't exist
        """
        pass
```

### 3.3 Module Docstring

**Rule:** Every Python file starts with a module docstring

```python
"""Term protection tool for AI Humanizer System.

This module provides functionality to protect technical terms during
paraphrasing by replacing them with placeholders.

Typical usage:
    protector = TermProtector("data/glossary.json")
    result = protector.protect(text)

Author: Your Name
Date: 2025-10-30
"""

import os
import json
# ... rest of code
```

---

## 4. Naming Conventions

### 4.1 General Rules

| Type | Convention | Example |
|------|------------|---------|
| Modules | lowercase_with_underscores | `term_protector.py` |
| Classes | CapitalizedWords | `TermProtector` |
| Functions | lowercase_with_underscores | `calculate_perplexity()` |
| Methods | lowercase_with_underscores | `process_text()` |
| Constants | UPPERCASE_WITH_UNDERSCORES | `MAX_ITERATIONS = 7` |
| Variables | lowercase_with_underscores | `detection_score` |
| Private | _leading_underscore | `_internal_helper()` |

### 4.2 Descriptive Names

```python
# ✅ Good: Descriptive names
def calculate_bertscore(original_text: str, humanized_text: str) -> float:
    pass

detection_threshold: float = 0.15
max_retry_attempts: int = 5

# ❌ Bad: Cryptic abbreviations
def calc_bs(ot: str, ht: str) -> float:
    pass

dt: float = 0.15
mra: int = 5
```

### 4.3 Boolean Names

**Rule:** Prefix with `is_`, `has_`, `should_`, `can_`

```python
# ✅ Good: Clear boolean intent
is_valid: bool = True
has_errors: bool = False
should_retry: bool = True
can_continue: bool = False

# ❌ Bad: Unclear
valid = True
errors = False
```

---

## 5. Error Handling

### 5.1 Custom Exceptions

**Rule:** Use custom exception classes, don't raise generic `Exception`

```python
# ✅ Good: Custom exceptions
class ValidationError(Exception):
    """Raised when input validation fails."""
    def __init__(self, message: str, field: str, expected_type: str):
        self.message = message
        self.field = field
        self.expected_type = expected_type
        super().__init__(message)

class ProcessingError(Exception):
    """Raised when processing fails."""
    pass

# Usage
if not text:
    raise ValidationError(
        message="Text cannot be empty",
        field="text",
        expected_type="non-empty string"
    )

# ❌ Bad: Generic exceptions
raise Exception("Something went wrong")
raise ValueError("Invalid")
```

### 5.2 Error Messages

**Rule:** Include context and actionable information

```python
# ✅ Good: Detailed error message
if not os.path.exists(glossary_path):
    raise FileNotFoundError(
        f"Glossary file not found: {glossary_path}\n"
        f"Expected location: data/glossary.json\n"
        f"To create: cp data/glossary.json.template data/glossary.json"
    )

# ❌ Bad: Vague error message
if not os.path.exists(glossary_path):
    raise FileNotFoundError("File not found")
```

### 5.3 Try-Except Blocks

**Rule:** Catch specific exceptions, not bare `except:`

```python
# ✅ Good: Specific exception catching
try:
    with open(file_path, 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    logger.error(f"File not found: {file_path}")
    raise
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON in {file_path}: {e}")
    raise

# ❌ Bad: Bare except (catches everything, even KeyboardInterrupt)
try:
    data = json.load(f)
except:
    pass  # Silently swallows all errors
```

---

## 6. Logging

### 6.1 Logger Setup

**Rule:** Use module-level logger

```python
import logging

# ✅ Good: Module-level logger
logger = logging.getLogger(__name__)

def process_text(text: str) -> str:
    logger.info("Processing text", extra={"text_length": len(text)})
    # ... processing
    logger.info("Processing complete")
    return result

# ❌ Bad: print statements
def process_text(text: str) -> str:
    print("Processing text")
    # ... processing
    print("Done")
    return result
```

### 6.2 Log Levels

| Level | When to Use | Example |
|-------|-------------|---------|
| DEBUG | Detailed diagnostic info | Variable values, loop iterations |
| INFO | General informational messages | Workflow milestones, progress |
| WARNING | Warning messages | Non-critical issues, fallbacks |
| ERROR | Error messages | Failures that allow continuation |
| CRITICAL | Critical failures | System cannot continue |

```python
# ✅ Good: Appropriate log levels
logger.debug(f"Term protector checking {len(terms)} terms")
logger.info("Term protection completed successfully")
logger.warning("spaCy model unavailable, using fallback")
logger.error("Failed to load glossary, retrying...")
logger.critical("Cannot continue without configuration file")
```

### 6.3 Structured Logging

**Rule:** Use `extra` parameter for structured data

```python
# ✅ Good: Structured logging (JSON-friendly)
logger.info(
    "Iteration completed",
    extra={
        "iteration": 3,
        "detection_score": 0.25,
        "perplexity": 82.5,
        "processing_time_ms": 15000
    }
)

# ❌ Bad: String formatting (hard to parse)
logger.info(f"Iteration 3 completed: score=0.25, ppl=82.5, time=15000ms")
```

---

## 7. Code Organization

### 7.1 Function Length

**Rule:** Functions should be <50 lines (excluding docstring)

**Rationale:** Long functions are hard to understand and test

```python
# ✅ Good: Short, focused function
def validate_input(data: dict) -> None:
    """Validate input data has required fields."""
    required_fields = ["text", "glossary_path"]
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"Missing field: {field}")

# ❌ Bad: Long function doing too much
def process_everything(data: dict) -> dict:
    # 200 lines of code doing validation, processing, formatting, logging...
    pass
```

### 7.2 Single Responsibility

**Rule:** Each function/class does one thing well

```python
# ✅ Good: Separate responsibilities
def load_glossary(path: str) -> dict:
    """Load glossary from JSON file."""
    pass

def protect_terms(text: str, glossary: dict) -> tuple:
    """Replace terms with placeholders."""
    pass

def restore_placeholders(text: str, placeholders: dict) -> str:
    """Restore original terms from placeholders."""
    pass

# ❌ Bad: One function does everything
def protect_and_restore_terms(text: str, glossary_path: str, mode: str) -> str:
    # Loads glossary, protects terms, processes, restores...
    pass
```

### 7.3 Constants

**Rule:** Define constants at module level, uppercase

```python
# ✅ Good: Module-level constants
MAX_ITERATIONS = 7
DETECTION_THRESHOLD = 0.15
DEFAULT_AGGRESSION = "moderate"

def process(text: str) -> str:
    for i in range(MAX_ITERATIONS):
        # ... processing
        if score < DETECTION_THRESHOLD:
            break

# ❌ Bad: Magic numbers in code
def process(text: str) -> str:
    for i in range(7):  # What does 7 mean?
        if score < 0.15:  # Why 0.15?
            break
```

---

## 8. Comments

### 8.1 When to Comment

**Rule:** Explain *why*, not *what* (code should be self-explanatory)

```python
# ✅ Good: Explains why
# Use exponential backoff to avoid overwhelming API
delay = base_delay * (2 ** attempt)

# ❌ Bad: States the obvious
# Calculate delay
delay = base_delay * (2 ** attempt)
```

### 8.2 TODO Comments

**Rule:** Use `TODO` for future work, include date/name

```python
# ✅ Good: Actionable TODO
# TODO(alice, 2025-11-01): Replace with GPU-accelerated version
perplexity = calculate_perplexity_cpu(text)

# ❌ Bad: Vague TODO
# TODO: make faster
perplexity = calculate_perplexity(text)
```

### 8.3 Comment Style

```python
# ✅ Good: Proper comment formatting

# This is a single-line comment

"""
This is a multi-line comment (actually a string literal).
Use for longer explanations or to temporarily disable code blocks.
"""

# ❌ Bad: Inconsistent formatting
#this has no space after #
##double ## is weird
```

---

## 9. Testing Requirements

### 9.1 Test Coverage

**Rule:** ≥80% code coverage for all modules

```bash
# Run tests with coverage
pytest tests/ --cov=src --cov-report=html

# Expected
Coverage: 85%  ✓ PASS
```

### 9.2 Test Naming

**Rule:** `test_<function>_<scenario>`

```python
# ✅ Good: Descriptive test names
def test_term_protector_with_valid_input():
    pass

def test_term_protector_raises_on_empty_text():
    pass

def test_term_protector_handles_missing_glossary():
    pass

# ❌ Bad: Vague test names
def test_1():
    pass

def test_protector():
    pass
```

### 9.3 Test Structure (AAA Pattern)

**Rule:** Arrange, Act, Assert

```python
def test_perplexity_calculator():
    # Arrange: Set up test data
    text = "The austenitic stainless steel was tested."
    model = "gpt2"

    # Act: Execute function
    result = calculate_perplexity(text, model)

    # Assert: Verify results
    assert 20 <= result <= 150  # Valid range
    assert isinstance(result, float)
```

---

## 10. Performance Considerations

### 10.1 Avoid Premature Optimization

**Rule:** Write clear code first, optimize only when profiling shows a bottleneck

```python
# ✅ Good: Clear, readable code (fast enough)
terms = [term for term in all_terms if term in glossary]

# ❌ Bad: Premature optimization (harder to read, minimal gain)
terms = list(filter(lambda t: t in glossary, all_terms))
```

### 10.2 Use Generators for Large Data

**Rule:** Use generators instead of lists when processing large datasets

```python
# ✅ Good: Generator (memory efficient)
def read_lines(file_path: str):
    with open(file_path, 'r') as f:
        for line in f:
            yield line.strip()

# ❌ Bad: Load entire file into memory
def read_lines(file_path: str) -> List[str]:
    with open(file_path, 'r') as f:
        return [line.strip() for line in f]  # Loads all at once
```

### 10.3 Cache Expensive Computations

**Rule:** Use `@lru_cache` for expensive pure functions

```python
from functools import lru_cache

# ✅ Good: Cache model loading
@lru_cache(maxsize=1)
def load_spacy_model(model_name: str):
    """Load spaCy model (cached after first call)."""
    return spacy.load(model_name)

# Now subsequent calls are instant
nlp = load_spacy_model("en_core_web_trf")  # Loads model
nlp = load_spacy_model("en_core_web_trf")  # Returns cached
```

---

## 11. Code Quality Tools

### 11.1 Linting (flake8)

**Configuration:** `.flake8`
```ini
[flake8]
max-line-length = 120
exclude = venv/,__pycache__/,.git/
ignore = E203,W503
```

**Usage:**
```bash
flake8 src/
```

### 11.2 Formatting (black)

**Configuration:** `pyproject.toml`
```toml
[tool.black]
line-length = 120
target-version = ['py39', 'py310', 'py311']
```

**Usage:**
```bash
# Format all files
black src/

# Check without modifying
black --check src/
```

### 11.3 Type Checking (mypy)

**Configuration:** `mypy.ini`
```ini
[mypy]
python_version = 3.10
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
```

**Usage:**
```bash
mypy src/
```

---

## 12. Pre-Commit Checklist

Before committing code:

- [ ] **Lint**: `flake8 src/` passes with no errors
- [ ] **Format**: `black src/` shows no changes needed
- [ ] **Type check**: `mypy src/` passes (if enabled)
- [ ] **Tests**: `pytest tests/` passes all tests
- [ ] **Coverage**: Coverage ≥80%
- [ ] **Docstrings**: All public functions documented
- [ ] **Type hints**: All function signatures typed
- [ ] **No TODOs**: Remove or document TODOs before commit
- [ ] **No debug code**: No `print()`, `breakpoint()`, commented code

---

## 13. Examples

### Good Module Example

```python
"""Term protection module for AI Humanizer System.

This module protects technical terms during paraphrasing by replacing
them with placeholders.

Typical usage:
    protector = TermProtector("data/glossary.json")
    result = protector.protect("The AISI 304 steel was tested.")
    print(result['protected_text'])  # "The __TERM_001__ steel was tested."
"""

import json
import logging
import re
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

# Constants
TERM_PREFIX = "__TERM_"
NUMBER_PREFIX = "__NUM_"
DEFAULT_PROTECTION_TIER = "auto"


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


class TermProtector:
    """Protect technical terms during paraphrasing.

    Attributes:
        glossary: Dictionary of protected terms
        protection_tier: Current protection level
    """

    def __init__(self, glossary_path: str):
        """Initialize TermProtector.

        Args:
            glossary_path: Path to glossary JSON file

        Raises:
            FileNotFoundError: If glossary file doesn't exist
        """
        self.glossary = self._load_glossary(glossary_path)
        self.protection_tier = DEFAULT_PROTECTION_TIER
        logger.info(f"TermProtector initialized with {len(self.glossary)} terms")

    def protect(self, text: str) -> Dict[str, any]:
        """Protect technical terms in text.

        Args:
            text: Input text containing technical terms

        Returns:
            Dictionary with 'protected_text' and 'placeholders' keys

        Raises:
            ValidationError: If text is empty
        """
        if not text:
            raise ValidationError("Text cannot be empty")

        logger.debug(f"Protecting terms in text (length: {len(text)})")

        protected_text, placeholders = self._replace_terms(text)

        logger.info(
            "Term protection complete",
            extra={
                "terms_protected": len(placeholders),
                "original_length": len(text),
                "protected_length": len(protected_text)
            }
        )

        return {
            "protected_text": protected_text,
            "placeholders": placeholders
        }

    def _load_glossary(self, path: str) -> Dict[str, List[str]]:
        """Load glossary from JSON file (private helper)."""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Glossary not found: {path}")
            raise

    def _replace_terms(self, text: str) -> Tuple[str, Dict[str, str]]:
        """Replace terms with placeholders (private helper)."""
        # Implementation details...
        pass
```

---

**Status:** ✅ Coding Standards Complete
**Standards Defined:** 13 sections
**Examples Provided:** Yes
**Tool Configurations:** Yes

**Last Updated:** 2025-10-30
**Next:** Code Review Guidelines (`docs/code-review-guidelines.md`)
