#!/usr/bin/env python3
"""
Burstiness Enhancer CLI Tool

Stdin/stdout JSON interface for burstiness enhancement.

Input JSON:
{
    "text": "Text to enhance...",
    "target_burstiness": 0.6  // 0.0 - 1.0
}

Output JSON:
{
    "enhanced_text": "Text with varied sentence lengths...",
    "burstiness_before": 0.3,
    "burstiness_after": 0.6,
    "sentences_modified": 12
}
"""

import json
import sys
from typing import Dict, Any
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.tools.burstiness_enhancer import BurstinessEnhancer


def process_burstiness_enhancement(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process burstiness enhancement request.

    Args:
        input_data: Input JSON with text and target burstiness

    Returns:
        Output JSON with enhanced text and metrics
    """
    text = input_data.get("text", "")
    target_burstiness = input_data.get("target_burstiness", 0.6)

    if not text:
        return {
            "error": "Missing required field: text",
            "enhanced_text": "",
            "burstiness_before": 0.0,
            "burstiness_after": 0.0,
            "sentences_modified": 0
        }

    # Validate target burstiness
    if not (0.0 <= target_burstiness <= 1.0):
        return {
            "error": "target_burstiness must be between 0.0 and 1.0",
            "enhanced_text": text,
            "burstiness_before": 0.0,
            "burstiness_after": 0.0,
            "sentences_modified": 0
        }

    try:
        # Initialize burstiness enhancer
        enhancer = BurstinessEnhancer(target_burstiness=target_burstiness)

        # Calculate initial burstiness
        burstiness_before = enhancer.calculate_burstiness(text)

        # Enhance burstiness
        enhanced_text, modifications = enhancer.enhance(text)

        # Calculate final burstiness
        burstiness_after = enhancer.calculate_burstiness(enhanced_text)

        return {
            "enhanced_text": enhanced_text,
            "burstiness_before": round(burstiness_before, 3),
            "burstiness_after": round(burstiness_after, 3),
            "sentences_modified": modifications
        }

    except Exception as e:
        return {
            "error": str(e),
            "enhanced_text": text,
            "burstiness_before": 0.0,
            "burstiness_after": 0.0,
            "sentences_modified": 0
        }


def main():
    """Main CLI entry point."""
    try:
        # Read JSON from stdin
        input_data = json.load(sys.stdin)

        # Process
        output_data = process_burstiness_enhancement(input_data)

        # Write JSON to stdout
        json.dump(output_data, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write('\n')

        # Exit with error code if processing failed
        if "error" in output_data:
            sys.exit(1)

    except json.JSONDecodeError as e:
        error_output = {
            "error": f"Invalid JSON input: {str(e)}",
            "enhanced_text": "",
            "burstiness_before": 0.0,
            "burstiness_after": 0.0,
            "sentences_modified": 0
        }
        json.dump(error_output, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write('\n')
        sys.exit(1)

    except Exception as e:
        error_output = {
            "error": f"Unexpected error: {str(e)}",
            "enhanced_text": "",
            "burstiness_before": 0.0,
            "burstiness_after": 0.0,
            "sentences_modified": 0
        }
        json.dump(error_output, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write('\n')
        sys.exit(1)


if __name__ == "__main__":
    main()
