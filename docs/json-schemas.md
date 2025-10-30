# JSON Interface Schemas - AI Humanizer System

**Version:** 1.0
**Date:** 2025-10-30
**Purpose:** Define exact JSON interfaces for all 8 Python tools

---

## Overview

All Python tools communicate with the Claude Code orchestrator via JSON over stdin/stdout. This document defines the exact schemas for input and output, including error responses.

### Communication Protocol

```
Claude Code Orchestrator → Bash Tool → Python Script
                                          ↓
                            JSON via stdin (input)
                                          ↓
                            [Python Processing]
                                          ↓
                            JSON via stdout (output)
                                          ↓
Claude Code Orchestrator ← Bash Tool ← Python Script
```

### Common Patterns

**Success Response:**
```json
{
  "status": "success",
  "data": { ... },
  "metadata": {
    "processing_time_ms": 1234,
    "tool": "tool_name",
    "version": "1.0"
  }
}
```

**Error Response:**
```json
{
  "status": "error",
  "error": {
    "type": "ErrorClassName",
    "message": "Human-readable error message",
    "details": { ... },
    "traceback": "Full stack trace (if debug mode)"
  },
  "metadata": {
    "tool": "tool_name",
    "timestamp": "2025-10-30T09:00:00Z"
  }
}
```

---

## Tool 1: term_protector.py

**Purpose:** Protect technical terms by replacing with placeholders

### Input Schema

```json
{
  "text": "The AISI 304 stainless steel was heat treated at 850°C.",
  "glossary_path": "data/glossary.json",
  "protection_tier": "auto",
  "options": {
    "protect_numbers": true,
    "protect_citations": true,
    "placeholder_prefix": "__TERM_",
    "number_prefix": "__NUM_"
  }
}
```

**Field Descriptions:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `text` | string | Yes | - | Input text to protect |
| `glossary_path` | string | Yes | - | Path to glossary JSON file |
| `protection_tier` | string | No | `"auto"` | `"auto"`, `"tier1"`, `"tier2"`, `"tier3"`, or `"all"` |
| `options.protect_numbers` | boolean | No | `true` | Protect numerical values (850°C → `__NUM_001__`) |
| `options.protect_citations` | boolean | No | `true` | Protect citations ([Smith, 2024] → `__CIT_001__`) |
| `options.placeholder_prefix` | string | No | `"__TERM_"` | Prefix for term placeholders |
| `options.number_prefix` | string | No | `"__NUM_"` | Prefix for number placeholders |

### Output Schema (Success)

```json
{
  "status": "success",
  "data": {
    "protected_text": "The __TERM_001__ stainless steel was heat treated at __NUM_001__.",
    "placeholders": {
      "__TERM_001__": "AISI 304",
      "__NUM_001__": "850°C"
    },
    "protection_map": {
      "tier1_terms": ["AISI 304"],
      "tier2_terms": [],
      "tier3_terms": [],
      "numbers": ["850°C"],
      "citations": []
    }
  },
  "metadata": {
    "processing_time_ms": 1234,
    "tool": "term_protector",
    "version": "1.0",
    "stats": {
      "terms_protected": 1,
      "numbers_protected": 1,
      "citations_protected": 0,
      "total_placeholders": 2
    }
  }
}
```

### Output Schema (Error)

```json
{
  "status": "error",
  "error": {
    "type": "ValidationError",
    "message": "Glossary file not found: data/glossary.json",
    "details": {
      "expected_path": "data/glossary.json",
      "searched_paths": ["data/glossary.json", "./data/glossary.json"]
    }
  },
  "metadata": {
    "tool": "term_protector",
    "timestamp": "2025-10-30T09:00:00Z"
  }
}
```

---

## Tool 2: paraphraser_processor.py

**Purpose:** Post-process Claude's paraphrased text

### Input Schema

```json
{
  "original_text": "The austenitic stainless steel exhibited excellent corrosion resistance.",
  "paraphrased_text": "The austenite-phase stainless steel showed great resistance against corrosion.",
  "protected_placeholders": {
    "__TERM_001__": "AISI 304"
  },
  "aggression_level": "moderate",
  "options": {
    "restore_placeholders": true,
    "verify_meaning": true,
    "fix_grammar": true
  }
}
```

**Field Descriptions:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `original_text` | string | Yes | - | Original text (for verification) |
| `paraphrased_text` | string | Yes | - | Claude's paraphrased output |
| `protected_placeholders` | object | No | `{}` | Map of placeholders to restore |
| `aggression_level` | string | No | `"moderate"` | `"gentle"`, `"moderate"`, `"aggressive"`, `"intensive"`, `"nuclear"` |
| `options.restore_placeholders` | boolean | No | `true` | Restore protected terms |
| `options.verify_meaning` | boolean | No | `true` | Check semantic similarity |
| `options.fix_grammar` | boolean | No | `true` | Fix minor grammar issues |

### Output Schema (Success)

```json
{
  "status": "success",
  "data": {
    "processed_text": "The __TERM_001__ stainless steel showed excellent resistance to corrosion.",
    "restored_placeholders": ["__TERM_001__"],
    "quality_checks": {
      "semantic_similarity": 0.94,
      "grammar_score": 0.98,
      "technical_terms_preserved": true
    },
    "changes_made": [
      "Restored placeholder __TERM_001__",
      "Fixed grammar: 'against corrosion' → 'to corrosion'"
    ]
  },
  "metadata": {
    "processing_time_ms": 4567,
    "tool": "paraphraser_processor",
    "version": "1.0",
    "aggression_level_used": "moderate"
  }
}
```

---

## Tool 3: fingerprint_remover.py

**Purpose:** Remove AI-specific patterns and fingerprints

### Input Schema

```json
{
  "text": "It is important to note that the austenitic steel exhibited excellent properties.",
  "patterns_path": "data/patterns.json",
  "confidence_threshold": 0.75,
  "options": {
    "remove_hedging": true,
    "remove_meta_discourse": true,
    "aggressive_removal": false
  }
}
```

**Field Descriptions:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `text` | string | Yes | - | Text to clean |
| `patterns_path` | string | Yes | - | Path to patterns database |
| `confidence_threshold` | number | No | `0.75` | Minimum confidence for pattern detection (0-1) |
| `options.remove_hedging` | boolean | No | `true` | Remove hedging phrases ("it is important to note") |
| `options.remove_meta_discourse` | boolean | No | `true` | Remove meta-discourse ("in this study, we") |
| `options.aggressive_removal` | boolean | No | `false` | More aggressive pattern removal |

### Output Schema (Success)

```json
{
  "status": "success",
  "data": {
    "cleaned_text": "The austenitic steel exhibited excellent properties.",
    "removed_patterns": [
      {
        "pattern": "It is important to note that",
        "category": "hedging",
        "position": 0,
        "confidence": 0.95
      }
    ],
    "statistics": {
      "patterns_detected": 1,
      "patterns_removed": 1,
      "characters_removed": 28
    }
  },
  "metadata": {
    "processing_time_ms": 2345,
    "tool": "fingerprint_remover",
    "version": "1.0"
  }
}
```

---

## Tool 4: burstiness_enhancer.py

**Purpose:** Enhance sentence length variation (burstiness)

### Input Schema

```json
{
  "text": "The steel was tested. It showed good results. The material performed well.",
  "target_burstiness": 0.70,
  "options": {
    "preserve_meaning": true,
    "max_sentence_length": 50,
    "min_sentence_length": 5
  }
}
```

**Field Descriptions:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `text` | string | Yes | - | Text to enhance |
| `target_burstiness` | number | No | `0.70` | Target burstiness score (0-1, higher = more varied) |
| `options.preserve_meaning` | boolean | No | `true` | Don't change meaning during enhancement |
| `options.max_sentence_length` | number | No | `50` | Maximum words per sentence |
| `options.min_sentence_length` | number | No | `5` | Minimum words per sentence |

### Output Schema (Success)

```json
{
  "status": "success",
  "data": {
    "enhanced_text": "The steel underwent rigorous testing and demonstrated favorable results. The material's performance met expectations.",
    "burstiness_analysis": {
      "original_score": 0.35,
      "enhanced_score": 0.68,
      "improvement": 0.33,
      "target_met": false,
      "sentence_lengths": [12, 6]
    },
    "changes": {
      "sentences_merged": 2,
      "sentences_split": 0,
      "words_added": 8
    }
  },
  "metadata": {
    "processing_time_ms": 8901,
    "tool": "burstiness_enhancer",
    "version": "1.0"
  }
}
```

---

## Tool 5: detector_processor.py

**Purpose:** Format text for AI detection testing

### Input Schema

```json
{
  "text": "The austenitic stainless steel was tested at various temperatures.",
  "detector_type": "originality",
  "options": {
    "clean_formatting": true,
    "remove_artifacts": true
  }
}
```

**Field Descriptions:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `text` | string | Yes | - | Text to format |
| `detector_type` | string | No | `"originality"` | `"originality"`, `"gptzero"`, `"turnitin"`, `"generic"` |
| `options.clean_formatting` | boolean | No | `true` | Remove extra whitespace, normalize |
| `options.remove_artifacts` | boolean | No | `true` | Remove processing artifacts |

### Output Schema (Success)

```json
{
  "status": "success",
  "data": {
    "formatted_text": "The austenitic stainless steel was tested at various temperatures.",
    "ready_for_detection": true,
    "formatting_applied": [
      "Normalized whitespace",
      "Removed trailing spaces",
      "Standardized line breaks"
    ]
  },
  "metadata": {
    "processing_time_ms": 567,
    "tool": "detector_processor",
    "version": "1.0",
    "detector_type": "originality"
  }
}
```

---

## Tool 6: perplexity_calculator.py

**Purpose:** Calculate GPT-2 perplexity score

### Input Schema

```json
{
  "text": "The austenitic stainless steel was tested at various temperatures.",
  "model": "gpt2",
  "options": {
    "stride": 512,
    "max_length": 1024,
    "device": "cpu"
  }
}
```

**Field Descriptions:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `text` | string | Yes | - | Text to analyze |
| `model` | string | No | `"gpt2"` | `"gpt2"`, `"gpt2-medium"`, `"gpt2-large"` |
| `options.stride` | number | No | `512` | Sliding window stride |
| `options.max_length` | number | No | `1024` | Maximum sequence length |
| `options.device` | string | No | `"cpu"` | `"cpu"` or `"cuda"` |

### Output Schema (Success)

```json
{
  "status": "success",
  "data": {
    "perplexity": 87.34,
    "interpretation": "human-like",
    "details": {
      "token_count": 156,
      "sequence_count": 1,
      "average_log_likelihood": -4.468
    },
    "benchmark": {
      "ai_generated_typical": "20-50",
      "human_written_typical": "75-150",
      "this_text": "87.34 (human-like)"
    }
  },
  "metadata": {
    "processing_time_ms": 12345,
    "tool": "perplexity_calculator",
    "version": "1.0",
    "model_used": "gpt2",
    "device": "cpu"
  }
}
```

---

## Tool 7: validator.py

**Purpose:** Validate semantic similarity and quality

### Input Schema

```json
{
  "original_text": "The austenitic stainless steel was tested at 850°C.",
  "humanized_text": "The austenite-phase stainless steel underwent testing at 850°C.",
  "thresholds": {
    "min_bertscore": 0.85,
    "min_bleu": 0.70
  },
  "options": {
    "calculate_bertscore": true,
    "calculate_bleu": true,
    "calculate_rouge": false,
    "bertscore_model": "roberta-large"
  }
}
```

**Field Descriptions:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `original_text` | string | Yes | - | Original text (before humanization) |
| `humanized_text` | string | Yes | - | Humanized text (after processing) |
| `thresholds.min_bertscore` | number | No | `0.85` | Minimum acceptable BERTScore (0-1) |
| `thresholds.min_bleu` | number | No | `0.70` | Minimum acceptable BLEU score (0-1) |
| `options.calculate_bertscore` | boolean | No | `true` | Calculate BERTScore (slow, ~45s) |
| `options.calculate_bleu` | boolean | No | `true` | Calculate BLEU score (fast, <1s) |
| `options.calculate_rouge` | boolean | No | `false` | Calculate ROUGE score (medium, ~5s) |
| `options.bertscore_model` | string | No | `"roberta-large"` | Model for BERTScore |

### Output Schema (Success)

```json
{
  "status": "success",
  "data": {
    "validation_passed": true,
    "scores": {
      "bertscore": {
        "precision": 0.923,
        "recall": 0.918,
        "f1": 0.920
      },
      "bleu": 0.756,
      "rouge": null
    },
    "thresholds_met": {
      "bertscore": true,
      "bleu": true
    },
    "quality_assessment": {
      "semantic_preservation": "excellent",
      "overall_quality": "pass"
    }
  },
  "metadata": {
    "processing_time_ms": 45678,
    "tool": "validator",
    "version": "1.0",
    "bertscore_model": "roberta-large"
  }
}
```

---

## Tool 8: state_manager.py

**Purpose:** Manage checkpoints and iteration state

### Input Schema

**Action: Save Checkpoint**
```json
{
  "action": "save",
  "checkpoint_data": {
    "iteration": 3,
    "current_text": "Humanized text after iteration 3...",
    "detection_score": 0.25,
    "scores": {
      "perplexity": 82.5,
      "burstiness": 0.65,
      "bertscore": 0.91
    },
    "component_outputs": {
      "term_protector": { ... },
      "paraphraser_processor": { ... }
    }
  },
  "checkpoint_id": "paper_abc123_iter3"
}
```

**Action: Load Checkpoint**
```json
{
  "action": "load",
  "checkpoint_id": "paper_abc123_iter3"
}
```

**Action: List Checkpoints**
```json
{
  "action": "list",
  "paper_id": "paper_abc123"
}
```

**Field Descriptions:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `action` | string | Yes | `"save"`, `"load"`, `"list"`, `"delete"` |
| `checkpoint_data` | object | For save | Full checkpoint data to save |
| `checkpoint_id` | string | For save/load/delete | Unique checkpoint identifier |
| `paper_id` | string | For list | Filter by paper ID |

### Output Schema (Success - Save)

```json
{
  "status": "success",
  "data": {
    "checkpoint_saved": true,
    "checkpoint_id": "paper_abc123_iter3",
    "checkpoint_path": ".humanizer/checkpoints/paper_abc123_iter3.json",
    "size_bytes": 15678,
    "compressed": true
  },
  "metadata": {
    "processing_time_ms": 234,
    "tool": "state_manager",
    "version": "1.0",
    "timestamp": "2025-10-30T10:15:30Z"
  }
}
```

### Output Schema (Success - Load)

```json
{
  "status": "success",
  "data": {
    "checkpoint_found": true,
    "checkpoint_data": {
      "iteration": 3,
      "current_text": "Humanized text after iteration 3...",
      "detection_score": 0.25,
      "scores": { ... },
      "component_outputs": { ... }
    },
    "checkpoint_age_seconds": 3600
  },
  "metadata": {
    "processing_time_ms": 123,
    "tool": "state_manager",
    "version": "1.0"
  }
}
```

### Output Schema (Success - List)

```json
{
  "status": "success",
  "data": {
    "checkpoints": [
      {
        "checkpoint_id": "paper_abc123_iter1",
        "iteration": 1,
        "detection_score": 0.78,
        "timestamp": "2025-10-30T09:00:00Z",
        "size_bytes": 12345
      },
      {
        "checkpoint_id": "paper_abc123_iter2",
        "iteration": 2,
        "detection_score": 0.45,
        "timestamp": "2025-10-30T09:15:00Z",
        "size_bytes": 13456
      },
      {
        "checkpoint_id": "paper_abc123_iter3",
        "iteration": 3,
        "detection_score": 0.25,
        "timestamp": "2025-10-30T09:30:00Z",
        "size_bytes": 15678
      }
    ],
    "total_checkpoints": 3
  },
  "metadata": {
    "processing_time_ms": 89,
    "tool": "state_manager",
    "version": "1.0"
  }
}
```

---

## Common Error Types

### 1. ValidationError

**When:** Input validation fails (missing required field, invalid type, out of range)

```json
{
  "status": "error",
  "error": {
    "type": "ValidationError",
    "message": "Field 'text' is required but missing",
    "details": {
      "field": "text",
      "expected_type": "string",
      "received": null
    }
  }
}
```

### 2. ProcessingError

**When:** Processing fails mid-execution (model error, calculation failure)

```json
{
  "status": "error",
  "error": {
    "type": "ProcessingError",
    "message": "Failed to load spaCy model: en_core_web_trf not found",
    "details": {
      "model_name": "en_core_web_trf",
      "suggested_fix": "Run: python -m spacy download en_core_web_trf"
    }
  }
}
```

### 3. ConfigError

**When:** Configuration file missing or invalid

```json
{
  "status": "error",
  "error": {
    "type": "ConfigError",
    "message": "Configuration file not found: config/config.yaml",
    "details": {
      "expected_path": "config/config.yaml",
      "searched_paths": ["config/config.yaml", "./config/config.yaml"]
    }
  }
}
```

### 4. FileNotFoundError

**When:** Required file (glossary, patterns, checkpoint) not found

```json
{
  "status": "error",
  "error": {
    "type": "FileNotFoundError",
    "message": "Glossary file not found: data/glossary.json",
    "details": {
      "file_path": "data/glossary.json",
      "file_type": "glossary"
    }
  }
}
```

### 5. APIError

**When:** External API call fails (if using Originality.ai for detection)

```json
{
  "status": "error",
  "error": {
    "type": "APIError",
    "message": "Originality.ai API request failed: Rate limit exceeded",
    "details": {
      "api": "originality.ai",
      "status_code": 429,
      "retry_after_seconds": 60
    }
  }
}
```

---

## Schema Validation

### Python JSON Schema Validation

Use `jsonschema` library to validate inputs:

```python
from jsonschema import validate, ValidationError

# Define schema
term_protector_schema = {
    "type": "object",
    "properties": {
        "text": {"type": "string"},
        "glossary_path": {"type": "string"},
        "protection_tier": {
            "type": "string",
            "enum": ["auto", "tier1", "tier2", "tier3", "all"]
        }
    },
    "required": ["text", "glossary_path"]
}

# Validate input
try:
    validate(instance=input_data, schema=term_protector_schema)
except ValidationError as e:
    return error_response("ValidationError", str(e))
```

---

## Usage Examples

### Example 1: Full Pipeline (Term Protection → Paraphrasing → Validation)

**Step 1: Protect Terms**
```bash
echo '{
  "text": "The AISI 304 steel was tested at 850°C.",
  "glossary_path": "data/glossary.json",
  "protection_tier": "auto"
}' | python src/tools/term_protector.py
```

**Output:**
```json
{
  "status": "success",
  "data": {
    "protected_text": "The __TERM_001__ steel was tested at __NUM_001__.",
    "placeholders": {
      "__TERM_001__": "AISI 304",
      "__NUM_001__": "850°C"
    }
  }
}
```

**Step 2: Paraphrase (via Claude Code)**
```
[Claude paraphrases protected text]
→ "The __TERM_001__ steel underwent testing at __NUM_001__."
```

**Step 3: Process Paraphrase**
```bash
echo '{
  "original_text": "The __TERM_001__ steel was tested at __NUM_001__.",
  "paraphrased_text": "The __TERM_001__ steel underwent testing at __NUM_001__.",
  "protected_placeholders": {
    "__TERM_001__": "AISI 304",
    "__NUM_001__": "850°C"
  },
  "aggression_level": "moderate"
}' | python src/tools/paraphraser_processor.py
```

**Step 4: Validate**
```bash
echo '{
  "original_text": "The AISI 304 steel was tested at 850°C.",
  "humanized_text": "The AISI 304 steel underwent testing at 850°C.",
  "thresholds": {
    "min_bertscore": 0.85,
    "min_bleu": 0.70
  }
}' | python src/tools/validator.py
```

---

## Best Practices

### 1. Always Validate Input
```python
def validate_input(data: dict, required_fields: list) -> Optional[dict]:
    """Validate input data has required fields."""
    for field in required_fields:
        if field not in data:
            return error_response(
                "ValidationError",
                f"Required field '{field}' is missing"
            )
    return None  # No error
```

### 2. Provide Detailed Error Messages
```python
# Bad
return {"status": "error", "error": {"message": "Failed"}}

# Good
return {
    "status": "error",
    "error": {
        "type": "FileNotFoundError",
        "message": "Glossary file not found: data/glossary.json",
        "details": {
            "file_path": "data/glossary.json",
            "suggested_fix": "Create glossary.json with at least tier1 terms"
        }
    }
}
```

### 3. Include Metadata
```python
metadata = {
    "processing_time_ms": elapsed_time_ms,
    "tool": "term_protector",
    "version": "1.0",
    "timestamp": datetime.utcnow().isoformat() + "Z"
}
```

### 4. Use Consistent Error Codes
- `ValidationError`: Input validation failed
- `ProcessingError`: Runtime processing error
- `ConfigError`: Configuration issue
- `FileNotFoundError`: Required file missing
- `APIError`: External API failure

---

## Testing

### Unit Test Example

```python
import json
import subprocess

def test_term_protector_success():
    """Test term_protector.py with valid input."""
    input_data = {
        "text": "The AISI 304 steel was tested.",
        "glossary_path": "tests/fixtures/test_glossary.json",
        "protection_tier": "auto"
    }

    # Run tool
    result = subprocess.run(
        ["python", "src/tools/term_protector.py"],
        input=json.dumps(input_data),
        capture_output=True,
        text=True
    )

    # Parse output
    output = json.loads(result.stdout)

    # Assertions
    assert output["status"] == "success"
    assert "__TERM_001__" in output["data"]["protected_text"]
    assert "AISI 304" in output["data"]["placeholders"].values()
```

---

**Status:** ✅ JSON Schemas Complete
**Tools Documented:** 8/8
**Examples Provided:** Yes
**Validation Guide:** Yes

**Last Updated:** 2025-10-30
**Next:** Data Formats Documentation (`docs/data-formats.md`)
