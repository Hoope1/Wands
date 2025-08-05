# Prozessdokumentation

## Einleitung
Hinweis: Die Prüfroutine in `AGENTS_Pruefung.md` ist nach jeder Änderung vollständig auszuführen und bei Fehlern zu wiederholen.

Dieses Projekt entwickelt ein Python-Programm, das auf einem 77×50‑Raster eine optimale Raumverteilung berechnet, bei der die Raumfläche maximiert wird und alle formalen Bedingungen wie Gangbreite ≥4, Konnektivität, Türen und fester Eingang erfüllt sind (Quelle: README.md#10-20).

## Ablauf in 10 Schritten
1. **Aufgabe verstehen** – Issue lesen und Ziele klären.
2. **Arbeitsbaum prüfen** – `git status` ausführen, bei Bedarf aktualisieren oder aufräumen.
3. **Anweisungsscan** – alle Dateien mit `readme` oder `agent` im Namen durchsuchen; spezifischere Verzeichnisse überschreiben allgemeinere Vorgaben.
4. **Prozess.md pflegen** – Aufgabenliste, Status-Tabelle und Change‑Log aktualisieren; Parameterreferenzen ergänzen.
5. **Änderungen planen** – betroffene Dateien und Tests festlegen.
6. **Implementieren oder dokumentieren** – Änderungen idempotent und minimal durchführen.
7. **Linting** – `ruff .` ausführen; bei Ausfall `flake8` nutzen.
8. **Tests** – `pytest` laufen lassen und Fehler beheben.
9. **Commit** – nur bei sauberem Test/Lint-Status, Commit‑Message im Imperativ auf Deutsch.
10. **Review & PR** – `git status` kontrollieren, Pull‑Request erstellen und Prozess beenden.

### Einbeziehung zusätzlicher Vorgaben
- Anweisungen aus `README*`‑ und `AGENT*`‑Dateien gelten für den jeweiligen Verzeichnisbaum.
- Tiefer liegende Dateien haben Vorrang vor übergeordneten.
- Benutzer‑ und Systemvorgaben haben höhere Priorität als AGENTS/README.

## Idempotenz-Regeln
- Schritte nur ausführen, wenn Änderungen nötig sind.
- Vor dem Schreiben prüfen, ob Inhalt bereits existiert; doppelte Einträge vermeiden.
- Chronologische Listen (Fortschritt, Change‑Log, Aufgaben) nur ergänzen, niemals bearbeiten oder löschen.
- Werkzeuge mit festen Parametern ausführen (z. B. definierter Zufallsseed).
- Wiederholtes Ausführen des Prozesses führt zu identischen Ergebnissen und unverändertem Git‑Status.

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

---

## Schritt-für-Schritt-Aufgabenliste
1. Projekt mit Python ≥ 3.10 initialisieren (Quelle: AGENTS.md#12) – ✔ erledigt
2. Konfigurationsdaten aus `rooms.yaml` laden (Quelle: README-SPEC.md#34-35) – ✔ erledigt
3. CpModel und Variablen `x,y,w,h` pro Raum definieren (Quelle: README-SPEC.md#9) – ✔ erledigt
4. Eingangsbereich als stets freien Gang modellieren (Quelle: README.md#41-45; README-SPEC.md#15) – ✔ erledigt
5. Rand- und Rastergrenzen (`x+w≤77`, `y+h≤50`) absichern (Quelle: README-SPEC.md#36) – ✔ erledigt
6. Nichtüberlappung durch Lage-Binärvariablen erzwingen (Quelle: README-SPEC.md#19) – ✔ erledigt
7. Mindest‑Gangbreite ≥4 überall sicherstellen (Quelle: README.md#91-98; README-SPEC.md#21) – ✔ erledigt
8. Gang-Konnektivität via Flussmodell herstellen (Quelle: README-SPEC.md#23) – ✔ erledigt
9. Pro Raum mindestens eine Tür zum Gang anlegen (Quelle: README.md#73-84; README-SPEC.md#25) – ✔ erledigt
10. Zielfunktion zur Maximierung der Raumfläche definieren (Quelle: README-SPEC.md#11) – ✔ erledigt
11. Solver starten und bei Abbruch beste Lösung sichern (Quelle: README-SPEC.md#28) – ✔ erledigt
12. `solution.json` generieren (Quelle: README-SPEC.md#44-52) – ✔ erledigt
13. `solution.png` rendern (Quelle: README-SPEC.md#55) – ✔ erledigt
14. `validation_report.json` schreiben (Quelle: README-SPEC.md#57-81) – ✔ erledigt
15. CLI‑Schalter implementieren (`--log-level`, `--log-format`, `--log-file`, `--progress`, `--progress-interval`, `--seed`, `--time-limit`, `--threads`) (Quelle: README.md#409-416) – ✔ erledigt
16. Strukturierte Logs und Progress-Anzeige entwickeln (Quelle: README.md#418-439; README-SPEC.md#83-91) – ✔ erledigt
17. Sauberen Abbruch und optionale Checkpoints unterstützen (Quelle: README.md#447-450; README-SPEC.md#91) – ✔ erledigt
18. Validierung aller Muss-Kriterien implementieren (Quelle: README.md#15-20; README-SPEC.md#57-77) – ✔ erledigt
19. Tests für Geometrie und Validierung erweitern (Quelle: AGENTS.md#17; README.md#475-479) – ✔ erledigt
20. Prozessstarter-Skript `start_process.py` mit Standardpfaden bereitstellen – ✔ erledigt
21. Datenmodelle `RoomPlacement` und `SolveParams` ergänzen (Quelle: Benutzeranweisung) – ✔ erledigt
22. Fortschrittsmodul für Heartbeat implementieren (Quelle: Benutzeranweisung) – ✔ erledigt
23. JSON-Schema für `solution.json` bereitstellen (Quelle: Benutzeranweisung) – ✔ erledigt
24. `rooms.yaml` auf Einzeilenformat standardisieren – ✔ erledigt
25. Validator um diagonale Engstellen und Türengpässe erweitern – ✔ erledigt
26. Fortschrittsdaten mit Bound/Gap/Vars/Constraints/Mem ergänzen – ✔ erledigt
27. `requirements.txt` mit Abhängigkeiten erstellen (Quelle: Benutzeranweisung) – ✔ erledigt
28. Anleitung für Nutzung in Google Colab (GUIDE.md) erstellen – ✔ erledigt
29. Prüfroutine `AGENTS_Pruefung.md` hinzufügen – ✔ erledigt

## Parameter- & Optionsreferenz
- Rastergröße `GRID_W=77`, `GRID_H=50` (Quelle: README.md#115-118)
- Eingang `x1=56`, `x2=60`, `y1=40`, `y2=50` (Quelle: README.md#41-45)
- Korridorfenster `corridor_win=4` (Quelle: Benutzeranweisung)
- Iterative Cuts `max_cut_rounds=10` (Quelle: Benutzeranweisung)
- CLI: `--grid-w <int>`, `--grid-h <int>` (Quelle: Benutzeranweisung)
- CLI: `--entr-x1 <int>`, `--entr-w <int>`, `--entr-y1 <int>`, `--entr-len <int>` (Quelle: Benutzeranweisung)
- CLI: `--threads <n>` (Quelle: README.md#416)
- CLI: `--seed <int>` (Quelle: README.md#416)
- CLI: `--time-limit <sek>` (Quelle: README.md#416)
- CLI: `--max-cut-rounds <n>` (Quelle: Benutzeranweisung)
- CLI: `--progress {auto,json,off}` (Quelle: README.md#414)
- CLI: `--progress-interval <sek>` (Quelle: README.md#415)
- CLI: `--checkpoint <sek>` (Quelle: README.md#447-450)
- CLI: `--validate-only` (Quelle: Benutzeranweisung)
- Ausgaben: `solution.json`, `solution.png`, `validation_report.json` (Quelle: AGENTS.md#14)
 - CLI: `--log-level`, `--log-format`, `--log-file` (Quelle: README.md#409-416)

## Status
| Aufgabe                                     | Status | Letzte Änderung        | Verantwortlich |
|---------------------------------------------|:------:|------------------------|----------------|
| Prozessdokumentation aufsetzen              | ✔     | 2025-08-03T22:05:52Z   | Agent          |
| Algorithmus zur Raumverteilung implementieren| ✔     | 2025-08-05T00:00:00Z   | Agent          |
| Logging & Fortschrittsanzeige ausbauen      | ✔     | 2025-08-07T00:00:00Z   | Agent          |
| Tests erweitern                             | ✔     | 2025-08-07T00:00:00Z   | Agent          |
| Prozessstarter-Skript hinzufügen            | ✔     | 2025-08-04T00:00:00Z   | Agent          |
| Datenmodelle für RoomPlacement/SolveParams ergänzen | ✔     | 2025-08-04T01:00:00Z   | Agent          |
| Visualisierung für solution.png implementieren | ✔     | 2025-08-04T00:12:49Z   | Agent          |
| JSON-Schema für solution.json bereitstellen | ✔     | 2025-08-06T01:00:00Z   | Agent          |
| Validator um diagonale Engstellen/Türengpässe erweitern | ✔     | 2025-08-08T00:00:00Z   | Agent          |
| Fortschrittsdaten mit Bound/Gap/Vars/Constraints/Mem erweitern | ✔     | 2025-08-08T00:00:00Z   | Agent          |
| `requirements.txt` für Abhängigkeiten erstellen | ✔     | 2025-08-10T02:00:00Z   | Agent          |
| Prüfroutine `AGENTS_Pruefung.md` hinzufügen | ✔     | 2025-08-11T01:00:00Z   | Agent          |
| Dokumentation für Google-Colab-Nutzung schreiben | ✔     | 2025-08-10T02:00:00Z   | Agent          |

## Change-Log
- 2025-08-03T21:25:34Z – Initiale Prozessbeschreibung erstellt
- 2025-08-03T21:40:00Z – CP-SAT-Variablen und Randbedingungen implementiert
- 2025-08-03T22:05:52Z – Zehn-Schritte-Ablauf und Idempotenzregeln ergänzt
- 2025-08-04T00:00:00Z – Prozessstarter-Skript hinzugefügt
- 2025-08-04T01:00:00Z – Datenmodelle für RoomPlacement und SolveParams ergänzt
- 2025-08-04T02:00:00Z – Hilfsfunktionen für Rasteroperationen und Tests ergänzt
- 2025-08-04T03:00:00Z – Fortschrittsmodul mit Heartbeat und Abschluss implementiert
- 2025-08-04T00:12:49Z – Visualisierung mit Raster, Farben und Türen ergänzt
- 2025-08-04T00:24:03Z – Validator um 4×4-Gangprüfung und Türvalidierung erweitert
- 2025-08-05T00:00:00Z – CP-SAT-Solver mit Tür- und Konnektivitäts-Cuts implementiert
- 2025-08-06T00:00:00Z – CLI um Grid- und Eingang-Parameter sowie Validierungsmodus erweitert
- 2025-08-06T01:00:00Z – `rooms.yaml` auf Einzeilenformat gebracht und Lösungsschema ergänzt
- 2025-08-06T02:00:00Z – CLI-Tests für Versionsausgabe und Minimalablauf hinzugefügt
- 2025-08-07T00:00:00Z – Logging, Progress, Checkpoint-Unterstützung und zusätzliche Validierungs-Tests ergänzt
- 2025-08-08T00:00:00Z – Validator um diagonale Engstellen/Türengpässe erweitert und Fortschrittsstatistiken ergänzt
- 2025-08-09T00:00:00Z – requirements.txt mit Laufzeit- und Prüf-Abhängigkeiten ergänzt
- 2025-08-10T00:00:00Z – GUIDE.md mit Colab-Installationsanleitung ergänzt
- 2025-08-10T02:00:00Z – requirements auf Colab-Version abgestimmt und GUIDE aktualisiert
- 2025-08-11T00:00:00Z – Prüfroutine AGENTS_Pruefung.md hinzugefügt
- 2025-08-11T01:00:00Z – Prüfroutine in AGENTS_Pruefung.md vervollständigt
- 2025-08-11T02:00:00Z – Codeformatierung und Lintingfehler bereinigt
