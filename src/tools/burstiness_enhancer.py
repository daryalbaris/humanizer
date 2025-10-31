#!/usr/bin/env python3
"""
Burstiness Enhancement Tool

Enhances sentence-level variability across 6 dimensions to mimic human writing patterns.
AI-generated text tends to have uniform sentence structure; human writing is "bursty"
(varying between short punchy sentences and longer complex ones).

Input JSON:
{
    "text": "The text to enhance...",
    "section_type": "introduction|methods|results|discussion|conclusion",
    "dimensions": [1, 2, 3],  # Which dimensions to apply (1-6)
    "intensity": "subtle|moderate|strong"
}

Output JSON:
{
    "status": "success|error",
    "data": {
        "enhanced_text": "Text with enhanced burstiness...",
        "enhancements_applied": [
            {"dimension": 1, "type": "sentence_split", "description": "Split long sentence"},
            {"dimension": 2, "type": "structure_variation", "description": "Complex → Simple"}
        ],
        "statistics": {
            "original_sentence_count": 20,
            "modified_sentence_count": 24,
            "dimension_1_changes": 8,
            "dimension_2_changes": 6,
            "dimension_3_changes": 5
        },
        "burstiness_metrics": {
            "original_variance": 12.5,
            "enhanced_variance": 25.8,
            "improvement": "106.4%"
        }
    },
    "metadata": {...}
}

Dimensions:
1. Sentence Length Variation (by section)
2. Sentence Structure Variation (simple, compound, complex)
3. Beginning Word Diversity (avoid repetitive starters)
4. Grammatical Variety (declarative, interrogative, imperative) [Sprint 5]
5. Clause Variation (independent vs dependent clauses) [Sprint 5]
6. Voice Mixing (active/passive by section) [Sprint 5]

Author: AI Humanizer System
Version: 1.0 (Dimensions 1-3)
Sprint: Sprint 4 (STORY-004)
"""

import sys
import json
import re
import time
import random
import statistics
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import get_logger

# Initialize logger (file output only, no console for clean JSON)
logger = get_logger(__name__)


class BurstinessEnhancer:
    """
    Sentence-Level Burstiness Enhancement Engine

    Implements 6 dimensions of human-like variability:
    - Dimension 1: Sentence length variation by section
    - Dimension 2: Sentence structure variation (simple/compound/complex)
    - Dimension 3: Beginning word diversity
    - Dimensions 4-6: Grammatical variety, clause variation, voice mixing (Sprint 5)
    """

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize burstiness patterns

        Args:
            seed: Random seed for reproducibility (testing)
        """
        if seed is not None:
            random.seed(seed)

        self.start_time = time.time()

        # Dimension 1: Target sentence length ranges by section (words per sentence)
        self.sentence_length_targets = {
            "introduction": {"min": 12, "max": 30, "mean": 20, "variance_target": 40},
            "methods": {"min": 15, "max": 28, "mean": 22, "variance_target": 25},
            "results": {"min": 14, "max": 25, "mean": 18, "variance_target": 20},
            "discussion": {"min": 12, "max": 35, "mean": 22, "variance_target": 50},
            "conclusion": {"min": 14, "max": 32, "mean": 20, "variance_target": 45},
            "general": {"min": 12, "max": 30, "mean": 20, "variance_target": 40}
        }

        # Dimension 2: Sentence structure templates
        self.structure_templates = {
            "simple": [
                # Subject-Verb-Object
                "SVO",
                # Subject-Verb-Complement
                "SVC"
            ],
            "compound": [
                # Two independent clauses with coordinator
                "S1V1, and S2V2",
                "S1V1, but S2V2",
                "S1V1; S2V2"
            ],
            "complex": [
                # Dependent clause first
                "Although..., S1V1",
                "Because..., S1V1",
                "When..., S1V1",
                # Dependent clause last
                "S1V1, which...",
                "S1V1, because..."
            ]
        }

        # Dimension 3: Common sentence starters (to avoid repetition)
        self.sentence_starters = {
            "overused": ["The", "This", "These", "It", "There"],
            "alternatives": [
                "In this study", "Our results", "The present work",
                "Notably", "Importantly", "Furthermore", "Moreover",
                "By contrast", "In contrast", "However",
                "First", "Second", "Finally", "Subsequently"
            ]
        }

        logger.info("BurstinessEnhancer initialized (Dimensions 1-3)", data={
            "dimensions_available": [1, 2, 3],
            "section_targets": len(self.sentence_length_targets),
            "seed": seed
        })

    def enhance_burstiness(
        self,
        text: str,
        section_type: str = "general",
        dimensions: List[int] = [1, 2, 3],
        intensity: str = "moderate"
    ) -> Dict[str, Any]:
        """
        Enhance text burstiness across specified dimensions

        Args:
            text: Input text
            section_type: Section type for context-aware enhancement
            dimensions: Which dimensions to apply (1-6)
            intensity: Enhancement intensity
                - subtle: Minimal changes (8% of sentences)
                - moderate: Balanced changes (30% of sentences) [default]
                - strong: Aggressive changes (45% of sentences)

        Returns:
            Dictionary with enhanced text and statistics
        """
        logger.info(f"Starting burstiness enhancement", data={
            "text_length": len(text),
            "section_type": section_type,
            "dimensions": dimensions,
            "intensity": intensity
        })

        # Split into sentences
        sentences = self._split_sentences(text)

        if len(sentences) < 3:
            logger.warning("Text too short for meaningful burstiness enhancement")
            return {
                "enhanced_text": text,
                "enhancements_applied": [],
                "statistics": {
                    "original_sentence_count": len(sentences),
                    "modified_sentence_count": len(sentences),
                    "dimension_1_changes": 0,
                    "dimension_2_changes": 0,
                    "dimension_3_changes": 0
                },
                "burstiness_metrics": {
                    "original_variance": 0,
                    "enhanced_variance": 0,
                    "improvement": "0%"
                }
            }

        # Calculate original burstiness
        original_lengths = [len(re.findall(r'\b\w+\b', s)) for s in sentences]
        original_variance = statistics.variance(original_lengths) if len(original_lengths) > 1 else 0

        enhanced_sentences = sentences.copy()
        enhancements = []
        stats = {
            "original_sentence_count": len(sentences),
            "dimension_1_changes": 0,
            "dimension_2_changes": 0,
            "dimension_3_changes": 0
        }

        # Determine modification rate based on intensity
        modification_rate = {
            "subtle": 0.08,      # 8% of sentences
            "moderate": 0.30,    # 30% of sentences
            "strong": 0.45       # 45% of sentences
        }.get(intensity, 0.30)

        # Apply each dimension
        if 1 in dimensions:
            enhanced_sentences, dim1_enhancements = self._apply_dimension_1(
                enhanced_sentences, section_type, modification_rate
            )
            enhancements.extend(dim1_enhancements)
            stats["dimension_1_changes"] = len(dim1_enhancements)

        if 2 in dimensions:
            enhanced_sentences, dim2_enhancements = self._apply_dimension_2(
                enhanced_sentences, section_type, modification_rate
            )
            enhancements.extend(dim2_enhancements)
            stats["dimension_2_changes"] = len(dim2_enhancements)

        if 3 in dimensions:
            enhanced_sentences, dim3_enhancements = self._apply_dimension_3(
                enhanced_sentences, modification_rate
            )
            enhancements.extend(dim3_enhancements)
            stats["dimension_3_changes"] = len(dim3_enhancements)

        # Reconstruct text
        enhanced_text = ' '.join(enhanced_sentences)

        # Calculate enhanced burstiness
        enhanced_lengths = [len(re.findall(r'\b\w+\b', s)) for s in enhanced_sentences]
        enhanced_variance = statistics.variance(enhanced_lengths) if len(enhanced_lengths) > 1 else 0

        improvement_pct = ((enhanced_variance - original_variance) / original_variance * 100) if original_variance > 0 else 0

        stats["modified_sentence_count"] = len(enhanced_sentences)

        logger.info(f"Burstiness enhancement complete", data={
            "total_enhancements": len(enhancements),
            "dimension_1": stats["dimension_1_changes"],
            "dimension_2": stats["dimension_2_changes"],
            "dimension_3": stats["dimension_3_changes"],
            "variance_improvement": f"{improvement_pct:.1f}%"
        })

        return {
            "enhanced_text": enhanced_text,
            "enhancements_applied": enhancements,
            "statistics": stats,
            "burstiness_metrics": {
                "original_variance": round(original_variance, 2),
                "enhanced_variance": round(enhanced_variance, 2),
                "improvement": f"{improvement_pct:.1f}%"
            }
        }

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences (robust splitting)"""
        # Split on sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text)

        # Remove empty sentences
        sentences = [s.strip() for s in sentences if s.strip()]

        return sentences

    def _apply_dimension_1(
        self,
        sentences: List[str],
        section_type: str,
        modification_rate: float
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Dimension 1: Sentence Length Variation

        Strategy:
        - Analyze current sentence lengths
        - Identify sentences that are too uniform
        - Split long sentences or merge short sentences
        - Target section-specific length distribution
        """
        enhancements = []
        modified = sentences.copy()

        targets = self.sentence_length_targets.get(section_type, self.sentence_length_targets["general"])

        # Analyze sentence lengths
        lengths = [len(re.findall(r'\b\w+\b', s)) for s in modified]

        # Find sentences outside target range
        num_modifications = int(len(sentences) * modification_rate)

        for i in range(min(num_modifications, len(modified))):
            sentence_idx = random.randint(0, len(modified) - 1)
            length = lengths[sentence_idx]

            # Too long → split
            if length > targets["max"]:
                split_sentences = self._split_long_sentence(modified[sentence_idx])
                if split_sentences and len(split_sentences) > 1:
                    # Replace with split sentences
                    modified[sentence_idx:sentence_idx+1] = split_sentences
                    lengths[sentence_idx:sentence_idx+1] = [len(re.findall(r'\b\w+\b', s)) for s in split_sentences]

                    enhancements.append({
                        "dimension": 1,
                        "type": "sentence_split",
                        "description": f"Split sentence (was {length} words)",
                        "sentence_index": sentence_idx
                    })

            # Too short → potentially merge (if next sentence is also short)
            elif length < targets["min"] and sentence_idx < len(modified) - 1:
                next_length = lengths[sentence_idx + 1]
                if next_length < targets["min"] and (length + next_length) < targets["max"]:
                    # Merge sentences
                    merged = modified[sentence_idx].rstrip('.!?') + ', ' + modified[sentence_idx + 1][0].lower() + modified[sentence_idx + 1][1:]
                    modified[sentence_idx] = merged
                    del modified[sentence_idx + 1]
                    del lengths[sentence_idx + 1]
                    lengths[sentence_idx] = len(re.findall(r'\b\w+\b', merged))

                    enhancements.append({
                        "dimension": 1,
                        "type": "sentence_merge",
                        "description": f"Merged two short sentences ({length}+{next_length} words)",
                        "sentence_index": sentence_idx
                    })

        return modified, enhancements

    def _split_long_sentence(self, sentence: str) -> List[str]:
        """Split a long sentence at natural break points"""
        # Look for coordinators (and, but, or)
        coordinator_pattern = r'(.*?),\s+(and|but|or)\s+(.*)'
        match = re.match(coordinator_pattern, sentence, re.IGNORECASE)

        if match:
            # Split at coordinator
            part1 = match.group(1).strip() + '.'
            part2 = match.group(3).strip()
            if not part2.endswith('.'):
                part2 += '.'
            return [part1, part2[0].upper() + part2[1:]]

        # Look for semicolons
        if ';' in sentence:
            parts = sentence.split(';')
            return [p.strip() + '.' for p in parts if p.strip()]

        # No natural split point
        return [sentence]

    def _apply_dimension_2(
        self,
        sentences: List[str],
        section_type: str,
        modification_rate: float
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Dimension 2: Sentence Structure Variation

        Strategy:
        - Classify sentences as simple/compound/complex
        - Ensure variety (not all sentences of same structure)
        - Transform some sentences to different structures
        """
        enhancements = []
        modified = sentences.copy()

        num_modifications = int(len(sentences) * modification_rate)

        for _ in range(num_modifications):
            sentence_idx = random.randint(0, len(modified) - 1)
            sentence = modified[sentence_idx]

            # Classify current structure
            structure = self._classify_sentence_structure(sentence)

            # Transform to different structure
            if structure == "simple":
                # Make it compound (add a second clause)
                transformed = self._make_compound(sentence)
                if transformed:
                    modified[sentence_idx] = transformed
                    enhancements.append({
                        "dimension": 2,
                        "type": "structure_variation",
                        "description": "Simple → Compound",
                        "sentence_index": sentence_idx
                    })

            elif structure == "compound":
                # Split into simple sentences
                split = self._split_long_sentence(sentence)
                if len(split) > 1:
                    modified[sentence_idx:sentence_idx+1] = split
                    enhancements.append({
                        "dimension": 2,
                        "type": "structure_variation",
                        "description": "Compound → Simple (split)",
                        "sentence_index": sentence_idx
                    })

        return modified, enhancements

    def _classify_sentence_structure(self, sentence: str) -> str:
        """Classify sentence as simple, compound, or complex"""
        # Complex: Contains subordinating conjunctions
        complex_markers = ['although', 'because', 'since', 'while', 'if', 'when', 'which', 'that']
        if any(marker in sentence.lower() for marker in complex_markers):
            return "complex"

        # Compound: Contains coordinating conjunctions or semicolons
        if re.search(r',\s+(and|but|or|yet|so)\s+', sentence, re.IGNORECASE) or ';' in sentence:
            return "compound"

        # Default: Simple
        return "simple"

    def _make_compound(self, sentence: str) -> Optional[str]:
        """Transform simple sentence to compound (add second clause)"""
        # Simple heuristic: Add "and this..." or "but this..."
        # (In a real system, this would use NLP to generate meaningful clauses)

        # Remove period
        base = sentence.rstrip('.!?')

        # Add compound clause
        coordinators = ["and this demonstrates", "but this suggests", "and this indicates"]
        addition = random.choice(coordinators) + " the importance of further study"

        return base + ", " + addition + "."

    def _apply_dimension_3(
        self,
        sentences: List[str],
        modification_rate: float
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Dimension 3: Beginning Word Diversity

        Strategy:
        - Identify consecutive sentences starting with same word
        - Replace overused starters ("The", "This", "It")
        - Introduce varied transitions
        """
        enhancements = []
        modified = sentences.copy()

        # Find consecutive same-start sentences
        for i in range(len(modified) - 1):
            start1 = re.match(r'^\w+', modified[i])
            start2 = re.match(r'^\w+', modified[i + 1])

            if start1 and start2:
                word1 = start1.group(0)
                word2 = start2.group(0)

                # If consecutive sentences start with same word
                if word1.lower() == word2.lower():
                    # Check if it's an overused starter
                    if word2 in self.sentence_starters["overused"]:
                        # Replace with alternative
                        alternative = random.choice(self.sentence_starters["alternatives"])

                        # Replace starter in second sentence
                        modified[i + 1] = alternative + ", " + modified[i + 1][len(word2):].lstrip()

                        enhancements.append({
                            "dimension": 3,
                            "type": "beginning_word_diversity",
                            "description": f"Replaced '{word2}' with '{alternative}'",
                            "sentence_index": i + 1
                        })

        return modified, enhancements


def process_input(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main processing function for CLI interface

    Args:
        input_data: JSON input with text, section_type, dimensions, intensity

    Returns:
        JSON output with burstiness-enhanced text and statistics
    """
    start_time = time.perf_counter()

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
        dimensions = input_data.get("dimensions", [1, 2, 3])
        intensity = input_data.get("intensity", "moderate")

        # Validate dimensions
        if not isinstance(dimensions, list) or not all(isinstance(d, int) and 1 <= d <= 6 for d in dimensions):
            return {
                "status": "error",
                "error": {
                    "code": "INVALID_DIMENSIONS",
                    "message": "Dimensions must be a list of integers between 1 and 6"
                }
            }

        # Check for unsupported dimensions (4-6 in Sprint 5)
        if any(d > 3 for d in dimensions):
            return {
                "status": "error",
                "error": {
                    "code": "UNSUPPORTED_DIMENSION",
                    "message": "Dimensions 4-6 not yet implemented (Sprint 5). Use dimensions 1-3."
                }
            }

        # Validate intensity
        if intensity not in ["subtle", "moderate", "strong"]:
            return {
                "status": "error",
                "error": {
                    "code": "INVALID_INTENSITY",
                    "message": f"Invalid intensity '{intensity}'. Must be: subtle, moderate, or strong"
                }
            }

        # Initialize enhancer
        seed = input_data.get("seed")  # Optional for testing reproducibility
        enhancer = BurstinessEnhancer(seed=seed)

        # Process
        result = enhancer.enhance_burstiness(text, section_type, dimensions, intensity)

        # Calculate processing time (ensure at least 1ms to avoid 0)
        processing_time_ms = max(1, int((time.perf_counter() - start_time) * 1000))

        # Return success response
        return {
            "status": "success",
            "data": result,
            "metadata": {
                "processing_time_ms": processing_time_ms,
                "tool": "burstiness_enhancer",
                "version": "1.0",
                "input_length": len(text),
                "output_length": len(result["enhanced_text"]),
                "section_type": section_type,
                "dimensions": dimensions,
                "intensity": intensity,
                "seed": seed
            }
        }

    except Exception as e:
        logger.error(f"Burstiness enhancement failed", data={
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
