"""Prüft, ob die Render-Skripte laufen können: Python, Pakete, LibreOffice, Word.

Aufruf: python check_env.py
Exit 0, wenn Python neu genug ist und alle Pakete da sind; sonst 1 mit dem pip-Befehl.
LibreOffice und Word entscheiden nur über den PDF-Schritt und werden gemeldet, nicht verlangt.
"""

from __future__ import annotations

import importlib.util
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

import _common

MIN_PYTHON = (3, 10)
PACKAGES = {"python-docx": "docx", "docxtpl": "docxtpl", "pyyaml": "yaml"}
CALIBRI_NAMEN = ("calibri", "carlito")


def _has(module: str) -> bool:
    try:
        return importlib.util.find_spec(module) is not None
    except (ImportError, ValueError):
        return False


def _fc_list() -> str:
    """Ausgabe von `fc-list`, alle Familiennamen, eine pro Zeile."""
    return subprocess.run(
        ["fc-list", ":", "family"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",  # Schriftnamen in fremder Kodierung sollen die Prüfung nicht beenden
        timeout=20,
        check=False,
    ).stdout


def calibri_verfuegbar() -> bool | None:
    """True, wenn Calibri oder die metrikgleiche Carlito da ist; None, wenn nicht prüfbar."""
    if platform.system() == "Windows":
        ordner = [Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"]
        # Schriften, die jemand ohne Adminrechte nur für sich installiert hat
        if os.environ.get("LOCALAPPDATA"):
            ordner.append(Path(os.environ["LOCALAPPDATA"]) / "Microsoft" / "Windows" / "Fonts")
        soffice = _common.find_soffice()
        if soffice:
            ordner.append(Path(soffice).parent.parent / "share" / "fonts" / "truetype")
        namen = [p.name.lower() for d in ordner if d.is_dir() for p in d.iterdir()]
        return any(n.startswith(CALIBRI_NAMEN) for n in namen)
    if shutil.which("fc-list") is None:
        return None
    return any(name in _fc_list().lower() for name in CALIBRI_NAMEN)


def report() -> dict:
    """Alles, was das Einrichten in `/weiter` wissen will, als ein Dict."""
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
            f'Fehlende Pakete installieren: "{sys.executable}" -m pip install -r "{requirements}"'
        )
    try:
        schrift = calibri_verfuegbar()
    except Exception:  # noqa: BLE001 - die Schriftprüfung ist nur ein Hinweis, der Bericht zählt
        schrift = None
    schrift_hinweis = None
    if schrift is False:
        schrift_hinweis = (
            "Weder Calibri noch Carlito gefunden. Das PDF entsteht dann mit einer Ersatzschrift, "
            "Umbrüche können sich verschieben."
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
        "schrift_calibri": schrift,
        "schrift_hinweis": schrift_hinweis,
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
    schrift = data["schrift_calibri"]
    schrift_status = "ok" if schrift else ("nicht prüfbar" if schrift is None else "fehlt")
    print(f"Schrift Calibri oder Carlito: {schrift_status}")
    if data["schrift_hinweis"]:
        print(data["schrift_hinweis"])
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
