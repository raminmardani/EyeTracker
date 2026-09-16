"""Packaging invariants.

Layer: test
"""

import pathlib
import re
import subprocess
import sys


def test_eye_tracker_and_main_import_without_path_manipulation(tmp_path):
    """FR-26: both targets import from a foreign cwd with PYTHONPATH cleared.

    Runs in a subprocess from tmp_path so the repository root cannot be on
    sys.path implicitly — the failure mode a same-process assert would miss.
    """
    result = subprocess.run(
        [sys.executable, "-c", "import eye_tracker, main; print('ok')"],
        cwd=tmp_path,
        env={**{k: v for k, v in __import__("os").environ.items() if k != "PYTHONPATH"}},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout


def test_no_test_file_manipulates_sys_path():
    """FR-26: the fragility this story removes must not creep back in."""
    offenders = []
    for path in pathlib.Path("tests").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if re.search(r"sys\.path\.(append|insert)", text):
            offenders.append(str(path))
    assert offenders == [], f"sys.path manipulation found in: {offenders}"
