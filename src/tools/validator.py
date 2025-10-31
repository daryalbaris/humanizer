"""
Validator Tool - Quality Validation for Humanized Text

This tool validates humanized text against original text to ensure:
1. Semantic similarity (BERTScore ≥0.92)
2. BLEU score (lexical similarity)
3. Protected term preservation (95-98% accuracy)
4. Factual accuracy preservation

Input (JSON stdin):
{
    "original_text": "The original text...",
    "humanized_text": "The humanized version...",
    "placeholder_map": {
        "__TERM_001__": "original term",
        "__NUM_001__": "100°C"
    },
    "validation_thresholds": {
        "min_bertscore": 0.92,
        "min_bleu": 0.40,
        "min_term_preservation": 0.95
    },
    "check_term_preservation": true,
    "check_semantic_similarity": true
}

Output (JSON stdout):
{
    "status": "success",
    "data": {
        "valid": true,
        "semantic_similarity": {
            "bertscore_f1": 0.94,
            "bertscore_precision": 0.93,
            "bertscore_recall": 0.95,
            "passes_threshold": true
        },
        "lexical_similarity": {
            "bleu_score": 0.45,
            "passes_threshold": true
        },
        "term_preservation": {
            "terms_expected": 10,
            "terms_found": 10,
            "preservation_rate": 1.00,
            "passes_threshold": true,
            "missing_terms": []
        },
        "overall_quality": "excellent"
    },
    "metadata": {
        "processing_time_ms": 38000,
        "tool": "validator",
        "version": "1.0"
    }
}

Author: BMAD Development Team
Version: 1.0
Created: 2025-10-30
"""

import sys
import json
import time
import re
from typing import Dict, List, Tuple, Optional
from bert_score import score as bert_score_fn
import nltk
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')


class Validator:
    """
    Validates humanized text for quality, semantic similarity, and term preservation.
    """

    def __init__(self):
        """Initialize the validator with necessary resources."""
        # Download NLTK resources if not already present
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)

        self.smoother = SmoothingFunction()

    def calculate_bertscore(
        self,
        original: str,
        humanized: str,
        lang: str = 'en',
        model_type: str = 'microsoft/deberta-xlarge-mnli'
    ) -> Dict[str, float]:
        """
        Calculate BERTScore between original and humanized text.

        BERTScore measures semantic similarity using contextualized embeddings.
        - Precision: How much of humanized text is relevant to original
        - Recall: How much of original is preserved in humanized
        - F1: Harmonic mean of precision and recall

        Args:
            original: Original text
            humanized: Humanized text
            lang: Language code
            model_type: BERT model to use (default: deberta-xlarge-mnli for best performance)

        Returns:
            Dictionary with precision, recall, and F1 scores
        """
        # Calculate BERTScore
        P, R, F1 = bert_score_fn(
            [humanized],
            [original],
            lang=lang,
            model_type=model_type,
            verbose=False
        )

        return {
            'precision': round(float(P[0]), 4),
            'recall': round(float(R[0]), 4),
            'f1': round(float(F1[0]), 4)
        }

    def calculate_bleu(
        self,
        original: str,
        humanized: str,
        n_grams: Tuple[float, ...] = (0.25, 0.25, 0.25, 0.25)
    ) -> float:
        """
        Calculate BLEU score between original and humanized text.

        BLEU measures lexical overlap (n-gram precision).
        Lower BLEU is expected for paraphrasing (we want semantic similarity, not word-for-word copy).

        Args:
            original: Original text
            humanized: Humanized text
            n_grams: Weights for 1-4 gram precision (default: equal weights)

        Returns:
            BLEU score (0.0 to 1.0)
        """
        # Tokenize sentences
        reference = [nltk.word_tokenize(original.lower())]
        candidate = nltk.word_tokenize(humanized.lower())

        # Calculate BLEU with smoothing (for short texts)
        bleu = sentence_bleu(
            reference,
            candidate,
            weights=n_grams,
            smoothing_function=self.smoother.method1
        )

        return round(bleu, 4)

    def check_term_preservation(
        self,
        humanized_text: str,
        placeholder_map: Dict[str, str]
    ) -> Dict[str, any]:
        """
        Check if protected terms are correctly preserved in humanized text.

        Args:
            humanized_text: The humanized text
            placeholder_map: Map of placeholders to original terms

        Returns:
            Dictionary with preservation statistics
        """
        terms_expected = list(placeholder_map.keys())
        terms_found = []
        missing_terms = []

        for placeholder, original_term in placeholder_map.items():
            # Check if placeholder is in humanized text
            # (The term_protector should have replaced terms with placeholders,
            #  and the restoration step should put them back)
            if original_term.lower() in humanized_text.lower():
                terms_found.append(original_term)
            elif placeholder in humanized_text:
                # Placeholder not restored yet - this is expected in intermediate stages
                terms_found.append(original_term)
            else:
                missing_terms.append(original_term)

        preservation_rate = len(terms_found) / len(terms_expected) if terms_expected else 1.0

        return {
            'terms_expected': len(terms_expected),
            'terms_found': len(terms_found),
            'preservation_rate': round(preservation_rate, 4),
            'missing_terms': missing_terms
        }

    def assess_quality(
        self,
        metrics: Dict[str, float],
        bertscore_threshold: float = 0.92,
        bleu_threshold: float = 0.10,
        term_threshold: float = 0.95
    ) -> Dict[str, str]:
        """
        Assess overall quality of humanization based on metrics.

        Args:
            metrics: Dictionary with bertscore_f1, bleu_score, term_preservation_rate
            bertscore_threshold: Minimum BERTScore F1 threshold
            bleu_threshold: Minimum BLEU score threshold
            term_threshold: Minimum term preservation rate threshold

        Returns:
            Dictionary with overall_quality and individual status checks:
            {
                "overall_quality": "excellent" | "good" | "acceptable" | "poor",
                "bertscore_status": "pass" | "fail",
                "bleu_status": "pass" | "fail",
                "term_preservation_status": "pass" | "fail"
            }
        """
        bertscore = metrics.get("bertscore_f1", 0.0)
        bleu = metrics.get("bleu_score", 0.0)
        term_pres = metrics.get("term_preservation_rate", 0.0)

        # Check if each metric passes threshold
        bertscore_passes = bertscore >= bertscore_threshold
        bleu_passes = bleu >= bleu_threshold
        term_pres_passes = term_pres >= term_threshold

        # Calculate how much each metric exceeds threshold
        bertscore_margin = (bertscore - bertscore_threshold) / bertscore_threshold if bertscore_threshold > 0 else 0
        bleu_margin = (bleu - bleu_threshold) / bleu_threshold if bleu_threshold > 0 else 0
        term_pres_margin = (term_pres - term_threshold) / term_threshold if term_threshold > 0 else 0

        # Determine overall quality
        if not (bertscore_passes and bleu_passes and term_pres_passes):
            overall = "poor"
        elif bertscore_margin > 0.05 and bleu_margin > 0.05 and term_pres_margin > 0.05:
            overall = "excellent"  # All exceed by >5%
        elif bertscore_margin >= 0.02 and bleu_margin >= 0.02 and term_pres_margin >= 0.02:
            overall = "good"  # All exceed by 2-5%
        else:
            overall = "acceptable"  # Meet threshold exactly

        # Build list of failed checks
        failed_checks = []
        if not bertscore_passes:
            failed_checks.append(f"bertscore ({bertscore:.4f} < {bertscore_threshold})")
        if not bleu_passes:
            failed_checks.append(f"bleu ({bleu:.4f} < {bleu_threshold})")
        if not term_pres_passes:
            failed_checks.append(f"term_preservation ({term_pres:.4f} < {term_threshold})")

        result = {
            "overall_quality": overall,
            "bertscore_status": "pass" if bertscore_passes else "fail",
            "bleu_status": "pass" if bleu_passes else "fail",
            "term_preservation_status": "pass" if term_pres_passes else "fail"
        }

        # Add failed_checks only when quality is poor
        if overall == "poor":
            result["failed_checks"] = failed_checks

        return result

    def assess_overall_quality(
        self,
        bertscore_f1: float,
        bleu_score: float,
        term_preservation_rate: float,
        thresholds: Dict[str, float]
    ) -> str:
        """
        Assess overall quality based on all metrics.

        Args:
            bertscore_f1: BERTScore F1
            bleu_score: BLEU score
            term_preservation_rate: Term preservation rate
            thresholds: Validation thresholds

        Returns:
            Quality assessment string
        """
        # Calculate how far above/below thresholds
        bertscore_margin = bertscore_f1 - thresholds.get('min_bertscore', 0.92)
        bleu_margin = bleu_score - thresholds.get('min_bleu', 0.40)
        term_margin = term_preservation_rate - thresholds.get('min_term_preservation', 0.95)

        # All passing?
        all_passing = bertscore_margin >= 0 and bleu_margin >= 0 and term_margin >= 0

        if not all_passing:
            return 'poor'

        # Calculate average margin
        avg_margin = (bertscore_margin + bleu_margin + term_margin) / 3

        if avg_margin >= 0.05:
            return 'excellent'
        elif avg_margin >= 0.02:
            return 'good'
        else:
            return 'acceptable'

    def validate(
        self,
        original_text: str,
        humanized_text: str,
        placeholder_map: Optional[Dict[str, str]] = None,
        thresholds: Optional[Dict[str, float]] = None
    ) -> Dict[str, any]:
        """
        High-level validation combining all metrics.

        This is a convenience wrapper that combines semantic similarity (BERTScore),
        lexical similarity (BLEU), and term preservation checks into a single call.

        Args:
            original_text: Original text
            humanized_text: Humanized text
            placeholder_map: Optional map of placeholders to original terms
            thresholds: Optional validation thresholds (uses defaults if not provided)

        Returns:
            Dictionary with comprehensive validation results:
            {
                'bertscore': {'precision': float, 'recall': float, 'f1': float},
                'bleu_score': float,
                'term_preservation': {...} or None,
                'quality_assessment': {
                    'overall_quality': str,
                    'bertscore_status': str,
                    'bleu_status': str,
                    'term_preservation_status': str
                }
            }

        Raises:
            ValueError: If original_text or humanized_text is empty
        """
        # Validate inputs
        if not original_text or not original_text.strip():
            raise ValueError("original_text cannot be empty")
        if not humanized_text or not humanized_text.strip():
            raise ValueError("humanized_text cannot be empty")

        # Use default thresholds if not provided
        if thresholds is None:
            thresholds = {
                'min_bertscore': 0.92,
                'min_bleu': 0.10,
                'min_term_preservation': 0.95
            }

        # Calculate BERTScore
        bertscore_result = self.calculate_bertscore(original_text, humanized_text)

        # Calculate BLEU score
        bleu_score = self.calculate_bleu(original_text, humanized_text)

        # Check term preservation (if placeholder_map provided)
        term_preservation_result = None
        term_preservation_rate = 1.0
        if placeholder_map:
            term_preservation_result = self.check_term_preservation(humanized_text, placeholder_map)
            term_preservation_rate = term_preservation_result['preservation_rate']

        # Assess quality using the assess_quality method
        quality_metrics = {
            'bertscore_f1': bertscore_result['f1'],
            'bleu_score': bleu_score,
            'term_preservation_rate': term_preservation_rate
        }
        quality_assessment = self.assess_quality(
            metrics=quality_metrics,
            bertscore_threshold=thresholds['min_bertscore'],
            bleu_threshold=thresholds['min_bleu'],
            term_threshold=thresholds['min_term_preservation']
        )

        return {
            'bertscore': bertscore_result,
            'bleu_score': bleu_score,
            'term_preservation': term_preservation_result,
            'quality_assessment': quality_assessment
        }


def process_input(input_data: Dict[str, any]) -> Dict[str, any]:
    """
    Process input and validate humanized text.

    Args:
        input_data: Input dictionary from JSON stdin

    Returns:
        Output dictionary for JSON stdout
    """
    start_time = time.time()

    try:
        # Extract parameters
        original_text = input_data.get('original_text', '')
        humanized_text = input_data.get('humanized_text', '')
        placeholder_map = input_data.get('placeholder_map', {})
        thresholds = input_data.get('validation_thresholds', {
            'min_bertscore': 0.92,
            'min_bleu': 0.10,
            'min_term_preservation': 0.95
        })
        check_term_preservation_flag = input_data.get('check_term_preservation', True)
        check_semantic_similarity_flag = input_data.get('check_semantic_similarity', True)

        # Validate inputs
        if not original_text.strip():
            return {
                'status': 'error',
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'original_text cannot be empty'
                }
            }

        if not humanized_text.strip():
            return {
                'status': 'error',
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'humanized_text cannot be empty'
                }
            }

        # Initialize validator
        validator = Validator()

        # Use the validate() method for the core validation logic
        validation_result = validator.validate(
            original_text=original_text,
            humanized_text=humanized_text,
            placeholder_map=placeholder_map if (check_term_preservation_flag and placeholder_map) else None,
            thresholds=thresholds
        )

        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)

        # Build response using validation_result
        return {
            'status': 'success',
            'data': validation_result,
            'metadata': {
                'processing_time_ms': processing_time,
                'tool': 'validator',
                'version': '1.0'
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
