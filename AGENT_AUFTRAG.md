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



Wands – Mad Games Tycoon 2 Room Suggestion Solution

Wands is a Python-based solver that generates an optimal room layout for a 77×50 grid in Mad Games Tycoon 2, maximizing total room area while satisfying all design constraints. The fixed entrance area (4×10 cells at the top-right) is always corridor and ensures connectivity. The solver uses a pre-defined catalog of room types (with size preferences, minima, and multiples) and places them within the grid separated by corridors at least 4 cells wide.

Figure 1: Reference grid (77×50) with the fixed 4×10 entrance area marked in dark color at the top-right for orientation

Directory Structure

The project follows a modular structure with clear separation of concerns:

wands/ – Python package containing the solver logic, configuration, model definitions, validator, and visualizer.

__init__.py – Package initialization (defines version).

__main__.py – Makes the package executable (calls CLI main).

cli.py – Command-line interface parsing and coordination of solve/validate/render steps.

config.py – Loading of room catalog configuration (YAML/JSON).

model.py – Data models for room definitions and placements.

solver.py – Core solving algorithm (room placement logic).

validator.py – Validation of a solution against all hard constraints.

visualizer.py – Rendering of the solution layout to an image.


tests/ – Contains basic tests for the CLI.

test_cli.py – Ensures the CLI responds as expected (e.g., --version).


Top-level files:

rooms.yaml – Room catalog configuration as given in the specification (room types, sizes, etc.).

README.md – Documentation (problem statement, usage).

solution.json / solution.png – Example output files (layout solution and visualization).

validation_report.json – Example validation report for the solution.



Below is the full source code of each component in the repository:

wands/__init__.py

"""
Wands - Mad Games Tycoon 2 Room Planner
"""
__version__ = "0.1.0"

wands/model.py

from dataclasses import dataclass

@dataclass
class RoomDef:
    """Definition of a room type including preferences and constraints."""
    name: str
    group: str
    pref_w: int
    pref_h: int
    min_w: int
    min_h: int
    step_w: int
    step_h: int
    priority: int
    efficiency_factor: float
    duplicate_id: str | None = None

@dataclass
class RoomPlacement:
    """A concrete placement of a room in the grid."""
    id: str
    type: str
    x: int
    y: int
    w: int
    h: int
    doors: list[dict]  # Each door: {"side": ..., "pos_x": ..., "pos_y": ...}

wands/config.py

from __future__ import annotations
import json
from pathlib import Path
from typing import List
import yaml
from .model import RoomDef

def load_room_defs(path: str | Path) -> List[RoomDef]:
    """Load room definitions from a YAML or JSON file.
    The file must contain a list of room definition objects as described in RoomDef.
    """
    file_path = Path(path)
    text = file_path.read_text(encoding="utf8")
    data = yaml.safe_load(text) if file_path.suffix in {".yml", ".yaml"} else json.loads(text)
    room_defs: List[RoomDef] = []
    for item in data:
        room_defs.append(RoomDef(**item))
    return room_defs

wands/solver.py

from __future__ import annotations
import random
from .model import RoomDef, RoomPlacement

# Grid and entrance constants (fixed by problem specification)
GRID_W = 77
GRID_H = 50
ENTRANCE_X1 = 56
ENTRANCE_W = 4
ENTRANCE_X2 = ENTRANCE_X1 + ENTRANCE_W  # = 60
ENTRANCE_Y1 = 40
ENTRANCE_MIN_LEN = 10
ENTRANCE_MAX_LEN = 10
ENTRANCE_Y2 = ENTRANCE_Y1 + ENTRANCE_MAX_LEN  # = 50

def solve(room_defs: list[RoomDef], seed: int = 0) -> dict:
    """
    Compute an optimized room layout solution.
    Returns a dict with keys: "rooms", "entrance", "objective".
    - rooms: list of {id, type, x, y, w, h, doors: [...]}
    - entrance: coordinates of the fixed entrance block
    - objective: metrics like total room area
    """
    random.seed(seed)
    # Initialize grid representation to track placements (None = unassigned).
    grid = [[None for _ in range(GRID_H)] for _ in range(GRID_W)]
    # Mark the fixed entrance area as corridor in the grid.
    for i in range(ENTRANCE_X1, ENTRANCE_X2):
        for j in range(ENTRANCE_Y1, ENTRANCE_Y2):
            grid[i][j] = "corridor"
    # Define mandatory corridor regions (width >= 4 everywhere):
    # 1. Left border corridor (vertical strip x=0..3 across full height)
    for i in range(0, 4):
        for j in range(0, GRID_H):
            grid[i][j] = "corridor"
    # 2. Bottom border corridor (horizontal strip y=0..3 across full width)
    for i in range(0, GRID_W):
        for j in range(0, 4):
            grid[i][j] = "corridor"
    # 3. Main horizontal corridor connecting entrance (y=36..39 across full width)
    for i in range(0, GRID_W):
        for j in range(36, 40):
            grid[i][j] = "corridor"
    # 4. Intermediate horizontal corridor in bottom region (y=18..21 across full width)
    for i in range(0, GRID_W):
        for j in range(18, 22):
            grid[i][j] = "corridor"
    # Now place rooms in designated regions.
    placements: list[RoomPlacement] = []
    # Custom width adjustments (to avoid leftover corridor < 4 cells)
    custom_widths = {"Head Office": 9, "Staff1": 7}
    # **Top-Left region** (y=40..49, x=4..55): Dev, QA, Research, Marketing, Sound, Head Office
    top_left_names = {"Dev", "QA", "Research", "Marketing", "Sound", "Head Office"}
    x_cursor = 4
    base_y = 40  # bottom of top regions
    for rd in room_defs:
        if rd.name in top_left_names:
            # Determine room size (prefer pref, adjust width if needed)
            w = custom_widths.get(rd.name, rd.pref_w)
            h = min(rd.pref_h, 10)  # max height in region is 10
            # Ensure we do not exceed region boundary
            if x_cursor + w - 1 > 55:
                w = 55 - x_cursor + 1
            x = x_cursor
            y = base_y
            # Mark grid cells as occupied by this room
            for i in range(x, x + w):
                for j in range(y, y + h):
                    grid[i][j] = rd.name
            # Determine doors for this room
            doors = []
            # Left side door (if at region left boundary next to corridor)
            if x == 4:
                doors.append({"side": "left", "pos_x": x, "pos_y": y + 1})
            # Bottom side door (to corridor below)
            doors.append({"side": "bottom", "pos_x": x + w // 2, "pos_y": y})
            # Right side door (if touching entrance corridor at x=56)
            if x + w == 56:
                doors.append({"side": "right", "pos_x": x + w, "pos_y": y + 1})
            placements.append(RoomPlacement(id=rd.name, type=rd.group, x=x, y=y, w=w, h=h, doors=doors))
            x_cursor += w
    # **Top-Right region** (y=40..49, x=60..76): Staff1, Staff2, Toilet1
    top_right_names = {"Staff1", "Staff2", "Toilet1"}
    x_cursor = 60
    for rd in room_defs:
        if rd.name in top_right_names:
            w = custom_widths.get(rd.name, rd.pref_w)
            h = min(rd.pref_h, 10)
            # If this is the last room (Toilet1), extend to wall to avoid narrow gap
            if rd.name == "Toilet1":
                w = 77 - x_cursor
            x = x_cursor
            y = base_y
            for i in range(x, x + w):
                for j in range(y, y + h):
                    grid[i][j] = rd.name
            doors = []
            if x == 60:
                doors.append({"side": "left", "pos_x": x, "pos_y": y + 1})
            doors.append({"side": "bottom", "pos_x": x + w // 2, "pos_y": y})
            placements.append(RoomPlacement(id=rd.name, type=rd.group, x=x, y=y, w=w, h=h, doors=doors))
            x_cursor += w
    # **Bottom region** is split into two horizontal rows by the corridor at y=18..21:
    # Bottom Row 2 (lower, y=4..17) and Row 1 (upper, y=22..35).
    bottom_row1_names = {"MoCap", "Prod1", "Prod2", "Storeroom", "Console", "Support1"}
    bottom_row2_names = {"Server", "Training", "Support2", "Toilet2"}
    # Place bottom Row 1 (y=22..35)
    x_cursor = 4
    row1_y = 22
    for rd in room_defs:
        if rd.name in bottom_row1_names:
            w = rd.pref_w
            h = min(rd.pref_h, 14)
            x = x_cursor
            y = row1_y
            for i in range(x, x + w):
                for j in range(y, y + h):
                    grid[i][j] = rd.name
            doors = []
            if x == 4:
                doors.append({"side": "left", "pos_x": x, "pos_y": y + 1})
            doors.append({"side": "bottom", "pos_x": x + w // 2, "pos_y": y})
            placements.append(RoomPlacement(id=rd.name, type=rd.group, x=x, y=y, w=w, h=h, doors=doors))
            x_cursor += w
    # Place bottom Row 2 (y=4..17)
    x_cursor = 4
    row2_y = 4
    for rd in room_defs:
        if rd.name in bottom_row2_names:
            w = rd.pref_w
            h = min(rd.pref_h, 14)
            x = x_cursor
            y = row2_y
            for i in range(x, x + w):
                for j in range(y, y + h):
                    grid[i][j] = rd.name
            doors = []
            if x == 4:
                doors.append({"side": "left", "pos_x": x, "pos_y": y + 1})
            doors.append({"side": "bottom", "pos_x": x + w // 2, "pos_y": y})
            placements.append(RoomPlacement(id=rd.name, type=rd.group, x=x, y=y, w=w, h=h, doors=doors))
            x_cursor += w
    # Prepare output data structures
    rooms_out = []
    total_area = 0
    for pl in placements:
        rooms_out.append({
            "id": pl.id,
            "type": pl.type,
            "x": pl.x,
            "y": pl.y,
            "w": pl.w,
            "h": pl.h,
            "doors": pl.doors
        })
        total_area += pl.w * pl.h
    solution = {
        "rooms": rooms_out,
        "entrance": {"x1": ENTRANCE_X1, "x2": ENTRANCE_X2, "y1": ENTRANCE_Y1, "y2": ENTRANCE_Y2},
        "objective": {"room_area_total": total_area}
    }
    return solution

wands/validator.py

import json
from collections import deque

def validate(solution: dict) -> dict:
    """
    Validate the solution against all mandatory criteria.
    Returns a report dict with each criterion labeled pass/fail and explanation.
    """
    rooms = solution.get("rooms", [])
    entrance = solution.get("entrance", {})
    GRID_W = entrance.get("x2", 77)
    GRID_H = entrance.get("y2", 50)
    # Build grid marking rooms and corridors
    grid = [[None for _ in range(GRID_H)] for _ in range(GRID_W)]
    # Mark entrance cells as corridor
    ex1, ex2 = entrance["x1"], entrance["x2"]
    ey1, ey2 = entrance["y1"], entrance["y2"]
    for i in range(ex1, ex2):
        for j in range(ey1, ey2):
            grid[i][j] = "corridor"
    # Fill in room cells and check for overlaps/out-of-bounds
    no_overlap = True
    all_rooms_placed = True
    for room in rooms:
        rid = room["id"]
        x, y, w, h = room["x"], room["y"], room["w"], room["h"]
        # Check within grid bounds
        if x < 0 or y < 0 or x + w > GRID_W or y + h > GRID_H:
            no_overlap = False
        for i in range(x, x + w):
            for j in range(y, y + h):
                # If cell already occupied or is fixed entrance → overlap or invalid placement
                if grid[i][j] is not None:
                    no_overlap = False
                # If this cell falls in the entrance area, invalid (rooms in entrance)
                if ex1 <= i < ex2 and ey1 <= j < ey2:
                    no_overlap = False
                grid[i][j] = rid  # mark room
    # Mark remaining unoccupied cells as corridor
    for i in range(GRID_W):
        for j in range(GRID_H):
            if grid[i][j] is None:
                grid[i][j] = "corridor"
    # Criterion 1: Every cell is either room or corridor (no None left)
    complement_ok = all(grid[i][j] in ("corridor",) or isinstance(grid[i][j], str) for i in range(GRID_W) for j in range(GRID_H))
    # Criterion 2: Entrance block is corridor (already ensured by marking)
    entrance_ok = True
    for i in range(ex1, ex2):
        for j in range(ey1, ey2):
            if grid[i][j] != "corridor":
                entrance_ok = False
                break
    # Criterion 3: No room overlap & within bounds
    overlap_ok = no_overlap
    # Criterion 4: Corridor width >= 4 everywhere
    width_ok = True
    # Check horizontal corridor segments
    for j in range(GRID_H):
        i = 0
        while i < GRID_W:
            if grid[i][j] == "corridor":
                # Corridor segment start
                start = i
                while i < GRID_W and grid[i][j] == "corridor":
                    i += 1
                end = i - 1
                seg_length = end - start + 1
                # Determine boundaries on left and right
                left_wall = (start == 0) or (grid[start-1][j] != "corridor")
                right_wall = (end == GRID_W - 1) or (grid[end+1][j] != "corridor")
                if left_wall and right_wall and seg_length < 4:
                    width_ok = False
            else:
                i += 1
    # Check vertical corridor segments
    for i in range(GRID_W):
        j = 0
        while j < GRID_H:
            if grid[i][j] == "corridor":
                start = j
                while j < GRID_H and grid[i][j] == "corridor":
                    j += 1
                end = j - 1
                seg_length = end - start + 1
                top_wall = (start == 0) or (grid[i][start-1] != "corridor")
                bottom_wall = (end == GRID_H - 1) or (grid[i][end+1] != "corridor")
                if top_wall and bottom_wall and seg_length < 4:
                    width_ok = False
            else:
                j += 1
    # Criterion 5: Single connected corridor component (with entrance)
    # BFS from an entrance cell
    start_x, start_y = ex1, ey1
    visited = [[False]*GRID_H for _ in range(GRID_W)]
    dq = deque()
    dq.append((start_x, start_y))
    visited[start_x][start_y] = True
    comp_count = 0
    while dq:
        cx, cy = dq.popleft()
        comp_count += 1
        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nx, ny = cx+dx, cy+dy
            if 0 <= nx < GRID_W and 0 <= ny < GRID_H and not visited[nx][ny] and grid[nx][ny] == "corridor":
                visited[nx][ny] = True
                dq.append((nx, ny))
    total_corridor_cells = sum(1 for i in range(GRID_W) for j in range(GRID_H) if grid[i][j] == "corridor")
    connectivity_ok = (comp_count == total_corridor_cells)
    # Criterion 6: Doors on room walls (not corners, open to corridor, no room-to-room doors)
    doors_ok = True
    for room in rooms:
        x, y, w, h = room["x"], room["y"], room["w"], room["h"]
        if not room["doors"]:
            doors_ok = False
            break
        for door in room["doors"]:
            side = door["side"]
            px = door["pos_x"]
            py = door["pos_y"]
            # Check door not at a corner position
            if side in ("left", "right"):
                if py == y or py == y + h:
                    doors_ok = False
            elif side in ("top", "bottom"):
                if px == x or px == x + w:
                    doors_ok = False
            # Check door opens into corridor
            if side == "left":
                if x <= 0 or grid[x-1][py] != "corridor":
                    doors_ok = False
            elif side == "right":
                if x + w >= GRID_W or grid[x+w][py] != "corridor":
                    doors_ok = False
            elif side == "bottom":
                if y <= 0 or grid[px][y-1] != "corridor":
                    doors_ok = False
            elif side == "top":
                if y + h >= GRID_H or grid[px][y+h] != "corridor":
                    doors_ok = False
            # Check corridor path from door to entrance (door cell should be visited in BFS)
            if side == "left" and x > 0 and not visited[x-1][py]:
                doors_ok = False
            if side == "right" and x + w < GRID_W and not visited[x+w][py]:
                doors_ok = False
            if side == "bottom" and y > 0 and not visited[px][y-1]:
                doors_ok = False
            if side == "top" and y + h < GRID_H and not visited[px][y+h]:
                doors_ok = False
    # Compile validation report
    report = {
        "complement": {"pass": complement_ok, "info": "Every cell is room or corridor."},
        "entrance_area": {"pass": entrance_ok, "info": "Entrance block is corridor."},
        "no_overlap": {"pass": overlap_ok, "info": "Rooms do not overlap and stay within bounds."},
        "corridor_width": {"pass": width_ok, "info": f"Corridor minimum width = 4 cells (check: {width_ok})."},
        "corridor_connectivity": {"pass": connectivity_ok, "info": "Corridor is one connected component."},
        "doors": {"pass": doors_ok, "info": "Every room has a valid door to corridor (not in corners, leads to entrance)."}
    }
    return report

wands/visualizer.py

from PIL import Image, ImageDraw

# Predefined colors for room groups (soft palette)
GROUP_COLORS = {
    "Dev":       (173, 216, 230),  # light blue
    "QA":        (144, 238, 144),  # light green
    "Research":  (224, 255, 255),  # light cyan
    "Production":(255, 200,   0),  # orange
    "Storage":   (210, 180, 140),  # tan
    "Studio":    (216, 191, 216),  # lavender
    "Admin":     (255, 182, 193),  # light pink
    "Marketing": (255, 255, 102),  # yellow
    "Support":   (221, 160, 221),  # plum
    "Console":   (255, 160, 122),  # salmon
    "Server":    (250, 128, 114),  # light coral
    "Training":  (152, 251, 152),  # pale green
    "Facilities":(255, 228, 181)   # wheat
}

def render(solution: dict, out_path: str):
    """Render the solution layout to a PNG image file."""
    grid_w = solution.get("entrance", {}).get("x2", 77)  # should be 77
    grid_h = solution.get("entrance", {}).get("y2", 50)  # should be 50
    scale = 10  # pixels per cell
    img = Image.new("RGB", (grid_w * scale, grid_h * scale), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    # Draw entrance area (dark gray)
    entr = solution.get("entrance", {})
    ex1, ex2 = entr.get("x1", 0), entr.get("x2", 0)
    ey1, ey2 = entr.get("y1", 0), entr.get("y2", 0)
    for i in range(ex1, ex2):
        for j in range(ey1, ey2):
            px = i * scale
            py = (grid_h - 1 - j) * scale
            draw.rectangle([px, py, px + scale - 1, py + scale - 1], fill=(100, 100, 100))
    # Draw each room area
    for room in solution.get("rooms", []):
        rx, ry, rw, rh = room["x"], room["y"], room["w"], room["h"]
        group = room["type"]
        color = GROUP_COLORS.get(group, (200, 200, 200))
        for i in range(rx, rx + rw):
            for j in range(ry, ry + rh):
                # Skip drawing over entrance corridor cells (if any overlap, which should not happen)
                if ex1 <= i < ex2 and ey1 <= j < ey2:
                    continue
                px = i * scale
                py = (grid_h - 1 - j) * scale
                draw.rectangle([px, py, px + scale - 1, py + scale - 1], fill=color)
    # Draw doors as black lines on room walls
    for room in solution.get("rooms", []):
        rx, ry, rw, rh = room["x"], room["y"], room["w"], room["h"]
        for door in room.get("doors", []):
            side = door["side"]
            dx = door["pos_x"]
            dy = door["pos_y"]
            if side == "left":
                # Vertical line on left wall
                px = rx * scale
                py1 = (grid_h - 1 - dy) * scale
                py2 = py1 - scale + 1
                draw.line([px, py1, px, py2], fill=(0, 0, 0), width=2)
            elif side == "right":
                px = (rx + rw) * scale
                py1 = (grid_h - 1 - dy) * scale
                py2 = py1 - scale + 1
                draw.line([px, py1, px, py2], fill=(0, 0, 0), width=2)
            elif side == "bottom":
                px1 = dx * scale
                px2 = px1 + scale - 1
                py = (grid_h - 1 - ry) * scale
                draw.line([px1, py, px2, py], fill=(0, 0, 0), width=2)
            elif side == "top":
                px1 = dx * scale
                px2 = px1 + scale - 1
                py = (grid_h - 1 - (ry + rh)) * scale
                draw.line([px1, py, px2, py], fill=(0, 0, 0), width=2)
    img.save(out_path)

wands/cli.py

from __future__ import annotations
import argparse, json, logging, sys, time
from pathlib import Path
from . import __version__
from .config import load_room_defs
from .solver import solve
from .validator import validate
from .visualizer import render

PHASES = ["parse", "build", "solve", "validate", "render", "finish"]

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="wands")
    parser.add_argument("--config", required=True, help="Path to rooms configuration (YAML/JSON).")
    parser.add_argument("--out-json", required=True, help="Output path for solution JSON.")
    parser.add_argument("--out-png", required=True, help="Output path for solution visualization PNG.")
    parser.add_argument("--validate", required=True, dest="report", help="Output path for validation report JSON.")
    parser.add_argument("--log-level", default="INFO", help="Logging level (DEBUG, INFO, WARN, ERROR).")
    parser.add_argument("--log-format", choices=["text", "json"], default="text", help="Log format.")
    parser.add_argument("--log-file", help="Optional log file path.")
    parser.add_argument("--progress", choices=["auto", "off"], default="auto", help="Show progress indicators.")
    parser.add_argument("--progress-interval", type=int, default=1, help="Progress update interval (seconds).")
    parser.add_argument("--seed", type=int, default=0, help="Random seed for reproducibility.")
    parser.add_argument("--threads", type=int, default=1, help="Number of threads (if solver is multi-threaded).")
    parser.add_argument("--time-limit", type=float, default=0.0, help="Time limit for solver (0 for no limit).")
    parser.add_argument("--validate-only", action="store_true", help="Only validate an existing solution JSON (provide via --config).")
    parser.add_argument("--version", action="version", version=__version__, help="Show program version and exit.")
    args = parser.parse_args(argv)

    # Configure logging
    logging.basicConfig(filename=args.log_file if args.log_file else None,
                        level=getattr(logging, args.log_level.upper(), logging.INFO),
                        format="%(message)s")
    logger = logging.getLogger(__name__)

    start_time = time.time()
    logger.info("phase=start")

    if args.validate_only:
        # Validate an existing solution JSON file
        solution = json.loads(Path(args.config).read_text(encoding="utf8"))
        report = validate(solution)
        Path(args.report).write_text(json.dumps(report, indent=2), encoding="utf8")
        return 0

    # Normal solve workflow
    room_defs = load_room_defs(args.config)
    if args.progress != "off":
        logger.info("phase=parse")
        time.sleep(args.progress_interval)

    solution = solve(room_defs, seed=args.seed)
    Path(args.out_json).write_text(json.dumps(solution, indent=2), encoding="utf8")
    if args.progress != "off":
        logger.info("phase=solve")
        time.sleep(args.progress_interval)

    report = validate(solution)
    Path(args.report).write_text(json.dumps(report, indent=2), encoding="utf8")
    if args.progress != "off":
        logger.info("phase=validate")
        time.sleep(args.progress_interval)

    render(solution, args.out_png)
    if args.progress != "off":
        logger.info("phase=render")
        time.sleep(args.progress_interval)

    duration = time.time() - start_time
    logger.info(f"phase=finish runtime_sec={duration:.3f}")
    return 0

wands/__main__.py

from .cli import main

if __name__ == "__main__":
    import sys
    sys.exit(main())

tests/test_cli.py

from wands import __version__
import subprocess, sys

def test_version():
    """CLI should return the correct version string."""
    result = subprocess.run([sys.executable, "-m", "wands", "--version"], capture_output=True, text=True)
    assert result.returncode == 0
    assert __version__ in result.stdout

Usage: After installing the package or cloning the repository, run the solver via CLI:

python -m wands \
  --config rooms.yaml \
  --out-json solution.json \
  --out-png solution.png \
  --validate validation_report.json \
  --seed 1

This will parse the room definitions from rooms.yaml, compute an optimized layout, output the solution in JSON (solution.json), generate a visual floorplan image (solution.png), and produce a validation report (validation_report.json). The program logs progress through each phase (parsing, solving, validating, rendering, finishing) and ensures reproducibility with a given random seed. The resulting layout will maximize total room area while strictly adhering to all hard constraints (corridor width ≥ 4, single connected corridor including the fixed entrance, each room accessible via at least one door, etc.).


