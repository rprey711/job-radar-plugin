"""foto_aus_docx: das größte Bild aus einem Word-Lebenslauf als Bewerbungsfoto ablegen."""

from __future__ import annotations

import base64
import json
import struct
import subprocess
import sys
import zipfile
from pathlib import Path

import _common
from docx import Document

PNG_1PX = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)


def _run(plugin_root: Path, *args: str, cwd: Path) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(plugin_root / "scripts" / "foto_aus_docx.py"), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=cwd,
    )
    last = proc.stdout.rstrip("\n").splitlines()[-1]
    return proc.returncode, json.loads(last[len(_common.RESULT_PREFIX) :])


def test_extracts_the_picture(plugin_root: Path, workdir: Path):
    png = workdir / "bild.png"
    png.write_bytes(PNG_1PX)
    doc = Document()
    doc.add_paragraph("Anna Test")
    doc.add_picture(str(png))
    (workdir / "Bewerbungsmaterialien").mkdir()
    doc.save(str(workdir / "Bewerbungsmaterialien" / "Lebenslauf_alt.docx"))
    code, result = _run(plugin_root, "Bewerbungsmaterialien/Lebenslauf_alt.docx", cwd=workdir)
    assert code == 0
    assert result["foto"] == "Bewerbungsmaterialien/Bewerbungsfoto.png"
    assert (workdir / "Bewerbungsmaterialien" / "Bewerbungsfoto.png").read_bytes() == PNG_1PX


def test_no_picture_is_a_clear_exit_1(plugin_root: Path, workdir: Path):
    doc = Document()
    doc.add_paragraph("ohne Bild")
    doc.save(str(workdir / "ohne.docx"))
    code, result = _run(plugin_root, "ohne.docx", cwd=workdir)
    assert code == 1
    assert result["foto"] is None
    assert result["hinweis"] == "Kein Bild im Dokument gefunden."


def test_not_a_docx_is_a_clear_exit_1(plugin_root: Path, workdir: Path):
    (workdir / "cv.pdf").write_bytes(b"%PDF-1.4")
    code, result = _run(plugin_root, "cv.pdf", cwd=workdir)
    assert code == 1
    assert result["foto"] is None
    assert "keine Word-Datei" in result["hinweis"]


def test_the_largest_jpeg_wins_over_png_and_emf(plugin_root: Path, workdir: Path):
    png = workdir / "bild.png"
    png.write_bytes(PNG_1PX)
    doc = Document()
    doc.add_picture(str(png))
    docx = workdir / "cv.docx"
    doc.save(str(docx))
    jpeg = b"\xff\xd8\xff\xe0" + b"J" * 1000 + b"\xff\xd9"
    with zipfile.ZipFile(docx, "a") as z:
        z.writestr("word/media/foto.jpeg", jpeg)
        z.writestr("word/media/logo.emf", b"\x01\x00\x00\x00" + b"E" * 5000)
    code, result = _run(plugin_root, "cv.docx", cwd=workdir)
    assert code == 0
    assert result["foto"] == "Bewerbungsmaterialien/Bewerbungsfoto.jpg"
    assert (workdir / "Bewerbungsmaterialien" / "Bewerbungsfoto.jpg").read_bytes() == jpeg
    assert not (workdir / "Bewerbungsmaterialien" / "Bewerbungsfoto.png").exists()


def test_missing_file_is_a_clear_exit_1(plugin_root: Path, workdir: Path):
    code, result = _run(plugin_root, "fehlt.docx", cwd=workdir)
    assert code == 1
    assert result["foto"] is None
    assert result["hinweis"] == "Datei nicht gefunden: fehlt.docx"


def test_corrupt_picture_in_the_docx_is_a_clear_exit_1(plugin_root: Path, workdir: Path):
    png = workdir / "bild.png"
    png.write_bytes(PNG_1PX)
    doc = Document()
    doc.add_picture(str(png))
    docx = workdir / "cv.docx"
    doc.save(str(docx))
    with zipfile.ZipFile(docx) as z:
        info = next(i for i in z.infolist() if i.filename.startswith("word/media/"))
    assert info.compress_type == zipfile.ZIP_DEFLATED
    raw = bytearray(docx.read_bytes())
    # Local file header: 30 bytes, name and extra field lengths at offset 26.
    head = info.header_offset
    name_len, extra_len = struct.unpack("<HH", raw[head + 26 : head + 30])
    start = head + 30 + name_len + extra_len
    raw[start : start + info.compress_size] = b"\xff" * info.compress_size
    docx.write_bytes(bytes(raw))
    code, result = _run(plugin_root, "cv.docx", cwd=workdir)
    assert code == 1
    assert result["foto"] is None
    assert "nicht lesbar" in result["hinweis"]
    assert "keine Word-Datei" not in result["hinweis"]


def test_damaged_word_file_is_not_called_a_non_word_file(plugin_root: Path, workdir: Path):
    doc = Document()
    doc.add_paragraph("Anna Test")
    docx = workdir / "cv.docx"
    doc.save(str(docx))
    jpeg = b"\xff\xd8\xff\xe0" + b"J" * 1000 + b"\xff\xd9"
    with zipfile.ZipFile(docx, "a") as z:
        z.writestr("word/media/foto.jpeg", jpeg, compress_type=zipfile.ZIP_STORED)
    with zipfile.ZipFile(docx) as z:
        info = z.getinfo("word/media/foto.jpeg")
    raw = bytearray(docx.read_bytes())
    # Unkomprimiert: ein geändertes Byte trifft nur die Prüfsumme (Bad CRC-32 beim Lesen).
    head = info.header_offset
    name_len, extra_len = struct.unpack("<HH", raw[head + 26 : head + 30])
    raw[head + 30 + name_len + extra_len + 100] ^= 0xFF
    docx.write_bytes(bytes(raw))
    code, result = _run(plugin_root, "cv.docx", cwd=workdir)
    assert code == 1
    assert result["foto"] is None
    assert result["hinweis"].startswith("cv.docx ist nicht lesbar: Bad CRC")
    assert "keine Word-Datei" not in result["hinweis"]
