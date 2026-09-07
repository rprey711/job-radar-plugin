"""Gemeinsame Helfer der Render-Skripte. Nur Standardbibliothek, Python 3.10.

Die Skripte werden als Dateien aufgerufen (`python <plugin>/scripts/x.py`); Python setzt dabei
das Skriptverzeichnis an den Anfang von sys.path, deshalb reicht `import _common`.
"""

from __future__ import annotations

import glob
import json
import os
import re
import shutil
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
RESULT_PREFIX = "JOBRADAR_RESULT "

_ILLEGAL = re.compile(r'[/\\:*?"<>|]')
_PAGE_OBJECT = re.compile(rb"/Type\s*/Page\b")

KNOWN_SOFFICE = [
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    "/usr/bin/soffice",
    "/usr/bin/libreoffice",
    "/usr/lib/libreoffice/program/soffice",
    "/opt/libreoffice*/program/soffice",
    "/snap/bin/libreoffice",
]


def sanitize_filename(name: str) -> str:
    """Personen- und Firmennamen dateisystemsicher machen (Windows und POSIX).

    Ersetzt die unter Windows verbotenen Zeichen und Leerzeichen durch Unterstriche und
    entfernt Klammern. Umlaute und andere Unicode-Buchstaben bleiben.
    """
    cleaned = _ILLEGAL.sub("_", name).replace(" ", "_")
    return cleaned.replace("(", "").replace(")", "")


def next_version(directory: Path, stem: str) -> int:
    """Nächste freie Fassungsnummer für Dateien `<stem>_v<N>.<ext>` im Ordner."""
    pattern = re.compile(re.escape(stem) + r"_v(\d+)\.")
    highest = 0
    if directory.is_dir():
        for entry in directory.iterdir():
            match = pattern.match(entry.name)
            if match:
                highest = max(highest, int(match.group(1)))
    return highest + 1


def relative_posix(path: Path, root: Path | None = None) -> str:
    """Pfad relativ zum Arbeitsordner mit Schrägstrichen, so wie `dokument_registrieren` ihn
    erwartet. Liegt die Datei außerhalb, kommt der absolute Pfad zurück."""
    base = (root or Path.cwd()).resolve()
    resolved = path.resolve()
    try:
        return resolved.relative_to(base).as_posix()
    except ValueError:
        return resolved.as_posix()


def print_result(data: dict) -> None:
    """Die Ergebniszeile, die Claude liest: Präfix plus ein JSON-Objekt, als letzte Zeile."""
    sys.stdout.flush()
    print(RESULT_PREFIX + json.dumps(data, ensure_ascii=False))
    sys.stdout.flush()


def plugin_version() -> str:
    manifest = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
    try:
        return str(json.loads(manifest.read_text(encoding="utf-8"))["version"])
    except (OSError, ValueError, KeyError):
        return "unbekannt"


def dashboard_url() -> str:
    """Die Dashboard-Adresse aus `.mcp.json`, ohne `/mcp`. Eine Quelle für beide."""
    declaration = PLUGIN_ROOT / ".mcp.json"
    try:
        url = json.loads(declaration.read_text(encoding="utf-8"))["mcpServers"]["jobradar"]["url"]
    except (OSError, ValueError, KeyError):
        return ""
    return url[: -len("/mcp")] if url.endswith("/mcp") else url


def find_soffice() -> Path | None:
    """LibreOffice: Umgebungsvariable, PATH, dann die üblichen Installationsorte. Zeigt
    `JOBRADAR_SOFFICE` ins Leere, gibt es absichtlich None statt auf die Suche zurückzufallen,
    damit ein falsch gesetzter Pfad auffällt."""
    override = os.environ.get("JOBRADAR_SOFFICE")
    if override:
        candidate = Path(override)
        return candidate if candidate.is_file() else None
    for name in ("soffice", "libreoffice"):
        found = shutil.which(name)
        if found:
            return Path(found)
    for pattern in KNOWN_SOFFICE:
        for hit in glob.glob(pattern):
            if Path(hit).is_file():
                return Path(hit)
    return None


def count_pdf_pages(pdf: Path) -> int | None:
    """Seiten eines PDFs über die Page-Objekte zählen. None, wenn keine gefunden werden
    (etwa bei komprimierten Objektströmen); dann entscheidet der Aufrufer anders."""
    try:
        data = pdf.read_bytes()
    except OSError:
        return None
    count = len(_PAGE_OBJECT.findall(data))
    return count or None


def ensure_utf8_stdout() -> None:
    """Die Ausgabe auf UTF-8 stellen, einmal beim Import dieses Moduls.

    Windows-Konsolen laufen ohne gesetzte Codepage unter cp1252 (`chcp`); print() mit Umlauten
    schlägt dann fehl oder erzeugt Bytes, die ein UTF-8-Leser (etwa subprocess mit
    encoding="utf-8") nicht decodieren kann. Streams ohne reconfigure (pytest-Capture) bleiben
    unberührt.
    """
    if not hasattr(sys.stdout, "reconfigure"):
        return
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")


ensure_utf8_stdout()
