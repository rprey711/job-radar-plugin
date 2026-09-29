"""Skript-Flags kommen nur hinzu (E12 C). Server-Texte und ältere Skills rufen die Skripte mit
diesen Flags auf, also darf keins verschwinden oder umbenannt werden. Ein neues Flag kommt hier
dazu, ein altes geht nie."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

# Every flag and fixed choice a script accepts as of 0.3.0. check_env.py takes none.
FLAGS = {
    "einrichten.py": (
        "--name",
        "--ordner",
        "--oberflaeche",
        "{cowork,claude_code,unbekannt}",
        "--neu-schreiben",
    ),
    "read_docx.py": ("--max-zeichen",),
    "foto_aus_docx.py": ("--ziel",),
    "cv_master.py": (
        "--data",
        "--name",
        "--output-dir",
        "--template",
        "--version",
        "--pdf",
        "--master",
    ),
    "cover_master.py": (
        "--data",
        "--name",
        "--firma",
        "--output-dir",
        "--template",
        "--version",
        "--max-words",
        "--pdf",
    ),
    "to_pdf.py": ("--outdir",),
}


def test_every_script_with_arguments_is_listed(plugin_root: Path):
    scripts = {p.name for p in (plugin_root / "scripts").glob("*.py")}
    assert scripts - {"_common.py", "check_env.py"} == set(FLAGS)


@pytest.mark.parametrize("script", sorted(FLAGS))
def test_script_keeps_its_flags(plugin_root: Path, script: str):
    proc = subprocess.run(
        [sys.executable, str(plugin_root / "scripts" / script), "--help"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    for flag in FLAGS[script]:
        assert flag in proc.stdout, f"{script}: {flag} fehlt, Flags kommen nur hinzu"
