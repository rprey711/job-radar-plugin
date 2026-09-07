"""Manifeste: gueltiges JSON, die Felder, die Claude Code und Cowork lesen, eine Adresse."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "job-radar"
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_marketplace_manifest_points_at_the_plugin():
    data = _load(ROOT / ".claude-plugin" / "marketplace.json")
    assert data["name"] == "job-radar"
    assert data["owner"]["name"]
    (entry,) = data["plugins"]
    assert entry["name"] == "job-radar"
    assert entry["source"] == "./plugins/job-radar"
    assert SEMVER.match(entry["version"])


def test_plugin_manifest():
    data = _load(PLUGIN / ".claude-plugin" / "plugin.json")
    assert data["name"] == "job-radar"
    assert SEMVER.match(data["version"])
    assert "description" in data and data["description"]
    market = _load(ROOT / ".claude-plugin" / "marketplace.json")
    assert market["plugins"][0]["version"] == data["version"]


def test_mcp_declaration_names_the_live_connector():
    data = _load(PLUGIN / ".mcp.json")
    server = data["mcpServers"]["jobradar"]
    assert server["type"] == "http"
    assert server["url"] == "https://jobs.162-55-50-225.nip.io/mcp"
    assert server["oauth"] is True
    assert set(server) == {"type", "url", "oauth"}


def test_requirements_match_pyproject():
    wanted = {"python-docx", "docxtpl", "pyyaml"}
    lines = (PLUGIN / "requirements.txt").read_text(encoding="utf-8").splitlines()
    names = {
        line.split(">=")[0].strip() for line in lines if line.strip() and not line.startswith("#")
    }
    assert names == wanted
