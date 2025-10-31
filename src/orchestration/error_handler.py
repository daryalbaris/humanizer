"""
Error Handling and Recovery for BMAD Orchestrator

Provides comprehensive error handling, recovery strategies, and graceful
degradation for the workflow orchestrator.
"""

import json
import subprocess
import logging
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels."""
    WARNING = "warning"  # Non-critical, can continue
    ERROR = "error"  # Recoverable, retry possible
    FATAL = "fatal"  # Unrecoverable, must abort


class RecoveryAction(Enum):
    """Recovery action types."""
    RETRY = "retry"  # Retry the operation
    SKIP = "skip"  # Skip and continue
    ABORT = "abort"  # Abort workflow
    MANUAL = "manual"  # Requires manual intervention


@dataclass
class ErrorContext:
    """Context information for an error."""
    component: str
    operation: str
    error_message: str
    severity: ErrorSeverity
    iteration: int
    recoverable: bool
    suggestion: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ToolExecutionError(Exception):
    """Exception raised when a tool execution fails."""
    def __init__(self, component: str, message: str, exit_code: int = 1):
        self.component = component
        self.message = message
        self.exit_code = exit_code
        super().__init__(f"{component}: {message}")


class ValidationError(Exception):
    """Exception raised when validation fails."""
    def __init__(self, quality_score: float, issues: list):
        self.quality_score = quality_score
        self.issues = issues
        super().__init__(f"Validation failed: {', '.join(issues)}")


class WorkflowError(Exception):
    """Exception raised for workflow-level errors."""
    pass


class ErrorHandler:
    """
    Centralized error handling and recovery for BMAD orchestrator.

    Features:
    - Tool execution error handling
    - Validation failure recovery
    - Checkpoint recovery on unexpected termination
    - Retry mechanisms with exponential backoff
    - User-guided error resolution
    """

    def __init__(
        self,
        max_retries: int = 3,
        retry_delay_seconds: int = 2,
        enable_logging: bool = True
    ):
        """
        Initialize error handler.

        Args:
            max_retries: Maximum retry attempts per operation
            retry_delay_seconds: Initial delay between retries
            enable_logging: Enable error logging
        """
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds
        self.enable_logging = enable_logging

        if enable_logging:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = None

        self.error_history = []

    def log_error(self, context: ErrorContext):
        """
        Log error with context.

        Args:
            context: Error context information
        """
        self.error_history.append(context)

        if self.logger:
            self.logger.error(
                f"[{context.severity.value.upper()}] {context.component} - "
                f"{context.operation}: {context.error_message}"
            )

    def execute_tool_safely(
        self,
        tool_name: str,
        input_json: str,
        timeout: int = 60,
        iteration: int = 0
    ) -> Dict[str, Any]:
        """
        Execute Python tool with error handling and retries.

        Args:
            tool_name: Tool name (without _cli.py suffix)
            input_json: JSON input string
            timeout: Execution timeout in seconds
            iteration: Current iteration number

        Returns:
            Tool output as dictionary

        Raises:
            ToolExecutionError: If execution fails after retries
        """
        import time

        for attempt in range(self.max_retries):
            try:
                result = subprocess.run(
                    ['python', f'src/orchestration/tools/{tool_name}_cli.py'],
                    input=input_json,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )

                # Check exit code
                if result.returncode != 0:
                    try:
                        error_output = json.loads(result.stdout) if result.stdout else {}
                        error_message = error_output.get('error', result.stderr or 'Unknown error')
                    except json.JSONDecodeError:
                        error_message = result.stderr or 'Invalid output'

                    # Log error
                    context = ErrorContext(
                        component=tool_name,
                        operation="execute",
                        error_message=error_message,
                        severity=ErrorSeverity.ERROR,
                        iteration=iteration,
                        recoverable=True,
                        suggestion=f"Retry {attempt + 1}/{self.max_retries}"
                    )
                    self.log_error(context)

                    # Retry with backoff
                    if attempt < self.max_retries - 1:
                        delay = self.retry_delay_seconds * (2 ** attempt)
                        if self.logger:
                            self.logger.info(f"Retrying in {delay} seconds...")
                        time.sleep(delay)
                        continue
                    else:
                        raise ToolExecutionError(tool_name, error_message, result.returncode)

                # Parse output
                try:
                    output = json.loads(result.stdout)

                    # Check for error in output
                    if 'error' in output:
                        context = ErrorContext(
                            component=tool_name,
                            operation="execute",
                            error_message=output['error'],
                            severity=ErrorSeverity.ERROR,
                            iteration=iteration,
                            recoverable=True
                        )
                        self.log_error(context)

                        if attempt < self.max_retries - 1:
                            delay = self.retry_delay_seconds * (2 ** attempt)
                            time.sleep(delay)
                            continue
                        else:
                            raise ToolExecutionError(tool_name, output['error'])

                    return output

                except json.JSONDecodeError as e:
                    context = ErrorContext(
                        component=tool_name,
                        operation="parse_output",
                        error_message=f"Invalid JSON output: {str(e)}",
                        severity=ErrorSeverity.ERROR,
                        iteration=iteration,
                        recoverable=False
                    )
                    self.log_error(context)
                    raise ToolExecutionError(tool_name, f"Invalid JSON output: {str(e)}")

            except subprocess.TimeoutExpired:
                context = ErrorContext(
                    component=tool_name,
                    operation="execute",
                    error_message=f"Timeout after {timeout} seconds",
                    severity=ErrorSeverity.ERROR,
                    iteration=iteration,
                    recoverable=True,
                    suggestion="Increase timeout or simplify input"
                )
                self.log_error(context)

                if attempt < self.max_retries - 1:
                    delay = self.retry_delay_seconds * (2 ** attempt)
                    time.sleep(delay)
                    continue
                else:
                    raise ToolExecutionError(tool_name, f"Timeout after {timeout} seconds")

            except Exception as e:
                context = ErrorContext(
                    component=tool_name,
                    operation="execute",
                    error_message=str(e),
                    severity=ErrorSeverity.FATAL,
                    iteration=iteration,
                    recoverable=False
                )
                self.log_error(context)
                raise ToolExecutionError(tool_name, str(e))

    def handle_validation_failure(
        self,
        validation_result: Dict[str, Any],
        iteration: int
    ) -> RecoveryAction:
        """
        Handle validation failure with user guidance.

        Args:
            validation_result: Validation result dictionary
            iteration: Current iteration number

        Returns:
            Recovery action
        """
        quality_score = validation_result.get('quality_score', 0.0)
        issues = validation_result.get('issues', [])

        context = ErrorContext(
            component="validator",
            operation="validate",
            error_message=f"Quality score {quality_score}/10.0 below threshold",
            severity=ErrorSeverity.WARNING if quality_score >= 6.0 else ErrorSeverity.ERROR,
            iteration=iteration,
            recoverable=True,
            suggestion="Increase aggression level or review content",
            metadata={"quality_score": quality_score, "issues": issues}
        )
        self.log_error(context)

        # Determine recovery action based on severity
        if quality_score >= 6.0:
            # Marginal failure, can continue
            return RecoveryAction.SKIP
        elif quality_score >= 4.0:
            # Moderate failure, retry recommended
            return RecoveryAction.RETRY
        else:
            # Severe failure, manual intervention needed
            return RecoveryAction.MANUAL

    def handle_detection_anomaly(
        self,
        current_score: float,
        previous_score: float,
        iteration: int
    ) -> Optional[str]:
        """
        Handle anomalous detection score changes.

        Args:
            current_score: Current detection score
            previous_score: Previous detection score
            iteration: Current iteration number

        Returns:
            Warning message if anomaly detected, None otherwise
        """
        score_change = current_score - previous_score

        # Score increased (worse)
        if score_change > 10:
            context = ErrorContext(
                component="detector",
                operation="analyze",
                error_message=f"Detection score increased by {score_change:.1f}%",
                severity=ErrorSeverity.WARNING,
                iteration=iteration,
                recoverable=True,
                suggestion="Review recent changes, consider reverting to previous iteration"
            )
            self.log_error(context)

            return (
                f"⚠ WARNING: Detection score increased by {score_change:.1f}%\n"
                f"Previous: {previous_score:.1f}% → Current: {current_score:.1f}%\n"
                f"Suggestion: Review recent changes or revert to checkpoint"
            )

        return None

    def handle_checkpoint_recovery(
        self,
        workflow_id: str,
        state_manager
    ) -> bool:
        """
        Attempt to recover workflow from checkpoint.

        Args:
            workflow_id: Workflow identifier
            state_manager: State manager instance

        Returns:
            True if recovery successful, False otherwise
        """
        try:
            workflow_state = state_manager.load_workflow(workflow_id)

            if workflow_state is None:
                context = ErrorContext(
                    component="state_manager",
                    operation="load_checkpoint",
                    error_message=f"No checkpoint found for workflow {workflow_id}",
                    severity=ErrorSeverity.ERROR,
                    iteration=0,
                    recoverable=False
                )
                self.log_error(context)
                return False

            if self.logger:
                self.logger.info(
                    f"✓ Recovered workflow {workflow_id} from checkpoint\n"
                    f"  Last iteration: {workflow_state.current_iteration}\n"
                    f"  Status: {workflow_state.status}"
                )

            return True

        except Exception as e:
            context = ErrorContext(
                component="state_manager",
                operation="load_checkpoint",
                error_message=str(e),
                severity=ErrorSeverity.FATAL,
                iteration=0,
                recoverable=False
            )
            self.log_error(context)
            return False

    def get_recovery_strategy(
        self,
        error_type: str,
        attempt_count: int
    ) -> RecoveryAction:
        """
        Determine recovery strategy based on error type and attempt count.

        Args:
            error_type: Type of error
            attempt_count: Number of attempts made

        Returns:
            Recommended recovery action
        """
        strategies = {
            "tool_execution": {
                1: RecoveryAction.RETRY,
                2: RecoveryAction.RETRY,
                3: RecoveryAction.MANUAL
            },
            "validation": {
                1: RecoveryAction.RETRY,
                2: RecoveryAction.SKIP,
                3: RecoveryAction.MANUAL
            },
            "detection_anomaly": {
                1: RecoveryAction.RETRY,
                2: RecoveryAction.MANUAL,
                3: RecoveryAction.ABORT
            }
        }

        strategy = strategies.get(error_type, {})
        return strategy.get(attempt_count, RecoveryAction.ABORT)

    def format_error_report(self) -> str:
        """
        Generate error report from error history.

        Returns:
            Formatted error report
        """
        if not self.error_history:
            return "No errors recorded."

        report = f"\n{'='*80}\nERROR REPORT\n{'='*80}\n"
        report += f"Total errors: {len(self.error_history)}\n\n"

        # Group by severity
        by_severity = {}
        for error in self.error_history:
            severity = error.severity.value
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(error)

        for severity, errors in by_severity.items():
            report += f"\n{severity.upper()} ({len(errors)}):\n"
            report += f"{'-'*80}\n"

            for i, error in enumerate(errors, 1):
                report += f"{i}. [{error.component}] {error.operation}\n"
                report += f"   Iteration: {error.iteration}\n"
                report += f"   Message: {error.error_message}\n"
                if error.suggestion:
                    report += f"   Suggestion: {error.suggestion}\n"
                report += "\n"

        report += f"{'='*80}\n"
        return report


# Example usage
if __name__ == "__main__":
    handler = ErrorHandler(max_retries=3, retry_delay_seconds=2)

    # Test tool execution
    try:
        input_json = json.dumps({"text": "Sample text"})
        result = handler.execute_tool_safely(
            tool_name="fingerprint_remover",
            input_json=input_json,
            iteration=1
        )
        print("✓ Tool execution successful")
        print(json.dumps(result, indent=2))

    except ToolExecutionError as e:
        print(f"✗ Tool execution failed: {e}")

    # Display error report
    print(handler.format_error_report())
