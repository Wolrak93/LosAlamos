# Cycle 1 — Testliste

Checkboxes zum Abhaken. Jeder Abschnitt kann separat durchgearbeitet werden.

---

## A — Automatisierbare Tests (pytest-Lücken)

### A1 — BitBoard / Move.apply()

- [x] **A1.1** `halfmove_clock` wird bei einem Schlag zurückgesetzt (kein Bauernzug, aber Figur geschlagen)
- [x] **A1.2** `halfmove_clock` wird bei Turm/Springer/Dame-Zug ohne Schlag um 1 erhöht
- [x] **A1.3** `ply`-Zähler steigt nach jedem Zug um 1
- [x] **A1.4** `side_to_move` wechselt korrekt: White→Black→White (zwei Züge = wieder White)
- [x] **A1.5** Promotion + Schlag: Bauer entfernt, gegnerische Figur entfernt, neue Figur gesetzt

### A2 — Zuggenerierung

- [x] **A2.1** Schwarzer Bauer schreitet vorwärts (rank 4 → rank 3)
- [x] **A2.2** Schwarzer Bauer schlägt diagonal
- [x] **A2.3** Schwarzer Bauer auf rank 1 → Promotion auf rank 0 → 3 Züge (Q/R/N)
- [x] **A2.4** Bauer auf a-Linie (file 0) → nur rechts-diagonaler Schlag möglich
- [x] **A2.5** Bauer auf f-Linie (file 5) → nur links-diagonaler Schlag möglich
- [x] **A2.6** Promotion + diagonaler Schlag → 3 Züge pro Schlagrichtung
- [x] **A2.7** Springer in den vier Ecken (a1, f1, a6, f6) → korrekte Zuganzahl (je 2)
- [x] **A2.8** Springer auf Randfeldern → keine Züge außerhalb des 6×6-Bretts
- [x] **A2.9** Turm schlägt Figur und stoppt dort (kann nicht weiter)
- [x] **A2.10** Dame diagonal blockiert durch eigene Figur
- [x] **A2.11** Dame schlägt diagonal am Ende des Strahls
- [x] **A2.12** Legale Zuganzahl in der Normalstartstellung = 16 (12 Bauern + 4 Springer)
- [x] **A2.13** Fesselung (Pin): Figur kann nicht ziehen, wenn sie den König dem Schach aussetzt
- [x] **A2.14** Doppelschach: Nur König-Züge sind legal
- [x] **A2.15** König kann nicht neben den gegnerischen König ziehen
- [x] **A2.16** König kann unverteidigte Figur schlagen
- [x] **A2.17** König kann verteidigte Figur nicht schlagen
- [x] **A2.18** König in der Ecke hat genau 3 mögliche Zielfelder (wenn alle frei)

### A3 — Spielzustand / Remisbedingungen

- [x] **A3.1** `halfmove_clock == 99` → kein Remis
- [x] **A3.2** Gleiche Position 2× in History → kein Draw (erst beim 3. Mal)
- [x] **A3.3** Unzureichendes Material: K+N vs. K → Remis
- [x] **A3.4** Unzureichendes Material: K+N vs. K+N → Remis
- [x] **A3.5** Kein Remis: K+2N vs. K (zwei Springer = ausreichendes Material)
- [x] **A3.6** Kein Remis: K+Bauer vs. K
- [x] **A3.7** Zeitüberschreitung bei unzureichendem Material → Remis (nicht Niederlage)
- [x] **A3.8** Matt hat Vorrang vor der 50-Züge-Regel (clock=100 + Matt → Matt, nicht Remis)
- [x] **A3.9** `play_move` hängt Zobrist-Hash an `position_history` an
- [x] **A3.10** Nach Schlag: neuer Zobrist-Hash unterscheidet sich von vorherigem

### A4 — Bots

- [x] **A4.1** RandomBot gibt Zug zurück, auch wenn nur 1 legaler Zug existiert
- [x] **A4.2** GreedyBot: Promotion + Schlag werden kombiniert bewertet (captured_value + promo_gain)
- [x] **A4.3** GreedyBot: Wenn alle Züge Score 0 haben, wird trotzdem ein legaler Zug zurückgegeben
- [x] **A4.4** GreedyBot: Promotiert immer zur Dame, auch bei mehreren gleichwertigen Optionen
- [x] **A4.5** GreedyBot: Rückgabe ist stets ein gültiger legaler Zug (Regression-Guard)

### A5 — Startaufstellungen

- [x] **A5.1** Normale Aufstellung: exakt 12 Bauern, 4 Springer, 4 Türme, 2 Damen, 2 Könige
- [x] **A5.2** Normale Aufstellung: `side_to_move == WHITE`
- [x] **A5.3** Normale Aufstellung: `halfmove_clock == 0`
- [x] **A5.4** Random-sym: Weiße Grundreihe enthält exakt 1K, 1D, 2T, 2S
- [x] **A5.5** Random-asym: Grundreihen sind in ≥1 von 20 Durchläufen unterschiedlich

---

## B — Manuelle GUI-Tests

### B1 — Hauptmenü

- [x] **B1.1** Titel "LOS ALAMOS" und Untertitel "Schachvariante · 6×6" sichtbar
- [x] **B1.2** Dropdown Weiß: Mensch / RandomBot / GreedyBot auswählbar
- [x] **B1.3** Dropdown Schwarz: dieselben Optionen, unabhängig von Weiß
- [x] **B1.4** Nur ein Dropdown gleichzeitig geöffnet; zuletzt geöffnetes liegt oben (kein Overlap-Bug)
- [x] **B1.5** Namensfeld Weiß: Tippen fügt Zeichen hinzu, Backspace löscht letztes Zeichen
- [x] **B1.6** Namensfeld Schwarz: s.o.
- [x] **B1.7** Zeitfeld "min": nimmt nur Ziffern an, max. 3 Stellen
- [x] **B1.8** Zeitfeld "sek": nimmt nur Ziffern an, max. 3 Stellen
- [x] **B1.9** Beide Zeitfelder leer → Spiel startet ohne sichtbare Uhren
- [x] **B1.10** Aufstellungs-Buttons: Klick markiert Button (grüner Rahmen), vorherige Markierung erlischt
- [x] **B1.11** Standard-Auswahl beim Öffnen: "Normal" ist vorausgewählt
- [x] **B1.12** Aktives Eingabefeld zeigt Cursor-Strich
- [x] **B1.13** Klick auf "Match starten" → Spielbildschirm öffnet sich

### B2 — Spielbildschirm — Grundfunktionen

- [x] **B2.1** Brett: weiße Figuren unten (rank 1), schwarze oben (rank 6)
- [x] **B2.2** Koordinaten: Buchstaben a–f unter dem Brett, Zahlen 1–6 links
- [x] **B2.3** Klick auf eigene Figur → Feld gelb markiert
- [x] **B2.4** Nach Auswahl: legale Züge als Punkte (leere Felder) und farbig (Schlagfelder)
- [x] **B2.5** Klick auf legales Ziel → Zug wird ausgeführt, Figur bewegt sich
- [x] **B2.6** Klick auf dieselbe Figur ein zweites Mal → Auswahl aufgehoben
- [x] **B2.7** Klick auf andere eigene Figur → Auswahl wechselt zur neuen Figur
- [x] **B2.8** Klick auf leeres Nicht-Zielfeld → Auswahl aufgehoben
- [x] **B2.9** Klick außerhalb des Bretts → kein Absturz, Auswahl aufgehoben
- [x] **B2.10** Während Bot-Zug: Klick aufs Brett führt keinen menschlichen Zug aus
- [x] **B2.11** Bot-Zug erscheint nach ca. 300 ms (sichtbare Verzögerung)

### B3 — Info-Panel

- [x] **B3.1** Spielernamen korrekt angezeigt (aus dem Menü übernommen)
- [x] **B3.2** Bot-Bezeichnung korrekt (z.B. "RandomBot · Schwarz")
- [x] **B3.3** Uhren: aktiver Spieler zählt runter, inaktiver steht still
- [x] **B3.4** Aktive Uhr: grüner Hintergrund, weiße Schrift
- [x] **B3.5** Inaktive Uhr: beiger Hintergrund, gedämpfte Schrift
- [x] **B3.6** Inkrement wird nach Zug zur Uhr des ziehenden Spielers addiert
- [x] **B3.7** Keine Zeitkontrolle: Uhren nicht sichtbar
- [x] **B3.8** Geschlagene Figuren: Nach Schlag erscheint Icon beim überlegenen Spieler
- [x] **B3.9** Gleichstand Material: keine Icons angezeigt
- [x] **B3.10** Eval-Bar nur sichtbar für GreedyBot-Spieler (nicht für Mensch / RandomBot)
- [x] **B3.11** Eval-Bar bewegt sich nach Materialveränderung korrekt
- [x] **B3.12** "← Zurück zum Menü"-Button am unteren Rand → kehrt ins Menü zurück

### B4 — Zughistorie & 50-Züge-Anzeige

- [x] **B4.1** Weißer Zug in linker Spalte, schwarzer in rechter (PGN-Format mit Nummerierung)
- [x] **B4.2** Bauernzug: nur Zielfeld angezeigt (z.B. "a3")
- [x] **B4.3** Bauernschlag: "axb3"-Format
- [x] **B4.4** Figurenzug: Stückbuchstabe + Ziel (z.B. "Nc3")
- [x] **B4.5** Figur schlägt: "Nxc3"-Format
- [x] **B4.6** Promotion: "e6=Q"-Format
- [x] **B4.7** Aktueller Halbzug ist farblich hervorgehoben
- [x] **B4.8** Bei langen Partien: neueste Züge immer sichtbar (automatisches Scrollen)
- [x] **B4.9** 50-Züge-Zähler: zeigt korrekte verbleibende Halbzüge (100 am Anfang)
- [x] **B4.10** 50-Züge-Zähler: springt zurück auf 100 nach Bauernzug oder Schlag

### B5 — Promotions-Dialog

- [x] **B5.1** Weißer Bauer erreicht rank 6 → Brett abgedunkelt, drei Kreise erscheinen
- [x] **B5.2** Kreise überlagern die Promotionsspalte (korrekte Position)
- [x] **B5.3** Reihenfolge von oben nach unten: Dame → Turm → Springer
- [x] **B5.4** Hover-Effekt: orangener Hintergrund auf dem Kreis unter der Maus
- [x] **B5.5** Klick auf Dame → Bauer wird zur Dame, Spiel geht weiter
- [x] **B5.6** Klick auf Turm → Bauer wird zum Turm
- [x] **B5.7** Klick auf Springer → Bauer wird zum Springer
- [x] **B5.8** Klick außerhalb der Kreise → Dialog geschlossen, Bauer an Ausgangsposition zurück
- [x] **B5.9** Schwarzer Bauer erreicht rank 1 → Kreise gehen nach oben (nicht nach unten)
- [x] **B5.10** RandomBot promotiert ohne Dialog automatisch
- [x] **B5.11** GreedyBot promotiert immer zur Dame
- [x] **B5.12** Nach Promotion-Abbruch: kein Halbzug gezählt, Brett wieder normal

### B6 — Spielende-Overlay

- [x] **B6.1** Schachmatt (Weiß verliert) → "Schwarz gewinnt" + "Schachmatt"
- [x] **B6.2** Schachmatt (Schwarz verliert) → "Weiß gewinnt" + "Schachmatt"
- [x] **B6.3** Patt → "Remis" + "Patt"
- [x] **B6.4** Zeitüberschreitung → "Weiß/Schwarz gewinnt" + "Zeit abgelaufen"
- [x] **B6.5** Zeitüberschreitung + unzureichendes Material → "Remis" + "Unzureichendes Material"
- [x] **B6.6** 50-Züge-Regel → "Remis" + "50-Züge-Regel"
- [x] **B6.7** Dreifache Stellungswiederholung → "Remis" + "Dreifache Stellungswiederholung"
- [x] **B6.8** Unzureichendes Material mid-game → "Remis" + "Unzureichendes Material"
- [x] **B6.9** Overlay-Hintergrund semi-transparent (Brett dahinter noch erkennbar)
- [x] **B6.10** "Neues Spiel"-Button → Spiel startet sofort mit denselben Einstellungen
- [x] **B6.11** "← Menü"-Button → zurück ins Hauptmenü
- [x] **B6.12** Nach "Neues Spiel": Uhren auf Ausgangszeit zurückgesetzt

### B7 — Bot-vs-Bot

- [x] **B7.1** RandomBot vs. RandomBot: Partie spielt bis zum Ende, kein Freeze / Absturz
- [x] **B7.2** GreedyBot vs. GreedyBot: Partie spielt bis zum Ende
- [x] **B7.3** RandomBot vs. GreedyBot mit Zeitkontrolle: Uhren laufen korrekt, Partie endet
- [x] **B7.4** Bot-Zug wird nicht ausgeführt, solange Promotions-Dialog offen ist

### B8 — Zufalls-Startaufstellungen

- [x] **B8.1** "Sym. Zufall": Weiß und Schwarz haben dieselbe Grundreihe (visuell erkennbar)
- [x] **B8.2** "Asym. Zufall": Grundreihen sind üblicherweise unterschiedlich (mehrfach testen)
- [x] **B8.3** In allen 3 Modi: korrekte Bauern auf rank 2 (Weiß) und rank 5 (Schwarz)
- [x] **B8.4** Keine Figuren in den mittleren Reihen zu Spielbeginn

---

## Fortschritt

- Gesamt: 104 Tests (38 automatisierbar, 66 manuell)
- Erledigt: 0 / 104
