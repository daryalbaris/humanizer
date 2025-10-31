#!/usr/bin/env python3
"""
Term Protector CLI Tool

Stdin/stdout JSON interface for term protection.

Input JSON:
{
    "text": "Academic paper text...",
    "custom_terms": ["optional", "custom", "terms"]
}

Output JSON:
{
    "protected_text": "Text with protected terms...",
    "protected_terms": ["term1", "term2", ...],
    "protection_count": 42
}
"""

import json
import sys
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pathlib import Path
from src.tools.term_protector import TermProtector


def process_term_protection(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process term protection request.

    Args:
        input_data: Input JSON with text and optional custom_terms

    Returns:
        Output JSON with protected text and terms
    """
    text = input_data.get("text", "")
    custom_terms = input_data.get("custom_terms", [])

    if not text:
        return {
            "error": "Missing required field: text",
            "protected_text": "",
            "protected_terms": [],
            "protection_count": 0
        }

    try:
        # Initialize term protector
        protector = TermProtector()

        # Add custom terms if provided
        if custom_terms:
            protector.add_custom_terms(custom_terms)

        # Protect terms
        protected_text, protected_terms = protector.protect_terms(text)

        return {
            "protected_text": protected_text,
            "protected_terms": list(protected_terms),
            "protection_count": len(protected_terms)
        }

    except Exception as e:
        return {
            "error": str(e),
            "protected_text": text,
            "protected_terms": [],
            "protection_count": 0
        }


def main():
    """Main CLI entry point."""
    try:
        # Read JSON from stdin
        input_data = json.load(sys.stdin)

        # Process
        output_data = process_term_protection(input_data)

        # Write JSON to stdout
        json.dump(output_data, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write('\n')

        # Exit with error code if processing failed
        if "error" in output_data:
            sys.exit(1)

    except json.JSONDecodeError as e:
        error_output = {
            "error": f"Invalid JSON input: {str(e)}",
            "protected_text": "",
            "protected_terms": [],
            "protection_count": 0
        }
        json.dump(error_output, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write('\n')
        sys.exit(1)

    except Exception as e:
        error_output = {
            "error": f"Unexpected error: {str(e)}",
            "protected_text": "",
            "protected_terms": [],
            "protection_count": 0
        }
        json.dump(error_output, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write('\n')
        sys.exit(1)


if __name__ == "__main__":
    main()
