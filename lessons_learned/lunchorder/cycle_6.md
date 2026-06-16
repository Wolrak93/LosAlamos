# Lessons Learned — Cycle 6

## What went well

- The detailed manual E2E test checklist uncovered several real bugs and UI issues that automated tests did not catch. Creating a structured checklist at the end of the cycle is worth the time investment.
- UI elements that were designed using the Superpowers brainstorming plugin were noticeably more stable and required fewer corrections. This confirms the value of structured upfront design for UI work.
- The branch sequence and dependency management worked cleanly — no Alembic migration conflicts.

## What could be improved

### Azure User Sync not planned upfront
The need for Azure AD user synchronization only became clear mid-cycle, requiring a new Cycle 7.

**Rule going forward:** In any project using Azure AD / Microsoft SSO, plan the user sync mechanism (Graph API integration) as part of the initial cycle, not as an afterthought.

### Live migration not planned upfront
Moving the app to production was not considered during project planning. Server setup, networking, and deployment were left until the end.

**Rule going forward:** Plan the production deployment path (server, networking, Docker Compose on a real host) as an explicit item in the first or second cycle. Don't treat it as a post-feature concern.

### Short names feature arrived late
The `name_de_short` / `name_en_short` feature was introduced mid-cycle without having been part of the original design. This predictably caused some rework as it touched multiple layers (DB model, AI prompt, schema, frontend).

**Rule going forward:** If a feature is identified mid-cycle, add it to the TODO.md design section and fully spec it before any implementation begins — even if it feels small.

## Architectural decisions

- **DMZ reverse proxy for non-VPN access:** The decision to place a reverse proxy in the DMZ so the app is reachable without VPN is a good pattern. Apply this in future projects whenever an internal app needs to be accessible to users outside the corporate network.

## Deferred question (for Cycle 7 / end of project)

The question "What would we change about the workflow for future projects?" is intentionally deferred to the Cycle 7 lessons learned session, as it is the final cycle of this project.
