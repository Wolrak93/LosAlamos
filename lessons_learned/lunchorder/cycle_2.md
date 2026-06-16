# Lessons Learned — Cycle 2: Authentication & Authorization

## What was built
- Azure AD / MSAL SPA login flow (PKCE popup) with token exchange at a FastAPI backend
- App-level JWT issuance (HS256) and storage in localStorage
- FastAPI RBAC middleware (`get_current_user`, `require_roles`)
- Guest invitation system: email via Microsoft Graph API, token-link re-login (no password)

---

## Process Lessons

### 1. Azure App Registration must be fully configured before implementation starts
**Issue:** The `blank.html` redirect URI needed for the MSAL popup flow was not registered
in Azure Portal until after it was discovered to be necessary mid-implementation.
This caused a test failure and a manual portal detour.
**Fix:** Before writing any MSAL code, produce an explicit "Azure Portal Checklist" as part
of the task description:
- SPA platform added
- All redirect URIs registered (including `http://localhost:5173/blank.html` for popup flow)
- Required API permissions granted (e.g. `openid`, `profile`, `email`)
- (If backend validation) Expose an API scope or confirm ID token use
**Advice:** Treat the Azure App Registration as infrastructure. Set it up completely
before touching code, just like a database migration precedes model code.

---

## Technical Lessons

### 2. MSAL popup flow requires a dedicated blank redirect page
**Issue:** `ProtectedRoute` redirected unauthenticated users to `/login` on every render.
When MSAL opened a popup and tried to close it via the redirect URI, the React app
intercepted the redirect, matched no route, and broke the popup handshake.
**Fix:** Create a `frontend/public/blank.html` (an empty HTML page) and register it as
the popup redirect URI (`redirectUri` in `loginPopupRequest`). The popup loads the blank
page and closes cleanly without triggering React Router.
**Advice:** Any MSAL SPA project using popup flow must include `blank.html` from the start.
Add it to the feature branch task description explicitly.

### 3. MSAL access tokens are not the same as ID tokens — use the right one
**Issue:** `acquireTokenPopup` with scope `User.Read` returns a Microsoft Graph
**access token** (`aud = https://graph.microsoft.com`). The FastAPI backend validated
the token expecting `aud = {AZURE_CLIENT_ID}` and rejected it with 401.
**Fix:** Send `result.idToken` (the OIDC ID token) to the backend instead of
`result.accessToken`. The ID token always has `aud = client_id` and contains the user's
`oid`, `email`, and `name` claims needed for the exchange endpoint.
**Alternative:** If an access token must be used, expose a custom API scope
(`api://{client_id}/access_as_user`) in the App Registration and request that scope.
The resulting access token will then have `aud = client_id`.
**Advice:** In the TODO task description, explicitly state:
> "Send `idToken` to the backend exchange endpoint, not `accessToken`."
This distinction is non-obvious and caused significant debugging time.

### 4. CORS middleware must be part of the backend foundation, not an afterthought
**Issue:** The backend had no CORS headers. The browser blocked every request from
`localhost:5173` to `localhost:8000` with a CORS error — only visible in the browser
console, not in backend logs. This was not discovered until the frontend tried its first
real API call.
**Fix:** Add `CORSMiddleware` to `main.py` as part of the initial backend setup, before
any frontend integration work begins.
**Advice:** Add "configure CORS middleware" as a mandatory step in the backend foundation
task of every new project that has a separate frontend. It should never be left for later.

### 5. Frontend .env file must be created explicitly before first test run
**Issue:** Only `.env.example` was committed. The actual `frontend/.env` file was never
created. As a result, `VITE_AZURE_TENANT_ID` and other variables were `undefined` at
runtime, causing silent failures in the MSAL config.
**Fix:** After committing `.env.example`, immediately create `frontend/.env` with real
values for the local dev environment and verify the app starts without undefined env vars.
**Advice:** Add an explicit step to the task checklist:
> "Create `frontend/.env` from `frontend/.env.example` and fill in real values.
> Verify with `console.log(import.meta.env)` that all required vars are defined."

---

### 6. Prefer Microsoft Graph API over Azure Communication Services for email delivery
**Issue:** Azure Communication Services (ACS) was the initial choice for sending invitation
emails. ACS requires a separate Azure resource, a dedicated connection string credential,
and an additional SDK (`azure-communication-email`). During the cycle it became clear that
the project's Azure App Registration already had access to the Microsoft Graph API and a
shared mailbox was available.
**Fix:** Replaced ACS with a direct Graph API call (`POST /users/{sender}/sendMail`).
The existing `msal`, `httpx`, and Azure AD credentials (`tenant_id`, `client_id`,
`client_secret`) were already present in the project — zero new dependencies or env vars
were needed. The only Azure Portal step required was adding the `Mail.Send` **Application**
permission to the App Registration and granting admin consent.
**Advice:** In any future project that already uses Azure AD / Microsoft 365:
- **Default to Graph API (`Mail.Send`)** for transactional email.
- Only consider ACS if the organisation does not use Microsoft 365 or if advanced
  telephony/SMS features are required.
- **Azure Portal checklist for Graph email:**
  1. Azure Portal → App Registration → API Permissions
  2. Add `Microsoft Graph` → Application permission → `Mail.Send`
  3. Grant admin consent
  4. Use the shared or service mailbox address as the sender (`/users/{email}/sendMail`)
- Shared mailboxes work with Graph API application permissions without any extra
  configuration.

---

## What went well
- The token exchange pattern (Azure token in → app JWT out) was clean and decoupled
  once the correct token type was identified.
- Using the MSAL popup flow (vs. redirect flow) kept the UX simple and avoided full-page
  navigation issues.
- RBAC middleware with `require_roles(*roles)` as a FastAPI dependency proved ergonomic
  and easy to apply to any endpoint.
- Locking design decisions at the top of `TODO.md` (token type, JWT storage, role
  hierarchy) prevented scope creep mid-cycle.
- Switching from password-based guest auth to a token-link (re-login via same link)
  simplified both backend and frontend significantly, with no loss of security for
  the internal-app use case.
