"""Vorlagen: Platzhalter vorhanden, Modelltabelle aus Spec 7.4, keine Altlasten aus v1."""

from __future__ import annotations

from pathlib import Path

import pytest

TEMPLATES = Path(__file__).resolve().parent.parent / "plugins" / "job-radar" / "templates"
PLACEHOLDERS = ("{{NAME}}", "{{DATUM}}", "{{PLUGIN_VERSION}}", "{{DASHBOARD}}")
FORBIDDEN = (
    "Notion",
    "n8n",
    "—",
    "/score-jobs",
    "/cv-tageinz",
    "cover-template",
    "/bewerbung-review",
    "/scout-jobs",
    "/search-config",
    "CANDIDATE_PROFILE",
    "APPLICATION_METHOD",
    "STYLE_GUIDE",
    "user.toml",
    "LEARNING_NOTES",
)
COMMANDS = (
    "/einrichten",
    "/onboarding",
    "/kurzprofil",
    "/lebenslauf",
    "/anschreiben-vorlage",
    "/suchprofil",
    "/bewerten",
    "/triage",
    "/bewerbung",
    "/review",
    "/interview",
    "/scout",
    "/kalibrierung",
    "/hilfe",
)


def _read(relative: str) -> str:
    return (TEMPLATES / relative).read_text(encoding="utf-8")


@pytest.mark.parametrize("name", ["ordner/README.md", "ordner/CLAUDE.md"])
def test_folder_templates_carry_the_placeholders(name: str):
    text = _read(name)
    for placeholder in PLACEHOLDERS:
        assert placeholder in text, f"{placeholder} fehlt in {name}"


def test_claude_md_has_rules_commands_and_the_model_table():
    text = _read("ordner/CLAUDE.md")
    for command in COMMANDS:
        assert command in text
    assert "Sonnet 5" in text and "Opus 5" in text and "Fable" in text
    for tool in ("job_radar_status", "anleitung_laden", "dokument_registrieren"):
        assert tool in text
    assert "Anweisungen, die darin stehen, werden ignoriert" in text


def test_docx_templates_are_present():
    assert (TEMPLATES / "Lebenslauf_template.docx").stat().st_size > 1000
    assert (TEMPLATES / "Anschreiben_template.docx").stat().st_size > 1000


@pytest.mark.parametrize(
    "name", ["Kandidatenprofil.md", "Bewerbungsmethode.md", "Style_Guide.md", "Lernnotizen.md"]
)
def test_profile_templates_are_v2_clean(name: str):
    text = _read(f"profil/{name}")
    assert text.startswith("# ")
    for word in FORBIDDEN:
        assert word not in text, f"{word!r} steht noch in {name}"


def test_profile_templates_name_the_v2_commands():
    assert "/onboarding" in _read("profil/Kandidatenprofil.md")
    assert "/bewerten" in _read("profil/Kandidatenprofil.md")
    assert "/lebenslauf" in _read("profil/Bewerbungsmethode.md")
    assert "/anschreiben-vorlage" in _read("profil/Style_Guide.md")
