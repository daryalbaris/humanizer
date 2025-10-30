#!/usr/bin/env python3
"""
AI Humanizer System - Sandbox Verification Script
==================================================

This script verifies that the Claude Code sandbox environment is properly
configured for the AI Humanizer System. It checks:

1. Python version compatibility
2. Required package availability
3. spaCy model installation
4. JSON stdin/stdout communication
5. File system access (read/write)
6. GPU/CUDA availability (optional)
7. System resources (memory, CPU)

Usage:
    python scripts/verify_sandbox.py [--json] [--verbose]

Arguments:
    --json      Output results in JSON format for programmatic consumption
    --verbose   Display detailed diagnostic information

Exit Codes:
    0: All checks passed
    1: One or more critical checks failed
    2: Warnings present but no failures

Author: BMAD Development Team
Date: 2025-10-30
Version: 1.0
"""

import sys
import json
import argparse
import platform
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Any
import importlib.util

# Set UTF-8 encoding for stdout on Windows
if sys.platform == "win32":
    import io
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


# ANSI color codes for terminal output
class Colors:
    """ANSI color codes for pretty terminal output."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


# Unicode symbols (with ASCII fallback)
class Symbols:
    """Unicode symbols with ASCII fallback for compatibility."""
    try:
        CHECK = '✓'
        CROSS = '✗'
        WARNING = '⚠'
    except UnicodeEncodeError:
        CHECK = '[OK]'
        CROSS = '[FAIL]'
        WARNING = '[WARN]'


class SandboxVerifier:
    """Comprehensive Claude Code sandbox environment verification."""

    def __init__(self, verbose: bool = False):
        """Initialize the verifier.

        Args:
            verbose: Enable detailed diagnostic output
        """
        self.verbose = verbose
        self.results = {
            "python_version": {},
            "packages": {},
            "spacy_models": {},
            "filesystem": {},
            "gpu": {},
            "system_resources": {},
            "json_communication": {},
            "overall_status": "unknown"
        }
        self.warnings: List[str] = []
        self.errors: List[str] = []

    def check_python_version(self) -> bool:
        """Verify Python version is 3.9 or higher.

        Returns:
            True if version requirement met, False otherwise
        """
        print(f"\n{Colors.BLUE}{Colors.BOLD}=== Python Version Check ==={Colors.RESET}")

        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"

        self.results["python_version"] = {
            "version": version_str,
            "major": version.major,
            "minor": version.minor,
            "micro": version.micro,
            "required": "3.9+",
            "meets_requirement": version >= (3, 9)
        }

        if version >= (3, 9):
            print(f"{Colors.GREEN}{Symbols.CHECK}{Colors.RESET} Python {version_str} (requirement: 3.9+)")
            return True
        else:
            error_msg = f"Python {version_str} < 3.9 (REQUIREMENT NOT MET)"
            self.errors.append(error_msg)
            print(f"{Colors.RED}{Symbols.CROSS}{Colors.RESET} {error_msg}")
            return False

    def check_required_packages(self) -> bool:
        """Verify all required packages can be imported.

        Returns:
            True if all packages available, False if any missing
        """
        print(f"\n{Colors.BLUE}{Colors.BOLD}=== Required Package Check ==={Colors.RESET}")

        required_packages = {
            "spacy": "3.7.2",
            "transformers": "4.35.0",
            "torch": "2.1.0",
            "bert_score": "0.3.13",
            "nltk": "3.8.1",
            "yaml": "6.0.1",
            "pytest": "7.4.3",
        }

        all_available = True

        for package_name, expected_version in required_packages.items():
            # Handle special cases for package names
            import_name = package_name
            if package_name == "yaml":
                import_name = "yaml"
                module_attr = "safe_load"  # PyYAML
            elif package_name == "bert_score":
                import_name = "bert_score"
                module_attr = "score"

            try:
                # Try to import the package
                module = __import__(import_name)

                # Get version if available
                version = "unknown"
                if hasattr(module, "__version__"):
                    version = module.__version__
                elif hasattr(module, "VERSION"):
                    version = module.VERSION

                self.results["packages"][package_name] = {
                    "installed": True,
                    "version": version,
                    "expected_version": expected_version,
                    "version_match": version.startswith(expected_version.split('.')[0])
                }

                # Color code based on version match
                if version.startswith(expected_version.split('.')[0]):
                    print(f"{Colors.GREEN}{Symbols.CHECK}{Colors.RESET} {package_name:20s} {version:15s} "
                          f"(expected: {expected_version})")
                else:
                    warning_msg = f"{package_name} version {version} != {expected_version}"
                    self.warnings.append(warning_msg)
                    print(f"{Colors.YELLOW}{Symbols.WARNING}{Colors.RESET} {package_name:20s} {version:15s} "
                          f"(expected: {expected_version})")

            except ImportError as e:
                error_msg = f"Package '{package_name}' not found: {str(e)}"
                self.errors.append(error_msg)
                self.results["packages"][package_name] = {
                    "installed": False,
                    "version": None,
                    "expected_version": expected_version,
                    "error": str(e)
                }
                print(f"{Colors.RED}{Symbols.CROSS}{Colors.RESET} {package_name:20s} NOT FOUND")
                all_available = False

        return all_available

    def check_spacy_models(self) -> bool:
        """Verify spaCy models are installed and loadable.

        Returns:
            True if required models available, False otherwise
        """
        print(f"\n{Colors.BLUE}{Colors.BOLD}=== spaCy Model Check ==={Colors.RESET}")

        try:
            import spacy
        except ImportError:
            error_msg = "spaCy not installed, cannot check models"
            self.errors.append(error_msg)
            self.results["spacy_models"]["available"] = False
            print(f"{Colors.RED}{Symbols.CROSS}{Colors.RESET} {error_msg}")
            return False

        # Production model (large)
        prod_model = "en_core_web_trf"
        # CI model (small)
        ci_model = "en_core_web_sm"

        models_ok = True

        for model_name in [prod_model, ci_model]:
            try:
                nlp = spacy.load(model_name)
                model_info = {
                    "installed": True,
                    "name": model_name,
                    "version": nlp.meta.get("version", "unknown"),
                    "lang": nlp.meta.get("lang", "unknown"),
                    "pipeline": list(nlp.pipe_names)
                }
                self.results["spacy_models"][model_name] = model_info

                print(f"{Colors.GREEN}{Symbols.CHECK}{Colors.RESET} {model_name:25s} v{model_info['version']} "
                      f"(pipeline: {', '.join(nlp.pipe_names[:3])}...)")

            except OSError:
                warning_msg = f"spaCy model '{model_name}' not installed"
                if model_name == prod_model:
                    # Production model is critical
                    self.errors.append(warning_msg)
                    models_ok = False
                    print(f"{Colors.RED}{Symbols.CROSS}{Colors.RESET} {model_name:25s} NOT FOUND (CRITICAL)")
                else:
                    # CI model is optional
                    self.warnings.append(warning_msg)
                    print(f"{Colors.YELLOW}{Symbols.WARNING}{Colors.RESET} {model_name:25s} NOT FOUND (optional)")

                self.results["spacy_models"][model_name] = {
                    "installed": False,
                    "name": model_name
                }

        return models_ok

    def check_filesystem_access(self) -> bool:
        """Verify file system read/write capabilities.

        Returns:
            True if filesystem accessible, False otherwise
        """
        print(f"\n{Colors.BLUE}{Colors.BOLD}=== File System Access Check ==={Colors.RESET}")

        test_dir = Path(".humanizer/test_sandbox")
        test_file = test_dir / "test_write.txt"
        test_content = "Claude Code Sandbox Test"

        try:
            # Create directory
            test_dir.mkdir(parents=True, exist_ok=True)
            print(f"{Colors.GREEN}{Symbols.CHECK}{Colors.RESET} Directory creation: {test_dir}")

            # Write file
            test_file.write_text(test_content)
            print(f"{Colors.GREEN}{Symbols.CHECK}{Colors.RESET} File write: {test_file}")

            # Read file
            read_content = test_file.read_text()
            if read_content == test_content:
                print(f"{Colors.GREEN}{Symbols.CHECK}{Colors.RESET} File read: content matches")
            else:
                raise ValueError("Read content doesn't match written content")

            # Delete file
            test_file.unlink()
            print(f"{Colors.GREEN}{Symbols.CHECK}{Colors.RESET} File deletion: successful")

            # Delete directory
            test_dir.rmdir()
            print(f"{Colors.GREEN}{Symbols.CHECK}{Colors.RESET} Directory deletion: successful")

            self.results["filesystem"] = {
                "accessible": True,
                "read": True,
                "write": True,
                "delete": True
            }
            return True

        except Exception as e:
            error_msg = f"Filesystem access failed: {str(e)}"
            self.errors.append(error_msg)
            self.results["filesystem"] = {
                "accessible": False,
                "error": str(e)
            }
            print(f"{Colors.RED}{Symbols.CROSS}{Colors.RESET} {error_msg}")
            return False

    def check_gpu_availability(self) -> bool:
        """Check GPU/CUDA availability (optional).

        Returns:
            True if GPU available, False otherwise (not a failure)
        """
        print(f"\n{Colors.BLUE}{Colors.BOLD}=== GPU/CUDA Check (Optional) ==={Colors.RESET}")

        try:
            import torch

            cuda_available = torch.cuda.is_available()

            if cuda_available:
                device_count = torch.cuda.device_count()
                device_name = torch.cuda.get_device_name(0) if device_count > 0 else "unknown"

                self.results["gpu"] = {
                    "available": True,
                    "cuda_available": True,
                    "device_count": device_count,
                    "device_name": device_name,
                    "cuda_version": torch.version.cuda
                }

                print(f"{Colors.GREEN}{Symbols.CHECK}{Colors.RESET} CUDA available: {device_count} device(s)")
                print(f"  Device 0: {device_name}")
                print(f"  CUDA version: {torch.version.cuda}")
                return True
            else:
                self.results["gpu"] = {
                    "available": False,
                    "cuda_available": False,
                    "message": "Running on CPU (slower but functional)"
                }
                print(f"{Colors.YELLOW}{Symbols.WARNING}{Colors.RESET} CUDA not available (will use CPU)")
                return False

        except ImportError:
            self.results["gpu"] = {
                "available": False,
                "error": "PyTorch not installed"
            }
            print(f"{Colors.YELLOW}{Symbols.WARNING}{Colors.RESET} PyTorch not available, cannot check GPU")
            return False

    def check_json_communication(self) -> bool:
        """Test JSON stdin/stdout communication capability.

        Returns:
            True if JSON communication works, False otherwise
        """
        print(f"\n{Colors.BLUE}{Colors.BOLD}=== JSON Communication Check ==={Colors.RESET}")

        test_data = {
            "text": "This is a test sentence for AI humanization.",
            "options": {
                "protect_numbers": True,
                "aggression_level": 2
            }
        }

        try:
            # Test JSON serialization
            json_str = json.dumps(test_data, indent=2)
            print(f"{Colors.GREEN}{Symbols.CHECK}{Colors.RESET} JSON serialization successful")

            # Test JSON deserialization
            parsed_data = json.loads(json_str)
            if parsed_data == test_data:
                print(f"{Colors.GREEN}{Symbols.CHECK}{Colors.RESET} JSON deserialization successful")
            else:
                raise ValueError("Parsed data doesn't match original")

            # Test stdin simulation
            import io
            test_stdin = io.StringIO(json_str)
            parsed_from_stdin = json.load(test_stdin)
            if parsed_from_stdin == test_data:
                print(f"{Colors.GREEN}{Symbols.CHECK}{Colors.RESET} stdin JSON parsing successful")

            # Test stdout simulation
            test_stdout = io.StringIO()
            json.dump(test_data, test_stdout)
            if test_stdout.getvalue():
                print(f"{Colors.GREEN}{Symbols.CHECK}{Colors.RESET} stdout JSON writing successful")

            self.results["json_communication"] = {
                "working": True,
                "serialization": True,
                "deserialization": True,
                "stdin_parsing": True,
                "stdout_writing": True
            }
            return True

        except Exception as e:
            error_msg = f"JSON communication failed: {str(e)}"
            self.errors.append(error_msg)
            self.results["json_communication"] = {
                "working": False,
                "error": str(e)
            }
            print(f"{Colors.RED}{Symbols.CROSS}{Colors.RESET} {error_msg}")
            return False

    def check_system_resources(self) -> bool:
        """Check system resources (memory, CPU).

        Returns:
            True if resources adequate, False otherwise
        """
        print(f"\n{Colors.BLUE}{Colors.BOLD}=== System Resources Check ==={Colors.RESET}")

        try:
            import psutil

            # Memory check
            memory = psutil.virtual_memory()
            memory_gb = memory.total / (1024 ** 3)
            memory_available_gb = memory.available / (1024 ** 3)

            # CPU check
            cpu_count = psutil.cpu_count(logical=False)
            cpu_count_logical = psutil.cpu_count(logical=True)

            self.results["system_resources"] = {
                "memory_total_gb": round(memory_gb, 2),
                "memory_available_gb": round(memory_available_gb, 2),
                "memory_percent_used": memory.percent,
                "cpu_count_physical": cpu_count,
                "cpu_count_logical": cpu_count_logical,
                "platform": platform.system(),
                "platform_release": platform.release()
            }

            # Memory recommendation: 8GB minimum, 16GB recommended
            if memory_gb >= 16:
                print(f"{Colors.GREEN}{Symbols.CHECK}{Colors.RESET} Memory: {memory_gb:.1f} GB total "
                      f"({memory_available_gb:.1f} GB available) - Excellent")
            elif memory_gb >= 8:
                print(f"{Colors.YELLOW}{Symbols.WARNING}{Colors.RESET} Memory: {memory_gb:.1f} GB total "
                      f"({memory_available_gb:.1f} GB available) - Adequate")
                self.warnings.append(f"Memory {memory_gb:.1f} GB < 16 GB recommended")
            else:
                error_msg = f"Memory {memory_gb:.1f} GB < 8 GB minimum"
                self.errors.append(error_msg)
                print(f"{Colors.RED}{Symbols.CROSS}{Colors.RESET} Memory: {memory_gb:.1f} GB total - Insufficient")
                return False

            # CPU recommendation: 4+ cores
            if cpu_count >= 4:
                print(f"{Colors.GREEN}{Symbols.CHECK}{Colors.RESET} CPU: {cpu_count} physical cores "
                      f"({cpu_count_logical} logical)")
            else:
                warning_msg = f"CPU {cpu_count} cores < 4 recommended"
                self.warnings.append(warning_msg)
                print(f"{Colors.YELLOW}{Symbols.WARNING}{Colors.RESET} CPU: {cpu_count} physical cores - Limited")

            print(f"{Colors.GREEN}{Symbols.CHECK}{Colors.RESET} Platform: {platform.system()} {platform.release()}")

            return True

        except ImportError:
            # psutil not available, skip resource check
            self.results["system_resources"] = {
                "available": False,
                "message": "psutil not installed, skipping resource check"
            }
            print(f"{Colors.YELLOW}{Symbols.WARNING}{Colors.RESET} psutil not available, cannot check system resources")
            return True  # Not a critical failure

    def generate_report(self, json_output: bool = False) -> str:
        """Generate final verification report.

        Args:
            json_output: Output in JSON format instead of text

        Returns:
            Formatted report string
        """
        if json_output:
            self.results["overall_status"] = self._get_overall_status()
            self.results["warnings"] = self.warnings
            self.results["errors"] = self.errors
            return json.dumps(self.results, indent=2)

        # Text report
        print(f"\n{Colors.BLUE}{Colors.BOLD}{'=' * 60}{Colors.RESET}")
        print(f"{Colors.BLUE}{Colors.BOLD}     VERIFICATION SUMMARY{Colors.RESET}")
        print(f"{Colors.BLUE}{Colors.BOLD}{'=' * 60}{Colors.RESET}")

        status = self._get_overall_status()

        if status == "PASS":
            print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL CHECKS PASSED{Colors.RESET}")
            print(f"{Colors.GREEN}The Claude Code sandbox is properly configured for the AI Humanizer System.{Colors.RESET}")
        elif status == "PASS_WITH_WARNINGS":
            print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ PASSED WITH WARNINGS{Colors.RESET}")
            print(f"{Colors.YELLOW}The system will function but some features may be degraded.{Colors.RESET}")
            print(f"\n{Colors.YELLOW}Warnings:{Colors.RESET}")
            for warning in self.warnings:
                print(f"  • {warning}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}✗ VERIFICATION FAILED{Colors.RESET}")
            print(f"{Colors.RED}Critical issues must be resolved before using the system.{Colors.RESET}")
            print(f"\n{Colors.RED}Errors:{Colors.RESET}")
            for error in self.errors:
                print(f"  • {error}")

        if self.warnings:
            print(f"\n{Colors.YELLOW}Total warnings: {len(self.warnings)}{Colors.RESET}")
        if self.errors:
            print(f"{Colors.RED}Total errors: {len(self.errors)}{Colors.RESET}")

        print(f"\n{Colors.BLUE}{'=' * 60}{Colors.RESET}\n")

        return status

    def _get_overall_status(self) -> str:
        """Determine overall verification status.

        Returns:
            Status string: "PASS", "PASS_WITH_WARNINGS", or "FAIL"
        """
        if self.errors:
            return "FAIL"
        elif self.warnings:
            return "PASS_WITH_WARNINGS"
        else:
            return "PASS"

    def run_all_checks(self) -> bool:
        """Run all verification checks.

        Returns:
            True if all critical checks passed, False otherwise
        """
        print(f"\n{Colors.BLUE}{Colors.BOLD}{'=' * 60}{Colors.RESET}")
        print(f"{Colors.BLUE}{Colors.BOLD}  AI HUMANIZER SYSTEM - SANDBOX VERIFICATION{Colors.RESET}")
        print(f"{Colors.BLUE}{Colors.BOLD}{'=' * 60}{Colors.RESET}")

        checks = [
            self.check_python_version,
            self.check_required_packages,
            self.check_spacy_models,
            self.check_filesystem_access,
            self.check_json_communication,
            self.check_system_resources,
            self.check_gpu_availability,  # Optional, won't fail overall
        ]

        for check in checks:
            check()

        return len(self.errors) == 0


def main():
    """Main entry point for sandbox verification."""
    parser = argparse.ArgumentParser(
        description="Verify Claude Code sandbox environment for AI Humanizer System"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Display detailed diagnostic information"
    )

    args = parser.parse_args()

    verifier = SandboxVerifier(verbose=args.verbose)
    all_passed = verifier.run_all_checks()
    report = verifier.generate_report(json_output=args.json)

    if args.json:
        print(report)

    # Exit code based on results
    if all_passed and not verifier.warnings:
        sys.exit(0)  # Perfect
    elif all_passed and verifier.warnings:
        sys.exit(2)  # Warnings but functional
    else:
        sys.exit(1)  # Critical errors


if __name__ == "__main__":
    main()
