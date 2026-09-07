"""Skills: Frontmatter passt zum Ordnernamen, alle vierzehn Befehle da, jeder holt sein Skript."""

from __future__ import annotations

from pathlib import Path

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
WITH_ARGUMENT = {"bewerbung", "review", "interview"}


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
