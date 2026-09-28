"""check_env: Python-Version, Pakete, LibreOffice, Word; Exit 0 nur, wenn Rendern moeglich ist."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import _common
import check_env
import pytest


def test_report_lists_python_and_packages():
    report = check_env.report()
    assert report["python"]["version"].startswith(f"{sys.version_info[0]}.{sys.version_info[1]}")
    assert report["python"]["ok"] is True
    assert set(report["pakete"]) == {"python-docx", "docxtpl", "pyyaml"}
    assert all(report["pakete"].values())
    assert report["plugin_version"] == _common.plugin_version()
    assert "libreoffice" in report and "word" in report


def test_missing_package_fails_with_pip_hint(monkeypatch: pytest.MonkeyPatch):
    def fake_find_spec(name: str):
        return None if name == "docxtpl" else object()

    monkeypatch.setattr(check_env.importlib.util, "find_spec", fake_find_spec)
    report = check_env.report()
    assert report["pakete"]["docxtpl"] is False
    assert report["ok"] is False
    assert "pip install -r" in report["hinweis"]
    assert "requirements.txt" in report["hinweis"]
    # Beide Pfade in Anführungszeichen: venv-Pfade unter OneDrive enthalten Leerzeichen.
    assert f'"{sys.executable}" -m pip install -r "' in report["hinweis"]


def test_old_python_fails(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_env, "MIN_PYTHON", (99, 0))
    report = check_env.report()
    assert report["python"]["ok"] is False
    assert report["ok"] is False


def test_cli_prints_summary_and_result_line(plugin_root: Path):
    proc = subprocess.run(
        [sys.executable, str(plugin_root / "scripts" / "check_env.py")],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    lines = proc.stdout.rstrip("\n").splitlines()
    assert lines[-1].startswith(_common.RESULT_PREFIX)
    data = json.loads(lines[-1][len(_common.RESULT_PREFIX) :])
    assert data["ok"] is True
    assert "Python" in proc.stdout


def test_report_has_a_calibri_field():
    assert "schrift_calibri" in check_env.report()


def test_calibri_found_via_fc_list(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_env.platform, "system", lambda: "Linux")
    monkeypatch.setattr(check_env.shutil, "which", lambda name: "/usr/bin/fc-list")
    monkeypatch.setattr(
        check_env, "_fc_list", lambda: "Carlito:style=Regular\nDejaVu Sans:style=Book\n"
    )
    assert check_env.calibri_verfuegbar() is True


def test_calibri_missing_is_reported_with_a_hint(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_env, "calibri_verfuegbar", lambda: False)
    report = check_env.report()
    assert report["schrift_calibri"] is False
    assert report["ok"] is True  # fonts never block rendering
    assert "Ersatzschrift" in (report["schrift_hinweis"] or "")


def test_font_check_errors_do_not_break_the_report(monkeypatch: pytest.MonkeyPatch):
    def boom():
        raise OSError("fc-list kaputt")

    monkeypatch.setattr(check_env, "calibri_verfuegbar", boom)
    report = check_env.report()
    assert report["schrift_calibri"] is None
