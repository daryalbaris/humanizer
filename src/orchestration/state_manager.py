"""
State Management for BMAD Orchestrator

Handles checkpoint/resume functionality, processing logs, and atomic writes
for the BMAD humanization workflow orchestrator.
"""

import json
import os
import shutil
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import tempfile

# Cross-platform file locking
try:
    import fcntl
    HAS_FCNTL = True
except ImportError:
    # fcntl not available on Windows - use no-op fallback
    HAS_FCNTL = False

    class fcntl:
        """No-op fallback for Windows (fcntl not available)"""
        LOCK_SH = 1  # Shared lock
        LOCK_EX = 2  # Exclusive lock
        LOCK_UN = 8  # Unlock

        @staticmethod
        def flock(fd, operation):
            """No-op file lock for Windows - single process development OK"""
            pass


@dataclass
class IterationState:
    """State for a single iteration of the humanization workflow."""
    iteration: int
    timestamp: str
    detection_score: float
    originality_score: float
    gptzero_score: float
    aggression_level: str
    components_executed: List[str] = field(default_factory=list)
    component_outputs: Dict[str, Any] = field(default_factory=dict)
    token_usage: Dict[str, int] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    completed: bool = False
    status: str = "in_progress"  # in_progress, completed, failed

    @property
    def aggressiveness(self) -> str:
        """Backward compatibility alias for aggression_level."""
        return self.aggression_level


@dataclass
class WorkflowState:
    """Complete state of the humanization workflow."""
    workflow_id: str
    original_text: str
    current_text: str
    target_originality_threshold: float
    max_iterations: int
    current_iteration: int
    iterations: List[IterationState] = field(default_factory=list)
    injection_points: List[Dict[str, Any]] = field(default_factory=list)
    human_inputs: Dict[int, str] = field(default_factory=dict)  # iteration -> input
    total_token_usage: Dict[str, int] = field(default_factory=dict)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    status: str = "in_progress"  # in_progress, completed, failed, paused
    final_scores: Optional[Dict[str, float]] = None


class StateManager:
    """
    Manages workflow state with checkpoint/resume capability.

    Features:
    - Atomic writes prevent corruption
    - Backup checkpoints in separate directory
    - Processing log with timestamps and scores
    - Resume capability from any checkpoint
    """

    def __init__(self, checkpoint_dir: str = "checkpoints", backup_dir: str = "checkpoints/backups"):
        """
        Initialize state manager.

        Args:
            checkpoint_dir: Directory for active checkpoints
            backup_dir: Directory for backup checkpoints
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.backup_dir = Path(backup_dir)

        # Create directories
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        self.current_state: Optional[WorkflowState] = None
        self.checkpoint_path: Optional[Path] = None

    def create_workflow(
        self,
        workflow_id: str,
        original_text: str,
        target_originality_threshold: float = 20.0,
        max_iterations: int = 7
    ) -> WorkflowState:
        """
        Create new workflow state.

        Args:
            workflow_id: Unique workflow identifier
            original_text: Original academic text
            target_originality_threshold: Target Originality.ai score
            max_iterations: Maximum refinement iterations

        Returns:
            New workflow state
        """
        state = WorkflowState(
            workflow_id=workflow_id,
            original_text=original_text,
            current_text=original_text,
            target_originality_threshold=target_originality_threshold,
            max_iterations=max_iterations,
            current_iteration=0,
            started_at=datetime.now().isoformat(),
            total_token_usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        )

        self.current_state = state
        self.checkpoint_path = self.checkpoint_dir / f"{workflow_id}.json"

        # Save initial state
        self.save_checkpoint()

        return state

    def load_workflow(self, workflow_id: str) -> Optional[WorkflowState]:
        """
        Load workflow state from checkpoint.

        Args:
            workflow_id: Workflow identifier

        Returns:
            Workflow state if found, None otherwise
        """
        checkpoint_path = self.checkpoint_dir / f"{workflow_id}.json"

        if not checkpoint_path.exists():
            return None

        try:
            with open(checkpoint_path, 'r', encoding='utf-8') as f:
                # Use file locking to prevent concurrent access
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                data = json.load(f)
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

            # Reconstruct state from JSON
            iterations = [IterationState(**it) for it in data.pop('iterations', [])]
            state = WorkflowState(**data, iterations=iterations)

            self.current_state = state
            self.checkpoint_path = checkpoint_path

            return state

        except Exception as e:
            print(f"Error loading checkpoint: {e}")
            return None

    def save_checkpoint(self, backup: bool = True) -> bool:
        """
        Save current state to checkpoint with atomic write.

        Args:
            backup: Create backup copy

        Returns:
            True if successful
        """
        if not self.current_state or not self.checkpoint_path:
            return False

        try:
            # Convert state to JSON
            state_dict = asdict(self.current_state)
            state_json = json.dumps(state_dict, indent=2, ensure_ascii=False)

            # Atomic write using temporary file + rename
            temp_fd, temp_path = tempfile.mkstemp(
                dir=self.checkpoint_dir,
                suffix='.tmp',
                text=True
            )

            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                # Use file locking during write
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                f.write(state_json)
                f.flush()
                os.fsync(f.fileno())
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

            # Create backup before replacing
            if backup and self.checkpoint_path.exists():
                # Use microseconds to ensure unique filenames even within same second
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                backup_path = self.backup_dir / f"{self.current_state.workflow_id}_{timestamp}.json"
                shutil.copy2(self.checkpoint_path, backup_path)

                # Keep only last 10 backups
                self._cleanup_old_backups(self.current_state.workflow_id, keep=10)

            # Atomic rename
            shutil.move(temp_path, self.checkpoint_path)

            return True

        except Exception as e:
            print(f"Error saving checkpoint: {e}")
            # Clean up temp file if it exists
            if 'temp_path' in locals() and Path(temp_path).exists():
                os.unlink(temp_path)
            return False

    def start_iteration(self, iteration: int, aggression_level: str) -> IterationState:
        """
        Start new iteration and update state.

        Args:
            iteration: Iteration number
            aggression_level: Current aggression level

        Returns:
            New iteration state
        """
        if not self.current_state:
            raise ValueError("No active workflow")

        iteration_state = IterationState(
            iteration=iteration,
            timestamp=datetime.now().isoformat(),
            detection_score=0.0,
            originality_score=0.0,
            gptzero_score=0.0,
            aggression_level=aggression_level
        )

        self.current_state.iterations.append(iteration_state)
        self.current_state.current_iteration = iteration

        return iteration_state

    def update_iteration(
        self,
        component: str,
        output: Any,
        detection_score: Optional[float] = None,
        originality_score: Optional[float] = None,
        gptzero_score: Optional[float] = None,
        token_usage: Optional[Dict[str, int]] = None,
        error: Optional[str] = None
    ):
        """
        Update current iteration with component output.

        Args:
            component: Component name
            output: Component output data
            detection_score: Weighted detection score
            originality_score: Originality.ai score
            gptzero_score: GPTZero score
            token_usage: Token usage for this component
            error: Error message if any
        """
        if not self.current_state or not self.current_state.iterations:
            raise ValueError("No active iteration")

        current_iter = self.current_state.iterations[-1]

        # Update component execution
        current_iter.components_executed.append(component)
        current_iter.component_outputs[component] = output

        # Update scores
        if detection_score is not None:
            current_iter.detection_score = detection_score
        if originality_score is not None:
            current_iter.originality_score = originality_score
        if gptzero_score is not None:
            current_iter.gptzero_score = gptzero_score

        # Update token usage
        if token_usage:
            for key, value in token_usage.items():
                current_iter.token_usage[key] = current_iter.token_usage.get(key, 0) + value
                self.current_state.total_token_usage[key] = self.current_state.total_token_usage.get(key, 0) + value

        # Record error
        if error:
            current_iter.errors.append(f"{component}: {error}")

        # Save checkpoint after each component
        self.save_checkpoint(backup=False)

    def complete_iteration(self, humanized_text: str):
        """
        Mark current iteration as completed.

        Args:
            humanized_text: Final humanized text from this iteration
        """
        if not self.current_state or not self.current_state.iterations:
            raise ValueError("No active iteration")

        current_iter = self.current_state.iterations[-1]
        current_iter.completed = True
        current_iter.status = "completed"

        # Update current text
        self.current_state.current_text = humanized_text

        # Save checkpoint with backup
        self.save_checkpoint(backup=True)

    def add_injection_point(
        self,
        section: str,
        priority: int,
        guidance: str,
        context: str
    ):
        """
        Add human injection point.

        Args:
            section: Section name (Introduction, Results, etc.)
            priority: Priority score 1-5
            guidance: Guidance prompt for human
            context: Surrounding context
        """
        if not self.current_state:
            raise ValueError("No active workflow")

        injection_point = {
            "section": section,
            "priority": priority,
            "guidance": guidance,
            "context": context,
            "timestamp": datetime.now().isoformat()
        }

        self.current_state.injection_points.append(injection_point)
        self.save_checkpoint(backup=False)

    def record_human_input(self, iteration: int, human_input: str):
        """
        Record human input for injection point.

        Args:
            iteration: Iteration number
            human_input: Human-provided input
        """
        if not self.current_state:
            raise ValueError("No active workflow")

        self.current_state.human_inputs[iteration] = human_input
        self.save_checkpoint(backup=False)

    def complete_workflow(
        self,
        final_scores: Dict[str, float],
        status: str = "completed"
    ):
        """
        Mark workflow as completed.

        Args:
            final_scores: Final detection scores
            status: Workflow status (completed/failed)
        """
        if not self.current_state:
            raise ValueError("No active workflow")

        self.current_state.completed_at = datetime.now().isoformat()
        self.current_state.status = status
        self.current_state.final_scores = final_scores

        # Final checkpoint with backup
        self.save_checkpoint(backup=True)

    def get_processing_log(self) -> List[Dict[str, Any]]:
        """
        Get processing log with timestamps and scores.

        Returns:
            List of iteration logs
        """
        if not self.current_state:
            return []

        log = []
        for iteration in self.current_state.iterations:
            log.append({
                "iteration": iteration.iteration,
                "timestamp": iteration.timestamp,
                "aggression_level": iteration.aggression_level,
                "detection_score": iteration.detection_score,
                "originality_score": iteration.originality_score,
                "gptzero_score": iteration.gptzero_score,
                "components": iteration.components_executed,
                "token_usage": iteration.token_usage,
                "errors": iteration.errors,
                "completed": iteration.completed
            })

        return log

    def get_summary(self) -> Dict[str, Any]:
        """
        Get workflow summary.

        Returns:
            Summary dictionary
        """
        if not self.current_state:
            return {}

        return {
            "workflow_id": self.current_state.workflow_id,
            "status": self.current_state.status,
            "iterations_completed": len([i for i in self.current_state.iterations if i.completed]),
            "current_iteration": self.current_state.current_iteration,
            "max_iterations": self.current_state.max_iterations,
            "target_threshold": self.current_state.target_originality_threshold,
            "current_scores": {
                "detection": self.current_state.iterations[-1].detection_score if self.current_state.iterations else 0,
                "originality": self.current_state.iterations[-1].originality_score if self.current_state.iterations else 0,
                "gptzero": self.current_state.iterations[-1].gptzero_score if self.current_state.iterations else 0
            } if self.current_state.iterations else {},
            "final_scores": self.current_state.final_scores,
            "total_token_usage": self.current_state.total_token_usage,
            "injection_points": len(self.current_state.injection_points),
            "human_inputs": len(self.current_state.human_inputs),
            "started_at": self.current_state.started_at,
            "completed_at": self.current_state.completed_at
        }

    def _cleanup_old_backups(self, workflow_id: str, keep: int = 10):
        """
        Keep only the most recent N backups.

        Args:
            workflow_id: Workflow identifier
            keep: Number of backups to keep
        """
        pattern = f"{workflow_id}_*.json"
        backups = sorted(self.backup_dir.glob(pattern), key=lambda p: p.stat().st_mtime)

        # Remove old backups
        for backup in backups[:-keep]:
            backup.unlink()

    def list_workflows(self) -> List[Dict[str, Any]]:
        """
        List all available workflows.

        Returns:
            List of workflow summaries
        """
        workflows = []

        for checkpoint_file in self.checkpoint_dir.glob("*.json"):
            if checkpoint_file.is_file():
                try:
                    with open(checkpoint_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    workflows.append({
                        "workflow_id": data.get("workflow_id"),
                        "status": data.get("status"),
                        "current_iteration": data.get("current_iteration", 0),
                        "started_at": data.get("started_at"),
                        "completed_at": data.get("completed_at")
                    })
                except Exception:
                    continue

        return workflows

    def delete_workflow(self, workflow_id: str) -> bool:
        """
        Delete workflow checkpoint and backups.

        Args:
            workflow_id: Workflow identifier

        Returns:
            True if successful
        """
        try:
            # Delete main checkpoint
            checkpoint_path = self.checkpoint_dir / f"{workflow_id}.json"
            if checkpoint_path.exists():
                checkpoint_path.unlink()

            # Delete backups
            for backup in self.backup_dir.glob(f"{workflow_id}_*.json"):
                backup.unlink()

            return True

        except Exception as e:
            print(f"Error deleting workflow: {e}")
            return False


# Example usage
if __name__ == "__main__":
    # Create state manager
    manager = StateManager()

    # Create new workflow
    state = manager.create_workflow(
        workflow_id="test_workflow_001",
        original_text="This is a sample academic paper text...",
        target_originality_threshold=20.0,
        max_iterations=7
    )

    # Start iteration
    iteration = manager.start_iteration(iteration=1, aggression_level="moderate")

    # Update with component outputs
    manager.update_iteration(
        component="term_protector",
        output={"protected_terms": ["machine learning", "neural network"]},
        token_usage={"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}
    )

    manager.update_iteration(
        component="fingerprint_remover",
        output={"cleaned_text": "Modified text..."},
        detection_score=65.5,
        originality_score=45.2,
        gptzero_score=70.1,
        token_usage={"prompt_tokens": 200, "completion_tokens": 150, "total_tokens": 350}
    )

    # Complete iteration
    manager.complete_iteration(humanized_text="Humanized text after iteration 1...")

    # Get summary
    summary = manager.get_summary()
    print(json.dumps(summary, indent=2))

    # Get processing log
    log = manager.get_processing_log()
    print(json.dumps(log, indent=2))
