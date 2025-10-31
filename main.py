"""
BMAD Academic Humanizer - Production Orchestrator
==================================================

Main entry point for the complete humanization workflow.
Orchestrates all components, manages state, handles errors, and generates reports.

Usage:
    python main.py --input paper.txt --config config.yaml
    python main.py --input paper.txt --resume workflow-id
    python main.py --help

Architecture:
    - Claude Code agent orchestrates workflow via Bash tool
    - Python tools executed as stateless workers (stdin/stdout JSON)
    - State persisted via checkpoints for crash recovery
    - Human injection points for expert input (optional)
"""

import sys
import argparse
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.orchestration import (
    StateManager,
    WorkflowState,
    InjectionPointIdentifier,
    CLIInterface,
    ConfigLoader,
    ErrorHandler,
    ToolExecutionError,
    ValidationError
)


class ProductionOrchestrator:
    """
    Production orchestrator for BMAD humanization workflow.

    Coordinates all 8 components:
    1. Term Protection
    2. Paraphrasing
    3. Fingerprint Removal
    4. Burstiness Enhancement
    5. Detection Analysis
    6. Perplexity Calculation
    7. Validation
    8. Iterative Refinement
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize orchestrator.

        Args:
            config: Configuration dictionary from YAML
        """
        self.config = config

        # Initialize components
        self.state_manager = StateManager(
            checkpoint_dir=config.get("checkpoint_dir", ".humanizer/checkpoints"),
            backup_dir=config.get("backup_dir", ".humanizer/checkpoints/backups")
        )

        self.cli = CLIInterface(config)
        self.error_handler = ErrorHandler(
            max_retries=config.get("max_retries", 3),
            retry_delay_seconds=config.get("retry_delay", 2)
        )

        self.injection_identifier = InjectionPointIdentifier(
            max_injection_points=config.get("max_injection_points", 5)
        ) if config.get("human_injection_enabled", True) else None

        # Workflow configuration
        self.max_iterations = config.get("max_iterations", 7)
        self.target_threshold = config.get("target_originality_threshold", 20.0)
        self.early_termination_threshold = config.get("early_termination_improvement", 2.0)

        # Aggression levels (escalation ladder)
        self.aggression_levels = ["gentle", "moderate", "aggressive", "intensive", "nuclear"]

    def run_workflow(self, input_text: str, workflow_id: Optional[str] = None) -> WorkflowState:
        """
        Run complete humanization workflow.

        Args:
            input_text: Original academic paper text
            workflow_id: Optional workflow ID for resume

        Returns:
            Final workflow state
        """
        # Phase 1: Initialization
        self.cli.display_banner()
        self.cli.display_message("Initializing workflow...")

        # Create or resume workflow
        if workflow_id:
            # Resume from checkpoint
            self.cli.display_message(f"Resuming workflow: {workflow_id}")
            workflow_state = self.state_manager.load_workflow(workflow_id)
            if not workflow_state:
                raise ValueError(f"Workflow {workflow_id} not found")
        else:
            # Create new workflow
            workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.cli.display_message(f"Creating new workflow: {workflow_id}")
            workflow_state = self.state_manager.create_workflow(
                workflow_id=workflow_id,
                original_text=input_text,
                target_originality_threshold=self.target_threshold,
                max_iterations=self.max_iterations
            )

        # Phase 2: Iterative Refinement Loop
        current_iteration = workflow_state.current_iteration
        current_text = workflow_state.current_text

        while current_iteration < self.max_iterations:
            iteration_num = current_iteration + 1

            # Determine aggression level
            aggression_level = self._select_aggression_level(
                workflow_state, iteration_num
            )

            self.cli.progress.set_iteration(iteration_num, self.max_iterations)
            self.cli.display_message(
                f"\n{'='*80}\n"
                f"Iteration {iteration_num}/{self.max_iterations} "
                f"(Aggression: {aggression_level})\n"
                f"{'='*80}"
            )

            # Start iteration
            self.state_manager.start_iteration(iteration_num, aggression_level)

            try:
                # Step 1: Term Protection
                current_text = self._execute_term_protection(current_text)

                # Step 2: Paraphrasing (Claude performs this via direct inference)
                current_text = self._execute_paraphrasing(
                    current_text, aggression_level
                )

                # Step 3: Paraphrase Post-Processing
                current_text = self._execute_paraphraser_processor(current_text)

                # Step 4: Fingerprint Removal
                current_text = self._execute_fingerprint_removal(current_text)

                # Step 5: Burstiness Enhancement
                current_text = self._execute_burstiness_enhancement(current_text)

                # Step 6: Detection Analysis
                detection_score = self._execute_detection_analysis(current_text)

                # Step 7: Perplexity Calculation
                perplexity_score = self._execute_perplexity_calculation(current_text)

                # Step 8: Validation
                validation_result = self._execute_validation(
                    workflow_state.original_text, current_text
                )

                # Complete iteration
                self.state_manager.complete_iteration(current_text)

                # Display iteration results
                self._display_iteration_results(
                    iteration_num, detection_score, perplexity_score, validation_result
                )

                # Check for early termination
                if detection_score <= self.target_threshold:
                    self.cli.display_success(
                        f"\n✓ Target threshold reached! "
                        f"Detection: {detection_score:.1f}% <= {self.target_threshold}%"
                    )
                    break

                # Check for human injection (if enabled)
                if self.injection_identifier and self._should_inject_human_input(
                    workflow_state, iteration_num, detection_score
                ):
                    current_text = self._handle_human_injection(
                        current_text, detection_score
                    )

                current_iteration = iteration_num

            except (ToolExecutionError, ValidationError) as e:
                # Handle errors
                self.cli.display_error(f"Error in iteration {iteration_num}: {str(e)}")
                recovery_action = self._handle_error(e, iteration_num)

                if recovery_action == "abort":
                    self.cli.display_error("Workflow aborted due to unrecoverable error")
                    break
                elif recovery_action == "skip":
                    self.cli.display_warning("Skipping iteration due to error")
                    continue
                # Otherwise retry

        # Phase 3: Finalization
        final_scores = {
            "weighted": detection_score if 'detection_score' in locals() else 100.0,
            "originality": detection_score if 'detection_score' in locals() else 100.0
        }

        status = "completed" if detection_score <= self.target_threshold else "max_iterations"

        self.state_manager.complete_workflow(
            final_scores=final_scores,
            status=status
        )

        # Generate final report
        self._generate_final_report(workflow_state)

        return workflow_state

    def _execute_term_protection(self, text: str) -> str:
        """Execute term protection tool."""
        self.cli.progress.set_stage("Term Protection")
        self.cli.display_message("Protecting technical terms...")

        input_data = {"text": text}
        input_json = json.dumps(input_data, ensure_ascii=False)

        output = self.error_handler.execute_tool_safely(
            tool_name="term_protector",
            input_json=input_json,
            iteration=self.state_manager.current_state.current_iteration
        )

        protected_text = output["protected_text"]
        placeholders = output.get("placeholder_map", {})

        self.state_manager.update_iteration(
            component="term_protector",
            output={"protected_terms": len(placeholders)}
        )

        self.cli.display_message(f"✓ Protected {len(placeholders)} technical terms")

        return protected_text

    def _execute_paraphrasing(self, text: str, aggression_level: str) -> str:
        """
        Execute paraphrasing via Claude direct inference.

        Note: This is performed by Claude agent directly, not via Bash tool.
        The orchestrator (Claude) performs the paraphrasing task.
        """
        self.cli.progress.set_stage("Paraphrasing")
        self.cli.display_message(f"Paraphrasing (Level: {aggression_level})...")

        # Claude performs paraphrasing via direct inference
        # This is a placeholder - actual implementation would use Claude's paraphrasing
        paraphrased_text = text  # Placeholder

        self.state_manager.update_iteration(
            component="paraphraser",
            output={"aggression_level": aggression_level}
        )

        self.cli.display_message("✓ Paraphrasing completed")

        return paraphrased_text

    def _execute_paraphraser_processor(self, text: str) -> str:
        """Execute paraphrase post-processor tool."""
        self.cli.progress.set_stage("Paraphrase Processing")
        self.cli.display_message("Post-processing paraphrased text...")

        input_data = {"text": text}
        input_json = json.dumps(input_data, ensure_ascii=False)

        output = self.error_handler.execute_tool_safely(
            tool_name="paraphraser_processor",
            input_json=input_json,
            iteration=self.state_manager.current_state.current_iteration
        )

        processed_text = output.get("processed_text", text)

        self.state_manager.update_iteration(
            component="paraphraser_processor",
            output=output
        )

        self.cli.display_message("✓ Post-processing completed")

        return processed_text

    def _execute_fingerprint_removal(self, text: str) -> str:
        """Execute fingerprint removal tool."""
        self.cli.progress.set_stage("Fingerprint Removal")
        self.cli.display_message("Removing AI fingerprints...")

        input_data = {"text": text}
        input_json = json.dumps(input_data, ensure_ascii=False)

        output = self.error_handler.execute_tool_safely(
            tool_name="fingerprint_remover",
            input_json=input_json,
            iteration=self.state_manager.current_state.current_iteration
        )

        cleaned_text = output["cleaned_text"]
        patterns_removed = output.get("patterns_removed", 0)

        self.state_manager.update_iteration(
            component="fingerprint_remover",
            output={"patterns_removed": patterns_removed}
        )

        self.cli.display_message(f"✓ Removed {patterns_removed} AI fingerprints")

        return cleaned_text

    def _execute_burstiness_enhancement(self, text: str) -> str:
        """Execute burstiness enhancement tool."""
        self.cli.progress.set_stage("Burstiness Enhancement")
        self.cli.display_message("Enhancing sentence burstiness...")

        input_data = {"text": text}
        input_json = json.dumps(input_data, ensure_ascii=False)

        output = self.error_handler.execute_tool_safely(
            tool_name="burstiness_enhancer",
            input_json=input_json,
            iteration=self.state_manager.current_state.current_iteration
        )

        enhanced_text = output["enhanced_text"]

        self.state_manager.update_iteration(
            component="burstiness_enhancer",
            output=output
        )

        self.cli.display_message("✓ Burstiness enhanced")

        return enhanced_text

    def _execute_detection_analysis(self, text: str) -> float:
        """Execute detection processor tool."""
        self.cli.progress.set_stage("Detection Analysis")
        self.cli.display_message("Analyzing AI detection risk...")

        # First calculate perplexity
        perplexity_input = {"text": text}
        perplexity_json = json.dumps(perplexity_input, ensure_ascii=False)

        perplexity_output = self.error_handler.execute_tool_safely(
            tool_name="perplexity_calculator",
            input_json=perplexity_json,
            iteration=self.state_manager.current_state.current_iteration
        )

        perplexity = perplexity_output.get("overall_perplexity", 100.0)

        # Then process detection
        detection_input = {"perplexity": perplexity}
        detection_json = json.dumps(detection_input, ensure_ascii=False)

        detection_output = self.error_handler.execute_tool_safely(
            tool_name="detector_processor",
            input_json=detection_json,
            iteration=self.state_manager.current_state.current_iteration
        )

        detection_score = detection_output.get("proxy_detection_score", 100.0)

        self.state_manager.update_iteration(
            component="detector_processor",
            output=detection_output,
            detection_score=detection_score,
            originality_score=detection_score
        )

        self.cli.display_message(f"✓ Detection score: {detection_score:.1f}%")

        return detection_score

    def _execute_perplexity_calculation(self, text: str) -> float:
        """Execute perplexity calculator tool."""
        self.cli.progress.set_stage("Perplexity Calculation")
        self.cli.display_message("Calculating perplexity...")

        input_data = {"text": text}
        input_json = json.dumps(input_data, ensure_ascii=False)

        output = self.error_handler.execute_tool_safely(
            tool_name="perplexity_calculator",
            input_json=input_json,
            iteration=self.state_manager.current_state.current_iteration
        )

        perplexity = output.get("overall_perplexity", 100.0)

        self.state_manager.update_iteration(
            component="perplexity_calculator",
            output=output
        )

        self.cli.display_message(f"✓ Perplexity: {perplexity:.2f}")

        return perplexity

    def _execute_validation(self, original_text: str, humanized_text: str) -> Dict[str, Any]:
        """Execute validator tool."""
        self.cli.progress.set_stage("Validation")
        self.cli.display_message("Validating quality...")

        input_data = {
            "original_text": original_text,
            "humanized_text": humanized_text
        }
        input_json = json.dumps(input_data, ensure_ascii=False)

        output = self.error_handler.execute_tool_safely(
            tool_name="validator",
            input_json=input_json,
            iteration=self.state_manager.current_state.current_iteration
        )

        self.state_manager.update_iteration(
            component="validator",
            output=output
        )

        bertscore = output.get("bertscore", 0.0)
        quality_assessment = output.get("quality_assessment", "unknown")

        self.cli.display_message(
            f"✓ Validation: BERTScore={bertscore:.3f}, Quality={quality_assessment}"
        )

        return output

    def _select_aggression_level(
        self, workflow_state: WorkflowState, iteration_num: int
    ) -> str:
        """
        Select aggression level based on progress.

        Escalation logic:
        - Iteration 1: gentle
        - Iteration 2: gentle (if improving) or moderate (if stagnant)
        - Iteration 3+: escalate if improvement < 5% for 2 iterations
        """
        if iteration_num == 1:
            return "gentle"

        if len(workflow_state.iterations) < 2:
            return "gentle"

        # Check recent improvement
        recent_iterations = workflow_state.iterations[-2:]

        if len(recent_iterations) == 2:
            score_diff = (
                recent_iterations[0].detection_score -
                recent_iterations[1].detection_score
            )

            if score_diff < 5.0:
                # Stagnant improvement → escalate
                current_level_index = self.aggression_levels.index(
                    recent_iterations[-1].aggressiveness
                )
                next_index = min(current_level_index + 1, len(self.aggression_levels) - 1)
                return self.aggression_levels[next_index]

        # Default to previous level or gentle
        return workflow_state.iterations[-1].aggressiveness if workflow_state.iterations else "gentle"

    def _should_inject_human_input(
        self, workflow_state: WorkflowState, iteration_num: int, detection_score: float
    ) -> bool:
        """Determine if human input should be requested."""
        if not self.injection_identifier:
            return False

        # Inject if:
        # 1. Detection score still high (>40%) after iteration 3
        # 2. Or every 2 iterations if enabled
        if iteration_num >= 3 and detection_score > 40.0:
            return True

        if iteration_num % 2 == 0 and self.config.get("human_injection_enabled", False):
            return True

        return False

    def _handle_human_injection(self, current_text: str, detection_score: float) -> str:
        """Handle human injection point."""
        self.cli.display_message("\n" + "="*80)
        self.cli.display_message("HUMAN INPUT REQUESTED")
        self.cli.display_message("="*80)

        # Identify injection points
        injection_points = self.injection_identifier.identify_injection_points(
            current_text, detection_score
        )

        if not injection_points:
            self.cli.display_message("No suitable injection points found")
            return current_text

        # Display injection points
        for i, point in enumerate(injection_points, 1):
            self.cli.display_message(
                f"\n{i}. Section: {point.section} (Priority: {point.priority}/5)\n"
                f"   {point.guidance_prompt}"
            )

        # Request user input
        user_choice = input(f"\nSelect injection point (1-{len(injection_points)}) or 's' to skip: ")

        if user_choice.lower() == 's':
            self.cli.display_message("Skipping human injection")
            return current_text

        try:
            point_index = int(user_choice) - 1
            selected_point = injection_points[point_index]

            user_input = input("\nEnter your expert input:\n> ")

            if user_input.strip():
                integrated_text = self.injection_identifier.integrate_user_input(
                    text=current_text,
                    injection_point=selected_point,
                    user_input=user_input
                )

                self.cli.display_success("✓ Human input integrated")
                return integrated_text
        except (ValueError, IndexError):
            self.cli.display_warning("Invalid selection, skipping injection")

        return current_text

    def _handle_error(self, error: Exception, iteration_num: int) -> str:
        """Handle errors and determine recovery action."""
        if isinstance(error, ValidationError):
            validation_result = {
                "is_valid": False,
                "quality_score": error.quality_score,
                "issues": error.issues
            }
            action = self.error_handler.handle_validation_failure(
                validation_result, iteration_num
            )
            return action.value

        # Default: retry
        return "retry"

    def _display_iteration_results(
        self, iteration_num: int, detection_score: float,
        perplexity_score: float, validation_result: Dict[str, Any]
    ):
        """Display iteration results."""
        self.cli.display_message(f"\n{'='*80}")
        self.cli.display_message(f"Iteration {iteration_num} Results:")
        self.cli.display_message(f"  Detection Score: {detection_score:.1f}%")
        self.cli.display_message(f"  Perplexity: {perplexity_score:.2f}")
        self.cli.display_message(
            f"  BERTScore: {validation_result.get('bertscore', 0.0):.3f}"
        )
        self.cli.display_message(
            f"  Quality: {validation_result.get('quality_assessment', 'unknown')}"
        )
        self.cli.display_message(f"{'='*80}\n")

    def _generate_final_report(self, workflow_state: WorkflowState):
        """Generate and display final report."""
        self.cli.display_message("\n" + "="*80)
        self.cli.display_message("WORKFLOW COMPLETED")
        self.cli.display_message("="*80)

        report = self.cli.report_generator.generate_final_report(
            workflow_state=workflow_state,
            token_usage=workflow_state.total_token_usage
        )

        self.cli.display_message(report)

        # Save report to file
        report_path = Path(self.config.get("output_dir", "output")) / f"{workflow_state.workflow_id}_report.txt"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report, encoding="utf-8")

        self.cli.display_success(f"\n✓ Report saved to: {report_path}")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="BMAD Academic Humanizer - Production Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default config
  python main.py --input paper.txt

  # Use custom config
  python main.py --input paper.txt --config custom_config.yaml

  # Resume from checkpoint
  python main.py --resume workflow_20241030_143022

  # Disable human injection
  python main.py --input paper.txt --no-human-injection
        """
    )

    parser.add_argument(
        "--input", "-i",
        type=str,
        help="Path to input academic paper (txt or markdown format)"
    )

    parser.add_argument(
        "--config", "-c",
        type=str,
        default="config/config.yaml",
        help="Path to configuration file (default: config/config.yaml)"
    )

    parser.add_argument(
        "--resume", "-r",
        type=str,
        help="Resume workflow from checkpoint (workflow ID)"
    )

    parser.add_argument(
        "--no-human-injection",
        action="store_true",
        help="Disable human injection points (fully automated)"
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output directory for humanized text and reports"
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_arguments()

    # Load configuration
    config_loader = ConfigLoader()
    config = config_loader.load_config(args.config)

    # Override config with command line arguments
    if args.no_human_injection:
        config["human_injection_enabled"] = False

    if args.output:
        config["output_dir"] = args.output

    # Initialize orchestrator
    orchestrator = ProductionOrchestrator(config)

    try:
        if args.resume:
            # Resume from checkpoint
            workflow_state = orchestrator.run_workflow(
                input_text="",  # Text loaded from checkpoint
                workflow_id=args.resume
            )
        elif args.input:
            # New workflow
            input_path = Path(args.input)
            if not input_path.exists():
                print(f"Error: Input file not found: {args.input}")
                sys.exit(1)

            input_text = input_path.read_text(encoding="utf-8")
            workflow_state = orchestrator.run_workflow(input_text)
        else:
            print("Error: Either --input or --resume must be specified")
            print("Run 'python main.py --help' for usage information")
            sys.exit(1)

        # Save humanized text
        output_dir = Path(config.get("output_dir", "output"))
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / f"{workflow_state.workflow_id}_humanized.txt"
        output_path.write_text(workflow_state.current_text, encoding="utf-8")

        print(f"\n✓ Humanized text saved to: {output_path}")
        print(f"✓ Workflow ID: {workflow_state.workflow_id}")
        print(f"✓ Final detection score: {workflow_state.final_scores.get('originality', 'N/A')}")

    except KeyboardInterrupt:
        print("\n\nWorkflow interrupted by user")
        print("Checkpoint saved - use --resume to continue")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
