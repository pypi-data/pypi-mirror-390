#!/usr/bin/env python3
"""
ToDoWrite Command Stub Generator (tw_stub_command.py)
Generates executable command stubs from Acceptance Criteria
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml


class CommandStubGenerator:
    """Generates Command layer stubs from Acceptance Criteria"""

    def __init__(self) -> None:
        self.generated_count: int = 0
        self.ac_files: list[Path] = []
        self.existing_commands: set[str] = set()

    def _find_acceptance_criteria_files(self) -> list[Path]:
        """Find all Acceptance Criteria YAML files"""
        ac_dir = Path("configs/plans/acceptance_criteria")
        if not ac_dir.exists():
            print(f"ERROR: Acceptance Criteria directory not found: {ac_dir}")
            return []

        ac_files = list(ac_dir.glob("AC-*.yaml"))
        print(f"Found {len(ac_files)} Acceptance Criteria files")
        return sorted(ac_files)

    def _find_existing_commands(self) -> None:
        """Find existing command files to avoid duplicates"""
        commands_dir = Path("configs/commands")
        if commands_dir.exists():
            for cmd_file in commands_dir.glob("CMD-*.yaml"):
                # Extract AC reference from existing command
                try:
                    with open(cmd_file) as f:
                        data = yaml.safe_load(f)
                    ac_ref = data.get("command", {}).get("ac_ref", "")
                    if ac_ref:
                        self.existing_commands.add(ac_ref)
                except Exception as e:
                    print(
                        f"WARNING: Failed to read existing command file {cmd_file}: {e}"
                    )
                    continue

        print(f"Found {len(self.existing_commands)} existing commands")

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

    def _generate_command_id(self, ac_id: str) -> str:
        """Generate Command ID from Acceptance Criteria ID"""
        # Convert AC-EXAMPLE-NAME to CMD-EXAMPLE-NAME
        if ac_id.startswith("AC-"):
            return ac_id.replace("AC-", "CMD-", 1)
        else:
            return f"CMD-{ac_id}"

    def _generate_shell_command(self, ac_data: dict[str, Any]) -> str:
        """Generate appropriate shell command based on AC content"""
        title = ac_data.get("title", "").lower()

        # Determine command type based on content
        if "makefile" in title or "targets" in title:
            return "make tw-all && echo 'Makefile targets verified'"
        elif "validation" in title or "schema" in title:
            return "python todowrite/tools/tw_validate.py --strict"
        elif "lint" in title or "soc" in title:
            return "python todowrite/tools/tw_lint_soc.py"
        elif "trace" in title or "links" in title:
            return "python todowrite/tools/tw_trace.py"
        elif "cli" in title or "command" in title:
            return "python -m todowrite --help && echo 'CLI commands verified'"
        elif "documentation" in title or "docs" in title:
            return "find docs -name '*.md' -exec echo 'Documentation file: {}' \\; && echo 'Documentation verified'"
        elif "test" in title:
            return "python -m pytest tests/ -v"
        else:
            # Generic validation command
            title = ac_data.get("title", "Acceptance Criteria")
            return f"echo 'Manual verification required for: {title}'"

    def _generate_artifacts_list(self, ac_data: dict[str, Any]) -> list[str]:
        """Generate expected artifacts list"""
        title = ac_data.get("title", "").lower()
        cmd_id = self._generate_command_id(ac_data.get("id", ""))

        artifacts = [f"results/{cmd_id}/execution.log"]

        if "makefile" in title:
            artifacts.extend(
                [
                    f"results/{cmd_id}/make_output.log",
                    "configs/schemas/todowrite.schema.json",
                ]
            )
        elif "validation" in title:
            artifacts.extend(
                [
                    f"results/{cmd_id}/validation_report.json",
                    f"results/{cmd_id}/schema_errors.log",
                ]
            )
        elif "trace" in title:
            artifacts.extend(
                [
                    "trace/trace.csv",
                    "trace/graph.json",
                    f"results/{cmd_id}/traceability_report.json",
                ]
            )
        elif "test" in title:
            artifacts.extend(
                [
                    f"results/{cmd_id}/test_results.xml",
                    f"results/{cmd_id}/coverage_report.json",
                ]
            )
        elif "documentation" in title:
            artifacts.extend([f"results/{cmd_id}/doc_verification.json"])

        return artifacts

    def generate_command_stub(self, ac_file: Path) -> bool:
        """Generate command stub for single Acceptance Criteria file"""
        ac_data, success = self._load_yaml_file(ac_file)
        if not success:
            return False

        ac_id = ac_data.get("id", "")
        if not ac_id or not ac_id.startswith("AC-"):
            print(f"WARNING: Invalid AC ID in {ac_file}: {ac_id}")
            return False

        # Skip if command already exists
        if ac_id in self.existing_commands:
            print(f"SKIP: Command already exists for {ac_id}")
            return True

        cmd_id = self._generate_command_id(ac_id)
        shell_command = self._generate_shell_command(ac_data)
        artifacts = self._generate_artifacts_list(ac_data)

        # Create command stub YAML
        command_data = {
            "id": cmd_id,
            "layer": "Command",
            "title": f"Execute validation for {ac_data.get('title', 'Acceptance Criteria')}",
            "description": f"Automated execution to verify: {ac_data.get('description', '')[:200]}...",
            "metadata": {
                "owner": ac_data.get("metadata", {}).get("owner", "system"),
                "labels": ["generated", "automated", "verification"],
                "severity": ac_data.get("metadata", {}).get("severity", "med"),
                "work_type": "validation",
            },
            "links": {"parents": [ac_id], "children": []},
            "command": {
                "ac_ref": ac_id,
                "run": {
                    "shell": shell_command,
                    "workdir": ".",
                    "env": {"TODOWRITE_MODE": "validation", "AC_REF": ac_id},
                },
                "artifacts": artifacts,
            },
        }

        # Write command file
        commands_dir = Path("configs/commands")
        commands_dir.mkdir(exist_ok=True)

        cmd_file = commands_dir / f"{cmd_id}.yaml"
        try:
            with open(cmd_file, "w") as f:
                yaml.dump(
                    command_data, f, default_flow_style=False, sort_keys=False
                )

            print(f"✓ Generated {cmd_file}")
            self.generated_count += 1
            return True

        except Exception as e:
            print(f"ERROR: Failed to write {cmd_file}: {e}")
            return False

    def update_ac_children_links(self, ac_file: Path, cmd_id: str) -> bool:
        """Update Acceptance Criteria file to include command in children links"""
        ac_data, success = self._load_yaml_file(ac_file)
        if not success:
            return False

        # Add command to children links if not already present
        children = ac_data.get("links", {}).get("children", [])
        if cmd_id not in children:
            children.append(cmd_id)
            ac_data.setdefault("links", {})["children"] = children

            try:
                with open(ac_file, "w") as f:
                    yaml.dump(
                        ac_data, f, default_flow_style=False, sort_keys=False
                    )
                return True
            except Exception as e:
                print(f"ERROR: Failed to update {ac_file}: {e}")
                return False

        return True

    def generate_all_stubs(self) -> tuple[int, int]:
        """Generate command stubs for all Acceptance Criteria"""
        self.ac_files = self._find_acceptance_criteria_files()
        self._find_existing_commands()

        if not self.ac_files:
            print("No Acceptance Criteria files found")
            return 0, 0

        print(
            f"Generating command stubs for {len(self.ac_files)} Acceptance Criteria..."
        )
        print()

        success_count = 0
        for ac_file in self.ac_files:
            if self.generate_command_stub(ac_file):
                success_count += 1

                # Update AC file with command link
                ac_data, _ = self._load_yaml_file(ac_file)
                if ac_data:
                    cmd_id = self._generate_command_id(ac_data.get("id", ""))
                    self.update_ac_children_links(ac_file, cmd_id)

        return success_count, len(self.ac_files)

    def generate_summary(self, success_count: int, total_count: int) -> None:
        """Generate command stub generation summary"""
        print("=" * 50)
        print("COMMAND STUB GENERATION SUMMARY")
        print("=" * 50)
        print(f"Acceptance Criteria processed: {total_count}")
        print(f"Command stubs generated: {self.generated_count}")
        print(f"Existing commands skipped: {len(self.existing_commands)}")
        print(f"Success rate: {success_count}/{total_count}")

        if success_count == total_count:
            print("✓ All command stubs generated successfully!")
            status = "SUCCESS"
        else:
            print(f"✗ {total_count - success_count} failures occurred")
            status = "PARTIAL"

        print(f"Command Generation {status}")
        print("=" * 50)


def main() -> None:
    """Main entry point for tw_stub_command.py"""
    parser = argparse.ArgumentParser(
        description="Generate ToDoWrite command stubs from Acceptance Criteria"
    )
    parser.add_argument(
        "--summary", action="store_true", help="Show summary report only"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate existing command stubs",
    )

    args = parser.parse_args()

    # Initialize generator
    generator = CommandStubGenerator()

    if args.force:
        # Clear existing commands if force flag is used
        commands_dir = Path("configs/commands")
        if commands_dir.exists():
            for cmd_file in commands_dir.glob("CMD-*.yaml"):
                cmd_file.unlink()
            print("Cleared existing command stubs")

    # Generate command stubs
    success_count, total_count = generator.generate_all_stubs()

    # Generate summary
    if args.summary or generator.generated_count > 0:
        print()
        generator.generate_summary(success_count, total_count)

    # Exit with appropriate code
    sys.exit(0 if success_count == total_count else 1)


if __name__ == "__main__":
    main()
