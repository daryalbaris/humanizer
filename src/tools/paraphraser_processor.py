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
from typing import Dict, List, Tuple, Optional
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')


class ParaphraserProcessor:
    """
    Prepares text for paraphrasing and provides prompts/strategies for Claude Code.

    Aggression Levels:
    1. Gentle (5-10%): Light lexical substitution, maintains original structure
    2. Moderate (10-20%): Sentence restructuring, synonym variation
    3. Aggressive (20-35%): Extensive rewriting, voice/tense changes
    4. Intensive (35-50%): Deep transformation, multiple techniques combined
    5. Nuclear (50-70%): Translation chain (EN→DE→JA→EN), last resort

    Section-Specific Strategies (IMRAD):
    - Introduction: Aggressive (sets tone, often flagged)
    - Methods: Gentle-Moderate (technical precision critical)
    - Results: Moderate (balance clarity and variation)
    - Discussion: Aggressive (interpretive, more flexible)
    - Conclusion: Aggressive (synthesis, often formulaic)
    """

    # IMRAD section detection patterns
    SECTION_PATTERNS = {
        'abstract': r'(?i)^(abstract|summary)\s*$',
        'introduction': r'(?i)^(introduction|background)\s*$',
        'methods': r'(?i)^(methods?|materials?\s+and\s+methods?|methodology|experimental)\s*$',
        'results': r'(?i)^(results?|findings?|observations?)\s*$',
        'discussion': r'(?i)^(discussion|interpretation)\s*$',
        'conclusion': r'(?i)^(conclusions?|summary|final\s+remarks?)\s*$',
        'references': r'(?i)^(references?|bibliography|works?\s+cited)\s*$'
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
