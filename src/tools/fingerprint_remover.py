#!/usr/bin/env python3
"""
AI Fingerprint Removal Tool

Identifies and removes AI-generated text fingerprints (filler phrases, repetitive patterns,
AI punctuation tells). Operates via stdin/stdout JSON interface for Claude Code orchestration.

Input JSON:
{
    "text": "The text to analyze...",
    "section_type": "introduction|methods|results|discussion|conclusion",
    "aggressiveness": "conservative|moderate|aggressive"
}

Output JSON:
{
    "status": "success|error",
    "data": {
        "cleaned_text": "Text with AI fingerprints removed...",
        "fingerprints_removed": [
            {"type": "filler_phrase", "original": "It is important to note that", "replacement": ""},
            {"type": "hedging", "original": "arguably", "replacement": ""}
        ],
        "statistics": {
            "total_removals": 15,
            "filler_phrases": 8,
            "hedging_words": 3,
            "punctuation_tells": 4
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
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import get_logger

# Initialize logger (file output only, no console for clean JSON)
logger = get_logger(__name__)


class FingerprintRemover:
    """
    AI Fingerprint Removal Engine

    Detects and removes AI-generated text tells:
    - Filler phrases ("It is important to note that", "It's worth noting", etc.)
    - Hedging language overuse ("arguably", "perhaps", "might", etc.)
    - AI punctuation tells (em dashes, comma-linked clauses)
    - Repetitive sentence structures
    """

    def __init__(self):
        """Initialize fingerprint patterns database"""
        self.start_time = time.time()

        # AI filler phrase patterns (15+ patterns)
        # Using (?i) flag for case-insensitivity instead of character classes
        self.filler_phrases = {
            # Academic hedging overused by AI
            r'(?i)\bit is important to note that\b': '',
            r'(?i)\bit(?:\'s| is) worth noting that\b': '',
            r'(?i)\bit should be noted that\b': '',
            r'(?i)\bit is worth mentioning that\b': '',
            r'(?i)\bit is interesting to note that\b': '',

            # Transition overuse
            r'(?i)\bmoreover\b(?:,)?': '',  # Remove standalone "Moreover,"
            r'(?i)\bfurthermore\b(?:,)?': '',
            r'(?i)\badditionally\b(?:,)?': '',
            r'(?i)\bin addition to this\b(?:,)?': '',

            # Meta-commentary (AI explaining itself)
            r'(?i)\bas mentioned (?:previously|earlier|above)\b(?:,)?': '',
            r'(?i)\bas discussed (?:previously|earlier|above)\b(?:,)?': '',
            r'(?i)\bas we have seen\b(?:,)?': '',

            # Redundant qualifiers
            r'(?i)\bin essence\b(?:,)?': '',
            r'(?i)\bbasically\b(?:,)?': '',
            r'(?i)\bessentially\b(?:,)?': '',

            # Overly formal starts (AI default patterns)
            r'(?i)^it is evident that\b': '',
            r'(?i)^it can be seen that\b': '',
            r'(?i)^it is clear that\b': '',
        }

        # Hedging words (remove if excessive)
        self.hedging_words = [
            'arguably', 'perhaps', 'possibly', 'seemingly', 'apparently',
            'presumably', 'conceivably', 'potentially', 'likely', 'probably',
            'may', 'might', 'could', 'would', 'should'
        ]

        # AI punctuation tells
        self.punctuation_patterns = {
            # Em dash overuse (AI loves em dashes)
            r'\s*—\s*': ' - ',  # Replace em dash with en dash

            # Comma-linked independent clauses (AI habit)
            r',\s+(?=\b(?:however|moreover|furthermore|additionally|therefore|thus|hence)\b)': '; ',

            # Excessive semicolon use
            # (Pattern to detect semicolons used >2 times per paragraph)
        }

        # Repetitive structure patterns
        self.structure_patterns = {
            # Repeated sentence starters
            r'^The\s+': '',  # Remove "The" at start of consecutive sentences
            r'^This\s+': '',  # Remove "This" at start of consecutive sentences
        }

        logger.info("FingerprintRemover initialized", data={
            "filler_patterns": len(self.filler_phrases),
            "hedging_words": len(self.hedging_words),
            "punctuation_patterns": len(self.punctuation_patterns)
        })

    def remove_fingerprints(
        self,
        text: str,
        section_type: str = "general",
        aggressiveness: str = "moderate"
    ) -> Dict[str, Any]:
        """
        Remove AI fingerprints from text

        Args:
            text: Input text to clean
            section_type: Section type for context-aware cleaning
            aggressiveness: Cleaning aggressiveness level
                - conservative: Only remove obvious AI tells
                - moderate: Remove common patterns (default)
                - aggressive: Remove all suspected patterns

        Returns:
            Dictionary with cleaned text and removal statistics
        """
        logger.info(f"Starting fingerprint removal", data={
            "text_length": len(text),
            "section_type": section_type,
            "aggressiveness": aggressiveness
        })

        cleaned_text = text
        removals = []
        stats = {
            "total_removals": 0,
            "filler_phrases": 0,
            "hedging_words": 0,
            "punctuation_tells": 0,
            "structure_fixes": 0
        }

        # 1. Remove filler phrases
        cleaned_text, filler_removals = self._remove_filler_phrases(
            cleaned_text, aggressiveness
        )
        removals.extend(filler_removals)
        stats["filler_phrases"] = len(filler_removals)

        # 2. Reduce hedging language
        cleaned_text, hedging_removals = self._reduce_hedging(
            cleaned_text, section_type, aggressiveness
        )
        removals.extend(hedging_removals)
        stats["hedging_words"] = len(hedging_removals)

        # 3. Fix AI punctuation tells
        cleaned_text, punct_removals = self._fix_punctuation_tells(
            cleaned_text, aggressiveness
        )
        removals.extend(punct_removals)
        stats["punctuation_tells"] = len(punct_removals)

        # 4. Fix repetitive structures
        cleaned_text, structure_removals = self._fix_repetitive_structures(
            cleaned_text, aggressiveness
        )
        removals.extend(structure_removals)
        stats["structure_fixes"] = len(structure_removals)

        # 5. Clean up extra whitespace
        cleaned_text = self._clean_whitespace(cleaned_text)

        stats["total_removals"] = len(removals)

        logger.info(f"Fingerprint removal complete", data={
            "total_removals": stats["total_removals"],
            "filler_phrases": stats["filler_phrases"],
            "hedging_words": stats["hedging_words"],
            "punctuation_tells": stats["punctuation_tells"],
            "structure_fixes": stats["structure_fixes"]
        })

        return {
            "cleaned_text": cleaned_text,
            "fingerprints_removed": removals,
            "statistics": stats
        }

    def _remove_filler_phrases(
        self,
        text: str,
        aggressiveness: str
    ) -> Tuple[str, List[Dict[str, str]]]:
        """Remove AI filler phrases"""
        removals = []
        cleaned = text

        for pattern, replacement in self.filler_phrases.items():
            # Collect all matches before processing
            matches = list(re.finditer(pattern, cleaned))

            # Filter based on aggressiveness
            if aggressiveness == "conservative":
                # Only keep most obvious patterns
                matches = [m for m in matches if
                          "important to note" in m.group(0).lower() or
                          "worth noting" in m.group(0).lower()]

            # Work backwards through matches to preserve positions
            for match in reversed(matches):
                original = match.group(0)
                start = match.start()
                end = match.end()

                # Clean up extra space after removal
                if end < len(cleaned) and cleaned[end] == ' ':
                    end += 1  # Remove trailing space
                elif start > 0 and cleaned[start-1] == ' ':
                    start -= 1  # Remove leading space

                # Replace and track
                cleaned = cleaned[:start] + replacement + cleaned[end:]
                removals.append({
                    "type": "filler_phrase",
                    "original": original,
                    "replacement": replacement,
                    "position": match.start()
                })

        return cleaned, removals

    def _reduce_hedging(
        self,
        text: str,
        section_type: str,
        aggressiveness: str
    ) -> Tuple[str, List[Dict[str, str]]]:
        """
        Reduce excessive hedging language

        Methods section: Allow more hedging (scientific caution)
        Results section: Minimize hedging (present findings confidently)
        """
        removals = []
        cleaned = text

        # Section-specific hedging tolerance
        hedge_threshold = {
            "methods": 0.04,      # 4% of words can be hedging (more tolerant)
            "results": 0.015,     # 1.5% (minimize hedging)
            "discussion": 0.03,   # 3% (balanced)
            "introduction": 0.025,# 2.5%
            "conclusion": 0.02,   # 2%
            "general": 0.025      # Default
        }.get(section_type, 0.025)

        # Adjust threshold by aggressiveness
        if aggressiveness == "aggressive":
            hedge_threshold *= 0.5  # More strict
        elif aggressiveness == "conservative":
            hedge_threshold *= 1.5  # More lenient

        # Count hedge words
        words = re.findall(r'\b\w+\b', text.lower())
        hedge_count = sum(1 for w in words if w in self.hedging_words)
        hedge_ratio = hedge_count / len(words) if words else 0

        # If excessive hedging, remove some
        # Use ceiling for more sensitive/aggressive removal calculation
        if hedge_ratio > hedge_threshold:
            import math
            excess_ratio = hedge_ratio - hedge_threshold

            # Results section should be more aggressive in hedge removal
            if section_type == "results":
                excess_ratio *= 1.2  # 20% boost for results section
            else:
                # Non-results sections: reduce removals to preserve some hedging
                excess_ratio *= 0.5  # 50% reduction for introduction/discussion/etc.

            removals_needed = math.ceil(excess_ratio * len(words))

            for hedge_word in self.hedging_words:
                if removals_needed <= 0:
                    break

                # Find all occurrences (work backwards to preserve positions)
                pattern = r'\b' + re.escape(hedge_word) + r'\b'
                matches = list(re.finditer(pattern, cleaned, re.IGNORECASE))

                # Remove some instances (not all) - work backwards through matches
                # Results section: remove all matches if needed, other sections: remove half + 1
                if section_type == "results":
                    num_to_remove = min(len(matches), removals_needed)
                else:
                    num_to_remove = min(len(matches) // 2 + 1, len(matches), removals_needed)
                for match in reversed(matches[-num_to_remove:]):
                    original = match.group(0)
                    # Remove with surrounding space if present
                    start = match.start()
                    end = match.end()

                    # Clean up extra space after removal
                    if start > 0 and cleaned[start-1] == ' ' and end < len(cleaned) and cleaned[end] == ' ':
                        start -= 1  # Remove leading space
                    elif end < len(cleaned) and cleaned[end] == ' ':
                        end += 1  # Remove trailing space
                    elif start > 0 and cleaned[start-1] == ' ':
                        start -= 1  # Remove leading space

                    cleaned = cleaned[:start] + cleaned[end:]
                    removals.append({
                        "type": "hedging",
                        "original": original,
                        "replacement": "",
                        "position": match.start()
                    })
                    removals_needed -= 1

                    if removals_needed <= 0:
                        break

        return cleaned, removals

    def _fix_punctuation_tells(
        self,
        text: str,
        aggressiveness: str
    ) -> Tuple[str, List[Dict[str, str]]]:
        """Fix AI punctuation patterns"""
        removals = []
        cleaned = text

        for pattern, replacement in self.punctuation_patterns.items():
            # First collect all matches before replacement
            matches = list(re.finditer(pattern, cleaned))

            # Use re.sub for proper replacement (handles position shifts)
            cleaned = re.sub(pattern, replacement, cleaned)

            # Track removals
            for match in matches:
                original = match.group(0)
                removals.append({
                    "type": "punctuation_tell",
                    "original": original,
                    "replacement": replacement,
                    "position": match.start()
                })

        return cleaned, removals

    def _fix_repetitive_structures(
        self,
        text: str,
        aggressiveness: str
    ) -> Tuple[str, List[Dict[str, str]]]:
        """
        Fix repetitive sentence structures

        Detects consecutive sentences starting with the same word
        """
        removals = []
        cleaned = text

        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', cleaned)

        if len(sentences) < 2:
            return cleaned, removals

        # Check for consecutive same-start sentences
        for i in range(len(sentences) - 1):
            current_start = re.match(r'^\w+', sentences[i])
            next_start = re.match(r'^\w+', sentences[i + 1])

            if current_start and next_start:
                if current_start.group(0).lower() == next_start.group(0).lower():
                    # Remove repeated starter from second sentence
                    word = next_start.group(0)
                    if word.lower() in ['the', 'this', 'these', 'those']:
                        sentences[i + 1] = sentences[i + 1][len(word):].lstrip()
                        removals.append({
                            "type": "structure_fix",
                            "original": word,
                            "replacement": "",
                            "position": -1  # Sentence-level fix
                        })

        # Rejoin sentences
        cleaned = ' '.join(sentences)

        return cleaned, removals

    def _clean_whitespace(self, text: str) -> str:
        """Clean up excessive whitespace"""
        # Multiple spaces → single space
        text = re.sub(r' {2,}', ' ', text)

        # Multiple newlines → double newline (paragraph break)
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Space before punctuation
        text = re.sub(r' +([.,;:!?])', r'\1', text)

        # Trim lines
        text = '\n'.join(line.strip() for line in text.split('\n'))

        return text.strip()


def process_input(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main processing function for CLI interface

    Args:
        input_data: JSON input with text, section_type, aggressiveness

    Returns:
        JSON output with cleaned text and statistics
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
        aggressiveness = input_data.get("aggressiveness", "moderate")

        # Validate aggressiveness
        if aggressiveness not in ["conservative", "moderate", "aggressive"]:
            return {
                "status": "error",
                "error": {
                    "code": "INVALID_AGGRESSIVENESS",
                    "message": f"Invalid aggressiveness '{aggressiveness}'. Must be: conservative, moderate, or aggressive"
                }
            }

        # Initialize remover
        remover = FingerprintRemover()

        # Process
        result = remover.remove_fingerprints(text, section_type, aggressiveness)

        # Calculate processing time (ensure at least 1ms to avoid 0)
        processing_time_ms = max(1, int((time.time() - start_time) * 1000))

        # Return success response
        return {
            "status": "success",
            "data": result,
            "metadata": {
                "processing_time_ms": processing_time_ms,
                "tool": "fingerprint_remover",
                "version": "1.0",
                "input_length": len(text),
                "output_length": len(result["cleaned_text"]),
                "section_type": section_type,
                "aggressiveness": aggressiveness
            }
        }

    except Exception as e:
        logger.error(f"Fingerprint removal failed", data={
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
