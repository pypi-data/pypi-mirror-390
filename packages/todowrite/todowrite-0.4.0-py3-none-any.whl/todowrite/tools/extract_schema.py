from __future__ import annotations

import json
import re
from pathlib import Path


def extract_and_write_schema(
    markdown_path: Path, schema_output_path: Path
) -> None:
    """
    Extracts the JSON schema from a Markdown file and writes it to a specified output path.
    """
    try:
        markdown_content = markdown_path.read_text()
        # Regex to find the JSON schema block in the Markdown file
        match = re.search(
            r"```json\n({.*?})\n```", markdown_content, re.DOTALL
        )

        if match:
            schema_json_str = match.group(1)
            schema_data = json.loads(schema_json_str)

            schema_output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(schema_output_path, "w") as f:
                json.dump(schema_data, f, indent=2)
            print(
                f"✅ JSON schema extracted from {markdown_path} and written to {schema_output_path}"
            )
        else:
            print(f"❌ No JSON schema block found in {markdown_path}")
            exit(1)
    except FileNotFoundError:
        print(f"❌ Markdown file not found: {markdown_path}")
        exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in schema block: {e}")
        exit(1)
    except (ValueError, KeyError, AttributeError) as e:
        print(f"❌ An unexpected error occurred: {e}")
        exit(1)


if __name__ == "__main__":
    # Assuming the script is run from the project root
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    markdown_file = project_root / "ToDoWrite.md"
    schema_file = (
        project_root
        / "ToDoWrite"
        / "todowrite"
        / "schemas"
        / "todowrite.schema.json"
    )
    extract_and_write_schema(markdown_file, schema_file)
