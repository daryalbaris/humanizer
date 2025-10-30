#!/usr/bin/env python3
"""
Imperfection Injection Tool

Injects controlled human-like imperfections (mild disfluencies, hesitations, filler words)
into academic text to reduce AI detection scores. Section-aware and carefully calibrated
to maintain academic quality while adding subtle human tells.

Input JSON:
{
    "text": "The text to inject imperfections...",
    "section_type": "introduction|methods|results|discussion|conclusion",
    "intensity": "minimal|light|moderate"
}

Output JSON:
{
    "status": "success|error",
    "data": {
        "text_with_imperfections": "Text with controlled imperfections...",
        "imperfections_added": [
            {"type": "hesitation", "insertion": "somewhat", "position": 245},
            {"type": "filler", "insertion": "in fact", "position": 512}
        ],
        "statistics": {
            "total_injections": 8,
            "hesitations": 3,
            "fillers": 2,
            "minor_errors": 1,
            "structural_variations": 2
        }
    },
    "metadata": {...}
}

Author: AI Humanizer System
Version: 1.0
Sprint: Sprint 4 (STORY-004)
"""

import sys
import json
import re
import time
import random
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import HumanizerLogger

# Initialize logger (file output only, no console for clean JSON)
logger = HumanizerLogger(
    name="imperfection_injector",
    log_file="logs/imperfection_injector.log",
    console_output=False
)


class ImperfectionInjector:
    """
    Human-like Imperfection Injection Engine

    Adds subtle imperfections that humans naturally produce:
    - Hesitation markers ("somewhat", "rather", "quite")
    - Academic fillers ("indeed", "in fact", "of course")
    - Minor punctuation variations
    - Subtle structural imperfections (within academic norms)

    Section-aware: Different imperfection types for different sections
    """

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize imperfection patterns

        Args:
            seed: Random seed for reproducibility (testing)
        """
        if seed is not None:
            random.seed(seed)

        self.start_time = time.time()

        # Hesitation markers (academic-appropriate)
        self.hesitations = {
            "introduction": ["somewhat", "rather", "quite", "fairly", "relatively"],
            "methods": ["approximately", "roughly", "about", "nearly"],
            "results": ["approximately", "roughly", "about"],  # Keep minimal in results
            "discussion": ["somewhat", "rather", "quite", "fairly", "relatively", "to some extent"],
            "conclusion": ["somewhat", "rather", "generally"]
        }

        # Academic filler words (humans use these for emphasis)
        self.fillers = {
            "introduction": ["indeed", "in fact", "notably", "importantly"],
            "methods": ["specifically", "particularly", "in particular"],
            "results": ["notably", "interestingly"],  # Minimal in results
            "discussion": ["indeed", "in fact", "notably", "importantly", "significantly"],
            "conclusion": ["indeed", "overall", "ultimately"]
        }

        # Punctuation variations (human inconsistency)
        self.punctuation_variations = {
            "oxford_comma": 0.7,  # 70% chance to use Oxford comma (humans are inconsistent)
            "em_dash_vs_parentheses": 0.5,  # 50-50 split between em dash and parentheses
            "colon_vs_semicolon": 0.6  # Prefer colon but not always
        }

        # Structural imperfections (mild sentence structure variations)
        self.structure_imperfections = [
            "start_with_and",      # Start sentence with "And" occasionally
            "end_with_preposition", # End with preposition (humans do this)
            "split_infinitive",    # Split infinitives (natural in English)
            "minor_passive"        # Occasional passive voice in active sections
        ]

        logger.info("ImperfectionInjector initialized", extra={
            "hesitation_categories": len(self.hesitations),
            "filler_categories": len(self.fillers),
            "seed": seed
        })

    def inject_imperfections(
        self,
        text: str,
        section_type: str = "general",
        intensity: str = "light"
    ) -> Dict[str, Any]:
        """
        Inject controlled imperfections into text

        Args:
            text: Input text
            section_type: Section type for context-aware injection
            intensity: Imperfection intensity
                - minimal: 1-2 imperfections per 1000 words (very subtle)
                - light: 3-5 imperfections per 1000 words (default)
                - moderate: 6-10 imperfections per 1000 words (noticeable but acceptable)

        Returns:
            Dictionary with imperfection-injected text and statistics
        """
        logger.info(f"Starting imperfection injection", extra={
            "text_length": len(text),
            "section_type": section_type,
            "intensity": intensity
        })

        # Calculate injection rate based on intensity
        word_count = len(re.findall(r'\b\w+\b', text))
        injection_rate = {
            "minimal": 0.0015,   # 1.5 per 1000 words
            "light": 0.004,      # 4 per 1000 words
            "moderate": 0.008    # 8 per 1000 words
        }.get(intensity, 0.004)

        target_injections = int(word_count * injection_rate)

        # Ensure at least 1 injection, max 20
        target_injections = max(1, min(20, target_injections))

        injected_text = text
        injections = []
        stats = {
            "total_injections": 0,
            "hesitations": 0,
            "fillers": 0,
            "punctuation_variations": 0,
            "structural_variations": 0
        }

        # Distribute injections across types
        injection_types = ["hesitation", "filler", "punctuation", "structure"]
        type_counts = {t: target_injections // len(injection_types) for t in injection_types}

        # Add remainder to random types
        remainder = target_injections % len(injection_types)
        for _ in range(remainder):
            random.choice(injection_types)
            type_counts[random.choice(injection_types)] += 1

        # 1. Inject hesitations
        for _ in range(type_counts["hesitation"]):
            injected_text, injection = self._inject_hesitation(
                injected_text, section_type
            )
            if injection:
                injections.append(injection)
                stats["hesitations"] += 1

        # 2. Inject fillers
        for _ in range(type_counts["filler"]):
            injected_text, injection = self._inject_filler(
                injected_text, section_type
            )
            if injection:
                injections.append(injection)
                stats["fillers"] += 1

        # 3. Vary punctuation
        for _ in range(type_counts["punctuation"]):
            injected_text, injection = self._vary_punctuation(injected_text)
            if injection:
                injections.append(injection)
                stats["punctuation_variations"] += 1

        # 4. Add structural variations
        for _ in range(type_counts["structure"]):
            injected_text, injection = self._add_structural_variation(
                injected_text, section_type
            )
            if injection:
                injections.append(injection)
                stats["structural_variations"] += 1

        stats["total_injections"] = len(injections)

        logger.info(f"Imperfection injection complete", extra={
            "total_injections": stats["total_injections"],
            "hesitations": stats["hesitations"],
            "fillers": stats["fillers"],
            "punctuation_variations": stats["punctuation_variations"],
            "structural_variations": stats["structural_variations"]
        })

        return {
            "text_with_imperfections": injected_text,
            "imperfections_added": injections,
            "statistics": stats
        }

    def _inject_hesitation(
        self,
        text: str,
        section_type: str
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        """Inject hesitation marker before an adjective or adverb"""
        # Get section-appropriate hesitations
        hesitations = self.hesitations.get(section_type, self.hesitations["introduction"])

        # Find adjectives/adverbs to modify (pattern: space + adj/adv + space)
        # Simple heuristic: words ending in -ly, -ive, -ous, -al, -ant, -ent
        pattern = r'\b((?:\w+ly|\w+ive|\w+ous|\w+al|\w+ant|\w+ent))\b'
        matches = list(re.finditer(pattern, text, re.IGNORECASE))

        if not matches:
            return text, None

        # Pick random match
        match = random.choice(matches)
        hesitation = random.choice(hesitations)

        # Insert hesitation before adjective
        position = match.start()
        modified_text = text[:position] + hesitation + " " + text[position:]

        return modified_text, {
            "type": "hesitation",
            "insertion": hesitation,
            "before_word": match.group(0),
            "position": position
        }

    def _inject_filler(
        self,
        text: str,
        section_type: str
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        """Inject academic filler word at sentence start or mid-sentence"""
        # Get section-appropriate fillers
        fillers = self.fillers.get(section_type, self.fillers["introduction"])

        # Find sentence boundaries (after period/question mark/exclamation)
        sentences = re.split(r'(?<=[.!?])\s+', text)

        if len(sentences) < 2:
            return text, None

        # Pick random sentence (not first)
        sentence_idx = random.randint(1, len(sentences) - 1)
        filler = random.choice(fillers)

        # Insert filler at start of sentence
        sentences[sentence_idx] = filler.capitalize() + ", " + sentences[sentence_idx]

        modified_text = ' '.join(sentences)

        return modified_text, {
            "type": "filler",
            "insertion": filler,
            "at_sentence": sentence_idx,
            "position": -1  # Sentence-level modification
        }

    def _vary_punctuation(
        self,
        text: str
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        """Add punctuation variation (Oxford comma, em dash vs parentheses)"""
        # Oxford comma variation: Find lists without Oxford comma
        pattern = r'(\w+),\s+(\w+)\s+and\s+(\w+)'
        matches = list(re.finditer(pattern, text))

        if matches and random.random() < self.punctuation_variations["oxford_comma"]:
            match = random.choice(matches)
            # Add Oxford comma
            original = match.group(0)
            modified = f"{match.group(1)}, {match.group(2)}, and {match.group(3)}"

            modified_text = text[:match.start()] + modified + text[match.end():]

            return modified_text, {
                "type": "punctuation_variation",
                "subtype": "oxford_comma",
                "original": original,
                "modified": modified,
                "position": match.start()
            }

        # Em dash vs parentheses: Find parenthetical expressions
        pattern = r'\(([^)]+)\)'
        matches = list(re.finditer(pattern, text))

        if matches and random.random() < self.punctuation_variations["em_dash_vs_parentheses"]:
            match = random.choice(matches)
            # Replace parentheses with em dashes
            original = match.group(0)
            modified = f"—{match.group(1)}—"

            modified_text = text[:match.start()] + modified + text[match.end():]

            return modified_text, {
                "type": "punctuation_variation",
                "subtype": "em_dash_for_parentheses",
                "original": original,
                "modified": modified,
                "position": match.start()
            }

        return text, None

    def _add_structural_variation(
        self,
        text: str,
        section_type: str
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        """Add subtle structural variation"""
        variation_type = random.choice(self.structure_imperfections)

        if variation_type == "start_with_and":
            # Start a sentence with "And" (humans do this for emphasis)
            sentences = re.split(r'(?<=[.!?])\s+', text)

            if len(sentences) < 3:
                return text, None

            # Pick a middle sentence (not first or last)
            sentence_idx = random.randint(1, len(sentences) - 2)

            # Only if it doesn't already start with a conjunction
            if not re.match(r'^(And|But|Or|Yet|So)\b', sentences[sentence_idx], re.IGNORECASE):
                sentences[sentence_idx] = "And " + sentences[sentence_idx][0].lower() + sentences[sentence_idx][1:]

                modified_text = ' '.join(sentences)

                return modified_text, {
                    "type": "structural_variation",
                    "subtype": "start_with_and",
                    "at_sentence": sentence_idx,
                    "position": -1
                }

        # If no variation applied, return original
        return text, None


def process_input(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main processing function for CLI interface

    Args:
        input_data: JSON input with text, section_type, intensity

    Returns:
        JSON output with imperfection-injected text and statistics
    """
    start_time = time.time()

    try:
        # Validate input
        if "text" not in input_data:
            return {
                "status": "error",
                "error": {
                    "code": "MISSING_FIELD",
                    "message": "Required field 'text' not found in input"
                }
            }

        text = input_data["text"]
        section_type = input_data.get("section_type", "general")
        intensity = input_data.get("intensity", "light")

        # Validate intensity
        if intensity not in ["minimal", "light", "moderate"]:
            return {
                "status": "error",
                "error": {
                    "code": "INVALID_INTENSITY",
                    "message": f"Invalid intensity '{intensity}'. Must be: minimal, light, or moderate"
                }
            }

        # Initialize injector
        seed = input_data.get("seed")  # Optional for testing reproducibility
        injector = ImperfectionInjector(seed=seed)

        # Process
        result = injector.inject_imperfections(text, section_type, intensity)

        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)

        # Return success response
        return {
            "status": "success",
            "data": result,
            "metadata": {
                "processing_time_ms": processing_time_ms,
                "tool": "imperfection_injector",
                "version": "1.0",
                "input_length": len(text),
                "output_length": len(result["text_with_imperfections"]),
                "section_type": section_type,
                "intensity": intensity,
                "seed": seed
            }
        }

    except Exception as e:
        logger.error(f"Imperfection injection failed", extra={
            "error": str(e),
            "error_type": type(e).__name__
        })

        return {
            "status": "error",
            "error": {
                "code": "PROCESSING_ERROR",
                "message": str(e),
                "type": type(e).__name__
            }
        }


def main():
    """Main entry point for CLI usage"""
    try:
        # Read JSON from stdin
        input_data = json.load(sys.stdin)

        # Process
        output_data = process_input(input_data)

        # Write JSON to stdout
        json.dump(output_data, sys.stdout, indent=2, ensure_ascii=False)

        # Exit with appropriate code
        sys.exit(0 if output_data["status"] == "success" else 1)

    except json.JSONDecodeError as e:
        error_output = {
            "status": "error",
            "error": {
                "code": "INVALID_JSON",
                "message": f"Invalid JSON input: {str(e)}"
            }
        }
        json.dump(error_output, sys.stdout, indent=2)
        sys.exit(1)

    except Exception as e:
        error_output = {
            "status": "error",
            "error": {
                "code": "UNEXPECTED_ERROR",
                "message": str(e),
                "type": type(e).__name__
            }
        }
        json.dump(error_output, sys.stdout, indent=2)
        sys.exit(1)


if __name__ == "__main__":
    main()
