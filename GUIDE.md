# GUIDE: Nutzung in Google Colab (Free Plan)

## Installation

1. Neues Notebook auf [Google Colab](https://colab.research.google.com) anlegen.
2. Repository klonen und Arbeitsverzeichnis wechseln:
   ```bash
   !git clone <REPO_URL>
   %cd Wands
   ```
3. Abhängigkeiten aus der gepflegten `requirements.txt` installieren:
   ```bash
   !pip install -r requirements.txt
   ```

## Start über die CLI

Das Programm kann direkt über `python -m wands` gestartet werden. Alle Ausgaben werden in die angegebenen Dateien geschrieben.

Nachfolgend sind Beispielbefehle für drei Laufzeitlimits (1 min, 10 min, 30 min) angegeben. Für jede Laufzeit gibt es eine Variante mit minimaler und maximaler Rechenlast.

### 1 Minute

**Minimale Rechenlast**
```bash
!python -m wands --config rooms.yaml --out-json solution.json --out-png solution.png --validate validation_report.json --time-limit 60 --threads 1 --progress off
```

**Maximale Rechenlast**
```bash
!python -m wands --config rooms.yaml --out-json solution.json --out-png solution.png --validate validation_report.json --time-limit 60 --threads 2 --progress auto
```

### 10 Minuten

**Minimale Rechenlast**
```bash
!python -m wands --config rooms.yaml --out-json solution.json --out-png solution.png --validate validation_report.json --time-limit 600 --threads 1 --progress off
```

**Maximale Rechenlast**
```bash
!python -m wands --config rooms.yaml --out-json solution.json --out-png solution.png --validate validation_report.json --time-limit 600 --threads 2 --progress auto
```

### 30 Minuten

**Minimale Rechenlast**
```bash
!python -m wands --config rooms.yaml --out-json solution.json --out-png solution.png --validate validation_report.json --time-limit 1800 --threads 1 --progress off
```

**Maximale Rechenlast**
```bash
!python -m wands --config rooms.yaml --out-json solution.json --out-png solution.png --validate validation_report.json --time-limit 1800 --threads 2 --progress auto
```

Die erzeugten Dateien `solution.json`, `solution.png` und `validation_report.json` erscheinen im aktuellen Arbeitsverzeichnis und können über das Dateimenü von Colab heruntergeladen werden.
