"""
AI Humanizer System - Main Orchestrator
========================================

Coordinates the complete humanization workflow pipeline.
Manages tool execution, iteration loops, quality gates, and adaptive aggression.

Author: BMAD Development Team
Date: 2025-10-31
Version: 1.0
Phase: Phase 2 - Core Architecture
"""

import json
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestration import (
    StateManager,
    WorkflowState,
    ErrorHandler,
    ErrorContext,
    ErrorSeverity,
    ToolExecutionError
)
from utils.logger import get_logger
from utils.exceptions import ProcessingError, ValidationError

# Initialize logger
logger = get_logger(__name__)


class Orchestrator:
    """
    Main orchestrator for the AI Humanizer pipeline.

    Coordinates:
    - Tool pipeline execution (term_protector → paraphraser → ... → validator)
    - Iterative refinement (up to 7 iterations)
    - Quality gate evaluation (detection threshold)
    - Adaptive aggression adjustment
    - Checkpoint/resume capability

    Attributes:
        config (dict): System configuration
        state_manager (StateManager): Workflow state management
        error_handler (ErrorHandler): Error handling and recovery
        tool_paths (dict): Paths to tool executables
        aggression_levels (dict): Aggression level mapping
    """

    # Tool execution order
    TOOL_PIPELINE = [
        "term_protector",
        "paraphraser_processor",
        "fingerprint_remover",
        "imperfection_injector",
        "burstiness_enhancer",
        "reference_analyzer",
        "detector_processor",
        "perplexity_calculator",
        "validator"
    ]

    # Aggression level numeric mapping
    AGGRESSION_MAP = {
        "gentle": 1,
        "moderate": 2,
        "aggressive": 3,
        "intensive": 4,
        "nuclear": 5
    }

    REVERSE_AGGRESSION_MAP = {
        1: "gentle",
        2: "moderate",
        3: "aggressive",
        4: "intensive",
        5: "nuclear"
    }

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize orchestrator with configuration.

        Args:
            config: System configuration dictionary
                Required keys:
                - humanizer.max_iterations (int)
                - humanizer.detection_threshold (float)
                - humanizer.early_termination_improvement (float)
                - paths.glossary (str)
                - paths.checkpoint_dir (str)
                - components.paraphraser.default_aggression (str)
        """
        self.config = config

        # Initialize state manager
        checkpoint_dir = config.get("paths", {}).get("checkpoint_dir", ".humanizer/checkpoints")
        backup_dir = f"{checkpoint_dir}/backups"
        self.state_manager = StateManager(checkpoint_dir=checkpoint_dir, backup_dir=backup_dir)

        # Initialize error handler
        self.error_handler = ErrorHandler()

        # Set up tool paths
        self.tool_paths = self._initialize_tool_paths()

        # Configuration shortcuts
        self.max_iterations = config.get("humanizer", {}).get("max_iterations", 7)
        self.detection_threshold = config.get("humanizer", {}).get("detection_threshold", 0.15)
        self.early_termination_improvement = config.get("humanizer", {}).get("early_termination_improvement", 0.02)

        logger.info(
            "Orchestrator initialized",
            context={
                "max_iterations": self.max_iterations,
                "detection_threshold": self.detection_threshold,
                "checkpoint_dir": checkpoint_dir
            }
        )

    def _initialize_tool_paths(self) -> Dict[str, Path]:
        """
        Initialize paths to all tool executables.

        Returns:
            Dictionary mapping tool names to Path objects
        """
        base_path = Path(__file__).parent.parent / "tools"
        tool_paths = {}

        for tool_name in self.TOOL_PIPELINE:
            tool_file = base_path / f"{tool_name}.py"
            if not tool_file.exists():
                logger.warning(
                    f"Tool file not found: {tool_name}",
                    context={"path": str(tool_file)}
                )
            tool_paths[tool_name] = tool_file

        return tool_paths

    def run_pipeline(
        self,
        input_text: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run the complete humanization pipeline.

        Args:
            input_text: Original text to humanize
            options: Optional parameters:
                - workflow_id (str): Resume existing workflow
                - glossary_path (str): Custom glossary
                - initial_aggression (str): Starting aggression level
                - max_iterations (int): Override default max iterations

        Returns:
            Dictionary containing:
            - status (str): "completed", "failed", or "in_progress"
            - workflow_id (str): Workflow identifier
            - final_text (str): Humanized text
            - iterations (int): Number of iterations performed
            - final_scores (dict): Final detection scores
            - history (list): Iteration history
        """
        options = options or {}

        # Check for resume
        workflow_id = options.get("workflow_id")
        if workflow_id:
            logger.info(f"Resuming workflow: {workflow_id}")
            state = self.state_manager.load_workflow(workflow_id)
            if state is None:
                raise ProcessingError(f"Workflow not found: {workflow_id}")
        else:
            # Create new workflow
            workflow_id = options.get("workflow_id") or str(uuid.uuid4())[:8]
            logger.info(f"Creating new workflow: {workflow_id}")
            state = self.state_manager.create_workflow(
                workflow_id=workflow_id,
                original_text=input_text,
                target_originality_threshold=self.detection_threshold * 100,  # Convert to percentage
                max_iterations=options.get("max_iterations", self.max_iterations)
            )

        # Get initial aggression level
        initial_aggression = options.get(
            "initial_aggression",
            self.config.get("components", {}).get("paraphraser", {}).get("default_aggression", "moderate")
        )

        try:
            # Run iterations
            for iteration in range(state.current_iteration + 1, state.max_iterations + 1):
                logger.info(f"Starting iteration {iteration}/{state.max_iterations}")

                # Determine aggression level
                if iteration == 1:
                    aggression = initial_aggression
                else:
                    # Adjust aggression based on previous iteration
                    prev_iter = state.iterations[-1]
                    current_score = prev_iter.detection_score
                    aggression = self.adjust_aggression(current_score, self.detection_threshold * 100)

                # Execute iteration
                iteration_result = self.execute_iteration(
                    text=state.current_text,
                    iteration=iteration,
                    aggression=aggression,
                    glossary_path=options.get("glossary_path", self.config.get("paths", {}).get("glossary"))
                )

                # Update state
                state.current_text = iteration_result["processed_text"]
                state.current_iteration = iteration

                # Check quality gates
                if self.evaluate_quality_gates(iteration_result):
                    logger.info(
                        f"Quality gate passed at iteration {iteration}",
                        context={"detection_score": iteration_result.get("detection_score")}
                    )
                    self.state_manager.complete_workflow(
                        final_scores={
                            "weighted": iteration_result.get("detection_score", 0),
                            "originality": iteration_result.get("originality_score", 0)
                        },
                        status="completed"
                    )
                    break

                # Check early termination
                if iteration > 1 and self._should_terminate_early(state):
                    logger.info(
                        f"Early termination at iteration {iteration}",
                        context={"reason": "insufficient_improvement"}
                    )
                    self.state_manager.complete_workflow(
                        final_scores={
                            "weighted": iteration_result.get("detection_score", 0),
                            "originality": iteration_result.get("originality_score", 0)
                        },
                        status="completed"
                    )
                    break

            # Max iterations reached
            if state.current_iteration >= state.max_iterations:
                logger.info(f"Max iterations reached: {state.max_iterations}")
                last_iter = state.iterations[-1]
                self.state_manager.complete_workflow(
                    final_scores={
                        "weighted": last_iter.detection_score,
                        "originality": last_iter.originality_score
                    },
                    status="completed"
                )

            # Return final results
            return self._format_results(state)

        except Exception as e:
            logger.error(
                f"Pipeline execution failed",
                context={"workflow_id": workflow_id, "error": str(e)}
            )
            self.state_manager.complete_workflow(
                final_scores={},
                status="failed"
            )
            raise ProcessingError(f"Pipeline execution failed: {str(e)}")

    def execute_iteration(
        self,
        text: str,
        iteration: int,
        aggression: str,
        glossary_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a single iteration of the tool pipeline.

        Args:
            text: Input text for this iteration
            iteration: Iteration number (1-based)
            aggression: Aggression level ("gentle", "moderate", "aggressive", "intensive", "nuclear")
            glossary_path: Path to glossary file

        Returns:
            Dictionary containing:
            - processed_text (str): Output text
            - detection_score (float): AI detection score (0-100)
            - originality_score (float): Originality score
            - components_executed (list): List of tools executed
            - errors (list): Any errors encountered
        """
        logger.info(
            f"Executing iteration {iteration}",
            context={"aggression": aggression}
        )

        # Start iteration in state manager
        self.state_manager.start_iteration(iteration, aggression)

        current_text = text
        components_executed = []
        errors = []
        final_scores = {
            "detection_score": 0,
            "originality_score": 0,
            "perplexity": 0
        }

        # Execute tool pipeline
        for tool_name in self.TOOL_PIPELINE:
            try:
                logger.info(f"Executing tool: {tool_name}")

                # Prepare tool input
                tool_input = self._prepare_tool_input(
                    tool_name=tool_name,
                    text=current_text,
                    aggression=aggression,
                    glossary_path=glossary_path
                )

                # Execute tool
                tool_output = self._execute_tool(tool_name, tool_input)

                # Update state
                components_executed.append(tool_name)
                self.state_manager.update_iteration(
                    component=tool_name,
                    output=tool_output
                )

                # Extract text and scores
                current_text = self._extract_text_from_output(tool_name, tool_output)
                self._extract_scores(tool_name, tool_output, final_scores)

            except Exception as e:
                error_msg = f"Tool {tool_name} failed: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)

                # Log error context
                context = ErrorContext(
                    component=tool_name,
                    operation="execute",
                    error_message=str(e),
                    severity=ErrorSeverity.ERROR,
                    iteration=iteration,
                    recoverable=False
                )
                self.error_handler.log_error(context)

                # Continue with next tool (non-critical errors)
                if tool_name not in ["paraphraser_processor", "validator"]:
                    continue
                else:
                    raise ToolExecutionError(component=tool_name, message=f"Critical tool failed: {str(e)}")

        # Complete iteration
        self.state_manager.complete_iteration(current_text)

        # Set scores in state
        if final_scores["detection_score"] > 0:
            current_iter = self.state_manager.current_state.iterations[-1]
            current_iter.detection_score = final_scores["detection_score"]
            current_iter.originality_score = final_scores.get("originality_score", 0)
            current_iter.gptzero_score = final_scores.get("gptzero_score", 0)
            self.state_manager.save_checkpoint()

        return {
            "processed_text": current_text,
            "detection_score": final_scores["detection_score"],
            "originality_score": final_scores.get("originality_score", 0),
            "perplexity": final_scores.get("perplexity", 0),
            "components_executed": components_executed,
            "errors": errors
        }

    def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool via subprocess.

        Args:
            tool_name: Name of the tool to execute
            tool_input: Input data for the tool (JSON)

        Returns:
            Tool output as dictionary

        Raises:
            ToolExecutionError: If tool execution fails
        """
        tool_path = self.tool_paths.get(tool_name)
        if not tool_path or not tool_path.exists():
            raise ToolExecutionError(component=tool_name, message="Tool not found")

        try:
            # Convert input to JSON
            input_json = json.dumps(tool_input)

            # Execute tool
            result = subprocess.run(
                [sys.executable, str(tool_path)],
                input=input_json,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            # Check for errors
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else "Unknown error"
                raise ToolExecutionError(component=tool_name, message=f"Returned non-zero exit code: {error_msg}")

            # Parse output
            output = json.loads(result.stdout)

            # Check status
            if output.get("status") == "error":
                raise ToolExecutionError(component=tool_name, message=f"Tool reported error: {output.get('error')}")

            return output

        except subprocess.TimeoutExpired:
            raise ToolExecutionError(component=tool_name, message="Tool timed out after 5 minutes")
        except json.JSONDecodeError as e:
            raise ToolExecutionError(component=tool_name, message=f"Returned invalid JSON: {str(e)}")
        except Exception as e:
            raise ToolExecutionError(component=tool_name, message=f"Execution failed: {str(e)}")

    def _prepare_tool_input(
        self,
        tool_name: str,
        text: str,
        aggression: str,
        glossary_path: Optional[str]
    ) -> Dict[str, Any]:
        """
        Prepare input dictionary for a tool.

        Args:
            tool_name: Name of the tool
            text: Input text
            aggression: Aggression level
            glossary_path: Path to glossary

        Returns:
            Input dictionary for the tool
        """
        # Base input
        tool_input = {"text": text}

        # Tool-specific parameters
        if tool_name == "term_protector":
            if glossary_path:
                tool_input["glossary_path"] = glossary_path
            tool_input["protection_tier"] = "auto"

        elif tool_name == "paraphraser_processor":
            tool_input["aggression"] = aggression
            tool_input["preserve_structure"] = True

        elif tool_name == "fingerprint_remover":
            tool_input["detection_confidence"] = self.config.get(
                "components", {}
            ).get("fingerprint_remover", {}).get("detection_confidence", 0.75)

        elif tool_name == "burstiness_enhancer":
            tool_input["target_burstiness"] = self.config.get(
                "components", {}
            ).get("burstiness_enhancer", {}).get("target_burstiness", 0.7)

        elif tool_name == "validator":
            tool_input["original_text"] = self.state_manager.current_state.original_text
            tool_input["bertscore_model"] = self.config.get(
                "components", {}
            ).get("validator", {}).get("bertscore_model", "roberta-large")

        return tool_input

    def _extract_text_from_output(self, tool_name: str, tool_output: Dict[str, Any]) -> str:
        """
        Extract processed text from tool output.

        Args:
            tool_name: Name of the tool
            tool_output: Tool output dictionary

        Returns:
            Processed text
        """
        # Most tools return "text" or "processed_text"
        if "processed_text" in tool_output:
            return tool_output["processed_text"]
        elif "text" in tool_output:
            return tool_output["text"]
        elif "result" in tool_output and isinstance(tool_output["result"], str):
            return tool_output["result"]
        else:
            # No text modification, return unchanged
            return self.state_manager.current_state.current_text

    def _extract_scores(
        self,
        tool_name: str,
        tool_output: Dict[str, Any],
        scores: Dict[str, float]
    ) -> None:
        """
        Extract scores from tool output and update scores dictionary.

        Args:
            tool_name: Name of the tool
            tool_output: Tool output dictionary
            scores: Scores dictionary to update
        """
        if tool_name == "detector_processor":
            if "detection_score" in tool_output:
                scores["detection_score"] = tool_output["detection_score"]
            if "originality_score" in tool_output:
                scores["originality_score"] = tool_output["originality_score"]
            if "gptzero_score" in tool_output:
                scores["gptzero_score"] = tool_output["gptzero_score"]

        elif tool_name == "perplexity_calculator":
            if "perplexity" in tool_output:
                scores["perplexity"] = tool_output["perplexity"]

        elif tool_name == "validator":
            if "semantic_similarity" in tool_output:
                scores["semantic_similarity"] = tool_output["semantic_similarity"]
            if "bleu_score" in tool_output:
                scores["bleu_score"] = tool_output["bleu_score"]

    def evaluate_quality_gates(self, results: Dict[str, Any]) -> bool:
        """
        Evaluate if quality gates are met.

        Args:
            results: Iteration results containing detection_score

        Returns:
            True if quality gates passed, False otherwise
        """
        detection_score = results.get("detection_score", 100)
        target_threshold = self.detection_threshold * 100  # Convert to percentage

        passed = detection_score <= target_threshold

        logger.info(
            f"Quality gate evaluation: {'PASSED' if passed else 'FAILED'}",
            context={
                "detection_score": detection_score,
                "target_threshold": target_threshold
            }
        )

        return passed

    def adjust_aggression(self, current_score: float, target_score: float) -> str:
        """
        Adjust aggression level based on current vs target score.

        Args:
            current_score: Current detection score (0-100)
            target_score: Target detection score (0-100)

        Returns:
            Adjusted aggression level name
        """
        score_gap = current_score - target_score

        # Get current aggression from last iteration
        if self.state_manager.current_state and self.state_manager.current_state.iterations:
            last_aggression_name = self.state_manager.current_state.iterations[-1].aggression_level
            current_level = self.AGGRESSION_MAP.get(last_aggression_name, 2)
        else:
            current_level = 2  # Start at moderate

        # Adjust based on score gap
        if score_gap > 50:
            # Far from target, increase aggression significantly
            new_level = min(5, current_level + 2)
        elif score_gap > 30:
            # Moderately far, increase aggression
            new_level = min(5, current_level + 1)
        elif score_gap > 10:
            # Close to target, maintain or slight increase
            new_level = min(5, current_level + 1) if current_level < 3 else current_level
        elif score_gap > 0:
            # Very close, maintain current level
            new_level = current_level
        else:
            # Below target (shouldn't happen often), decrease slightly
            new_level = max(1, current_level - 1)

        new_aggression = self.REVERSE_AGGRESSION_MAP[new_level]

        logger.info(
            f"Aggression adjusted: {last_aggression_name if self.state_manager.current_state.iterations else 'none'} → {new_aggression}",
            context={
                "current_score": current_score,
                "target_score": target_score,
                "score_gap": score_gap
            }
        )

        return new_aggression

    def _should_terminate_early(self, state: WorkflowState) -> bool:
        """
        Check if early termination criteria are met.

        Args:
            state: Current workflow state

        Returns:
            True if should terminate early, False otherwise
        """
        if len(state.iterations) < 2:
            return False

        # Get last two iterations
        prev_score = state.iterations[-2].detection_score
        current_score = state.iterations[-1].detection_score

        # Calculate improvement
        improvement = prev_score - current_score
        improvement_percentage = improvement / prev_score if prev_score > 0 else 0

        should_terminate = improvement_percentage < self.early_termination_improvement

        if should_terminate:
            logger.info(
                "Early termination criteria met",
                context={
                    "prev_score": prev_score,
                    "current_score": current_score,
                    "improvement": improvement,
                    "improvement_percentage": improvement_percentage,
                    "threshold": self.early_termination_improvement
                }
            )

        return should_terminate

    def create_checkpoint(self, state: Dict[str, Any]) -> str:
        """
        Create a checkpoint of current state.

        Args:
            state: State dictionary to checkpoint

        Returns:
            Checkpoint ID
        """
        # State manager handles checkpointing automatically
        self.state_manager.save_checkpoint()
        return self.state_manager.current_state.workflow_id

    def restore_checkpoint(self, checkpoint_id: str) -> Dict[str, Any]:
        """
        Restore from a checkpoint.

        Args:
            checkpoint_id: Checkpoint identifier

        Returns:
            Restored state dictionary
        """
        state = self.state_manager.load_workflow(checkpoint_id)
        if state is None:
            raise ProcessingError(f"Checkpoint not found: {checkpoint_id}")

        return self._format_results(state)

    def _format_results(self, state: WorkflowState) -> Dict[str, Any]:
        """
        Format workflow state as results dictionary.

        Args:
            state: Workflow state

        Returns:
            Results dictionary
        """
        return {
            "status": state.status,
            "workflow_id": state.workflow_id,
            "final_text": state.current_text,
            "original_text": state.original_text,
            "iterations": state.current_iteration,
            "max_iterations": state.max_iterations,
            "final_scores": state.final_scores or {},
            "history": [
                {
                    "iteration": iter_state.iteration,
                    "detection_score": iter_state.detection_score,
                    "originality_score": iter_state.originality_score,
                    "aggression_level": iter_state.aggression_level,
                    "components_executed": iter_state.components_executed,
                    "timestamp": iter_state.timestamp,
                    "status": iter_state.status
                }
                for iter_state in state.iterations
            ],
            "started_at": state.started_at,
            "completed_at": state.completed_at
        }


def main():
    """
    Main entry point for standalone testing.
    """
    # Load config
    config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"

    import yaml
    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Create orchestrator
    orchestrator = Orchestrator(config)

    # Example text
    sample_text = """
    Machine learning has revolutionized many fields of study. This paper presents
    a novel approach to deep learning optimization.
    """

    # Run pipeline
    results = orchestrator.run_pipeline(
        input_text=sample_text,
        options={"initial_aggression": "moderate"}
    )

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
