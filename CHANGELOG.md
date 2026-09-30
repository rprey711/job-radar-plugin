# Changelog

Jedes Release des Plugins bekommt hier einen Abschnitt und einen Git-Tag `v<Version>`, die neueste Version steht oben. Versionen bis 0.2.5 haben keinen Abschnitt, ihre Änderungen stehen in der Git-Historie.

## 0.4.0 (2026-10-01)

Die Texte, die Freunde vom Plugin lesen, tragen die Namen aus Phase 4. Das Plugin geht diesmal vor dem Server live, weil die Servertexte von Phase 4 auf diese Namen verweisen (E12 C). Vom Server braucht es nichts Neues.

- Die Beschreibungen von `/weiter`, `/bewerten` und `/bewerbung` beginnen mit einem Satz von höchstens zwölf Wörtern für das Befehlsmenü. Danach folgen die Sätze, auf die Claude den Befehl startet, mit „Pass meine Suche an“ statt „Ändere mein Suchprofil“ und „Etwas klappt nicht“ als neuem Satz für `/weiter`.
- Hakt etwas, bietet `/weiter` an, das Problem zu melden. Claude fasst die Meldung zusammen, zeigt sie und schickt sie mit `problem_melden` erst nach einem „ja“. Hat der Server das Werkzeug noch nicht, bittet Claude wie bisher, Raul Bescheid zu geben. Dieselbe Regel steht in der `CLAUDE.md` im Ordner.
- Die `README.md` im Ordner hat höchstens 200 statt 467 Wörter. Sie nennt die drei Befehle mit ihren Sätzen, die vier Chats nur mit Titel („Job Radar Einrichtung“, „Job Radar Tagesrunde“, ein Chat je Bewerbung, „Job Radar Pflege“) und verlinkt die Hilfe im Dashboard statt der Anleitung für Cowork.
- Ordner-`CLAUDE.md`, Profilvorlagen und Skill-Beschreibungen sprechen von Profil, Profilgespräch, Suche, Feinauswahl, Rückschau, Anker und Stilregeln statt von Kandidatenprofil, Kurzprofil, Suchprofil, Triage, Kalibrierung, Anker-Pool und Style Guide. Der erste Chat heißt „Job Radar Einrichtung“, und `/weiter` verweist am Ende der Einrichtung auf die Seite „Einrichtung“ statt auf die Anleitung für Cowork.
- `Bewerbungsmethode.md` und `Style_Guide.md` folgen Rauls Schreibregeln. Pfeilketten, Semikolons und Doppelpunkte zwischen Sätzen, Versalien und die drei Emoji sind weg, ebenso die Regel, die Doppelpunkte statt Gedankenstrichen empfahl, und der Abschnitt „Was wir nicht mehr verwenden“. Deutsche Wörter ersetzen Positive Pivot (Umlenken), Micro-Story (Eigene Szene), Swap-the-firm-name-Test (Firmennamen-Tausch) und Quick-Reference mit Talking Points (Schnellübersicht). Oben stehen je zwei Sätze für den Freund.
- Ordner, die mit 0.3.x eingerichtet sind, bekommen `README.md` und `CLAUDE.md` beim nächsten `/weiter` neu, weil die Plugin-Version abweicht. Die Profilvorlagen bleiben dort, wie sie sind, weil Claude sie schon gefüllt hat.
- Die Tests prüfen Skill-Beschreibungen und Ordnervorlagen auf die verbotenen Varianten des Glossars (eine Kopie der Liste aus `glossar.py` des Servers), auf Rauls Schreibregeln und auf die Wortbudgets. Sie halten auch die Überschriften fest, die die Abläufe des Servers in den Profilvorlagen suchen.

## 0.3.0 (2026-09-29)

Drei Befehle statt vierzehn. Freunde arbeiten nur noch in Cowork und in der Claude-App, Claude Code bleibt Rauls Weg und der der Proben. Braucht den Server-Stand von Phase 2 mit dem Thema `weiter`, deshalb ging der Server zuerst live.

- Neu ist `/weiter`. Fehlen Ordner oder Verbindung, richtet der Skill beides ein, mit dem Inhalt des früheren `/einrichten`. Sonst lädt er die Weiche `weiter` vom Server, die den nächsten Schritt oder den Stand des Tages nennt.
- `/bewerten` und `/bewerbung <Firma oder Link>` bleiben dünne Hüllen um ihr Skript vom Server.
- Freunde arbeiten in Cowork im Projekt „Job Radar“ mit vier Arten von Chats: Einrichtung, „Job Radar Tagesrunde“, ein Chat je Bewerbung und „Job Radar Pflege“. Am Ende der Einrichtung bittet `/weiter`, das Projekt aus dem Ordner anzulegen. Der Plan geht im selben Chat weiter, beim Wechsel der Stufe nach dem Umstellen des Modells. `/bewerbung <Firma>` beginnt den Chat einer Bewerbung, Interview und Review zu diesem Job laufen später dort.
- Alle drei Skills starten auch auf einen Satz, etwa „Wie geht es weiter?“, „Bewerte meine neuen Jobs“ oder „Bereite eine Bewerbung bei … vor“. Keiner trägt mehr `disable-model-invocation`.
- Die elf übrigen Befehle entfallen: `/kurzprofil`, `/onboarding`, `/lebenslauf`, `/anschreiben-vorlage`, `/suchprofil`, `/triage`, `/review`, `/interview`, `/scout`, `/kalibrierung` und `/hilfe`. Ihre Abläufe starten über `/weiter` oder einen Wunsch in Worten. `/einrichten` geht in `/weiter` auf.
- Jeder Skill nennt Claude den Plugin-Pfad. `docs/WERKZEUGE.md` benutzt `${CLAUDE_PLUGIN_ROOT}` nicht mehr und spricht vom Plugin-Pfad, den der Skill genannt hat.
- `/weiter` schreibt README und CLAUDE.md eines Ordners neu, der mit einer älteren Plugin-Version eingerichtet wurde.
- `/bewerten` läuft auch als geplante Morgenbewertung in Cowork, außerhalb des Projekts, ohne Ordner und ohne Rückfragen. Sie startet mit „Morgenbewertung: Bewerte meine neuen Jobs“ und gibt den fünf Werkzeugen `job_radar_status`, `anleitung_laden`, `profil_lesen`, `jobs_laden` und `jobs_aktualisieren` `geplant=true` mit, damit der Lauf nicht als Besuch des Freundes zählt.
- Ordner-README, Ordner-CLAUDE.md, Profilvorlagen und README nennen die drei Befehle und Cowork, Ordner-README und Ordner-CLAUDE.md auch die vier Chats. Die Ordner-CLAUDE.md sagt, dass bei allem rund um Job Radar zuerst `job_radar_status` und dann `anleitung_laden` kommen.
- `einrichten.py --oberflaeche` bleibt, weil Skript-Flags nur hinzukommen. Ein Test hält die Flags aller Skripte fest.
