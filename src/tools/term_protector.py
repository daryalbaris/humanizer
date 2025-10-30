"""
AI Humanizer System - Term Protector Tool
=========================================

Protects technical terminology by replacing with placeholders before paraphrasing.
Implements 3-tier protection strategy with spaCy-based context analysis.

Input: JSON via stdin (text, glossary_path, options)
Output: JSON via stdout (protected_text, placeholders, statistics)

Protection Tiers:
- Tier 1 (Absolute): Never paraphrase (alloy names, standards, phase names)
- Tier 2 (Context-aware): Paraphrase only if technical meaning preserved
- Tier 3 (Minimal): Free paraphrasing allowed

Additional Protection:
- Numerical values (temperatures, pressures, compositions)
- Equipment specifications (SEM, XRD, TEM, etc.)
- Chemical formulas (Fe₂O₃, M23C6, etc.)
- Standard references (ASTM E8, ISO 6892-1, etc.)

Author: BMAD Development Team
Date: 2025-10-30
Version: 1.0
Sprint: Sprint 2 (STORY-002)
"""

import sys
import json
import re
import time
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional, Set

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import get_logger
from utils.exceptions import (
    ValidationError, ProcessingError, FileNotFoundError as HumanizerFileNotFoundError
)

# Initialize logger
# Note: For tools using stdin/stdout JSON communication, we disable console logging
# to prevent log messages from interfering with JSON output
logger = get_logger(__name__)

# Disable console logging for this tool (only file logging)
import logging
root_logger = logging.getLogger()
# Remove console handlers to prevent interference with JSON stdout
for handler in root_logger.handlers[:]:
    if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
        root_logger.removeHandler(handler)


class TermProtector:
    """
    Protects technical terms using 3-tier protection strategy.

    Uses spaCy for context-aware NLP analysis to distinguish between
    protected technical terms and general language.

    Attributes:
        glossary (dict): Loaded glossary with tier1/tier2/tier3 terms
        nlp: spaCy language model (en_core_web_trf)
        placeholder_counter (int): Counter for generating unique placeholders
        placeholders (dict): Map of placeholder → original term
        protection_map (dict): Categorized list of protected items
    """

    def __init__(self, glossary_path: str):
        """Initialize term protector with glossary.

        Args:
            glossary_path: Path to glossary JSON file

        Raises:
            FileNotFoundError: If glossary file not found
            ValidationError: If glossary format invalid
        """
        self.glossary_path = Path(glossary_path)
        self.glossary = self._load_glossary()
        self.nlp = None  # Lazy load spaCy model
        self.placeholder_counter = 0
        self.placeholders: Dict[str, str] = {}
        self.protection_map: Dict[str, List[str]] = {
            "tier1_terms": [],
            "tier2_terms": [],
            "tier3_terms": [],
            "numbers": [],
            "citations": [],
            "equipment": [],
            "formulas": [],
            "standards": []
        }

    def _load_glossary(self) -> dict:
        """Load and validate glossary JSON file.

        Returns:
            Parsed glossary dictionary

        Raises:
            FileNotFoundError: If glossary not found
            ValidationError: If JSON malformed or missing required fields
        """
        if not self.glossary_path.exists():
            raise HumanizerFileNotFoundError(
                message=f"Glossary file not found: {self.glossary_path}",
                component="term_protector",
                details={
                    "file_path": str(self.glossary_path),
                    "suggested_fix": "Create data/glossary.json with term tiers"
                }
            )

        try:
            with open(self.glossary_path, 'r', encoding='utf-8') as f:
                glossary = json.load(f)

            # Validate required fields
            required_fields = ["tier1", "tier2", "tier3"]
            for field in required_fields:
                if field not in glossary:
                    raise ValidationError(
                        message=f"Glossary missing required field: {field}",
                        component="term_protector",
                        details={"missing_field": field}
                    )

            logger.info(f"Glossary loaded successfully: {len(glossary.get('tier1', {}).get('terms', []))} tier1, "
                       f"{len(glossary.get('tier2', {}).get('terms', []))} tier2, "
                       f"{len(glossary.get('tier3', {}).get('terms', []))} tier3 terms")

            return glossary

        except json.JSONDecodeError as e:
            raise ValidationError(
                message=f"Invalid JSON in glossary file",
                component="term_protector",
                details={"file_path": str(self.glossary_path)},
                original_error=e
            )

    def _load_spacy_model(self):
        """Lazy load spaCy model (only when needed for context analysis).

        Raises:
            ProcessingError: If spaCy model not installed
        """
        if self.nlp is not None:
            return  # Already loaded

        try:
            import spacy
            self.nlp = spacy.load("en_core_web_trf")
            logger.info("spaCy model loaded: en_core_web_trf")
        except ImportError:
            raise ProcessingError(
                message="spaCy library not installed",
                component="term_protector",
                details={"suggested_fix": "pip install spacy"}
            )
        except OSError:
            raise ProcessingError(
                message="spaCy model not found: en_core_web_trf",
                component="term_protector",
                details={"suggested_fix": "python -m spacy download en_core_web_trf"}
            )

    def _generate_placeholder(self, prefix: str) -> str:
        """Generate unique placeholder.

        Args:
            prefix: Placeholder prefix (e.g., "__TERM_", "__NUM_")

        Returns:
            Unique placeholder like "__TERM_001__"
        """
        self.placeholder_counter += 1
        return f"{prefix}{self.placeholder_counter:03d}__"

    def _protect_tier1_terms(self, text: str, prefix: str) -> str:
        """Protect Tier 1 terms (absolute protection - exact match).

        Tier 1 includes:
        - Alloy designations (AISI 304, SAF 2507, Inconel 718)
        - Phase names (austenite, martensite, ferrite)
        - Test methods (Charpy V-notch, Vickers hardness)
        - Standards (ASTM E8, ISO 6892-1)

        Args:
            text: Input text
            prefix: Placeholder prefix

        Returns:
            Text with Tier 1 terms replaced by placeholders
        """
        tier1_terms = self.glossary.get("tier1", {}).get("terms", [])

        # Sort by length (descending) to match longer terms first
        # This prevents "AISI 304" from being matched as "AISI" + "304"
        tier1_terms_sorted = sorted(tier1_terms, key=len, reverse=True)

        for term in tier1_terms_sorted:
            # Case-insensitive exact match with word boundaries
            pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
            matches = list(pattern.finditer(text))

            for match in reversed(matches):  # Reverse to maintain indices
                original = match.group(0)
                placeholder = self._generate_placeholder(prefix)
                self.placeholders[placeholder] = original
                self.protection_map["tier1_terms"].append(original)

                # Replace in text
                text = text[:match.start()] + placeholder + text[match.end():]

        return text

    def _is_technical_context(self, text: str, term: str, position: int) -> bool:
        """Determine if term appears in technical context (for Tier 2).

        Uses spaCy to analyze surrounding context and detect technical usage.

        Args:
            text: Full text
            term: Term to check
            position: Position of term in text

        Returns:
            True if term is in technical context (should be protected)
        """
        # Load spaCy model if not already loaded
        self._load_spacy_model()

        # Extract context window (±50 characters)
        start = max(0, position - 50)
        end = min(len(text), position + len(term) + 50)
        context = text[start:end]

        # Parse with spaCy
        doc = self.nlp(context)

        # Check for technical indicators in context
        technical_indicators = [
            "steel", "alloy", "metal", "phase", "temperature", "pressure",
            "treatment", "testing", "microstructure", "grain", "properties",
            "corrosion", "strength", "hardness", "ductility", "toughness"
        ]

        # Check if term is near technical words
        term_tokens = [token for token in doc if term.lower() in token.text.lower()]

        for token in term_tokens:
            # Check surrounding tokens (±3 words)
            for i in range(max(0, token.i - 3), min(len(doc), token.i + 4)):
                if doc[i].text.lower() in technical_indicators:
                    return True  # Technical context found

                # Check if part of noun phrase with technical terms
                if doc[i].pos_ in ["NOUN", "PROPN"] and any(ind in doc[i].text.lower() for ind in technical_indicators):
                    return True

        return False  # Not in technical context

    def _protect_tier2_terms(self, text: str, prefix: str) -> str:
        """Protect Tier 2 terms (context-aware protection).

        Tier 2 includes:
        - Heat treatment processes (if in metallurgical context)
        - Material properties (if discussing technical specs)
        - Phase transformations (if in materials science context)

        Args:
            text: Input text
            prefix: Placeholder prefix

        Returns:
            Text with Tier 2 terms replaced by placeholders (if in technical context)
        """
        tier2_terms = self.glossary.get("tier2", {}).get("terms", [])
        tier2_terms_sorted = sorted(tier2_terms, key=len, reverse=True)

        for term in tier2_terms_sorted:
            pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
            matches = list(pattern.finditer(text))

            for match in reversed(matches):
                original = match.group(0)

                # Check if in technical context
                if self._is_technical_context(text, term, match.start()):
                    placeholder = self._generate_placeholder(prefix)
                    self.placeholders[placeholder] = original
                    self.protection_map["tier2_terms"].append(original)

                    # Replace in text
                    text = text[:match.start()] + placeholder + text[match.end():]

        return text

    def _protect_tier3_terms(self, text: str, prefix: str) -> str:
        """Protect Tier 3 terms (minimal protection - just for tracking).

        Tier 3 terms can be paraphrased freely, but we track them for statistics.

        Args:
            text: Input text
            prefix: Placeholder prefix (not used, terms not replaced)

        Returns:
            Unchanged text (Tier 3 terms not protected)
        """
        tier3_terms = self.glossary.get("tier3", {}).get("terms", [])

        for term in tier3_terms:
            pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
            matches = list(pattern.finditer(text))

            for match in matches:
                self.protection_map["tier3_terms"].append(match.group(0))

        # Tier 3 terms are NOT replaced (minimal protection)
        return text

    def _protect_numbers(self, text: str, prefix: str) -> str:
        """Protect numerical values (temperatures, pressures, compositions).

        Patterns protected:
        - Temperatures: 850°C, 1000°F, 1273K
        - Pressures: 100 MPa, 1.5 GPa, 50 ksi
        - Compositions: 18Cr-8Ni, Fe-0.4C, 25Cr-7Ni-4Mo-0.27N
        - Percentages: 18.0 wt%, 0.08%, 95.5%
        - Tolerances: 850°C ± 25°C, 18.0 ± 0.5 wt%

        Args:
            text: Input text
            prefix: Placeholder prefix

        Returns:
            Text with numbers replaced by placeholders
        """
        # Temperature patterns
        temp_pattern = r'\d+(?:\.\d+)?(?:\s*±\s*\d+(?:\.\d+)?)?\s*[°]?[CFK]'

        # Pressure patterns
        pressure_pattern = r'\d+(?:\.\d+)?(?:\s*±\s*\d+(?:\.\d+)?)?\s*(?:MPa|GPa|ksi|psi|Pa|bar|atm)'

        # Composition patterns (18Cr-8Ni, Fe-0.4C)
        composition_pattern = r'\d+(?:\.\d+)?[A-Z][a-z]?(?:-\d+(?:\.\d+)?[A-Z][a-z]?)*'

        # Percentage patterns
        percentage_pattern = r'\d+(?:\.\d+)?(?:\s*±\s*\d+(?:\.\d+)?)?\s*(?:wt\.?%|at\.?%|mol\.?%|vol\.?%|%)'

        # Time patterns
        time_pattern = r'\d+(?:\.\d+)?(?:\s*±\s*\d+(?:\.\d+)?)?\s*(?:hours?|minutes?|seconds?|min|sec|h|s|ms)'

        # Length patterns
        length_pattern = r'\d+(?:\.\d+)?(?:\s*±\s*\d+(?:\.\d+)?)?\s*(?:mm|cm|m|μm|nm|in|ft)'

        # Combine all patterns
        all_patterns = [
            temp_pattern, pressure_pattern, composition_pattern,
            percentage_pattern, time_pattern, length_pattern
        ]

        for pattern_str in all_patterns:
            pattern = re.compile(pattern_str)
            matches = list(pattern.finditer(text))

            for match in reversed(matches):
                original = match.group(0)
                placeholder = self._generate_placeholder(prefix)
                self.placeholders[placeholder] = original
                self.protection_map["numbers"].append(original)

                # Replace in text
                text = text[:match.start()] + placeholder + text[match.end():]

        return text

    def _protect_special_patterns(self, text: str, prefix: str) -> str:
        """Protect special patterns (equipment, standards, formulas).

        Patterns:
        - Equipment: SEM, XRD, TEM, EDS, EBSD, Instron
        - Standards: ASTM E8, ISO 6892-1, DIN 17440
        - Chemical formulas: Fe₂O₃, M23C6, Al2O3

        Args:
            text: Input text
            prefix: Placeholder prefix

        Returns:
            Text with special patterns replaced by placeholders
        """
        # Equipment patterns
        equipment_specs = self.glossary.get("special_patterns", {}).get("equipment_specifications", {}).get("patterns", [])
        for equipment in equipment_specs:
            pattern = re.compile(r'\b' + re.escape(equipment) + r'\b', re.IGNORECASE)
            matches = list(pattern.finditer(text))

            for match in reversed(matches):
                original = match.group(0)
                placeholder = self._generate_placeholder(prefix)
                self.placeholders[placeholder] = original
                self.protection_map["equipment"].append(original)
                text = text[:match.start()] + placeholder + text[match.end():]

        # Standard references
        standard_refs = self.glossary.get("special_patterns", {}).get("standard_references", {})
        for std_type, standards in standard_refs.items():
            if std_type == "protection":
                continue  # Skip metadata field

            for standard in standards:
                pattern = re.compile(r'\b' + re.escape(standard) + r'\b')
                matches = list(pattern.finditer(text))

                for match in reversed(matches):
                    original = match.group(0)
                    placeholder = self._generate_placeholder(prefix)
                    self.placeholders[placeholder] = original
                    self.protection_map["standards"].append(original)
                    text = text[:match.start()] + placeholder + text[match.end():]

        # Chemical formulas (basic pattern)
        chemical_examples = self.glossary.get("special_patterns", {}).get("chemical_formulas", {}).get("examples", [])
        for formula in chemical_examples:
            pattern = re.compile(re.escape(formula))
            matches = list(pattern.finditer(text))

            for match in reversed(matches):
                original = match.group(0)
                placeholder = self._generate_placeholder(prefix)
                self.placeholders[placeholder] = original
                self.protection_map["formulas"].append(original)
                text = text[:match.start()] + placeholder + text[match.end():]

        return text

    def protect_text(
        self,
        text: str,
        protection_tier: str = "auto",
        protect_numbers: bool = True,
        protect_citations: bool = True,
        placeholder_prefix: str = "__TERM_",
        number_prefix: str = "__NUM_"
    ) -> Tuple[str, Dict[str, str], Dict[str, List[str]]]:
        """Main method to protect text with placeholders.

        Args:
            text: Input text to protect
            protection_tier: "auto", "tier1", "tier2", "tier3", or "all"
            protect_numbers: Protect numerical values
            protect_citations: Protect citations (future)
            placeholder_prefix: Prefix for term placeholders
            number_prefix: Prefix for number placeholders

        Returns:
            Tuple of (protected_text, placeholders, protection_map)
        """
        # Reset state
        self.placeholder_counter = 0
        self.placeholders = {}
        self.protection_map = {
            "tier1_terms": [],
            "tier2_terms": [],
            "tier3_terms": [],
            "numbers": [],
            "citations": [],
            "equipment": [],
            "formulas": [],
            "standards": []
        }

        protected_text = text

        # Protect based on tier selection
        if protection_tier in ["auto", "all", "tier1"]:
            protected_text = self._protect_tier1_terms(protected_text, placeholder_prefix)

        if protection_tier in ["auto", "all", "tier2"]:
            protected_text = self._protect_tier2_terms(protected_text, placeholder_prefix)

        if protection_tier in ["auto", "all", "tier3"]:
            protected_text = self._protect_tier3_terms(protected_text, placeholder_prefix)

        # Protect special patterns (equipment, standards, formulas)
        if protection_tier in ["auto", "all"]:
            protected_text = self._protect_special_patterns(protected_text, placeholder_prefix)

        # Protect numbers
        if protect_numbers:
            protected_text = self._protect_numbers(protected_text, number_prefix)

        # Citations protection (future feature)
        if protect_citations:
            # TODO: Implement citation detection and protection
            pass

        return protected_text, self.placeholders, self.protection_map


def process_input(input_data: dict) -> dict:
    """Process term protection request.

    Args:
        input_data: JSON input with text, glossary_path, options

    Returns:
        JSON response with protected text and metadata

    Raises:
        ValidationError: If input validation fails
        ProcessingError: If term protection fails
    """
    start_time = time.time()

    # Validate required fields
    if "text" not in input_data:
        raise ValidationError(
            message="Field 'text' is required but missing",
            component="term_protector",
            details={"required_fields": ["text", "glossary_path"]}
        )

    if "glossary_path" not in input_data:
        raise ValidationError(
            message="Field 'glossary_path' is required but missing",
            component="term_protector",
            details={"required_fields": ["text", "glossary_path"]}
        )

    # Extract parameters
    text = input_data["text"]
    glossary_path = input_data["glossary_path"]
    protection_tier = input_data.get("protection_tier", "auto")
    options = input_data.get("options", {})

    # Extract options
    protect_numbers = options.get("protect_numbers", True)
    protect_citations = options.get("protect_citations", True)
    placeholder_prefix = options.get("placeholder_prefix", "__TERM_")
    number_prefix = options.get("number_prefix", "__NUM_")

    # Validate protection_tier
    valid_tiers = ["auto", "tier1", "tier2", "tier3", "all"]
    if protection_tier not in valid_tiers:
        raise ValidationError(
            message=f"Invalid protection_tier: {protection_tier}",
            component="term_protector",
            details={
                "valid_values": valid_tiers,
                "received": protection_tier
            }
        )

    # Initialize term protector
    protector = TermProtector(glossary_path)

    # Protect text
    protected_text, placeholders, protection_map = protector.protect_text(
        text=text,
        protection_tier=protection_tier,
        protect_numbers=protect_numbers,
        protect_citations=protect_citations,
        placeholder_prefix=placeholder_prefix,
        number_prefix=number_prefix
    )

    # Calculate statistics
    stats = {
        "terms_protected": len(protection_map["tier1_terms"]) + len(protection_map["tier2_terms"]),
        "numbers_protected": len(protection_map["numbers"]),
        "citations_protected": len(protection_map["citations"]),
        "equipment_protected": len(protection_map["equipment"]),
        "formulas_protected": len(protection_map["formulas"]),
        "standards_protected": len(protection_map["standards"]),
        "total_placeholders": len(placeholders)
    }

    # Calculate processing time
    processing_time_ms = int((time.time() - start_time) * 1000)

    # Build response
    response = {
        "status": "success",
        "data": {
            "protected_text": protected_text,
            "placeholders": placeholders,
            "protection_map": protection_map
        },
        "metadata": {
            "processing_time_ms": processing_time_ms,
            "tool": "term_protector",
            "version": "1.0",
            "stats": stats
        }
    }

    logger.info(
        "Term protection completed",
        data={
            "input_length": len(text),
            "output_length": len(protected_text),
            "placeholders_created": len(placeholders),
            "processing_time_ms": processing_time_ms
        }
    )

    return response


def error_response(error_type: str, message: str, details: Optional[dict] = None) -> dict:
    """Create standardized error response.

    Args:
        error_type: Error class name
        message: Error message
        details: Additional error details

    Returns:
        JSON error response
    """
    return {
        "status": "error",
        "error": {
            "type": error_type,
            "message": message,
            "details": details or {}
        },
        "metadata": {
            "tool": "term_protector",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
    }


def main():
    """Main entry point for term_protector.py.

    Reads JSON from stdin, processes term protection, writes JSON to stdout.
    """
    try:
        # Read input from stdin
        input_text = sys.stdin.read()

        if not input_text.strip():
            response = error_response(
                "ValidationError",
                "No input provided on stdin",
                {"expected": "JSON object with 'text' and 'glossary_path' fields"}
            )
            print(json.dumps(response, indent=2))
            sys.exit(1)

        # Parse JSON
        try:
            input_data = json.loads(input_text)
        except json.JSONDecodeError as e:
            response = error_response(
                "ValidationError",
                f"Invalid JSON input: {str(e)}",
                {"position": e.pos, "line": e.lineno}
            )
            print(json.dumps(response, indent=2))
            sys.exit(1)

        # Process term protection
        response = process_input(input_data)

        # Output JSON to stdout
        print(json.dumps(response, indent=2))
        sys.exit(0)

    except (ValidationError, HumanizerFileNotFoundError, ProcessingError) as e:
        # Handle known errors
        response = error_response(
            e.__class__.__name__,
            e.message,
            e.details
        )
        logger.error(f"Term protection failed: {e.message}", data=e.details, exc_info=True)
        print(json.dumps(response, indent=2))
        sys.exit(1)

    except Exception as e:
        # Handle unexpected errors
        response = error_response(
            "ProcessingError",
            f"Unexpected error: {str(e)}",
            {"traceback": str(e)}
        )
        logger.exception("Unexpected error in term_protector")
        print(json.dumps(response, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
