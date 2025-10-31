"""
Paraphraser Processor Tool - Adversarial Paraphrasing Engine

This tool coordinates adversarial paraphrasing with Claude Code agent to reduce
AI detection while maintaining semantic meaning and protecting technical terms.

The actual paraphrasing is performed by Claude Code via the orchestrator, but
this tool provides:
1. Section detection (IMRAD structure)
2. Aggression level configuration
3. Prompt templates
4. Post-processing and validation

Input (JSON stdin):
{
    "text": "The text to paraphrase...",
    "protected_text": "Text with __TERM_001__ placeholders...",
    "placeholder_map": {
        "__TERM_001__": "original term"
    },
    "aggression_level": 2,  # 1-5 (Gentle to Nuclear)
    "section_type": "auto",  # auto, introduction, methods, results, discussion, conclusion
    "preserve_structure": true,
    "max_iterations": 7
}

Output (JSON stdout):
{
    "status": "success",
    "data": {
        "paraphrased_text": "The paraphrased version...",
        "sections_detected": [
            {"type": "introduction", "start": 0, "end": 500, "strategy": "gentle"}
        ],
        "aggression_used": 2,
        "iterations_performed": 1,
        "changes_summary": {
            "sentences_modified": 12,
            "words_changed": 45,
            "structure_preserved": true
        }
    },
    "metadata": {
        "processing_time_ms": 120000,
        "tool": "paraphraser_processor",
        "version": "1.0"
    }
}

NOTE: This tool prepares the input and configuration for Claude-based paraphrasing.
The actual paraphrasing is coordinated by the orchestrator agent.

Author: BMAD Development Team
Version: 1.0
Created: 2025-10-30
"""

import sys
import json
import time
import re
import os
from typing import Dict, List, Tuple, Optional
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')


class ParaphraserProcessor:
    """
    Prepares text for paraphrasing and provides prompts/strategies for Claude Code.

    Aggression Levels (COMPLETE 1-5):
    1. Gentle (5-10%): Light lexical substitution, maintains original structure
    2. Moderate (10-20%): Sentence restructuring, synonym variation
    3. Aggressive (20-35%): Extensive rewriting, voice/tense changes
    4. Intensive (35-50%): Multi-layered transformation with context-aware synonyms,
       sentence structure transformation, paragraph architecture redesign,
       voice/tense/perspective shifts, maximum sentence opening diversity
    5. Nuclear (50-70%): Translation chain (EN→DE→JA→EN) with protected term
       preservation, formal academic register throughout all languages,
       post-translation refinement for natural English flow. Last resort option.

    Section-Specific Strategies (IMRAD):
    - Introduction: Aggressive (Level 3) - Sets tone, often flagged
    - Methods: Gentle-Moderate (Levels 1-2) - Technical precision critical
    - Results: Moderate (Level 2) - Balance clarity and variation
    - Discussion: Aggressive (Level 3) - Interpretive, more flexible
    - Conclusion: Aggressive (Level 3) - Synthesis, often formulaic

    Note: Levels 4-5 are reserved for extreme cases when target detection
    thresholds cannot be achieved with standard levels 1-3.
    """

    # IMRAD section detection patterns (supports both plain and markdown headers)
    SECTION_PATTERNS = {
        'abstract': r'(?i)^#*\s*(abstract|summary)\s*$',
        'introduction': r'(?i)^#*\s*(introduction|background)\s*$',
        'methods': r'(?i)^#*\s*(methods?|materials?\s+and\s+methods?|methodology|experimental)\s*$',
        'results': r'(?i)^#*\s*(results?|findings?|observations?)\s*$',
        'discussion': r'(?i)^#*\s*(discussion|interpretation)\s*$',
        'conclusion': r'(?i)^#*\s*(conclusions?|summary|final\s+remarks?)\s*$',
        'references': r'(?i)^#*\s*(references?|bibliography|works?\s+cited)\s*$'
    }

    # Section-specific aggression recommendations
    SECTION_AGGRESSION = {
        'abstract': 3,  # Aggressive
        'introduction': 3,  # Aggressive
        'methods': 2,  # Moderate
        'results': 2,  # Moderate
        'discussion': 3,  # Aggressive
        'conclusion': 3,  # Aggressive
        'references': 1   # Gentle (if paraphrasing at all)
    }

    def __init__(self):
        """Initialize the paraphraser processor."""
        pass

    def detect_sections(self, text: str) -> List[Dict[str, any]]:
        """
        Detect IMRAD sections in academic paper.

        Args:
            text: Full paper text

        Returns:
            List of detected sections with type, start, end positions
        """
        sections = []
        lines = text.split('\n')
        current_section = 'unknown'
        section_start = 0
        char_position = 0

        for i, line in enumerate(lines):
            line_start = char_position
            char_position += len(line) + 1  # +1 for newline

            # Check if line is a section header
            for section_type, pattern in self.SECTION_PATTERNS.items():
                if re.match(pattern, line.strip()):
                    # Save previous section if exists
                    if current_section != 'unknown' and section_start < line_start:
                        sections.append({
                            'type': current_section,
                            'start': section_start,
                            'end': line_start,
                            'text': text[section_start:line_start].strip(),
                            'strategy': self._get_section_strategy(current_section)
                        })

                    # Start new section
                    current_section = section_type
                    section_start = char_position
                    break

        # Add final section
        if current_section != 'unknown':
            sections.append({
                'type': current_section,
                'start': section_start,
                'end': len(text),
                'text': text[section_start:].strip(),
                'strategy': self._get_section_strategy(current_section)
            })

        # If no sections detected, treat as single section
        if not sections:
            sections.append({
                'type': 'full_text',
                'start': 0,
                'end': len(text),
                'text': text,
                'strategy': 'moderate'
            })

        return sections

    def _get_section_strategy(self, section_type: str) -> str:
        """
        Get recommended paraphrasing strategy for section type.

        Args:
            section_type: Type of section

        Returns:
            Strategy name
        """
        aggression_level = self.SECTION_AGGRESSION.get(section_type, 2)

        strategy_map = {
            1: 'gentle',
            2: 'moderate',
            3: 'aggressive',
            4: 'intensive',
            5: 'nuclear'
        }

        return strategy_map.get(aggression_level, 'moderate')

    def get_section_strategies(self, sections: List[Dict[str, any]]) -> List[Dict[str, str]]:
        """
        Get paraphrasing strategies for multiple sections.

        Args:
            sections: List of section dictionaries from detect_sections()

        Returns:
            List of strategy dictionaries, one per section
        """
        strategies = []
        for section in sections:
            section_type = section.get('type', 'full_text')
            strategy = self._get_section_strategy(section_type)
            strategies.append({
                'section': section_type,  # Test expects 'section' not 'type'
                'strategy': strategy
            })
        return strategies

    def generate_paraphrasing_prompt(
        self,
        text: str,
        aggression_level: int,
        sections: List[Dict[str, any]] = None
    ) -> Dict[str, str]:
        """
        Generate complete paraphrasing prompt with text and instructions.

        Args:
            text: Text to be paraphrased
            aggression_level: Aggression level (1-5)
            sections: Optional list of sections for section-aware prompting

        Returns:
            Dictionary with 'system_prompt' and 'user_prompt' keys
        """
        # Get base prompts for aggression level
        section_type = 'general'
        if sections and len(sections) > 0:
            section_type = sections[0].get('type', 'general')

        base_prompts = self.get_aggression_prompt(aggression_level, section_type)

        # Format user prompt with actual text
        user_prompt = base_prompts['user_prompt_template'].format(
            section_type=section_type,
            protected_terms="All terms marked with __TERM_XXX__ or __NUM_XXX__ placeholders",
            text=text
        )

        return {
            'system_prompt': base_prompts['system_prompt'],
            'user_prompt': user_prompt,
            'level': aggression_level,  # Include aggression level for reference
            'name': base_prompts['name']  # Include name for reference
        }

    def get_aggression_prompt(
        self,
        level: int,
        section_type: str = 'general'
    ) -> Dict[str, str]:
        """
        Get paraphrasing prompt for specific aggression level.

        Args:
            level: Aggression level (1-5)
            section_type: Type of section being paraphrased

        Returns:
            Dictionary with system_prompt and user_prompt
        """
        prompts = {
            1: {
                'name': 'Gentle',
                'system_prompt': """You are an expert academic editor specializing in light paraphrasing.

Your task: Perform MINIMAL paraphrasing (5-10% change) while preserving:
- Original structure and flow
- Technical terminology (NEVER change terms marked with __TERM_XXX__ or __NUM_XXX__)
- Factual accuracy
- Academic tone

Techniques to use:
- Synonym substitution (common words only)
- Minor phrase reordering
- Contractions ↔ expansions (it's/it is, don't/do not)

What NOT to do:
- Change sentence structure
- Alter technical terms
- Modify voice or tense
- Add or remove information""",

                'user_prompt': """Paraphrase this {section_type} section with GENTLE modifications:

Protected terms (DO NOT CHANGE):
{protected_terms}

Text to paraphrase:
{text}

Apply only light synonym substitution and minor phrasing adjustments. Maintain 90-95% similarity to original."""
            },

            2: {
                'name': 'Moderate',
                'system_prompt': """You are an expert academic editor specializing in moderate paraphrasing.

Your task: Perform MODERATE paraphrasing (10-20% change) while preserving:
- Technical terminology (NEVER change terms marked with __TERM_XXX__ or __NUM_XXX__)
- Core meaning and factual content
- Academic tone

Techniques to use:
- Synonym variation (academic vocabulary)
- Sentence restructuring (active ↔ passive voice)
- Clause reordering
- Phrase variation (e.g., "it is important to note" → "notably")

What NOT to do:
- Change technical terms
- Alter factual claims
- Remove critical details
- Change overall structure""",

                'user_prompt': """Paraphrase this {section_type} section with MODERATE restructuring:

Protected terms (DO NOT CHANGE):
{protected_terms}

Text to paraphrase:
{text}

Apply sentence restructuring, synonym variation, and voice changes. Maintain 80-90% similarity."""
            },

            3: {
                'name': 'Aggressive',
                'system_prompt': """You are an expert academic editor specializing in extensive paraphrasing.

Your task: Perform AGGRESSIVE paraphrasing (20-35% change) while preserving:
- Technical terminology (NEVER change terms marked with __TERM_XXX__ or __NUM_XXX__)
- Core meaning and factual accuracy
- Academic credibility

Techniques to use:
- Extensive synonym variation
- Sentence restructuring and splitting/merging
- Voice and tense changes
- Paragraph reorganization
- Transition phrase variation
- Beginning word diversity

What NOT to do:
- Change technical terms
- Alter factual claims
- Remove important details""",

                'user_prompt': """Paraphrase this {section_type} section with AGGRESSIVE rewriting:

Protected terms (DO NOT CHANGE):
{protected_terms}

Text to paraphrase:
{text}

Apply extensive restructuring, voice/tense changes, and paragraph reorganization. Target 65-80% similarity."""
            },

            4: {
                'name': 'Intensive',
                'system_prompt': """You are an expert academic editor specializing in deep paraphrasing and stylistic transformation.

Your task: Perform INTENSIVE paraphrasing (35-50% change) while preserving:
- Technical terminology (NEVER change terms marked with __TERM_XXX__ or __NUM_XXX__)
- Core factual content and research findings
- Academic integrity and credibility

Techniques to use (MULTI-LAYERED APPROACH):
1. Context-Aware Synonym Replacement:
   - Use discipline-specific terminology variations
   - Replace common academic phrases with field-specific alternatives
   - Vary connector words extensively (however → nevertheless → conversely)

2. Sentence Structure Transformation:
   - Complex sentences → Simple sentences (and vice versa)
   - Embedded clauses → Separate sentences
   - Serial sentences → Compound structures
   - Question format for emphasis (rare, strategic use)

3. Paragraph Architecture Redesign:
   - Reverse topic sentence placement (front → back)
   - Split dense paragraphs into focused units
   - Merge related short paragraphs
   - Vary paragraph opening strategies

4. Voice, Tense, and Perspective Shifts:
   - Consistent active/passive voice changes
   - Present → Past tense (where appropriate)
   - Nominalization variations (e.g., "analyzed" → "analysis was performed")
   - Perspective shifts (direct → indirect discourse)

5. Sentence Opening Diversification:
   - NEVER repeat opening patterns
   - Use prepositional phrases, adverbs, subordinate clauses
   - Avoid generic starts (The, This, It)

6. Transitional Architecture:
   - Replace explicit transitions with implicit logical flow
   - Vary transition types (additive, causal, contrastive)
   - Strategic removal or addition of connectors

What NOT to do:
- Change technical terms or protected placeholders
- Alter numerical data or statistical findings
- Remove or add substantive information
- Introduce informal language""",

                'user_prompt': """Paraphrase this {section_type} section with INTENSIVE multi-layered transformation:

Protected terms (DO NOT CHANGE):
{protected_terms}

Text to paraphrase:
{text}

Apply ALL intensive techniques:
1. Context-aware synonym replacement throughout
2. Complete sentence structure transformation
3. Paragraph architecture redesign
4. Voice/tense/perspective shifts
5. Maximum sentence opening diversity
6. Advanced transitional architecture

Target: 50-65% similarity. Transform the writing style while maintaining academic rigor and factual precision."""
            },

            5: {
                'name': 'Nuclear',
                'system_prompt': """You are an expert multilingual academic translator specializing in translation-based paraphrasing.

Your task: Perform NUCLEAR paraphrasing (50-70% change) using TRANSLATION CHAIN methodology while preserving:
- Technical terminology (NEVER translate terms marked with __TERM_XXX__ or __NUM_XXX__)
- Core factual content and research validity
- Academic standards and credibility

TRANSLATION CHAIN PROCESS (EN → DE → JA → EN):

1. English → German Translation:
   - Translate to formal academic German
   - PRESERVE all __TERM_XXX__ and __NUM_XXX__ placeholders as-is
   - Use formal register ("untersucht wurde" not "wurde untersucht")
   - Maintain technical precision

2. German → Japanese Translation:
   - Translate to formal Japanese (です/ます form)
   - PRESERVE all __TERM_XXX__ and __NUM_XXX__ placeholders as-is
   - Use academic kanji compounds
   - Maintain logical structure

3. Japanese → English Re-translation:
   - Translate back to formal academic English
   - PRESERVE all __TERM_XXX__ and __NUM_XXX__ placeholders as-is
   - Natural English academic style
   - Maintain factual accuracy

CRITICAL RULES:
1. Protected Terms: ALWAYS preserve __TERM_XXX__ and __NUM_XXX__ unchanged through ALL translation steps
2. Factual Preservation: Numerical values, findings, and conclusions must remain identical
3. Academic Register: Maintain formal academic tone throughout
4. Structural Integrity: Preserve paragraph boundaries and logical flow
5. Quality Check: If re-translated English is nonsensical, retry with adjusted German/Japanese

POST-TRANSLATION REFINEMENT:
- Fix any grammatical artifacts from translation
- Ensure natural English academic flow
- Verify all protected terms remain intact
- Confirm factual accuracy preserved

What NOT to do:
- Translate technical terms or placeholders
- Alter statistical data or findings
- Introduce translation artifacts
- Create unnatural English phrasing""",

                'user_prompt': """Paraphrase this {section_type} section using NUCLEAR translation chain (EN→DE→JA→EN):

Protected terms (NEVER TRANSLATE - keep as-is in all languages):
{protected_terms}

Text to paraphrase:
{text}

Execute the translation chain:
1. Translate English → German (formal academic register, preserve placeholders)
2. Translate German → Japanese (formal register, preserve placeholders)
3. Translate Japanese → English (natural academic English, preserve placeholders)
4. Refine final English for naturalness and flow
5. Verify all protected terms unchanged
6. Confirm factual accuracy maintained

Target: 30-50% similarity. Maximum transformation while maintaining research integrity.

WARNING: This is the most aggressive paraphrasing level. Use only when Levels 1-4 fail to achieve target detection scores."""
            }
        }

        # Get prompt for requested level (default to level 2 if not found)
        prompt_data = prompts.get(level, prompts[2])

        # Format prompts with section context
        system_prompt = prompt_data['system_prompt']
        user_prompt = prompt_data['user_prompt'].format(
            section_type=section_type,
            protected_terms="{protected_terms}",  # Will be filled by orchestrator
            text="{text}"  # Will be filled by orchestrator
        )

        return {
            'name': prompt_data['name'],
            'level': level,
            'system_prompt': system_prompt,
            'user_prompt_template': user_prompt
        }


def _basic_paraphrase(text: str, aggression_level: int) -> str:
    """
    Rule-based paraphrasing for testing and fallback when API key unavailable.

    Performs simple word/phrase substitutions. More aggressive levels apply
    more substitutions. Preserves __TERM_XXX__ and __NUM_XXX__ placeholders.

    Args:
        text: Input text (may contain placeholders)
        aggression_level: 1-5, higher = more changes

    Returns:
        Paraphrased text with placeholders preserved
    """
    import re

    # Word/phrase substitutions (academic style)
    # Ordered by commonality for better paraphrasing effect
    replacements = {
        # Common academic phrases
        r'\bthe\b': 'a',
        r'\bis\b': 'appears to be',
        r'\bwas\b': 'had been',
        r'\bare\b': 'seem to be',
        r'\bwere\b': 'had been',

        # Adverbs and modifiers
        r'\bvery\b': 'quite',
        r'\bextremely\b': 'remarkably',
        r'\bhighly\b': 'considerably',
        r'\bquite\b': 'rather',

        # Common adjectives
        r'\bgood\b': 'excellent',
        r'\bbad\b': 'poor',
        r'\bimportant\b': 'significant',
        r'\bbig\b': 'large',
        r'\bsmall\b': 'minor',

        # Common verbs (simpler replacements without suffix preservation)
        r'\bshows?\b': 'demonstrates',
        r'\bshowed\b': 'demonstrated',
        r'\buses?\b': 'utilizes',
        r'\bused\b': 'utilized',
        r'\bmakes?\b': 'produces',
        r'\bgets?\b': 'obtains',
        r'\bgives?\b': 'provides',

        # Connectors and transitions
        r'\bhowever\b': 'nevertheless',
        r'\btherefore\b': 'consequently',
        r'\balso\b': 'additionally',
        r'\bbut\b': 'however',
        r'\bso\b': 'thus',

        # Quantifiers
        r'\bmany\b': 'numerous',
        r'\bsome\b': 'certain',
        r'\ba few\b': 'several',
        r'\ba lot of\b': 'considerable amounts of',
    }

    result = text

    # Scale replacements by aggression level
    # Level 1: 5 replacements, Level 5: 25 replacements
    max_replacements = aggression_level * 5

    # Apply substitutions with case-insensitive matching
    for pattern, replacement in replacements.items():
        # Count parameter limits how many times to replace
        result = re.sub(
            pattern,
            replacement,
            result,
            flags=re.IGNORECASE,
            count=max_replacements
        )

    # Additional transformation for higher aggression levels
    if aggression_level >= 3:
        # Add passive voice transformations for level 3+
        result = re.sub(r'\bwe (.*?)\b', r'it is \\1', result, flags=re.IGNORECASE, count=3)

    if aggression_level >= 4:
        # Add more complex transformations for level 4+
        result = re.sub(r'\bin this\b', 'within this particular', result, flags=re.IGNORECASE, count=2)
        result = re.sub(r'\bcan be\b', 'may potentially be', result, flags=re.IGNORECASE, count=2)

    return result


def process_input(input_data: Dict[str, any]) -> Dict[str, any]:
    """
    Process input and prepare for paraphrasing.

    Args:
        input_data: Input dictionary from JSON stdin

    Returns:
        Output dictionary for JSON stdout
    """
    start_time = time.time()

    try:
        # Extract parameters
        text = input_data.get('text', '')
        protected_text = input_data.get('protected_text', text)
        placeholder_map = input_data.get('placeholder_map', {})
        aggression_level = input_data.get('aggression_level', 2)
        section_type = input_data.get('section_type', 'auto')
        preserve_structure = input_data.get('preserve_structure', True)

        # Validate text
        if not text.strip():
            return {
                'status': 'error',
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Text cannot be empty'
                }
            }

        # Validate aggression level
        if not 1 <= aggression_level <= 5:
            return {
                'status': 'error',
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Aggression level must be between 1 and 5'
                }
            }

        # Initialize processor
        processor = ParaphraserProcessor()

        # Detect sections if auto
        if section_type == 'auto':
            sections_detected = processor.detect_sections(text)
        else:
            sections_detected = [{
                'type': section_type,
                'start': 0,
                'end': len(text),
                'text': text,
                'strategy': processor._get_section_strategy(section_type)
            }]

        # Get paraphrasing prompts
        prompts = []
        for section in sections_detected:
            prompt = processor.get_aggression_prompt(
                level=aggression_level,
                section_type=section['type']
            )
            prompts.append({
                'section': section['type'],
                'prompt': prompt
            })

        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)

        # Check if basic paraphrasing should be performed (for testing/fallback)
        enable_basic_paraphrasing = os.getenv('ENABLE_BASIC_PARAPHRASING', 'true').lower() == 'true'

        if enable_basic_paraphrasing:
            # Perform basic rule-based paraphrasing
            paraphrased_text = _basic_paraphrase(text, aggression_level)

            return {
                'status': 'success',
                'data': {
                    'paraphrased_text': paraphrased_text,
                    'original_text': text,
                    'sections_detected': sections_detected,
                    'paraphrasing_prompts': prompts,
                    'aggression_level': aggression_level,
                    'ready_for_paraphrasing': False,
                    'method': 'basic_rule_based',
                    'note': 'Basic rule-based paraphrasing applied (ENABLE_BASIC_PARAPHRASING=true).'
                },
                'metadata': {
                    'processing_time_ms': processing_time,
                    'tool': 'paraphraser_processor',
                    'version': '1.0',
                    'sections_count': len(sections_detected)
                }
            }
        else:
            # Build response (preparation only - actual paraphrasing done by orchestrator)
            return {
                'status': 'success',
                'data': {
                    'sections_detected': sections_detected,
                    'paraphrasing_prompts': prompts,
                    'aggression_level': aggression_level,
                    'ready_for_paraphrasing': True,
                    'note': 'This is a preparation step. Actual paraphrasing is performed by Claude Code orchestrator.'
                },
                'metadata': {
                    'processing_time_ms': processing_time,
                    'tool': 'paraphraser_processor',
                    'version': '1.0',
                    'sections_count': len(sections_detected)
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
