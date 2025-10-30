# Data Formats - AI Humanizer System

**Version:** 1.0
**Date:** 2025-10-30
**Purpose:** Define JSON structure for all data files

---

## Overview

This document defines the exact structure for all data files used in the AI Humanizer System:
1. **Glossary** (`data/glossary.json`) - Protected technical terms
2. **Pattern Database** (`data/patterns.json`) - AI fingerprint patterns
3. **Checkpoint Files** (`.humanizer/checkpoints/*.json`) - Iteration state
4. **Reference Text Metadata** (`data/reference_texts/metadata.json`) - Human-written paper info

---

## 1. Glossary Format (`data/glossary.json`)

**Purpose:** Define technical terms that must be protected during paraphrasing

### Structure

```json
{
  "version": "1.0",
  "domain": "metallurgy",
  "last_updated": "2025-10-30",
  "tier1": {
    "description": "Absolute protection - never paraphrase",
    "protection": "absolute",
    "paraphrase_allowed": false,
    "terms": [
      "AISI 304",
      "AISI 316",
      "AISI 316L",
      "AISI 410",
      "AISI 4140",
      "SAF 2205",
      "SAF 2507",
      "austenite",
      "martensite",
      "ferrite",
      "pearlite",
      "bainite",
      "cementite",
      "ledeburite",
      "FCC",
      "BCC",
      "HCP",
      "SEM",
      "TEM",
      "XRD",
      "EBSD",
      "EDS"
    ],
    "term_count": 23
  },
  "tier2": {
    "description": "Context-aware protection - allow synonyms if meaning preserved",
    "protection": "context-aware",
    "paraphrase_allowed": "if_context_preserved",
    "terms": [
      "heat treatment",
      "annealing",
      "quenching",
      "tempering",
      "normalizing",
      "phase diagram",
      "TTT diagram",
      "CCT diagram",
      "equilibrium diagram",
      "solidification",
      "recrystallization",
      "grain growth",
      "precipitation",
      "work hardening",
      "solution treatment",
      "aging"
    ],
    "context_rules": {
      "heat treatment": {
        "allowed_synonyms": ["thermal processing", "heat processing", "thermal treatment"],
        "forbidden_synonyms": ["heating", "warming", "cooking"],
        "context_preservation": "Must refer to controlled heating/cooling process"
      },
      "annealing": {
        "allowed_synonyms": ["softening treatment", "stress relief"],
        "forbidden_synonyms": ["heating"],
        "context_preservation": "Must refer to specific heat treatment for softening"
      },
      "quenching": {
        "allowed_synonyms": ["rapid cooling", "fast cooling"],
        "forbidden_synonyms": ["cooling", "chilling"],
        "context_preservation": "Must indicate rapid cooling from elevated temperature"
      }
    },
    "term_count": 16
  },
  "tier3": {
    "description": "Minimal protection - allow paraphrasing with variations",
    "protection": "minimal",
    "paraphrase_allowed": true,
    "terms": [
      "corrosion resistance",
      "mechanical properties",
      "microstructure",
      "grain size",
      "hardness",
      "tensile strength",
      "yield strength",
      "ductility",
      "toughness",
      "impact resistance",
      "fatigue resistance",
      "creep resistance",
      "wear resistance",
      "fracture toughness"
    ],
    "allowed_variations": {
      "corrosion resistance": [
        "resistance to corrosion",
        "corrosion-resistant properties",
        "ability to resist corrosion"
      ],
      "mechanical properties": [
        "mechanical characteristics",
        "mechanical behavior",
        "strength properties"
      ],
      "microstructure": [
        "microscopic structure",
        "internal structure",
        "structural features at microscale"
      ]
    },
    "term_count": 14
  },
  "units": {
    "description": "Measurement units - always protect exact values and units",
    "protection": "absolute",
    "patterns": [
      "\\d+\\s*°C",
      "\\d+\\s*K",
      "\\d+\\s*°F",
      "\\d+\\s*MPa",
      "\\d+\\s*GPa",
      "\\d+\\s*HV",
      "\\d+\\s*HRC",
      "\\d+\\s*%",
      "\\d+\\s*μm",
      "\\d+\\s*mm",
      "\\d+\\s*cm"
    ],
    "examples": [
      "850°C",
      "1173 K",
      "500 MPa",
      "250 HV",
      "45 HRC",
      "18% Cr",
      "10 μm"
    ]
  },
  "citations": {
    "description": "Citation formats - always protect",
    "protection": "absolute",
    "patterns": [
      "\\[[A-Za-z]+\\s*et\\s*al\\.?,\\s*\\d{4}\\]",
      "\\([A-Za-z]+\\s*et\\s*al\\.?,\\s*\\d{4}\\)",
      "\\[[A-Za-z]+,\\s*\\d{4}\\]",
      "\\([A-Za-z]+,\\s*\\d{4}\\)"
    ],
    "examples": [
      "[Smith et al., 2024]",
      "(Jones, 2023)",
      "[Chen et al., 2025]",
      "(Kumar and Patel, 2024)"
    ]
  },
  "statistics": {
    "total_terms": 53,
    "tier1_count": 23,
    "tier2_count": 16,
    "tier3_count": 14,
    "total_protected_patterns": 22
  }
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `version` | string | Glossary version (semantic versioning) |
| `domain` | string | Domain name (e.g., "metallurgy", "materials_science") |
| `last_updated` | string | ISO 8601 date of last update |
| `tier1.terms` | array | List of Tier 1 terms (absolute protection) |
| `tier2.terms` | array | List of Tier 2 terms (context-aware) |
| `tier2.context_rules` | object | Synonym rules for each Tier 2 term |
| `tier3.terms` | array | List of Tier 3 terms (minimal protection) |
| `tier3.allowed_variations` | object | Acceptable paraphrases for Tier 3 terms |
| `units.patterns` | array | Regex patterns for units/measurements |
| `citations.patterns` | array | Regex patterns for citation formats |

---

## 2. Pattern Database Format (`data/patterns.json`)

**Purpose:** Define AI-specific patterns and fingerprints to remove

### Structure

```json
{
  "version": "1.0",
  "last_updated": "2025-10-30",
  "fingerprints": [
    {
      "id": "fp001",
      "pattern": "It is important to note that",
      "regex": "It is important to note that",
      "category": "hedging",
      "confidence": 0.95,
      "removal_strategy": "delete",
      "replacement": null,
      "examples": [
        "It is important to note that the steel exhibited high strength.",
        "It is important to note that corrosion resistance was excellent."
      ]
    },
    {
      "id": "fp002",
      "pattern": "In this study, we",
      "regex": "In this study, we",
      "category": "meta-discourse",
      "confidence": 0.85,
      "removal_strategy": "replace",
      "replacements": [
        "We",
        "This investigation",
        "Our research",
        "The present work"
      ],
      "examples": [
        "In this study, we investigated the mechanical properties.",
        "In this study, we analyzed the microstructure."
      ]
    },
    {
      "id": "fp003",
      "pattern": "It can be seen that",
      "regex": "It can be seen that",
      "category": "hedging",
      "confidence": 0.90,
      "removal_strategy": "delete",
      "replacement": null,
      "examples": [
        "It can be seen that the hardness increased with temperature."
      ]
    },
    {
      "id": "fp004",
      "pattern": "As mentioned above",
      "regex": "As mentioned (above|previously|earlier)",
      "category": "meta-discourse",
      "confidence": 0.88,
      "removal_strategy": "replace",
      "replacements": [
        "As noted",
        "As discussed",
        "Previously"
      ],
      "examples": [
        "As mentioned above, the steel was heat treated.",
        "As mentioned previously, austenite forms at high temperatures."
      ]
    },
    {
      "id": "fp005",
      "pattern": "showcased",
      "regex": "\\bshowcased\\b",
      "category": "overused_word",
      "confidence": 0.70,
      "removal_strategy": "replace",
      "replacements": [
        "demonstrated",
        "exhibited",
        "displayed",
        "showed"
      ],
      "examples": [
        "The material showcased excellent properties."
      ]
    },
    {
      "id": "fp006",
      "pattern": "delve",
      "regex": "\\bdelve(d|s)?\\b",
      "category": "overused_word",
      "confidence": 0.80,
      "removal_strategy": "replace",
      "replacements": [
        "examine",
        "investigate",
        "explore",
        "study"
      ],
      "examples": [
        "We delve into the microstructural changes.",
        "This paper delves into phase transformations."
      ]
    }
  ],
  "categories": {
    "hedging": {
      "description": "Hedging phrases that weaken statements",
      "examples": ["It is important to note", "It can be seen that", "It should be noted"]
    },
    "meta-discourse": {
      "description": "Self-referential phrases about the paper itself",
      "examples": ["In this study", "As mentioned above", "The present work"]
    },
    "overused_word": {
      "description": "Words commonly overused by AI",
      "examples": ["showcased", "delve", "utilize", "leverage", "robust"]
    },
    "passive_voice": {
      "description": "Excessive passive voice constructions",
      "examples": ["was investigated", "was analyzed", "was observed"]
    }
  },
  "statistics": {
    "total_patterns": 6,
    "hedging_count": 2,
    "meta_discourse_count": 2,
    "overused_word_count": 2,
    "average_confidence": 0.85
  }
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique pattern identifier (e.g., "fp001") |
| `pattern` | string | Human-readable pattern description |
| `regex` | string | Regular expression for pattern matching |
| `category` | string | Pattern category (hedging, meta-discourse, overused_word) |
| `confidence` | number | Detection confidence (0-1, higher = more certain) |
| `removal_strategy` | string | "delete" or "replace" |
| `replacements` | array | List of replacement options (if strategy = "replace") |
| `examples` | array | Example sentences containing this pattern |

---

## 3. Checkpoint File Format (`.humanizer/checkpoints/*.json`)

**Purpose:** Save iteration state for resume/rollback capability

### Structure

```json
{
  "checkpoint_id": "paper_abc123_iter3",
  "paper_id": "paper_abc123",
  "iteration": 3,
  "timestamp": "2025-10-30T10:30:45Z",
  "current_text": "Humanized text after iteration 3 processing...",
  "original_text": "Original AI-generated text...",
  "detection_score": 0.25,
  "target_threshold": 0.15,
  "scores": {
    "perplexity": 82.5,
    "burstiness": 0.65,
    "bertscore": {
      "precision": 0.923,
      "recall": 0.918,
      "f1": 0.920
    },
    "bleu": 0.756
  },
  "component_outputs": {
    "term_protector": {
      "placeholders": {
        "__TERM_001__": "AISI 304",
        "__TERM_002__": "austenite",
        "__NUM_001__": "850°C"
      },
      "terms_protected": 2,
      "numbers_protected": 1
    },
    "paraphraser_processor": {
      "aggression_level": "moderate",
      "semantic_similarity": 0.94,
      "changes_applied": 15
    },
    "fingerprint_remover": {
      "patterns_removed": 3,
      "patterns_detected": [
        {"id": "fp001", "pattern": "It is important to note that"},
        {"id": "fp002", "pattern": "In this study, we"},
        {"id": "fp005", "pattern": "showcased"}
      ]
    },
    "burstiness_enhancer": {
      "original_burstiness": 0.45,
      "enhanced_burstiness": 0.65,
      "improvement": 0.20,
      "sentences_merged": 2,
      "sentences_split": 1
    },
    "detector_processor": {
      "formatted_for": "originality",
      "ready": true
    },
    "perplexity_calculator": {
      "perplexity": 82.5,
      "interpretation": "human-like",
      "model": "gpt2"
    },
    "validator": {
      "validation_passed": true,
      "bertscore": 0.920,
      "bleu": 0.756
    }
  },
  "iteration_history": [
    {
      "iteration": 1,
      "detection_score": 0.78,
      "improvement": null,
      "timestamp": "2025-10-30T10:00:00Z"
    },
    {
      "iteration": 2,
      "detection_score": 0.45,
      "improvement": 0.33,
      "timestamp": "2025-10-30T10:15:00Z"
    },
    {
      "iteration": 3,
      "detection_score": 0.25,
      "improvement": 0.20,
      "timestamp": "2025-10-30T10:30:45Z"
    }
  ],
  "config": {
    "max_iterations": 7,
    "detection_threshold": 0.15,
    "early_termination_improvement": 0.02,
    "aggression_level": "moderate"
  },
  "status": {
    "completed": false,
    "reason": "in_progress",
    "next_action": "continue_iteration_4"
  },
  "metadata": {
    "version": "1.0",
    "compressed": true,
    "size_bytes": 15678,
    "created_at": "2025-10-30T10:30:45Z",
    "last_accessed": "2025-10-30T10:30:45Z"
  }
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `checkpoint_id` | string | Unique checkpoint identifier |
| `paper_id` | string | Paper identifier for grouping checkpoints |
| `iteration` | number | Current iteration number (1-7) |
| `current_text` | string | Text after this iteration's processing |
| `original_text` | string | Original AI-generated text (unchanged) |
| `detection_score` | number | AI detection score after this iteration (0-1) |
| `scores` | object | All quality metrics (perplexity, burstiness, BERTScore, BLEU) |
| `component_outputs` | object | Output from each of 8 tools |
| `iteration_history` | array | History of all iterations so far |
| `config` | object | Configuration used for this run |
| `status` | object | Current status and next action |

---

## 4. Reference Text Metadata Format (`data/reference_texts/metadata.json`)

**Purpose:** Store metadata about human-written reference papers

### Structure

```json
{
  "version": "1.0",
  "last_updated": "2025-10-30",
  "papers": [
    {
      "id": "ref001",
      "title": "Microstructural Evolution in AISI 304 Stainless Steel During Heat Treatment",
      "filename": "ref001_aisi304_microstructure.txt",
      "source": "Materials Science and Engineering A",
      "doi": "10.1016/j.msea.2024.123456",
      "year": 2024,
      "authors": ["Smith, J.", "Johnson, M.", "Chen, L."],
      "word_count": 8234,
      "domain": "metallurgy",
      "subdomain": "heat treatment",
      "baseline_scores": {
        "ai_detection": 0.05,
        "perplexity": 95.7,
        "burstiness": 0.72,
        "flesch_reading_ease": 58.3
      },
      "structure": "IMRAD",
      "technical_terms_count": 156,
      "citation_count": 42,
      "notes": "Well-written human paper with excellent technical detail"
    },
    {
      "id": "ref002",
      "title": "Phase Transformation Kinetics in Duplex Stainless Steels",
      "filename": "ref002_duplex_kinetics.txt",
      "source": "Journal of Materials Processing Technology",
      "doi": "10.1016/j.jmatprotec.2024.654321",
      "year": 2024,
      "authors": ["Kumar, R.", "Patel, S."],
      "word_count": 7845,
      "domain": "metallurgy",
      "subdomain": "phase transformations",
      "baseline_scores": {
        "ai_detection": 0.08,
        "perplexity": 88.2,
        "burstiness": 0.68,
        "flesch_reading_ease": 62.1
      },
      "structure": "IMRAD",
      "technical_terms_count": 142,
      "citation_count": 38,
      "notes": "Good example of human writing style in phase transformation research"
    },
    {
      "id": "ref003",
      "title": "Corrosion Behavior of Austenitic Stainless Steels in Marine Environments",
      "filename": "ref003_corrosion_marine.txt",
      "source": "Corrosion Science",
      "doi": "10.1016/j.corsci.2024.789012",
      "year": 2024,
      "authors": ["Garcia, M.", "Anderson, K.", "Lee, Y."],
      "word_count": 9012,
      "domain": "metallurgy",
      "subdomain": "corrosion",
      "baseline_scores": {
        "ai_detection": 0.06,
        "perplexity": 92.3,
        "burstiness": 0.75,
        "flesch_reading_ease": 55.8
      },
      "structure": "IMRAD",
      "technical_terms_count": 178,
      "citation_count": 51,
      "notes": "Excellent example with high burstiness and natural flow"
    }
  ],
  "statistics": {
    "total_papers": 3,
    "average_word_count": 8364,
    "average_ai_detection": 0.063,
    "average_perplexity": 92.1,
    "average_burstiness": 0.717,
    "average_flesch": 58.7
  },
  "usage": {
    "purpose": "Baseline for human writing style",
    "comparison_metrics": ["perplexity", "burstiness", "detection_score"],
    "use_in_validation": true
  }
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique reference paper identifier |
| `title` | string | Paper title |
| `filename` | string | File name in `data/reference_texts/` directory |
| `source` | string | Journal or source name |
| `doi` | string | DOI (Digital Object Identifier) |
| `baseline_scores` | object | Metrics for human-written text baseline |
| `technical_terms_count` | number | Count of technical terms in paper |
| `citation_count` | number | Number of citations in paper |

---

## 5. Configuration File Format (`config/config.yaml`)

**(Already documented in Phase 1, included here for completeness)**

```yaml
humanizer:
  max_iterations: 7
  detection_threshold: 0.15
  early_termination_improvement: 0.02

aggression_levels:
  gentle: 1
  moderate: 2
  aggressive: 3
  intensive: 4
  nuclear: 5

translation_chain:
  enabled: true
  trigger_threshold: 0.05
  languages: ["de", "ja"]

paths:
  glossary: "data/glossary.json"
  patterns: "data/patterns.json"
  checkpoint_dir: ".humanizer/checkpoints"
  log_dir: ".humanizer/logs"
  output_dir: ".humanizer/output"

# ... (rest of config as defined in Phase 1)
```

---

## 6. Log File Format (`.humanizer/logs/*.log`)

**Purpose:** Structured JSON logs for debugging and monitoring

### Structure (JSON Lines format)

```json
{"timestamp": "2025-10-30T10:00:00Z", "level": "INFO", "tool": "orchestrator", "message": "Starting humanization process", "paper_id": "paper_abc123", "max_iterations": 7}
{"timestamp": "2025-10-30T10:00:15Z", "level": "INFO", "tool": "term_protector", "message": "Protected 15 technical terms", "terms_protected": 15, "numbers_protected": 8}
{"timestamp": "2025-10-30T10:00:30Z", "level": "INFO", "tool": "paraphraser_processor", "message": "Paraphrasing completed", "aggression_level": "moderate", "semantic_similarity": 0.94}
{"timestamp": "2025-10-30T10:00:45Z", "level": "WARNING", "tool": "fingerprint_remover", "message": "Low confidence pattern detected", "pattern_id": "fp005", "confidence": 0.70}
{"timestamp": "2025-10-30T10:01:00Z", "level": "ERROR", "tool": "validator", "message": "BERTScore below threshold", "bertscore": 0.82, "threshold": 0.85}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | string | ISO 8601 timestamp |
| `level` | string | Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `tool` | string | Tool name (orchestrator or specific Python tool) |
| `message` | string | Human-readable log message |
| Additional fields | various | Tool-specific context (varies by tool) |

---

## Data Validation

### Python Example: Validate Glossary

```python
from jsonschema import validate, ValidationError

glossary_schema = {
    "type": "object",
    "properties": {
        "version": {"type": "string"},
        "domain": {"type": "string"},
        "tier1": {
            "type": "object",
            "properties": {
                "terms": {"type": "array", "items": {"type": "string"}},
                "protection": {"type": "string", "enum": ["absolute"]},
                "paraphrase_allowed": {"type": "boolean"}
            },
            "required": ["terms", "protection", "paraphrase_allowed"]
        }
    },
    "required": ["version", "domain", "tier1"]
}

def validate_glossary(glossary_data: dict) -> bool:
    """Validate glossary structure."""
    try:
        validate(instance=glossary_data, schema=glossary_schema)
        return True
    except ValidationError as e:
        print(f"Validation error: {e.message}")
        return False
```

---

## Best Practices

### 1. Version All Data Files
```json
{
  "version": "1.0",
  "last_updated": "2025-10-30",
  ...
}
```

### 2. Include Statistics
```json
{
  "statistics": {
    "total_terms": 53,
    "tier1_count": 23,
    ...
  }
}
```

### 3. Use ISO 8601 for Dates
```json
{
  "timestamp": "2025-10-30T10:30:45Z",
  "last_updated": "2025-10-30"
}
```

### 4. Provide Examples
```json
{
  "pattern": "It is important to note that",
  "examples": [
    "It is important to note that the steel exhibited high strength."
  ]
}
```

---

## File Size Estimates

| File | Typical Size | Max Size |
|------|-------------|----------|
| `glossary.json` | 15-30 KB | 100 KB |
| `patterns.json` | 10-20 KB | 50 KB |
| Checkpoint file | 10-50 KB | 200 KB |
| Reference metadata | 5-10 KB | 30 KB |
| Log file (per day) | 1-5 MB | 50 MB |

---

**Status:** ✅ Data Formats Complete
**Files Documented:** 6 types
**Examples Provided:** Yes
**Validation Code:** Yes

**Last Updated:** 2025-10-30
**Next:** Error Handling Strategy (`docs/error-handling-strategy.md`)
