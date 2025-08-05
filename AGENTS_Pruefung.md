# Prüfroutine

Die folgende Reihenfolge ist nach jedem Arbeitsschritt vollständig auszuführen. Tritt ein Fehler auf, ist er zu beheben und die Prüfroutine zu wiederholen.

1. `python -m docformatter --black --in-place --recursive .`
2. `python -m ruff check --select I --fix .`
3. `python -m ruff format .`
4. `python -m ruff check .`
5. `python -m pydocstyle .`
6. `python -m mypy .`
7. `python -m vulture .`
8. `python -m radon cc -s -a .`
9. `python -m radon mi -s .`
10. *(optional)* `python -m nbqa ruff --fix <notebooks>`
11. *(optional)* `python -m nbqa pydocstyle <notebooks>`
12. `pytest`

Fallback-Tools (nur bei Ausfall der Hauptwerkzeuge):
- Formatter: Black → YAPF → autopep8
- Linter: Flake8(+WPS) → Pylint → Prospector
- Importe: isort (`profile = "black"`)
- Typprüfung: Pyright → Pyre → pytype
- Metriken: Xenon als Gate über Radon
