Hier ist der **vollständige Arbeitsauftrag** (neutral, methodenoffen, Python-Pflicht) – **ohne** irgendeine Implementierungsrichtung vorzugeben, aber mit **allen** Daten/Parametern, die für eine unabhängige Neuumsetzung nötig sind.

> **Referenzbild (Pflichtbeilage):**
> `grundstueck_77x50_eingang_4x10.png` – zeigt das 77×50-Gitternetz und den fixen Eingang als 4×10-Fläche oben (x=56..59, y=40..49).
> Bitte das Bild in der Doku/README einbinden und zur visuellen Verifikation verwenden.

---

## 1) Ziel / Problemstellung

Entwickeln Sie in **Python** ein Programm, das für ein diskretes Spielfeld (Gitternetz) eine **optimale Raumverteilung** erzeugt.

* **Primärziel:** **Maximierung der Gesamt-Raumfläche** (Summe der belegten Gitterzellen aller geforderten Räume).
* **Harte Nebenbedingungen (müssen erfüllt sein):**

  1. **Eingang** ist **fix** und gehört **immer** zum Gang (Details siehe §3).
  2. **Gang = Komplement** der Räume: **jede** Zelle ist **entweder Raum oder Gang**.
  3. **Mindestbreite Gang ≥ 4** an **jeder** Stelle (auch in Kurven/Kreuzungen/vor Türen).
  4. **Konnektivität:** Die **gesamte Gangfläche** ist **zusammenhängend** (4-Nachbarschaft) und enthält den **Eingangsblock**.
  5. **Türen:** Pro Raum ≥1 Tür, auf **einer Raumwand**, **nicht** in Ecken, öffnet **in den Gang**; **kein** Durchgang durch Räume.
  6. **Erreichbarkeit:** Von **jeder Tür** existiert ein Gangpfad zum **Eingang**.
  7. **Räume:** Achsenparallele Rechtecke, **wand-an-wand** erlaubt, **keine Überlappung**, vollständig innerhalb des Rasters.
  8. **Raumkatalog** (Typen, Größenintervalle, Schrittweiten, Instanzanzahlen) gemäß §4.

Methodik/Algorithmik ist **frei** (exakt/heuristisch/hybrid), solange alle harten Regeln eingehalten werden.

---

## 2) Spielfeld, Koordinaten

* **Rastergröße:** 77 (x) × 50 (y) Zellen à 1×1; Gitterlinien bei ganzzahligen Koordinaten $[0,77]\times[0,50]$.
  (**Code-Parameter:** `GRID_W, GRID_H = 77, 50`.)&#x20;
* **Zelle (i,j):** belegt Rechteck $[i,i+1]\times[j,j+1]$.
* **Ecken:** unten-links $(0,0)$, oben-rechts $(77,50)$.

---

## 3) Fester Eingang (immer Gang)

* **Lage (fix):** **x = 56..59**, **y = 40..49** (4×10, Oberkante bei y=50).
* **Konstanten:** `ENTRANCE_X1=56`, `ENTRANCE_W=4`, `ENTRANCE_X2=ENTRANCE_X1+ENTRANCE_W=60`.&#x20;
  **Länge:** `ENTRANCE_MIN_LEN = ENTRANCE_MAX_LEN = 10` (fest oben, y=40..49).&#x20;
* Der gesamte 4×10-Block ist **Gang** und muss Teil der **zusammenhängenden Gangkomponente** sein.

---

## 4) Räume

### 4.1 Raumdefinition (Felder je Raumtyp)

Im Code ist die Struktur `RoomDef` definiert mit:
`name, group, pref_w, pref_h, min_w, min_h, step_w, step_h, priority, efficiency_factor, duplicate_id?`. &#x20;

* **Interpretation:**

  * **Bevorzugte Größe:** `(pref_w, pref_h)` (nur weiches Kriterium, wenn genutzt).
  * **Mindestgröße:** `(min_w, min_h)` — harte Untergrenze.
  * **Schrittweiten:** `(step_w, step_h)` — erlaubte Größeninkremente.
  * **priority/efficiency\_factor:** optionale Gewichte für weiche Ziele.
  * **duplicate\_id:** Kennung für Typfamilien mit mehreren **Instanzen** (z. B. Prod1/Prod2).

### 4.2 Geforderte Raum-Instanzen (vollständige Liste)

> Jede Zeile in der folgenden Liste entspricht **einer** zu planenden **Instanz** (einzelner Raum). Typen mit „1/2“ bedeuten **zwei** getrennte Räume. Quelle: `ROOMS: List[RoomDef] = [...]`.&#x20;

* **Kern-Räume:**

  * Dev (group: Dev), **pref 10×8**, **min 6×6**, **step 2×1**, **priority 10**, eff 1.5.&#x20;
  * QA (QA), **pref 9×7**, **min 6×6**, **step 1×1**, **priority 9**, eff 1.4.&#x20;
  * Research (Research), **pref 8×7**, **min 6×6**, **step 1×1**, **priority 8**, eff 1.1.&#x20;
* **Produktion:**

  * Prod1 (Production), **pref 12×8**, **min 8×6**, **step 2×1**, **priority 8**, eff 1.3, **duplicate\_id="Prod"**.&#x20;
  * Prod2 (Production), **gleich wie Prod1**, **zweite Instanz**.&#x20;
* **Lager/Studios:**

  * Storeroom (Storage), **pref 10×8**, **min 6×6**, **step 1×1**, **priority 9**, eff 1.4.&#x20;
  * Graphics (Studio), **pref 8×7**, **min 6×6**, **step 1×1**, **priority 9**, eff 1.3.&#x20;
  * Sound (Studio), **pref 8×6**, **min 6×6**, **step 1×1**, **priority 9**, eff 1.3.&#x20;
  * MoCap (Studio), **pref 14×8**, **min 10×6**, **step 2×1**, **priority 8**, eff 1.2.&#x20;
* **Management/Support:**

  * Head Office (Admin), **pref 6×6**, **min 4×4**, **step 1×1**, **priority 9**, eff 1.3.&#x20;
  * Marketing (Marketing), **pref 8×6**, **min 6×6**, **step 1×1**, **priority 7**, eff 1.1.&#x20;
  * Support1 (Support), **pref 8×6**, **min 6×6**, **step 1×1**, **priority 6**, eff 1.0, **duplicate\_id="Support"**.&#x20;
  * Support2 (Support), **gleich wie Support1**, **zweite Instanz**.&#x20;
* **Tech-Räume:**

  * Console (Console), **pref 10×7**, **min 6×6**, **step 1×1**, **priority 7**, eff 1.1.&#x20;
  * Server (Server), **pref 10×8**, **min 6×6**, **step 1×1**, **priority 8**, eff 1.2.&#x20;
  * Training (Training), **pref 10×8**, **min 6×6**, **step 1×1**, **priority 6**, eff 1.1.&#x20;
* **Komfort:**

  * Toilet1 (Facilities), **pref 4×4**, **min 3×3**, **step 1×1**, **priority 5**, eff 0.8, **duplicate\_id="Toilet"**.&#x20;
  * Toilet2 (Facilities), **gleich wie Toilet1**, **zweite Instanz**.&#x20;
  * Staff1 (Facilities), **pref 6×5**, **min 4×4**, **step 1×1**, **priority 6**, eff 1.0, **duplicate\_id="Staff"**.&#x20;
  * Staff2 (Facilities), **gleich wie Staff1**, **zweite Instanz**.&#x20;

> **Anmerkung:** Die Liste ist **fix**; sie definiert **welche Räume, wie viele Instanzen**, sowie **bevorzugte/minimale Größen** und **Schrittweiten**.

---

## 5) Türen & Wände (harte Regeln)

* **Pflicht:** mind. **eine Tür pro Raum**.
* **Position:** Tür liegt **auf einer Raumwand**, **nicht** in einer Ecke (also innerhalb des Wandsegments).
* **Tür → Gang:** die Zelle **jenseits** des Wandsegments (außerhalb des Raums) muss **Gang** sein.
* **Keine** Tür zwischen zwei Räumen (Türen führen **immer** in den Gang).
* **Erreichbarkeit:** Jeder Raum ist über **seine Tür(en)** per **Gangpfad** (4-Nachbarschaft) mit dem **Eingang** verbunden.
* **Hinweis auf vorhandene (nicht bindende) Heuristik-Konstanten:** `DOOR_CLUSTER_LIMIT=4`, `K_DOOR=150`, `THRESHOLD_VERY_CLOSE_DOORS=3`, `THRESHOLD_CLOSE_DOORS=8`. (Nur als Kontext, kein Muss.) &#x20;

---

## 6) Gang (Definition, Breite, Konnektivität)

* **Definition:** **Komplement** der Räume auf dem 77×50-Raster (Eingang ⊂ Gang).
* **Breite ≥ 4 überall:** Der Gang darf **nirgends** auf 1–3 Zellen verjüngen – auch nicht in Kurven, an T-Kreuzungen oder direkt vor Türen (L∞-Dicke ≥ 4).
* **Konnektivität:** **Eine** zusammenhängende Gangkomponente (4-Nachbarschaft), die **den Eingangsblock enthält**.
* **Tür-Erreichbarkeit:** Für **jede Tür** existiert ein Gangpfad zum Eingangsblock.
* **Kein** Durchgang durch Räume.

---

## 7) Optimierung (Ziele)

* **Primär:** **Maximiere die Gesamt-Raumfläche** (Summe aller Raumzellen).
* **Sekundär (optional):** Zusätzliche weiche Ziele **dürfen** verwendet werden (z. B. kompakte Anordnung, Adjazenzen), **niemals** auf Kosten der harten Regeln.
  *(Bestehende Gewichte aus dem Code – **nur informativ**, nicht bindend: u. a. `W_ROOM_EFFICIENCY=5000`, `W_PRIORITY_BONUS=2500`, `W_PROD_STORE_BON=10000`, `W_COMPACT_BONUS=2000` …)*&#x20;

---

## 8) Ein-/Ausgaben (Artefakte)

**Pflichtausgaben:**

1. `solution.json`

   * `rooms`: Liste `{id, type, x, y, w, h, doors:[{side, pos_x, pos_y}]}`
   * `entrance`: `{x1:56, x2:60, y1:40, y2:50}`
   * optional `corridor_mask` (oder aus Komplement rekonstruieren)
   * `objective`: z. B. `{room_area_total: …, …}`
2. `solution.png`

   * Raster 77×50, **Eingang** klar markiert, **Räume** farbig, **Gang** hell, **Türen** als Striche auf Wänden, **keine** Engstellen < 4.
3. `validation_report.json`

   * Pro Muss-Kriterium (§1–§6): **pass/fail**, kurze Begründung, Kennzahlen (z. B. minimale Gangbreite, Anzahl isolierter Komponenten = 0).

---

## 9) Validierung (MUSS)

Eine Lösung ist **nur gültig**, wenn **alle** folgenden Prüfungen **bestehen**:

1. **Komplement:** Jede Zelle ist **genau eine** Kategorie (Raum/Gang).
2. **Eingang:** Alle Zellen des 4×10-Blocks sind Gang (x=56..59, y=40..49).
3. **Keine Überlappung:** Räume überdecken sich nicht; alle Räume liegen vollständig innerhalb 77×50.
4. **Gangbreite ≥ 4:** Überall (auch an Kurven/Kreuzungen/vor Türen).
5. **Konnektivität:** Eine Gangkomponente (enthält den Eingang).
6. **Türen:** pro Raum ≥1; nicht in Ecken; Tür führt in Gang; **kein** Raum-zu-Raum-Durchgang.
7. **Erreichbarkeit:** Von **jeder Tür** ein Gangpfad zum Eingangsblock.

*Bitte Validator bereitstellen (CLI-Schalter `--validate-only solution.json`).*

---

## 10) Benutzermodell (fachliche Analogie)

* Räume werden wie im Spiel per Drag-&-Drop als **rechteckige Bereiche** erstellt.
* Türen werden an **Wandsegmenten** (nicht in Ecken) platziert und **führen in den Gang**.
* Räume **dürfen aneinandergrenzen**; **alles Nicht-Raum ist Gang** (unter Einhaltung der Regeln aus §6).

---

## 11) Konfiguration (Eingaben)

* **Grid-Parameter:** Standard `GRID_W=77`, `GRID_H=50` (parametrisierbar).&#x20;
* **Eingangsblock:** Standard `x=56..59`, `y=40..49` (parametrisierbar).&#x20;
* **Raumkatalog:** gemäß §4.2 (als JSON/TOML/YAML einlesbar); die **Anzahl** der Instanzen ergibt sich aus der **Anzahl der gelisteten Einträge** (z. B. `Prod1`+`Prod2`=2 Produktionsräume).  &#x20;

---

## 12) CLI (Vorschlag; methodenneutral)

```
python solver.py \
  --config rooms.yaml \
  --out-json solution.json \
  --out-png solution.png \
  --validate report.json \
  --seed 1 --threads 8 --time-limit 0
```

* `--time-limit 0` = kein Limit (oder weglassen).
* Weitere sinnvolle Schalter: `--objective weights.json`, `--show`, `--validate-only`.

---

## 13) Logging & Fortschritt (Pflicht)

**Kontinuierliche** und **verlässliche** Statusausgabe während **Einlesen → Modellaufbau → Optimierung → Validierung → Visualisierung**:

* **CLI-Schalter:**
  `--log-level {DEBUG,INFO,WARN,ERROR}` (Default: INFO),
  `--log-format {text,json}` (Default: text),
  `--log-file <pfad>` (optional),
  `--progress {auto,off}` (Default: auto),
  `--progress-interval <sek>` (Default: 1),
  `--seed <int>`, `--threads <n>`, `--time-limit <sek>` (optional).
* **Strukturierte Logs (JSON-Lines):** je Event ein Record `{ts, phase ∈ {start,parse,build,solve,incumbent,bound,gap,validate,render,finish}, runtime_sec, eta_sec, objective_best, objective_bound, gap, vars, constraints, mem_mb, …}`.
* **Terminal-Progress:** dynamische Anzeige (z. B. eine Zeile oder `tqdm`), u. a. **Phase**, **Laufzeit**, **ETA**, **bestes Ziel**, **Bound**, **GAP**, **Verbesserungsschritte**.
* **Callbacks/Polling:** Bei neuem **Incumbent/Bound** sofortiges Update; sonst Heartbeat mind. alle `--progress-interval` Sekunden.
* **Abbruch & Checkpoints:** Sauberer SIGINT-Abbruch; optional periodische Checkpoints (`--checkpoint <sek>`), die beste bekannte Lösung+PNG sichern.

---

## 14) Abnahme-/Testkriterien

* **Validator** bestätigt **alle Muss-Kriterien** (Pass).
* **PNG** zeigt Eingang, Räume, Gang (ohne Engstellen), Türen korrekt.
* **JSON** konsistent (integre Koordinaten, innerhalb 77×50).
* **Log/Progress** vorhanden, mit ETA, GAP/Bound-Entwicklung, Incumbent-Events.
* **Reproduzierbarkeit:** mit gleichem `--seed` identische Lösung (bei deterministischen Settings).

---

## 15) Nicht-Festlegungen (bewusste Freiheit)

* **Keine Vorgabe** der Algorithmik (CP-SAT/ILP/Flows/Heuristik/Metaheuristik): frei wählbar.
* **Keine Bindung** an bestehende Gewichte/Heuristiken aus dem Code – sie dienen nur als **Informationsquelle** (siehe §7).&#x20;

---

## 16) Beistellunterlagen (aus Code extrahierte Konstanten)

* **GRID:** `GRID_W=77`, `GRID_H=50`.&#x20;
* **Eingang:** `ENTRANCE_X1=56`, `ENTRANCE_W=4`, `ENTRANCE_X2=60`, `ENTRANCE_MIN_LEN=ENTRANCE_MAX_LEN=10`.&#x20;
* **Tür/Abstand-Konstanten (informativ):** `DOOR_CLUSTER_LIMIT=4`, `K_DOOR=150`, `THRESHOLD_VERY_CLOSE_DOORS=3`, `THRESHOLD_CLOSE_DOORS=8`. &#x20;
* **Gewichte (informativ):** u. a. `W_ROOM_EFFICIENCY=5000`, `W_PRIORITY_BONUS=2500`, `W_PROD_STORE_BON=10000`, `W_COMPACT_BONUS=2000`.&#x20;
* **Raumkatalog/Instanzen:** vollständige Liste siehe §4.2 (Quelle: `ROOMS: List[RoomDef]` mit u. a. `Prod1/Prod2`, `Support1/Support2`, `Toilet1/Toilet2`, `Staff1/Staff2`).   &#x20;

---

### Abschluss

Diese Spezifikation enthält **alle** fachlichen und technischen Eckdaten (Raster/Koordinaten, fixer Eingang, Tür-/Gangregeln, Raumkatalog inkl. Größen/Anzahlen/Schrittweiten, Ziele, Ausgaben, Validierung, Logging/Progress).
Bitte implementieren Sie **in Python**; die Wahl der Verfahren ist **frei**, die **harten Regeln** müssen **immer** erfüllt sein. Bei Fragen zur Interpretation einzelner Regeln bitte frühzeitig klären. Viel Erfolg! 💼🧩


zusätzlich und wichtig!:
1. **Gang = Komplement (Zellgranularität fehlt)**

   * Du schreibst, man brauche „keine expliziten Zellenvariablen“ – das ist in Spannung zu den harten Auflagen (**Gangbreite≥4 überall**, **Konnektivität**, **Tür-in-Gang**). Ohne zellweise Binärvariablen wird es äußerst schwierig, diese Eigenschaften **im Modell** (nicht nur ex post) korrekt zu garantieren.

2. **Gangbreite ≥4 unscharf/angreifbar**

   * „Abstandsconstraints“ zwischen Wänden/außen sind nur ein **Surrogat** und decken nicht alle Geometrien ab (S-Kurven, diagonale Engstellen, T-Kreuzungen, Vor-Tür-Schultern).
   * Es fehlt ein **hinreichendes, vollständiges** Formalisierungsprinzip (z. B. 4×4-Fenster-Deckung in L∞).

3. **Konnektivität inkonsistent beschrieben**

   * Einerseits formulierst du einen **Fluss** auf „Gangknoten“, andererseits sagst du, die Gangzellen kennt man erst **nach** der Raumplatzierung. Das widerspricht sich, wenn das Ganze **in einem** Modell optimal werden soll.
   * Es fehlt die explizite Kopplung: **Fluss ≤ M · corr\_cell\[u]** für Knoten/Kanten, Quelle = Eingangsblock, Senken = alle Tür-Gangzellen **oder** alle Gangzellen (je nach Variante), **Flusserhaltung** usw.

4. **Türen nur verbal, nicht robust formalisiert**

   * Du erwähnst Tür-Variablen, aber die **Ecken-Ausschlüsse**, **Randfälle** (Außenkante), **Tür-zu-Gang-Kopplung** und **≥1 Tür pro Raum** sind nicht sauber formalisiert.
   * Keine explizite Regel: **keine Außentür außer am fixen Eingang**, falls so gewünscht.
   * Tür-Zellenkoordinaten und Kopplung an Raumwand (lineare Indikator-Constraints) fehlen als klare Formeln.

5. **Komplement & Nicht-Überlappung nur halbfest**

   * Nicht-Überlappung per „four-way disjunction“ ist ok, aber es fehlt der **Nachweis**, dass damit das Komplement „Gang“ korrekt entsteht (ohne Zellenvariablen bleibt’s abgeleitet und für Breite/Konnektivität zu grob).

6. **Ausgaben/Schema/Validierung nicht normiert**

   * JSON-Schema, Tür-Koordinatenkonvention (bezüglich **Gangseite**), PNG-Beschriftung (Achsen, Legende, Eingang), **Validator-Schnittstelle** – vieles ist nur narrativ, nicht präzise.

7. **Logging/Progress unzureichend**

   * Gewünscht war „laufend informiert, was passiert & ETA“. Es fehlen **konkrete** Vorgaben (CLI-Schalter, Event-Felder, Intervalle, Heartbeat, Abbruch/Checkpoint).

8. **Raumkatalog/Instanzanzahl nicht explizit**

   * Du referenzierst „rooms.yaml“ und ein Katalog-Konzept, nennst aber **nicht** die konkreten Typen/Instanz-Anzahlen, Mindest-/Schrittmaße (die in deinem Code stehen). Das ist für eine unabhängige Umsetzung **Pflicht**.

9. **Ränder/Koordinatensystem**

   * Ursprung, Orientierung (unten-links), Gitterinterpretation (Zelle \[i,i+1]×\[j,j+1]) solltest du **explizit** verankern (du deutest es an, aber normierst es nicht).

---

## So wäre die **perfekte Version** (vollständig & präzise, methodenneutral)

> **Ziel:** In Python ein Programm, das bei Raster 77×50 die **Gesamt-Raumfläche maximiert**, unter **harten** Regeln: fixer Eingang (4×10 oben, x=56..59/y=40..49), **Gang = Komplement** der Räume, **Gangbreite ≥4 überall**, **eine zusammenhängende Gangkomponente** mit Eingang, **jede Tür führt in den Gang**, **kein Durchgang durch Räume**, **Räume rechteckig, wand-an-wand erlaubt, keine Überlappung**.

### 1) Raster & Koordinaten

* Raster: **77×50** Zellen; Ganzzahlgitter $[0,77]×[0,50]$.
* Zelle $(i,j)$ belegt $[i,i+1]×[j,j+1]$; **Ursprung unten-links**; 4-Nachbarschaft.

### 2) Fixer Eingang (immer Gang)

* **Eingangsblock:** $x \in \{56,57,58,59\}$, $y \in \{40,\dots,49\}$.
* Diese 40 Zellen sind **Gang** und Teil der **einen** Gangkomponente.

### 3) Raumkatalog & Instanzen (verbindlich)

* **Jede Zeile = 1 Instanz**, also geforderte Anzahl ist implizit:
  **Dev(10×8, min 6×6, step 2×1)**; **QA(9×7, min 6×6, step 1×1)**; **Research(8×7, min 6×6, step 1×1)**;
  **Prod1/Prod2(12×8, min 8×6, step 2×1)**; **Storeroom(10×8, min 6×6, step 1×1)**;
  **Graphics(8×7, 6×6, 1×1)**; **Sound(8×6, 6×6, 1×1)**; **MoCap(14×8, 10×6, 2×1)**;
  **Head Office(6×6, 4×4, 1×1)**; **Marketing(8×6, 6×6, 1×1)**;
  **Support1/Support2(8×6, 6×6, 1×1)**; **Console(10×7, 6×6, 1×1)**; **Server(10×8, 6×6, 1×1)**; **Training(10×8, 6×6, 1×1)**;
  **Toilet1/Toilet2(4×4, min 3×3, 1×1)**; **Staff1/Staff2(6×5, 4×4, 1×1)**.
* **Größenwahl:** $w = w_{\min} + k\cdot\text{step}_w$, $h = h_{\min} + \ell\cdot\text{step}_h$, integer, solange $x+w \le 77, y+h \le 50$.

### 4) Modellierung (methodenneutral, aber formal präzise)

**Zell-Binärvariablen (empfohlen, für Korrektheit der harten Regeln):**

* Für jede Zelle $(i,j)$: `room_cell[i,j] ∈ {0,1}`, `corr_cell[i,j] ∈ {0,1}`.
* **Komplement:** `room_cell + corr_cell = 1` (für alle Zellen).
* **Eingang:** `corr_cell=1` auf $x=56..59, y=40..49$.

**Räume (rechteckige Instanzen):**

* Für jede Rauminstanz $r$: Integer `x_r,y_r,w_r,h_r` mit Domänen gemäß §3.
* Kopple `room_cell` an die Rechtecke:

  * Hilfsbinär `in_r[i,j]` ⇒ $(i,j)$ liegt in Rechteck $r$.
  * `room_cell[i,j] = OR_r in_r[i,j]` (linearisiert: `room_cell ≥ in_r`; `room_cell ≤ Σ_r in_r`).
* **Nicht-Überlappung** folgt dann automatisch aus obiger OR-Kopplung (oder zusätzlich NoOverlap-Disjunktionen nutzen).

**Gangbreite ≥4 (L∞-Dicke):**

* **4×4-Fenster-Deckung**: Für jedes Fenster $W(a,b)$ (oben-links $(a,b)$, Größe 4×4) Binär `win[a,b]`.
* `win[a,b] = 1 ⇒ corr_cell[i,j] = 1` für alle $(i,j)∈W(a,b)$.
* **Jede** Gangzelle muss in **mindestens einem** vollen 4×4-Fenster liegen:
  `corr_cell[i,j] ≤ Σ_{W⊇(i,j)} win[a,b]`.
  → Garantiert **keine Engstelle <4**, auch an Kurven/Kreuzungen/Vor-Tür-Schultern.

**Konnektivität (Fluss vom Eingang):**

* Graph: Zellen als Knoten, Kanten zwischen 4-Nachbarn.
* Direktionaler Fluss `f_e ≥ 0` mit Kapazität an `corr_cell` gekoppelt:
  `f_e ≤ M·corr_cell[u]` und `f_e ≤ M·corr_cell[v]`.
* **Quelle:** alle Eingangszellen (aggregiert) mit Supply =
  – Variante A: **Anzahl Gangzellen** (dann alle werden „versorgt“), **Senken:** alle Gangknoten (Demand=1).
  – Variante B: Supply = **Anzahl Türen**, **Senken:** Gangzellen an Türen (Demand=1) **und** zusätzlich „Spülfluss“ über alle Gangzellen (für Ein-Komponenten-Nachweis).
* **Flusserhaltung** für alle übrigen Knoten.
  → Erzwingt **eine zusammenhängende Gangkomponente**, die den Eingang enthält, und **Erreichbarkeit aller Türen**.

**Türen (nicht in Ecken, auf Wand, in den Gang):**

* Für jede Rauminstanz $r$ und jede mögliche **innere** Wandposition (ohne Eckindizes) eine Binärvariable `door_r_side_t`.
* **Kopplung an Gang:**

  * LEFT: `door ⇒ corr_cell[x_r-1,y_r+t]=1` (und $x_r>0$).
  * RIGHT: `door ⇒ corr_cell[x_r+w_r,y_r+t]=1` (und $x_r+w_r<77$).
  * BOTTOM: `door ⇒ corr_cell[x_r+t,y_r-1]=1` (und $y_r>0$).
  * TOP: `door ⇒ corr_cell[x_r+t,y_r+h_r]=1` (und $y_r+h_r<50$).
* **≥1 Tür pro Raum:** `Σ_t door_r_*_t ≥ 1`.
* **Optional:** Außentüren (an Grundstücksrand) **verbieten**, außer am fixen Eingang: dann oben genannte Randfälle via Domänen ausschließen.

### 5) Ziele

* **Primär:** maximiere `Σ room_cell[i,j]` (oder `Σ_r w_r·h_r`).
* **Sekundär (optional):** Prioritäten/Effizienz (weiche Gewichte), Kompaktheit etc. – stets **dominierend** hinter der Feasibility.

### 6) Ausgaben (verbindlich)

* **`solution.json`**:

  * `rooms: [{id,type,x,y,w,h,doors:[{side,pos_x,pos_y}]}]`
  * `entrance:{x1:56,x2:60,y1:40,y2:50}`
  * optional `corridor_mask` (77×50 Bool)
  * `objective:{room_area_total:…}`
* **`solution.png`**: Raster 77×50, **Achsen**, **Eingang** eindeutig markiert, **Räume** farbig, **Gang** hell, **Türen** als Striche auf den Wänden.
* **`validation_report.json`**: Jedes Muss-Kriterium **pass/fail** + Kennzahlen (min Gangbreite, #Komponenten, Tür-Erreichbarkeit…).

### 7) Validierung (MUSS)

* **Komplement** geprüft (Zellmenge disjunkt & vollständig).
* **Eingang frei** (40 Zellen Gang).
* **Keine Überlappung**, **im Grid**.
* **Gangbreite ≥4** via 4×4-Fenster-Check der `corridor_mask`.
* **Konnektivität**: BFS auf Gang vom Eingang → **eine** Komponente.
* **Türen**: pro Raum ≥1; nicht in Ecken; Tür-Nachbarzelle ist Gang; **Türpfad** zum Eingang existiert.

### 8) Logging & Fortschritt (Pflicht)

* CLI: `--log-level {DEBUG,INFO,…}`, `--log-format {text,json}`, `--log-file`,
  `--progress {auto,off}`, `--progress-interval <s>`, `--seed`, `--threads`, `--time-limit`.
* **JSON-Events** (1/sec Heartbeat): `{ts,phase∈{start,parse,build,solve,incumbent,bound,gap,validate,render,finish}, runtime_sec, eta_sec, objective_best, objective_bound, gap, vars, constraints, mem_mb,…}`.
* **Terminal-Progress**: eine Zeile mit Phase, t, ETA, obj, bound, GAP; Updates bei Incumbent/Bound + Heartbeat.
* **Abbruch/Checkpoint:** SIGINT speichert letzte beste `solution.json/.png` + `validation_report.json`.

### 9) CLI-Vorschlag & Tests

* `python solver.py --config rooms.yaml --out-json solution.json --out-png solution.png --validate validation_report.json --seed 1 --threads 8 --time-limit 0`
* Tests: leeres Layout, Hotelgang mit Zimmern beidseitig, 3-Zellen-Engstelle (muss failen), isolierte Insel (fail), Tür in Ecke (fail), Randtür (fail, außer Eingang).
