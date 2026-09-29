# Changelog

Jedes Release des Plugins bekommt hier einen Abschnitt und einen Git-Tag `v<Version>`, die neueste Version steht oben. Versionen bis 0.2.5 haben keinen Abschnitt, ihre Änderungen stehen in der Git-Historie.

## 0.3.0 (2026-09-29)

Drei Befehle statt vierzehn. Freunde arbeiten nur noch in Cowork und in der Claude-App, Claude Code bleibt Rauls Weg und der der Proben. Braucht den Server-Stand von Phase 2 mit dem Thema `weiter`, deshalb ging der Server zuerst live.

- Neu ist `/weiter`. Fehlen Ordner oder Verbindung, richtet der Skill beides ein, mit dem Inhalt des früheren `/einrichten`. Sonst lädt er die Weiche `weiter` vom Server, die den nächsten Schritt oder den Stand des Tages nennt.
- `/bewerten` und `/bewerbung <Firma oder Link>` bleiben dünne Hüllen um ihr Skript vom Server.
- Freunde arbeiten in Cowork im Projekt „Job Radar“ mit vier Arten von Chats: Einrichtung, „Job Radar Tagesrunde“, ein Chat je Bewerbung und „Job Radar Pflege“. Am Ende der Einrichtung bittet `/weiter`, das Projekt aus dem Ordner anzulegen. Der Plan geht im selben Chat weiter, beim Wechsel der Stufe nach dem Umstellen des Modells. `/bewerbung <Firma>` beginnt den Chat einer Bewerbung, Interview und Review zu diesem Job laufen später dort.
- Alle drei Skills starten auch auf einen Satz, etwa „Wie geht es weiter?“, „Bewerte meine neuen Jobs“ oder „Bereite eine Bewerbung bei … vor“. Keiner trägt mehr `disable-model-invocation`.
- Die elf übrigen Befehle entfallen: `/kurzprofil`, `/onboarding`, `/lebenslauf`, `/anschreiben-vorlage`, `/suchprofil`, `/triage`, `/review`, `/interview`, `/scout`, `/kalibrierung` und `/hilfe`. Ihre Abläufe starten über `/weiter` oder einen Wunsch in Worten. `/einrichten` geht in `/weiter` auf.
- Jeder Skill nennt Claude den Plugin-Pfad. `docs/WERKZEUGE.md` benutzt `${CLAUDE_PLUGIN_ROOT}` nicht mehr und spricht vom Plugin-Pfad, den der Skill genannt hat.
- `/weiter` schreibt README und CLAUDE.md eines Ordners neu, der mit einer älteren Plugin-Version eingerichtet wurde.
- `/bewerten` läuft auch als geplante Morgenbewertung in Cowork, außerhalb des Projekts, ohne Ordner und ohne Rückfragen. Sie startet mit „Morgenbewertung: Bewerte meine neuen Jobs“ und gibt den vier Werkzeugen `job_radar_status`, `anleitung_laden`, `jobs_laden` und `jobs_aktualisieren` `geplant=true` mit, damit der Lauf nicht als Besuch des Freundes zählt.
- Ordner-README, Ordner-CLAUDE.md, Profilvorlagen und README nennen die drei Befehle und Cowork, Ordner-README und Ordner-CLAUDE.md auch die vier Chats. Die Ordner-CLAUDE.md sagt, dass bei allem rund um Job Radar zuerst `job_radar_status` und dann `anleitung_laden` kommen.
- `einrichten.py --oberflaeche` bleibt, weil Skript-Flags nur hinzukommen. Ein Test hält die Flags aller Skripte fest.
