"""Rendering details of the CV: escaping, lists, empty sections, photo, metadata."""

from __future__ import annotations

import zipfile
from pathlib import Path

import cv_master
import yaml

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "plugins" / "job-radar" / "templates" / "Lebenslauf_template.docx"
FIXTURES = Path(__file__).parent / "fixtures"


def _data(tmp_path: Path, **changes) -> Path:
    raw = yaml.safe_load((FIXTURES / "dummy_data.yml").read_text(encoding="utf-8"))
    raw.update(changes)
    path = tmp_path / "daten.yml"
    path.write_text(yaml.safe_dump(raw, allow_unicode=True), encoding="utf-8")
    return path


def _render(tmp_path: Path, **changes) -> Path:
    out = tmp_path / "cv.docx"
    cv_master.render_docx(TEMPLATE, cv_master.load_data(_data(tmp_path, **changes)), out)
    return out


def _xml(path: Path, part: str = "word/document.xml") -> str:
    with zipfile.ZipFile(path) as z:
        return z.read(part).decode("utf-8")


def test_ampersand_and_angle_brackets_survive(tmp_path: Path):
    out = _render(tmp_path, skills_section="Tools: A & B | Methoden: <C>")
    xml = _xml(out)
    assert "B.A. Marketing &amp; Kommunikation" in xml
    assert "TOOLS &amp; METHODEN" in xml
    assert "Tools: A &amp; B | Methoden: &lt;C&gt;" in xml
