# Job Radar Plugin

Marketplace und Plugin `job-radar` für Cowork. Gehört zu [Job Radar v2](https://github.com/rprey711/job-radar), dem Server mit Dashboard, Sammler und Connector. Das Plugin ist bewusst dünn. Die Abläufe, die Lernseiten und die Hilfe liegen im Server-Repo unter `content/` und kommen über den Connector (`anleitung_laden`), hier liegen nur die Dinge, die lokal sein müssen.

> Das Repo ist öffentlich, damit Cowork das Plugin laden kann. Nutzen lässt es sich nur mit einem Konto im Job-Radar-Dashboard, das Raul per Einladung anlegt. Lizenz: alle Rechte vorbehalten, siehe `LICENSE`.

Freunde arbeiten in Cowork und in der Claude-App auf dem Handy. Claude Code ist Rauls Arbeitsweg und der Weg der automatischen Proben, Freunden wird es nicht angeboten.

## Was drin ist

| Pfad | Zweck |
|---|---|
| `.claude-plugin/marketplace.json` | Marketplace-Manifest, ein Eintrag: `plugins/job-radar` |
| `plugins/job-radar/.claude-plugin/plugin.json` | Plugin-Manifest, Version |
| `plugins/job-radar/.mcp.json` | Connector `jobradar` auf `https://jobs.162-55-50-225.nip.io/mcp` (OAuth über die 401-Antwort des Servers, kein `oauth`-Schlüssel, siehe unten) |
| `plugins/job-radar/skills/` | drei Befehle: `/weiter` richtet Ordner und Verbindung ein und lädt danach die Weiche vom Server, `/bewerten` und `/bewerbung` holen ihr Skript vom Server |
| `plugins/job-radar/scripts/` | `check_env.py`, `einrichten.py`, `read_docx.py`, `foto_aus_docx.py`, `cv_master.py`, `cover_master.py`, `to_pdf.py`, `_common.py` |
| `plugins/job-radar/templates/` | DOCX-Vorlagen, Ordner-README und CLAUDE.md, Profilvorlagen |
| `plugins/job-radar/docs/WERKZEUGE.md` | Aufruf und Ergebnisformat der Skripte, gelesen von Claude |
| `CHANGELOG.md` | ein Eintrag je Release, die neueste Version oben |

## Installation

**Cowork**, der Weg der Freunde: Customize, Plugins, Marketplace hinzufügen, `rprey711/job-radar-plugin`, Plugin „Job Radar“ installieren. Beim Installieren fragt Cowork nach der Anmeldung beim Connector. Danach in Cowork eine Aufgabe im Ordner „Job Radar“ öffnen und `/weiter` tippen. Am Ende der Einrichtung bittet Claude, aus dem Ordner das Projekt „Job Radar“ anzulegen, in dem die weiteren Chats laufen (Einrichtung, „Job Radar Tagesrunde“, ein Chat je Bewerbung, „Job Radar Pflege“). Das Repo ist seit dem 2026-09-09 öffentlich, weil Cowork private GitHub-Repos nicht lädt (Issues #28125 und #61271 in anthropics/claude-code).

Beim Freund braucht es ein Konto im Job-Radar-Dashboard (Einladung von Raul) und Claude Pro mit der Claude-Desktop-App. PDF entsteht über LibreOffice, sonst über Word, sonst per Hand.

**Claude Code**, der Weg für Raul und die Proben:

```bash
claude plugin marketplace add rprey711/job-radar-plugin
claude plugin install job-radar@job-radar
```

Danach in einem Ordner „Job Radar“ Claude Code starten und `/weiter` eingeben. Die Verbindung zum Server meldet `/mcp` an. Claude Code braucht Python 3.10 oder neuer auf dem Rechner und die Pakete der Skripte (`python -m pip install -r plugins/job-radar/requirements.txt`). Fehlt etwas, nennt `/weiter` den genauen Befehl.

## Connector-Deklaration

`.mcp.json` nennt nur `type` und `url`. Die Boolean-Form `"oauth": true`, die die Cowork-Dokumentation zeigt, lässt Claude Code 2.1 die ganze Deklaration verwerfen (am 2026-09-07 live geprüft: mit `true` fehlt der Server in `claude mcp list`, ohne den Schlüssel oder mit einem Objekt erscheint er als `plugin:job-radar:jobradar`). Claude Code findet den OAuth-Server über die 401-Antwort und die Protected-Resource-Metadaten von selbst. Ob Cowork ohne den Schlüssel beim Installieren nach der Anmeldung fragt oder erst beim ersten Werkzeugaufruf, zeigt Rauls Cowork-Test. Falls Cowork den Schlüssel braucht, ist ein Objekt (`"oauth": {}`) der nächste Versuch, weil Claude Code diese Form annimmt.

## Vertrag mit dem Server

Die Skills laden über `anleitung_laden` die Themen `weiter`, `bewerten` und `bewerbung` und melden beim Einrichten das Modul `ordner`. Alle Themen stehen in `connector/tools_status.TOPICS`, die Modulschlüssel für `job_radar_status(modul_erledigt=…)` in `repo/setup.MODULES`, die Schritte des Plans in `repo/plan.STEPS`. Ändert sich dort etwas, ändern sich hier die Skills. Modellnamen stehen nur in `model_tiers.py` auf dem Server und kommen über `job_radar_status` und `anleitung_laden`. Skills und Vorlagen nennen keinen, das prüft `test_no_model_names_in_plugin_texts`.

Jeder Skill nennt Claude den Plugin-Pfad (`${CLAUDE_PLUGIN_ROOT}`), weil die Variable nur in Skill-Dateien ersetzt wird. Die Texte vom Server und `docs/WERKZEUGE.md` sprechen deshalb vom „Plugin-Pfad, den der Skill genannt hat“. Die Adresse in `.mcp.json` ist die des Servers. Bei einem Domainwechsel Version anheben.

## Regeln für Texte und Versionen

Server und Plugin gehen getrennt live. Damit das ohne eigene Maschinerie klappt, gelten vier Regeln (Entscheidung E12 C).

1. Was gebraucht wird, geht zuerst live. Braucht ein Server-Text etwas Neues aus dem Plugin, etwa ein Skript, ein Flag oder eine Vorlage, erscheint das Plugin-Release zuerst. Braucht ein Skill etwas Neues vom Server, etwa ein Thema, ein Werkzeug oder einen Parameter, geht der Server zuerst live. Bei 0.3.0 war das der Server, weil der Skill `weiter` das Thema `weiter` lädt.
2. Skript-Flags kommen nur hinzu. Keins wird umbenannt oder entfernt, weil Server-Texte und ältere Skills sie weiter aufrufen. Deshalb bleibt `einrichten.py --oberflaeche`, obwohl der Server die Oberfläche nicht mehr liest. `tests/test_script_flags.py` hält die Flags fest.
3. Eine Prüfung der Plugin-Version gibt es nicht. Ein älteres Plugin läuft weiter, solange jedes Thema, das seine Skills laden, auf dem Server bestehen bleibt. Für 0.2.5 gilt das, weil sein Skill `einrichten` kein Thema lädt und alle übrigen Themen seiner Skills bleiben.
4. Jedes Release bekommt einen Git-Tag `v<Version>` und einen Eintrag in `CHANGELOG.md`.

## Entwicklung

```bash
uv sync
uv run ruff check . && uv run ruff format --check .
uv run pytest
```

Die PDF-Tests laufen nur mit LibreOffice (`soffice` auf dem PATH, in `C:\Program Files\LibreOffice` oder über `JOBRADAR_SOFFICE`), ohne werden sie übersprungen. Die CI installiert LibreOffice und testet auf Python 3.10 und 3.12.

## Release

1. Braucht ein Skill etwas Neues vom Server, zuerst den Server ausrollen und `/health` prüfen (Regel 1).
2. Version in `plugins/job-radar/.claude-plugin/plugin.json` und in `.claude-plugin/marketplace.json` gleich anheben, oben in `CHANGELOG.md` einen Abschnitt `## <Version> (<Datum>)` anlegen, committen. `tests/test_manifests.py` prüft, dass beide Versionen und der oberste Abschnitt übereinstimmen.
3. Pushen und die CI abwarten.
4. Tag und GitHub-Release anlegen, mit dem Abschnitt aus `CHANGELOG.md` als Text:

```bash
V=0.3.0
NOTES="$(mktemp)"
awk -v v="$V" 'index($0, "## " v " ") == 1 {f=1; next} /^## /{f=0} f' CHANGELOG.md > "$NOTES"
git tag -a "v$V" -m "Job Radar Plugin $V"
git push origin "v$V"
gh release create "v$V" --verify-tag --title "$V" --notes-file "$NOTES"
```

Cowork und Claude Code holen Updates aus dem Marketplace, in Claude Code mit `claude plugin update job-radar@job-radar`.

**Nach der Installation prüfen**: `claude plugin list`, `claude mcp list` (der Server heißt `plugin:job-radar:jobradar` oder ähnlich), `/weiter` in einem leeren Ordner.
