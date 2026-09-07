"""cv_master.py: Lebenslauf-Filler des Job-Radar-Plugins.

Aufruf:
    python cv_master.py --data <daten.yml> --name "<Vor- und Nachname>" --output-dir <ordner>
                        [--template <vorlage.docx>] [--version N] [--pdf]

Ausgabe:
    <ordner>/Lebenslauf_<Name>_v<N>.docx      das Dokument
    <ordner>/Lebenslauf_<Name>_v<N>.md        die Markdown-Quelle derselben Fassung
    <ordner>/Lebenslauf_<Name>_v<N>.pdf       mit --pdf, über to_pdf.py
    letzte Zeile: JOBRADAR_RESULT {...}       Pfade relativ zum Arbeitsordner, Fassung, Befunde

Exit-Codes: 0 ok, 1 harter Fehler (nichts erzeugt), 2 Style-Drift (Ausgabe bleibt),
4 PDF nicht erzeugt (DOCX bleibt). Ohne --version nimmt das Skript die nächste freie Nummer.
Exit 2 ohne Ergebniszeile ist ein Aufruffehler von argparse (falsche Argumente).
Die Style-Prüfung vergleicht Schriftart, Größe und Absatzstil der ersten Überschrift
zwischen Vorlage und Ausgabe; bei Drift bleibt die Markdown-Quelle die Wahrheit.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import _common
import to_pdf
import yaml
from docx import Document
from docxtpl import DocxTemplate


@dataclass
class Position:
    datum: str
    rolle: str
    firma: str
    bullets: list[str] = field(default_factory=list)
    subsections: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class Education:
    datum: str
    titel: str
    institution: str
    detail: str = ""


@dataclass
class CVData:
    name: str
    ort: str
    phone: str
    email: str
    positions: list[Position]
    education: list[Education]
    skills_section: str
    sprachen_line: str
    international: list[str] = field(default_factory=list)
    weiteres: list[str] = field(default_factory=list)
    geburtsdatum: str = ""


class StyleDriftError(Exception):
    """Wird geworfen wenn Output-CV in Schriftart/Größe vom Template abweicht."""


def load_data(data_path: Path) -> CVData:
    """Liest YAML, validiert Schema, gibt CVData zurück."""
    raw = yaml.safe_load(data_path.read_text(encoding="utf-8"))

    positions = [
        Position(
            datum=p["datum"],
            rolle=p["rolle"],
            firma=p["firma"],
            bullets=p.get("bullets", []),
            subsections=p.get("subsections", []),
        )
        for p in raw.get("positions", [])
    ]
    education = [
        Education(
            datum=e["datum"],
            titel=e["titel"],
            institution=e["institution"],
            detail=e.get("detail", ""),
        )
        for e in raw.get("education", [])
    ]
    return CVData(
        name=raw["name"],
        ort=raw["ort"],
        phone=raw["phone"],
        email=raw["email"],
        positions=positions,
        education=education,
        skills_section=raw.get("skills_section", ""),
        sprachen_line=raw.get("sprachen_line", ""),
        international=raw.get("international", []),
        weiteres=raw.get("weiteres", []),
        geburtsdatum=raw.get("geburtsdatum", ""),
    )


def format_education_section(education: list[Education]) -> str:
    """Bildungs-Liste zu Multi-Line-String mit Daten + Titel + Institution."""
    lines: list[str] = []
    for edu in education:
        line = f"{edu.datum} | {edu.titel}"
        if edu.institution:
            line += f"\n{edu.institution}"
        if edu.detail:
            line += f"\n{edu.detail}"
        lines.append(line)
    return "\n\n".join(lines)


def format_international_section(international: list[str]) -> str:
    """Internationaler Hintergrund als Bullet-Liste."""
    if not international:
        return ""
    return "\n".join(f"• {entry}" for entry in international)


def format_weiteres_section(weiteres: list[str]) -> str:
    """Weiteres als Bullet-Liste."""
    if not weiteres:
        return ""
    return "\n".join(f"• {entry}" for entry in weiteres)


def render_docx(template_path: Path, data: CVData, output_path: Path) -> None:
    """Rendert das Template mit den Daten, schreibt nach output_path."""
    tpl = DocxTemplate(str(template_path))

    context = {
        "name": data.name,
        "ort": data.ort,
        "phone": data.phone,
        "email": data.email,
        "geburtsdatum": data.geburtsdatum,
        "positions": [
            {
                "datum": p.datum,
                "rolle": p.rolle,
                "firma": p.firma,
                "bullets": p.bullets,
                "subsections": p.subsections,
            }
            for p in data.positions
        ],
        "education_section": format_education_section(data.education),
        "skills_section": data.skills_section,
        "sprachen_line": data.sprachen_line,
        "international_section": format_international_section(data.international),
        "weiteres_section": format_weiteres_section(data.weiteres),
    }
    tpl.render(context)
    tpl.save(str(output_path))


def write_markdown_source(data: CVData, md_path: Path) -> None:
    """Schreibt menschen-lesbare Markdown-Version (für Re-Run-Audit)."""
    lines = [
        f"# Lebenslauf, {data.name}",
        "",
        f"**Kontakt:** {data.ort} | {data.phone} | {data.email}",
    ]
    if data.geburtsdatum:
        lines.append(f"**Geboren:** {data.geburtsdatum}")
    lines.extend(["", "## Berufserfahrung", ""])

    for pos in data.positions:
        lines.append(f"### {pos.datum} | {pos.rolle}")
        lines.append(f"*{pos.firma}*")
        lines.append("")
        if pos.subsections:
            for sub in pos.subsections:
                lines.append(f"#### {sub.get('titel', '')}")
                if sub.get("description"):
                    lines.append(sub["description"])
                lines.append("")
        for bullet in pos.bullets:
            lines.append(f"- {bullet}")
        lines.append("")

    lines.append("## Bildung")
    lines.append("")
    for edu in data.education:
        lines.append(f"- **{edu.datum} | {edu.titel}**, {edu.institution}")
        if edu.detail:
            lines.append(f"  {edu.detail}")
    lines.append("")

    lines.append("## Sprachen")
    lines.append(data.sprachen_line)
    lines.append("")

    lines.append("## Tools & Methoden")
    lines.append(data.skills_section)
    lines.append("")

    if data.international:
        lines.append("## Internationaler Hintergrund")
        for entry in data.international:
            lines.append(f"- {entry}")
        lines.append("")

    if data.weiteres:
        lines.append("## Weiteres")
        for entry in data.weiteres:
            lines.append(f"- {entry}")
        lines.append("")

    md_path.write_text("\n".join(lines), encoding="utf-8")


def sample_run_style(doc, paragraph_index: int) -> dict[str, Any]:
    """Extrahiere Style des ersten Runs eines Paragraphs."""
    paragraphs = doc.paragraphs
    if paragraph_index >= len(paragraphs):
        return {}
    para = paragraphs[paragraph_index]
    if not para.runs:
        return {"style_name": para.style.name if para.style else None}
    run = para.runs[0]
    return {
        "font_name": run.font.name,
        "font_size": run.font.size,
        "bold": run.font.bold,
        "style_name": para.style.name if para.style else None,
    }


def find_first_heading_index(doc) -> int | None:
    """Find Index des ersten Section-Headers (Style 'Heading 1' o.ä.)."""
    heading_styles = (
        "Heading 1",
        "Überschrift 1",
        "Überschrift1",
        "Heading1",
    )
    for i, p in enumerate(doc.paragraphs):
        if p.style and p.style.name in heading_styles:
            return i
        # Fallback: text uppercase starts with known section names
        text = p.text.strip().upper()
        if text in ("BERUFSERFAHRUNG", "BILDUNG", "SPRACHEN", "TOOLS & METHODEN"):
            return i
    return None


def validate_style_preservation(template_path: Path, output_path: Path) -> None:
    """
    Vergleicht Style des ersten Section-Headers (BERUFSERFAHRUNG) zwischen
    Template und Output. Bei Drift: StyleDriftError.

    Wir prüfen Style-Name + font_name + font_size für die Hauptelemente.
    """
    template_doc = Document(str(template_path))
    output_doc = Document(str(output_path))

    drifts: list[str] = []

    # Erstes Section-Header (BERUFSERFAHRUNG)
    template_heading_idx = find_first_heading_index(template_doc)
    output_heading_idx = find_first_heading_index(output_doc)

    if template_heading_idx is not None and output_heading_idx is not None:
        template_heading = sample_run_style(template_doc, template_heading_idx)
        output_heading = sample_run_style(output_doc, output_heading_idx)
        for key in ("font_name", "font_size", "style_name"):
            if template_heading.get(key) != output_heading.get(key):
                drifts.append(
                    f"Section-Header-{key}: template={template_heading.get(key)} "
                    f"output={output_heading.get(key)}"
                )

    if drifts:
        raise StyleDriftError("Style-Drift detected:\n  " + "\n  ".join(drifts))


sanitize_filename = _common.sanitize_filename

DEFAULT_TEMPLATE = _common.PLUGIN_ROOT / "templates" / "Lebenslauf_template.docx"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lebenslauf-Filler")
    parser.add_argument("--data", type=Path, required=True, help="YAML mit den Lebenslauf-Daten")
    parser.add_argument(
        "--name", type=str, required=True, help="Vor- und Nachname für den Dateinamen"
    )
    parser.add_argument("--output-dir", type=Path, required=True, help="Zielordner")
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE, help="DOCX-Vorlage")
    parser.add_argument(
        "--version",
        type=int,
        default=None,
        help=(
            "Fassungsnummer, sonst die nächste freie, "
            "eine vorhandene Datei dieser Nummer wird ersetzt"
        ),
    )
    parser.add_argument("--pdf", action="store_true", help="danach PDF über to_pdf.py erzeugen")
    args = parser.parse_args(argv)

    if not args.template.is_file():
        print(f"FEHLER: Vorlage nicht gefunden: {args.template}")
        return 1
    if not args.data.is_file():
        print(f"FEHLER: Daten nicht gefunden: {args.data}")
        return 1
    if args.version is not None and args.version < 1:
        print("FEHLER: --version muss mindestens 1 sein")
        return 1
    try:
        data = load_data(args.data)
    except (AttributeError, KeyError, TypeError, yaml.YAMLError) as exc:
        print(f"FEHLER: Daten unvollständig oder kein gültiges YAML: {exc}")
        return 1

    out = args.output_dir
    try:
        out.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"FEHLER: Zielordner nicht anlegbar: {out} ({exc})")
        return 1
    stem = f"Lebenslauf_{sanitize_filename(args.name)}"
    version = args.version or _common.next_version(out, stem)
    docx_path = out / f"{stem}_v{version}.docx"
    md_path = out / f"{stem}_v{version}.md"

    print(f"-> Rendere {docx_path.name} ...")
    try:
        render_docx(args.template, data, docx_path)
    except Exception as exc:  # noqa: BLE001 - python-docx meldet Unlesbares auf viele Arten
        print(f"FEHLER: Vorlage nicht lesbar: {args.template} ({exc})")
        return 1
    write_markdown_source(data, md_path)

    drift = False
    try:
        validate_style_preservation(args.template, docx_path)
        print("OK Stil erhalten")
    except StyleDriftError as exc:
        print(f"WARN Style-Drift: {exc}")
        drift = True

    pdf_result = to_pdf.to_pdf(docx_path) if args.pdf else None
    if args.pdf:
        marke = "OK" if pdf_result["pdf"] else "WARN"
        print(f"{marke} PDF: {pdf_result['pdf'] or pdf_result['hinweis']}")

    _common.print_result(
        {
            "art": "lebenslauf",
            "docx": _common.relative_posix(docx_path),
            "markdown": _common.relative_posix(md_path),
            "pdf": pdf_result["pdf"] if pdf_result else None,
            "pdf_methode": pdf_result["methode"] if pdf_result else None,
            "seiten": pdf_result["seiten"] if pdf_result else None,
            "hinweis": pdf_result["hinweis"] if pdf_result else None,
            "dateiname": docx_path.name,
            "version": version,
            "vorlage": args.template.resolve().as_posix(),
            "style_drift": drift,
        }
    )
    if drift:
        return 2
    if args.pdf and not pdf_result["pdf"]:
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
