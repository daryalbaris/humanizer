"""
CLI Interface for BMAD Orchestrator

Provides user interaction, progress indicators, and reporting for the
orchestrator workflow.
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime


class ProgressIndicator:
    """Progress indicator for workflow stages."""

    STAGES = [
        "Initialization",
        "Term Protection",
        "Paraphrasing",
        "Fingerprint Removal",
        "Burstiness Enhancement",
        "Detection Analysis",
        "Validation",
        "Human Injection",
        "Iteration Complete"
    ]

    def __init__(self):
        self.current_stage = 0
        self.current_iteration = 0
        self.max_iterations = 7

    def set_iteration(self, iteration: int, max_iterations: int):
        """Set current iteration."""
        self.current_iteration = iteration
        self.max_iterations = max_iterations

    def set_stage(self, stage_name: str):
        """Set current stage."""
        if stage_name in self.STAGES:
            self.current_stage = self.STAGES.index(stage_name)

    def display(self, detection_score: Optional[float] = None):
        """Display progress indicator."""
        stage_name = self.STAGES[self.current_stage] if self.current_stage < len(self.STAGES) else "Complete"

        # Progress bar
        progress_pct = (self.current_stage / len(self.STAGES)) * 100
        bar_length = 30
        filled = int((progress_pct / 100) * bar_length)
        bar = '█' * filled + '░' * (bar_length - filled)

        # Detection score indicator
        score_indicator = ""
        if detection_score is not None:
            if detection_score < 20:
                score_indicator = f"✓ Score: {detection_score:.1f}% (Target achieved!)"
            elif detection_score < 30:
                score_indicator = f"→ Score: {detection_score:.1f}% (Close to target)"
            else:
                score_indicator = f"⚠ Score: {detection_score:.1f}% (Needs improvement)"

        print(f"\n{'='*80}")
        print(f"Iteration: {self.current_iteration}/{self.max_iterations} | Stage: {stage_name}")
        print(f"Progress: [{bar}] {progress_pct:.1f}%")
        if score_indicator:
            print(f"{score_indicator}")
        print(f"{'='*80}\n")


class TokenTracker:
    """Track token usage and estimate costs."""

    # Cost per 1000 tokens (example rates, adjust based on actual API)
    COST_PER_1K_TOKENS = {
        "prompt": 0.01,  # $0.01 per 1K prompt tokens
        "completion": 0.03  # $0.03 per 1K completion tokens
    }

    def __init__(self):
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_tokens = 0

    def add_usage(self, prompt_tokens: int, completion_tokens: int):
        """Add token usage."""
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        self.total_tokens = self.total_prompt_tokens + self.total_completion_tokens

    def get_cost_estimate(self) -> float:
        """Calculate estimated cost."""
        prompt_cost = (self.total_prompt_tokens / 1000) * self.COST_PER_1K_TOKENS["prompt"]
        completion_cost = (self.total_completion_tokens / 1000) * self.COST_PER_1K_TOKENS["completion"]
        return prompt_cost + completion_cost

    def display_summary(self):
        """Display token usage summary."""
        print(f"\n{'='*80}")
        print("TOKEN USAGE SUMMARY")
        print(f"{'='*80}")
        print(f"Prompt tokens:     {self.total_prompt_tokens:,}")
        print(f"Completion tokens: {self.total_completion_tokens:,}")
        print(f"Total tokens:      {self.total_tokens:,}")
        print(f"Estimated cost:    ${self.get_cost_estimate():.4f}")
        print(f"{'='*80}\n")


class ConfigLoader:
    """Load and validate YAML configuration."""

    DEFAULT_CONFIG = {
        "max_iterations": 7,
        "target_originality_threshold": 20.0,
        "early_termination_improvement": 2.0,
        "aggressiveness_levels": ["subtle", "moderate", "aggressive"],
        "default_aggressiveness": "moderate",
        "human_injection_enabled": True,
        "max_injection_points": 5,
        "checkpoint_enabled": True,
        "checkpoint_dir": "checkpoints",
        "backup_dir": "checkpoints/backups"
    }

    @staticmethod
    def load(config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to config file (optional)

        Returns:
            Configuration dictionary
        """
        config = ConfigLoader.DEFAULT_CONFIG.copy()

        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    loaded_config = yaml.safe_load(f)
                    if loaded_config:
                        config.update(loaded_config)
                print(f"✓ Loaded configuration from: {config_path}")
            except Exception as e:
                print(f"⚠ Error loading config file: {e}")
                print("Using default configuration")

        return config

    @staticmethod
    def display(config: Dict[str, Any]):
        """Display configuration."""
        print(f"\n{'='*80}")
        print("CONFIGURATION")
        print(f"{'='*80}")
        print(f"Max iterations:              {config.get('max_iterations')}")
        print(f"Target Originality.ai:       {config.get('target_originality_threshold')}%")
        print(f"Early termination threshold: {config.get('early_termination_improvement')}%")
        print(f"Default aggressiveness:      {config.get('default_aggressiveness')}")
        print(f"Human injection:             {'Enabled' if config.get('human_injection_enabled') else 'Disabled'}")
        print(f"Max injection points:        {config.get('max_injection_points')}")
        print(f"Checkpoint directory:        {config.get('checkpoint_dir')}")
        print(f"{'='*80}\n")


class ReportGenerator:
    """Generate final workflow report."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize report generator.

        Args:
            config: Configuration dictionary (optional)
        """
        self.config = config

    @staticmethod
    def generate(
        workflow_state: Dict[str, Any],
        token_usage: Dict[str, int],
        execution_time_seconds: float
    ) -> str:
        """
        Generate final report.

        Args:
            workflow_state: Workflow state summary
            token_usage: Token usage data
            execution_time_seconds: Total execution time

        Returns:
            Formatted report string
        """
        report = f"""
{'='*80}
BMAD ACADEMIC HUMANIZER - FINAL REPORT
{'='*80}

Workflow ID: {workflow_state.get('workflow_id', 'N/A')}
Status: {workflow_state.get('status', 'N/A').upper()}
Started: {workflow_state.get('started_at', 'N/A')}
Completed: {workflow_state.get('completed_at', 'N/A')}
Execution Time: {execution_time_seconds:.1f} seconds ({execution_time_seconds/60:.1f} minutes)

{'='*80}
ITERATIONS SUMMARY
{'='*80}
Total Iterations: {workflow_state.get('iterations_completed', 0)}/{workflow_state.get('max_iterations', 0)}
Target threshold: {workflow_state.get('target_threshold', 0)}%

DETECTION SCORES:
"""

        # Final scores
        final_scores = workflow_state.get('final_scores', {})
        if final_scores:
            report += f"  Final Detection Score: {final_scores.get('weighted', 0):.1f}%\n"
            report += f"  Originality.ai:   {final_scores.get('originality', 0):.1f}%\n"
            report += f"  GPTZero:          {final_scores.get('gptzero', 0):.1f}%\n"
        else:
            report += "  No final scores available\n"

        # Current scores
        current_scores = workflow_state.get('current_scores', {})
        if current_scores:
            report += f"\nCURRENT SCORES:\n"
            report += f"  Detection:        {current_scores.get('detection', 0):.1f}%\n"
            report += f"  Originality:      {current_scores.get('originality', 0):.1f}%\n"
            report += f"  GPTZero:          {current_scores.get('gptzero', 0):.1f}%\n"

        # Human injection
        report += f"""
{'='*80}
HUMAN INJECTION
{'='*80}
Injection points identified: {workflow_state.get('injection_points', 0)}
Human inputs provided: {workflow_state.get('human_inputs', 0)}

{'='*80}
TOKEN USAGE & COST
{'='*80}
Token Usage:
  Prompt tokens:     {token_usage.get('prompt_tokens', 0):,}
  Completion tokens: {token_usage.get('completion_tokens', 0):,}
  Total tokens:      {token_usage.get('total_tokens', 0):,}
"""

        # Cost estimate
        tracker = TokenTracker()
        tracker.add_usage(
            token_usage.get('prompt_tokens', 0),
            token_usage.get('completion_tokens', 0)
        )
        report += f"Estimated cost:    ${tracker.get_cost_estimate():.4f}\n"

        report += f"""
{'='*80}
RESULT SUMMARY
{'='*80}
"""

        # Success/failure indicator
        target = workflow_state.get('target_threshold', 20)
        final_score = final_scores.get('originality', 100) if final_scores else 100

        if final_score <= target:
            report += f"✓ SUCCESS: Target achieved ({final_score:.1f}% ≤ {target}%)\n"
        elif final_score <= target + 10:
            report += f"→ PARTIAL: Close to target ({final_score:.1f}% vs {target}%)\n"
        else:
            report += f"✗ INCOMPLETE: Target not reached ({final_score:.1f}% > {target}%)\n"

        report += f"\n{'='*80}\n"

        return report

    def generate_final_report(
        self,
        workflow_state: Dict[str, Any],
        token_usage: Dict[str, int]
    ) -> str:
        """
        Generate final report (instance method wrapper).

        Args:
            workflow_state: Workflow state summary (dict or WorkflowState dataclass)
            token_usage: Token usage data

        Returns:
            Formatted report string
        """
        # Convert WorkflowState dataclass to dict if needed
        from dataclasses import is_dataclass, asdict
        if is_dataclass(workflow_state) and not isinstance(workflow_state, type):
            state_dict = asdict(workflow_state)
        else:
            state_dict = workflow_state

        # Calculate execution time from workflow state
        execution_time = state_dict.get('execution_time', 0.0)

        return self.generate(
            workflow_state=state_dict,
            token_usage=token_usage,
            execution_time_seconds=execution_time
        )


class CLIInterface:
    """Main CLI interface for user interaction."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize CLI interface.

        Args:
            config: Configuration dictionary
        """
        self.config = config or ConfigLoader.load()
        self.progress = ProgressIndicator()
        self.token_tracker = TokenTracker()

    def display_welcome(self):
        """Display welcome message."""
        print(f"\n{'='*80}")
        print(" " * 20 + "BMAD ACADEMIC HUMANIZER")
        print(" " * 15 + "Burstiness - Memory - Awareness - Detection")
        print(f"{'='*80}\n")

    def prompt_user_input(self, prompt: str, default: Optional[str] = None) -> str:
        """
        Prompt user for input.

        Args:
            prompt: Prompt message
            default: Default value if user presses Enter

        Returns:
            User input
        """
        if default:
            prompt = f"{prompt} [{default}]: "
        else:
            prompt = f"{prompt}: "

        user_input = input(prompt).strip()

        if not user_input and default:
            return default

        return user_input

    def prompt_yes_no(self, prompt: str, default: bool = True) -> bool:
        """
        Prompt user for yes/no.

        Args:
            prompt: Prompt message
            default: Default value

        Returns:
            True for yes, False for no
        """
        default_str = "Y/n" if default else "y/N"
        response = self.prompt_user_input(f"{prompt} [{default_str}]", "y" if default else "n")

        return response.lower() in ['y', 'yes']

    def display_error(self, message: str, recoverable: bool = True):
        """
        Display error message.

        Args:
            message: Error message
            recoverable: Whether error is recoverable
        """
        print(f"\n{'='*80}")
        print(f"{'⚠ ERROR' if recoverable else '✗ FATAL ERROR'}")
        print(f"{'='*80}")
        print(f"{message}")
        print(f"{'='*80}\n")

    def prompt_error_recovery(self) -> str:
        """
        Prompt user for error recovery action.

        Returns:
            Recovery action: 'retry', 'skip', 'abort'
        """
        print("Recovery options:")
        print("  1. Retry the operation")
        print("  2. Skip this step and continue")
        print("  3. Abort workflow")

        while True:
            choice = self.prompt_user_input("Select option (1-3)", "1")
            if choice in ['1', '2', '3']:
                return ['retry', 'skip', 'abort'][int(choice) - 1]
            print("Invalid choice. Please enter 1, 2, or 3.")

    def update_progress(
        self,
        stage: str,
        iteration: int,
        max_iterations: int,
        detection_score: Optional[float] = None
    ):
        """Update and display progress."""
        self.progress.set_iteration(iteration, max_iterations)
        self.progress.set_stage(stage)
        self.progress.display(detection_score)

    def display_final_report(
        self,
        workflow_state: Dict[str, Any],
        execution_time_seconds: float
    ):
        """Display final report."""
        report = ReportGenerator.generate(
            workflow_state,
            workflow_state.get('total_token_usage', {}),
            execution_time_seconds
        )
        print(report)

        # Ask to save report
        if self.prompt_yes_no("Save report to file?", default=True):
            filename = f"bmad_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(report)
                print(f"✓ Report saved to: {filename}")
            except Exception as e:
                print(f"✗ Error saving report: {e}")


# Example usage
if __name__ == "__main__":
    # Load configuration
    config = ConfigLoader.load()
    ConfigLoader.display(config)

    # Initialize CLI
    cli = CLIInterface(config)
    cli.display_welcome()

    # Simulate workflow progress
    for iteration in range(1, 4):
        for stage in ProgressIndicator.STAGES[:-1]:
            cli.update_progress(stage, iteration, config['max_iterations'], detection_score=50.0 - iteration * 10)
            import time
            time.sleep(0.5)

    # Display final report
    mock_state = {
        "workflow_id": "test_001",
        "status": "completed",
        "started_at": "2024-01-15T10:00:00",
        "completed_at": "2024-01-15T10:25:00",
        "iterations_completed": 3,
        "max_iterations": 7,
        "target_threshold": 20.0,
        "final_scores": {"weighted": 18.5, "originality": 18.5, "gptzero": 22.3},
        "injection_points": 4,
        "human_inputs": 2,
        "total_token_usage": {"prompt_tokens": 15000, "completion_tokens": 8000, "total_tokens": 23000}
    }

    cli.display_final_report(mock_state, 1500)
