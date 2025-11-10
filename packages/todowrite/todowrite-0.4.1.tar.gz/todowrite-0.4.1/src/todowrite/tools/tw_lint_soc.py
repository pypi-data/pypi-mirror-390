#!/usr/bin/env python3
"""
ToDoWrite Separation of Concerns Linter (tw_lint_soc.py)
Ensures layers 1-11 are non-executable and only layer 12 (Command) contains executable content
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any, ClassVar, cast

import yaml

# Type aliases for YAML data structures
YAMLValue = str | int | float | bool | None
YAMLObject = dict[str, Any]
YAMLData = YAMLValue | list[YAMLValue | YAMLObject] | YAMLObject


# pyright: ignore [reportUnknownVariableType, reportUnknownArgumentType, reportUnknownMemberType]
class SoCLinter:
    """Separation of Concerns linter for ToDoWrite framework"""

    # Layers that MUST NOT contain executable content
    NON_EXECUTABLE_LAYERS: ClassVar[set[str]] = {
        "Goal",
        "Concept",
        "Context",
        "Constraints",
        "Requirements",
        "AcceptanceCriteria",
        "InterfaceContract",
        "Phase",
        "Step",
        "Task",
        "SubTask",
    }

    # Patterns that indicate actual executable content (focused on dangerous patterns)
    EXECUTABLE_PATTERNS: ClassVar[list[str]] = [
        r"#!/.*",  # Shebang lines
        r"exec\s*\(",  # Python exec calls
        r"eval\s*\(",  # Python eval calls
        r"subprocess\.",  # Python subprocess
        r"os\.system",  # Python os.system
        r"os\.popen",  # Python os.popen
        r"\$\([^)]+\)",  # Shell command substitution
        r"`[^`]+`",  # Shell backticks with content
        r"import\s+subprocess",  # Subprocess imports
        r"from\s+subprocess",  # Subprocess imports
        r"import\s+os",  # OS imports for system calls
        r"shell=True",  # Dangerous subprocess calls
    ]

    def __init__(self) -> None:
        self.violation_count: int = 0
        self.total_files: int = 0

    def _find_yaml_files(self) -> list[Path]:
        """Find all YAML files in configs/plans/* directories"""
        yaml_files: list[Path] = []
        plans_dir = Path("configs/plans")

        if not plans_dir.exists():
            print(f"ERROR: Plans directory not found: {plans_dir}")
            print("Run 'make tw-init' to initialize directory structure")
            return []

        # Scan all subdirectories for .yaml files
        for subdir in plans_dir.iterdir():
            if subdir.is_dir():
                yaml_files.extend(subdir.glob("*.yaml"))

        return sorted(yaml_files)

    def _load_yaml_file(self, file_path: Path) -> tuple[dict[str, Any], bool]:
        """Load and parse YAML file, return (data, success)"""
        try:
            with open(file_path) as f:
                data = yaml.safe_load(f)
            return data, True
        except yaml.YAMLError as e:
            print(f"ERROR: Invalid YAML in {file_path}: {e}")
            return {}, False
        except Exception as e:
            print(f"ERROR: Failed to read {file_path}: {e}")
            return {}, False

    def _check_for_command_key(
        self, data: dict[str, Any], _file_path: Path
    ) -> list[str]:
        """Check if non-executable layers contain 'command' key"""
        violations: list[str] = []

        layer = data.get("layer", "")
        if layer in self.NON_EXECUTABLE_LAYERS and "command" in data:
            violations.append(
                f"Layer '{layer}' contains forbidden 'command' key (only Layer 12/Command allowed)"
            )

        return violations

    def _check_for_executable_patterns(
        self, data: dict[str, Any], _file_path: Path
    ) -> list[str]:
        """Check for executable patterns in string values"""
        violations: list[str] = []

        # Use the simplified recursive function
        layer = data.get("layer", "")
        if layer in self.NON_EXECUTABLE_LAYERS:
            nested_violations = self._scan_recursive(data, "")
            violations.extend(nested_violations)

        return violations

    def _scan_recursive(self, data: YAMLData, path: str) -> list[str]:
        """Scan data recursively for executable patterns"""
        violations: list[str] = []

        if isinstance(data, str):
            for pattern in self.EXECUTABLE_PATTERNS:
                if re.search(pattern, data, re.IGNORECASE):
                    violations.append(
                        f"Potential executable content found{path}: '{pattern.strip()}' matches in '{data[:100]}...'"
                    )
        elif isinstance(data, dict):
            data_dict: dict[str, YAMLData | YAMLValue] = data
            for key, value in data_dict.items():
                current_path = f"{path}.{key}"
                nested_violations = self._scan_recursive(value, current_path)
                violations.extend(nested_violations)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]"
                nested_violations = self._scan_recursive(item, current_path)
                violations.extend(nested_violations)

        return violations

    def _check_command_layer_requirements(
        self, data: YAMLObject, _file_path: Path
    ) -> list[str]:
        """Check that Command layer has proper structure"""
        violations: list[str] = []

        layer = data.get("layer", "")
        if layer == "Command":
            # Command layer MUST have 'command' key
            if "command" not in data:
                violations.append(
                    "Command layer missing required 'command' key"
                )
            else:
                command_data = data["command"]
                if not isinstance(command_data, dict):
                    violations.append("'command' value must be an object")
                else:
                    # Check for required fields
                    if "ac_ref" not in command_data:
                        violations.append(
                            "Command missing required 'ac_ref' field"
                        )
                    elif not cast("str", command_data["ac_ref"]).startswith(
                        "AC-"
                    ):
                        violations.append(
                            "'ac_ref' must start with 'AC-' prefix"
                        )

                    if "run" not in command_data:
                        violations.append(
                            "Command missing required 'run' field"
                        )
                    elif not isinstance(command_data["run"], dict):
                        violations.append("'run' value must be an object")
                    elif "shell" not in command_data["run"]:
                        violations.append(
                            "Command 'run' missing required 'shell' field"
                        )

        return violations

    def lint_file(self, file_path: Path) -> bool:
        """Lint single YAML file for SoC violations"""
        data, load_success = self._load_yaml_file(file_path)
        if not load_success:
            return False

        violations: list[str] = []

        # Check for command key in non-executable layers
        violations.extend(self._check_for_command_key(data, file_path))

        # Check for executable patterns in content
        violations.extend(self._check_for_executable_patterns(data, file_path))

        # Check Command layer requirements
        violations.extend(
            self._check_command_layer_requirements(data, file_path)
        )

        if violations:
            print(f"✗ {file_path}")
            for violation in violations:
                print(f"  SoC Violation: {violation}")
            print()
            self.violation_count += len(violations)
            return False
        else:
            print(f"✓ {file_path}")
            return True

    def lint_all(self) -> tuple[int, int]:
        """Lint all YAML files, return (clean_files, total_files)"""
        yaml_files = self._find_yaml_files()

        if not yaml_files:
            print("No YAML files found in configs/plans/")
            return 0, 0

        clean_files = 0
        self.total_files = len(yaml_files)

        print(
            f"Linting {self.total_files} YAML files for Separation of Concerns..."
        )
        print()

        for file_path in yaml_files:
            if self.lint_file(file_path):
                clean_files += 1

        return clean_files, self.total_files

    def generate_summary(self, clean_files: int, total_files: int) -> None:
        """Generate linting summary report"""
        print("=" * 50)
        print("SEPARATION OF CONCERNS LINTING SUMMARY")
        print("=" * 50)
        print(f"Total files processed: {total_files}")
        print(f"Clean files: {clean_files}")
        print(f"Files with violations: {total_files - clean_files}")
        print(f"Total violations found: {self.violation_count}")

        if clean_files == total_files:
            print("✓ All files pass SoC requirements!")
            status = "SUCCESS"
        else:
            print(f"✗ {total_files - clean_files} files have SoC violations")
            status = "FAILED"

        print(f"SoC Linting {status}")
        print("=" * 50)


def main() -> None:
    """Main entry point for tw_lint_soc.py"""
    parser = argparse.ArgumentParser(
        description="Lint ToDoWrite YAML files for Separation of Concerns violations"
    )
    parser.add_argument(
        "--summary", action="store_true", help="Show summary report only"
    )

    args = parser.parse_args()

    # Initialize linter
    linter = SoCLinter()

    # Run linting
    clean_files, total_files = linter.lint_all()

    # Generate summary if requested or if there are violations
    if args.summary or clean_files != total_files:
        print()
        linter.generate_summary(clean_files, total_files)

    # Exit with appropriate code
    sys.exit(0 if clean_files == total_files else 1)


if __name__ == "__main__":
    main()
