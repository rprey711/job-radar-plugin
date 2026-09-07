# Werkzeuge des Plugins

Diese Datei liest Claude, bevor ein Skript aufgerufen wird. Alle Skripte liegen unter `${CLAUDE_PLUGIN_ROOT}/scripts/`. Aufruf mit `python` (Windows auch `py`, macOS und Linux `python3`). Jedes Skript schreibt als letzte Zeile `JOBRADAR_RESULT {…}`, ein JSON-Objekt; daraus kommen die Pfade für `dokument_registrieren`. Pfade in der Ergebniszeile sind relativ zum Arbeitsordner und benutzen Schrägstriche.

## Ordnerregeln

- Pro Bewerbung ein Ordner `Bewerbungen/<Firma>/`, Firmenname mit Unterstrichen statt Leerzeichen und ohne `/ \ : * ? " < > |` (so sanitisiert das Skript auch die Dateinamen). Beispiel: `Bewerbungen/Beispiel_GmbH/`.
- Master-Lebenslauf nach `Bewerbungsmaterialien/`, angepasste Lebensläufe und Anschreiben in den Bewerbungsordner, Recherche als `Recherche.md`, Interview-Briefing als `Interview_Briefing.md` dort.
- Frühere Fassungen bleiben liegen. Die Skripte zählen `_v1`, `_v2` selbst hoch; `--version N` erzwingt eine Nummer.
- Die Daten für die Skripte (YAML) als `Lebenslauf_Daten.yml` beziehungsweise `Anschreiben_Daten.yml` in denselben Ordner schreiben; sie sind die Quelle der nächsten Fassung.

## `check_env.py`

```
python "${CLAUDE_PLUGIN_ROOT}/scripts/check_env.py"
```

Exit 0: Python und Pakete in Ordnung. Exit 1: die Ergebniszeile trägt unter `hinweis` den pip-Befehl. `pdf_moeglich` sagt, ob LibreOffice oder Word da ist.

## `einrichten.py`

```
python "${CLAUDE_PLUGIN_ROOT}/scripts/einrichten.py" --name "<Name>" --oberflaeche <cowork|claude_code>
```

Nur aus `/einrichten`. Idempotent. `--neu-schreiben` ersetzt README und CLAUDE.md.

## `cv_master.py`

```
python "${CLAUDE_PLUGIN_ROOT}/scripts/cv_master.py" --data <Lebenslauf_Daten.yml> --name "<Name>" --output-dir <ordner> [--template <vorlage.docx>] [--version N] [--pdf]
```

YAML-Felder: `name`, `ort`, `phone`, `email`, `geburtsdatum` (optional), `positions[]` (je `datum`, `rolle`, `firma`, `bullets[]`, optional `subsections[]` mit `titel` und `description`), `education[]` (je `datum`, `titel`, `institution`, optional `detail`), `skills_section`, `sprachen_line`, `international[]`, `weiteres[]`. Ohne `--template` die Vorlage des Plugins; eine eigene Vorlage kann unter `Profil/Lebenslauf_Vorlage.docx` liegen und wird dann mit `--template` übergeben.

Ausgabe: `Lebenslauf_<Name>_v<N>.docx` und `.md`, mit `--pdf` auch `.pdf`. Ergebniszeile: `docx`, `markdown`, `pdf`, `pdf_methode`, `seiten`, `dateiname`, `version`, `vorlage`, `style_drift`. Exit 0 ok, 1 harter Fehler, 2 Style-Drift (Datei bleibt, Markdown ist die Wahrheit, Freund informieren), 4 PDF nicht erzeugt (DOCX bleibt, Hinweis weitergeben).

## `cover_master.py`

```
python "${CLAUDE_PLUGIN_ROOT}/scripts/cover_master.py" --data <Anschreiben_Daten.yml> --name "<Name>" --firma "<Firma>" --output-dir <ordner> [--template <vorlage.docx>] [--version N] [--max-words 400] [--pdf]
```

YAML-Felder: `empfaenger` (mehrzeilig), `betreff`, `anrede`, `body[]` (ein Eintrag pro Absatz, ohne Anrede und Gruß), optional `datum`, `signatur`, `absender` (sonst heutiges Datum und Name). Vorlage: die persönliche aus `/anschreiben-vorlage` unter `Profil/Anschreiben_Vorlage.docx`, sonst die des Plugins.

Ausgabe: `Anschreiben_<Name>_<Firma>_v<N>.docx`, mit `--pdf` auch `.pdf`. Ergebniszeile zusätzlich `woerter` und `zu_lang`. Exit 3 heißt länger als eine Seite: kürzen und neu rendern, die Datei bleibt zum Vergleich liegen.

## `to_pdf.py`

```
python "${CLAUDE_PLUGIN_ROOT}/scripts/to_pdf.py" <datei.docx> [--outdir <ordner>]
```

LibreOffice headless, sonst Word über docx2pdf, sonst Exit 4 mit Hinweis. Ergebniszeile: `pdf`, `methode`, `seiten`, `hinweis`.

## Dokumente melden

Nach jedem gerenderten Dokument, mit dem Pfad aus der Ergebniszeile:

```
dokument_registrieren(art="anschreiben", pfad="Bewerbungen/Beispiel_GmbH/Anschreiben_Anna_Test_Beispiel_GmbH_v1.docx", job_id=<id>, version=1)
```

`art`: `master_lebenslauf` (ohne `job_id`, aus `/lebenslauf`), `lebenslauf`, `anschreiben`, `recherche`, `interview_briefing`, `sonstiges`. Das PDF wird nicht extra gemeldet; das Dashboard zeigt den DOCX-Eintrag mit Ordner. `notiz` ist frei und kurz.

## Zwischenstände

`.jobradar/ablauf_<thema>.md`: freies Markdown, das ein Ablauf anlegt, wenn er Checkpoints hat (Onboarding in zwei Sitzungen, Bewerbung über mehrere Zettel). Am Anfang eines Ablaufs lesen, am Ende löschen oder als erledigt markieren.
