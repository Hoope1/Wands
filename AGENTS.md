# AGENTS Instructions

## Scope
Diese Vorgaben gelten für das gesamte Repository.

## Nutzung von Prozess.md
- Prozess.md ist die einzige verbindliche Prozess- und Wissensquelle.
- Vor jeder Änderung alle README*/AGENTS*-Dateien prüfen und Prozess.md aktualisieren.
- Aufgabenliste mit ✔/✖ pflegen, Status-Tabelle und Change-Log bei jeder Aktualisierung anpassen.
- Externe Tools lesen Parameterreferenz und Aufgabenliste zur Steuerung von Linting, Tests und Deployment.
- Die Prüfroutine in `AGENTS_Pruefung.md` ist nach jedem Abschluss vollständig auszuführen; Fehler sind zu beheben und die Prüfung zu wiederholen, bis keine Fehler mehr auftreten.

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
Keine

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
- 2025-08-06: CLI um Grid- und Eingang-Parameter sowie Validierungsmodus erweitert.
- 2025-08-07: Logging, Fortschrittsanzeige, Checkpoints und zusätzliche Tests ergänzt.
- 2025-08-08: Validator um diagonale Engstellen/Türengpässe erweitert, Fortschrittsdaten aus Solver ergänzt.
- 2025-08-09: requirements.txt mit Laufzeit- und Prüf-Abhängigkeiten ergänzt.
- 2025-08-10: GUIDE.md mit Colab-Installations- und Startanleitung ergänzt.
- 2025-08-11: AGENTS_Pruefung.md mit Prüfroutine hinzugefügt.
- 2025-08-13: Solver setzt Seed- und Thread-Parameter.
- 2025-08-14: Solver verbindet Korridorinseln über Pfad-Cut.
- 2025-08-16: Validator verbietet Außentüren standardmäßig, CLI-Schalter hinzugefügt.
