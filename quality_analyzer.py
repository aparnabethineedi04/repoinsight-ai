
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def analyze_python_code(source_code: str) -> dict:
    """Analyze Python code using Ruff without executing the submitted code."""

    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / "analyzed_file.py"
        file_path.write_text(source_code, encoding="utf-8")

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ruff",
                "check",
                "--output-format",
                "json",
                "--select",
                "E,F,I",
                str(file_path),
            ],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        if result.returncode not in (0, 1):
            raise RuntimeError(
                result.stderr or "Ruff analysis failed."
            )

        issues = json.loads(result.stdout or "[]")

    error_count = sum(
        1 for issue in issues
        if issue["code"].startswith(("E", "F"))
    )
    warning_count = len(issues) - error_count

    return {
        "issue_count": len(issues),
        "error_count": error_count,
        "warning_count": warning_count,
        "issues": [
            {
                "code": issue["code"],
                "message": issue["message"],
                "line": issue["location"]["row"],
                "column": issue["location"]["column"],
            }
            for issue in issues
        ],
    }
 