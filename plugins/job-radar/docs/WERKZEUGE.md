# Werkzeuge des Plugins

Diese Datei liest Claude, bevor ein Skript aufgerufen wird. Alle Skripte liegen unter `<Plugin-Pfad>/scripts/`. Den Plugin-Pfad nennt der Skill, der den Ablauf gestartet hat, in den Befehlen unten steht er als `<Plugin-Pfad>`. Aufruf mit `python` (Windows auch `py`, macOS und Linux `python3`). Jedes Skript schreibt als letzte Zeile `JOBRADAR_RESULT {…}`, ein JSON-Objekt. Daraus kommen die Pfade für `dokument_registrieren`. Pfade in der Ergebniszeile sind relativ zum Arbeitsordner und benutzen Schrägstriche. Liegt eine Datei außerhalb des Arbeitsordners, kommt ihr Pfad absolut zurück. Dann vor `dokument_registrieren` selbst relativ zum Job-Radar-Ordner machen, absolute Pfade weist das Werkzeug zurück.

## Ordnerregeln

- Pro Bewerbung ein Ordner `Bewerbungen/<Firma>/`, Firmenname mit Unterstrichen statt Leerzeichen und ohne `/ \ : * ? " < > |` (so sanitisiert das Skript auch die Dateinamen). Beispiel: `Bewerbungen/Beispiel_GmbH/`.
- Master-Lebenslauf nach `Bewerbungsmaterialien/`, angepasste Lebensläufe und Anschreiben in den Bewerbungsordner, Recherche als `Recherche.md`, Interview-Briefing als `Interview_Briefing.md` dort.
- Frühere Fassungen bleiben liegen. Die Skripte zählen `_v1`, `_v2` selbst hoch; `--version N` erzwingt eine Nummer.
- Die Daten für die Skripte (YAML) als `Lebenslauf_Daten.yml` beziehungsweise `Anschreiben_Daten.yml` in denselben Ordner schreiben; sie sind die Quelle der nächsten Fassung.

## `check_env.py`

```
python "<Plugin-Pfad>/scripts/check_env.py"
```

Exit 0: Python und Pakete in Ordnung. Exit 1 auch bei einem Python älter als 3.10. `hinweis` sagt dann, welche Fassung gebraucht und welche gefunden wurde, bei fehlenden Paketen steht dort der pip-Befehl. `pdf_moeglich` sagt, ob LibreOffice oder Word da ist. `plugin_root` ist der Pfad zum Plugin, wie das Skript ihn sieht.

`schrift_calibri` ist `true`, wenn Calibri oder die metrikgleiche Carlito installiert ist, und `false`, wenn keine von beiden gefunden wurde. `null` heißt, dass sich das nicht prüfen ließ, etwa auf einem Mac ohne `fc-list` oder wenn die Prüfung scheitert. Bei `false` erklärt `schrift_hinweis`, dass das PDF dann mit einer Ersatzschrift entsteht und sich Umbrüche verschieben können, sonst ist es `null`. Die Schrift ändert den Exit-Code nicht.

## `einrichten.py`

```
python "<Plugin-Pfad>/scripts/einrichten.py" --name "<Name>" --oberflaeche <cowork|claude_code>
```

Nur aus dem Skill `weiter`, beim Einrichten und wenn ein Ordner mit einer älteren Plugin-Version eingerichtet wurde. Idempotent. `--neu-schreiben` ersetzt README und CLAUDE.md. `--oberflaeche` bleibt, obwohl der Server die Oberfläche nicht mehr liest, weil Flags nur hinzukommen.

## `read_docx.py`

```
python "<Plugin-Pfad>/scripts/read_docx.py" <datei.docx> [--max-zeichen N]
```

Vorhandene Unterlagen lesen, etwa den alten Lebenslauf aus `Bewerbungsmaterialien/`: DOCX-Dateien liest `read_docx.py`, PDFs das normale Lesen. Ausgegeben werden Absätze und Tabellen in Dokumentreihenfolge, jede Tabellenzeile als Zellen mit „ | “ dazwischen; leere Absätze fallen weg. Tabellen, die in einer Zelle verschachtelt sind, liest das Skript rekursiv mit und rückt ihre Zeilen pro Ebene um zwei Leerzeichen ein. `--max-zeichen N` deckelt die Ausgabe und hängt „[gekürzt]“ an, sinnvoll bei langen Zeugnissen. Ergebniszeile: `datei`, `zeichen` (Länge des ausgegebenen Textes), `absaetze`, `tabellen`, `gekuerzt`. Exit 0, Exit 1 mit `FEHLER: …`, wenn die Datei fehlt, kein DOCX ist oder nicht gelesen werden kann. Das Skript schreibt nichts und meldet nichts; gelesene Unterlagen bleiben im Ordner.

## `foto_aus_docx.py`

```
python "<Plugin-Pfad>/scripts/foto_aus_docx.py" <lebenslauf.docx> [--ziel Bewerbungsmaterialien]
```

Holt das Bewerbungsfoto aus einem alten Word-Lebenslauf. Das Skript nimmt das größte PNG oder JPEG unter den Bildern des Dokuments, andere Formate wie EMF-Logos übergeht es. Es speichert das Bild als `Bewerbungsfoto.png` oder `Bewerbungsfoto.jpg` in `--ziel`, ohne die Angabe in `Bewerbungsmaterialien/`. Aus `.jpeg` wird dabei `.jpg`, eine vorhandene Datei gleichen Namens wird überschrieben. Ergebniszeile: `foto` (Pfad relativ zum Arbeitsordner, so direkt als `foto` in `Lebenslauf_Daten.yml` verwendbar, ohne Foto `null`) und `hinweis`. Exit 0 mit Foto. Exit 1 ohne Foto, `hinweis` nennt dann den Grund: Datei nicht gefunden, keine Word-Datei, Datei nicht lesbar, kein Bild im Dokument oder Foto nicht speicherbar.

## `cv_master.py`

```
python "<Plugin-Pfad>/scripts/cv_master.py" --data <Lebenslauf_Daten.yml> --name "<Name>" --output-dir <ordner> [--template <vorlage.docx>] [--version N] [--master] [--pdf]
```

YAML-Felder: `name`, `ort`, `phone`, `email`, `geburtsdatum` (optional), `positions[]` (je `datum`, `rolle`, `firma`, `bullets[]`, optional `subsections[]` mit `titel` und `description`), `education[]` (je `datum`, `titel`, `institution`, optional `detail`), `skills_section`, `sprachen_line`, `international[]`, `weiteres[]`, `foto` (optional, siehe unten). `bullets`, `international` und `weiteres` nehmen eine Liste, einen einzelnen Text oder nichts. Ohne `--template` die Vorlage des Plugins; eine eigene Vorlage kann unter `Profil/Lebenslauf_Vorlage.docx` liegen und wird dann mit `--template` übergeben.

Ausgabe: `Lebenslauf_<Name>_v<N>.docx` und `.md`, mit `--pdf` auch `.pdf`. Ergebniszeile: `art`, `docx`, `markdown`, `pdf`, `pdf_methode`, `seiten`, `hinweis`, `dateiname`, `version`, `vorlage`, `style_drift`. `art` ist `lebenslauf`, mit `--master` `master_lebenslauf`. Der Ablauf Lebenslauf rendert den Master mit `--master` nach `Bewerbungsmaterialien/`, angepasste Fassungen aus der Bewerbung laufen ohne die Fahne. `hinweis` trägt bei Exit 4 den Weg zum PDF von Hand. Exit 0 ok, 1 harter Fehler, 2 Style-Drift (Datei bleibt, Markdown ist die Wahrheit, Freund informieren), 4 PDF nicht erzeugt (DOCX bleibt, Hinweis weitergeben).

`foto` ist der Pfad zum Bewerbungsfoto, relativ zum Job-Radar-Ordner, in dem die Skripte laufen, etwa `Bewerbungsmaterialien/Bewerbungsfoto.jpg`. Die Vorlage des Plugins setzt es 32 mm breit an die Stelle `{{ foto }}`. Fehlt die Datei, steht in `hinweis` „Foto nicht gefunden: …“. Ist sie nicht lesbar, etwa ein HEIC-Bild mit `.jpg`-Endung oder eine abgeschnittene Datei, steht dort „Foto nicht lesbar: … (bitte als JPG oder PNG speichern)“. In beiden Fällen entsteht der Lebenslauf ohne Foto. Das Foto ändert den Exit-Code nicht. Kommt ein PDF-Hinweis dazu, stehen beide durch „; “ getrennt in `hinweis`. Den Foto-Hinweis dem Freund weitergeben.

## `cover_master.py`

```
python "<Plugin-Pfad>/scripts/cover_master.py" --data <Anschreiben_Daten.yml> --name "<Name>" --firma "<Firma>" --output-dir <ordner> [--template <vorlage.docx>] [--version N] [--max-words 400] [--pdf]
```

YAML-Felder: `empfaenger` (mehrzeilig), `betreff`, `anrede`, `body[]` (ein Eintrag pro Absatz, ohne Anrede und Gruß), optional `datum`, `signatur`, `absender` (sonst heutiges Datum und Name). Vorlage: die persönliche aus dem Ablauf Anschreiben-Vorlage unter `Profil/Anschreiben_Vorlage.docx`, sonst die des Plugins.

Ausgabe: `Anschreiben_<Name>_<Firma>_v<N>.docx`, mit `--pdf` auch `.pdf`. Die Ergebniszeile ist die des Lebenslaufs ohne `markdown` und zusätzlich mit `woerter` und `zu_lang`; `art` ist `anschreiben`, `hinweis` trägt bei Exit 4 den Weg zum PDF von Hand. Exit 2 und Exit 4 gelten hier genauso. Exit 3 heißt länger als eine Seite: kürzen und neu rendern, die Datei bleibt zum Vergleich liegen.

## `to_pdf.py`

```
python "<Plugin-Pfad>/scripts/to_pdf.py" <datei.docx> [--outdir <ordner>]
```

LibreOffice headless, sonst Word über docx2pdf, sonst Exit 4 mit Hinweis. Ergebniszeile: `docx`, `pdf`, `methode`, `seiten`, `hinweis`.

## Dokumente melden

Nach jedem gerenderten Dokument, mit dem Pfad aus der Ergebniszeile:

```
dokument_registrieren(art="anschreiben", pfad="Bewerbungen/Beispiel_GmbH/Anschreiben_Anna_Test_Beispiel_GmbH_v1.docx", job_id=<id>, version=1)
```

`art`: `master_lebenslauf` (ohne `job_id`, aus dem Ablauf Lebenslauf), `lebenslauf`, `anschreiben`, `recherche`, `interview_briefing`, `sonstiges`. Das PDF wird nicht extra gemeldet, das Dashboard zeigt den DOCX-Eintrag mit Ordner. `notiz` ist frei und kurz.

## Zwischenstände

`.jobradar/ablauf_<thema>.md`: freies Markdown, das ein Ablauf anlegt, wenn er Checkpoints hat (Standortbestimmung in zwei Sitzungen, Bewerbung über mehrere Zettel). Am Anfang eines Ablaufs lesen, am Ende löschen oder als erledigt markieren.
