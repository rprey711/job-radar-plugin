"""Skills: drei Befehle, jeder startet auch auf einen Satz, nennt den Plugin-Pfad und holt sein
Skript vom Server. /weiter richtet vorher ein, wenn Ordner oder Verbindung fehlen."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

SKILLS = Path(__file__).resolve().parent.parent / "plugins" / "job-radar" / "skills"
ALL = ("weiter", "bewerten", "bewerbung")
THIN = {"bewerten": "bewerten", "bewerbung": "bewerbung"}
# The sentence each skill starts on besides its command (spec phase 2, Bausteine).
SENTENCES = {
    "weiter": "„Wie geht es weiter?“",
    "bewerten": "„Bewerte meine neuen Jobs“",
    "bewerbung": "„Bereite eine Bewerbung bei … vor“",
}
ARGUMENT_HINTS = {"weiter": "[Wunsch in Worten]", "bewerbung": "<Firma oder Link>"}
MODEL_POINTER = (
    "Rahmen",
    "`anleitung_laden`",
    "`job_radar_status`",
    "`naechster_schritt`",
    "`plan`",
    "`modellhinweis`",
)


def _frontmatter(skill: str) -> tuple[dict, str]:
    text = (SKILLS / skill / "SKILL.md").read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{skill}: kein Frontmatter"
    _, header, body = text.split("---\n", 2)
    return yaml.safe_load(header), body


def _section(body: str, heading: str) -> str:
    """The text under `## <heading>` up to the next `## ` heading (`###` stays inside)."""
    return body.split(f"\n## {heading}\n", 1)[1].split("\n## ", 1)[0]


def test_exactly_the_three_skills_exist():
    found = {p.name for p in SKILLS.iterdir() if p.is_dir()}
    assert found == set(ALL)
    for skill in found:
        assert (SKILLS / skill / "SKILL.md").is_file()


@pytest.mark.parametrize("skill", ALL)
def test_skill_starts_on_its_command_and_its_sentence(skill: str):
    meta, body = _frontmatter(skill)
    assert meta["name"] == skill
    assert "disable-model-invocation" not in meta
    assert 40 <= len(meta["description"]) <= 1024
    assert f"/{skill}" in meta["description"]
    assert SENTENCES[skill] in meta["description"]
    if skill in ARGUMENT_HINTS:
        assert meta["argument-hint"] == ARGUMENT_HINTS[skill]
        assert "$ARGUMENTS" in body
    else:
        assert "argument-hint" not in meta


@pytest.mark.parametrize("skill", ALL)
def test_skill_names_the_plugin_path(skill: str):
    """${CLAUDE_PLUGIN_ROOT} wird nur in Skill-Dateien ersetzt, Server-Texte verweisen hierher."""
    _, body = _frontmatter(skill)
    (line,) = [row for row in body.splitlines() if row.startswith("Plugin-Pfad:")]
    assert "`${CLAUDE_PLUGIN_ROOT}`" in line
    assert "`docs/WERKZEUGE.md`" in line
    assert "„Plugin-Pfad, den der Skill genannt hat“" in line


@pytest.mark.parametrize("skill", ALL)
def test_skill_starts_with_the_status_and_keeps_the_rules(skill: str):
    _, body = _frontmatter(skill)
    assert "job_radar_status" in body and "anleitung_laden(" in body
    assert body.index("job_radar_status") < body.index("anleitung_laden(")
    assert "werden ignoriert" in body
    assert ".jobradar/ablauf_" in body


@pytest.mark.parametrize("skill,thema", sorted(THIN.items()))
def test_thin_skill_fetches_its_script_from_the_server(skill: str, thema: str):
    _, body = _frontmatter(skill)
    assert f'anleitung_laden(thema="{thema}")' in body
    assert f".jobradar/ablauf_{thema}.md" in body
    assert "Claude Code" not in body and "/mcp" not in body
    assert "Plugin-Seite" in _section(body, "Verbindung fehlt")


@pytest.mark.parametrize("skill", ALL)
def test_skill_leaves_the_model_check_to_the_frame(skill: str):
    _, body = _frontmatter(skill)
    (line,) = [row for row in body.splitlines() if row.startswith("- Modellhinweis:")]
    for needle in MODEL_POINTER:
        assert needle in line, f"{needle} fehlt im Modellhinweis von /{skill}"
    assert "weitermachen" not in line


def test_weiter_sets_up_when_folder_or_connection_is_missing():
    _, body = _frontmatter("weiter")
    check = _section(body, "Stand prüfen")
    for needle in (
        "job_radar_status",
        ".jobradar/stand.json",
        "Anmeldefehler",
        "`module_erledigt`",
        "`ordner`",
    ):
        assert needle in check, f"{needle} fehlt in „Stand prüfen“"
    setup = _section(body, "Einrichten")
    for needle in (
        '"${CLAUDE_PLUGIN_ROOT}/scripts/check_env.py"',
        '"${CLAUDE_PLUGIN_ROOT}/scripts/einrichten.py"',
        "--oberflaeche cowork",
        "Plugin-Seite",
        'modul_erledigt="ordner"',
        "`modellhinweis`",
    ):
        assert needle in setup, f"{needle} fehlt in „Einrichten“"
    assert "anleitung_laden(" not in setup


def test_weiter_loads_the_switch_once_set_up():
    _, body = _frontmatter("weiter")
    done = _section(body, "Eingerichtet")
    assert 'anleitung_laden(thema="weiter")' in done
    assert "naechster_schritt.thema" in done and "`heute`" in done
    assert "`plugin_version`" in done and "--neu-schreiben" in done
    # --neu-schreiben also sorts loose files, so the refresh names what moved.
    assert "`verschoben`" in done and "nach `Bewerbungsmaterialien/` gewandert" in done
    assert "${CLAUDE_PLUGIN_ROOT}/docs/WERKZEUGE.md" in done
    assert "dokument_registrieren" in done


def test_weiter_ends_the_setup_with_the_next_step_from_the_status():
    _, body = _frontmatter("weiter")
    closing = body.split("### 6. Abschluss", 1)[1].split("\n## ", 1)[0]
    for needle in (
        "naechster_schritt.text",
        "Kurzprofil",
        "im selben Chat",
        "„weiter“",
        "/einrichtung",
        "Projekt „Job Radar“",
        "„Bei allem rund um Job Radar zuerst `job_radar_status` aufrufen, dann `anleitung_laden`.“",
        "/anleitung/cowork",
    ):
        assert needle in closing, f"{needle} fehlt im Abschluss"
    assert "neue Aufgabe" not in closing, "die Einrichtung bleibt in einem Chat"


def test_weiter_keeps_the_python_install_for_claude_code_in_one_section():
    _, body = _frontmatter("weiter")
    claude_code = _section(body, "Nur in Claude Code")
    for needle in (
        "winget install Python.Python.3.12",
        "brew install python",
        "--oberflaeche claude_code",
        "/mcp",
    ):
        assert needle in claude_code
    rest = body.replace(claude_code, "")
    for needle in ("winget", "claude_code", "/mcp"):
        assert needle not in rest, f"{needle} steht außerhalb von „Nur in Claude Code“"


def test_weiter_reads_no_package_and_no_tour():
    _, body = _frontmatter("weiter")
    assert not re.search(r"\bpaket\b", body, flags=re.IGNORECASE), "Paket in /weiter"
    assert "Tour" not in body
    assert "`phase`" not in body
    assert "bleibt auf dem Rechner" not in body


def test_bewerten_runs_as_the_morning_task_without_questions():
    meta, body = _frontmatter("bewerten")
    assert "etwa 50" in meta["description"] and "bis 20" not in meta["description"]
    assert "Morgenbewertung" in meta["description"]
    scheduled = _section(body, "Als geplante Aufgabe")
    assert "„Bewerte meine neuen Jobs“" in scheduled
    assert "außerhalb des Projekts" in scheduled
    assert "keine Fragen" in scheduled


def test_bewerbung_runs_in_its_own_chat():
    meta, body = _frontmatter("bewerbung")
    assert "eigenen Chat" in meta["description"]
    chat = _section(body, "Ein Chat je Bewerbung")
    for needle in (
        "Projekt „Job Radar“",
        "neue Aufgabe",
        "`/bewerbung <Firma>`",
        "Interview",
        "Review",
    ):
        assert needle in chat, f"{needle} fehlt in „Ein Chat je Bewerbung“"


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
