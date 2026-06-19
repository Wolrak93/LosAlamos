# Cycle 2 — Testliste

Checkboxes zum Abhaken. Jeder Abschnitt kann separat durchgearbeitet werden.

---

## A — Automatisierbare Tests (pytest)

### A1 — Evaluator: Material

- [x] **A1.1** Symmetrische Stellung (nur K vs. K) → Score 0
- [x] **A1.2** Weiß hat eine extra Dame → Score +900
- [x] **A1.3** Schwarz hat einen extra Turm → Score -500
- [x] **A1.4** Symmetrische Stellung mit je 1 Turm → Score 0
- [x] **A1.5** Weiß hat einen extra Bauern → Score +100
- [x] **A1.6** Weiß hat einen extra Springer → Score +300

### A2 — Evaluator: Positional (Piece-Square Tables)

- [x] **A2.1** Weißer Springer im Zentrum (c3 = sq.14) bewertet besser als am Rand (a2 = sq.6)
- [x] **A2.2** Symmetrische Stellung (Springer auf c3 vs. gespiegeltes c4) → PST-Anteil 0
- [x] **A2.3** Weißer Bauer auf Rank 4 bewertet besser als Bauer auf Rank 1 (Fortschrittsbonus)
- [x] **A2.4** Endspiel-PST aktiv wenn ≤6 Figuren total: König erhält Zentralbonus statt Eckenbonus

### A3 — Evaluator: Mobility

- [x] **A3.1** Seite mit mehr legalen Zügen erhält höheren Score (Weiß-Dame im Zentrum vs. kein Zusatz)
- [x] **A3.2** Symmetrische Startstellung → Mobility-Anteil = 0 (beide Seiten 16 Züge)
- [x] **A3.3** Additivität: `Evaluator(mat+pos+mob).evaluate(b)` == Summe der drei Einzelkomponenten

### A4 — MinimaxBot

- [x] **A4.1** Gibt immer einen legalen Zug zurück (Startstellung, 1s Budget)
- [x] **A4.2** Findet Schachmatt in 1 (Testposition aus dem Plan: Turm f1, Dame a5, schwarzer König f6)
- [x] **A4.3** Hält Zeitbudget ein: elapsed < 3s bei time_budget_seconds=1.0 (großzügige Toleranz)
- [x] **A4.4** Gibt legalen Zug zurück bei sehr kurzem Budget (0.001s) — kein Absturz, kein Hänger
- [x] **A4.5** Gibt legalen Zug zurück wenn nur 1 legaler Zug existiert (Zugzwang-Situation)
- [x] **A4.6** Greift hängende Figur: freistehende Dame des Gegners wird geschlagen (Materialgewinn erkannt)

### A5 — MCTSBot

- [x] **A5.1** Gibt immer einen legalen Zug zurück (Startstellung, 1s Budget)
- [x] **A5.2** Findet Schachmatt in 1 mit ausreichend Zeit (5s Budget, gleiche Testposition wie A4.2)
- [x] **A5.3** Hält Zeitbudget ein: elapsed < 3s bei time_budget_seconds=1.0
- [x] **A5.4** Gibt legalen Zug zurück wenn nur 1 legaler Zug existiert

### A6 — Personalities & calculate_time_budget

- [x] **A6.1** Alle 6 Factories erzeugen korrekten Typ: Fermi/von Neumann/Oppenheimer → MinimaxBot, Feynman/Teller/Bethe → MCTSBot
- [x] **A6.2** `ALL_SCIENTISTS` hat genau 6 Einträge
- [x] **A6.3** `calculate_time_budget(None, 1)` → 120.0 (kein Clock: 2 Minuten)
- [x] **A6.4** `calculate_time_budget(60.0, 1)` ≈ 1.6s (80 % / 30 Frühzüge)
- [x] **A6.5** `calculate_time_budget(30.0, 40)` ≈ 3.0s (Spätphase: 10 % der Restzeit)
- [x] **A6.6** `calculate_time_budget(60.0, 1, increment_seconds=2.0)` ≈ 3.6s (1.6 + 2.0)
- [x] **A6.7** Alle 6 Bots spielen eine vollständige Partie gegen RandomBot ohne Absturz (0.1s Budget)
- [x] **A6.8** Alle 6 Bots geben ausschließlich legale Züge zurück (Assertion per Zug)

### A7 — GroupedDropdown Widget

- [x] **A7.1** `.value` gibt den ersten auswählbaren Eintrag zurück bei `selected=0` (Header übersprungen)
- [x] **A7.2** `.value` ändert sich korrekt wenn `selected` auf einen anderen Index gesetzt wird
- [x] **A7.3** Header-Einträge erhöhen den selectable-Index nicht: `selected=2` verweist auf dritten auswählbaren Eintrag (nicht den dritten Gesamt-Eintrag)

### A8 — Regressionstests: Bot-Interface-Update

- [x] **A8.1** Alle Tests aus `tests/test_bots.py` bestehen weiterhin (keine Regression durch Interface-Änderung)
- [x] **A8.2** `RandomBot.choose_move(board, time_budget_seconds=0.5)` gibt legalen Zug zurück
- [x] **A8.3** `GreedyBot.choose_move(board, time_budget_seconds=0.5)` gibt legalen Zug zurück

---

## B — Manuelle GUI-Tests

### B1 — Hauptmenü: GroupedDropdown

- [x] **B1.1** Standard-Auswahl: "Mensch" angezeigt (kein Bot vorausgewählt)
- [x] **B1.2** Klick auf Dropdown öffnet Liste mit 3 Gruppen: „── MENSCH ──", „── BASIS-BOTS ──", „── WISSENSCHAFTLER ──"
- [x] **B1.3** Gruppen-Header visuell abgesetzt: gedämpfte Farbe, kleiner Text, kein Hover-Effekt
- [x] **B1.4** Klick auf Gruppen-Header: Dropdown schließt sich ohne Auswahländerung
- [x] **B1.5** Wissenschaftler-Einträge zeigen Algorithmus-Info rechts (z.B. „Minimax · Material" für Fermi)
- [x] **B1.6** Aktuell ausgewählter Eintrag ist farblich hervorgehoben (ACCENT_LIGHT-Hintergrund)
- [x] **B1.7** Klick auf „Fermi" → Dropdown schließt, „Fermi" wird im Feld angezeigt
- [x] **B1.8** Weiß- und Schwarz-Dropdown vollständig unabhängig (z.B. Weiß = Oppenheimer, Schwarz = Bethe)
- [x] **B1.9** Bereits offenes Dropdown schließt sich beim Klick außerhalb (Z-Order-Verhalten aus Cycle 1 erhalten)
- [x] **B1.10** Nach Auswahl eines Wissenschaftlers: „Match starten" startet das Spiel ohne Fehler

### B2 — Spielen gegen Wissenschaftler-Bots

- [x] **B2.1** Mensch (Weiß) vs. Fermi (Schwarz): Bot zieht legal, kein Absturz
- [x] **B2.2** Mensch (Weiß) vs. von Neumann (Schwarz): Bot zieht legal
- [x] **B2.3** Mensch (Weiß) vs. Oppenheimer (Schwarz): Bot zieht legal
- [x] **B2.4** Mensch (Weiß) vs. Feynman (Schwarz): Bot zieht legal
- [x] **B2.5** Mensch (Weiß) vs. Teller (Schwarz): Bot zieht legal
- [x] **B2.6** Mensch (Weiß) vs. Bethe (Schwarz): Bot zieht legal
- [x] **B2.7** Bot-Name korrekt im Info-Panel (z.B. „Fermi · Schwarz", nicht „MinimaxBot")
- [x] **B2.8** Wissenschaftler-Bot promotiert automatisch ohne Dialog (kein Promotions-Overlay bei Bot-Zug)
- [x] **B2.9** Game-Over-Overlay erscheint korrekt nach Wissenschaftler-Zug (Matt/Patt/Remis)
- [x] **B2.10** Letzter Bot-Zug wird auf dem Brett farblich hervorgehoben (Last-Move-Highlight)
- [x] **B2.11** Nach Bot-Zug: menschlicher Spieler kann sofort weiterziehen (kein Freeze, kein Klick-Block)

### B3 — Zeitverhalten / Time Budget

- [x] **B3.1** Ohne Zeitkontrolle: Bot denkt spürbar mehrere Sekunden (kein sofortiger Zug)
- [ ] **B3.2** Mit 1 Min Zeitkontrolle: Bot verwendet deutlich weniger als die gesamte Restzeit pro Zug
- [x] **B3.3** Bot-Uhr läuft während der Denkzeit weiter (Thread-Verhalten aus Cycle 1 erhalten)
- [x] **B3.4** Bot überschreitet nie die gesamte Restzeit — keine Zeitüberschreitung durch Denkzeit allein
- [x] **B3.5** Mit Inkrement (z.B. 2s): Bot nutzt sichtbar leicht mehr Zeit pro Zug als ohne Inkrement
- [x] **B3.6** Langes Spiel (>30 Züge): Bot wird sparsamer — Denkzeit pro Zug nimmt ab (10%-Modus)

### B4 — Bot vs. Bot (Wissenschaftler)

- [x] **B4.1** Fermi vs. Feynman: Partie spielt bis zum Ende, kein Freeze / Absturz
- [x] **B4.2** von Neumann vs. Teller: Partie endet in endlicher Zeit
- [x] **B4.3** Oppenheimer vs. Bethe: Partie endet korrekt (Matt, Patt oder Remis)
- [x] **B4.4** Fermi vs. GreedyBot: Partie endet korrekt
- [x] **B4.5** Zughistorie wird in Bot-vs-Bot-Partien korrekt befüllt (alle Züge in PGN-Format sichtbar)

### B5 — Info-Panel mit Wissenschaftler-Bots

- [x] **B5.1** Eval-Bar erscheint nicht für Wissenschaftler-Bots (nur GreedyBot zeigt Eval-Bar — Cycle-1-Verhalten erhalten)
- [x] **B5.2** Geschlagene-Figuren-Anzeige aktualisiert sich nach Wissenschaftler-Schlag
- [x] **B5.3** Zughistorie zeigt Wissenschaftler-Züge korrekt im PGN-Format (inkl. Schlagzeichen, Promotion)
- [x] **B5.4** „← Zurück zum Menü" funktioniert auch während laufender Wissenschaftler-Partie

---

## Fortschritt

- Gesamt: 73 Tests (37 automatisierbar, 36 manuell)
- Erledigt: 72 / 73 (37 A-Tests automatisch ✅, 35 B-Tests manuell ✅, B3.2 offen)
