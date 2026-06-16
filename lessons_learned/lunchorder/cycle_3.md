# Lessons Learned — Cycle 3: Menu Management

## What was built
- Food item library (internal, reusable items managed by operators)
- Weekly menu setup: 5-column Mon–Fri grid, operator can add/remove items per day
- PDF upload & Claude API extraction: catering PDFs parsed via `pypdf` + `claude-opus-4-6`,
  extracted items stored as pending `MenuEntry` rows
- AI review screen: operator reviews, edits, confirms or deletes extracted entries
- Menu navigation & user view: read-only weekly view with role-aware week navigation
- Alembic migration: `status` column on `menu_entries` (`"confirmed"` | `"pending"`)

---

## Process Lessons

### 1. TODO.md structure with locked design decisions worked well
**Observation:** Locking design decisions (week identification, food item types, day mapping,
Claude prompt template, DB migration plan) at the top of TODO.md before any coding began
prevented ambiguity and scope creep throughout the cycle.
**Advice:** Keep this pattern in future cycles. Design decisions belong at the top of
TODO.md, not scattered in commit messages or chat history.

### 2. Sequential feature branches with explicit dependencies caused no problems
**Observation:** The branch sequence had clear dependencies (TODO 3 → TODO 2 → TODO 1 etc.),
but this did not cause friction in practice. Each branch was small enough that waiting for
the previous one was never a bottleneck.
**Advice:** Explicit dependency declarations in the TODO ("Depends on: TODO N") are worth
keeping even when the dependencies turn out not to be a practical problem — they make the
build order self-documenting.

---

## Technical Lessons

### 3. Claude API (PDF extraction) is fast and simple to integrate
**Observation:** The PDF extraction via `pypdf` + Claude API worked after a single bug fix
and was quicker and simpler than expected. The structured JSON prompt (`Return ONLY the JSON
array`) was reliable without additional parsing logic.
**Advice:** For future features involving structured data extraction from unstructured text,
reach for the Claude API first. The pattern (extract text → prompt with schema → parse JSON
response) is low-friction and robust. Mocking the API call in tests with `unittest.mock.patch`
kept the test suite fast and free of external dependencies.

### 4. Pay close attention to UI contrast and readability
**Issue:** Two separate contrast problems appeared during the cycle:
1. A light-colored button with light-colored text (unreadable)
2. A dark-green button placed on a dark-green background (invisible)
Neither issue was caught before the user noticed it manually.
**Fix:** After implementing any new button, badge, or interactive element, verify that:
- Text color has sufficient contrast against the button/background color
- The element is visually distinguishable from its surrounding background
- This applies especially to colored states (primary, success, warning) placed inside
  colored containers (cards, panels, sidebars)
**Advice:** When choosing a color for a UI element, explicitly ask: "What is the background
behind this element?" Never assume a component looks correct in isolation — check it in
its actual rendered context.

---

## What went well
- The TODO structure and branch sequence were well-designed: no confusion, no rework.
- The Claude API integration was straightforward and the result was immediately usable.
- 152 backend tests and 4 frontend Vitest tests pass cleanly at cycle end.
- Locking the Claude prompt template in TODO.md (including the exact JSON schema) meant
  the implementation matched the spec without ambiguity.
