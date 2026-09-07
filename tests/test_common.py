"""_common: Dateinamen, Fassungsnummern, relative Pfade, Ergebniszeile, Plugin-Metadaten."""

from __future__ import annotations

import json
from pathlib import Path

import _common
import pytest


def test_sanitize_filename_keeps_umlauts_and_replaces_illegal_chars():
    assert _common.sanitize_filename("Jürgen Müller-Lüdenscheidt") == "Jürgen_Müller-Lüdenscheidt"
    assert _common.sanitize_filename('A/B\\C:D*E?F"G<H>I|J (K)') == "A_B_C_D_E_F_G_H_I_J_K"


def test_next_version_counts_existing_files(tmp_path: Path):
    stem = "Anschreiben_Anna_Test_Beispiel_GmbH"
    assert _common.next_version(tmp_path, stem) == 1
    (tmp_path / f"{stem}_v1.docx").write_bytes(b"")
    (tmp_path / f"{stem}_v1.pdf").write_bytes(b"")
    (tmp_path / f"{stem}_v3.docx").write_bytes(b"")
    (tmp_path / "Anschreiben_Anna_Test_Andere_v9.docx").write_bytes(b"")
    assert _common.next_version(tmp_path, stem) == 4


def test_next_version_of_missing_directory_is_one(tmp_path: Path):
    assert _common.next_version(tmp_path / "gibt es nicht", "x") == 1


def test_relative_posix_inside_and_outside_cwd(workdir: Path, tmp_path: Path):
    inside = workdir / "Bewerbungen" / "Firma" / "Datei.docx"
    assert _common.relative_posix(inside) == "Bewerbungen/Firma/Datei.docx"
    outside = tmp_path / "anderswo.docx"
    assert Path(_common.relative_posix(outside)).is_absolute()


def test_print_result_writes_one_json_line(capsys: pytest.CaptureFixture[str]):
    _common.print_result({"docx": "a/b.docx", "version": 2, "seiten": None})
    out = capsys.readouterr().out.rstrip("\n").splitlines()
    assert out[-1].startswith(_common.RESULT_PREFIX)
    parsed = json.loads(out[-1][len(_common.RESULT_PREFIX) :])
    assert parsed == {"docx": "a/b.docx", "version": 2, "seiten": None}


def test_plugin_metadata_comes_from_the_manifests():
    assert (
        _common.plugin_version()
        == json.loads(
            (_common.PLUGIN_ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        )["version"]
    )
    assert _common.dashboard_url() == "https://jobs.162-55-50-225.nip.io"


def test_find_soffice_prefers_the_env_override(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    fake = tmp_path / "soffice.exe"
    fake.write_bytes(b"")
    monkeypatch.setenv("JOBRADAR_SOFFICE", str(fake))
    assert _common.find_soffice() == fake
    monkeypatch.setenv("JOBRADAR_SOFFICE", str(tmp_path / "fehlt.exe"))
    monkeypatch.setattr(_common.shutil, "which", lambda name: None)
    monkeypatch.setattr(_common, "KNOWN_SOFFICE", [])
    assert _common.find_soffice() is None


def test_find_soffice_override_pointing_nowhere_does_not_fall_back(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Ein gesetzter, aber falscher Pfad soll auffallen, nicht still durch die Suche ersetzt
    werden. `shutil.which` liefert hier absichtlich einen Treffer, damit der Test auch auf
    Rechnern ohne LibreOffice auf dem PATH etwas prüft und nicht zufällig grün ist."""
    monkeypatch.setenv("JOBRADAR_SOFFICE", str(tmp_path / "gibt_es_nicht.exe"))
    monkeypatch.setattr(_common.shutil, "which", lambda name: "/usr/bin/soffice")
    assert _common.find_soffice() is None


def test_count_pdf_pages_reads_page_objects(tmp_path: Path):
    two_pages = (
        b"%PDF-1.4\n1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
        b"2 0 obj << /Type /Pages /Kids [3 0 R 4 0 R] /Count 2 >> endobj\n"
        b"3 0 obj << /Type /Page /Parent 2 0 R >> endobj\n"
        b"4 0 obj << /Type /Page /Parent 2 0 R >> endobj\n%%EOF\n"
    )
    pdf = tmp_path / "zwei.pdf"
    pdf.write_bytes(two_pages)
    assert _common.count_pdf_pages(pdf) == 2
    (tmp_path / "leer.pdf").write_bytes(b"%PDF-1.4\n%%EOF\n")
    assert _common.count_pdf_pages(tmp_path / "leer.pdf") is None
