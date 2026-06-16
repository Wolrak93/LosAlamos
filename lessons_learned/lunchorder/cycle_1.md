# Lessons Learned — Cycle 1: Project Foundation

## What was built
- React + Vite (TypeScript) frontend scaffold with Tailwind CSS, shadcn/ui, react-i18next (DE/EN), ESLint, Prettier
- SQLAlchemy models for all core entities + Alembic migrations
- Docker Compose setup (FastAPI + React/nginx + PostgreSQL)
- Local development documentation for Windows

---

## Process Lessons

### 1. Communication language
**Issue:** The primary developer finds it hard to express himself in English.
**Fix:** Claude communicates with the user in German at all times. All documentation,
code comments, commit messages, and files stay in English for English-speaking colleagues.
**Status:** Added to RULES.md.

### 2. Never merge feature branches without explicit user approval
**Issue:** Claude merged feature branches into development immediately after implementation,
without giving the user a chance to test first. Bugs could have gone undetected.
**Fix:** When implementation is done, Claude must stop, summarize what was done, and
explicitly ask the user to test and confirm before any merge happens.
Only after the user gives explicit approval does the merge proceed.
**Status:** Added to RULES.md under FEATURE BRANCHES.

---

## Technical Lessons

### 3. Docker Compose on Windows — nginx and path issues
**Observation:** Several small issues appeared during `docker compose build` / `docker compose up`
on Windows (nginx config, missing Alembic run step). These required a dedicated verification task.
**Advice:** For future cycles, always include a Docker smoke-test step early. Do not assume
the compose setup from a previous cycle still works after adding new services or volumes.

### 4. Alembic autogenerate requires a running database
**Observation:** `alembic revision --autogenerate` needs a live Postgres connection.
Local dev setup must have Docker running before any migration work.
**Advice:** Document this dependency explicitly in task descriptions that touch migrations.

### 5. Windows CRLF line endings break Prettier/ESLint
**Observation:** All frontend files had Windows-style CRLF line endings. ESLint with the
Prettier plugin reported 222 errors (`Delete ␍`) on the first test run.
**Fix:** Added `.gitattributes` with `* text=auto eol=lf` to enforce LF line endings
for all text files across all platforms.
**Advice:** Always add `.gitattributes` as the very first commit in any new project
when Windows developers are involved.

---

## What went well
- The task breakdown into small, focused feature branches worked cleanly.
- Having design decisions locked at the top of TODO.md prevented scope creep.
- The local dev docs task paid off immediately — setup on Windows was straightforward
  once the guide existed.
