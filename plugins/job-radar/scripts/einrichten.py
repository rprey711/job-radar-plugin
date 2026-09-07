"""Richtet den Job-Radar-Ordner ein: Struktur, README, CLAUDE.md, Profilvorlagen, Sortieren.

Aufruf: python einrichten.py --name "<Vor- und Nachname>" [--ordner <pfad>]
                             [--oberflaeche cowork|claude_code|unbekannt] [--neu-schreiben]

Idempotent: was da ist, bleibt. README und CLAUDE.md werden nur mit --neu-schreiben ersetzt.
Lose Dateien im Ordner (Lebenslauf, alte Anschreiben, Zeugnisse, Fotos) wandern nach
Bewerbungsmaterialien/. Exit 0 ok, 1 harter Fehler. Letzte Zeile: JOBRADAR_RESULT.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import date
from pathlib import Path

import _common

FOLDERS = ["Profil", "Bewerbungsmaterialien", "Bewerbungen", ".jobradar"]
PROFILE_FILES = ["Kandidatenprofil.md", "Bewerbungsmethode.md", "Style_Guide.md", "Lernnotizen.md"]
LOOSE_SUFFIXES = {".pdf", ".docx", ".doc", ".odt", ".rtf", ".txt", ".md", ".jpg", ".jpeg", ".png"}
KEEP_AT_ROOT = {"README.md", "CLAUDE.md"}
SURFACES = ("cowork", "claude_code", "unbekannt")
STAND = ".jobradar/stand.json"


def _fill(template: Path, name: str) -> str:
    text = template.read_text(encoding="utf-8")
    replacements = {
        "{{NAME}}": name,
        "{{DATUM}}": date.today().strftime("%d.%m.%Y"),
        "{{PLUGIN_VERSION}}": _common.plugin_version(),
        "{{DASHBOARD}}": _common.dashboard_url(),
    }
    for key, value in replacements.items():
        text = text.replace(key, value)
    return text


def _free_target(directory: Path, filename: str) -> Path:
    """`name.ext`, sonst `name_1.ext`, `name_2.ext`, bis der Name frei ist."""
    target = directory / filename
    stem, suffix = Path(filename).stem, Path(filename).suffix
    counter = 1
    while target.exists():
        target = directory / f"{stem}_{counter}{suffix}"
        counter += 1
    return target


def _move_loose_files(folder: Path) -> list[str]:
    materials = folder / "Bewerbungsmaterialien"
    moved: list[str] = []
    for entry in sorted(folder.iterdir()):
        if not entry.is_file() or entry.name.startswith(".") or entry.name in KEEP_AT_ROOT:
            continue
        if entry.suffix.lower() not in LOOSE_SUFFIXES:
            continue
        shutil.move(str(entry), str(_free_target(materials, entry.name)))
        moved.append(entry.name)
    return moved


def _write_stand(folder: Path, name: str, surface: str | None) -> dict:
    path = folder / STAND
    stand: dict = {}
    if path.is_file():
        try:
            stand = json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            stand = {}
    stand["name"] = name
    stand.setdefault("eingerichtet_am", date.today().isoformat())
    if surface is not None:
        stand["oberflaeche"] = surface
    stand.setdefault("oberflaeche", "unbekannt")
    stand["plugin_version"] = _common.plugin_version()
    path.write_text(json.dumps(stand, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return stand


def setup(folder: Path, name: str, surface: str | None = None, rewrite: bool = False) -> dict:
    """Alles anlegen, was fehlt, und berichten, was passiert ist."""
    folder = folder.resolve()
    created: list[str] = []
    existing: list[str] = []
    for sub in FOLDERS:
        path = folder / sub
        if path.is_dir():
            existing.append(sub + "/")
        else:
            path.mkdir(parents=True)
            created.append(sub + "/")

    templates = _common.PLUGIN_ROOT / "templates"
    for filename in ("README.md", "CLAUDE.md"):
        target = folder / filename
        if target.is_file() and not rewrite:
            existing.append(filename)
            continue
        target.write_text(_fill(templates / "ordner" / filename, name), encoding="utf-8")
        created.append(filename)
    for filename in PROFILE_FILES:
        target = folder / "Profil" / filename
        relative = f"Profil/{filename}"
        if target.is_file():
            existing.append(relative)
            continue
        shutil.copyfile(templates / "profil" / filename, target)
        created.append(relative)

    moved = _move_loose_files(folder)
    stand = _write_stand(folder, name, surface)
    return {
        "ordner": folder.as_posix(),
        "name": name,
        "angelegt": created,
        "vorhanden": existing,
        "verschoben": moved,
        "stand": stand,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Job-Radar-Ordner einrichten")
    parser.add_argument(
        "--name", required=True, help="Vor- und Nachname, wie er im Lebenslauf steht"
    )
    parser.add_argument(
        "--ordner", type=Path, default=Path.cwd(), help="Zielordner, sonst der Arbeitsordner"
    )
    parser.add_argument("--oberflaeche", choices=SURFACES, default=None)
    parser.add_argument(
        "--neu-schreiben", action="store_true", help="README und CLAUDE.md neu aus den Vorlagen"
    )
    args = parser.parse_args(argv)
    name = " ".join(args.name.split())
    if not name:
        print("FEHLER: --name darf nicht leer sein")
        return 1
    if not args.ordner.is_dir():
        print(f"FEHLER: Ordner nicht gefunden: {args.ordner}")
        return 1
    try:
        result = setup(args.ordner, name, args.oberflaeche, args.neu_schreiben)
    except OSError as exc:
        print(f"FEHLER: {exc}")
        return 1
    for item in result["angelegt"]:
        print(f"angelegt   {item}")
    for item in result["vorhanden"]:
        print(f"vorhanden  {item}")
    for item in result["verschoben"]:
        print(f"verschoben {item} -> Bewerbungsmaterialien/")
    print(f"OK Ordner eingerichtet für {name}: {result['ordner']}")
    _common.print_result(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
