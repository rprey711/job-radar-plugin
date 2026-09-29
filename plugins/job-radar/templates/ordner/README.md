# Job Radar, Ordner von {{NAME}}

Dieser Ordner ist dein Arbeitsplatz für die Jobsuche mit Claude. Eingerichtet am {{DATUM}} mit dem Plugin Job Radar {{PLUGIN_VERSION}}. Dashboard: {{DASHBOARD}}

## Was wo liegt

| Ordner | Inhalt |
|---|---|
| `Profil/` | Kandidatenprofil, Bewerbungsmethode, Style Guide, Lernnotizen. Claude füllt sie in den Abläufen, du kannst jederzeit reinschreiben. |
| `Bewerbungsmaterialien/` | Dein Lebenslauf, alte Anschreiben, Zeugnisse, Foto. Lege hier ab, was Claude kennen soll. |
| `Bewerbungen/<Firma>/` | Pro Bewerbung ein Unterordner mit Lebenslauf, Anschreiben (DOCX und PDF), Recherche und Interview-Briefing. Frühere Fassungen bleiben als `_v1`, `_v2` liegen. |
| `.jobradar/` | Stand der Einrichtung und Zwischenstände der Abläufe. Nichts, was du anfassen musst. |

Der Ordner liegt bei dir, auf deinem Rechner oder in deinem eigenen Cloud-Speicher. Zum Server gehen nur Scores, Entscheidungen, Notizen zu Jobs, das Suchprofil, eine kompakte Profilkopie und die Namen der Dokumente, nie die Dateien selbst.

Was Claude und der Server mit deinen Daten tun und wer sie sonst noch verarbeitet, steht auf der Seite [Datenschutz]({{DASHBOARD}}/datenschutz).

## Drei Befehle

In Cowork brauchst du drei Befehle. Jeder startet auch auf einen Satz, und in der Claude-App auf dem Handy reichen die Sätze.

| Befehl | Satz | Wofür |
|---|---|---|
| `/weiter` | „Wie geht es weiter?“ | sagt, was ansteht, und führt dich durch die Einrichtung und danach durch jeden Tag |
| `/bewerten` | „Bewerte meine neuen Jobs“ | gibt neuen Jobs Score und Begründung |
| `/bewerbung <Firma oder Link>` | „Bereite eine Bewerbung bei … vor“ | schreibt Lebenslauf und Anschreiben für einen Job |

Alles andere sagst du Claude in eigenen Worten, auch hinter `/weiter`, etwa `/weiter Interview bei Lorenz Logistik`. Die Seite „Hilfe“ im Dashboard nennt die Sätze mit Dauer und Modell.

## Chats in Cowork

Du arbeitest in Cowork im Projekt „Job Radar“, das auf diesen Ordner zeigt. Wie du es anlegst, steht in der [Anleitung für Cowork]({{DASHBOARD}}/anleitung/cowork). Dort reichen vier Chats: einer für die Einrichtung, der Chat „Job Radar Tagesrunde“ für jeden Morgen, je Bewerbung ein eigener Chat, den `/bewerbung <Firma>` beginnt, und der Chat „Job Radar Pflege“ für Suchprofil, Rückschau und Hilfe.

## Der Alltag

Morgens tippst du im Chat „Job Radar Tagesrunde“ `/weiter`. Claude sagt dir dann, was seit deinem letzten Besuch passiert ist und womit du anfangen solltest. Die tägliche Runde hat vier Schritte.

1. Morgens liegen neue Jobs im Dashboard unter „Neu“.
2. Claude bewertet sie mit `/bewerten`. Mit der Morgenbewertung, die `/weiter` dir anbietet, passiert das jeden Morgen von selbst.
3. Im Dashboard klickst du Ja oder Nein, gern auf dem Handy.
4. In der Tagesrunde sortiert `/weiter` die Ja-Jobs in Go, Vielleicht und Skip. Für jeden Go-Job beginnt `/bewerbung <Firma>` einen eigenen Chat, in dem Claude die Unterlagen schreibt. Versenden tust du selbst, danach klickst du im Dashboard auf „Abgeschickt“.

## Wenn etwas hakt

Sag Claude „Was kann ich hier machen?“ oder öffne die Hilfe im Dashboard. Wenn Claude den Server nicht erreicht, öffne in Cowork die Plugin-Seite und melde die Verbindung „Job Radar“ neu an.
