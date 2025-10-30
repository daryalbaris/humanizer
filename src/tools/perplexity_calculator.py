"""
Perplexity Calculator Tool - GPT-2 Based Perplexity Measurement

This tool calculates perplexity scores for text using a pre-trained GPT-2 model.
Lower perplexity indicates more predictable/AI-like text, while higher perplexity
suggests more varied/human-like text.

Input (JSON stdin):
{
    "text": "The text to analyze...",
    "sections": [
        {"name": "Introduction", "text": "...", "start": 0, "end": 500},
        {"name": "Methods", "text": "...", "start": 500, "end": 1500}
    ],  # Optional: for section-level analysis
    "model_name": "gpt2",  # Optional: gpt2, gpt2-medium, gpt2-large
    "chunk_size": 512  # Optional: token chunk size for processing
}

Output (JSON stdout):
{
    "status": "success",
    "data": {
        "overall_perplexity": 45.2,
        "section_perplexities": [
            {"name": "Introduction", "perplexity": 42.5, "length": 500},
            {"name": "Methods", "perplexity": 48.1, "length": 1000}
        ],
        "perplexity_distribution": {
            "min": 38.2,
            "max": 52.7,
            "mean": 45.2,
            "median": 44.8,
            "std_dev": 4.3
        }
    },
    "metadata": {
        "processing_time_ms": 8432,
        "tool": "perplexity_calculator",
        "version": "1.0",
        "model": "gpt2",
        "total_tokens": 2048,
        "chunks_processed": 4
    }
}

Author: BMAD Development Team
Version: 1.0
Created: 2025-10-30
"""

import sys
import json
import time
import torch
import numpy as np
from typing import List, Dict, Tuple, Optional
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')


class PerplexityCalculator:
    """
    Calculates perplexity scores for text using GPT-2.

    Perplexity is defined as:
    PPL = exp(average negative log-likelihood per token)

    Lower perplexity = more predictable (AI-like)
    Higher perplexity = less predictable (human-like)

    Typical ranges:
    - GPT-generated text: 15-30
    - Human-written academic text: 40-70
    - Human-written creative text: 60-100+
    """

    def __init__(self, model_name: str = "gpt2", device: Optional[str] = None):
        """
        Initialize the perplexity calculator.

        Args:
            model_name: GPT-2 model variant (gpt2, gpt2-medium, gpt2-large)
            device: Device to run on ('cuda', 'cpu', or None for auto-detect)
        """
        self.model_name = model_name

        # Auto-detect device
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        # Load model and tokenizer
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.model = GPT2LMHeadModel.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()  # Set to evaluation mode

        # Add padding token (GPT-2 doesn't have one by default)
        self.tokenizer.pad_token = self.tokenizer.eos_token

    def calculate_perplexity(
        self,
        text: str,
        chunk_size: int = 512,
        stride: int = 256
    ) -> Tuple[float, List[float]]:
        """
        Calculate perplexity for text using sliding window approach.

        Args:
            text: Text to analyze
            chunk_size: Maximum tokens per chunk
            stride: Number of tokens to stride between chunks (overlap)

        Returns:
            Tuple of (overall_perplexity, chunk_perplexities)
        """
        # Tokenize text
        encodings = self.tokenizer(text, return_tensors='pt')
        input_ids = encodings.input_ids.to(self.device)

        # Handle empty text
        if input_ids.size(1) == 0:
            return float('inf'), []

        # Calculate perplexity using sliding window
        max_length = self.model.config.n_positions
        chunk_size = min(chunk_size, max_length)

        nlls = []  # Negative log-likelihoods
        chunk_perplexities = []

        seq_len = input_ids.size(1)

        # Process text in overlapping chunks
        for begin_loc in range(0, seq_len, stride):
            end_loc = min(begin_loc + chunk_size, seq_len)
            trg_len = end_loc - begin_loc

            input_ids_chunk = input_ids[:, begin_loc:end_loc]
            target_ids = input_ids_chunk.clone()

            # Calculate negative log-likelihood
            with torch.no_grad():
                outputs = self.model(input_ids_chunk, labels=target_ids)
                neg_log_likelihood = outputs.loss * trg_len

            nlls.append(neg_log_likelihood)

            # Calculate chunk perplexity
            chunk_ppl = torch.exp(neg_log_likelihood / trg_len).item()
            chunk_perplexities.append(chunk_ppl)

            # Break if we've reached the end
            if end_loc == seq_len:
                break

        # Calculate overall perplexity
        if len(nlls) > 0:
            ppl = torch.exp(torch.stack(nlls).sum() / seq_len).item()
        else:
            ppl = float('inf')

        return ppl, chunk_perplexities

    def calculate_section_perplexities(
        self,
        sections: List[Dict[str, any]],
        chunk_size: int = 512
    ) -> List[Dict[str, any]]:
        """
        Calculate perplexity for each section.

        Args:
            sections: List of section dictionaries with 'name' and 'text'
            chunk_size: Chunk size for processing

        Returns:
            List of section perplexity results
        """
        results = []

        for section in sections:
            section_name = section.get('name', 'Unnamed')
            section_text = section.get('text', '')

            if not section_text.strip():
                results.append({
                    'name': section_name,
                    'perplexity': float('inf'),
                    'length': 0,
                    'tokens': 0
                })
                continue

            # Calculate perplexity for this section
            ppl, _ = self.calculate_perplexity(section_text, chunk_size)

            # Tokenize to get length
            encodings = self.tokenizer(section_text, return_tensors='pt')
            num_tokens = encodings.input_ids.size(1)

            results.append({
                'name': section_name,
                'perplexity': round(ppl, 2),
                'length': len(section_text),
                'tokens': num_tokens
            })

        return results

    def analyze_perplexity_distribution(
        self,
        chunk_perplexities: List[float]
    ) -> Dict[str, float]:
        """
        Calculate statistics for perplexity distribution.

        Args:
            chunk_perplexities: List of perplexity values

        Returns:
            Dictionary of distribution statistics
        """
        if not chunk_perplexities:
            return {
                'min': float('inf'),
                'max': float('inf'),
                'mean': float('inf'),
                'median': float('inf'),
                'std_dev': 0.0
            }

        return {
            'min': round(float(np.min(chunk_perplexities)), 2),
            'max': round(float(np.max(chunk_perplexities)), 2),
            'mean': round(float(np.mean(chunk_perplexities)), 2),
            'median': round(float(np.median(chunk_perplexities)), 2),
            'std_dev': round(float(np.std(chunk_perplexities)), 2)
        }


def process_input(input_data: Dict[str, any]) -> Dict[str, any]:
    """
    Process input and calculate perplexity scores.

    Args:
        input_data: Input dictionary from JSON stdin

    Returns:
        Output dictionary for JSON stdout
    """
    start_time = time.time()

    try:
        # Extract parameters
        text = input_data.get('text', '')
        sections = input_data.get('sections', [])
        model_name = input_data.get('model_name', 'gpt2')
        chunk_size = input_data.get('chunk_size', 512)

        # Validate text
        if not text.strip():
            return {
                'status': 'error',
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Text cannot be empty'
                }
            }

        # Initialize calculator
        calculator = PerplexityCalculator(model_name=model_name)

        # Calculate overall perplexity
        overall_ppl, chunk_ppls = calculator.calculate_perplexity(
            text,
            chunk_size=chunk_size
        )

        # Calculate section perplexities if provided
        section_results = []
        if sections:
            section_results = calculator.calculate_section_perplexities(
                sections,
                chunk_size=chunk_size
            )

        # Calculate perplexity distribution
        distribution = calculator.analyze_perplexity_distribution(chunk_ppls)

        # Get token count
        encodings = calculator.tokenizer(text, return_tensors='pt')
        total_tokens = encodings.input_ids.size(1)

        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)

        # Build response
        return {
            'status': 'success',
            'data': {
                'overall_perplexity': round(overall_ppl, 2),
                'section_perplexities': section_results,
                'perplexity_distribution': distribution
            },
            'metadata': {
                'processing_time_ms': processing_time,
                'tool': 'perplexity_calculator',
                'version': '1.0',
                'model': model_name,
                'total_tokens': total_tokens,
                'chunks_processed': len(chunk_ppls)
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
