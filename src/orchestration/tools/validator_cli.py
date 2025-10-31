#!/usr/bin/env python3
"""
Validator CLI Tool

Stdin/stdout JSON interface for humanization quality validation.

Input JSON:
{
    "original_text": "Original academic text...",
    "humanized_text": "Humanized version...",
    "min_quality_score": 7.0
}

Output JSON:
{
    "is_valid": true,
    "quality_score": 8.5,
    "semantic_similarity": 0.92,
    "readability_score": 7.8,
    "structure_preserved": true,
    "issues": []
}
"""

import json
import sys
from typing import Dict, Any
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.tools.validator import Validator


def process_validation(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process validation request.

    Args:
        input_data: Input JSON with original and humanized text

    Returns:
        Output JSON with validation results
    """
    original_text = input_data.get("original_text", "")
    humanized_text = input_data.get("humanized_text", "")
    min_quality_score = input_data.get("min_quality_score", 7.0)

    if not original_text or not humanized_text:
        return {
            "error": "Missing required fields: original_text and/or humanized_text",
            "is_valid": False,
            "quality_score": 0.0,
            "semantic_similarity": 0.0,
            "readability_score": 0.0,
            "structure_preserved": False,
            "issues": ["Missing input text"]
        }

    try:
        # Initialize validator
        validator = Validator(min_quality_score=min_quality_score)

        # Validate
        result = validator.validate(
            original_text=original_text,
            humanized_text=humanized_text
        )

        return {
            "is_valid": result["is_valid"],
            "quality_score": round(result["quality_score"], 2),
            "semantic_similarity": round(result["semantic_similarity"], 3),
            "readability_score": round(result["readability_score"], 2),
            "structure_preserved": result["structure_preserved"],
            "issues": result.get("issues", [])
        }

    except Exception as e:
        return {
            "error": str(e),
            "is_valid": False,
            "quality_score": 0.0,
            "semantic_similarity": 0.0,
            "readability_score": 0.0,
            "structure_preserved": False,
            "issues": [str(e)]
        }


def main():
    """Main CLI entry point."""
    try:
        # Read JSON from stdin
        input_data = json.load(sys.stdin)

        # Process
        output_data = process_validation(input_data)

        # Write JSON to stdout
        json.dump(output_data, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write('\n')

        # Exit with error code if validation failed
        if not output_data.get("is_valid", False):
            sys.exit(1)

    except json.JSONDecodeError as e:
        error_output = {
            "error": f"Invalid JSON input: {str(e)}",
            "is_valid": False,
            "quality_score": 0.0,
            "semantic_similarity": 0.0,
            "readability_score": 0.0,
            "structure_preserved": False,
            "issues": ["Invalid JSON input"]
        }
        json.dump(error_output, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write('\n')
        sys.exit(1)

    except Exception as e:
        error_output = {
            "error": f"Unexpected error: {str(e)}",
            "is_valid": False,
            "quality_score": 0.0,
            "semantic_similarity": 0.0,
            "readability_score": 0.0,
            "structure_preserved": False,
            "issues": [str(e)]
        }
        json.dump(error_output, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write('\n')
        sys.exit(1)


if __name__ == "__main__":
    main()
