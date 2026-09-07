# Job Radar Plugin

Marketplace und Plugin `job-radar` für Cowork und Claude Code. Gehört zu [Job Radar v2](https://github.com/rprey711/job-radar), dem Server mit Dashboard, Sammler und Connector. Das Plugin ist bewusst dünn: die Abläufe, Lernseiten und die Hilfe liegen im Server-Repo unter `content/` und kommen über den Connector (`anleitung_laden`). Hier liegen nur die Dinge, die lokal sein müssen.

## Was drin ist

| Pfad | Zweck |
|---|---|
| `.claude-plugin/marketplace.json` | Marketplace-Manifest, ein Eintrag: `plugins/job-radar` |
| `plugins/job-radar/.claude-plugin/plugin.json` | Plugin-Manifest, Version |
| `plugins/job-radar/.mcp.json` | Connector `jobradar` auf `https://jobs.162-55-50-225.nip.io/mcp` (OAuth über die 401-Antwort des Servers, kein `oauth`-Schlüssel, siehe unten) |
| `plugins/job-radar/skills/` | vierzehn Slash-Befehle; `/einrichten` mit eigenem Inhalt, die anderen holen ihr Skript vom Server |
| `plugins/job-radar/scripts/` | `check_env.py`, `einrichten.py`, `cv_master.py`, `cover_master.py`, `to_pdf.py`, `_common.py` |
| `plugins/job-radar/templates/` | DOCX-Vorlagen, Ordner-README und CLAUDE.md, Profilvorlagen |
| `plugins/job-radar/docs/WERKZEUGE.md` | Aufruf und Ergebnisformat der Skripte, gelesen von Claude |

## Installation

**Claude Code** (funktioniert mit dem privaten Repo, wenn `gh auth login` und `gh auth setup-git` eingerichtet sind):

```bash
claude plugin marketplace add rprey711/job-radar-plugin
claude plugin install job-radar@job-radar
```

Danach in einem Ordner „Job Radar“ Claude Code starten und `/einrichten` eingeben. Die Verbindung zum Server wird beim ersten Werkzeugaufruf über `/mcp` angemeldet.

**Cowork**: Customize, Plugins, Marketplace hinzufügen, `rprey711/job-radar-plugin`, Plugin „Job Radar“ installieren. Beim Installieren fragt Cowork nach der Anmeldung beim Connector. Stand 2026-09-07 lädt Cowork private GitHub-Repos nicht (Issues #28125 und #61271 in anthropics/claude-code); bis das Repo öffentlich ist, geht nur der Weg über Claude Code.

**Voraussetzungen beim Freund**: ein Konto im Job-Radar-Dashboard (Einladung von Raul), Claude Pro, in Claude Code zusätzlich Python 3.10 oder neuer. Die Pakete der Skripte: `python -m pip install -r plugins/job-radar/requirements.txt` (in Claude Code auf dem Rechner; `/einrichten` sagt den genauen Befehl). PDF entsteht über LibreOffice, sonst über Word, sonst per Hand.

## Connector-Deklaration

`.mcp.json` nennt nur `type` und `url`. Die Boolean-Form `"oauth": true`, die die Cowork-Dokumentation zeigt, lässt Claude Code 2.1 die ganze Deklaration verwerfen (am 2026-09-07 live geprüft: mit `true` fehlt der Server in `claude mcp list`, ohne den Schlüssel oder mit einem Objekt erscheint er als `plugin:job-radar:jobradar`). Claude Code findet den OAuth-Server über die 401-Antwort und die Protected-Resource-Metadaten von selbst. Ob Cowork ohne den Schlüssel beim Installieren nach der Anmeldung fragt oder erst beim ersten Werkzeugaufruf, zeigt Rauls Cowork-Test; falls Cowork den Schlüssel braucht, ist ein Objekt (`"oauth": {}`) der nächste Versuch, weil Claude Code diese Form annimmt.

## Vertrag mit dem Server

Die vierzehn Themen von `anleitung_laden` stehen in `connector/tools_status.TOPICS`, die Modulschlüssel für `job_radar_status(modul_erledigt=…)` in `repo/setup.MODULES`, die Befehle, die das Dashboard anzeigt, in `tools_status.COMMANDS`. Ändert sich dort etwas, ändern sich hier die Skills. Die Adresse in `.mcp.json` ist die des Servers; bei einem Domainwechsel Version anheben.

## Entwicklung

```bash
uv sync
uv run ruff check . && uv run ruff format --check .
uv run pytest
```

Die PDF-Tests laufen nur mit LibreOffice (`soffice` auf dem PATH, in `C:\Program Files\LibreOffice` oder über `JOBRADAR_SOFFICE`); ohne werden sie übersprungen. Die CI installiert LibreOffice und testet auf Python 3.10 und 3.12.

**Release**: Version in `plugins/job-radar/.claude-plugin/plugin.json` und in `.claude-plugin/marketplace.json` gleich anheben, committen, pushen. Claude Code und Cowork holen Updates aus dem Marketplace; in Claude Code `claude plugin update job-radar@job-radar`.

**Nach der Installation prüfen** (Task 12 des Bauplans): `claude plugin list`, `claude mcp list` (der Server heißt `plugin:job-radar:jobradar` oder ähnlich), `/einrichten` in einem leeren Ordner.
