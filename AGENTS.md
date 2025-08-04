# AGENTS Instructions

## Scope
Diese Vorgaben gelten für das gesamte Repository.

## Nutzung von Prozess.md
- Prozess.md ist die einzige verbindliche Prozess- und Wissensquelle.
- Vor jeder Änderung alle README*/AGENTS*-Dateien prüfen und Prozess.md aktualisieren.
- Aufgabenliste mit ✔/✖ pflegen, Status-Tabelle und Change-Log bei jeder Aktualisierung anpassen.
- Externe Tools lesen Parameterreferenz und Aufgabenliste zur Steuerung von Linting, Tests und Deployment.

## Backup-Agenten
| Disziplin            | Primärtool | Backup-Tool | Wechselkriterium                         |
|----------------------|-----------|-------------|-----------------------------------------|
| Linting & Formatierung| ruff      | flake8      | wenn ruff nicht verfügbar oder fehlschlägt |
| Importsortierung     | ruff (I)  | isort       | wenn ruff‑I nicht läuft                 |
| Typprüfung           | pyright   | mypy        | bei Ausfall oder Fehler von pyright     |
| Tote-Code-Analyse    | vulture   | ruff F401   | wenn vulture nicht nutzbar              |
| Komplexitätsanalyse  | xenon     | radon       | wenn xenon nicht nutzbar                |

## Arbeitsweise
- README.md nicht löschen oder kürzen; Fortschritt dort dokumentieren.
- AGENTS.md bei jedem Durchgang aktualisieren.
- Python 3.10+ nutzen, PEP8, Typannotationen und klare Modulstruktur beachten.
- Algorithmus/Heuristik zur optimalen Raumverteilung implementieren.
- Programm erzeugt `solution.json`, `solution.png` und `validation_report.json`.
- CLI-Schalter und Logging gemäß README Abschnitt 16 umsetzen.
- Muss-Kriterien (Gangbreite, Türen, Konnektivität etc.) validieren.
- Tests hinzufügen und `pytest` vor jedem Commit ausführen.
- Commit-Messages auf Deutsch, prägnant und im Imperativ.

## Fortschrittspflege
- Nach jedem Feature README unter *Fortschritt* ergänzen.
- Frühere Einträge niemals entfernen.

## Offene Punkte
- Validator deckt noch nicht alle Spezialfälle ab (z. B. diagonale Engstellen).
- Logging und Fortschrittsanzeige gemäß Spezifikation ausbauen.
- Tests für Geometrie und Validierung erweitern.

## Aktualisierung
- 2024-06-02: Grundgerüst (CLI, Konfigurationsladen, Dummy-Solver, Visualisierung, einfache Validierung) erstellt.
- 2024-06-03: Validator erweitert (Überschneidungen, Gangbreite, Türen, Erreichbarkeit) und Tests ergänzt.
- 2025-08-03: Prozessdokumentation, Pre-Commit-Konfiguration und Pyproject ergänzt.
- 2025-08-03: Solver um CP-SAT-Grundgerüst und Randbedingungen erweitert.
- 2025-08-04: Prozessstarter `start_process.py` eingeführt.
- 2025-08-04: Datenmodelle `RoomPlacement` und `SolveParams` ergänzt.
- 2025-08-04: Hilfsfunktionen für Rasteroperationen hinzugefügt.
- 2025-08-04: Fortschrittsmodul mit Heartbeat und Abschluss implementiert.
- 2025-08-04: Visualisierung mit Raster, Farben und Türen erweitert.
- 2025-08-04: Validator auf Grid-Aufbau, 4×4-Breitenprüfung und Türlogik aktualisiert.
- 2025-08-05: CP-SAT-Solver mit Tür- und Konnektivitäts-Cuts implementiert.
