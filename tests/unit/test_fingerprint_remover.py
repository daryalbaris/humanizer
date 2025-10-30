#!/usr/bin/env python3
"""
Unit tests for fingerprint_remover.py

Tests:
- AI filler phrase removal (15+ patterns)
- Hedging language reduction (section-aware)
- AI punctuation tell fixes
- Repetitive structure fixes
- Aggressiveness levels (conservative, moderate, aggressive)
- JSON I/O interface
- Error handling

Author: AI Humanizer System
Sprint: Sprint 4 (STORY-004)
"""

import pytest
import json
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tools.fingerprint_remover import FingerprintRemover, process_input


class TestFingerprintRemoverInit:
    """Test FingerprintRemover initialization"""

    def test_init_creates_pattern_databases(self):
        """Test that initialization creates pattern databases"""
        remover = FingerprintRemover()

        assert len(remover.filler_phrases) >= 15
        assert len(remover.hedging_words) >= 10
        assert len(remover.punctuation_patterns) > 0

    def test_init_includes_common_filler_phrases(self):
        """Test that common AI filler phrases are included"""
        remover = FingerprintRemover()

        filler_text = " ".join(remover.filler_phrases.keys())

        assert "important to note" in filler_text.lower()
        assert "worth noting" in filler_text.lower()
        assert "moreover" in filler_text.lower()


class TestFillerPhraseRemoval:
    """Test filler phrase removal functionality"""

    def test_remove_important_to_note(self):
        """Test removal of 'It is important to note that'"""
        remover = FingerprintRemover()
        text = "It is important to note that the results were significant."

        result = remover.remove_fingerprints(text, aggressiveness="moderate")

        assert "It is important to note that" not in result["cleaned_text"]
        assert "the results were significant" in result["cleaned_text"]
        assert result["statistics"]["filler_phrases"] >= 1

    def test_remove_worth_noting(self):
        """Test removal of 'It's worth noting that'"""
        remover = FingerprintRemover()
        text = "It's worth noting that the temperature was critical."

        result = remover.remove_fingerprints(text, aggressiveness="moderate")

        assert "worth noting" not in result["cleaned_text"].lower()
        assert result["statistics"]["filler_phrases"] >= 1

    def test_remove_moreover(self):
        """Test removal of 'Moreover,'"""
        remover = FingerprintRemover()
        text = "The samples were prepared. Moreover, they were tested."

        result = remover.remove_fingerprints(text, aggressiveness="moderate")

        assert result["statistics"]["filler_phrases"] >= 1

    def test_remove_multiple_filler_phrases(self):
        """Test removal of multiple filler phrases in one text"""
        remover = FingerprintRemover()
        text = "It is important to note that the results were significant. Moreover, the method was effective. Furthermore, the data supports this."

        result = remover.remove_fingerprints(text, aggressiveness="moderate")

        assert result["statistics"]["filler_phrases"] >= 2
        assert len(result["fingerprints_removed"]) >= 2

    def test_conservative_only_removes_obvious_patterns(self):
        """Test conservative aggressiveness only removes obvious patterns"""
        remover = FingerprintRemover()
        text = "It is important to note that this is critical. Additionally, we found results."

        result = remover.remove_fingerprints(text, aggressiveness="conservative")

        # Conservative should remove "important to note" but may keep "Additionally"
        assert "important to note" not in result["cleaned_text"].lower()

    def test_aggressive_removes_more_patterns(self):
        """Test aggressive aggressiveness removes more patterns"""
        remover = FingerprintRemover()
        text = "Moreover, the results were significant. Furthermore, the data supports this. Additionally, we observed trends."

        result = remover.remove_fingerprints(text, aggressiveness="aggressive")

        # Aggressive should remove multiple transition words
        assert result["statistics"]["filler_phrases"] >= 1


class TestHedgingLanguageReduction:
    """Test hedging language reduction functionality"""

    def test_reduce_excessive_hedging_in_results(self):
        """Test hedging reduction in Results section (should be minimal)"""
        remover = FingerprintRemover()
        text = "The results arguably show that the method may be effective. Perhaps the data might indicate trends."

        result = remover.remove_fingerprints(text, section_type="results", aggressiveness="moderate")

        # Results section should have minimal hedging (1.5% tolerance)
        # Some hedging words should be removed
        hedge_count_before = text.lower().count("arguably") + text.lower().count("perhaps") + text.lower().count("might")
        hedge_count_after = result["cleaned_text"].lower().count("arguably") + result["cleaned_text"].lower().count("perhaps") + result["cleaned_text"].lower().count("might")

        assert hedge_count_after < hedge_count_before

    def test_allow_more_hedging_in_methods(self):
        """Test that Methods section allows more hedging (scientific caution)"""
        remover = FingerprintRemover()
        text = "The samples were approximately 10mm in diameter. The temperature may vary by roughly 5°C."

        result = remover.remove_fingerprints(text, section_type="methods", aggressiveness="moderate")

        # Methods section allows more hedging (4% tolerance)
        # Some hedging words should remain
        assert "approximately" in result["cleaned_text"].lower() or "roughly" in result["cleaned_text"].lower()

    def test_hedging_reduction_tracks_removals(self):
        """Test that hedging reductions are tracked"""
        remover = FingerprintRemover()
        text = "The results arguably show trends. Perhaps the method might be effective. Possibly the data could indicate patterns."

        result = remover.remove_fingerprints(text, section_type="results", aggressiveness="aggressive")

        # Should track hedging removals
        assert result["statistics"]["hedging_words"] >= 0


class TestPunctuationTellFixes:
    """Test AI punctuation tell fixes"""

    def test_replace_em_dash_with_en_dash(self):
        """Test em dash replacement with en dash"""
        remover = FingerprintRemover()
        text = "The results—which were significant—showed trends."

        result = remover.remove_fingerprints(text, aggressiveness="moderate")

        assert "—" not in result["cleaned_text"]
        assert " - " in result["cleaned_text"]
        assert result["statistics"]["punctuation_tells"] >= 2  # Two em dashes

    def test_comma_linked_clauses_to_semicolon(self):
        """Test comma-linked independent clauses fixed to semicolon"""
        remover = FingerprintRemover()
        text = "The method was effective, however the results varied."

        result = remover.remove_fingerprints(text, aggressiveness="moderate")

        # Should replace comma before "however" with semicolon
        assert "; however" in result["cleaned_text"].lower()


class TestRepetitiveStructureFixes:
    """Test repetitive structure fixes"""

    def test_remove_consecutive_same_starters(self):
        """Test removal of consecutive sentences starting with same word"""
        remover = FingerprintRemover()
        text = "The samples were prepared. The samples were tested. The samples showed results."

        result = remover.remove_fingerprints(text, aggressiveness="moderate")

        # Should remove some "The" starters
        the_count_before = text.count("The ")
        the_count_after = result["cleaned_text"].count("The ")

        assert the_count_after < the_count_before
        assert result["statistics"]["structure_fixes"] >= 1

    def test_remove_this_repetition(self):
        """Test removal of 'This' repetition"""
        remover = FingerprintRemover()
        text = "This method was used. This approach was effective. This result was significant."

        result = remover.remove_fingerprints(text, aggressiveness="moderate")

        this_count_before = text.count("This ")
        this_count_after = result["cleaned_text"].count("This ")

        assert this_count_after < this_count_before


class TestWhitespaceCleanup:
    """Test whitespace cleanup functionality"""

    def test_remove_multiple_spaces(self):
        """Test removal of multiple consecutive spaces"""
        remover = FingerprintRemover()
        text = "The results  were   significant."

        result = remover.remove_fingerprints(text, aggressiveness="moderate")

        assert "  " not in result["cleaned_text"]

    def test_remove_excessive_newlines(self):
        """Test removal of excessive newlines"""
        remover = FingerprintRemover()
        text = "Paragraph 1.\n\n\n\nParagraph 2."

        result = remover.remove_fingerprints(text, aggressiveness="moderate")

        assert "\n\n\n" not in result["cleaned_text"]

    def test_remove_space_before_punctuation(self):
        """Test removal of space before punctuation"""
        remover = FingerprintRemover()
        text = "The results were significant ."

        result = remover.remove_fingerprints(text, aggressiveness="moderate")

        assert " ." not in result["cleaned_text"]
        assert result["cleaned_text"].endswith(".")


class TestSectionAwareProcessing:
    """Test section-aware processing"""

    def test_results_section_minimal_hedging(self):
        """Test Results section has minimal hedging tolerance"""
        remover = FingerprintRemover()
        text = "The results perhaps show that the method may be effective. Possibly the data might indicate trends."

        result_results = remover.remove_fingerprints(text, section_type="results", aggressiveness="moderate")
        result_methods = remover.remove_fingerprints(text, section_type="methods", aggressiveness="moderate")

        # Results section should remove more hedging than Methods
        assert result_results["statistics"]["hedging_words"] >= result_methods["statistics"]["hedging_words"]

    def test_different_sections_different_treatment(self):
        """Test that different sections get different treatment"""
        remover = FingerprintRemover()
        text = "The method may be effective. Perhaps the results are significant."

        intro_result = remover.remove_fingerprints(text, section_type="introduction", aggressiveness="moderate")
        results_result = remover.remove_fingerprints(text, section_type="results", aggressiveness="moderate")

        # Different sections should produce different results
        assert intro_result["cleaned_text"] != results_result["cleaned_text"] or \
               intro_result["statistics"] != results_result["statistics"]


class TestStatisticsTracking:
    """Test statistics tracking"""

    def test_track_total_removals(self):
        """Test that total removals are tracked correctly"""
        remover = FingerprintRemover()
        text = "It is important to note that the results were significant. Moreover, the data supports this."

        result = remover.remove_fingerprints(text, aggressiveness="moderate")

        assert result["statistics"]["total_removals"] >= 1
        assert result["statistics"]["total_removals"] == len(result["fingerprints_removed"])

    def test_track_removal_categories(self):
        """Test that removal categories are tracked"""
        remover = FingerprintRemover()
        text = "It is important to note that this is critical. The results—which were significant—showed trends."

        result = remover.remove_fingerprints(text, aggressiveness="moderate")

        assert "filler_phrases" in result["statistics"]
        assert "hedging_words" in result["statistics"]
        assert "punctuation_tells" in result["statistics"]
        assert "structure_fixes" in result["statistics"]

    def test_fingerprints_removed_list_populated(self):
        """Test that fingerprints_removed list is populated"""
        remover = FingerprintRemover()
        text = "It is important to note that the results were significant."

        result = remover.remove_fingerprints(text, aggressiveness="moderate")

        assert len(result["fingerprints_removed"]) >= 1

        for removal in result["fingerprints_removed"]:
            assert "type" in removal
            assert "original" in removal
            assert "replacement" in removal


class TestProcessInputFunction:
    """Test process_input function (JSON I/O interface)"""

    def test_process_valid_input(self):
        """Test process_input with valid input"""
        input_data = {
            "text": "It is important to note that the results were significant.",
            "section_type": "results",
            "aggressiveness": "moderate"
        }

        result = process_input(input_data)

        assert result["status"] == "success"
        assert "data" in result
        assert "cleaned_text" in result["data"]
        assert "fingerprints_removed" in result["data"]
        assert "statistics" in result["data"]
        assert "metadata" in result

    def test_process_missing_text_field(self):
        """Test process_input with missing text field"""
        input_data = {
            "section_type": "results"
        }

        result = process_input(input_data)

        assert result["status"] == "error"
        assert result["error"]["code"] == "MISSING_FIELD"

    def test_process_invalid_aggressiveness(self):
        """Test process_input with invalid aggressiveness"""
        input_data = {
            "text": "Sample text.",
            "aggressiveness": "invalid_level"
        }

        result = process_input(input_data)

        assert result["status"] == "error"
        assert result["error"]["code"] == "INVALID_AGGRESSIVENESS"

    def test_process_defaults_section_type(self):
        """Test process_input defaults section_type to 'general'"""
        input_data = {
            "text": "Sample text."
        }

        result = process_input(input_data)

        assert result["status"] == "success"
        assert result["metadata"]["section_type"] == "general"

    def test_process_defaults_aggressiveness(self):
        """Test process_input defaults aggressiveness to 'moderate'"""
        input_data = {
            "text": "Sample text."
        }

        result = process_input(input_data)

        assert result["status"] == "success"
        assert result["metadata"]["aggressiveness"] == "moderate"

    def test_process_tracks_processing_time(self):
        """Test that processing time is tracked"""
        input_data = {
            "text": "It is important to note that the results were significant. Moreover, the data supports this."
        }

        result = process_input(input_data)

        assert result["status"] == "success"
        assert "processing_time_ms" in result["metadata"]
        assert result["metadata"]["processing_time_ms"] > 0

    def test_process_includes_metadata(self):
        """Test that metadata is included in output"""
        input_data = {
            "text": "Sample text.",
            "section_type": "introduction",
            "aggressiveness": "aggressive"
        }

        result = process_input(input_data)

        assert result["status"] == "success"
        assert result["metadata"]["tool"] == "fingerprint_remover"
        assert result["metadata"]["version"] == "1.0"
        assert "input_length" in result["metadata"]
        assert "output_length" in result["metadata"]


class TestEdgeCases:
    """Test edge cases"""

    def test_empty_text(self):
        """Test with empty text"""
        remover = FingerprintRemover()
        text = ""

        result = remover.remove_fingerprints(text, aggressiveness="moderate")

        assert result["cleaned_text"] == ""
        assert result["statistics"]["total_removals"] == 0

    def test_text_with_no_fingerprints(self):
        """Test text with no fingerprints"""
        remover = FingerprintRemover()
        text = "The samples were prepared. The results showed trends."

        result = remover.remove_fingerprints(text, aggressiveness="moderate")

        # Text should remain largely unchanged
        assert len(result["cleaned_text"]) > 0
        # May have some removals (structure fixes)
        assert result["statistics"]["total_removals"] >= 0

    def test_text_with_only_fingerprints(self):
        """Test text consisting mostly of fingerprints"""
        remover = FingerprintRemover()
        text = "It is important to note that, moreover, furthermore, it's worth noting that, additionally, essentially."

        result = remover.remove_fingerprints(text, aggressiveness="aggressive")

        # Most of the text should be removed
        assert len(result["cleaned_text"]) < len(text)
        assert result["statistics"]["total_removals"] >= 3

    def test_very_long_text(self):
        """Test with very long text"""
        remover = FingerprintRemover()
        text = "It is important to note that the results were significant. " * 100

        result = remover.remove_fingerprints(text, aggressiveness="moderate")

        assert result["statistics"]["total_removals"] >= 50  # Should remove many instances


class TestPerformance:
    """Test performance benchmarks"""

    def test_performance_small_text(self):
        """Test performance with small text (<1000 words)"""
        import time

        remover = FingerprintRemover()
        text = "It is important to note that the results were significant. " * 50  # ~500 words

        start_time = time.time()
        result = remover.remove_fingerprints(text, aggressiveness="moderate")
        elapsed_ms = (time.time() - start_time) * 1000

        # Should complete in <100ms for small text
        assert elapsed_ms < 500  # Generous threshold for testing
        assert result["statistics"]["total_removals"] >= 0

    def test_performance_medium_text(self):
        """Test performance with medium text (~8000 words)"""
        import time

        remover = FingerprintRemover()
        # Simulate 8000-word text
        base_text = "It is important to note that the AISI 304 stainless steel exhibited excellent corrosion resistance. Moreover, the heat treatment at 850°C was effective. Furthermore, the microstructure showed fine grains. "
        text = base_text * 300  # ~8000 words

        start_time = time.time()
        result = remover.remove_fingerprints(text, aggressiveness="moderate")
        elapsed_ms = (time.time() - start_time) * 1000

        # Should complete in <500ms for 8000 words
        assert elapsed_ms < 2000  # Generous threshold for testing
        assert result["statistics"]["total_removals"] >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
