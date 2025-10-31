#!/usr/bin/env python3
"""
Detector Processor CLI Tool

Stdin/stdout JSON interface for AI detection result processing.

Input JSON:
{
    "text": "Text to analyze...",
    "detection_results": {
        "originality_ai": {"score": 45.2, "confidence": 0.89},
        "gptzero": {"score": 70.1, "confidence": 0.92},
        "zerogpt": {"score": 55.3, "confidence": 0.85}
    },
    "generate_heatmap": false
}

Output JSON:
{
    "weighted_score": 56.8,
    "individual_scores": {...},
    "risk_level": "medium",
    "heatmap_path": null,
    "recommendations": [...]
}
"""

import json
import sys
from typing import Dict, Any
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.tools.detector_processor import DetectorProcessor


def process_detection(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process AI detection results.

    Args:
        input_data: Input JSON with text and detection results

    Returns:
        Output JSON with processed results and analysis
    """
    text = input_data.get("text", "")
    detection_results = input_data.get("detection_results", {})
    generate_heatmap = input_data.get("generate_heatmap", False)

    if not text:
        return {
            "error": "Missing required field: text",
            "weighted_score": 0.0,
            "individual_scores": {},
            "risk_level": "unknown",
            "heatmap_path": None,
            "recommendations": []
        }

    if not detection_results:
        return {
            "error": "Missing required field: detection_results",
            "weighted_score": 0.0,
            "individual_scores": {},
            "risk_level": "unknown",
            "heatmap_path": None,
            "recommendations": []
        }

    try:
        # Initialize detector processor
        processor = DetectorProcessor()

        # Process results
        result = processor.process(
            text=text,
            detection_results=detection_results,
            generate_heatmap=generate_heatmap
        )

        return {
            "weighted_score": round(result["weighted_score"], 2),
            "individual_scores": result["individual_scores"],
            "risk_level": result["risk_level"],
            "heatmap_path": result.get("heatmap_path"),
            "recommendations": result.get("recommendations", [])
        }

    except Exception as e:
        return {
            "error": str(e),
            "weighted_score": 0.0,
            "individual_scores": {},
            "risk_level": "unknown",
            "heatmap_path": None,
            "recommendations": []
        }


def main():
    """Main CLI entry point."""
    try:
        # Read JSON from stdin
        input_data = json.load(sys.stdin)

        # Process
        output_data = process_detection(input_data)

        # Write JSON to stdout
        json.dump(output_data, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write('\n')

        # Exit with error code if processing failed
        if "error" in output_data:
            sys.exit(1)

    except json.JSONDecodeError as e:
        error_output = {
            "error": f"Invalid JSON input: {str(e)}",
            "weighted_score": 0.0,
            "individual_scores": {},
            "risk_level": "unknown",
            "heatmap_path": None,
            "recommendations": []
        }
        json.dump(error_output, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write('\n')
        sys.exit(1)

    except Exception as e:
        error_output = {
            "error": f"Unexpected error: {str(e)}",
            "weighted_score": 0.0,
            "individual_scores": {},
            "risk_level": "unknown",
            "heatmap_path": None,
            "recommendations": []
        }
        json.dump(error_output, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write('\n')
        sys.exit(1)


if __name__ == "__main__":
    main()
