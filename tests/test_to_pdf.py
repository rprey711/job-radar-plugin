"""to_pdf: LibreOffice zuerst, Word als Ausweg, sonst Exit 4 mit erhaltenem DOCX."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import _common
import pytest
import to_pdf
from docx import Document


def _docx(path: Path, paragraphs: int = 1) -> Path:
    doc = Document()
    for i in range(paragraphs):
        doc.add_paragraph(f"Absatz {i + 1}. " + "Text " * 40)
    doc.save(str(path))
    return path


def test_without_any_converter_returns_none_and_a_hint(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(to_pdf._common, "find_soffice", lambda: None)
    monkeypatch.setattr(to_pdf, "_convert_with_word", lambda docx, outdir: None)
    result = to_pdf.to_pdf(_docx(tmp_path / "a.docx"))
    assert result["pdf"] is None
    assert result["methode"] is None
    assert "Word" in result["hinweis"]


def test_word_fallback_is_used_when_libreoffice_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(to_pdf._common, "find_soffice", lambda: None)
    fake_pdf = tmp_path / "a.pdf"

    def fake_word(docx: Path, outdir: Path) -> Path:
        fake_pdf.write_bytes(b"%PDF-1.4\n1 0 obj << /Type /Page >> endobj\n%%EOF\n")
        return fake_pdf

    monkeypatch.setattr(to_pdf, "_convert_with_word", fake_word)
    result = to_pdf.to_pdf(_docx(tmp_path / "a.docx"))
    assert result["pdf"] == _common.relative_posix(fake_pdf)
    assert result["methode"] == "word"
    assert result["seiten"] == 1


def test_libreoffice_converts_and_counts_pages(tmp_path: Path, soffice: Path):
    docx = _docx(tmp_path / "lang.docx", paragraphs=80)
    result = to_pdf.to_pdf(docx)
    assert result["methode"] == "libreoffice"
    pdf = tmp_path / "lang.pdf"
    assert pdf.is_file()
    assert result["seiten"] is None or result["seiten"] >= 2


def test_cli_exit_code_and_result_line(
    tmp_path: Path, plugin_root: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setenv("JOBRADAR_SOFFICE", str(tmp_path / "fehlt.exe"))
    docx = _docx(tmp_path / "a.docx")
    proc = subprocess.run(
        [sys.executable, str(plugin_root / "scripts" / "to_pdf.py"), str(docx)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=tmp_path,
    )
    if proc.returncode == 0:
        pytest.skip("Word hat konvertiert; der Ausweg ohne Konverter ist hier nicht testbar")
    assert proc.returncode == 4
    line = proc.stdout.rstrip("\n").splitlines()[-1]
    data = json.loads(line[len(_common.RESULT_PREFIX) :])
    assert data["pdf"] is None
    assert docx.is_file()
