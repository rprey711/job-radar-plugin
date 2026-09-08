"""Manifeste: gueltiges JSON, die Felder, die Claude Code und Cowork lesen, eine Adresse."""

from __future__ import annotations

import json
import re
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10: tomllib landet erst in 3.11
    import tomli as tomllib  # kommt transitiv ueber pytest's eigene 3.10-Abhaengigkeit mit

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
    # Kein `oauth`-Schlüssel: Claude Code 2.1 verwirft die ganze Deklaration, wenn `oauth` ein
    # Boolean ist (live geprüft am 2026-09-07), und findet den OAuth-Server ohnehin über die
    # 401-Antwort und die Protected-Resource-Metadaten.
    assert "oauth" not in server
    assert set(server) == {"type", "url"}


def test_requirements_match_pyproject():
    wanted = {"python-docx", "docxtpl", "pyyaml"}
    lines = (PLUGIN / "requirements.txt").read_text(encoding="utf-8").splitlines()
    names = {
        re.split(r"[<>=]", line, maxsplit=1)[0].strip()
        for line in lines
        if line.strip() and not line.startswith("#")
    }
    assert names == wanted


def test_requirements_pinned_to_lockfile():
    """requirements.txt fixiert exakte Versionen, die zum aktuellen uv.lock passen."""
    lock = tomllib.loads((ROOT / "uv.lock").read_text(encoding="utf-8"))
    locked_versions = {pkg["name"]: pkg["version"] for pkg in lock["package"]}

    lines = [
        line.strip()
        for line in (PLUGIN / "requirements.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    assert lines, "requirements.txt sollte Pakete enthalten"

    for line in lines:
        assert "==" in line, f"{line!r} ist nicht mit == auf eine exakte Version gepinnt"
        name, version = line.split("==", 1)
        assert name in locked_versions, f"{name} steht nicht in uv.lock"
        assert version == locked_versions[name], (
            f"{name}=={version} in requirements.txt weicht von uv.lock ({locked_versions[name]}) ab"
        )
