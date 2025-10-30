"""
AI Humanizer System - Configuration Loader
==========================================

Loads and validates configuration from config/config.yaml and environment variables.
Implements the configuration strategy documented in docs/coding-standards.md.

Configuration Sources (priority order):
1. Environment variables (highest priority)
2. config.yaml file
3. Default values (fallback)

Environment Variables:
- ORIGINALITY_API_KEY: API key for Originality.ai (optional)
- ENVIRONMENT: development, staging, or production
- CUDA_VISIBLE_DEVICES: GPU device ID (if multiple GPUs)
- LOG_LEVEL: DEBUG, INFO, WARNING, ERROR, CRITICAL

Usage Example:
    from src.utils.config_loader import load_config

    config = load_config()

    # Access configuration
    max_iterations = config["humanizer"]["max_iterations"]  # 7
    gentle_level = config["aggression_levels"]["gentle"]  # 1
    glossary_path = config["paths"]["glossary"]  # "data/glossary.json"

Configuration Structure (see config/config.yaml for full details):
    humanizer:
        max_iterations: 7
        detection_threshold: 0.15
        early_termination_improvement: 0.02

    aggression_levels:
        gentle: 1
        moderate: 2
        aggressive: 3
        intensive: 4
        nuclear: 5

    translation_chain:
        enabled: true
        trigger_threshold: 0.05
        languages: ["de", "ja"]

    paths:
        glossary: "data/glossary.json"
        patterns: "data/patterns.json"
        checkpoint_dir: ".humanizer/checkpoints"
        log_dir: ".humanizer/logs"
        output_dir: ".humanizer/output"

Author: BMAD Development Team
Date: 2025-10-30
Version: 1.0
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from .exceptions import ConfigError
from .logger import get_logger

logger = get_logger(__name__)

# Default configuration file path
DEFAULT_CONFIG_PATH = Path("config/config.yaml")

# Default configuration values (fallback if config.yaml missing)
DEFAULT_CONFIG = {
    "humanizer": {
        "max_iterations": 7,
        "detection_threshold": 0.15,
        "early_termination_improvement": 0.02,
        "checkpoint_enabled": True,
        "checkpoint_interval": 1  # Save after each iteration
    },
    "aggression_levels": {
        "gentle": 1,
        "moderate": 2,
        "aggressive": 3,
        "intensive": 4,
        "nuclear": 5
    },
    "translation_chain": {
        "enabled": True,
        "trigger_threshold": 0.05,
        "languages": ["de", "ja"],
        "max_attempts": 2
    },
    "validation": {
        "bertscore_threshold": 0.92,
        "bertscore_model": "roberta-large",
        "term_preservation_threshold": 0.95,
        "bleu_weight": 0.3
    },
    "performance": {
        "timeout_seconds": 300,  # 5 minutes per tool
        "max_memory_gb": 8,
        "enable_gpu": True,
        "batch_size": 32
    },
    "paths": {
        "glossary": "data/glossary.json",
        "patterns": "data/patterns.json",
        "checkpoint_dir": ".humanizer/checkpoints",
        "log_dir": ".humanizer/logs",
        "output_dir": ".humanizer/output",
        "reference_texts_dir": "data/reference_texts"
    },
    "logging": {
        "level": "INFO",
        "console": True,
        "file": True,
        "max_log_size_mb": 10,
        "backup_count": 5
    }
}


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load configuration from YAML file and environment variables.

    Priority order:
    1. Environment variables (override all)
    2. YAML file values
    3. Default values (fallback)

    Args:
        config_path: Path to config.yaml (uses default if None)

    Returns:
        Configuration dictionary with all settings

    Raises:
        ConfigError: If config file is malformed or missing required fields

    Example:
        config = load_config()
        max_iters = config["humanizer"]["max_iterations"]
    """
    config_file = config_path or DEFAULT_CONFIG_PATH

    # Start with default configuration
    config = DEFAULT_CONFIG.copy()

    # Load from YAML file if exists
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                yaml_config = yaml.safe_load(f)

            if yaml_config:
                # Deep merge YAML config into defaults
                config = _deep_merge(config, yaml_config)

            logger.info(f"Configuration loaded from {config_file}")

        except yaml.YAMLError as e:
            raise ConfigError(
                message=f"Invalid YAML syntax in {config_file}",
                component="config_loader",
                details={"file": str(config_file)},
                original_error=e
            )
        except Exception as e:
            raise ConfigError(
                message=f"Failed to load configuration from {config_file}",
                component="config_loader",
                details={"file": str(config_file)},
                original_error=e
            )
    else:
        logger.warning(
            f"Configuration file not found: {config_file}. Using defaults.",
            data={"config_path": str(config_file)}
        )

    # Override with environment variables
    config = _apply_env_overrides(config)

    # Validate configuration
    _validate_config(config)

    # Create necessary directories
    _create_directories(config)

    logger.debug("Configuration loaded successfully", data={"config": config})

    return config


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries (override takes precedence).

    Args:
        base: Base dictionary (defaults)
        override: Override dictionary (YAML config)

    Returns:
        Merged dictionary
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dictionaries
            result[key] = _deep_merge(result[key], value)
        else:
            # Override value
            result[key] = value

    return result


def _apply_env_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
    """Apply environment variable overrides to configuration.

    Supported environment variables:
    - ORIGINALITY_API_KEY: API key for Originality.ai
    - ENVIRONMENT: development, staging, production
    - CUDA_VISIBLE_DEVICES: GPU device ID
    - LOG_LEVEL: DEBUG, INFO, WARNING, ERROR, CRITICAL
    - MAX_ITERATIONS: Override humanizer.max_iterations
    - DETECTION_THRESHOLD: Override humanizer.detection_threshold

    Args:
        config: Base configuration dictionary

    Returns:
        Configuration with environment overrides applied
    """
    # API keys
    if "ORIGINALITY_API_KEY" in os.environ:
        config["api_keys"] = config.get("api_keys", {})
        config["api_keys"]["originality"] = os.environ["ORIGINALITY_API_KEY"]
        logger.debug("ORIGINALITY_API_KEY loaded from environment")

    # Environment name
    if "ENVIRONMENT" in os.environ:
        config["environment"] = os.environ["ENVIRONMENT"]
        logger.info(f"Environment: {config['environment']}")

    # CUDA device
    if "CUDA_VISIBLE_DEVICES" in os.environ:
        config["performance"]["cuda_device"] = os.environ["CUDA_VISIBLE_DEVICES"]
        logger.debug(f"CUDA device: {config['performance']['cuda_device']}")

    # Log level
    if "LOG_LEVEL" in os.environ:
        config["logging"]["level"] = os.environ["LOG_LEVEL"].upper()
        logger.debug(f"Log level: {config['logging']['level']}")

    # Humanizer parameters
    if "MAX_ITERATIONS" in os.environ:
        try:
            config["humanizer"]["max_iterations"] = int(os.environ["MAX_ITERATIONS"])
        except ValueError:
            logger.warning("Invalid MAX_ITERATIONS environment variable (not an integer)")

    if "DETECTION_THRESHOLD" in os.environ:
        try:
            config["humanizer"]["detection_threshold"] = float(os.environ["DETECTION_THRESHOLD"])
        except ValueError:
            logger.warning("Invalid DETECTION_THRESHOLD environment variable (not a float)")

    return config


def _validate_config(config: Dict[str, Any]) -> None:
    """Validate configuration has required fields and valid values.

    Args:
        config: Configuration dictionary to validate

    Raises:
        ConfigError: If configuration is invalid
    """
    # Required top-level sections
    required_sections = ["humanizer", "aggression_levels", "paths", "logging"]
    for section in required_sections:
        if section not in config:
            raise ConfigError(
                message=f"Missing required configuration section: {section}",
                component="config_loader",
                details={"missing_section": section}
            )

    # Validate humanizer section
    if "max_iterations" not in config["humanizer"]:
        raise ConfigError(
            message="Missing humanizer.max_iterations in configuration",
            component="config_loader"
        )

    max_iters = config["humanizer"]["max_iterations"]
    if not isinstance(max_iters, int) or max_iters < 1 or max_iters > 20:
        raise ConfigError(
            message=f"humanizer.max_iterations must be integer between 1 and 20, got {max_iters}",
            component="config_loader",
            details={"value": max_iters}
        )

    # Validate aggression levels
    required_levels = ["gentle", "moderate", "aggressive", "intensive", "nuclear"]
    for level in required_levels:
        if level not in config["aggression_levels"]:
            raise ConfigError(
                message=f"Missing aggression level: {level}",
                component="config_loader",
                details={"missing_level": level}
            )

        value = config["aggression_levels"][level]
        if not isinstance(value, int) or value < 1 or value > 5:
            raise ConfigError(
                message=f"Aggression level {level} must be integer 1-5, got {value}",
                component="config_loader",
                details={"level": level, "value": value}
            )

    # Validate paths section
    required_paths = ["glossary", "checkpoint_dir", "log_dir", "output_dir"]
    for path_key in required_paths:
        if path_key not in config["paths"]:
            raise ConfigError(
                message=f"Missing path configuration: paths.{path_key}",
                component="config_loader",
                details={"missing_path": path_key}
            )

    logger.debug("Configuration validation passed")


def _create_directories(config: Dict[str, Any]) -> None:
    """Create necessary directories from configuration.

    Creates:
    - checkpoint_dir
    - log_dir
    - output_dir
    - reference_texts_dir (if specified)

    Args:
        config: Configuration dictionary with paths section
    """
    paths_to_create = [
        config["paths"]["checkpoint_dir"],
        config["paths"]["log_dir"],
        config["paths"]["output_dir"]
    ]

    if "reference_texts_dir" in config["paths"]:
        paths_to_create.append(config["paths"]["reference_texts_dir"])

    for path_str in paths_to_create:
        path = Path(path_str)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created directory: {path}")


def get_config_value(config: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """Get configuration value using dot-notation key path.

    Args:
        config: Configuration dictionary
        key_path: Dot-notation path (e.g., "humanizer.max_iterations")
        default: Default value if key not found

    Returns:
        Configuration value or default

    Example:
        max_iters = get_config_value(config, "humanizer.max_iterations", 7)
    """
    keys = key_path.split(".")
    value = config

    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default

    return value
