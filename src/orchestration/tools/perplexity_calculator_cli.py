#!/usr/bin/env python3
"""
Perplexity Calculator CLI Tool

Stdin/stdout JSON interface for perplexity calculation.

Input JSON:
{
    "text": "Text to analyze...",
    "model": "gpt2"  // optional, default: gpt2
}

Output JSON:
{
    "perplexity": 45.3,
    "sentence_perplexities": [32.1, 56.7, 41.2, ...],
    "avg_sentence_perplexity": 43.3,
    "model": "gpt2"
}
"""

import json
import sys
from typing import Dict, Any
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.tools.perplexity_calculator import PerplexityCalculator


def process_perplexity(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process perplexity calculation request.

    Args:
        input_data: Input JSON with text and optional model

    Returns:
        Output JSON with perplexity scores
    """
    text = input_data.get("text", "")
    model = input_data.get("model", "gpt2")

    if not text:
        return {
            "error": "Missing required field: text",
            "perplexity": 0.0,
            "sentence_perplexities": [],
            "avg_sentence_perplexity": 0.0,
            "model": model
        }

    try:
        # Initialize perplexity calculator
        calculator = PerplexityCalculator(model=model)

        # Calculate perplexity
        result = calculator.calculate(text)

        return {
            "perplexity": round(result["perplexity"], 2),
            "sentence_perplexities": [round(p, 2) for p in result["sentence_perplexities"]],
            "avg_sentence_perplexity": round(result["avg_sentence_perplexity"], 2),
            "model": model
        }

    except Exception as e:
        return {
            "error": str(e),
            "perplexity": 0.0,
            "sentence_perplexities": [],
            "avg_sentence_perplexity": 0.0,
            "model": model
        }


def main():
    """Main CLI entry point."""
    try:
        # Read JSON from stdin
        input_data = json.load(sys.stdin)

        # Process
        output_data = process_perplexity(input_data)

        # Write JSON to stdout
        json.dump(output_data, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write('\n')

        # Exit with error code if processing failed
        if "error" in output_data:
            sys.exit(1)

    except json.JSONDecodeError as e:
        error_output = {
            "error": f"Invalid JSON input: {str(e)}",
            "perplexity": 0.0,
            "sentence_perplexities": [],
            "avg_sentence_perplexity": 0.0,
            "model": "gpt2"
        }
        json.dump(error_output, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write('\n')
        sys.exit(1)

    except Exception as e:
        error_output = {
            "error": f"Unexpected error: {str(e)}",
            "perplexity": 0.0,
            "sentence_perplexities": [],
            "avg_sentence_perplexity": 0.0,
            "model": "gpt2"
        }
        json.dump(error_output, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write('\n')
        sys.exit(1)


if __name__ == "__main__":
    main()
