"""Skills: Frontmatter passt zum Ordnernamen, alle vierzehn Befehle da, jeder holt sein Skript."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

SKILLS = Path(__file__).resolve().parent.parent / "plugins" / "job-radar" / "skills"
THIN = {
    "onboarding": "onboarding",
    "kurzprofil": "kurzprofil",
    "lebenslauf": "lebenslauf",
    "anschreiben-vorlage": "anschreiben_vorlage",
    "suchprofil": "suchprofil",
    "bewerten": "bewerten",
    "triage": "triage",
    "bewerbung": "bewerbung",
    "review": "review",
    "interview": "interview",
    "scout": "scout",
    "kalibrierung": "kalibrierung",
    "hilfe": "hilfe",
}
WITH_ARGUMENT = {"bewerbung", "interview"}


def _frontmatter(skill: str) -> tuple[dict, str]:
    text = (SKILLS / skill / "SKILL.md").read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{skill}: kein Frontmatter"
    _, header, body = text.split("---\n", 2)
    return yaml.safe_load(header), body


def test_einrichten_has_its_own_content():
    meta, body = _frontmatter("einrichten")
    assert meta["name"] == "einrichten"
    assert meta["disable-model-invocation"] is True
    assert len(meta["description"]) <= 1024
    for needle in (
        "check_env.py",
        "einrichten.py",
        "job_radar_status",
        'modul_erledigt="ordner"',
        "${CLAUDE_PLUGIN_ROOT}",
    ):
        assert needle in body, f"{needle} fehlt in /einrichten"
    assert "anleitung_laden" not in body.split("## Regeln")[0]


def test_exactly_the_fourteen_skills_exist():
    found = {p.name for p in SKILLS.iterdir() if p.is_dir()}
    assert found == set(THIN) | {"einrichten"}
    for skill in found:
        assert (SKILLS / skill / "SKILL.md").is_file()


@pytest.mark.parametrize("skill,thema", sorted(THIN.items()))
def test_thin_skill_fetches_its_script_from_the_server(skill: str, thema: str):
    meta, body = _frontmatter(skill)
    assert meta["name"] == skill
    assert meta["disable-model-invocation"] is True
    assert 40 <= len(meta["description"]) <= 1024
    assert "job_radar_status" in body
    assert f'anleitung_laden(thema="{thema}")' in body
    assert f".jobradar/ablauf_{thema}.md" in body
    assert "werden ignoriert" in body
    assert "WERKZEUGE.md" in body
    if skill in WITH_ARGUMENT:
        assert meta["argument-hint"] == "<Firma>"
        assert "$ARGUMENTS" in body
    else:
        assert "argument-hint" not in meta


def test_werkzeuge_doc_names_every_script_and_the_result_line():
    text = (SKILLS.parent / "docs" / "WERKZEUGE.md").read_text(encoding="utf-8")
    for script in (
        "check_env.py",
        "einrichten.py",
        "read_docx.py",
        "cv_master.py",
        "cover_master.py",
        "to_pdf.py",
    ):
        assert script in text
    assert "JOBRADAR_RESULT" in text and "dokument_registrieren" in text
    for kind in (
        "master_lebenslauf",
        "lebenslauf",
        "anschreiben",
        "recherche",
        "interview_briefing",
        "sonstiges",
    ):
        assert kind in text
