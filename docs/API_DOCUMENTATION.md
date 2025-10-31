# BMAD Academic Humanizer - API Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Authentication](#authentication)
4. [API Endpoints](#api-endpoints)
5. [Request/Response Format](#requestresponse-format)
6. [Error Handling](#error-handling)
7. [Code Examples](#code-examples)
8. [Rate Limits](#rate-limits)
9. [Best Practices](#best-practices)

## Introduction

The BMAD Academic Humanizer API provides programmatic access to humanize AI-generated academic text while maintaining academic integrity and quality.

### Base URL

```
Development: http://localhost:8000
Production: TBD
```

### API Version

Current version: `v1.0.0`

## Getting Started

### Prerequisites

- Python 3.10+
- Required packages: `requests`, `json`

### Quick Start Example

```python
import requests

# API endpoint
url = "http://localhost:8000/fingerprint/remove"

# Request payload
payload = {
    "text": "It is important to note that the results may indicate significance.",
    "aggressiveness": "moderate",
    "section_type": "results"
}

# Make request
response = requests.post(url, json=payload)
result = response.json()

print(result['data']['cleaned_text'])
# Output: "The results indicate significance."
```

## Authentication

**Development:** No authentication required

**Production:** API key authentication required

```python
headers = {
    "X-API-Key": "your_api_key_here",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
```

## API Endpoints

### 1. Fingerprint Removal

Remove AI writing patterns and fingerprints from text.

**Endpoint:** `POST /fingerprint/remove`

**Request Body:**

```json
{
  "text": "string (required, 10-100000 chars)",
  "aggressiveness": "conservative|moderate|aggressive (optional, default: moderate)",
  "section_type": "introduction|methods|results|discussion|conclusion|general (optional, default: general)"
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "cleaned_text": "string",
    "fingerprints_removed": [
      {
        "type": "filler_phrase",
        "original": "It is important to note that",
        "replacement": "",
        "position": 0
      }
    ],
    "statistics": {
      "total_removals": 5,
      "filler_phrases": 2,
      "hedging_words": 2,
      "punctuation_tells": 1,
      "structure_fixes": 0
    }
  },
  "metadata": {
    "processing_time_ms": 125,
    "tool": "fingerprint_remover",
    "version": "1.0"
  }
}
```

**Example Usage:**

```python
import requests

def remove_fingerprints(text, aggressiveness="moderate"):
    """Remove AI fingerprints from text"""
    url = "http://localhost:8000/fingerprint/remove"

    payload = {
        "text": text,
        "aggressiveness": aggressiveness,
        "section_type": "results"
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        result = response.json()
        return result['data']['cleaned_text']
    else:
        raise Exception(f"API Error: {response.status_code}")

# Usage
text = "It is important to note that the results may show significance."
cleaned = remove_fingerprints(text)
print(cleaned)
# Output: "The results show significance."
```

### 2. Burstiness Enhancement

Add natural variation in sentence structures to mimic human writing.

**Endpoint:** `POST /burstiness/enhance`

**Request Body:**

```json
{
  "text": "string (required, 50-100000 chars)",
  "target_burstiness": "number (optional, 0.3-1.0, default: 0.6)",
  "strategy": "merge_and_split|add_connectors|vary_syntax|all (optional, default: all)"
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "enhanced_text": "string",
    "original_burstiness": 0.15,
    "enhanced_burstiness": 0.62,
    "transformations_applied": [
      {
        "type": "sentence_merge",
        "position": 25,
        "description": "Merged sentences 2 and 3"
      }
    ],
    "statistics": {
      "original_avg_sentence_length": 12.3,
      "enhanced_avg_sentence_length": 15.7,
      "original_sentence_count": 3,
      "enhanced_sentence_count": 3
    }
  },
  "metadata": {
    "processing_time_ms": 215,
    "tool": "burstiness_enhancer",
    "version": "1.0"
  }
}
```

**Example Usage:**

```python
def enhance_burstiness(text, target=0.6):
    """Enhance text burstiness for more natural variation"""
    url = "http://localhost:8000/burstiness/enhance"

    payload = {
        "text": text,
        "target_burstiness": target,
        "strategy": "all"
    }

    response = requests.post(url, json=payload)
    result = response.json()

    return {
        'text': result['data']['enhanced_text'],
        'original_score': result['data']['original_burstiness'],
        'enhanced_score': result['data']['enhanced_burstiness']
    }

# Usage
text = "This is a sentence. This is another. This is a third."
result = enhance_burstiness(text)
print(f"Burstiness: {result['original_score']} → {result['enhanced_score']}")
print(result['text'])
```

### 3. Imperfection Injection

Add subtle, human-like imperfections to text.

**Endpoint:** `POST /imperfection/inject`

**Request Body:**

```json
{
  "text": "string (required, 10-100000 chars)",
  "level": "subtle|moderate|noticeable (optional, default: subtle)",
  "preserve_academic_quality": "boolean (optional, default: true)"
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "modified_text": "string",
    "imperfections_added": [
      {
        "type": "punctuation_variation",
        "position": 52,
        "description": "Changed period to semicolon"
      }
    ],
    "statistics": {
      "total_imperfections": 2,
      "academic_quality_preserved": true
    }
  },
  "metadata": {
    "processing_time_ms": 95,
    "tool": "imperfection_injector",
    "version": "1.0"
  }
}
```

**Example Usage:**

```python
def inject_imperfections(text, level="subtle"):
    """Add human-like imperfections"""
    url = "http://localhost:8000/imperfection/inject"

    payload = {
        "text": text,
        "level": level,
        "preserve_academic_quality": True
    }

    response = requests.post(url, json=payload)
    result = response.json()

    return result['data']['modified_text']

# Usage
text = "The research demonstrates findings. The methodology is sound."
modified = inject_imperfections(text)
print(modified)
```

### 4. Reference Analysis

Analyze references and citations in academic text.

**Endpoint:** `POST /reference/analyze`

**Request Body:**

```json
{
  "text": "string (required, 50-100000 chars)",
  "expected_style": "apa|mla|chicago|harvard|ieee (optional)"
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "citations_found": [
      {
        "text": "Smith et al. (2020)",
        "position": 13,
        "style": "apa",
        "valid": true
      }
    ],
    "statistics": {
      "total_citations": 2,
      "valid_citations": 2,
      "invalid_citations": 0,
      "citation_density": 0.15
    },
    "style_consistency": {
      "detected_style": "apa",
      "consistency_score": 1.0
    }
  },
  "metadata": {
    "processing_time_ms": 180,
    "tool": "reference_analyzer",
    "version": "1.0"
  }
}
```

**Example Usage:**

```python
def analyze_references(text, expected_style="apa"):
    """Analyze citations in text"""
    url = "http://localhost:8000/reference/analyze"

    payload = {
        "text": text,
        "expected_style": expected_style
    }

    response = requests.post(url, json=payload)
    result = response.json()

    citations = result['data']['citations_found']
    stats = result['data']['statistics']

    return {
        'total_citations': stats['total_citations'],
        'valid_citations': stats['valid_citations'],
        'citation_density': stats['citation_density'],
        'citations': citations
    }

# Usage
text = "According to Smith et al. (2020), the findings are significant."
analysis = analyze_references(text)
print(f"Found {analysis['total_citations']} citations")
```

### 5. AI Detection

Test text against AI detection systems.

**Endpoint:** `POST /detect/ai`

**Request Body:**

```json
{
  "text": "string (required, 100-100000 chars)",
  "detectors": ["gptzero", "originality", "turnitin"] (optional, array)
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "overall_ai_score": 0.25,
    "human_probability": 0.75,
    "detector_results": {
      "gptzero": {
        "ai_probability": 0.30,
        "human_probability": 0.70,
        "confidence": 0.85
      },
      "originality": {
        "ai_probability": 0.20,
        "human_probability": 0.80,
        "confidence": 0.90
      }
    },
    "recommendation": "Text appears human-written"
  },
  "metadata": {
    "processing_time_ms": 3500,
    "tool": "detector_processor",
    "version": "1.0"
  }
}
```

**Example Usage:**

```python
def test_ai_detection(text, detectors=None):
    """Test text against AI detectors"""
    url = "http://localhost:8000/detect/ai"

    payload = {
        "text": text,
        "detectors": detectors or ["gptzero", "originality"]
    }

    response = requests.post(url, json=payload)
    result = response.json()

    return {
        'human_probability': result['data']['human_probability'],
        'ai_score': result['data']['overall_ai_score'],
        'recommendation': result['data']['recommendation'],
        'detectors': result['data']['detector_results']
    }

# Usage
text = "The research demonstrates significant findings."
detection = test_ai_detection(text)
print(f"Human probability: {detection['human_probability']:.2%}")
print(f"Recommendation: {detection['recommendation']}")
```

### 6. Validation

Validate academic text quality.

**Endpoint:** `POST /validate`

**Request Body:**

```json
{
  "text": "string (required, 50-100000 chars)",
  "check_academic_standards": "boolean (optional, default: true)",
  "check_readability": "boolean (optional, default: true)",
  "check_structure": "boolean (optional, default: true)"
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "overall_score": 8.5,
    "passed": true,
    "checks": {
      "academic_standards": {
        "passed": true,
        "score": 9.0,
        "issues": []
      },
      "readability": {
        "passed": true,
        "score": 8.5,
        "flesch_reading_ease": 65.5,
        "flesch_kincaid_grade": 10.2
      },
      "structure": {
        "passed": true,
        "score": 8.0,
        "paragraph_count": 3,
        "avg_paragraph_length": 85
      }
    },
    "recommendations": []
  },
  "metadata": {
    "processing_time_ms": 250,
    "tool": "validator",
    "version": "1.0"
  }
}
```

**Example Usage:**

```python
def validate_text(text):
    """Validate academic text quality"""
    url = "http://localhost:8000/validate"

    payload = {
        "text": text,
        "check_academic_standards": True,
        "check_readability": True,
        "check_structure": True
    }

    response = requests.post(url, json=payload)
    result = response.json()

    data = result['data']
    return {
        'passed': data['passed'],
        'overall_score': data['overall_score'],
        'readability_score': data['checks']['readability']['flesch_reading_ease'],
        'recommendations': data['recommendations']
    }

# Usage
text = "The research demonstrates significant findings with robust methodology."
validation = validate_text(text)
print(f"Quality score: {validation['overall_score']}/10")
print(f"Readability: {validation['readability_score']}")
```

### 7. Perplexity Analysis

Calculate perplexity score to measure text predictability.

**Endpoint:** `POST /analyze/perplexity`

**Request Body:**

```json
{
  "text": "string (required, 10-100000 chars)",
  "model": "gpt2|gpt2-medium|gpt2-large (optional, default: gpt2)"
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "overall_perplexity": 150.32,
    "section_perplexities": [],
    "perplexity_distribution": {
      "min": 145.5,
      "max": 155.8,
      "mean": 150.32,
      "median": 150.1,
      "std_dev": 3.2
    }
  },
  "metadata": {
    "processing_time_ms": 1250,
    "tool": "perplexity_calculator",
    "version": "1.0",
    "model": "gpt2"
  }
}
```

**Example Usage:**

```python
def calculate_perplexity(text, model="gpt2"):
    """Calculate perplexity score"""
    url = "http://localhost:8000/analyze/perplexity"

    payload = {
        "text": text,
        "model": model
    }

    response = requests.post(url, json=payload)
    result = response.json()

    return {
        'score': result['data']['overall_perplexity'],
        'distribution': result['data']['perplexity_distribution']
    }

# Usage
text = "The research demonstrates findings."
perplexity = calculate_perplexity(text)
print(f"Perplexity: {perplexity['score']:.2f}")
```

### 8. Full Pipeline

Run the complete humanization pipeline.

**Endpoint:** `POST /pipeline/full`

**Request Body:**

```json
{
  "text": "string (required, 100-100000 chars)",
  "config": {
    "paraphrase": "boolean (optional, default: false)",
    "fingerprint_removal": {
      "aggressiveness": "conservative|moderate|aggressive"
    },
    "burstiness_enhancement": {
      "target_burstiness": "number (0.3-1.0)"
    },
    "imperfection_injection": {
      "level": "subtle|moderate|noticeable"
    },
    "run_validation": "boolean (optional, default: true)",
    "run_detection": "boolean (optional, default: true)"
  }
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "final_text": "string",
    "pipeline_stages": [
      {
        "stage": "paraphrase",
        "success": true,
        "duration_ms": 2500
      },
      {
        "stage": "fingerprint_removal",
        "success": true,
        "duration_ms": 125
      }
    ],
    "validation_result": {
      "passed": true,
      "score": 8.5
    },
    "detection_result": {
      "human_probability": 0.75
    },
    "improvements": {
      "original_ai_probability": 0.85,
      "final_ai_probability": 0.25,
      "improvement_percentage": 70.6
    }
  },
  "metadata": {
    "total_processing_time_ms": 8500,
    "tool": "full_pipeline",
    "version": "1.0"
  }
}
```

**Example Usage:**

```python
def run_full_pipeline(text):
    """Run complete humanization pipeline"""
    url = "http://localhost:8000/pipeline/full"

    payload = {
        "text": text,
        "config": {
            "paraphrase": True,
            "fingerprint_removal": {
                "aggressiveness": "moderate"
            },
            "burstiness_enhancement": {
                "target_burstiness": 0.6
            },
            "imperfection_injection": {
                "level": "subtle"
            },
            "run_validation": True,
            "run_detection": True
        }
    }

    response = requests.post(url, json=payload)
    result = response.json()

    data = result['data']
    return {
        'final_text': data['final_text'],
        'passed_validation': data['validation_result']['passed'],
        'human_probability': data['detection_result']['human_probability'],
        'improvement': data['improvements']['improvement_percentage']
    }

# Usage
text = "It is important to note that the research demonstrates findings."
result = run_full_pipeline(text)
print(f"Humanization improvement: {result['improvement']:.1f}%")
print(f"Human probability: {result['human_probability']:.2%}")
print(f"Final text: {result['final_text']}")
```

## Request/Response Format

### Standard Request Format

All requests use JSON format:

```json
{
  "field1": "value1",
  "field2": "value2"
}
```

**Headers:**

```
Content-Type: application/json
X-API-Key: your_api_key (production only)
```

### Standard Response Format

All successful responses follow this structure:

```json
{
  "status": "success",
  "data": {
    // Tool-specific response data
  },
  "metadata": {
    "processing_time_ms": 0,
    "tool": "tool_name",
    "version": "1.0"
  }
}
```

### Error Response Format

Error responses follow this structure:

```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      // Additional error details
    }
  },
  "metadata": {
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

## Error Handling

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_INPUT` | 400 | Invalid request parameters |
| `TEXT_TOO_SHORT` | 400 | Text below minimum length |
| `TEXT_TOO_LONG` | 400 | Text exceeds maximum length |
| `INVALID_AGGRESSIVENESS` | 400 | Invalid aggressiveness value |
| `PROCESSING_ERROR` | 500 | Internal processing error |
| `API_TIMEOUT` | 504 | Request timeout |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |

### Error Handling Example

```python
import requests

def safe_api_call(url, payload):
    """Make API call with error handling"""
    try:
        response = requests.post(url, json=payload, timeout=30)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            error = response.json()['error']
            print(f"Invalid input: {error['message']}")
            return None
        elif response.status_code == 429:
            print("Rate limit exceeded. Please wait.")
            return None
        elif response.status_code == 500:
            print("Server error. Please try again later.")
            return None
        else:
            print(f"Unexpected error: {response.status_code}")
            return None

    except requests.exceptions.Timeout:
        print("Request timeout. Try again with smaller text.")
        return None
    except requests.exceptions.ConnectionError:
        print("Connection error. Check API availability.")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None

# Usage
result = safe_api_call("http://localhost:8000/fingerprint/remove", {
    "text": "Sample text"
})
```

## Code Examples

### Example 1: Complete Humanization Workflow

```python
import requests

class BMADHumanizer:
    """BMAD API client for text humanization"""

    def __init__(self, base_url="http://localhost:8000", api_key=None):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["X-API-Key"] = api_key

    def humanize(self, text, config=None):
        """Humanize text using full pipeline"""
        url = f"{self.base_url}/pipeline/full"

        default_config = {
            "paraphrase": False,
            "fingerprint_removal": {"aggressiveness": "moderate"},
            "burstiness_enhancement": {"target_burstiness": 0.6},
            "imperfection_injection": {"level": "subtle"},
            "run_validation": True,
            "run_detection": True
        }

        payload = {
            "text": text,
            "config": config or default_config
        }

        response = requests.post(url, json=payload, headers=self.headers)

        if response.status_code == 200:
            return response.json()['data']
        else:
            raise Exception(f"API Error: {response.status_code}")

# Usage
humanizer = BMADHumanizer()

text = """
It is important to note that the research demonstrates significant findings.
Moreover, it should be noted that the methodology is robust and reliable.
Furthermore, the results may indicate important implications for future work.
"""

result = humanizer.humanize(text)

print("Original AI probability:", result['improvements']['original_ai_probability'])
print("Final AI probability:", result['improvements']['final_ai_probability'])
print("Improvement:", result['improvements']['improvement_percentage'], "%")
print("\nHumanized text:")
print(result['final_text'])
```

### Example 2: Batch Processing Multiple Documents

```python
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_document(text, config):
    """Process single document"""
    url = "http://localhost:8000/pipeline/full"
    payload = {"text": text, "config": config}

    response = requests.post(url, json=payload)
    return response.json()['data']

def batch_humanize(documents, config=None, max_workers=4):
    """Process multiple documents in parallel"""
    default_config = {
        "fingerprint_removal": {"aggressiveness": "moderate"},
        "burstiness_enhancement": {"target_burstiness": 0.6},
        "imperfection_injection": {"level": "subtle"}
    }

    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_document, doc, config or default_config): idx
            for idx, doc in enumerate(documents)
        }

        for future in as_completed(futures):
            idx = futures[future]
            try:
                result = future.result()
                results.append((idx, result))
            except Exception as e:
                print(f"Error processing document {idx}: {str(e)}")
                results.append((idx, None))

    # Sort by original index
    results.sort(key=lambda x: x[0])
    return [r[1] for r in results]

# Usage
documents = [
    "It is important to note that document 1 content...",
    "Moreover, document 2 demonstrates findings...",
    "Furthermore, document 3 shows results..."
]

results = batch_humanize(documents, max_workers=3)

for idx, result in enumerate(results):
    if result:
        print(f"Document {idx + 1}:")
        print(f"  Human probability: {result['detection_result']['human_probability']:.2%}")
        print(f"  Validation passed: {result['validation_result']['passed']}")
        print()
```

### Example 3: Progressive Humanization with Quality Checks

```python
import requests

def progressive_humanize(text, quality_threshold=8.0):
    """
    Progressively humanize text, increasing aggressiveness
    until quality threshold is met
    """
    base_url = "http://localhost:8000"

    aggressiveness_levels = ["conservative", "moderate", "aggressive"]

    for level in aggressiveness_levels:
        print(f"Trying {level} humanization...")

        # Remove fingerprints
        response = requests.post(f"{base_url}/fingerprint/remove", json={
            "text": text,
            "aggressiveness": level
        })
        cleaned_text = response.json()['data']['cleaned_text']

        # Enhance burstiness
        response = requests.post(f"{base_url}/burstiness/enhance", json={
            "text": cleaned_text,
            "target_burstiness": 0.6
        })
        enhanced_text = response.json()['data']['enhanced_text']

        # Validate quality
        response = requests.post(f"{base_url}/validate", json={
            "text": enhanced_text
        })
        validation = response.json()['data']

        # Test detection
        response = requests.post(f"{base_url}/detect/ai", json={
            "text": enhanced_text
        })
        detection = response.json()['data']

        print(f"  Quality score: {validation['overall_score']}")
        print(f"  Human probability: {detection['human_probability']:.2%}")

        # Check if meets threshold
        if (validation['overall_score'] >= quality_threshold and
            detection['human_probability'] >= 0.7):
            print(f"Success with {level} level!")
            return {
                'text': enhanced_text,
                'level': level,
                'quality_score': validation['overall_score'],
                'human_probability': detection['human_probability']
            }

    print("Warning: Could not meet quality threshold")
    return None

# Usage
text = "It is important to note that the research findings are significant."
result = progressive_humanize(text, quality_threshold=8.0)

if result:
    print(f"\nFinal text: {result['text']}")
    print(f"Achieved with: {result['level']} aggressiveness")
```

## Rate Limits

### Development

No rate limits for local development.

### Production

(TBD based on deployment configuration)

Expected limits:
- 100 requests per minute per API key
- 1000 requests per day per API key
- Maximum text length: 100,000 characters per request

### Rate Limit Headers

Responses include rate limit information:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

## Best Practices

### 1. Input Validation

Always validate input before sending requests:

```python
def validate_input(text):
    """Validate text input"""
    if len(text) < 10:
        raise ValueError("Text too short (minimum 10 characters)")
    if len(text) > 100000:
        raise ValueError("Text too long (maximum 100,000 characters)")
    return True
```

### 2. Error Handling

Implement robust error handling:

```python
try:
    result = api_call(text)
except requests.exceptions.Timeout:
    # Retry with smaller chunks
    pass
except requests.exceptions.HTTPError as e:
    # Log error and notify user
    pass
```

### 3. Caching

Cache results for repeated requests:

```python
import hashlib
import json

cache = {}

def cached_api_call(text, endpoint, payload):
    """Cache API responses"""
    cache_key = hashlib.md5(
        json.dumps({'text': text, 'endpoint': endpoint}).encode()
    ).hexdigest()

    if cache_key in cache:
        return cache[cache_key]

    result = requests.post(endpoint, json=payload).json()
    cache[cache_key] = result
    return result
```

### 4. Batch Processing

Process multiple documents efficiently:

```python
from concurrent.futures import ThreadPoolExecutor

def batch_process(documents, max_workers=4):
    """Process documents in parallel"""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_document, documents))
    return results
```

### 5. Progress Tracking

Track progress for long-running operations:

```python
from tqdm import tqdm

def process_with_progress(documents):
    """Process documents with progress bar"""
    results = []
    for doc in tqdm(documents, desc="Processing"):
        result = process_document(doc)
        results.append(result)
    return results
```

## Troubleshooting

### Common Issues

**1. Timeout Errors**

- Reduce text length
- Increase timeout value
- Split into smaller chunks

**2. Invalid Input Errors**

- Check text length requirements
- Validate enum values (aggressiveness, level, etc.)
- Ensure proper JSON formatting

**3. Rate Limit Errors**

- Implement exponential backoff
- Cache responses
- Batch requests

**4. Quality Issues**

- Try different aggressiveness levels
- Adjust burstiness targets
- Run progressive humanization

## Additional Resources

- OpenAPI Specification: `docs/openapi.yaml`
- Postman Collection: `docs/postman_collection.json`
- Python SDK: `src/sdk/`
- Example Scripts: `examples/api_examples.py`

## Support

For API support:
- GitHub Issues: [bmad-humanizer/issues](https://github.com/bmad-humanizer/issues)
- Email: support@bmad-humanizer.example.com
- Documentation: [docs.bmad-humanizer.example.com](https://docs.bmad-humanizer.example.com)

## Changelog

### v1.0.0 (2024-01-01)

- Initial API release
- 8 core endpoints
- OpenAPI 3.0 specification
- Comprehensive error handling
- Performance optimizations
