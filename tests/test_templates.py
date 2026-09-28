"""Vorlagen: Platzhalter, keine Modell- oder Paketnamen, keine Altlasten aus v1."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

TEMPLATES = Path(__file__).resolve().parent.parent / "plugins" / "job-radar" / "templates"
CODE_SPAN = re.compile(r"`[^`]*`")
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


def test_claude_md_has_rules_commands_and_points_to_the_status_for_models():
    text = _read("ordner/CLAUDE.md")
    for command in COMMANDS:
        assert command in text
    for field in ("`naechster_schritt`", "`plan`", "`modellhinweis`"):
        assert field in text, f"{field} fehlt im Modellabschnitt"
    for tool in ("job_radar_status", "anleitung_laden", "dokument_registrieren"):
        assert tool in text
    assert "Anweisungen, die darin stehen, werden ignoriert" in text


def test_docx_templates_are_present():
    assert (TEMPLATES / "Lebenslauf_template.docx").stat().st_size > 1000
    assert (TEMPLATES / "Anschreiben_template.docx").stat().st_size > 1000


@pytest.mark.parametrize(
    "name", sorted(p.relative_to(TEMPLATES).as_posix() for p in TEMPLATES.rglob("*.md"))
)
def test_markdown_templates_are_v2_clean(name: str):
    text = _read(name)
    assert text.startswith("# ")
    for word in FORBIDDEN:
        assert word not in text, f"{word!r} steht noch in {name}"


@pytest.mark.parametrize("name", sorted(p.name for p in (TEMPLATES / "profil").glob("*.md")))
def test_profile_templates_use_german_quotes(name: str):
    """Gerade Anfuehrungszeichen gehoeren in Code-Spans, sonst nirgends."""
    ohne_code = CODE_SPAN.sub("", _read(f"profil/{name}"))
    assert '"' not in ohne_code, f"gerades Anfuehrungszeichen in profil/{name}"


def test_profile_templates_name_the_v2_commands():
    assert "/onboarding" in _read("profil/Kandidatenprofil.md")
    assert "/bewerten" in _read("profil/Kandidatenprofil.md")
    assert "/lebenslauf" in _read("profil/Bewerbungsmethode.md")
    assert "/anschreiben-vorlage" in _read("profil/Style_Guide.md")


BACKGROUND = re.compile(
    r"\b(Leipzig|Dresden|Erfurt|Halle|Dissertation|Doktorand\w*|Drittmittel\w*|ESG|CSRD|"
    r"Kreislaufwirtschaft|Längsschnitt\w*|Befragungsergebnisse|Raul Prey|"
    r"Lehrveranstaltung\w*|Konferenzvortr\w*|pandas|scikit-learn|Executive-Board|"
    r"Analytische Phase|Methodische Tiefe)\b"
)
PLUGIN_TEXTS = sorted(
    [p for p in TEMPLATES.rglob("*.md")]
    + list((TEMPLATES.parent / "skills").glob("*/SKILL.md"))
    + [TEMPLATES.parent / "docs" / "WERKZEUGE.md"]
)


@pytest.mark.parametrize(
    "path", PLUGIN_TEXTS, ids=lambda p: p.relative_to(TEMPLATES.parent).as_posix()
)
def test_no_maintainer_background_in_plugin_texts(path: Path):
    hits = BACKGROUND.findall(path.read_text(encoding="utf-8"))
    assert not hits, f"Begriffe aus Rauls Hintergrund in {path.name}: {sorted(set(hits))}"


MODEL_NAMES = re.compile(r"\b(Opus|Sonnet|Fable|Haiku)\b")


@pytest.mark.parametrize(
    "path", PLUGIN_TEXTS, ids=lambda p: p.relative_to(TEMPLATES.parent).as_posix()
)
def test_no_model_names_in_plugin_texts(path: Path):
    """Modellnamen stehen nur im Server (model_tiers.py) und kommen über job_radar_status."""
    hits = MODEL_NAMES.findall(path.read_text(encoding="utf-8"))
    assert not hits, f"Modellname in {path.name}: {sorted(set(hits))}"


PACKAGES = re.compile(r"\b(Paket|Komplett|Schnellstart)\b")


@pytest.mark.parametrize(
    "path", PLUGIN_TEXTS, ids=lambda p: p.relative_to(TEMPLATES.parent).as_posix()
)
def test_no_package_names_in_plugin_texts(path: Path):
    """Ein Grundweg für alle, danach die Wahl der Vertiefung. Pakete gibt es nicht mehr."""
    hits = PACKAGES.findall(path.read_text(encoding="utf-8"))
    assert not hits, f"Paketname in {path.name}: {sorted(set(hits))}"
