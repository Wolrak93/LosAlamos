# Lessons Learned — Cycle 5

## What went well

- The cycle ran very smoothly with almost no corrections needed.
- The upfront design decisions (locked in TODO.md before coding) meant there was little ambiguity during implementation.
- All four feature branches were implemented and passed lint + tests on the first attempt or with only minor fixes.
- The tab-based SettingsPage rewrite was clean and required no rework.

## What could be improved

### Branch dependency discipline
During TODO 2 (`feature/order-utils`) and TODO 3 (`feature/orders-page`), work on TODO 3 was started before TODO 2 was fully merged into `development`. This created unnecessary complexity — shared code (API client, utilities) was being developed in one branch while a dependent branch was already branching off.

**Rule going forward:** Before starting a branch that is listed as "Depends on X", verify that X is fully merged into `development` first. Check `git log development` if unsure.

## Architectural decisions

No regrets. The existing stack, data model, and UI structure all held up well in Cycle 5.

## For Cycle 6

No major process changes needed. Continue with the same workflow:
- Lock design decisions in TODO.md before coding
- One feature branch per TODO item
- Pause for manual testing after each branch before merging
