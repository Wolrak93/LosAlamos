# Project Roadmap — LosAlamos

## Goal
Eine vollständig spielbare Implementierung der Los Alamos Schachvariante (6x6-Brett,
keine Läufer) mit pygame-GUI, Main Menu, zwei einfachen Bots, und als solide
Performance-Grundlage für stärkere Bots in späteren Cycles.

## Development Cycles

### Cycle 1 — Fundament: Spielengine + GUI + Basic Bots

**Ziel:** Vollständig spielbares Los Alamos Schach.

- [ ] Task 1: Project Setup
      uv-Projekt, pygame, pytest, ruff, Ordnerstruktur
      (src/engine/, src/gui/, src/bots/, tests/)

- [ ] Task 2: Bitboard Engine — Board-Repräsentation
      - 10 Bitboards (5 Figurentypen × 2 Farben): King, Queen, Rook, Knight, Pawn
      - Figurenwerte: P=1, N=3, R=5, Q=9
      - Board-State: aktive Farbe, Halbzugzähler, Positionshistorie

- [ ] Task 3: Zuggenerierung
      - Bauer: 1 Schritt vorwärts, diagonales Schlagen, Promotion (Dame/Turm/Springer)
      - Turm: gleitende Angriffe (horizontal/vertikal)
      - Dame: gleitende Angriffe (horizontal/vertikal + diagonal)
      - Springer: vorberechnete Angriffstabelle
      - König: vorberechnete Angriffstabelle
      - Legale-Zug-Filter (König darf nach Zug nicht im Schach stehen)

- [ ] Task 4: Spielzustand & Unentschieden-Bedingungen
      - Schach, Schachmatt, Patt-Erkennung
      - Unzureichendes Material (König allein; König + Springer)
      - Dreifache Stellungswiederholung
      - 50-Züge-Regel

- [ ] Task 5: Startaufstellungen
      - Normal: T-S-D-K-S-T (a1–f1)
      - Zufällig symmetrisch (beide Seiten gleiche zufällige Backrow)
      - Zufällig asymmetrisch (beide Seiten unabhängig zufällige Backrow)

- [ ] Task 6: Bots
      - RandomBot: gleichmäßig zufälliger legaler Zug
      - GreedyBot:
        * Bester Materialgewinn: Schlagzug, Promotion, oder Schlag+Promotion
        * Materialgewinn = Wert der geschlagenen Figur + Promotiongewinn (Promotion von Bauer zur Dame: +8)
        * Schachmatt in 1 wird erkannt (hat Priorität vor allem anderen)

- [ ] Task 7: Main Menu (GUI)
      - Spielerauswahl Weiß/Schwarz (Mensch / RandomBot / GreedyBot)
      - Namenseingabe (für Spieler und Bots)
      - Zeitkontrolle: Ganzzahl-Feld "Minuten" + Ganzzahl-Feld "Inkrement (s)"
        Option "Keine Zeitkontrolle"
      - Startaufstellung wählen (Normal / Zufällig sym. / Zufällig asym.)
      - "Match starten"-Knopf

- [ ] Task 8: Spielbildschirm (GUI)
      - Brett mit Sprites (user_input/assets/)
      - Klick-zum-Auswählen + Klick-zum-Ziehen
      - Legale Züge hervorheben
      - Uhren (Weiß und Schwarz)
      - Spielernamen
      - Promotions-Dialog (Dame / Turm / Springer)
      - Game-Over-Overlay (Ergebnis + Grund)
      - "Zurück ins Menü"-Knopf

- [ ] Task 9: Integration & Test-Suite
      - Engine ↔ GUI-Verbindung
      - Vollständige pytest-Abdeckung für Engine und Bots

### Cycle 2 — Stärkere Bots

- [ ] Evaluierungsfunktionen (Material, Positionstabellen, Mobilität)
- [ ] Minimax mit Alpha-Beta-Pruning
- [ ] Monte-Carlo Tree Search (MCTS)
- [ ] Mehrere benannte Bot-Persönlichkeiten

### Cycle 3 — Endspiel-Tablebase

- [ ] Retrograde-Analyse-Engine
- [ ] Tablebase für ≤4 Figuren generieren (≤5/6 wenn machbar)
- [ ] Tablebase-Lookup in Bot-Suche integrieren

### Cycle 4 — Neural Network Bot (optional)

- [ ] Policy/Value-Netzwerk
- [ ] Self-Play-Training
- [ ] MCTS + NN (AlphaZero-Stil)

## Open Questions
keine
