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


def _windows(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> tuple[Path, Path]:
    """Windows ohne LibreOffice, mit leeren System- und Benutzer-Schriftordnern unter tmp_path."""
    windir = tmp_path / "Windows"
    (windir / "Fonts").mkdir(parents=True)
    local = tmp_path / "AppData" / "Local"
    (local / "Microsoft" / "Windows" / "Fonts").mkdir(parents=True)
    monkeypatch.setattr(check_env.platform, "system", lambda: "Windows")
    monkeypatch.setenv("WINDIR", str(windir))
    monkeypatch.setenv("LOCALAPPDATA", str(local))
    monkeypatch.setattr(check_env._common, "find_soffice", lambda: None)
    return windir / "Fonts", local / "Microsoft" / "Windows" / "Fonts"


def test_calibri_found_in_the_windows_fonts_folder(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    system_fonts, _user_fonts = _windows(monkeypatch, tmp_path)
    (system_fonts / "carlito-regular.ttf").write_bytes(b"")
    assert check_env.calibri_verfuegbar() is True


def test_calibri_missing_in_empty_windows_fonts_folders(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    system_fonts, _user_fonts = _windows(monkeypatch, tmp_path)
    (system_fonts / "arial.ttf").write_bytes(b"")
    assert check_env.calibri_verfuegbar() is False


def test_calibri_found_among_the_users_own_fonts(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    _system_fonts, user_fonts = _windows(monkeypatch, tmp_path)
    (user_fonts / "Calibri.ttf").write_bytes(b"")
    assert check_env.calibri_verfuegbar() is True


def test_missing_fc_list_on_linux_is_not_checkable(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_env.platform, "system", lambda: "Linux")
    monkeypatch.setattr(check_env.shutil, "which", lambda name: None)
    assert check_env.calibri_verfuegbar() is None


def test_calibri_missing_in_fc_list(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_env.platform, "system", lambda: "Linux")
    monkeypatch.setattr(check_env.shutil, "which", lambda name: "/usr/bin/fc-list")
    monkeypatch.setattr(check_env, "_fc_list", lambda: "DejaVu Sans:style=Book\nLiberation Serif\n")
    assert check_env.calibri_verfuegbar() is False


def test_undecodable_fc_list_output_still_finds_carlito(monkeypatch: pytest.MonkeyPatch):
    echtes_run = subprocess.run
    # Ein Schriftname mit einem Byte, das kein UTF-8 ist, gleich hinter „Carlito“.
    fc_list_ersatz = r"import sys;sys.stdout.buffer.write(b'Carlito\xff\n')"

    def run(args: list[str], **kwargs):
        assert args == ["fc-list", ":", "family"]
        return echtes_run([sys.executable, "-c", fc_list_ersatz], **kwargs)

    monkeypatch.setattr(check_env.platform, "system", lambda: "Linux")
    monkeypatch.setattr(check_env.shutil, "which", lambda name: "/usr/bin/fc-list")
    monkeypatch.setattr(check_env.subprocess, "run", run)
    assert check_env.calibri_verfuegbar() is True


@pytest.mark.parametrize(
    "schrift, status", [(True, "ok"), (False, "fehlt"), (None, "nicht prüfbar")]
)
def test_summary_names_the_font_status(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], schrift, status: str
):
    monkeypatch.setattr(check_env, "calibri_verfuegbar", lambda: schrift)
    check_env._print_summary(check_env.report())
    assert f"Schrift Calibri oder Carlito: {status}" in capsys.readouterr().out.splitlines()
