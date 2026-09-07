"""DOCX nach PDF: LibreOffice headless, sonst Word über docx2pdf, sonst ehrlich scheitern.

Aufruf: python to_pdf.py <datei.docx> [--outdir <ordner>]
Exit 0 mit PDF, Exit 4 ohne (das DOCX bleibt unangetastet). Letzte Zeile: JOBRADAR_RESULT.
Ein PDF mit demselben Stamm im Zielordner wird überschrieben; die Fassungsnummern vergeben die
Render-Skripte, nicht dieses Skript.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

import _common

TIMEOUT_SECONDS = 120
NO_CONVERTER_HINT = (
    "Kein PDF-Konverter gefunden. Das DOCX in Word öffnen und über „Speichern unter“ als PDF "
    "sichern, oder LibreOffice installieren (libreoffice.org)."
)


def _convert_with_libreoffice(docx: Path, outdir: Path, soffice: Path) -> Path | None:
    """`soffice --headless --convert-to pdf` mit eigenem Profil, damit eine offene LibreOffice-
    Instanz des Nutzers den Aufruf nicht blockiert."""
    with tempfile.TemporaryDirectory(prefix="jobradar-lo-") as profile:
        cmd = [
            str(soffice),
            f"-env:UserInstallation={Path(profile).as_uri()}",
            "--headless",
            "--norestore",
            "--convert-to",
            "pdf",
            "--outdir",
            str(outdir),
            str(docx),
        ]
        try:
            subprocess.run(cmd, capture_output=True, timeout=TIMEOUT_SECONDS, check=False)
        except (OSError, subprocess.TimeoutExpired):
            return None
    pdf = outdir / f"{docx.stem}.pdf"
    return pdf if pdf.is_file() else None


def _convert_with_word(docx: Path, outdir: Path) -> Path | None:
    """docx2pdf steuert Word (Windows und macOS). Nicht in requirements.txt, rein optional."""
    try:
        from docx2pdf import convert
    except ImportError:
        return None
    pdf = outdir / f"{docx.stem}.pdf"
    try:
        convert(str(docx), str(pdf))
    except Exception:  # noqa: BLE001 - Word meldet alles Mögliche, uns interessiert nur das Ergebnis
        return None
    return pdf if pdf.is_file() else None


def to_pdf(docx: Path, outdir: Path | None = None) -> dict:
    """Konvertieren und beschreiben. `pdf` ist der Pfad relativ zum Arbeitsordner oder None.
    Liegt im Zielordner schon ein PDF mit demselben Stamm, wird es überschrieben; die
    Fassungsnummern vergeben die Render-Skripte."""
    docx = docx.resolve()
    target = (outdir or docx.parent).resolve()
    target.mkdir(parents=True, exist_ok=True)
    pdf: Path | None = None
    method: str | None = None
    soffice = _common.find_soffice()
    if soffice is not None:
        pdf = _convert_with_libreoffice(docx, target, soffice)
        method = "libreoffice" if pdf else None
    if pdf is None:
        pdf = _convert_with_word(docx, target)
        method = "word" if pdf else None
    return {
        "docx": _common.relative_posix(docx),
        "pdf": _common.relative_posix(pdf) if pdf else None,
        "methode": method,
        "seiten": _common.count_pdf_pages(pdf) if pdf else None,
        "hinweis": None if pdf else NO_CONVERTER_HINT,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="DOCX nach PDF")
    parser.add_argument("docx", type=Path)
    parser.add_argument("--outdir", type=Path, default=None)
    args = parser.parse_args(argv)
    if not args.docx.is_file():
        print(f"FEHLER: Datei nicht gefunden: {args.docx}")
        return 1
    result = to_pdf(args.docx, args.outdir)
    if result["pdf"]:
        print(f"OK PDF erzeugt über {result['methode']}: {result['pdf']}")
    else:
        print(f"WARN {result['hinweis']}")
    _common.print_result(result)
    return 0 if result["pdf"] else 4


if __name__ == "__main__":
    sys.exit(main())
