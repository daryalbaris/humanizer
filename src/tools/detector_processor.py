"""
Detector Processor Tool - AI Detection Heatmap Generation

This tool processes AI detection results and generates a heatmap identifying
high-risk sections that need additional humanization. It acts as a proxy for
the Originality.ai API, using perplexity scores and other metrics.

Input (JSON stdin):
{
    "text": "The full text...",
    "perplexity_scores": {
        "overall": 45.2,
        "sections": [
            {"name": "Introduction", "perplexity": 42.5, "start": 0, "end": 500},
            {"name": "Methods", "perplexity": 48.1, "start": 500, "end": 1500}
        ]
    },
    "detection_threshold": 30.0,  # Perplexity below this = AI-detected
    "originality_score": 0.25  # Optional: Actual Originality.ai score if available
}

Output (JSON stdout):
{
    "status": "success",
    "data": {
        "overall_detection_score": 0.15,  # Estimated % AI-detected (0.0-1.0)
        "detection_level": "low",  # low, medium, high
        "sections_at_risk": [
            {
                "name": "Introduction",
                "start": 0,
                "end": 500,
                "detection_score": 0.25,
                "risk_level": "high",
                "perplexity": 42.5,
                "recommendation": "Increase paraphrasing aggression to Level 3"
            }
        ],
        "heatmap": [
            {"position": 0, "score": 0.25, "color": "#FF4444"},
            {"position": 100, "score": 0.18, "color": "#FFAA44"},
            {"position": 200, "score": 0.12, "color": "#AAFF44"}
        ],
        "recommended_action": "Focus on Introduction section (25% AI-detected)"
    },
    "metadata": {
        "processing_time_ms": 234,
        "tool": "detector_processor",
        "version": "1.0",
        "detection_method": "perplexity_proxy"
    }
}

Author: BMAD Development Team
Version: 1.0
Created: 2025-10-30
"""

import sys
import json
import time
from typing import Dict, List, Tuple, Optional
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')


class DetectorProcessor:
    """
    Processes AI detection results and generates actionable heatmaps.

    Uses perplexity scores as a proxy for AI detection:
    - Lower perplexity → More likely AI-generated
    - Higher perplexity → More likely human-written

    Detection mapping (conservative approach):
    - Perplexity < 20: ~80% AI-detected (very high risk)
    - Perplexity 20-30: ~40-80% AI-detected (high risk)
    - Perplexity 30-45: ~15-40% AI-detected (medium risk)
    - Perplexity 45-60: ~5-15% AI-detected (low risk)
    - Perplexity > 60: <5% AI-detected (very low risk)
    """

    def __init__(self):
        """Initialize the detector processor."""
        # Define perplexity-to-detection mapping
        self.detection_mapping = [
            (0, 20, 0.80, 'very_high'),
            (20, 30, 0.60, 'high'),
            (30, 45, 0.25, 'medium'),
            (45, 60, 0.10, 'low'),
            (60, float('inf'), 0.03, 'very_low')
        ]

    def perplexity_to_detection_score(self, perplexity: float) -> Tuple[float, str]:
        """
        Convert perplexity score to AI detection score.

        Args:
            perplexity: Perplexity value

        Returns:
            Tuple of (detection_score, risk_level)
        """
        for min_ppl, max_ppl, detection_score, risk_level in self.detection_mapping:
            if min_ppl <= perplexity < max_ppl:
                # Linear interpolation within the range
                if max_ppl != float('inf'):
                    range_size = max_ppl - min_ppl
                    position = (perplexity - min_ppl) / range_size
                    # Lower perplexity within range = higher detection
                    adjusted_score = detection_score * (1 - position * 0.3)
                else:
                    adjusted_score = detection_score

                return round(adjusted_score, 3), risk_level

        # Default for very low perplexity
        return 0.95, 'very_high'

    def analyze_sections(
        self,
        sections: List[Dict[str, any]],
        detection_threshold: float = 0.20
    ) -> List[Dict[str, any]]:
        """
        Analyze sections for AI detection risk.

        Args:
            sections: List of section dictionaries with perplexity scores
            detection_threshold: Detection score above which section is at risk

        Returns:
            List of sections with detection analysis
        """
        sections_at_risk = []

        for section in sections:
            perplexity = section.get('perplexity', 50.0)
            detection_score, risk_level = self.perplexity_to_detection_score(perplexity)

            # Determine recommendation
            if risk_level in ['very_high', 'high']:
                recommendation = "Increase paraphrasing aggression to Level 4-5 (Intensive)"
            elif risk_level == 'medium':
                recommendation = "Increase paraphrasing aggression to Level 3 (Aggressive)"
            elif risk_level == 'low':
                recommendation = "Current paraphrasing level adequate"
            else:
                recommendation = "Section passes detection threshold"

            section_analysis = {
                'name': section.get('name', 'Unnamed'),
                'start': section.get('start', 0),
                'end': section.get('end', 0),
                'detection_score': detection_score,
                'risk_level': risk_level,
                'perplexity': perplexity,
                'recommendation': recommendation
            }

            # Add to at-risk list if above threshold
            if detection_score >= detection_threshold:
                sections_at_risk.append(section_analysis)

        return sections_at_risk

    def generate_heatmap(
        self,
        text: str,
        sections: List[Dict[str, any]],
        resolution: int = 20
    ) -> List[Dict[str, any]]:
        """
        Generate a heatmap of AI detection scores across the text.

        Args:
            text: Full text
            sections: List of sections with detection scores
            resolution: Number of heatmap points (higher = more granular)

        Returns:
            List of heatmap points with positions, scores, and colors
        """
        text_length = len(text)
        chunk_size = text_length // resolution

        heatmap = []

        for i in range(resolution):
            position = i * chunk_size
            end_position = min((i + 1) * chunk_size, text_length)

            # Find which section this position belongs to
            section_score = 0.05  # Default low score
            for section in sections:
                section_start = section.get('start', 0)
                section_end = section.get('end', 0)
                if section_start <= position < section_end:
                    perplexity = section.get('perplexity', 50.0)
                    section_score, _ = self.perplexity_to_detection_score(perplexity)
                    break

            # Determine color based on score
            color = self._score_to_color(section_score)

            heatmap.append({
                'position': position,
                'score': section_score,
                'color': color
            })

        return heatmap

    def _score_to_color(self, score: float) -> str:
        """
        Convert detection score to color (hex).

        Args:
            score: Detection score (0.0-1.0)

        Returns:
            Hex color code
        """
        if score >= 0.60:
            return '#FF0000'  # Red (very high risk)
        elif score >= 0.40:
            return '#FF4444'  # Light red (high risk)
        elif score >= 0.20:
            return '#FFAA44'  # Orange (medium risk)
        elif score >= 0.10:
            return '#AAFF44'  # Yellow-green (low risk)
        else:
            return '#44FF44'  # Green (very low risk)

    def determine_overall_level(self, overall_score: float) -> str:
        """
        Determine overall detection level.

        Args:
            overall_score: Overall detection score

        Returns:
            Detection level string
        """
        if overall_score >= 0.40:
            return 'high'
        elif overall_score >= 0.20:
            return 'medium'
        else:
            return 'low'

    def generate_recommendation(
        self,
        overall_score: float,
        sections_at_risk: List[Dict[str, any]]
    ) -> str:
        """
        Generate actionable recommendation based on detection results.

        Args:
            overall_score: Overall detection score
            sections_at_risk: List of high-risk sections

        Returns:
            Recommendation string
        """
        if overall_score < 0.15:
            return "Text passes detection threshold (<15%). No action needed."

        if not sections_at_risk:
            return f"Overall detection: {overall_score*100:.1f}%. Consider full-text paraphrasing at higher aggression."

        # Focus on highest risk section
        highest_risk = max(sections_at_risk, key=lambda x: x['detection_score'])
        section_name = highest_risk['name']
        section_score = highest_risk['detection_score'] * 100

        return f"Focus on {section_name} section ({section_score:.1f}% AI-detected). {highest_risk['recommendation']}"


def process_input(input_data: Dict[str, any]) -> Dict[str, any]:
    """
    Process input and generate AI detection heatmap.

    Args:
        input_data: Input dictionary from JSON stdin

    Returns:
        Output dictionary for JSON stdout
    """
    start_time = time.time()

    try:
        # Extract parameters
        text = input_data.get('text', '')
        perplexity_scores = input_data.get('perplexity_scores', {})
        detection_threshold = input_data.get('detection_threshold', 0.20)
        originality_score = input_data.get('originality_score')  # Optional actual score

        # Validate inputs
        if not text.strip():
            return {
                'status': 'error',
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Text cannot be empty'
                }
            }

        # Initialize processor
        processor = DetectorProcessor()

        # Extract overall perplexity
        overall_perplexity = perplexity_scores.get('overall', 50.0)
        sections = perplexity_scores.get('sections', [])

        # Calculate overall detection score
        if originality_score is not None:
            # Use actual Originality.ai score if provided
            overall_detection_score = originality_score
            detection_method = 'originality_ai'
        else:
            # Use perplexity-based proxy
            overall_detection_score, _ = processor.perplexity_to_detection_score(overall_perplexity)
            detection_method = 'perplexity_proxy'

        # Determine detection level
        detection_level = processor.determine_overall_level(overall_detection_score)

        # Analyze sections
        sections_at_risk = processor.analyze_sections(sections, detection_threshold)

        # Generate heatmap
        heatmap = processor.generate_heatmap(text, sections, resolution=20)

        # Generate recommendation
        recommendation = processor.generate_recommendation(overall_detection_score, sections_at_risk)

        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)

        # Build response
        return {
            'status': 'success',
            'data': {
                'overall_detection_score': round(overall_detection_score, 3),
                'detection_level': detection_level,
                'sections_at_risk': sections_at_risk,
                'heatmap': heatmap,
                'recommended_action': recommendation
            },
            'metadata': {
                'processing_time_ms': processing_time,
                'tool': 'detector_processor',
                'version': '1.0',
                'detection_method': detection_method
            }
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': {
                'code': 'PROCESSING_ERROR',
                'message': str(e)
            }
        }


def main():
    """
    Main function for CLI interface.
    Reads JSON from stdin, processes, and writes JSON to stdout.
    """
    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)

        # Process input
        result = process_input(input_data)

        # Write output to stdout
        print(json.dumps(result, indent=2))
        sys.exit(0)

    except json.JSONDecodeError as e:
        error_response = {
            'status': 'error',
            'error': {
                'code': 'INVALID_JSON',
                'message': f'Invalid JSON input: {str(e)}'
            }
        }
        print(json.dumps(error_response, indent=2))
        sys.exit(1)

    except Exception as e:
        error_response = {
            'status': 'error',
            'error': {
                'code': 'UNEXPECTED_ERROR',
                'message': str(e)
            }
        }
        print(json.dumps(error_response, indent=2))
        sys.exit(1)


if __name__ == '__main__':
    main()
