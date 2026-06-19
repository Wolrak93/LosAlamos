# Lessons Learned — Cycle 1

## Prozess

### Chunk-Größe
The "program entire cycle at once" approach produced chunks that were too large.
The standard feature-by-feature workflow (smaller units, user tests between each) is
suspected to be more robust. The experiment continues until project end, but this is
a known risk going forward.

### master Branch
Only fully playable, stable versions should be merged to master.
Incomplete or partially-broken states belong in development only.

### ROADMAP vorher festlegen
Having the user define the ROADMAP upfront worked well.
It gave Claude precise priorities and ordering — no guessing about what matters most or what comes first.
Continue this practice for every cycle.

## Technik

### Fehlende Assets
Missing image files (sprites, icons) caused failures at many points throughout the cycle.
Assets should be created or stubbed out early — ideally before any GUI code references them.
Alternative: add a safe fallback in the asset loader that renders a colored rectangle
if the file is not found, so missing assets never crash the app.
