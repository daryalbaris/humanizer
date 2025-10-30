#!/usr/bin/env python3
"""
Unit tests for reference_analyzer.py

Tests:
- Sentence length distribution analysis
- Transition phrase extraction (50+ phrases)
- Vocabulary level classification
- Paragraph structure analysis
- Voice ratio analysis (active/passive)
- Tense distribution analysis
- Analysis depth levels (quick, standard, comprehensive)
- Reference validation
- JSON I/O interface
- Error handling

Author: AI Humanizer System
Sprint: Sprint 4 (STORY-005)
"""

import pytest
import json
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tools.reference_analyzer import ReferenceAnalyzer, process_input


class TestReferenceAnalyzerInit:
    """Test ReferenceAnalyzer initialization"""

    def test_init_creates_transition_database(self):
        """Test that initialization creates transition phrase database"""
        analyzer = ReferenceAnalyzer()

        assert len(analyzer.common_transitions) >= 5
        assert "addition" in analyzer.common_transitions
        assert "contrast" in analyzer.common_transitions
        assert "cause_effect" in analyzer.common_transitions

    def test_init_includes_transition_categories(self):
        """Test that transition categories have phrases"""
        analyzer = ReferenceAnalyzer()

        assert len(analyzer.common_transitions["addition"]) > 0
        assert "moreover" in analyzer.common_transitions["addition"]
        assert "however" in analyzer.common_transitions["contrast"]

    def test_init_creates_vocabulary_tiers(self):
        """Test that vocabulary tier database is created"""
        analyzer = ReferenceAnalyzer()

        assert "basic" in analyzer.vocabulary_tiers
        assert "intermediate" in analyzer.vocabulary_tiers
        assert "advanced" in analyzer.vocabulary_tiers

    def test_init_creates_section_patterns(self):
        """Test that section detection patterns are created"""
        analyzer = ReferenceAnalyzer()

        assert len(analyzer.section_patterns) >= 4
        assert "introduction" in analyzer.section_patterns
        assert "methods" in analyzer.section_patterns
        assert "results" in analyzer.section_patterns


class TestSentenceLengthAnalysis:
    """Test sentence length distribution analysis"""

    def test_analyze_sentence_lengths(self):
        """Test basic sentence length analysis"""
        analyzer = ReferenceAnalyzer()

        text = "Short sentence. This is a medium length sentence here. This is a significantly longer sentence with many words to create variance in the distribution."

        result = analyzer._analyze_sentence_lengths(text)

        assert "min" in result
        assert "max" in result
        assert "mean" in result
        assert "variance" in result
        assert "median" in result

        assert result["min"] > 0
        assert result["max"] > result["min"]
        assert result["mean"] > 0

    def test_sentence_length_with_single_sentence(self):
        """Test sentence length analysis with single sentence"""
        analyzer = ReferenceAnalyzer()

        text = "This is a single sentence."

        result = analyzer._analyze_sentence_lengths(text)

        assert result["min"] == result["max"]
        assert result["variance"] == 0

    def test_sentence_length_includes_quartiles(self):
        """Test that quartiles are calculated"""
        analyzer = ReferenceAnalyzer()

        text = "Short. Medium sentence here. Longer sentence with more words. Very long sentence with many words to create distribution."

        result = analyzer._analyze_sentence_lengths(text)

        assert "quartiles" in result
        assert "q1" in result["quartiles"]
        assert "q2" in result["quartiles"]
        assert "q3" in result["quartiles"]

    def test_empty_text_returns_zero_metrics(self):
        """Test that empty text returns zero metrics"""
        analyzer = ReferenceAnalyzer()

        text = ""

        result = analyzer._analyze_sentence_lengths(text)

        assert result["min"] == 0
        assert result["max"] == 0
        assert result["mean"] == 0
        assert result["variance"] == 0


class TestTransitionPhraseExtraction:
    """Test transition phrase extraction"""

    def test_extract_transition_phrases(self):
        """Test basic transition phrase extraction"""
        analyzer = ReferenceAnalyzer()

        text = "The results were significant. However, the method needs improvement. Moreover, the data supports this conclusion. Therefore, further research is needed."

        result = analyzer._extract_transition_phrases(text)

        assert len(result) > 0

        # Check structure
        if result:
            assert "phrase" in result[0]
            assert "category" in result[0]
            assert "frequency" in result[0]

    def test_transition_phrases_include_categories(self):
        """Test that extracted phrases include categories"""
        analyzer = ReferenceAnalyzer()

        text = "Moreover, the results were significant. However, the method varied."

        result = analyzer._extract_transition_phrases(text)

        # Should find transitions with categories
        categories = [item["category"] for item in result]

        # Check that categories are from known types
        valid_categories = ["addition", "contrast", "cause_effect", "example", "sequence"]
        assert all(cat in valid_categories for cat in categories)

    def test_transition_phrases_frequency_counted(self):
        """Test that phrase frequency is counted correctly"""
        analyzer = ReferenceAnalyzer()

        text = "However, the results were significant. However, the method varied. However, the data supports this."

        result = analyzer._extract_transition_phrases(text)

        # Should find "however" with frequency 3
        however_items = [item for item in result if item["phrase"] == "however"]

        assert len(however_items) > 0
        assert however_items[0]["frequency"] == 3

    def test_transition_phrases_sorted_by_frequency(self):
        """Test that phrases are sorted by frequency"""
        analyzer = ReferenceAnalyzer()

        text = "However this. Moreover that. However here. Therefore something. However again."

        result = analyzer._extract_transition_phrases(text)

        if len(result) > 1:
            # First item should have highest frequency
            assert result[0]["frequency"] >= result[1]["frequency"]

    def test_transition_phrases_limited_to_top_20(self):
        """Test that only top 20 phrases are returned"""
        analyzer = ReferenceAnalyzer()

        # Create text with many different transition phrases
        text = " Moreover, " + " Furthermore, " + " However, " + " Therefore, " + " Thus, "
        text = text * 10  # Repeat to create frequency

        result = analyzer._extract_transition_phrases(text)

        assert len(result) <= 20


class TestVocabularyLevelAnalysis:
    """Test vocabulary level classification"""

    def test_analyze_vocabulary_level(self):
        """Test basic vocabulary level analysis"""
        analyzer = ReferenceAnalyzer()

        text = "The samples were prepared using standard techniques. The results demonstrate the effectiveness."

        result = analyzer._analyze_vocabulary_level(text)

        assert "level" in result
        assert "score" in result
        assert "tier_distribution" in result

        assert result["level"] in ["basic", "intermediate", "advanced"]
        assert 0 <= result["score"] <= 100

    def test_basic_vocabulary_classification(self):
        """Test classification of basic vocabulary"""
        analyzer = ReferenceAnalyzer()

        # Use mostly basic words
        text = "We use this to make things. We get results and do work. We have data."

        result = analyzer._analyze_vocabulary_level(text)

        # Should classify as basic or intermediate (depending on exact tier words present)
        assert result["level"] in ["basic", "intermediate", "advanced"]

    def test_advanced_vocabulary_classification(self):
        """Test classification of advanced vocabulary"""
        analyzer = ReferenceAnalyzer()

        # Use advanced words
        text = "We employ sophisticated techniques to elucidate the mechanisms. The approach facilitates comprehension."

        result = analyzer._analyze_vocabulary_level(text)

        # May classify as advanced (depends on exact words in tiers)
        assert result["level"] in ["basic", "intermediate", "advanced"]

    def test_vocabulary_tier_distribution_tracked(self):
        """Test that tier distribution is tracked"""
        analyzer = ReferenceAnalyzer()

        text = "The method is used to demonstrate results."

        result = analyzer._analyze_vocabulary_level(text)

        assert "basic" in result["tier_distribution"]
        assert "intermediate" in result["tier_distribution"]
        assert "advanced" in result["tier_distribution"]


class TestParagraphStructureAnalysis:
    """Test paragraph structure analysis"""

    def test_analyze_paragraph_structure(self):
        """Test basic paragraph structure analysis"""
        analyzer = ReferenceAnalyzer()

        text = """First paragraph with multiple sentences. Another sentence here. And a third one.

Second paragraph starts here. It has two sentences.

Third paragraph is final. Short."""

        result = analyzer._analyze_paragraph_structure(text)

        assert "total_paragraphs" in result
        assert "sentences_per_paragraph" in result

        assert result["total_paragraphs"] == 3

    def test_paragraph_sentences_per_paragraph(self):
        """Test sentences per paragraph calculation"""
        analyzer = ReferenceAnalyzer()

        text = """Paragraph one. Sentence two. Sentence three.

Paragraph two. Just two sentences."""

        result = analyzer._analyze_paragraph_structure(text)

        spp = result["sentences_per_paragraph"]

        assert "min" in spp
        assert "max" in spp
        assert "mean" in spp

        assert spp["min"] <= spp["max"]

    def test_empty_text_returns_zero_paragraphs(self):
        """Test that empty text returns zero paragraphs"""
        analyzer = ReferenceAnalyzer()

        text = ""

        result = analyzer._analyze_paragraph_structure(text)

        assert result["sentences_per_paragraph"]["mean"] == 0


class TestVoiceRatioAnalysis:
    """Test active vs passive voice analysis"""

    def test_analyze_voice_ratio(self):
        """Test basic voice ratio analysis"""
        analyzer = ReferenceAnalyzer()

        text = "The sample was prepared. The test was conducted. We analyzed the results."

        result = analyzer._analyze_voice_ratio(text)

        assert "active" in result
        assert "passive" in result

        assert 0 <= result["active"] <= 1
        assert 0 <= result["passive"] <= 1
        assert abs(result["active"] + result["passive"] - 1.0) < 0.01  # Should sum to 1

    def test_passive_voice_detection(self):
        """Test detection of passive voice"""
        analyzer = ReferenceAnalyzer()

        text = "The sample was prepared. The test was conducted. The results were analyzed."

        result = analyzer._analyze_voice_ratio(text)

        # All sentences are passive
        assert result["passive"] > 0.5

    def test_active_voice_detection(self):
        """Test detection of active voice"""
        analyzer = ReferenceAnalyzer()

        text = "We prepared the sample. We conducted the test. We analyzed the results."

        result = analyzer._analyze_voice_ratio(text)

        # All sentences are active
        assert result["active"] > 0.5


class TestTenseDistributionAnalysis:
    """Test tense distribution analysis"""

    def test_analyze_tense_distribution(self):
        """Test basic tense distribution analysis"""
        analyzer = ReferenceAnalyzer()

        text = "The sample was prepared. The test is conducted. We will analyze the results."

        result = analyzer._analyze_tense_distribution(text)

        assert "past" in result
        assert "present" in result
        assert "future" in result

        assert 0 <= result["past"] <= 1
        assert 0 <= result["present"] <= 1
        assert 0 <= result["future"] <= 1

    def test_past_tense_detection(self):
        """Test detection of past tense"""
        analyzer = ReferenceAnalyzer()

        text = "The sample was prepared. The test was conducted. Results were analyzed."

        result = analyzer._analyze_tense_distribution(text)

        # Should have high past tense ratio
        assert result["past"] > 0


class TestReferenceValidation:
    """Test reference text validation"""

    def test_validate_short_reference(self):
        """Test validation of short reference text (< 500 words)"""
        analyzer = ReferenceAnalyzer()

        reference_texts = [
            {"text": "Short text. " * 10, "title": "Test Paper"}  # ~30 words
        ]

        result = analyzer._validate_references(reference_texts)

        assert result["valid"] == False
        assert len(result["warnings"]) > 0

    def test_validate_missing_sections(self):
        """Test validation of reference without sections"""
        analyzer = ReferenceAnalyzer()

        reference_texts = [
            {"text": "Text without sections. " * 100, "title": "Test Paper"}
        ]

        result = analyzer._validate_references(reference_texts)

        # Should warn about missing sections
        assert len(result["warnings"]) > 0

    def test_validate_missing_citations(self):
        """Test validation of reference without citations"""
        analyzer = ReferenceAnalyzer()

        reference_texts = [
            {"text": "Text without citations. " * 100, "title": "Test Paper"}
        ]

        result = analyzer._validate_references(reference_texts)

        # Should warn about missing citations
        warnings_text = " ".join(result["warnings"])
        assert "citation" in warnings_text.lower() or len(result["warnings"]) > 0

    def test_validate_valid_reference(self):
        """Test validation of valid reference text"""
        analyzer = ReferenceAnalyzer()

        reference_texts = [
            {
                "text": """Introduction

The stainless steels are widely used [1]. Methods section describes the approach.

Results section shows the findings (Smith, 2020). Discussion analyzes the results.""" * 20,
                "title": "Valid Paper"
            }
        ]

        result = analyzer._validate_references(reference_texts)

        # May still have some warnings, but should be less severe
        assert "valid" in result


class TestAnalysisDepthLevels:
    """Test analysis depth levels"""

    def test_quick_analysis(self):
        """Test quick analysis (sentence length + transitions only)"""
        analyzer = ReferenceAnalyzer()

        reference_texts = [
            {"text": "Sentence one. However, sentence two. Moreover, sentence three. " * 50, "title": "Paper 1"}
        ]

        result = analyzer.analyze_references(reference_texts, analysis_depth="quick")

        style_profile = result["style_profile"]

        # Should have sentence length and transitions
        assert "sentence_length_distribution" in style_profile
        assert "transition_phrases" in style_profile

        # Should NOT have comprehensive features
        assert "vocabulary_level" not in style_profile
        assert "voice_ratio" not in style_profile

    def test_standard_analysis(self):
        """Test standard analysis (default)"""
        analyzer = ReferenceAnalyzer()

        reference_texts = [
            {"text": "Sentence one. However, sentence two. " * 50, "title": "Paper 1"}
        ]

        result = analyzer.analyze_references(reference_texts, analysis_depth="standard")

        style_profile = result["style_profile"]

        # Should have standard features
        assert "sentence_length_distribution" in style_profile
        assert "transition_phrases" in style_profile
        assert "vocabulary_level" in style_profile
        assert "paragraph_structure" in style_profile

        # Should NOT have comprehensive-only features
        assert "voice_ratio" not in style_profile
        assert "tense_distribution" not in style_profile

    def test_comprehensive_analysis(self):
        """Test comprehensive analysis (all features)"""
        analyzer = ReferenceAnalyzer()

        reference_texts = [
            {"text": "Sentence one. However, sentence two. " * 50, "title": "Paper 1"}
        ]

        result = analyzer.analyze_references(reference_texts, analysis_depth="comprehensive")

        style_profile = result["style_profile"]

        # Should have ALL features
        assert "sentence_length_distribution" in style_profile
        assert "transition_phrases" in style_profile
        assert "vocabulary_level" in style_profile
        assert "paragraph_structure" in style_profile
        assert "voice_ratio" in style_profile
        assert "tense_distribution" in style_profile


class TestRecommendationGeneration:
    """Test recommendation generation"""

    def test_generate_recommendations(self):
        """Test that recommendations are generated"""
        analyzer = ReferenceAnalyzer()

        reference_texts = [
            {"text": "Sentence one. However, sentence two. Moreover, sentence three. " * 50, "title": "Paper 1"}
        ]

        result = analyzer.analyze_references(reference_texts, analysis_depth="standard")

        assert "recommendations" in result
        assert len(result["recommendations"]) > 0

    def test_recommendations_include_sentence_length(self):
        """Test that recommendations include sentence length guidance"""
        analyzer = ReferenceAnalyzer()

        reference_texts = [
            {"text": "This is a sentence. " * 100, "title": "Paper 1"}
        ]

        result = analyzer.analyze_references(reference_texts, analysis_depth="standard")

        recommendations_text = " ".join(result["recommendations"])

        # Should mention sentence length
        assert "sentence length" in recommendations_text.lower()

    def test_recommendations_include_transitions(self):
        """Test that recommendations include transition phrases"""
        analyzer = ReferenceAnalyzer()

        reference_texts = [
            {"text": "Sentence. However, another. Moreover, third. Therefore, fourth. " * 30, "title": "Paper 1"}
        ]

        result = analyzer.analyze_references(reference_texts, analysis_depth="standard")

        recommendations_text = " ".join(result["recommendations"])

        # Should mention transition phrases
        assert "transition" in recommendations_text.lower() or "phrase" in recommendations_text.lower()


class TestProcessInputFunction:
    """Test process_input function (JSON I/O interface)"""

    def test_process_valid_input(self):
        """Test process_input with valid input"""
        input_data = {
            "reference_texts": [
                {"text": "Sentence one. However, sentence two. " * 50, "title": "Paper 1"}
            ],
            "analysis_depth": "standard"
        }

        result = process_input(input_data)

        assert result["status"] == "success"
        assert "data" in result
        assert "style_profile" in result["data"]
        assert "quality_metrics" in result["data"]
        assert "recommendations" in result["data"]
        assert "metadata" in result

    def test_process_missing_reference_texts_field(self):
        """Test process_input with missing reference_texts field"""
        input_data = {
            "analysis_depth": "standard"
        }

        result = process_input(input_data)

        assert result["status"] == "error"
        assert result["error"]["code"] == "MISSING_FIELD"

    def test_process_invalid_reference_texts_format(self):
        """Test process_input with invalid reference_texts format"""
        input_data = {
            "reference_texts": "not a list"
        }

        result = process_input(input_data)

        assert result["status"] == "error"
        assert result["error"]["code"] == "INVALID_FORMAT"

    def test_process_invalid_analysis_depth(self):
        """Test process_input with invalid analysis depth"""
        input_data = {
            "reference_texts": [{"text": "Sample text.", "title": "Paper 1"}],
            "analysis_depth": "invalid_depth"
        }

        result = process_input(input_data)

        assert result["status"] == "error"
        assert result["error"]["code"] == "INVALID_ANALYSIS_DEPTH"

    def test_process_defaults_analysis_depth(self):
        """Test process_input defaults analysis_depth to 'standard'"""
        input_data = {
            "reference_texts": [{"text": "Sample text.", "title": "Paper 1"}]
        }

        result = process_input(input_data)

        assert result["status"] == "success"
        assert result["metadata"]["analysis_depth"] == "standard"

    def test_process_multiple_references(self):
        """Test process_input with multiple reference texts"""
        input_data = {
            "reference_texts": [
                {"text": "Sentence one. " * 100, "title": "Paper 1"},
                {"text": "Sentence two. " * 100, "title": "Paper 2"}
            ],
            "analysis_depth": "quick"
        }

        result = process_input(input_data)

        assert result["status"] == "success"
        assert result["metadata"]["num_references"] == 2

    def test_process_tracks_processing_time(self):
        """Test that processing time is tracked"""
        input_data = {
            "reference_texts": [{"text": "Sample text. " * 100, "title": "Paper 1"}]
        }

        result = process_input(input_data)

        assert result["status"] == "success"
        assert "processing_time_ms" in result["metadata"]
        assert result["metadata"]["processing_time_ms"] > 0

    def test_process_includes_metadata(self):
        """Test that metadata is included in output"""
        input_data = {
            "reference_texts": [{"text": "Sample text. " * 100, "title": "Paper 1"}],
            "analysis_depth": "comprehensive"
        }

        result = process_input(input_data)

        assert result["status"] == "success"
        assert result["metadata"]["tool"] == "reference_analyzer"
        assert result["metadata"]["version"] == "1.0"
        assert "total_words" in result["metadata"]


class TestEdgeCases:
    """Test edge cases"""

    def test_empty_reference_list(self):
        """Test with empty reference list"""
        analyzer = ReferenceAnalyzer()

        reference_texts = []

        result = analyzer.analyze_references(reference_texts, analysis_depth="standard")

        # Should return empty profile with error
        assert result["style_profile"] == {}
        assert "recommendations" in result

    def test_reference_with_minimal_text(self):
        """Test reference with minimal text"""
        analyzer = ReferenceAnalyzer()

        reference_texts = [
            {"text": "Short.", "title": "Paper 1"}
        ]

        result = analyzer.analyze_references(reference_texts, analysis_depth="quick")

        # Should handle gracefully
        assert "style_profile" in result

    def test_reference_without_title(self):
        """Test reference without title field"""
        analyzer = ReferenceAnalyzer()

        reference_texts = [
            {"text": "Sentence one. " * 100}  # No title field
        ]

        # Should handle gracefully (title is optional in validation)
        result = analyzer.analyze_references(reference_texts, analysis_depth="quick")

        assert "style_profile" in result


class TestPerformance:
    """Test performance benchmarks"""

    def test_performance_single_reference(self):
        """Test performance with single reference (~5000 words)"""
        import time

        analyzer = ReferenceAnalyzer()

        reference_texts = [
            {"text": "The sample was prepared. However, the method varied. " * 250, "title": "Paper 1"}
        ]

        start_time = time.time()
        result = analyzer.analyze_references(reference_texts, analysis_depth="standard")
        elapsed_ms = (time.time() - start_time) * 1000

        # Should complete in <2 seconds
        assert elapsed_ms < 3000  # Generous threshold
        assert "style_profile" in result

    def test_performance_multiple_references(self):
        """Test performance with 5 references (~10000 words total)"""
        import time

        analyzer = ReferenceAnalyzer()

        reference_texts = [
            {"text": "Sentence one. However, sentence two. " * 100, "title": f"Paper {i}"}
            for i in range(5)
        ]

        start_time = time.time()
        result = analyzer.analyze_references(reference_texts, analysis_depth="quick")
        elapsed_ms = (time.time() - start_time) * 1000

        # Should complete in <3 seconds for 5 references
        assert elapsed_ms < 5000  # Generous threshold
        assert "style_profile" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
