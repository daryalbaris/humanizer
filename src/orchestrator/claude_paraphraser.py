"""
Claude API Paraphraser - Automated Paraphrasing via Anthropic Claude API
============================================================================

This module integrates Anthropic's Claude API to perform automated paraphrasing
when the paraphraser_processor returns prompts marked as ready_for_paraphrasing.

The orchestrator calls this module to execute the actual paraphrasing that the
paraphraser_processor has prepared.

Environment Variables Required:
    ANTHROPIC_API_KEY: Your Anthropic API key

Usage:
    from src.orchestrator.claude_paraphraser import ClaudeParaphraser

    paraphraser = ClaudeParaphraser()
    result = paraphraser.paraphrase_text(
        text="protected text with __TERM_XXX__ placeholders",
        prompts=paraphraser_output['data']['paraphrasing_prompts'],
        placeholder_map={"__TERM_001__": "original term"}
    )

Author: BMAD Development Team
Version: 1.0
Created: 2025-10-31
"""

import os
import time
from typing import Dict, List, Any, Optional
from src.utils.logger import get_logger

# Try to import anthropic, handle gracefully if not available
try:
    from anthropic import Anthropic, AnthropicError
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

logger = get_logger(__name__)


class ClaudeParaphraser:
    """
    Automated paraphrasing via Anthropic Claude API.

    This class handles communication with Claude API to perform the actual
    paraphrasing work that paraphraser_processor has prepared.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514"):
        """
        Initialize Claude API paraphraser.

        Args:
            api_key: Anthropic API key (if None, reads from ANTHROPIC_API_KEY env var)
            model: Claude model to use (default: claude-sonnet-4-20250514)

        Raises:
            ValueError: If anthropic library not installed or API key not provided
        """
        if not ANTHROPIC_AVAILABLE:
            raise ValueError(
                "Anthropic library not installed. Install with: pip install anthropic"
            )

        # Get API key
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError(
                "No Anthropic API key provided. Set ANTHROPIC_API_KEY environment variable "
                "or pass api_key parameter"
            )

        self.model = model
        self.client = Anthropic(api_key=self.api_key)

        logger.info("Claude API paraphraser initialized", context={
            "model": self.model,
            "api_key_present": bool(self.api_key)
        })

    def paraphrase_text(
        self,
        text: str,
        prompts: List[Dict[str, Any]],
        placeholder_map: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Paraphrase text using Claude API based on prepared prompts.

        Args:
            text: Protected text with __TERM_XXX__ and __NUM_XXX__ placeholders
            prompts: List of paraphrasing prompts from paraphraser_processor
            placeholder_map: Mapping of placeholders to original terms

        Returns:
            Dictionary with:
                - paraphrased_text: The paraphrased version
                - success: Boolean indicating success
                - error: Error message if failed
                - api_call_time_ms: Time taken for API call
        """
        start_time = time.time()

        try:
            logger.info("Starting Claude API paraphrasing", context={
                "text_length": len(text),
                "num_sections": len(prompts),
                "placeholders": len(placeholder_map)
            })

            # Process each section
            paraphrased_sections = []

            for prompt_data in prompts:
                section_type = prompt_data.get('section', 'unknown')
                prompt = prompt_data.get('prompt', {})

                system_prompt = prompt.get('system_prompt', '')
                user_prompt_template = prompt.get('user_prompt_template', '')

                # Format user prompt with actual text and protected terms
                protected_terms_str = self._format_protected_terms(placeholder_map)
                user_prompt = user_prompt_template.format(
                    protected_terms=protected_terms_str,
                    text=text
                )

                logger.debug(f"Calling Claude API for section: {section_type}", context={
                    "aggression_level": prompt.get('level', 'unknown'),
                    "prompt_length": len(user_prompt)
                })

                # Call Claude API
                try:
                    response = self.client.messages.create(
                        model=self.model,
                        max_tokens=8000,
                        temperature=0.7,
                        system=system_prompt,
                        messages=[
                            {"role": "user", "content": user_prompt}
                        ]
                    )

                    # Extract paraphrased text from response
                    paraphrased = response.content[0].text.strip()
                    paraphrased_sections.append(paraphrased)

                    logger.info(f"Section {section_type} paraphrased successfully", context={
                        "original_length": len(text),
                        "paraphrased_length": len(paraphrased),
                        "tokens_used": response.usage.input_tokens + response.usage.output_tokens
                    })

                except AnthropicError as e:
                    logger.error(f"Claude API error for section {section_type}", context={
                        "error": str(e),
                        "section": section_type
                    }, exc_info=True)

                    return {
                        "success": False,
                        "error": f"Claude API error: {str(e)}",
                        "api_call_time_ms": int((time.time() - start_time) * 1000)
                    }

            # Combine paraphrased sections
            final_text = "\n\n".join(paraphrased_sections)

            # Verify placeholders are preserved
            missing_placeholders = self._verify_placeholders(text, final_text)
            if missing_placeholders:
                logger.warning("Some placeholders missing after paraphrasing", context={
                    "missing": missing_placeholders
                })

            api_call_time = int((time.time() - start_time) * 1000)

            logger.info("Paraphrasing completed successfully", context={
                "sections_processed": len(paraphrased_sections),
                "final_length": len(final_text),
                "time_ms": api_call_time
            })

            return {
                "success": True,
                "paraphrased_text": final_text,
                "api_call_time_ms": api_call_time,
                "sections_processed": len(paraphrased_sections),
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens if response else 0
            }

        except Exception as e:
            logger.error("Unexpected error during paraphrasing", context={
                "error": str(e)
            }, exc_info=True)

            return {
                "success": False,
                "error": f"Paraphrasing failed: {str(e)}",
                "api_call_time_ms": int((time.time() - start_time) * 1000)
            }

    def _format_protected_terms(self, placeholder_map: Dict[str, str]) -> str:
        """
        Format placeholder map as readable string for prompts.

        Args:
            placeholder_map: Dictionary of placeholder -> original term

        Returns:
            Formatted string listing all protected terms
        """
        if not placeholder_map:
            return "No protected terms (all terms in original form)"

        terms = [f"{placeholder} = {original}" for placeholder, original in placeholder_map.items()]
        return "\n".join(terms)

    def _verify_placeholders(self, original: str, paraphrased: str) -> List[str]:
        """
        Verify that all placeholders from original text are present in paraphrased.

        Args:
            original: Original text with placeholders
            paraphrased: Paraphrased text (should have same placeholders)

        Returns:
            List of missing placeholders (empty if all preserved)
        """
        import re

        # Find all placeholders in original
        placeholder_pattern = r'__(?:TERM|NUM)_\d+__'
        original_placeholders = set(re.findall(placeholder_pattern, original))
        paraphrased_placeholders = set(re.findall(placeholder_pattern, paraphrased))

        missing = original_placeholders - paraphrased_placeholders
        return list(missing)

    def test_connection(self) -> bool:
        """
        Test Claude API connection with a simple request.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            logger.info("Testing Claude API connection")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=100,
                messages=[
                    {"role": "user", "content": "Hello, respond with 'Connection successful'"}
                ]
            )

            success = "successful" in response.content[0].text.lower()

            if success:
                logger.info("Claude API connection test: SUCCESS")
            else:
                logger.warning("Claude API connection test: UNEXPECTED RESPONSE")

            return success

        except Exception as e:
            logger.error("Claude API connection test: FAILED", context={
                "error": str(e)
            })
            return False


# Convenience function for orchestrator
def paraphrase_with_claude(
    text: str,
    paraphraser_output: Dict[str, Any],
    placeholder_map: Dict[str, str],
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to paraphrase text using Claude API.

    This is the main entry point called by the orchestrator.

    Args:
        text: Protected text with placeholders
        paraphraser_output: Output from paraphraser_processor tool
        placeholder_map: Mapping of placeholders to original terms
        api_key: Optional API key (uses ANTHROPIC_API_KEY env var if None)

    Returns:
        Dictionary with paraphrased_text and success status
    """
    try:
        paraphraser = ClaudeParaphraser(api_key=api_key)

        prompts = paraphraser_output.get('data', {}).get('paraphrasing_prompts', [])
        if not prompts:
            return {
                "success": False,
                "error": "No paraphrasing prompts found in paraphraser output"
            }

        result = paraphraser.paraphrase_text(text, prompts, placeholder_map)
        return result

    except ValueError as e:
        logger.error("Failed to initialize Claude paraphraser", context={"error": str(e)})
        return {
            "success": False,
            "error": str(e)
        }
