# Quick start TL;DR

1. Clone and install both Node workspaces.
```bash
git clone <your-repo-url>
cd <repo-folder>
npm ci
npm --prefix frontend-react ci
```

2. Create env files from templates and fill required secrets.
```bash
cp .env.example .env
cp frontend-react/.env.example frontend-react/.env
```

3. Build frontend assets used by the Node server.
```bash
npm --prefix frontend-react run build
```

4. Start production server locally to validate.
```bash
npm run start
```

5. Deploy Node app (`server.js`) to a single web service (recommended: Render), set env vars, then verify:
```bash
curl https://<your-domain>/models/tiny_face_detector_model-weights_manifest.json
```

## SECTION 1 — Pre-deployment checklist

### Runtime versions (detected from project)

- Node.js: `>=20.0.0` (detected via `engines.node` constraints in `package-lock.json` transitive packages such as `@firebase/component`)
- npm: lockfile v3 detected in both lockfiles (`package-lock.json`, `frontend-react/package-lock.json`), so npm 7+ required (npm 10 recommended)
- Python: `>=3.10` recommended (project uses Flask 3 and modern deps)
- Python packages from `requirements.txt`:
  - Flask `>=3.0.0`
  - matplotlib `>=3.8.0`
- Optional ML sandbox Python packages from `Face_Emotion_Recognition/requirements.txt`:
  - tensorflow, keras, pandas, numpy, jupyter, notebook, tqdm, opencv-contrib-python, scikit-learn

### Required global tools / CLIs

- `git`
- `node` + `npm`
- `python` + `pip` (only needed if running `app.py` or ML sandbox)
- Optional:
  - `ngrok` (remote device testing)
  - `firebase-tools` (deploy/update Firestore rules)
  - `curl`/`Invoke-WebRequest` (health and endpoint checks)

### Required accounts / access

- Firebase project with:
  - Authentication enabled
  - Cloud Firestore enabled
  - (Recommended) Cloud Storage enabled
- Groq API key (for chatbot and assignment generation path using `LLAMA_API_KEY`)
- SMTP provider credentials (Gmail app password or SMTP provider account)
- Deployment platform account (recommended: Render; alternatives listed in Section 4)

### Environment variables (full audit + reconciliation)

The table below reconciles `.env.example`, `frontend-react/.env.example`, and actual source usage.

| Variable | Controls | Required? | Example / Default | Source status |
|---|---|---|---|---|
| `APP_BASE_URL` | Absolute base URL used in booking/report/reminder links from backend emails | Required in production | `http://localhost:3000` | Used in `server.js` |
| `LLAMA_API_KEY` | Groq chat completion authentication | Required for chatbot/assignment endpoints | `your_llama_api_key_here` | Used in `server.js` |
| `LLAMA_MODEL` | Groq model ID (normalized internally) | Optional | `llama-3.1-8b-instant` | Used in `server.js` |
| `GEMINI_API_KEY` | Backend Gemini key (currently imported but not used in active chat path) | Optional currently | `your_gemini_api_key_here` | Declared in `server.js`, effectively unused |
| `FIREBASE_PROJECT_ID` | Firebase Admin initialization and storage fallback IDs | Required (unless local service-account file exists) | `your_firebase_project_id` | Used in `server.js` |
| `FIREBASE_CLIENT_EMAIL` | Firebase Admin service account principal | Required (unless local service-account file exists) | `your_firebase_client_email` | Used in `server.js` |
| `FIREBASE_PRIVATE_KEY` | Firebase Admin private key (`\n` escaped) | Required (unless local service-account file exists) | `-----BEGIN PRIVATE KEY-----\n...` | Used in `server.js` |
| `FIREBASE_STORAGE_BUCKET` | Cloud Storage bucket name for uploads | Optional but recommended | `your_project.appspot.com` | Used in `server.js` |
| `USE_LOCAL_JOURNAL_UPLOADS` | Forces local filesystem uploads fallback (`journal-uploads/`) | Optional | defaults to `true` if unset | Used in `server.js` |
| `EMAIL_USER` | SMTP username (primary path) | Required for emails (or use `SMTP_USER`) | `your_email@example.com` | Used in `server.js` |
| `EMAIL_PASS` | SMTP password/app-password (primary path) | Required for emails (or use `SMTP_PASS`) | `your_app_password_or_smtp_password` | Used in `server.js` |
| `SMTP_USER` | SMTP username fallback | Optional | none | Used in `server.js` |
| `SMTP_PASS` | SMTP password fallback | Optional | none | Used in `server.js` |
| `SMTP_HOST` | SMTP host | Optional | `smtp.gmail.com` | Used in `server.js` |
| `SMTP_PORT` | SMTP port | Optional | `587` | Used in `server.js` |
| `SMTP_SECURE` | Use SMTPS TLS mode | Optional | `false` (or `true` for 465) | Used in `server.js` |
| `FROM_EMAIL` | Email sender identity | Optional (falls back to `EMAIL_USER`) | `Serien <your_email@example.com>` | Used in `server.js` |
| `VITE_GEMINI_API_KEY` | Frontend direct Gemini REST key (`lib/geminiApi.js`) | Optional unless using frontend Gemini helper | template currently contains a real-looking key; replace with placeholder | Used in frontend source |
| `VITE_FIREBASE_STORAGE_BUCKET` | Frontend Firebase storage bucket override | Optional (hardcoded fallback exists) | `your-project.appspot.com` | Used in `frontend-react/src/lib/firebase.js` |
| `VITE_TURN_URL` | TURN server URL for WebRTC NAT traversal | Optional but recommended in production | none | Used in `Patient.jsx`, `Therapist.jsx` |
| `VITE_TURN_USERNAME` | TURN credential username | Optional with TURN | none | Used in `Patient.jsx`, `Therapist.jsx` |
| `VITE_TURN_CREDENTIAL` | TURN credential password/token | Optional with TURN | none | Used in `Patient.jsx`, `Therapist.jsx` |
| `VITE_FIREBASE_API_KEY` | Frontend Firebase API key | Currently unused in code (hardcoded config present) | `your_api_key_here` | In `frontend-react/.env.example` only |
| `VITE_FIREBASE_AUTH_DOMAIN` | Frontend Firebase auth domain | Currently unused in code | `your-project.firebaseapp.com` | In template only |
| `VITE_FIREBASE_PROJECT_ID` | Frontend Firebase project ID | Currently unused in code | `your-project-id` | In template only |
| `VITE_FIREBASE_MESSAGING_SENDER_ID` | Frontend messaging sender ID | Currently unused in code | `your_sender_id_here` | In template only |
| `VITE_FIREBASE_APP_ID` | Frontend app ID | Currently unused in code | `your_app_id_here` | In template only |

Reconciliation note:
- `frontend-react/.env.example` lists many `VITE_FIREBASE_*` vars, but `frontend-react/src/lib/firebase.js` currently hardcodes all Firebase config except storage bucket. Either refactor to full env-based config or remove unused vars from template to avoid confusion.

---

## SECTION 2 — Git setup: what to push and what to exclude

### 2.1 Recommended `.gitignore` (tailored)

Use this repository-specific `.gitignore` baseline:

```gitignore
# Dependencies
node_modules/
frontend-react/node_modules/

# Build outputs
frontend-react/dist/
dist/
build/
out/
coverage/
*.tsbuildinfo

# Runtime/generated local data
journal-uploads/
frontend-react/build-output.log
firebase-debug.log

# Environment and secrets
.env
.env.*
!.env.example
!frontend-react/.env.example
firebase-adminsdk*.json
*.pem
*.key
*.p12

# Python caches and virtualenvs
__pycache__/
*.py[cod]
.pytest_cache/
.mypy_cache/
.ruff_cache/
.ipynb_checkpoints/
.venv/
venv/
env/
ENV/

# Logs/temp
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
*.tmp
*.temp

# OS/editor
.DS_Store
Thumbs.db
Desktop.ini
.idea/
*.swp
*.swo

# Optional: keep .vscode/settings.json only if team-agreed
.vscode/*
!.vscode/settings.json

# Local audit scratch files (generated)
audit_*.txt
frontend_orphans.txt
```

Critical note for this repo:
- Do **not** ignore runtime model assets required by web app loading (`models/` and `frontend-react/public/models/`).
- Do **not** blanket-ignore `face-api.js/` unless you replace server static serving strategy.

### 2.2 Push vs Do NOT push

| Push to Git | Do NOT push |
|---|---|
| `server.js` — production entrypoint and API/signaling logic | `.env` — secrets and credentials |
| `app.py` — optional Flask graph microservice | `node_modules/` — reproducible from lockfiles |
| `package.json`, `package-lock.json` — exact backend dependencies/scripts | `frontend-react/node_modules/` — reproducible |
| `frontend-react/package.json`, `frontend-react/package-lock.json` — exact frontend dependencies/scripts | `frontend-react/dist/` — generated build artifact |
| `frontend-react/src/` — application source | `journal-uploads/` — runtime-generated user media |
| `frontend-react/public/` and `frontend-react/public/models/` — static assets + model files | `firebase-adminsdk*.json` — service account secret |
| `models/` — server-served model assets needed by `/models` route | `*.pem`, `*.key`, `*.p12` — private keys |
| `face-api.js/` (or submodule pointer) — served by `/face-api.js` runtime route | `firebase-debug.log`, build logs — local diagnostics |
| `requirements.txt`, `Face_Emotion_Recognition/requirements.txt` — Python dependency definitions | `.venv/`, `venv/`, `__pycache__/` — local runtime artifacts |
| `firebase.json`, `firestore.rules`, `cors.json`, `storage.cors.json` — platform config and security rules | Temporary audit files (`audit_*.txt`, `frontend_orphans.txt`) |
| `README.md`, `DEPLOYMENT.md`, architecture docs — project ops knowledge | OS/editor noise (`.DS_Store`, `.idea/`, unmanaged `.vscode/`) |
| `.env.example`, `frontend-react/.env.example` — safe templates | Real API keys/tokens in any plaintext file |

### 2.3 Branching strategy and protection

Recommended for this project: **main + develop + feature branches**

- `main`: production-ready only
- `develop`: integration branch for next release
- `feature/<name>`: short-lived task branches
- `hotfix/<name>`: urgent production fixes from `main`

Recommended branch protection for `main`:
- Require pull request (no direct pushes)
- Require at least 1 approving review
- Require status checks to pass (build + smoke)
- Require branch up-to-date before merge
- Block force-push and branch deletion
- Restrict who can push to `main`
- Require signed commits (optional but recommended)

---

## SECTION 3 — Local development setup

### 1) Clone repo

```bash
git clone <your-repo-url>
cd <repo-folder>
```

### 2) Install dependencies

Backend/root:
```bash
npm ci
```

Frontend:
```bash
npm --prefix frontend-react ci
```

Optional Python Flask service:
```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Optional ML sandbox:
```bash
pip install -r Face_Emotion_Recognition/requirements.txt
```

### 3) Set up environment variables

Backend:
```bash
cp .env.example .env
```
Fill required values in `.env`.

Frontend:
```bash
cp frontend-react/.env.example frontend-react/.env
```
Fill `VITE_GEMINI_API_KEY` and optional TURN settings.

### 4) Database/service setup

- Firebase:
  - Enable Authentication and Firestore in your Firebase project
  - Ensure collection security aligns with `firestore.rules`
- Optional rules deployment:
```bash
firebase login
firebase use <project-id>
firebase deploy --only firestore:rules
```

No SQL migrations/seeds are required (Firestore is schema-less).

### 5) Start development servers

Single command (backend + frontend + ngrok):
```bash
npm run dev
```

Or split terminals:
```bash
npm run server
```
```bash
npm run react
```

Optional Flask service (separate terminal):
```bash
python app.py
```

### 6) Verify local run

- Frontend dev UI: `http://localhost:5173`
- Backend server: `http://localhost:3000`
- Flask health (if running): `http://localhost:5000/health`
- Model manifest check:
```bash
curl http://localhost:3000/models/tiny_face_detector_model-weights_manifest.json
```
Expected: HTTP 200 + JSON manifest content.

### 7) Common local setup errors and fixes

- Error: `Firebase Admin credentials are not configured`
  - Cause: missing backend Firebase env vars
  - Fix: set `FIREBASE_PROJECT_ID`, `FIREBASE_CLIENT_EMAIL`, `FIREBASE_PRIVATE_KEY` in `.env`

- Error: `/models/...` returns 404
  - Cause: backend not running, wrong ngrok target, or missing model files
  - Fix: run `npm run server`; verify model files exist in `models/` and `frontend-react/public/models/`

- Error: Chat endpoint returns 500
  - Cause: missing `LLAMA_API_KEY`
  - Fix: set `LLAMA_API_KEY` and optional `LLAMA_MODEL`

- Error: emails fail to send
  - Cause: missing SMTP credentials or provider policy
  - Fix: set `EMAIL_USER`/`EMAIL_PASS` or `SMTP_USER`/`SMTP_PASS`; verify SMTP host/port/security

- WebRTC call connects locally but fails on internet/mobile
  - Cause: no TURN server configured
  - Fix: set `VITE_TURN_URL`, `VITE_TURN_USERNAME`, `VITE_TURN_CREDENTIAL`

---

## SECTION 4 — Production deployment steps

Detected deployment reality:
- No `Dockerfile`, `docker-compose`, `vercel.json`, `netlify.toml`, `render.yaml`, `railway.json`, or CI deploy config found.
- Runtime model is a Node web service serving API + static frontend build + socket signaling.

### Recommended first-time target (simplest)

**Render Web Service** is the simplest first deployment because this repo is already a single Node process (`server.js`) serving both API and static frontend assets, so no multi-service architecture is required to go live.

### Option A — Render (recommended)

#### 1) One-time setup

1. Push repo to GitHub.
2. Create a new Render Web Service from repo.
3. Configure Build Command and Start Command (below).
4. Add environment variables from Section 1.

#### 2) Build command

```bash
npm ci && npm --prefix frontend-react ci && npm --prefix frontend-react run build
```

#### 3) Artifact/folder to deploy

- Deploy full repository as service source.
- Runtime serves `frontend-react/dist/` via `server.js`.

#### 4) Environment variables on platform

Set all required backend vars:
- `APP_BASE_URL` = your Render URL/custom domain
- `LLAMA_API_KEY`
- `LLAMA_MODEL` (optional)
- Firebase Admin vars
- SMTP vars
- Optional `USE_LOCAL_JOURNAL_UPLOADS=false` (recommended in production with cloud storage)

#### 5) Deploy updates

- Merge changes to `main`.
- Render auto-deploys on each push (if enabled).

#### 6) Rollback

- Use Render dashboard -> Deploys -> select last known good deploy -> Redeploy.

#### 7) Post-deployment verification

```bash
curl https://<render-domain>/models/tiny_face_detector_model-weights_manifest.json
curl https://<render-domain>/models/face_expression_model-weights_manifest.json
```

Expected: HTTP 200 for both.

Also verify:
- Open app URL and complete login flow
- Start therapist/patient call route
- Test `/chat` and email-triggering actions

### Option B — Railway

#### 1) One-time setup

1. Create Railway project from repo.
2. Configure service with same build/start commands as Render.
3. Add env vars.

#### 2) Build command

```bash
npm ci && npm --prefix frontend-react ci && npm --prefix frontend-react run build
```

#### 3) Artifact/folder

- Full repository source; app runs `server.js` serving `frontend-react/dist`.

#### 4) Environment variables

- Same set as Render option.

#### 5) Deploy updates

- Push to connected branch or deploy from Railway dashboard.

#### 6) Rollback

- Use Railway deployment history and redeploy prior build.

#### 7) Post-deployment verification

Same endpoint checks as Option A.

### Option C — VPS (Ubuntu) with PM2 + Nginx

#### 1) One-time setup

```bash
sudo apt update
sudo apt install -y nginx git
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm i -g pm2
```

Clone + install + build:
```bash
git clone <your-repo-url>
cd <repo-folder>
npm ci
npm --prefix frontend-react ci
npm --prefix frontend-react run build
```

Create `.env`, then start app:
```bash
pm2 start server.js --name serien
pm2 save
pm2 startup
```

#### 2) Build command

```bash
npm --prefix frontend-react run build
```

#### 3) Artifact/folder

- Full repository on server; runtime uses `server.js` + `frontend-react/dist`.

#### 4) Environment variable configuration

- Set via `.env` file (permissions `600`) or PM2 ecosystem env.

#### 5) Deploy updates

```bash
git pull
npm ci
npm --prefix frontend-react ci
npm --prefix frontend-react run build
pm2 restart serien
```

#### 6) Rollback

```bash
git checkout <last-known-good-tag-or-commit>
npm ci
npm --prefix frontend-react ci
npm --prefix frontend-react run build
pm2 restart serien
```

#### 7) Post-deployment verification

```bash
curl http://127.0.0.1:3000/models/tiny_face_detector_model-weights_manifest.json
curl https://<your-domain>/models/tiny_face_detector_model-weights_manifest.json
```

---

## SECTION 5 — CI/CD pipeline (if applicable)

### Existing pipeline status

- No CI/CD configuration found (`.github/workflows/*`, `Jenkinsfile`, platform YAMLs absent).

### Recommended pipeline stages

1. Install
2. Build frontend
3. Smoke check critical runtime files
4. Deploy

Note: repository has no lint/test scripts configured beyond placeholder `npm test` in root. Add real lint/test tasks later.

### Starter GitHub Actions (Render deploy via deploy hook)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install root dependencies
        run: npm ci

      - name: Install frontend dependencies
        run: npm --prefix frontend-react ci

      - name: Build frontend
        run: npm --prefix frontend-react run build

      - name: Verify required model files exist
        run: |
          test -f models/tiny_face_detector_model-weights_manifest.json
          test -f models/face_expression_model-weights_manifest.json

      - name: Trigger Render deploy
        if: ${{ success() }}
        run: curl -X POST "$RENDER_DEPLOY_HOOK_URL"
        env:
          RENDER_DEPLOY_HOOK_URL: ${{ secrets.RENDER_DEPLOY_HOOK_URL }}
```

### Secrets required in CI platform

- `RENDER_DEPLOY_HOOK_URL` (if using Render deploy hook)

If you instead deploy directly from CI via provider CLI/API, also add provider auth token secrets.

---

## SECTION 6 — Production maintenance

### Logs in production

- Render/Railway:
  - Use platform log viewer for live and historical logs.
- VPS + PM2:
```bash
pm2 logs serien
pm2 monit
```

### Database migrations in production

- No SQL migrations in this codebase.
- Firestore changes are schema-by-convention.
- Security rules updates should be versioned and deployed explicitly:
```bash
firebase deploy --only firestore:rules
```

### Update environment variables without full redeploy

- Render/Railway: update env vars in dashboard; service restart typically required.
- PM2/VPS:
  - update `.env`
  - restart app:
```bash
pm2 restart serien
```

### Monitoring and alerting recommendations

Minimum:
- Uptime checks for `/` and model manifests (`/models/*.json`)
- Error-rate alerts from application logs (`Chat API error`, `Firebase Admin not initialized`, email send failures)
- Latency and memory monitoring for Node service

Recommended stack by platform:
- Platform native metrics/alerts + external uptime monitor (UptimeRobot/Pingdom)
- Structured logging sink (Datadog/Logtail/Sentry)
- WebRTC quality telemetry (optional future enhancement)

### Backup strategy

- Firestore:
  - Schedule daily exports to Cloud Storage (GCP managed export)
- Storage/journal media:
  - If using Firebase Storage, use bucket lifecycle + backup policy
  - If using local uploads (`journal-uploads/`), schedule filesystem backups (snapshot + offsite)
- Config backups:
  - Version-control all non-secret config (`firebase.json`, `firestore.rules`, `cors.json`, `storage.cors.json`)
  - Keep secrets in platform secret manager, not in git

---

### Final reconciliation summary (post-review)

1. Environment variable mismatches corrected in this document:
- Added source-used but template-missing vars: `USE_LOCAL_JOURNAL_UPLOADS`, `SMTP_USER`, `SMTP_PASS`, TURN vars.
- Marked template-only currently unused vars (`VITE_FIREBASE_API_KEY`, `VITE_FIREBASE_AUTH_DOMAIN`, `VITE_FIREBASE_PROJECT_ID`, `VITE_FIREBASE_MESSAGING_SENDER_ID`, `VITE_FIREBASE_APP_ID`).

2. Commands validated against actual scripts:
- Root scripts confirmed: `npm run server`, `npm run react`, `npm run ngrok`, `npm run dev`, `npm run start`.
- Frontend scripts confirmed: `npm --prefix frontend-react run dev|build|preview`.

3. Simplest deployment recommendation for first-time deploy:
- **Render Web Service** (single service, no Docker required, supports env vars + auto-deploy + rollback UI).
