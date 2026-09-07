"""einrichten: Ordnerstruktur, README und CLAUDE.md aus den Vorlagen, Profilvorlagen, Sortieren,
stand.json; ein zweiter Lauf aendert nichts Bestehendes."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import _common
import einrichten

FOLDERS = ("Profil", "Bewerbungsmaterialien", "Bewerbungen", ".jobradar")


def test_setup_creates_the_structure_and_fills_placeholders(workdir: Path):
    result = einrichten.setup(workdir, name="Anna Test", surface="cowork")
    for folder in FOLDERS:
        assert (workdir / folder).is_dir()
    readme = (workdir / "README.md").read_text(encoding="utf-8")
    claude = (workdir / "CLAUDE.md").read_text(encoding="utf-8")
    assert "Anna Test" in readme and "Anna Test" in claude
    assert "{{" not in readme and "{{" not in claude
    assert _common.plugin_version() in claude
    assert _common.dashboard_url() in claude
    for name in ("Kandidatenprofil.md", "Bewerbungsmethode.md", "Style_Guide.md", "Lernnotizen.md"):
        assert (workdir / "Profil" / name).is_file()
    stand = json.loads((workdir / ".jobradar" / "stand.json").read_text(encoding="utf-8"))
    assert stand["name"] == "Anna Test" and stand["oberflaeche"] == "cowork"
    assert stand["plugin_version"] == _common.plugin_version()
    assert stand["eingerichtet_am"]
    assert "README.md" in result["angelegt"] and "Profil/Kandidatenprofil.md" in result["angelegt"]


def test_loose_files_move_into_materials(workdir: Path):
    (workdir / "Lebenslauf alt.pdf").write_bytes(b"pdf")
    (workdir / "Anschreiben_Firma.docx").write_bytes(b"docx")
    (workdir / "Notizen.txt").write_text("x", encoding="utf-8")
    (workdir / "foto.JPG").write_bytes(b"jpg")
    (workdir / ".versteckt.pdf").write_bytes(b"pdf")
    (workdir / "Unterordner").mkdir()
    (workdir / "Unterordner" / "bleibt.pdf").write_bytes(b"pdf")
    result = einrichten.setup(workdir, name="Anna Test")
    materials = workdir / "Bewerbungsmaterialien"
    assert (materials / "Lebenslauf alt.pdf").is_file()
    assert (materials / "Anschreiben_Firma.docx").is_file()
    assert (materials / "Notizen.txt").is_file()
    assert (materials / "foto.JPG").is_file()
    assert (workdir / ".versteckt.pdf").is_file()
    assert (workdir / "Unterordner" / "bleibt.pdf").is_file()
    assert (workdir / "README.md").is_file() and (workdir / "CLAUDE.md").is_file()
    assert sorted(result["verschoben"]) == sorted(
        ["Anschreiben_Firma.docx", "Lebenslauf alt.pdf", "Notizen.txt", "foto.JPG"]
    )


def test_name_conflicts_get_a_suffix(workdir: Path):
    (workdir / "Bewerbungsmaterialien").mkdir()
    (workdir / "Bewerbungsmaterialien" / "cv.pdf").write_bytes(b"alt")
    (workdir / "cv.pdf").write_bytes(b"neu")
    einrichten.setup(workdir, name="Anna Test")
    assert (workdir / "Bewerbungsmaterialien" / "cv.pdf").read_bytes() == b"alt"
    assert (workdir / "Bewerbungsmaterialien" / "cv_1.pdf").read_bytes() == b"neu"


def test_second_run_keeps_existing_files(workdir: Path):
    einrichten.setup(workdir, name="Anna Test", surface="claude_code")
    (workdir / "README.md").write_text("mein eigener Text", encoding="utf-8")
    (workdir / "Profil" / "Kandidatenprofil.md").write_text("# ausgefüllt", encoding="utf-8")
    first_stand = json.loads((workdir / ".jobradar" / "stand.json").read_text(encoding="utf-8"))
    result = einrichten.setup(workdir, name="Anna Test")
    assert (workdir / "README.md").read_text(encoding="utf-8") == "mein eigener Text"
    assert (workdir / "Profil" / "Kandidatenprofil.md").read_text(
        encoding="utf-8"
    ) == "# ausgefüllt"
    assert "README.md" in result["vorhanden"]
    assert result["angelegt"] == []
    stand = json.loads((workdir / ".jobradar" / "stand.json").read_text(encoding="utf-8"))
    assert stand["eingerichtet_am"] == first_stand["eingerichtet_am"]
    assert stand["oberflaeche"] == "claude_code"


def test_rewrite_flag_refreshes_readme_and_claude_md(workdir: Path):
    einrichten.setup(workdir, name="Anna Test")
    (workdir / "CLAUDE.md").write_text("alt", encoding="utf-8")
    einrichten.setup(workdir, name="Anna Test", rewrite=True)
    assert "Anna Test" in (workdir / "CLAUDE.md").read_text(encoding="utf-8")


def test_cli(plugin_root: Path, workdir: Path):
    proc = subprocess.run(
        [
            sys.executable,
            str(plugin_root / "scripts" / "einrichten.py"),
            "--name",
            "Anna Test",
            "--oberflaeche",
            "cowork",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=workdir,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    line = proc.stdout.rstrip("\n").splitlines()[-1]
    data = json.loads(line[len(_common.RESULT_PREFIX) :])
    assert data["ordner"] == workdir.resolve().as_posix()
    assert (workdir / ".jobradar" / "stand.json").is_file()


def test_cli_refuses_an_empty_name(plugin_root: Path, workdir: Path):
    proc = subprocess.run(
        [sys.executable, str(plugin_root / "scripts" / "einrichten.py"), "--name", "  "],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=workdir,
    )
    assert proc.returncode == 1
    assert not (workdir / "Profil").exists()
