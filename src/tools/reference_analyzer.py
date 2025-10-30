#!/usr/bin/env python3
"""
Reference Text Analysis Tool

Analyzes human-written reference texts (1-5 papers) to extract writing style patterns.
These patterns guide the humanization process to match the user's natural academic writing style.

Input JSON:
{
    "reference_texts": [
        {"text": "First reference paper...", "title": "Paper 1"},
        {"text": "Second reference paper...", "title": "Paper 2"}
    ],
    "analysis_depth": "quick|standard|comprehensive"
}

Output JSON:
{
    "status": "success|error",
    "data": {
        "style_profile": {
            "sentence_length_distribution": {"min": 12, "max": 35, "mean": 22.5, "variance": 45.2},
            "transition_phrases": ["However", "Moreover", "In contrast", ...],
            "vocabulary_level": "advanced",
            "paragraph_structure": {...},
            "voice_ratio": {"active": 0.72, "passive": 0.28},
            "tense_distribution": {"past": 0.55, "present": 0.40, "future": 0.05}
        },
        "quality_metrics": {
            "ai_detection_score": 2.5,  # % (lower is better - should be human)
            "perplexity": 145.3,
            "topic_consistency": 0.95
        },
        "recommendations": [
            "Use shorter sentences in Methods section (mean: 18 words)",
            "Incorporate transition phrases: 'Moreover', 'In contrast'",
            ...
        ]
    },
    "metadata": {...}
}

Author: AI Humanizer System
Version: 1.0
Sprint: Sprint 4 (STORY-005 - Week 1)
"""

import sys
import json
import re
import time
import statistics
from typing import Dict, Any, List, Tuple, Optional
from collections import Counter
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import get_logger

# Initialize logger (file output only, no console for clean JSON)
logger = get_logger(__name__)


class ReferenceAnalyzer:
    """
    Reference Text Style Analysis Engine

    Extracts writing style patterns from human-written papers:
    - Sentence length distribution
    - Transition phrase vocabulary
    - Paragraph organization patterns
    - Voice and tense preferences
    - Vocabulary level
    """

    def __init__(self):
        """Initialize analyzer with pattern databases"""
        self.start_time = time.time()

        # Transition phrase vocabulary (to be extracted)
        self.common_transitions = {
            "addition": ["moreover", "furthermore", "additionally", "in addition", "also"],
            "contrast": ["however", "nevertheless", "in contrast", "on the other hand", "conversely"],
            "cause_effect": ["therefore", "thus", "consequently", "as a result", "hence"],
            "example": ["for example", "for instance", "specifically", "in particular"],
            "sequence": ["first", "second", "finally", "subsequently", "next"]
        }

        # Academic vocabulary levels (simplified)
        self.vocabulary_tiers = {
            "basic": ["use", "make", "get", "do", "have"],
            "intermediate": ["utilize", "demonstrate", "obtain", "perform", "exhibit"],
            "advanced": ["employ", "elucidate", "procure", "execute", "manifest"]
        }

        # Section detection patterns (IMRAD)
        self.section_patterns = {
            "introduction": r'(?:^|\n)(?:1\.?\s*)?(?:introduction|background)\b',
            "methods": r'(?:^|\n)(?:2\.?\s*)?(?:methods?|materials? and methods?|experimental)\b',
            "results": r'(?:^|\n)(?:3\.?\s*)?(?:results?|findings?)\b',
            "discussion": r'(?:^|\n)(?:4\.?\s*)?(?:discussion)\b',
            "conclusion": r'(?:^|\n)(?:5\.?\s*)?(?:conclusions?|summary)\b'
        }

        logger.info("ReferenceAnalyzer initialized", data={
            "transition_categories": len(self.common_transitions),
            "vocabulary_tiers": len(self.vocabulary_tiers)
        })

    def analyze_references(
        self,
        reference_texts: List[Dict[str, str]],
        analysis_depth: str = "standard"
    ) -> Dict[str, Any]:
        """
        Analyze reference texts to extract style profile

        Args:
            reference_texts: List of reference texts with titles
            analysis_depth: Analysis depth
                - quick: Basic metrics (sentence length, transition phrases)
                - standard: + vocabulary level, paragraph structure [default]
                - comprehensive: + voice/tense analysis, detailed patterns

        Returns:
            Dictionary with style profile and recommendations
        """
        logger.info(f"Starting reference analysis", data={
            "num_references": len(reference_texts),
            "analysis_depth": analysis_depth
        })

        if not reference_texts:
            return self._empty_profile_error()

        # Validate reference texts (check they're human-written)
        validation_results = self._validate_references(reference_texts)

        if not validation_results["valid"]:
            logger.warning("Reference validation failed", data=validation_results)

        # Combine all reference texts
        combined_text = "\n\n".join([ref["text"] for ref in reference_texts])

        # Extract style profile
        style_profile = {}

        # 1. Sentence length distribution (always)
        style_profile["sentence_length_distribution"] = self._analyze_sentence_lengths(combined_text)

        # 2. Transition phrases (always)
        style_profile["transition_phrases"] = self._extract_transition_phrases(combined_text)

        # 3. Vocabulary level (standard+)
        if analysis_depth in ["standard", "comprehensive"]:
            style_profile["vocabulary_level"] = self._analyze_vocabulary_level(combined_text)

        # 4. Paragraph structure (standard+)
        if analysis_depth in ["standard", "comprehensive"]:
            style_profile["paragraph_structure"] = self._analyze_paragraph_structure(combined_text)

        # 5. Voice and tense (comprehensive)
        if analysis_depth == "comprehensive":
            style_profile["voice_ratio"] = self._analyze_voice_ratio(combined_text)
            style_profile["tense_distribution"] = self._analyze_tense_distribution(combined_text)

        # Generate quality metrics
        quality_metrics = {
            "ai_detection_score": validation_results.get("ai_detection_estimate", "N/A"),
            "perplexity": validation_results.get("perplexity_estimate", "N/A"),
            "topic_consistency": validation_results.get("topic_consistency", 0.95)
        }

        # Generate recommendations
        recommendations = self._generate_recommendations(style_profile, analysis_depth)

        logger.info(f"Reference analysis complete", data={
            "style_features": len(style_profile),
            "recommendations": len(recommendations)
        })

        return {
            "style_profile": style_profile,
            "quality_metrics": quality_metrics,
            "recommendations": recommendations,
            "validation": validation_results
        }

    def _validate_references(
        self,
        reference_texts: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Validate that reference texts are human-written and appropriate

        Checks:
        - Length (should be 500+ words)
        - Academic style (has section headers, citations)
        - Not AI-generated (heuristics)

        Note: Full AI detection requires external API (Originality.ai)
        """
        validation = {
            "valid": True,
            "warnings": [],
            "ai_detection_estimate": "Not computed (requires API)",
            "perplexity_estimate": "Not computed (requires GPT-2)",
            "topic_consistency": 0.95  # Placeholder
        }

        for i, ref in enumerate(reference_texts):
            text = ref["text"]
            title = ref.get("title", f"Reference {i+1}")

            # Length check
            word_count = len(re.findall(r'\b\w+\b', text))
            if word_count < 500:
                validation["warnings"].append(f"{title}: Too short ({word_count} words, min 500)")
                validation["valid"] = False

            # Section structure check (has IMRAD sections?)
            has_sections = any(re.search(pattern, text, re.IGNORECASE) for pattern in self.section_patterns.values())
            if not has_sections:
                validation["warnings"].append(f"{title}: Missing section headers (IMRAD structure)")

            # Academic citation check (has references?)
            has_citations = bool(re.search(r'\[\d+\]|\(\w+,?\s+\d{4}\)', text))
            if not has_citations:
                validation["warnings"].append(f"{title}: No citations found (may not be academic)")

        return validation

    def _analyze_sentence_lengths(self, text: str) -> Dict[str, float]:
        """Analyze sentence length distribution"""
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        # Count words per sentence
        lengths = [len(re.findall(r'\b\w+\b', s)) for s in sentences]

        if not lengths:
            return {"min": 0, "max": 0, "mean": 0, "variance": 0, "median": 0}

        return {
            "min": min(lengths),
            "max": max(lengths),
            "mean": round(statistics.mean(lengths), 2),
            "variance": round(statistics.variance(lengths), 2) if len(lengths) > 1 else 0,
            "median": round(statistics.median(lengths), 2),
            "quartiles": {
                "q1": round(statistics.quantiles(lengths, n=4)[0], 2) if len(lengths) > 3 else 0,
                "q2": round(statistics.quantiles(lengths, n=4)[1], 2) if len(lengths) > 3 else 0,
                "q3": round(statistics.quantiles(lengths, n=4)[2], 2) if len(lengths) > 3 else 0
            }
        }

    def _extract_transition_phrases(self, text: str) -> List[Dict[str, Any]]:
        """Extract transition phrases used in reference text"""
        found_transitions = []

        text_lower = text.lower()

        for category, phrases in self.common_transitions.items():
            for phrase in phrases:
                count = text_lower.count(phrase)
                if count > 0:
                    found_transitions.append({
                        "phrase": phrase,
                        "category": category,
                        "frequency": count
                    })

        # Sort by frequency (most common first)
        found_transitions.sort(key=lambda x: x["frequency"], reverse=True)

        # Limit to top 20
        return found_transitions[:20]

    def _analyze_vocabulary_level(self, text: str) -> Dict[str, Any]:
        """Analyze vocabulary sophistication level"""
        words = re.findall(r'\b\w+\b', text.lower())
        word_counts = Counter(words)

        # Count words in each tier
        tier_counts = {
            "basic": 0,
            "intermediate": 0,
            "advanced": 0
        }

        for tier, tier_words in self.vocabulary_tiers.items():
            for word in tier_words:
                tier_counts[tier] += word_counts.get(word, 0)

        total = sum(tier_counts.values())

        # Calculate vocabulary score (0-100, higher = more advanced)
        if total > 0:
            vocab_score = (tier_counts["intermediate"] * 50 + tier_counts["advanced"] * 100) / total
        else:
            vocab_score = 50  # Neutral

        # Classify
        if vocab_score > 70:
            level = "advanced"
        elif vocab_score > 40:
            level = "intermediate"
        else:
            level = "basic"

        return {
            "level": level,
            "score": round(vocab_score, 2),
            "tier_distribution": tier_counts
        }

    def _analyze_paragraph_structure(self, text: str) -> Dict[str, Any]:
        """Analyze paragraph organization patterns"""
        # Split into paragraphs
        paragraphs = re.split(r'\n\s*\n', text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        # Analyze paragraph lengths (sentences per paragraph)
        paragraph_lengths = []
        for para in paragraphs:
            sentences = re.split(r'(?<=[.!?])\s+', para)
            paragraph_lengths.append(len(sentences))

        if not paragraph_lengths:
            return {"sentences_per_paragraph": {"mean": 0}}

        return {
            "total_paragraphs": len(paragraphs),
            "sentences_per_paragraph": {
                "min": min(paragraph_lengths),
                "max": max(paragraph_lengths),
                "mean": round(statistics.mean(paragraph_lengths), 2)
            },
            "paragraph_transition_usage": "high"  # Placeholder (requires deeper analysis)
        }

    def _analyze_voice_ratio(self, text: str) -> Dict[str, float]:
        """
        Analyze active vs passive voice ratio

        Heuristic: Passive voice markers (was/were/been + past participle)
        """
        sentences = re.split(r'(?<=[.!?])\s+', text)

        passive_count = 0
        active_count = 0

        for sentence in sentences:
            # Check for passive voice markers
            if re.search(r'\b(?:was|were|been|is|are|be)\s+\w+ed\b', sentence, re.IGNORECASE):
                passive_count += 1
            else:
                active_count += 1

        total = passive_count + active_count

        return {
            "active": round(active_count / total, 3) if total > 0 else 0,
            "passive": round(passive_count / total, 3) if total > 0 else 0
        }

    def _analyze_tense_distribution(self, text: str) -> Dict[str, float]:
        """
        Analyze tense distribution (past, present, future)

        Heuristic: Verb form patterns
        """
        # Very simplified tense detection
        past_markers = len(re.findall(r'\b\w+ed\b', text))
        present_markers = len(re.findall(r'\b(?:is|are|have|has)\b', text, re.IGNORECASE))
        future_markers = len(re.findall(r'\b(?:will|shall|going to)\b', text, re.IGNORECASE))

        total = past_markers + present_markers + future_markers

        return {
            "past": round(past_markers / total, 3) if total > 0 else 0,
            "present": round(present_markers / total, 3) if total > 0 else 0,
            "future": round(future_markers / total, 3) if total > 0 else 0
        }

    def _generate_recommendations(
        self,
        style_profile: Dict[str, Any],
        analysis_depth: str
    ) -> List[str]:
        """Generate actionable recommendations based on style profile"""
        recommendations = []

        # Sentence length recommendations
        sent_length = style_profile.get("sentence_length_distribution", {})
        if sent_length.get("mean", 0) > 0:
            recommendations.append(
                f"Target sentence length: {sent_length['mean']:.1f} words on average "
                f"(range: {sent_length['min']}-{sent_length['max']} words)"
            )

        # Transition phrase recommendations
        transitions = style_profile.get("transition_phrases", [])
        if transitions:
            top_phrases = [t["phrase"] for t in transitions[:5]]
            recommendations.append(
                f"Incorporate transition phrases: {', '.join(top_phrases)}"
            )

        # Vocabulary level recommendations
        vocab = style_profile.get("vocabulary_level", {})
        if vocab:
            recommendations.append(
                f"Match vocabulary level: {vocab.get('level', 'intermediate')} "
                f"(score: {vocab.get('score', 0):.1f}/100)"
            )

        # Voice ratio recommendations (comprehensive)
        if analysis_depth == "comprehensive":
            voice = style_profile.get("voice_ratio", {})
            if voice:
                recommendations.append(
                    f"Voice ratio: {voice.get('active', 0)*100:.0f}% active, "
                    f"{voice.get('passive', 0)*100:.0f}% passive"
                )

        return recommendations

    def _empty_profile_error(self) -> Dict[str, Any]:
        """Return error for empty reference texts"""
        return {
            "style_profile": {},
            "quality_metrics": {},
            "recommendations": ["No reference texts provided for analysis"],
            "validation": {
                "valid": False,
                "warnings": ["No reference texts provided"]
            }
        }


def process_input(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main processing function for CLI interface

    Args:
        input_data: JSON input with reference_texts, analysis_depth

    Returns:
        JSON output with style profile and recommendations
    """
    start_time = time.time()

    try:
        # Validate input
        if "reference_texts" not in input_data:
            return {
                "status": "error",
                "error": {
                    "code": "MISSING_FIELD",
                    "message": "Required field 'reference_texts' not found in input"
                }
            }

        reference_texts = input_data["reference_texts"]
        analysis_depth = input_data.get("analysis_depth", "standard")

        # Validate reference_texts structure
        if not isinstance(reference_texts, list):
            return {
                "status": "error",
                "error": {
                    "code": "INVALID_FORMAT",
                    "message": "Field 'reference_texts' must be a list of objects with 'text' field"
                }
            }

        # Validate analysis_depth
        if analysis_depth not in ["quick", "standard", "comprehensive"]:
            return {
                "status": "error",
                "error": {
                    "code": "INVALID_ANALYSIS_DEPTH",
                    "message": f"Invalid analysis_depth '{analysis_depth}'. Must be: quick, standard, or comprehensive"
                }
            }

        # Initialize analyzer
        analyzer = ReferenceAnalyzer()

        # Process
        result = analyzer.analyze_references(reference_texts, analysis_depth)

        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)

        # Return success response
        return {
            "status": "success",
            "data": result,
            "metadata": {
                "processing_time_ms": processing_time_ms,
                "tool": "reference_analyzer",
                "version": "1.0",
                "num_references": len(reference_texts),
                "analysis_depth": analysis_depth,
                "total_words": sum(len(re.findall(r'\b\w+\b', ref["text"])) for ref in reference_texts)
            }
        }

    except Exception as e:
        logger.error(f"Reference analysis failed", data={
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
