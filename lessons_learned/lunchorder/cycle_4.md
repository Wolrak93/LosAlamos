# Lessons Learned — Cycle 4: Ordering System

## What was built
- Orders per day: users/guests/operators can place and modify orders with quantity
- Order cutoff logic: default Thursday 4pm (week before), configurable per week by operators
- Pricing engine: standard (4.60€), reduced (2.50€ for apprentices/trainees), free (guests)
- Reduced pricing flag assigned per user by operators
- Global price configuration by operators (Settings page)
- User management UI for operators (Settings page)
- Deadline edit UI in WeeklyMenuEditorPage
- Ordering UI in MenuPage with cutoff banner

---

## Process Lessons

### 1. TODO.md must be the source of truth — not .superpowers/
**Issue:** After the Superpowers plugin was introduced, task planning was written into the
`.superpowers/` folder instead of `TODO.md`. This caused a mismatch at the start of the
Cycle 4 lessons learned session: the project's canonical task list was out of date.
**Fix:** Always write the cycle's TODO items into `TODO.md` at the project root, regardless
of what the Superpowers workflow creates internally. `.superpowers/` is a plugin artifact,
not the project's task record.
**Advice:** Before starting any cycle, confirm that `TODO.md` contains the full task list.

### 2. Pause after each feature branch for manual testing
**Issue:** All feature branch sub-tasks were implemented back-to-back without stopping for
the user to test intermediate results. The user wanted to test between tasks.
**Fix:** After completing each feature branch and before starting the next one, explicitly
stop and ask the user to test. Only continue when the user confirms the feature works or
gives approval.
**Advice:** The CLAUDE.md rule "ask the user before merging" applies not just to the merge
itself but also to the pause for testing. Make the pause visible and deliberate.

---

## Technical Lessons

### 3. GitHub SSH connection may be blocked by corporate firewall
**Issue:** SSH connections to GitHub can fail silently when the corporate firewall blocks
outbound SSH traffic. This is not a config issue on Claude's side — it requires an
admin-approved internet exception.
**Fix:** If `git push` or any GitHub remote operation fails, the first question to ask is:
"Hast du gerade die Admin-Internetfreigabe, die die SSH-Verbindung zu GitHub erlaubt?"
Do not attempt alternative workarounds (HTTPS fallback, config changes) before checking this.
**Advice:** Corporate firewall blocks are common and transient — always check access first.

---

## Superpowers Plugin Assessment

### 4. Superpowers brainstorming improved requirements quality significantly
**Observation:** The Superpowers brainstorming feature ("superpowers:brainstorming") led to
more detailed exploration of ambiguities in requirements before implementation began. Less
guessing, more alignment. The UI planning feature in particular was very useful for designing
screens before writing code.
**Constraint:** The brainstorming skill uses significantly more tokens than normal. Never
invoke it automatically — always ask the user first whether they want to use it.
**Advice:** Default to asking "Soll ich das Brainstorming-Feature verwenden?" before any
feature that involves UI design or ambiguous requirements.

### 5. Superpowers plugin overall: keep it enabled
**Assessment:** Despite the TODO.md issue (see Lesson 1), the plugin brought net improvement
to the cycle: better requirements clarification, less rework, better UI planning.
The fix (Lesson 1) addresses the main downside without requiring the plugin to be disabled.

---

## What went well
- No major bugs or unexpected rework during the cycle.
- Pricing engine, cutoff logic, and order flow worked as designed without significant issues.
- Superpowers brainstorming led to better upfront clarity and less mid-cycle confusion.
- The cycle overall was smooth and well-structured.
