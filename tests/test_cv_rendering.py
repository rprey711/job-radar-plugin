"""Rendering details of the CV: escaping, lists, empty sections, photo, metadata."""

from __future__ import annotations

import re
import zipfile
from pathlib import Path

import cv_master
import yaml
from docx import Document

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


def _paragraphs(path: Path) -> list[str]:
    doc = Document(str(path))
    texts = [p.text for p in doc.paragraphs]
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                texts += [p.text for p in cell.paragraphs]
    return texts


def test_empty_sections_disappear_with_their_heading(tmp_path: Path):
    texts = _paragraphs(_render(tmp_path, international=[], weiteres=[]))
    assert "INTERNATIONALER HINTERGRUND" not in texts
    assert "WEITERES" not in texts


def test_filled_sections_are_list_items_without_literal_bullets(tmp_path: Path):
    out = _render(
        tmp_path, international=["Auslandssemester Lyon"], weiteres=["Führerschein B", "Ehrenamt"]
    )
    doc = Document(str(out))
    items = [
        p
        for p in doc.paragraphs
        if p.text in ("Auslandssemester Lyon", "Führerschein B", "Ehrenamt")
    ]
    assert len(items) == 3
    for p in items:
        assert p._p.pPr is not None and p._p.pPr.numPr is not None
    assert not any(t.startswith("•") for t in _paragraphs(out))


def test_achievements_are_plain_list_items(tmp_path: Path):
    doc = Document(str(_render(tmp_path)))
    bullets = [p for p in doc.paragraphs if p.text.startswith("Aufbau einer Content-Strategie")]
    assert len(bullets) == 1
    p = bullets[0]
    assert p._p.pPr.numPr is not None
    for run in p.runs:
        assert not run.bold and not run.italic
        assert run.font.color is None or run.font.color.rgb is None


def test_no_empty_paragraphs_from_loop_tags(tmp_path: Path):
    doc = Document(str(_render(tmp_path)))
    body = [p.text for p in doc.paragraphs]
    # Between the first heading and BILDUNG only content lines, no blanks left by {% %} tags.
    start, end = body.index("BERUFSERFAHRUNG"), body.index("BILDUNG")
    assert "" not in body[start + 1 : end]


def test_template_uses_calibri_and_has_no_picture_or_personal_metadata():
    with zipfile.ZipFile(TEMPLATE) as z:
        names = z.namelist()
        theme = z.read("word/theme/theme1.xml").decode("utf-8")
        props = z.read("docProps/core.xml").decode("utf-8") + z.read("docProps/app.xml").decode(
            "utf-8"
        )
    assert not [n for n in names if n.startswith("word/media/")]
    assert 'typeface="Aptos' not in theme
    assert re.search(r'<a:latin typeface="Calibri"', theme)
    assert "Raul" not in props and "Prey" not in props
