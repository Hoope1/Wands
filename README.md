# Wands
Mad Games Tycoon 2 Room Suggestion  **vollständige Aufgaben- & Spezifikationsbeschreibung** (auf Deutsch) (Algorithmus/Heuristik/Library frei wählbar) auskommt und alle Informationen enthält.
Die einzige Vorgabe: **Python** als Implementationssprache.

grundstueck_77x50_eingang_4x10.png ist im Hauptverzeichnis, so sieht das Grundstück aus, beim Beginn!

---
Vor diesen punkten immer README-SPEC.md und AGENT_AUFTRAG.md lesen!
Bitte nach jeder Änderung die Prüfroutine in `AGENTS_Pruefung.md` vollständig ausführen und bei Fehlern wiederholen.

Der komplette Prozess lässt sich mit Standardpfaden über das Skript
``start_process.py`` starten:

```bash
python start_process.py --progress off
```

Weitere unbekannte Parameter werden an die interne CLI von `wands`
weitergereicht.

## Kurz-Spezifikation

- Raster: **77×50** Zellen.
- Eingang: Block **x=56..59**, **y=40..49** (4×10) gehört immer zum Gang.
- Gang: Komplement aller Räume, **Breite ≥4** nach L∞ (**4×4-Fenster** vollständig Gang).
- Konnektivität: genau **eine Gangkomponente** in **4-Nachbarschaft** inklusive Eingang.
- Türen: liegen auf einer **Raumwand**, **nicht in Ecken**, öffnen in den Gang, sind vom Eingang aus erreichbar und liegen **nicht am Außenrand** (außer am Eingang).
- Räume: **rechteckig**, **wand-an-wand** erlaubt, **keine Überlappung**, vollständig im 77×50‑Grid.
- Primäres Ziel: **Maximiere die Gesamtfläche aller Räume**.
- Ausgaben: `solution.json`, `solution.png`, `validation_report.json`.
- CLI-Beispiel:
  ```bash
  python -m wands --config rooms.yaml --out-json solution.json --out-png solution.png --validate validation_report.json --seed 1
  ```
- Abhängigkeiten: **Python 3.10+**, `ortools`, `Pillow`, `PyYAML`.

## 1) Ziel & Problemkurzbeschreibung

Entwirf ein Python-Programm, das für ein rechteckiges, diskretes Grundstück (Gitternetz) eine **optimale Raumverteilung** berechnet.
„Optimal“ heißt: **maximiere** die Raumfläche (bzw. eine parametrisierbare Zielgröße), **unter Einhaltung aller harten Bedingungen**:

* **Gang = alles, was nicht Raum ist**, und der Gang ist **überall mindestens 4 Zellen breit**.
* **Konnektivität**: Sämtliche Gangbereiche bilden **eine zusammenhängende Fläche**, die den **fixen Eingangsbereich** einschließt.
* **Erreichbarkeit**: **Jeder Raum** besitzt mindestens **eine Tür**, die **in den Gang** führt; **durch** Räume zu gehen ist **verboten**.
* **Türen** liegen **auf Raumwänden**, **nicht** in Ecken.
* **Räume** sind achsenparallele Rechtecke, dürfen **wand-an-wand** aneinander liegen (gemeinsame Wand erlaubt), **überlappen** aber nicht.
* **Eingangsblock** ist **fix** vorgegeben.

Die konkrete **Algorithmik** (Exact/CP-SAT/ILP/Flow/Graph/Heuristik) ist **frei**. Wichtig ist die **Korrektheit** bzgl. der formalen Bedingungen.

---

## 2) Raster, Koordinaten, Topologie

* **Rastergröße:** 77 × 50 Zellen; jede Zelle ist 1×1.
* **Koordinatenlinien:** ganzzahlige Gitterlinien; kontinuierlicher Bereich $[0,77] \times [0,50]$.
* **Zellindizes:**

  * Spalten $x$ als Zellen $0,1,\dots,76$ ⇒ Zelle $i$ belegt $[i,i+1]$.
  * Zeilen $y$ als Zellen $0,1,\dots,49$ ⇒ Zelle $j$ belegt $[j,j+1]$.
* **Ecken Grundstück:** unten-links $(0,0)$, oben-rechts $(77,50)$.
* **Zelle $(i,j)$:** belegt Rechteck $[i,i+1]\times[j,j+1]$.

---

## 3) Fester Eingang

* **Lage (obligatorisch, fix):**

  * **x = 56..59**, **y = 40..49** (also 4×10 Zellen).
  * Oberkante liegt auf der Gitterlinie **$y = 50$** (direkt an der oberen Grundstücksgrenze).
* **Bedeutung:** Dieser 4×10-Block ist **immer Gang**, niemals Raum, und Teil der **zusammenhängenden Gangfläche**.

---

## 4) Räume

* **Definition:** Ein Raum ist ein achsenparalleles **Rechteck** mit ganzzahligen Grenzen:

  $$
  R=[a,b)\times[c,d),\quad 0 \le a < b \le 77,\ \ 0 \le c < d \le 50.
  $$

  Der Raum belegt alle Zellen $(i,j)$ mit $i\in\{a,\dots,b-1\}$, $j\in\{c,\dots,d-1\}$.
* **Zulässig:** Räume dürfen **wand-an-wand** liegen (gemeinsame Trennwände sind erlaubt).
* **Unzulässig:** Räume dürfen sich **nicht überlappen** und **nicht** in den **Eingangsblock** hineinragen.
* **Anzahl & Typen:** Die Menge/Arten der Räume ist **parametrisierbar**.
  Bitte **konfigurierbar** anlegen (siehe Abschnitt *Konfiguration*):

  * Raum-Typname (z. B. „Büro“, „Entwicklung“, …)
  * **min/max Breite** $[w_{\min}, w_{\max}]$ (in Zellen)
  * **min/max Höhe** $[h_{\min}, h_{\max}]$ (in Zellen)
  * **max. Stückzahl** oder „beliebig“
  * optionale Präferenzen (z. B. Nähe zum Eingang, Nachbarschaften), die **nur** als **weiche Ziele** wirken (niemals harte Regeln brechen).

---

## 5) Türen

* **Pflicht pro Raum:** mindestens **eine Tür**.
* **Lage:** Eine Tür liegt **auf genau einem Wandsegment** des Raums und hat **Länge 1** (entlang einer Gitterkante).
* **Nicht in Ecken:** Tür darf **nicht** den Schnittpunkt zweier Wände (Ecke) belegen.
* **Tür → Gang:** Direkt „außerhalb“ dieses Wandsegments muss eine **Gangzelle** liegen (also die Tür öffnet **in den Gang**, nicht in einen Raum).
* **Keine Raum-Durchreiche:** Es ist **verboten**, durch Räume zu gehen, um einen anderen Raum zu erreichen. Alle Erreichbarkeit verläuft **ausschließlich** über Gangzellen.
* **Keine Außentüren:** Türen dürfen **nicht** direkt am Außenrand liegen – einzig der feste Eingang bildet die Ausnahme.

**Formale Skizze (Türprüfung, exemplarisch):**

* **Linke Wand:** Türsegment auf $\{x=a\} \times [u,u+1]$ mit $c < u < d-1$ und **Gangzelle** bei $(a-1, u)$.
* **Rechte Wand:** Türsegment auf $\{x=b\} \times [u,u+1]$ mit $c < u < d-1$ und **Gangzelle** bei $(b, u)$.
* **Unterkante:** Türsegment auf $[v,v+1] \times \{y=c\}$ mit $a < v < b-1$ und **Gangzelle** bei $(v, c-1)$.
* **Oberkante:** Türsegment auf $[v,v+1] \times \{y=d\}$ mit $a < v < b-1$ und **Gangzelle** bei $(v, d)$.
  (Grenzfälle außerhalb des Grundstücks natürlich ausschließen.)

---

## 6) Gang (Definition, Breite, Konnektivität)

* **Definition:** **Gang** ist das **Komplement** der Räume auf dem Raster (inkl. des festen Eingangsblocks). **Jede Zelle** gehört **entweder** zu einem Raum **oder** zum Gang, **nie** zu beidem.
* **Mindestbreite 4 (überall):**

  * „Überall“ bedeutet **in jeder Geometrievariante** (gerade, Kurve, Kreuzung, Engstelle, vor Türen, zwischen gegenüberliegenden Wänden).
  * Praktisch kann man das z. B. als **L∞-Dicke ≥ 4** interpretieren: An **keiner Stelle** darf der Gang auf 1–3 Zellen Breite zusammenschrumpfen.
* **Konnektivität:** Die **gesamte Gangfläche** bildet **eine zusammenhängende Komponente** (4-Nachbarschaft) und **enthält** den **Eingangsblock**.
* **Erreichbarkeit:** Von **jedem** Türsegment existiert **ein Gangpfad** (4-Nachbarschaft) zum Eingangsblock.
* **Außenkanten:** Es gibt **keine Pflicht**, überall am Grundstücksrand Gang zu haben; Räume dürfen bis an den Rand reichen, sofern dadurch **nirgendwo** Gangbreite < 4 entsteht oder die **Konnektivität** verloren geht.

---

## 7) „So werden Räume erstellt“ (Benutzerlogik)

* Der/die Benutzer\*in „zieht“ einen rechteckigen Raum über freie Zellen (wie in vielen Aufbau-Spielen): **Achsenparalleles Rechteck**.
* Türen werden anschließend **auf einer Wand** des Raums platziert (nicht in der Ecke).
* Räume **dürfen aneinandergrenzen** (Wand-an-Wand) — aber **Türen** dürfen **nicht** in Raum-Trennwände münden (immer in den Gang).
* **Alles** was nicht als Raum markiert ist, gilt **per Definition als Gang** (unter Einhaltung Breite ≥ 4 und Konnektivität).

*(Diese Benutzerlogik ist nur die fachliche Interpretation; die Programmlogik kann davon unabhängig sein, solange das Ergebnis dieselben Regeln erfüllt.)*

---

## 8) Konfiguration (eingabeseitig, zwingend bereitzustellen)

1. **Grid-Parameter** (Standard = oben genannt, aber als Parameter modellieren):

   * `GRID_W = 77`, `GRID_H = 50`.
2. **Eingang** (fix, aber trotzdem konfigurierbar, falls später andere Maps):

   * `ENTRANCE_X_START = 56`, `ENTRANCE_WIDTH = 4`
   * `ENTRANCE_Y_BOTTOM = 40`, `ENTRANCE_HEIGHT = 10`.
3. **Raumkatalog** (JSON/TOML/YAML): Liste von Raum-Typen; für jeden Typ:

   * Name/ID
   * `w_min, w_max, h_min, h_max` (ganzzahlig, ≥1)
   * `max_count` oder None
   * optionale **weiche** Präferenzen (Adjazenzen, Distanzen).
4. **Zieldefinition**:

   * Primär: **Maximiere Raumfläche** (oder Summe aus Typ-Gewichten × Fläche).
   * Sekundär (optional): Präferenzen als **weiche** Terme (mit Gewichten).
5. **Ausgabeformate**: JSON/CSV/PNG (s. Abschnitt 10).

---

## 9) Harte Validierungskriterien (MUSS)

Ein Lösungskandidat ist **nur gültig**, wenn **alle** Punkte erfüllt sind:

1. **Disjunktheit:** Räume überlappen **nicht**.
2. **Komplement:** Jede Zelle gehört **genau einer** Kategorie: **Raum** oder **Gang** (Eingang ⊂ Gang).
3. **Mindestbreite 4:** Der Gang ist **überall** mindestens **4 Zellen** breit (keine Engstellen, auch nicht an Kurven/Kreuzungen/vor Türen).
4. **Konnektivität:** Die Gangzellen bilden **eine** zusammenhängende Komponente (4-Nachbarschaft), die den **Eingangsblock** enthält.
5. **Türregeln:**

   * Pro Raum ≥1 Tür, **nicht** in Ecken.
   * Tür öffnet **in den Gang** (die Nachbarzelle jenseits der Wand ist Gang).
   * **Keine** Tür auf gemeinsamen Raum-Trennwänden.
6. **Randbedingungen:** Alle Räume liegen **vollständig** im Raster; Eingangsblock bleibt **frei** (Gang).
7. **Erreichbarkeit:** Für **jede Tür** existiert ein Gangpfad zum Eingangsblock.

---

## 10) Erwartete Ausgaben (Dateiformate & Visualisierung)

* **Maschinenlesbar (Pflicht)**:

  * `solution.json` mit

    * `rooms: [ {id, type, x, y, w, h, doors:[{side, pos_x, pos_y}]}, … ]`
    * `corridor_mask` optional (booleanes 2D-Array) **oder** weglassen und als Komplement ableiten
    * `entrance: {x1:56, x2:60, y1:40, y2:50}`
    * `objective: {room_area_total, soft_scores...}`
* **Bild (Pflicht)**:

  * `solution.png` als Rasterdarstellung

    * Räume farbig gefüllt, Türen als kurze Striche auf Wänden,
    * Gang hell hinterlegt,
    * Eingangsblock deutlich hervorgehoben,
    * Achsen mit Koordinaten 0..77 (x) und 0..50 (y).
* **Validierungsprotokoll**:

  * Text/JSON (`validation_report.json`): alle Checks aus §9 inkl. „pass/fail“ und ggf. kurzer Begründung.

---

## 11) Testfälle (minimal/akzeptanz)

1. **Nur Eingang**: Keine Räume. Ergebnis: Gang = ganzes Feld, Breite≥4 überall? (Es darf Engstellen <4 geben? → Nach Spezifikation **nein**; also ohne Räume ist das triviale „alles Gang“ zulässig, da Breite überall ≥4: in einem leeren Feld ist Breite unkritisch, aber der Anspruch „überall ≥4“ gilt weiterhin — bitte so evaluieren, dass keine künstlichen Engstellen entstehen.)
2. **Ein langer Hotelgang** von Eingang nach unten, Zimmer links/rechts, Türen zum Gang → **gültig**.
3. **Tür direkt in Sackgasse <4** → **ungültig**.
4. **Tür in Ecke** → **ungültig**.
5. **Zwei Räume mit 1-Zellen-Spalt (Gang <4)** → **ungültig**.
6. **Isolierte Ganginsel** ohne Verbindung zum Eingang → **ungültig**.
7. **Raum ragt in Eingangsblock** → **ungültig**.

*(Gern zusätzliche Random-Tests.)*

---

## 12) API-/CLI-Vorschlag (neutral, nicht bindend)

* `python solver.py --config rooms.yaml --export solution.json --png solution.png`
* Optional: `--seed`, `--time_limit`, `--objective weights.json`, `--validate-only solution.json`, `--show`.

*(Nur als Orientierung; Implementierung frei.)*

---

## 13) Anforderungen an Code-Qualität

* **Nur Python.** Bibliotheken frei (z. B. OR-Tools, NetworkX, NumPy, Matplotlib, PuLP, Pyomo, …).
* Saubere Modulstruktur, Typannotationen, kurze README mit Startanleitung.
* Klare Trennung **Modell** (Constraints/Ziel) vs. **Validierung** vs. **Visualisierung**.
* Reproduzierbarkeit (Seeds, Versionshinweise).
* Keinerlei Abhängigkeit von dieser Chat-Konversation außer den **formalen Regeln**.

---

## 14) Was **nicht** festgelegt wird (um nicht zu beeinflussen)

* Kein Zwang zu CP-SAT/ILP/Flow — **freie** Wahl der Algorithmen/Heuristiken.
* Keine Vorgabe, ob zuerst Räume erzeugt oder Gang „ausgeschnitten“ wird — Hauptsache, das **Endergebnis** erfüllt alle harten Regeln.
* Keine feste Gewichtung weicher Ziele (falls genutzt) — diese sind **optional** und müssen die **harten** Regeln stets **respektieren**.

---

## 15) Anhänge & Quellen

* **Referenzbild mit Eingang & Raster:** `sandbox:/mnt/data/1000026908.png` (zeigt 77×50-Raster, Eingang als 4×10-Fläche **oben** bei x=56..59, y=40..49).
* **Diese Spezifikation** enthält **alle** Anforderungen aus dem Chat:

  * Raster/Koordinaten,
  * fester Eingangsblock,
  * Räume als Rechtecke (wand-an-wand erlaubt),
  * Türen auf Wänden (nicht in Ecken),
  * Tür → Gang (nie Raum),
  * Gang = Komplement der Räume, **Breite ≥4** überall,
  * Gang **zusammenhängend** und **mit Eingang verbunden**,
  * Erreichbarkeit jeder Tür **über Gang** (kein Durchgang durch Räume),
  * Optimierung auf **maximale Raumfläche** (oder konfigurierbar).

---

Unten findest du eine **neutrale, vollständige Spezifikation** inkl. **Raster/Koordinaten**, **fester Eingang**, **Raumkatalog mit Größen & Anzahl**, **Tür-/Wandregeln**, **Gang-Definition (Komplement, ≥4 breit, verbunden)** sowie **Zielsetzung**. Außerdem sind die **relevanten Konstanten** aus dem Code aufgeführt. (Python ist Pflicht, alles andere frei wählbar.)

> **Referenzbild (Pflichtbeilage):**
> `sandbox:/mnt/data/1000026908.png`
> Zeigt das 77×50-Gitternetz mit dem **Eingang** als **4×10-Fläche** oben (x=56..59, y=40..49).

---

## 1) Spielfeld, Koordinaten, Eingang

* **Raster**: 77 (x) × 50 (y) Zellen à 1×1; Gitterlinien bei ganzen Zahlen $[0,77]×[0,50]$.
  **Code-Parameter:** `GRID_W, GRID_H = 77, 50`.&#x20;
* **Fixer Eingangsblock (immer Gang):**
  **x = 56..59**, **y = 40..49** (Breite 4, Höhe 10; Oberkante bei y=50).
  **Code-Parameter:** `ENTRANCE_X1=56`, `ENTRANCE_W=4`, `ENTRANCE_X2=60`; `ENTRANCE_MIN_LEN=ENTRANCE_MAX_LEN=10`.&#x20;

---

## 2) Räume – Definition, Anzahl, Größen

* **Raumform:** Achsenparallele Rechtecke mit ganzzahligen Grenzen.
* **Zulässig:** Räume dürfen **wand-an-wand** liegen (gemeinsame Wand ok).
* **Unzulässig:** Überlappung; Hineinragen in den Eingangsblock.
* **Türpflicht:** Jeder Raum hat ≥ 1 Tür, **auf einer Raumwand**, **nicht** in Ecken, **öffnet in den Gang** (siehe §3).
* **Katalog & Parametrisierung im Code:** `RoomDef` enthält **Name, Gruppe, bevorzugte Größe (pref\_w×pref\_h), Mindestgröße (min\_w×min\_h), Schrittweiten (step\_w×step\_h), Priorität, Effizienzfaktor**, optional **duplicate\_id** (Kennung für Mehrfach-Instanzen).&#x20;

### 2.1 Raumkatalog (Instanzen)

> *Jede Zeile entspricht **einer** geforderten Instanz. Kategorien mit zwei Einträgen (z. B. „Prod1/Prod2“) bedeuten **2 Räume** desselben Typs.*
> *(Alle Werte in Zellen.)*

| Name        | Gruppe     | bevorzugt (w×h) | min (w×h) | Schritt (w×h) | Priorität | Effizienz | duplicate\_id |
| ----------- | ---------- | --------------: | --------: | ------------: | --------: | --------: | ------------- |
| Dev         | Dev        |            10×8 |       6×6 |           2×1 |        10 |       1.5 | –             |
| QA          | QA         |             9×7 |       6×6 |           1×1 |         9 |       1.4 | –             |
| Research    | Research   |             8×7 |       6×6 |           1×1 |         8 |       1.1 | –             |
| Prod1       | Production |            12×8 |       8×6 |           2×1 |         8 |       1.3 | Prod          |
| Prod2       | Production |            12×8 |       8×6 |           2×1 |         8 |       1.3 | Prod          |
| Storeroom   | Storage    |            10×8 |       6×6 |           1×1 |         9 |       1.4 | –             |
| Graphics    | Studio     |             8×7 |       6×6 |           1×1 |         9 |       1.3 | –             |
| Sound       | Studio     |             8×6 |       6×6 |           1×1 |         9 |       1.3 | –             |
| MoCap       | Studio     |            14×8 |      10×6 |           2×1 |         8 |       1.2 | –             |
| Head Office | Admin      |             6×6 |       4×4 |           1×1 |         9 |       1.3 | –             |
| Marketing   | Marketing  |             8×6 |       6×6 |           1×1 |         7 |       1.1 | –             |
| Support1    | Support    |             8×6 |       6×6 |           1×1 |         6 |       1.0 | Support       |
| Support2    | Support    |             8×6 |       6×6 |           1×1 |         6 |       1.0 | Support       |
| Console     | Console    |            10×7 |       6×6 |           1×1 |         7 |       1.1 | –             |
| Server      | Server     |            10×8 |       6×6 |           1×1 |         8 |       1.2 | –             |
| Training    | Training   |            10×8 |       6×6 |           1×1 |         6 |       1.1 | –             |
| Toilet1     | Facilities |             4×4 |       3×3 |           1×1 |         5 |       0.8 | Toilet        |
| Toilet2     | Facilities |             4×4 |       3×3 |           1×1 |         5 |       0.8 | Toilet        |
| Staff1      | Facilities |             6×5 |       4×4 |           1×1 |         6 |       1.0 | Staff         |
| Staff2      | Facilities |             6×5 |       4×4 |           1×1 |         6 |       1.0 | Staff         |

**Beleg (Auszug aus dem Code):** ROOMS-Einträge inkl. Duplikate, z. B. **Prod1/Prod2**, **Support1/Support2**, **Toilet1/Toilet2**, **Staff1/Staff2**.  &#x20;
Beispiel weiterer Einträge: **Storeroom**, **Graphics**, **Sound**, **MoCap**, **Console**, **Server**. &#x20;

---

## 3) Türen & Wände

* **Pflicht:** Jeder Raum besitzt ≥ 1 Tür.
* **Lage:** Tür liegt **auf einer Raumwand** (nicht in Ecken), entlang **einer** Gitterkante.
* **Öffnung:** Unmittelbar „hinter“ der Tür (jenseits des Wandsegments) muss eine **Gangzelle** liegen.
* **Verboten:** Türen **zwischen** zwei Räumen (Tür muss in den **Gang** führen).
* **Erreichbarkeit:** Von **jeder Tür** muss ein **Gangpfad** (4-Nachbarschaft) zum **Eingang** existieren – **ohne** durch Räume zu gehen.

*(Im Code existieren zusätzlich generelle Tür-Heuristiken/Schranken, z. B. `DOOR_CLUSTER_LIMIT=4`, `K_DOOR=150`, `THRESHOLD_VERY_CLOSE_DOORS=3`, `THRESHOLD_CLOSE_DOORS=8` – diese sind **nicht bindend** für deine Methode, aber als Richtwerte vorhanden.)*&#x20;

---

## 4) Gang – Definition, Mindestbreite, Konnektivität

* **Gang = Komplement** der Räume auf dem Raster (Eingangsblock ⊂ Gang). Jede Zelle ist **entweder** Raum **oder** Gang.
* **Mindestbreite 4 (überall):** In **jeder** Geometrie (gerade Strecken, Kurven, Kreuzungen, vor Türen, zwischen Wänden) darf der Gang **nirgends** schmaler als **4 Zellen** werden (L∞-Dicke ≥ 4).
* **Zusammenhängend:** Die Gangzellen bilden **eine** 4-nachbarschaftliche **Komponente**, die den **Eingangsblock** enthält.
* **Tür-Erreichbarkeit:** Für **jede** Tür existiert ein Gangpfad zum Eingangsblock.
* **Kein Durchgang durch Räume.**

---

## 5) Zielsetzung („Optimale Raumverteilung“)

* **Primärziel:** **Maximiere** die **Raumfläche** (Summe aller Raumzellen).
* **Sekundär (optional):** Du kannst zusätzliche **weiche** Teilziele verwenden (z. B. kompaktes Layout, gewisse Adjazenzen, Symmetrie), **solange** die harten Regeln aus §1–§4 **niemals verletzt** werden.
  *(Im bestehenden Code gibt es gewichtete Boni/Strafen – **nur informativ**: `W_CORRIDOR_AREA=200`, `W_ROOM_EFFICIENCY=5000`, `W_PRIORITY_BONUS=2500`, `W_PROD_STORE_BON=10000`, `W_COMPACT_BONUS=2000`, … – du bist frei, eigene Ziele zu definieren.)* &#x20;

---

## 6) Ein-/Ausgabe & Nachvollziehbarkeit (Vorschlag)

* **Input (konfigurierbar):**

  * Grid-Parameter (Standard 77×50).
  * Fester Eingangsblock (Standard x=56..59, y=40..49).
  * Raumkatalog (Name/Gruppe, bevorzugte & minimale Größe, Schrittweite, Anzahl = Anzahl der Instanzen im Katalog, optional duplicate\_id).
* **Output (maschinell & visuell):**

  * `solution.json` mit allen Räumen (`x,y,w,h`, Türen mit Kantenkoordinate), optional voller Gang-Maske (oder rekonstruierbar als Komplement), **Objective-Werte**.
  * `solution.png` (Rasterdarstellung) mit **Räumen**, **Gang**, **Türen**, **Eingang** (klar markiert).
  * `validation_report.json`: Alle Muss-Kriterien aus §1–§4 mit Pass/Fail.

---

## 7) Implementierungshinweise (neutral)

* **Nur Python**. Bibliotheken frei (z. B. OR-Tools, NetworkX, NumPy, Matplotlib, PuLP/Pyomo …).
* Methodik (exakt/heuristisch/hybride) ist **frei** – wichtig ist **Korrektheit** der Constraints:

  * Komplement **Raum/Gang**,
  * **Breite ≥4** überall,
  * **Konnektivität** (Eingang ↔ alle Türen),
  * **Türregeln** (Wand, nicht Ecke, öffnet in Gang),
  * **Keine** Gang-Unterbrechungen / isolierten Inseln,
  * **Räume** im Raster, **ohne** Überlappung.

---

### Anmerkungen

* Die obigen Parameter sind **wörtlich** aus dem Code übernommen (Raster/Eingang, Raumkatalog inkl. mehrfach geforderter Räume). Beispielsweise belegen **`Prod1`** und **`Prod2`** zwei Produktionsräume, **`Support1/2`** zwei Support-Räume, **`Toilet1/2`** zwei Toiletten, **`Staff1/2`** zwei Personalräume.  &#x20;
* Die **Struktur** der `RoomDef`-Einträge (inkl. bevorzugter/minimaler Größe und Schrittweiten) ist im Code definiert.&#x20;

---


## Ziel (Optimierung)

* **Primärziel:** Maximiere die **Gesamt-Raumfläche** (Summe aller belegten Zellen durch alle geforderten Räume).
* **Nebenbedingungen (müssen erfüllt sein):**

  1. **Eingang (fix, immer Gang):** x=56..59, y=40..49 (4×10, Oberkante y=50).
  2. **Gang = Komplement** aller Räume; **zusammenhängend** (4-Nachbarschaft) und enthält den **Eingang**.
  3. **Gangbreite ≥ 4** an **jeder** Stelle (auch an Kurven/Kreuzungen/vor Türen).
  4. **Räume:** achsenparallele Rechtecke, **wand-an-wand erlaubt**, **keine Überlappung**, vollständig im 77×50-Raster.
  5. **Türen:** pro Raum ≥1 Tür, **auf der Wand**, **nicht in Ecken**, öffnet **in den Gang** (Nachbarzelle außerhalb der Wand ist Gang); **kein** Weg durch Räume.
  6. **Erreichbarkeit:** Von **jeder Tür** existiert ein **Gangpfad** zum Eingangsblock.
  7. **Raumkatalog & Anzahlen/Größen:** gemäß bereitgestellter Liste (min/max, bevorzugte Maße, Schrittweiten; z. T. mehrfach geforderte Instanzen).

*Methodik frei (Python Pflicht); harte Regeln dürfen nie verletzt werden.*

## Ausgaben (Artefakte)

* **`solution.json` (Pflicht):**

  * `rooms`: Liste mit `{id, type, x, y, w, h, doors:[{side, pos_x, pos_y}]}`
  * `entrance`: `{x1:56, x2:60, y1:40, y2:50}`
  * optional `corridor_mask` (oder durch Komplement rekonstruierbar)
  * `objective`: z. B. `{room_area_total: …, …}`
* **`solution.png` (Pflicht):** Visualisierung (siehe unten).
* **`validation_report.json` (Pflicht):** Pass/Fail aller Muss-Kriterien (Breite≥4, Konnektivität, Tür-Regeln, etc.), inkl. kurzer Begründungen.

## Bild (Inhalt von `solution.png`)

* **Raster 77×50** mit Achsenbeschriftung.
* **Eingang** (x=56..59, y=40..49) **klar markiert**.
* **Räume** farbig gefüllt; **Türen** als kurze Striche auf der jeweiligen Wand.
* **Gang** (alles Nicht-Raum) hell hinterlegt; keine Engstellen <4.
* Optional Legende (Farben/Gruppen), Maßstab und Kurzhinweis auf das Ziel.

## Abnahme-Checkliste (kurz)

* ✅ JSON vorhanden & konsistent (Koordinaten integer, innerhalb 77×50).
* ✅ PNG zeigt Eingang, Räume, Gang, Türen korrekt.
* ✅ Validator meldet: *alle Muss-Kriterien erfüllt*.
* ✅ Zielwert (Raumfläche) maximiert bei gegebener Konfiguration.

---

## 16) Laufende Status-/Fortschrittsanzeige & Logging (Pflicht)

**Ziel:** Während Einlesen → Modellaufbau → Optimierung → Validierung → Visualisierung soll die Anwendung **kontinuierlich** und **verlässlich** Auskunft geben über *was gerade passiert*, *wie weit* der Prozess ist und *wie lange es voraussichtlich noch dauert*.

### 16.1 CLI-Schalter (Vorgaben)

* `--log-level {DEBUG,INFO,WARN,ERROR}` (Default: `INFO`)
* `--log-format {text,json}` (Default: `text`)
* `--log-file <pfad>` (optional; sonst stdout)
* `--progress {auto,json,off}` (Default: `auto`) – zeigt eine **fortlaufende Progress-Anzeige**
* `--progress-interval <sek>` (Default: `1`) – Mindestabstand zwischen Status-Updates
* `--checkpoint <sek>` (optional) – speichert periodisch Zwischenstände
* `--seed <int>` (Reproduzierbarkeit), `--time-limit <sek>` (optional), `--threads <n>` (optional)
* `--allow-outside-doors` – erlaubt Türen am Außenrand (standardmäßig verboten)

### 16.2 Strukturierte Logs (Maschinen- & menschenlesbar)

* **Textmodus**: prägnante Zeilen mit Zeitstempel, Phase, Kennzahlen.
* **JSON-Lines** (bei `--log-format json`): protokolliere **Events** als einzelne JSON-Objekte (je Zeile) mit Feldern:

  * `ts`, `phase` ∈ {`start`,`parse`,`build`,`solve`,`incumbent`,`bound`,`gap`,`validate`,`render`,`finish`},
  * `vars`,`constraints`,`nonzeros` (falls verfügbar),
  * `objective_best`,`objective_bound`,`gap` (in %),
  * `runtime_sec`,`eta_sec` (linear/EWMA-Schätzung),
  * `mem_mb`,`threads`, `seed`,
  * ggf. `room_count`,`corridor_area`,`violations` (Liste).
* **Heartbeat**: mindestens alle `--progress-interval` Sekunden ein Fortschritts-Event – auch wenn kein neuer Bestwert kam.

### 16.3 Fortschrittsanzeige (Terminal)

* Eine **dynamische** Zeile (oder `tqdm`-Balken), die u. a. zeigt:

  * **Phase** (Build/Solve/Validate/Render),
  * **Laufzeit** (gesamt & Phase), **ETA**, **aktuelle Iteration/Node/Restart** (falls verfügbar),
  * **Bestes Ziel**, **aktueller Bound**, **GAP**,
  * **Inkrementelle Verbesserungen** (z. B. „+240 Zellen in 12 s“),
  * **Fehlversuche/Infeasible-Cuts** (kumulativ).
* Bei Mehrzeilen-Output (verbose) zusätzlich **Top-5 Constraint-Kategorien** nach Violation-Counts.

### 16.4 Solver-/Algorithmus-Hooks (methodenneutral)

* Stelle **Callbacks**/Listener bereit, die bei **Inkrementen** feuern (neues Incumbent, neuer Bound, Restart, Heuristik-Fund, Cut-Loop, etc.) und die **oben beschriebenen Events** auslösen.
* Falls der gewählte Ansatz diese Hooks nicht nativ bietet, implementiere **periodisches Polling** (mind. alle `--progress-interval` Sekunden) mit robusten Kennzahlen (Nodes, explored states, incumbent, bound).

### 16.5 Checkpoints & Abbruch

* Unterstütze **sauberen Abbruch** (`SIGINT`): schreibe **letzte beste Lösung** + `validation_report.json` + Logabschluss.
* Optional: `--checkpoint <sek>` speichert periodisch *aktuelle beste Lösung* (JSON/PNG) + Log-Snapshot.

### 16.6 Validierungs- und Ergebnis-Logging

* Nach dem Solve:

  * **Validierungsreport** mit **jedem Muss-Kriterium** (Pass/Fail + kurze Begründung).
  * Zusammenfassung: `room_area_total`, **Anzahl Räume** je Typ, **Gangfläche**, **Engstellen gefunden: 0** (sollte 0 sein), **Tür-zu-Eingang Pfade** (Länge/Existenz).
* `solution.png` wird mit **Einblendung der wichtigsten Kennzahlen** beschriftet (Zielwert, GAP, Laufzeit, Seed).

### 16.7 Performance-Telemetrie (optional, empfohlen)

* Periodisch **RAM-Nutzung**, **Threads**, **CPU-Last** ins Log.
* Bei sehr langen Läufen: **Phasen-Historie** (Zeitanteile) und **Verbesserungskurve** (Zeit vs. Objective) als CSV.

### 16.8 Qualität & Robustheit

* Logs dürfen **nie** stillschweigend abbrechen; Fehlerzustände mit **Stacktrace** und **letztem konsistenten Artefakt** (JSON/PNG) dokumentieren.
* Fortschrittsanzeige unterdrückt **nie** die erzeugten Dateien (auch bei non-TTY).
* Alle Zeitangaben in **Sekunden** (mit 3 Nachkommastellen), **ISO-8601** in JSON-Feldern.

---

---

## Fortschritt

* 2024-06-01: AGENTS.md hinzugefügt und grundlegende Projektanweisungen dokumentiert.
* 2024-06-02: Grundgerüst in Python erstellt (CLI, Konfigurationsladen, Dummy-Lösung, Visualisierung, Validierung, Tests).*
* 2024-06-03: Validator erweitert (Überschneidungen, Gangbreite, Türen, Erreichbarkeit) und Tests ergänzt.
* 2025-08-03: CP-SAT-Modell mit Variablen und Randbedingungen eingeführt.
* 2025-08-03: Kurz-Spezifikation, CLI-Beispiel und Abhängigkeiten ergänzt.
* 2025-08-04: Prozessstarter-Skript `start_process.py` hinzugefügt.
* 2025-08-04: Datenmodelle für RoomPlacement und SolveParams ergänzt.
* 2025-08-04: Hilfsfunktionen für Rasteroperationen und entsprechende Tests ergänzt.
* 2025-08-04: Fortschrittsmodul für Heartbeat-Logging hinzugefügt.
* 2025-08-04: Visualisierung mit Raster, Farben und Türen erweitert.
* 2025-08-04: Validator auf Grid-Aufbau mit 4×4-Gangprüfung und Türlogik umgestellt.
* 2025-08-05: CP-SAT-Solver mit Tür- und Konnektivitäts-Cuts implementiert.
* 2025-08-06: CLI um Grid- und Eingang-Parameter sowie Validierung-only-Modus erweitert.
* 2025-08-06: `rooms.yaml` auf Einzeilenformat umgestellt und JSON-Schema `schemas/solution.schema.json` ergänzt.
* 2025-08-06: CLI-Tests für Versionsausgabe und Minimalablauf ergänzt.
* 2025-08-07: Logging/Progress ausgebaut, Checkpoints und zusätzliche Validator-Tests hinzugefügt.
* 2025-08-08: Validator auf diagonale Engstellen/Türengpässe erweitert, Fortschrittsstatistiken ergänzt.
* 2025-08-09: requirements.txt mit Laufzeit- und Prüf-Abhängigkeiten ergänzt.
* 2025-08-10: GUIDE.md mit Anleitung für Google Colab hinzugefügt.
* 2025-08-11: Codeformatierung und Lintingfehler bereinigt.
* 2025-08-13: CP-SAT-Solver setzt Seed- und Thread-Parameter.
* 2025-08-14: Solver verbindet Korridorinseln über Pfad-Cut.
* 2025-08-15: Türheuristik wählt anhand von Scoring bessere Türpositionen.
* 2025-08-16: Validator verbietet standardmäßig Außentüren; CLI-Schalter `--allow-outside-doors` hinzugefügt.
* 2025-08-17: Datenmodell vereinfacht und CLI auf fixes 77×50-Raster reduziert; Lösung enthält `grid_w`/`grid_h`.
