#!/usr/bin/env python3
"""
Fingerprint Remover CLI Tool

Stdin/stdout JSON interface for AI fingerprint removal.

Input JSON:
{
    "text": "Text to process...",
    "aggressiveness": "moderate"  // subtle, moderate, aggressive
}

Output JSON:
{
    "cleaned_text": "Text with fingerprints removed...",
    "patterns_removed": 42,
    "aggressiveness": "moderate"
}
"""

import json
import sys
from typing import Dict, Any
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.tools.fingerprint_remover import FingerprintRemover


def process_fingerprint_removal(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process fingerprint removal request.

    Args:
        input_data: Input JSON with text and aggressiveness

    Returns:
        Output JSON with cleaned text
    """
    text = input_data.get("text", "")
    aggressiveness = input_data.get("aggressiveness", "moderate")

    if not text:
        return {
            "error": "Missing required field: text",
            "cleaned_text": "",
            "patterns_removed": 0,
            "aggressiveness": aggressiveness
        }

    # Validate aggressiveness
    valid_levels = ["subtle", "moderate", "aggressive"]
    if aggressiveness not in valid_levels:
        return {
            "error": f"Invalid aggressiveness. Must be one of: {', '.join(valid_levels)}",
            "cleaned_text": text,
            "patterns_removed": 0,
            "aggressiveness": aggressiveness
        }

    try:
        # Initialize fingerprint remover
        remover = FingerprintRemover(aggressiveness=aggressiveness)

        # Remove fingerprints
        cleaned_text, patterns_removed = remover.remove_fingerprints(text)

        return {
            "cleaned_text": cleaned_text,
            "patterns_removed": patterns_removed,
            "aggressiveness": aggressiveness
        }

    except Exception as e:
        return {
            "error": str(e),
            "cleaned_text": text,
            "patterns_removed": 0,
            "aggressiveness": aggressiveness
        }


def main():
    """Main CLI entry point."""
    try:
        # Read JSON from stdin
        input_data = json.load(sys.stdin)

        # Process
        output_data = process_fingerprint_removal(input_data)

        # Write JSON to stdout
        json.dump(output_data, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write('\n')

        # Exit with error code if processing failed
        if "error" in output_data:
            sys.exit(1)

    except json.JSONDecodeError as e:
        error_output = {
            "error": f"Invalid JSON input: {str(e)}",
            "cleaned_text": "",
            "patterns_removed": 0,
            "aggressiveness": "moderate"
        }
        json.dump(error_output, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write('\n')
        sys.exit(1)

    except Exception as e:
        error_output = {
            "error": f"Unexpected error: {str(e)}",
            "cleaned_text": "",
            "patterns_removed": 0,
            "aggressiveness": "moderate"
        }
        json.dump(error_output, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write('\n')
        sys.exit(1)


if __name__ == "__main__":
    main()
