"""
Adaptive Aggression Analyzer - Sprint 9
========================================

Automatically selects optimal paraphrasing aggression level (1-5) based on
AI detection risk analysis.

Risk Factors Analyzed:
- Sentence structure uniformity
- Vocabulary diversity (Type-Token Ratio)
- Transition word patterns
- Burstiness (sentence length variance)
- Academic phrase frequency
- Sentence opening diversity
- Passive voice ratio
- Sentence complexity balance

Author: BMAD Development Team
Date: 2025-10-31
Sprint: Sprint 9
"""

import re
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter
from dataclasses import dataclass
import time


@dataclass
class AnalysisResult:
    """Container for adaptive aggression analysis results."""
    risk_score: float  # 0-100
    recommended_level: int  # 1-5
    justification: str  # Human-readable explanation
    factors: Dict[str, float]  # Individual factor scores (0.0-1.0)
    confidence: float  # 0.0-1.0
    metadata: Dict[str, Any]  # Additional analysis data


class AdaptiveAggressionAnalyzer:
    """
    Analyzes text and recommends optimal aggression level for paraphrasing.

    Analyzes 8 risk factors indicative of AI-generated text:
    1. Sentence Structure Uniformity (15%)
    2. Vocabulary Diversity (15%)
    3. Transition Word Patterns (10%)
    4. Burstiness - Sentence Length Variance (20%)
    5. Academic Phrase Frequency (10%)
    6. Sentence Opening Diversity (15%)
    7. Passive Voice Ratio (10%)
    8. Sentence Complexity Balance (5%)

    Risk Score Mapping:
    - 0-20:   Level 1 (Gentle)
    - 21-40:  Level 2 (Moderate)
    - 41-60:  Level 3 (Aggressive)
    - 61-80:  Level 4 (Intensive)
    - 81-100: Level 5 (Nuclear)
    """

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialize analyzer with optional custom weights.

        Args:
            weights: Custom weight dictionary (must sum to 100)
        """
        # Default weights (sum to 100)
        self.weights = weights or {
            'sentence_uniformity': 15,
            'vocabulary_diversity': 15,
            'transition_patterns': 10,
            'burstiness': 20,
            'academic_phrases': 10,
            'opening_diversity': 15,
            'passive_voice': 10,
            'sentence_complexity': 5
        }

        # Validate weights
        if abs(sum(self.weights.values()) - 100) > 0.01:
            raise ValueError(f"Weights must sum to 100, got {sum(self.weights.values())}")

        # Common patterns for detection
        self._formal_transitions = {
            'however', 'moreover', 'furthermore', 'additionally',
            'nevertheless', 'nonetheless', 'therefore', 'thus',
            'consequently', 'firstly', 'secondly', 'thirdly',
            'finally', 'in conclusion', 'to summarize'
        }

        self._formulaic_phrases = [
            'it is important to note that',
            'it is worth noting that',
            'it can be seen that',
            'it should be noted that',
            'this study aims to',
            'the purpose of this study',
            'in the context of',
            'with respect to',
            'in terms of',
            'as a result of',
            'due to the fact that',
            'in order to',
            'it has been found that',
            'it has been shown that',
            'research has shown that'
        ]

        # Passive voice detection patterns
        self._passive_patterns = [
            r'\b(is|are|was|were)\s+\w+ed\b',
            r'\b(is|are|was|were)\s+being\s+\w+ed\b',
            r'\b(has|have|had)\s+been\s+\w+ed\b'
        ]

    def analyze_text(self, text: str) -> AnalysisResult:
        """
        Perform comprehensive text analysis and return risk assessment.

        Args:
            text: Input text to analyze

        Returns:
            AnalysisResult with risk score, level, justification, etc.
        """
        start_time = time.time()

        # Preprocess text
        sentences = self._split_sentences(text)
        tokens = self._tokenize(text)
        word_count = len(tokens)
        sentence_count = len(sentences)

        # Handle edge case: very short text
        if word_count < 50:
            return self._create_fallback_result(
                word_count, sentence_count,
                reason="Text too short for reliable analysis (<50 words)"
            )

        # Calculate individual risk factors
        factors = {
            'sentence_uniformity': self._analyze_sentence_uniformity(sentences),
            'vocabulary_diversity': self._analyze_vocabulary_diversity(tokens),
            'transition_patterns': self._analyze_transition_patterns(sentences),
            'burstiness': self._analyze_burstiness(sentences),
            'academic_phrases': self._analyze_academic_phrases(text),
            'opening_diversity': self._analyze_opening_diversity(sentences),
            'passive_voice': self._analyze_passive_voice(sentences),
            'sentence_complexity': self._analyze_sentence_complexity(sentences)
        }

        # Calculate overall risk score
        risk_score = self._calculate_risk_score(factors)

        # Select aggression level
        recommended_level = self._select_aggression_level(risk_score)

        # Calculate confidence
        confidence = self._calculate_confidence(text, factors, word_count, sentence_count)

        # Generate justification
        justification = self._generate_justification(
            risk_score, recommended_level, factors, confidence
        )

        # Collect metadata
        analysis_time_ms = (time.time() - start_time) * 1000
        metadata = {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'analysis_time_ms': round(analysis_time_ms, 2),
            'weights': self.weights
        }

        return AnalysisResult(
            risk_score=risk_score,
            recommended_level=recommended_level,
            justification=justification,
            factors=factors,
            confidence=confidence,
            metadata=metadata
        )

    # =========================================================================
    # Text Preprocessing
    # =========================================================================

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences (simple rule-based)."""
        # Replace common abbreviations to avoid false splits
        text = re.sub(r'(\w)\.(\w)', r'\1<DOT>\2', text)
        text = text.replace('Dr.', 'Dr<DOT>')
        text = text.replace('Mr.', 'Mr<DOT>')
        text = text.replace('Ms.', 'Ms<DOT>')
        text = text.replace('Prof.', 'Prof<DOT>')
        text = text.replace('et al.', 'et al<DOT>')
        text = text.replace('i.e.', 'i<DOT>e<DOT>')
        text = text.replace('e.g.', 'e<DOT>g<DOT>')

        # Split on sentence terminators
        sentences = re.split(r'[.!?]+\s+', text)

        # Restore abbreviations
        sentences = [s.replace('<DOT>', '.') for s in sentences if s.strip()]

        return sentences

    def _tokenize(self, text: str) -> List[str]:
        """Simple word tokenization (lowercase, alphanumeric only)."""
        # Remove punctuation and split
        tokens = re.findall(r'\b[a-z]+\b', text.lower())
        return tokens

    # =========================================================================
    # Risk Factor Analyzers
    # =========================================================================

    def _analyze_sentence_uniformity(self, sentences: List[str]) -> float:
        """
        Factor 1: Sentence Structure Uniformity (0.0-1.0)

        AI tendency: Uniform sentence lengths and structures
        Human tendency: Varied sentence lengths and structures
        """
        if len(sentences) < 3:
            return 0.0

        # 1. Calculate word count variance
        lengths = [len(s.split()) for s in sentences]
        mean_length = np.mean(lengths)
        std_length = np.std(lengths)

        # Coefficient of variation
        cv = std_length / mean_length if mean_length > 0 else 0

        # 2. Sentence opening patterns
        openings = []
        for s in sentences:
            words = s.split()
            if words:
                openings.append(words[0].lower())

        unique_openings = len(set(openings))
        opening_diversity = unique_openings / len(sentences) if sentences else 1.0

        # 3. Combine metrics
        # Low CV = uniform = high risk
        cv_risk = 1 - min(cv / 0.5, 1.0)  # Normalize to 0.5 CV

        # Low diversity = high risk
        diversity_risk = 1 - opening_diversity

        uniformity_score = cv_risk * 0.6 + diversity_risk * 0.4

        return max(0.0, min(1.0, uniformity_score))

    def _analyze_vocabulary_diversity(self, tokens: List[str]) -> float:
        """
        Factor 2: Vocabulary Diversity (0.0-1.0)

        AI tendency: Limited vocabulary, repetitive word choice
        Human tendency: Rich vocabulary, varied expressions
        """
        if len(tokens) < 20:
            return 0.0

        # 1. Type-Token Ratio (TTR)
        unique_tokens = len(set(tokens))
        total_tokens = len(tokens)
        ttr = unique_tokens / total_tokens if total_tokens > 0 else 0

        # 2. Hapax legomena (words appearing exactly once)
        word_freq = Counter(tokens)
        hapax_count = sum(1 for count in word_freq.values() if count == 1)
        hapax_ratio = hapax_count / unique_tokens if unique_tokens > 0 else 0

        # 3. Calculate risk
        # Expected TTR for academic text: 0.5-0.7
        # Expected hapax ratio: 0.4-0.6
        ttr_risk = 1 - min(ttr / 0.6, 1.0)
        hapax_risk = 1 - min(hapax_ratio / 0.5, 1.0)

        diversity_risk = ttr_risk * 0.6 + hapax_risk * 0.4

        return max(0.0, min(1.0, diversity_risk))

    def _analyze_transition_patterns(self, sentences: List[str]) -> float:
        """
        Factor 3: Transition Word Patterns (0.0-1.0)

        AI tendency: Overuses formal transition words
        Human tendency: Natural, varied transitions
        """
        if len(sentences) < 5:
            return 0.0

        text_lower = ' '.join(sentences).lower()

        # Count transition occurrences
        transition_count = sum(
            text_lower.count(trans) for trans in self._formal_transitions
        )

        # Expected rate: 1-2 per 10 sentences
        sentence_count = len(sentences)
        expected_rate = (sentence_count / 10) * 1.5

        if transition_count <= expected_rate:
            overuse_score = 0.0
        else:
            excess = transition_count - expected_rate
            overuse_score = min(excess / expected_rate, 1.0)

        return overuse_score

    def _analyze_burstiness(self, sentences: List[str]) -> float:
        """
        Factor 4: Burstiness - Sentence Length Variance (0.0-1.0)

        AI tendency: Uniform sentence lengths (low variance)
        Human tendency: High variance (burstiness)

        **Highest weight factor (20%)**
        """
        if len(sentences) < 3:
            return 0.0

        sentence_lengths = [len(s.split()) for s in sentences]
        mean_length = np.mean(sentence_lengths)
        std_length = np.std(sentence_lengths)

        # Coefficient of Variation
        cv = std_length / mean_length if mean_length > 0 else 0

        # Human academic writing CV: 0.4-0.6
        # AI writing CV: 0.1-0.3
        if cv >= 0.4:
            burstiness_risk = 0.0  # Human-like variance
        elif cv <= 0.15:
            burstiness_risk = 1.0  # AI-like uniformity
        else:
            # Linear interpolation
            burstiness_risk = (0.4 - cv) / (0.4 - 0.15)

        return max(0.0, min(1.0, burstiness_risk))

    def _analyze_academic_phrases(self, text: str) -> float:
        """
        Factor 5: Academic Phrase Frequency (0.0-1.0)

        AI tendency: Overuses formulaic academic phrases
        Human tendency: Natural phrasing, varied expression
        """
        text_lower = text.lower()
        word_count = len(text.split())

        # Count formulaic phrases
        phrase_count = sum(
            text_lower.count(phrase) for phrase in self._formulaic_phrases
        )

        # Expected rate: 0-2 per 1000 words
        expected_rate = (word_count / 1000) * 1.0

        if phrase_count <= expected_rate:
            formulaic_score = 0.0
        else:
            excess = phrase_count - expected_rate
            formulaic_score = min(excess / max(expected_rate, 1), 1.0)

        return formulaic_score

    def _analyze_opening_diversity(self, sentences: List[str]) -> float:
        """
        Factor 6: Sentence Opening Diversity (0.0-1.0)

        AI tendency: Starts sentences with same words (The, This, It)
        Human tendency: Varied sentence openings
        """
        if len(sentences) < 5:
            return 0.0

        # Extract first word of each sentence
        openings = []
        for sent in sentences:
            words = sent.strip().split()
            if words:
                openings.append(words[0].lower())

        if not openings:
            return 0.0

        # Calculate frequency distribution
        opening_freq = Counter(openings)
        total_openings = len(openings)

        # Check for AI patterns
        the_ratio = opening_freq.get('the', 0) / total_openings
        this_these_ratio = (opening_freq.get('this', 0) + opening_freq.get('these', 0)) / total_openings
        it_they_ratio = (opening_freq.get('it', 0) + opening_freq.get('they', 0)) / total_openings

        # Simpson's Diversity Index
        diversity_index = 1 - sum((count / total_openings) ** 2 for count in opening_freq.values())

        # Calculate risk
        pattern_risk = (the_ratio > 0.3) * 0.3 + (this_these_ratio > 0.2) * 0.2 + (it_they_ratio > 0.15) * 0.15
        diversity_risk = 1 - diversity_index

        opening_risk = pattern_risk * 0.6 + diversity_risk * 0.4

        return max(0.0, min(1.0, opening_risk))

    def _analyze_passive_voice(self, sentences: List[str]) -> float:
        """
        Factor 7: Passive Voice Ratio (0.0-1.0)

        AI tendency: Overuses passive voice in academic writing
        Human tendency: Balanced active/passive voice
        """
        if not sentences:
            return 0.0

        passive_count = 0
        total_sentences = len(sentences)

        for sent in sentences:
            sent_lower = sent.lower()
            for pattern in self._passive_patterns:
                if re.search(pattern, sent_lower):
                    passive_count += 1
                    break  # Count once per sentence

        passive_ratio = passive_count / total_sentences if total_sentences > 0 else 0

        # Expected range: 0.2-0.4 (20-40%)
        # AI range: 0.5-0.7 (50-70%)
        if passive_ratio <= 0.4:
            passive_risk = 0.0
        elif passive_ratio >= 0.65:
            passive_risk = 1.0
        else:
            # Linear interpolation
            passive_risk = (passive_ratio - 0.4) / (0.65 - 0.4)

        return max(0.0, min(1.0, passive_risk))

    def _analyze_sentence_complexity(self, sentences: List[str]) -> float:
        """
        Factor 8: Sentence Complexity Balance (0.0-1.0)

        AI tendency: Imbalanced (all simple or all complex)
        Human tendency: Balanced mix of simple, compound, complex
        """
        if len(sentences) < 5:
            return 0.0

        simple_count = 0
        compound_count = 0
        complex_count = 0

        for sent in sentences:
            word_count = len(sent.split())
            comma_count = sent.count(',')

            if word_count < 15 and comma_count <= 1:
                simple_count += 1
            elif word_count < 30 and comma_count <= 3:
                compound_count += 1
            else:
                complex_count += 1

        total = len(sentences)
        simple_ratio = simple_count / total
        compound_ratio = compound_count / total
        complex_ratio = complex_count / total

        # Check for imbalance (any category >60%)
        max_ratio = max(simple_ratio, compound_ratio, complex_ratio)

        if max_ratio <= 0.5:
            complexity_risk = 0.0
        elif max_ratio >= 0.75:
            complexity_risk = 1.0
        else:
            # Linear interpolation
            complexity_risk = (max_ratio - 0.5) / (0.75 - 0.5)

        return max(0.0, min(1.0, complexity_risk))

    # =========================================================================
    # Risk Score Calculation
    # =========================================================================

    def _calculate_risk_score(self, factors: Dict[str, float]) -> float:
        """
        Aggregate factor scores into overall risk score (0-100).

        Args:
            factors: Dict of factor_name -> score (0.0-1.0)

        Returns:
            risk_score: 0-100
        """
        weighted_score = sum(
            factors[factor] * weight
            for factor, weight in self.weights.items()
        )

        return max(0, min(100, weighted_score))

    def _calculate_confidence(
        self,
        text: str,
        factors: Dict[str, float],
        word_count: int,
        sentence_count: int
    ) -> float:
        """
        Calculate confidence in the risk assessment (0.0-1.0).

        Factors:
        - Text length (longer = more confident)
        - Factor agreement (similar scores = more confident)
        - Extreme values (very high/low = more confident)
        """
        # 1. Length-based confidence
        if word_count < 200:
            length_confidence = 0.5
        elif word_count < 500:
            length_confidence = 0.7
        elif word_count < 1000:
            length_confidence = 0.85
        else:
            length_confidence = 1.0

        # 2. Factor agreement (low std = high agreement)
        factor_values = list(factors.values())
        factor_std = np.std(factor_values)
        agreement_confidence = 1 - min(factor_std, 1.0)

        # 3. Extremity (clear signal = high confidence)
        mean_factor = np.mean(factor_values)
        if mean_factor < 0.2 or mean_factor > 0.8:
            extremity_confidence = 1.0
        else:
            extremity_confidence = 0.7

        # Combine confidences
        overall_confidence = (
            length_confidence * 0.4 +
            agreement_confidence * 0.3 +
            extremity_confidence * 0.3
        )

        return max(0.0, min(1.0, overall_confidence))

    # =========================================================================
    # Level Selection
    # =========================================================================

    def _select_aggression_level(self, risk_score: float) -> int:
        """
        Map risk score to aggression level (1-5).

        Thresholds:
        - 0-20:   Level 1 (Gentle)
        - 21-40:  Level 2 (Moderate)
        - 41-60:  Level 3 (Aggressive)
        - 61-80:  Level 4 (Intensive)
        - 81-100: Level 5 (Nuclear)
        """
        if risk_score <= 20:
            return 1
        elif risk_score <= 40:
            return 2
        elif risk_score <= 60:
            return 3
        elif risk_score <= 80:
            return 4
        else:
            return 5

    def _generate_justification(
        self,
        risk_score: float,
        level: int,
        factors: Dict[str, float],
        confidence: float
    ) -> str:
        """Generate human-readable justification for level selection."""
        # Risk category
        if risk_score <= 20:
            risk_category = "Very Low Risk"
        elif risk_score <= 40:
            risk_category = "Low Risk"
        elif risk_score <= 60:
            risk_category = "Moderate Risk"
        elif risk_score <= 80:
            risk_category = "High Risk"
        else:
            risk_category = "Very High Risk"

        # Level name
        level_names = {
            1: "Gentle",
            2: "Moderate",
            3: "Aggressive",
            4: "Intensive",
            5: "Nuclear"
        }

        # Top 3 risk factors
        sorted_factors = sorted(factors.items(), key=lambda x: x[1], reverse=True)
        top_factors = sorted_factors[:3]

        # Build justification
        lines = [
            "=" * 70,
            "ADAPTIVE AGGRESSION ANALYSIS",
            "=" * 70,
            "",
            f"Risk Score: {risk_score:.1f}/100 ({risk_category})",
            f"Recommended Level: {level} ({level_names[level]})",
            f"Confidence: {confidence:.1%}",
            "",
            "Top Risk Factors:",
        ]

        for factor, score in top_factors:
            factor_name = self._format_factor_name(factor)
            risk_level = self._risk_level_description(score)
            lines.append(f"  * {factor_name}: {score:.2f} ({risk_level})")

        lines.append("")
        lines.append(f"Rationale: {self._generate_rationale(risk_score, top_factors)}")
        lines.append("=" * 70)

        return "\n".join(lines)

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _format_factor_name(self, factor: str) -> str:
        """Convert factor key to human-readable name."""
        names = {
            'sentence_uniformity': 'Sentence Structure Uniformity',
            'vocabulary_diversity': 'Vocabulary Diversity',
            'transition_patterns': 'Transition Word Patterns',
            'burstiness': 'Sentence Length Variance (Burstiness)',
            'academic_phrases': 'Academic Phrase Frequency',
            'opening_diversity': 'Sentence Opening Diversity',
            'passive_voice': 'Passive Voice Ratio',
            'sentence_complexity': 'Sentence Complexity Balance'
        }
        return names.get(factor, factor)

    def _risk_level_description(self, score: float) -> str:
        """Convert numeric score to risk level description."""
        if score <= 0.2:
            return "Very Low"
        elif score <= 0.4:
            return "Low"
        elif score <= 0.6:
            return "Moderate"
        elif score <= 0.8:
            return "High"
        else:
            return "Very High"

    def _generate_rationale(self, risk_score: float, top_factors: List[Tuple[str, float]]) -> str:
        """Generate brief rationale for level recommendation."""
        if risk_score <= 20:
            return "Text shows natural variation typical of human writing. Light paraphrasing sufficient."
        elif risk_score <= 40:
            return "Minor AI patterns detected. Moderate paraphrasing will address most concerns."
        elif risk_score <= 60:
            return "Significant AI markers present. Aggressive rewriting needed for style diversity."
        elif risk_score <= 80:
            return "Strong AI signature detected. Intensive multi-layered transformation required."
        else:
            return "Extremely high AI risk. Nuclear-level paraphrasing (translation chain) necessary."

    def _create_fallback_result(
        self,
        word_count: int,
        sentence_count: int,
        reason: str
    ) -> AnalysisResult:
        """Create fallback result for edge cases."""
        return AnalysisResult(
            risk_score=40.0,  # Default to Level 2 (Moderate)
            recommended_level=2,
            justification=f"Fallback analysis (Reason: {reason}). Defaulting to Level 2 (Moderate).",
            factors={factor: 0.0 for factor in self.weights.keys()},
            confidence=0.3,
            metadata={
                'word_count': word_count,
                'sentence_count': sentence_count,
                'analysis_time_ms': 0,
                'weights': self.weights,
                'fallback': True,
                'fallback_reason': reason
            }
        )

    # =========================================================================
    # Public Utility Methods
    # =========================================================================

    def get_factor_descriptions(self) -> Dict[str, str]:
        """
        Get descriptions of all risk factors.

        Returns:
            Dict mapping factor name to description
        """
        return {
            'sentence_uniformity': 'Uniformity in sentence structure and length (AI: uniform, Human: varied)',
            'vocabulary_diversity': 'Type-Token Ratio and lexical richness (AI: limited, Human: diverse)',
            'transition_patterns': 'Overuse of formal transition words (AI: excessive, Human: natural)',
            'burstiness': 'Sentence length variance (AI: low variance, Human: high variance)',
            'academic_phrases': 'Formulaic academic phrase frequency (AI: overused, Human: varied)',
            'opening_diversity': 'Variety in sentence openings (AI: repetitive, Human: diverse)',
            'passive_voice': 'Passive voice construction ratio (AI: excessive, Human: balanced)',
            'sentence_complexity': 'Balance of simple/compound/complex sentences (AI: imbalanced, Human: balanced)'
        }

    def get_level_descriptions(self) -> Dict[int, str]:
        """
        Get descriptions of all aggression levels.

        Returns:
            Dict mapping level (1-5) to description
        """
        return {
            1: "Level 1 (Gentle): 5-10% change - Light lexical substitution",
            2: "Level 2 (Moderate): 10-20% change - Sentence restructuring",
            3: "Level 3 (Aggressive): 20-35% change - Extensive rewriting",
            4: "Level 4 (Intensive): 35-50% change - Multi-layered transformation",
            5: "Level 5 (Nuclear): 50-70% change - Translation chain (EN→DE→JA→EN)"
        }


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    # Example: Analyze sample text
    sample_text = """
    This study aims to investigate the effects of climate change on agricultural productivity.
    It is important to note that the findings have significant implications.
    The results show that there is a correlation between temperature and yield.
    Moreover, it has been found that precipitation patterns are changing.
    Furthermore, the data indicates that adaptation strategies are necessary.
    In conclusion, this research demonstrates the need for policy interventions.
    """

    analyzer = AdaptiveAggressionAnalyzer()
    result = analyzer.analyze_text(sample_text)

    print(result.justification)
    print(f"\nDetailed Factors:")
    for factor, score in result.factors.items():
        print(f"  {factor}: {score:.3f}")
    print(f"\nMetadata: {result.metadata}")
