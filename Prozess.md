# Prozessdokumentation

## Einleitung
Dieses Projekt entwickelt ein Python-Programm, das auf einem 77×50‑Raster eine optimale Raumverteilung berechnet, bei der die Raumfläche maximiert wird und alle formalen Bedingungen wie Gangbreite ≥4, Konnektivität, Türen und fester Eingang erfüllt sind (Quelle: README.md#10-20).

## Komplette Lösungsstrategie
1. **Exakter Optimierungsansatz**: Formuliere das Problem als ganzzahliges Modell und löse es mit OR‑Tools CP‑SAT; Räume werden als platzierbare Rechtecke, der Gang als Komplement modelliert (Quelle: README-SPEC.md#5-8).
2. **Variablen**: Für jede Rauminstanz werden Integer-Variablen für linke untere Koordinate `(x,y)` sowie Breite `w` und Höhe `h` definiert; boolesche Variablen steuern relative Lagen (Quelle: README-SPEC.md#9).
3. **Zielfunktion**: Maximiere die Summe aller Raumflächen; sekundäre weiche Ziele dürfen nur bei gleicher Raumfläche entscheiden (Quelle: README-SPEC.md#11).
4. **Fixer Eingang**: Reserviere die Zellen `x=56..59, y=40..49` als Gang und verbiete Überlappung mit Räumen (Quelle: README.md#41-45; README-SPEC.md#15).
5. **Nichtüberlappung**: Für jedes Raum­paar erzwinge eine der vier Lagebeziehungen (links, rechts, oberhalb, unterhalb) mithilfe von Binärvariablen und Big‑M‑Constraints (Quelle: README-SPEC.md#19).
6. **Gangbreite**: Räume bzw. Außenrand müssen überall einen Abstand ≥4 Zellen lassen, sofern dort Gang verläuft (Quelle: README-SPEC.md#21).
7. **Konnektivität**: Modell­iere einen Fluss von einer Superquelle (Eingang) zu allen Gangzellen, sodass nur eine Gang­komponente entsteht (Quelle: README-SPEC.md#23).
8. **Türen**: Jede Raumwand, die an Gang grenzt, erhält potenzielle Türvariablen; pro Raum muss mindestens eine aktiv sein, Türen dürfen keine Ecken belegen (Quelle: README.md#73-84; README-SPEC.md#25).
9. **Solverlauf**: Der CP‑SAT‑Solver maximiert die Zielfunktion; bei Abbruch wird die beste gefundene Lösung gespeichert (Quelle: README-SPEC.md#28).
10. **Artefakte**: Nach der Optimierung werden `solution.json`, `solution.png` und `validation_report.json` erzeugt (Quelle: AGENTS.md#14; README-SPEC.md#44-81).
11. **Validierung**: Prüfe Komplement, Eingangsfreiheit, Überlappung, Gangbreite, Konnektivität, Türregeln und Erreichbarkeit (Quelle: README-SPEC.md#57-77).
12. **CLI & Logging**: Biete Schalter für Log‑Level, Format, Datei, Progress‑Anzeigen, Seed, Zeitlimit und Threads; logge strukturierte Events und zeige Fortschritt im Terminal (Quelle: README.md#409-439; README-SPEC.md#83-91).
13. **Abbruch & Checkpoints**: Unterstütze SIGINT sowie optionale periodische Sicherungen (`--checkpoint`) (Quelle: README.md#447-450; README-SPEC.md#91).
14. **Tests**: Entwickle und erweitere Pytest‑basierte Tests für Geometrie und Validierung (Quelle: AGENTS.md#17; README.md#475-479).

## Schritt-für-Schritt-Aufgabenliste
1. Projekt mit Python ≥ 3.10 initialisieren (Quelle: AGENTS.md#12) – ✔ erledigt
2. Konfigurationsdaten aus `rooms.yaml` laden (Quelle: README-SPEC.md#34-35) – ✔ erledigt
3. CpModel und Variablen `x,y,w,h` pro Raum definieren (Quelle: README-SPEC.md#9) – ✔ erledigt
4. Eingangsbereich als stets freien Gang modellieren (Quelle: README.md#41-45; README-SPEC.md#15) – ✔ erledigt
5. Rand- und Rastergrenzen (`x+w≤77`, `y+h≤50`) absichern (Quelle: README-SPEC.md#36) – ✔ erledigt
6. Nichtüberlappung durch Lage-Binärvariablen erzwingen (Quelle: README-SPEC.md#19) – ✖ offen
7. Mindest‑Gangbreite ≥4 überall sicherstellen (Quelle: README.md#91-98; README-SPEC.md#21) – ✖ offen
8. Gang-Konnektivität via Flussmodell herstellen (Quelle: README-SPEC.md#23) – ✖ offen
9. Pro Raum mindestens eine Tür zum Gang anlegen (Quelle: README.md#73-84; README-SPEC.md#25) – ✖ offen
10. Zielfunktion zur Maximierung der Raumfläche definieren (Quelle: README-SPEC.md#11) – ✖ offen
11. Solver starten und bei Abbruch beste Lösung sichern (Quelle: README-SPEC.md#28) – ✖ offen
12. `solution.json` generieren (Quelle: README-SPEC.md#44-52) – ✖ offen
13. `solution.png` rendern (Quelle: README-SPEC.md#55) – ✖ offen
14. `validation_report.json` schreiben (Quelle: README-SPEC.md#57-81) – ✖ offen
15. CLI‑Schalter implementieren (`--log-level`, `--log-format`, `--log-file`, `--progress`, `--progress-interval`, `--seed`, `--time-limit`, `--threads`) (Quelle: README.md#409-416) – ✔ erledigt
16. Strukturierte Logs und Progress-Anzeige entwickeln (Quelle: README.md#418-439; README-SPEC.md#83-91) – ✖ offen
17. Sauberen Abbruch und optionale Checkpoints unterstützen (Quelle: README.md#447-450; README-SPEC.md#91) – ✖ offen
18. Validierung aller Muss-Kriterien implementieren (Quelle: README.md#15-20; README-SPEC.md#57-77) – ✔ erledigt
19. Tests für Geometrie und Validierung erweitern (Quelle: AGENTS.md#17; README.md#475-479) – ✖ offen
20. Prozessstarter-Skript `start_process.py` mit Standardpfaden bereitstellen – ✔ erledigt

## Parameter- & Optionsreferenz
- Rastergröße `GRID_W=77`, `GRID_H=50` (Quelle: README.md#115-118)
- Eingang `x1=56`, `x2=60`, `y1=40`, `y2=50` (Quelle: README.md#41-45)
- CLI: `--log-level {DEBUG,INFO,WARN,ERROR}` (Quelle: README.md#411)
- CLI: `--log-format {text,json}` (Quelle: README.md#412)
- CLI: `--log-file <pfad>` (Quelle: README.md#413)
- CLI: `--progress {auto,off}` (Quelle: README.md#414)
- CLI: `--progress-interval <sek>` (Quelle: README.md#415)
- CLI: `--seed <int>` (Quelle: README.md#416)
- CLI: `--time-limit <sek>` (Quelle: README.md#416)
- CLI: `--threads <n>` (Quelle: README.md#416)
- Ausgaben: `solution.json`, `solution.png`, `validation_report.json` (Quelle: AGENTS.md#14)

## Status
| Aufgabe                                     | Status | Letzte Änderung        | Verantwortlich |
|---------------------------------------------|:------:|------------------------|----------------|
| Prozessdokumentation aufsetzen              | ✔     | 2025-08-03T21:25:34Z   | Agent          |
| Algorithmus zur Raumverteilung implementieren| ✖     | 2025-08-03T21:40:00Z   | Agent          |
| Logging & Fortschrittsanzeige ausbauen      | ✖     | 2025-08-03T21:25:34Z   | Agent          |
| Tests erweitern                             | ✖     | 2025-08-03T21:25:34Z   | Agent          |
| Prozessstarter-Skript hinzufügen            | ✔     | 2025-08-04T00:00:00Z   | Agent          |

## Change-Log
- 2025-08-03T21:25:34Z – Initiale Prozessbeschreibung erstellt
- 2025-08-03T21:40:00Z – CP-SAT-Variablen und Randbedingungen implementiert
- 2025-08-04T00:00:00Z – Prozessstarter-Skript hinzugefügt
