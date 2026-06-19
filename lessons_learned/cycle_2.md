# Lessons Learned — Cycle 2

## Prozess

### Ganzer Cycle auf einmal: funktioniert ab Cycle 2
The "program entire cycle at once" approach worked well for Cycle 2.
Hypothesis: Cycle 1 was uniquely difficult because it required building a complete
playable product from scratch. From Cycle 2 onwards, a working codebase already
exists — the scope per cycle is smaller and better-bounded, making the all-at-once
approach manageable.
**Going forward:** keep the all-at-once approach for Cycle 2+. Only break a cycle
into sub-cycles if scope unexpectedly grows to Cycle-1 levels.

### Master branch bleibt für Vollversionen
Master only receives complete, tested, stable cycles. No partial states.
Continue this practice unconditionally.

## Tests

### Automatisierte Tests während der Implementierung
Automated pytest tests should be written during implementation (TDD), not collected
at the end. The end-of-cycle test run was an unnecessary extra step.
**Going forward:** apply the TDD skill from the start of each feature.

### Testliste automatisch erstellen
The manual test checklist (`docs/cycleN-testlist.md`) was useful but had to be
explicitly requested by the user.
**Going forward:** at the end of each cycle's planning phase, automatically generate
the testlist before implementation starts — both the automated section (A) and the
manual GUI section (B). Do not wait for the user to ask.

### Manuelle Tests bleiben am Ende
Manual (GUI) tests are done by the user after full cycle implementation.
This workflow is correct — do not change it.
