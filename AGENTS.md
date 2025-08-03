# AGENTS Instructions

## Scope
These instructions apply to the entire repository.

## Ziel
Setze die Anforderungen der README.md vollständig in Python-Code um. Jede Bearbeitung dieses Repositories soll diese AGENTS.md überarbeiten und verfeinern.

## Arbeitsweise
- **README.md nicht löschen oder kürzen.** Ergänze stattdessen einen Abschnitt *Fortschritt* und trage dort alle erledigten Schritte ein.
- **AGENTS.md bei jedem Durchgang aktualisieren.** Führe neue Erkenntnisse, offene Punkte und Verbesserungen auf.
- **Python 3.10+** verwenden. Achte auf PEP8, Typannotationen und klare Modulstruktur.
- Implementiere einen Algorithmus/Heuristik zur optimalen Raumverteilung gemäß README.
- Das Programm muss `solution.json`, `solution.png` und `validation_report.json` erzeugen.
- CLI-Schalter und Logging wie in Abschnitt 16 der README beschrieben umsetzen.
- Eine Validierung aller Muss-Kriterien (Gangbreite, Türen, Konnektivität etc.) ist Pflicht.
- Tests hinzufügen und `pytest` vor jedem Commit ausführen.
- Commit-Messages auf Deutsch, prägnant und im Imperativ.

## Fortschrittspflege
- Nach jedem Feature: README unter *Fortschritt* ergänzen.
- Frühere Einträge niemals entfernen.


## Offene Punkte
- Algorithmus zur Raumverteilung fehlt.
- Validator deckt noch nicht alle Spezialfälle ab (z. B. diagonale Engstellen).
- Logging und Fortschrittsanzeige gemäß Spezifikation ausbauen.
- Tests für Geometrie und Validierung erweitern.

## Aktualisierung
- 2024-06-02: Grundgerüst (CLI, Konfigurationsladen, Dummy-Solver, Visualisierung, einfache Validierung) erstellt.
- 2024-06-03: Validator erweitert (Überschneidungen, Gangbreite, Türen, Erreichbarkeit) und Tests ergänzt.
