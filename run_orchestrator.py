"""
Run Python Orchestrator on DAC Paper - Real Automated Processing
================================================================

This script uses the actual Python Orchestrator API with real tools:
- term_protector.py (Python tool)
- paraphraser_processor.py (Python tool with GPT-2/spaCy)
- detector_processor.py (Python tool with GPTZero API)
- validator.py (Python tool with BERTScore)
- etc.

Author: BMAD Development Team
Date: 2025-10-31
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from orchestrator.orchestrator import Orchestrator
from utils.config_loader import load_config
from utils.logger import get_logger

logger = get_logger(__name__)


def load_paper(file_path: str) -> str:
    """Load the paper text from file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def split_into_sections(text: str) -> list:
    """Split paper into processable sections."""
    sections = []
    current_section = []
    current_heading = None

    for line in text.split('\n'):
        # Detect headings (lines starting with #)
        if line.strip().startswith('#'):
            # Save previous section
            if current_section:
                sections.append({
                    'heading': current_heading,
                    'content': '\n'.join(current_section).strip()
                })
                current_section = []
            current_heading = line.strip()
        else:
            if line.strip():  # Skip empty lines at boundaries
                current_section.append(line)

    # Add final section
    if current_section:
        sections.append({
            'heading': current_heading,
            'content': '\n'.join(current_section).strip()
        })

    return sections


def save_humanized_section(section: dict, output_path: str, mode: str = 'a'):
    """Save humanized section to output file."""
    with open(output_path, mode, encoding='utf-8') as f:
        if section['heading']:
            f.write(section['heading'] + '\n\n')
        f.write(section['humanized_content'] + '\n\n')


def main():
    """Main orchestrator workflow."""

    print("="*60)
    print("🤖 PYTHON ORCHESTRATOR - AUTOMATED HUMANIZATION")
    print("="*60)
    print()

    # Load configuration
    logger.info("Loading configuration...")
    config = load_config()
    print(f"✓ Configuration loaded")
    print(f"  - Max iterations: {config['humanizer']['max_iterations']}")
    print(f"  - Detection threshold: {config['humanizer']['detection_threshold']}")
    print()

    # Initialize orchestrator
    logger.info("Initializing orchestrator...")
    orchestrator = Orchestrator(config)
    print(f"✓ Orchestrator initialized")
    print(f"  - Tools available: {len(orchestrator.TOOL_PIPELINE)}")
    print()

    # Load paper
    input_file = "docs/dac test.md"
    output_file = "docs/dac test_ORCHESTRATED.md"

    logger.info(f"Loading paper from: {input_file}")
    paper_text = load_paper(input_file)
    print(f"✓ Paper loaded: {len(paper_text)} characters")
    print()

    # Split into sections
    logger.info("Splitting paper into sections...")
    sections = split_into_sections(paper_text)
    print(f"✓ Found {len(sections)} sections to process")
    print()

    # Clear output file
    Path(output_file).write_text("", encoding='utf-8')

    # Process each section
    humanized_sections = []
    total_sections = len(sections)

    for i, section in enumerate(sections, 1):
        section_name = section['heading'] or f"Section {i}"
        print(f"\n{'='*60}")
        print(f"📝 Processing {i}/{total_sections}: {section_name}")
        print(f"{'='*60}")

        # Skip empty sections
        if not section['content'].strip():
            logger.info(f"Skipping empty section: {section_name}")
            print(f"⚠ Skipping empty section")
            continue

        print(f"Input length: {len(section['content'])} characters")
        print()

        try:
            # Run orchestrator pipeline
            print(f"🚀 Starting orchestrator pipeline...")
            print(f"   This will run real Python tools:")
            print(f"   1. term_protector → 2. paraphraser_processor →")
            print(f"   3. fingerprint_remover → 4. imperfection_injector →")
            print(f"   5. burstiness_enhancer → 6. detector_processor →")
            print(f"   7. validator")
            print()

            result = orchestrator.run_pipeline(
                input_text=section['content'],
                options={
                    'initial_aggression': 'moderate',
                    'glossary_path': config['paths']['glossary']
                }
            )

            # Extract results
            section['humanized_content'] = result['final_text']
            section['status'] = result['status']
            section['iterations'] = result['iterations']
            section['final_scores'] = result['final_scores']
            section['workflow_id'] = result['workflow_id']

            humanized_sections.append(section)

            # Print results
            print()
            print(f"{'='*60}")
            print(f"✅ Section {i} completed!")
            print(f"{'='*60}")
            print(f"Status: {result['status']}")
            print(f"Iterations: {result['iterations']}/{config['humanizer']['max_iterations']}")
            print(f"Output length: {len(result['final_text'])} characters")
            print()
            print(f"📊 Final Scores:")
            if result['final_scores']:
                for metric, value in result['final_scores'].items():
                    print(f"   - {metric}: {value}")
            print()

            # Save section immediately
            save_humanized_section(section, output_file, mode='a')
            logger.info(f"Section {i} saved to {output_file}")

        except Exception as e:
            error_msg = f"Section {i} failed: {str(e)}"
            logger.error(error_msg)
            print(f"\n❌ ERROR: {error_msg}")
            print(f"   Skipping to next section...")
            continue

    # Generate final report
    print()
    print("="*60)
    print("📊 GENERATING FINAL REPORT")
    print("="*60)

    report = {
        'input_file': input_file,
        'output_file': output_file,
        'processing_date': datetime.now().isoformat(),
        'total_sections': total_sections,
        'processed_sections': len(humanized_sections),
        'failed_sections': total_sections - len(humanized_sections),
        'config': {
            'max_iterations': config['humanizer']['max_iterations'],
            'detection_threshold': config['humanizer']['detection_threshold'],
            'initial_aggression': 'moderate'
        },
        'sections': [
            {
                'section': i,
                'heading': sec['heading'],
                'status': sec.get('status', 'unknown'),
                'iterations': sec.get('iterations', 0),
                'workflow_id': sec.get('workflow_id', 'N/A'),
                'final_scores': sec.get('final_scores', {})
            }
            for i, sec in enumerate(humanized_sections, 1)
        ]
    }

    report_file = "docs/dac_orchestrator_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"✓ Report saved to: {report_file}")
    print()

    # Print summary
    print("="*60)
    print("✅ HUMANIZATION COMPLETE")
    print("="*60)
    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")
    print(f"Report: {report_file}")
    print()
    print(f"Sections processed: {len(humanized_sections)}/{total_sections}")
    print(f"Total iterations: {sum(s.get('iterations', 0) for s in humanized_sections)}")
    print("="*60)


if __name__ == "__main__":
    main()
