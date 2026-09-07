"""Prüft, ob die Render-Skripte laufen können: Python, Pakete, LibreOffice, Word.

Aufruf: python check_env.py
Exit 0, wenn Python neu genug ist und alle Pakete da sind; sonst 1 mit dem pip-Befehl.
LibreOffice und Word entscheiden nur über den PDF-Schritt und werden gemeldet, nicht verlangt.
"""

from __future__ import annotations

import importlib.util
import platform
import sys

import _common

MIN_PYTHON = (3, 10)
PACKAGES = {"python-docx": "docx", "docxtpl": "docxtpl", "pyyaml": "yaml"}


def _has(module: str) -> bool:
    try:
        return importlib.util.find_spec(module) is not None
    except (ImportError, ValueError):
        return False


def report() -> dict:
    """Alles, was `/einrichten` wissen will, als ein Dict."""
    version = ".".join(str(part) for part in sys.version_info[:3])
    python_ok = sys.version_info[:2] >= MIN_PYTHON
    packages = {name: _has(module) for name, module in PACKAGES.items()}
    soffice = _common.find_soffice()
    word = _has("docx2pdf")
    ok = python_ok and all(packages.values())
    hinweis = None
    if not python_ok:
        hinweis = (
            f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]} oder neuer wird gebraucht, gefunden {version}."
        )
    elif not ok:
        requirements = _common.PLUGIN_ROOT / "requirements.txt"
        hinweis = (
            f'Fehlende Pakete installieren: {sys.executable} -m pip install -r "{requirements}"'
        )
    return {
        "ok": ok,
        "python": {"version": version, "pfad": sys.executable, "ok": python_ok},
        "pakete": packages,
        "libreoffice": str(soffice) if soffice else None,
        "word": word,
        "pdf_moeglich": bool(soffice) or word,
        "system": platform.system(),
        "plugin_version": _common.plugin_version(),
        "plugin_root": str(_common.PLUGIN_ROOT),
        "hinweis": hinweis,
    }


def _print_summary(data: dict) -> None:
    mark = {True: "ok", False: "fehlt"}
    print(
        f"Python {data['python']['version']} ({data['python']['pfad']}): "
        f"{'ok' if data['python']['ok'] else 'zu alt'}"
    )
    for name, present in data["pakete"].items():
        print(f"Paket {name}: {mark[present]}")
    print(f"LibreOffice: {data['libreoffice'] or 'nicht gefunden'}")
    print(f"Word (docx2pdf): {mark[data['word']]}")
    pdf_status = "ja" if data["pdf_moeglich"] else "nein, DOCX in Word als PDF speichern"
    print(f"PDF möglich: {pdf_status}")
    print(f"Plugin {data['plugin_version']} unter {data['plugin_root']}")
    if data["hinweis"]:
        print(data["hinweis"])


def main() -> int:
    data = report()
    _print_summary(data)
    _common.print_result(data)
    return 0 if data["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
