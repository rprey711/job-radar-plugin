# Job Radar, Ordner von {{NAME}}

Dieser Ordner ist dein Arbeitsplatz für die Jobsuche mit Claude. Eingerichtet am {{DATUM}} mit dem Plugin Job Radar {{PLUGIN_VERSION}}. Dashboard: {{DASHBOARD}}

## Was wo liegt

| Ordner | Inhalt |
|---|---|
| `Profil/` | Kandidatenprofil, Bewerbungsmethode, Style Guide, Lernnotizen. Claude füllt sie in den Abläufen, du kannst jederzeit reinschreiben. |
| `Bewerbungsmaterialien/` | Dein Lebenslauf, alte Anschreiben, Zeugnisse, Foto. Lege hier ab, was Claude kennen soll. |
| `Bewerbungen/<Firma>/` | Pro Bewerbung ein Unterordner mit Lebenslauf, Anschreiben (DOCX und PDF), Recherche und Interview-Briefing. Frühere Fassungen bleiben als `_v1`, `_v2` liegen. |
| `.jobradar/` | Stand der Einrichtung und Zwischenstände der Abläufe. Nichts, was du anfassen musst. |

Der Ordner bleibt auf deinem Rechner. Zum Server gehen nur Scores, Entscheidungen, das Suchprofil, eine kompakte Profilkopie und die Namen der Dokumente, nie die Dateien selbst.

## Der Alltag in vier Schritten

1. Morgens liegen neue Jobs im Dashboard unter „Neu“.
2. In Cowork oder in der Claude-App: `/bewerten` oder „Bewerte die neuen Jobs“.
3. Im Dashboard Ja oder Nein klicken, gern auf dem Handy.
4. In Cowork `/triage` für die Ja-Jobs, dann `/bewerbung <Firma>` für die Go-Jobs. Versenden tust du selbst und setzt den Status im Dashboard.

## Befehle

`/einrichten`, `/kurzprofil`, `/onboarding`, `/lebenslauf`, `/anschreiben-vorlage`, `/suchprofil`, `/bewerten`, `/triage`, `/bewerbung <Firma>`, `/review`, `/interview <Firma>`, `/scout`, `/kalibrierung`, `/hilfe`. Die Seite „Hilfe“ im Dashboard erklärt jeden Befehl mit Dauer, Voraussetzung und empfohlenem Modell.

## Wenn etwas hakt

Sag Claude „Was kann ich hier machen?“ oder öffne die Hilfe im Dashboard. Wenn Claude den Server nicht erreicht, hilft in Cowork die Plugin-Seite (Verbindung anmelden), in Claude Code der Befehl `/mcp`.
