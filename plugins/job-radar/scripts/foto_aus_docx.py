"""foto_aus_docx.py: das größte Bild aus einem Word-Lebenslauf als Bewerbungsfoto ablegen.

Aufruf:
    python foto_aus_docx.py <lebenslauf.docx> [--ziel Bewerbungsmaterialien]

Schreibt <ziel>/Bewerbungsfoto.<endung> und als letzte Zeile JOBRADAR_RESULT
{"foto": <Pfad relativ zum Arbeitsordner> oder null, "hinweis": ...}.
Exit 0 mit Foto, 1 ohne (kein Bild, keine Word-Datei, nicht lesbar, Datei fehlt).
Braucht kein Zusatzpaket.
"""

from __future__ import annotations

import argparse
import sys
import zipfile
import zlib
from pathlib import Path

import _common

BILDENDUNGEN = {".png", ".jpg", ".jpeg"}


def groesstes_bild(docx: Path) -> tuple[str, bytes] | None:
    """Endung und Inhalt des größten PNG oder JPEG unter word/media, sonst None."""
    with zipfile.ZipFile(docx) as z:
        kandidaten = [
            info
            for info in z.infolist()
            if info.filename.startswith("word/media/")
            and Path(info.filename).suffix.lower() in BILDENDUNGEN
        ]
        if not kandidaten:
            return None
        best = max(kandidaten, key=lambda info: info.file_size)
        endung = Path(best.filename).suffix.lower().replace(".jpeg", ".jpg")
        return endung, z.read(best.filename)


def main(argv: list[str] | None = None) -> int:
    """Foto aus der Word-Datei lösen, ablegen und die Ergebniszeile schreiben."""
    parser = argparse.ArgumentParser(description="Bewerbungsfoto aus einem Word-Lebenslauf lösen")
    parser.add_argument("datei", type=Path)
    parser.add_argument("--ziel", type=Path, default=Path("Bewerbungsmaterialien"))
    args = parser.parse_args(argv)

    def fertig(foto: Path | None, hinweis: str | None) -> int:
        if hinweis:
            print(hinweis)
        _common.print_result(
            {"foto": _common.relative_posix(foto) if foto else None, "hinweis": hinweis}
        )
        return 0 if foto else 1

    if not args.datei.is_file():
        return fertig(None, f"Datei nicht gefunden: {args.datei}")
    try:
        bild = groesstes_bild(args.datei)
    except zipfile.BadZipFile:
        return fertig(None, f"{args.datei.name} ist keine Word-Datei (.docx).")
    except (zlib.error, OSError) as exc:
        return fertig(None, f"{args.datei.name} ist nicht lesbar: {exc}")
    if bild is None:
        return fertig(None, "Kein Bild im Dokument gefunden.")
    endung, inhalt = bild
    try:
        args.ziel.mkdir(parents=True, exist_ok=True)
        ziel = args.ziel / f"Bewerbungsfoto{endung}"
        ziel.write_bytes(inhalt)
    except OSError as exc:
        return fertig(None, f"Foto nicht speicherbar: {exc}")
    print(f"OK Foto: {ziel}")
    return fertig(ziel, None)


if __name__ == "__main__":
    sys.exit(main())
