"""
Orchestrator Package - Core Workflow Coordination
=================================================

This package contains the core orchestration logic for the AI Humanizer system.

Components:
- orchestrator.py: Main orchestration engine for tool pipeline execution
- Coordinates: Tool pipeline, iterations, quality gates, adaptive aggression
- Integrates with: StateManager, ErrorHandler, CLIInterface
"""

from .orchestrator import Orchestrator

__all__ = ['Orchestrator']
