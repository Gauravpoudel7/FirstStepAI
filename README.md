# FirstStep AI

> Enterprise AI assistant — onboarding, HR policies, security, projects, and personalized answers for your team, gated by role and permissions.

FirstStep AI is a full-stack web application that gives every employee a smart AI helper trained on company documents. Managers, HR, and admins get extra tools and dashboards. Employees get answers grounded in the company's own policy PDFs.

---

## ✨ Features

- 🤖 **AI Chat** — ask anything about HR policies, projects, or your profile; answers stream in real time and cite the source documents.
- 📊 **Dashboard** — role-aware summary of your activity, leave, projects, and recent chat.
- 👤 **Profile** — view and edit your personal info, job details, and skills.
- 🗂️ **Projects** — managers and admins can create, update, and assign projects; everyone sees only the ones they belong to.
- 📄 **Documents** — browse and search the company knowledge base.
- 📈 **Analytics** — usage stats and chat insights.
- 🕘 **Chat History** — every conversation is saved; come back to it any time.
- ⚙️ **Settings** — toggle theme (dark/light), change language, manage your account.
- 🛡️ **Admin tools** — user management, role assignment, and an activity log (admins only).
- 🔐 **Role-based access** — Employees, Managers, HR, and Admins each see only what they should.

---

## 🧰 Tech Stack

**Frontend** (`web/`)
- React 19 + TypeScript
- Vite (dev server & build)
- React Router (navigation)
- TanStack Query (data fetching & caching)
- Zustand (client state, with localStorage persistence)
- Axios (HTTP client) + SSE (real-time streaming)
- Tailwind CSS + shadcn/ui + Framer Motion (styling & animation)

**Backend** (`api/`)
- FastAPI (Python 3.11)
- SQLAlchemy ORM (Postgres in production, SQLite for local dev)
- JWT auth with HttpOnly cookies + refresh tokens
- Pydantic (request/response validation)
- ChromaDB + LangChain (RAG — Retrieval Augmented Generation)
- LangChain-Groq (LLM provider; falls back to a local mock if no API key)

**Tests**
- Playwright (end-to-end browser tests)
- Python smoke scripts (`scripts/smoke_phase*.py`) covering API phases 1 → 7

---

## 📦 Requirements

- **Python** 3.11 or newer
- **Node.js** 18 or newer
- A modern browser
- *(Optional)* A free **Groq API key** to enable real LLM responses — without it, the chat shows a friendly `[no-key]` mock so the app stays usable offline.

---

## 🚀 Installation

### 1. Clone the repo
```bash
git clone https://github.com/Gauravpoudel7/FirstStepAI.git
cd FirstStepAI
```

### 2. Set up the backend
```bash
cd api
python -m venv .venv
# activate the venv
# Windows (Git Bash):  source ../.venv/Scripts/activate
# macOS / Linux:        source .venv/bin/activate

pip install -e .
```

### 3. Set up the frontend
```bash
cd ../web
npm install
```

### 4. Create the `.env` files

Create `api/.env`:
```env
GROQ_API_KEY=your_groq_api_key_here      # leave empty for offline mock
GROQ_MODEL=llama-3.1-8b-instant
AUTH_SECRET=change-me-to-a-long-random-string
DATABASE_URL=sqlite:///./dev_http.db      # use postgresql://... in prod
COMPANY_NAME=Umbrella Corporation
```
Create `web/.env` (only if your API isn't on the default origin):
```env
VITE_API_BASE_URL=/api/v1
```

### 5. Seed the demo data
```bash
cd ../api
python scripts/smoke_phase1.py            # creates tables + seeds admin & demo users
python scripts/seed_from_json.py --source ../data/users.json   # adds hr/manager/employee
```

That's it — the database is ready and 5 demo users are loaded.

---

## ▶️ Running the Project

You need **two terminals** — one for the API, one for the frontend.

### Terminal 1 — Backend (FastAPI)
```bash
cd api
# activate your venv first
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
The API is now at `http://localhost:8000`. Health check: `http://localhost:8000/healthz`.

### Terminal 2 — Frontend (Vite)
```bash
cd web
npm run dev
```
The app is now at `http://localhost:5173`. Open that in your browser.

### Sign in with a demo account

| Role     | Email                       | Password   |
|----------|-----------------------------|------------|
| Admin    | `admin@umbrella.corp`       | `demo123`  |
| HR       | `hr@umbrella.corp`          | `demo123`  |
| Manager  | `manager@umbrella.corp`     | `demo123`  |
| Employee | `employee@umbrella.corp`    | `demo123`  |
| Demo     | `demo@umbrella.corp`        | `demo123`  |

> The login page also lets you click any of these accounts to auto-fill the form.

---

## 🧪 Running Tests

**End-to-end (Playwright):**
```bash
cd web
npm run test:e2e:install   # one-time, installs Chromium
npm run test:e2e
```

**Backend smoke tests:**
```bash
cd api
python scripts/smoke_phase1.py   # auth + RBAC
python scripts/smoke_phase4.py   # chat + RAG
python scripts/smoke_phase5.py   # documents
python scripts/smoke_phase6.py   # dashboard / profile
```

---

## 📁 Project Structure

```
FirstStepAI/
├── api/                          # FastAPI backend
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── endpoints/        # one file per resource (auth, chat, projects, …)
│   │   │   └── router.py         # aggregates all v1 routes under /api/v1
│   │   ├── core/                 # config, deps, exceptions
│   │   ├── db/                   # SQLAlchemy engine, session, base
│   │   ├── models/               # ORM models (User, Project, Conversation, …)
│   │   ├── schemas/              # Pydantic request/response models
│   │   ├── services/             # business logic
│   │   │   ├── auth_service.py
│   │   │   ├── chat_service.py
│   │   │   ├── llm/              # LLM provider abstraction + Groq + mock
│   │   │   └── rag/              # retrieval-augmented generation
│   │   ├── security/             # JWT, password hashing
│   │   ├── config/               # pydantic-settings, .env loader
│   │   └── main.py               # FastAPI app, lifespan, exception handlers
│   ├── scripts/                  # smoke tests, seeders
│   ├── data/                     # PDFs, vectorstore, sqlite db (dev)
│   ├── pyproject.toml
│   └── .env
│
├── web/                          # React frontend
│   ├── src/
│   │   ├── features/             # one folder per page (auth, chat, dashboard, …)
│   │   ├── components/
│   │   │   ├── ui/               # shadcn/ui primitives (Button, Card, Dialog, …)
│   │   │   └── layout/           # AppShell, Sidebar, TopBar, RoleBadge
│   │   ├── hooks/                # useAuth, useChatStream, useTheme
│   │   ├── lib/                  # api.ts (axios), sse.ts, utils, types
│   │   ├── routes/               # ProtectedRoute
│   │   ├── store/                # zustand stores (auth, chat)
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── tests/                    # Playwright specs
│   ├── package.json
│   └── vite.config.ts
│
├── data/                         # shared seed data (users.json, policies PDF)
└── deploy/                       # docker-compose, nginx, production guides
```

---

## 🖥️ Pages & Features — What Each One Does

The sidebar on the left is your navigation. The exact items shown depend on your role.

### 🔑 Login (`/login`)
The first page you see. Sign in with email + password. There's a list of demo accounts at the bottom — click any one to auto-fill the form and try the app instantly. After signing in, the sidebar (and your permissions) update automatically.

### 🏠 Dashboard (`/`)
The landing page after login. A role-aware summary of what's going on:
- Quick stats cards (leave days, active projects, recent chats)
- A snapshot of your projects and your team's recent activity
- For managers / admins: extra widgets showing team-wide numbers

> Use it as your "home base" — glance at it each morning to see what's new.

### 💬 AI Chat (`/chat`)
The main feature. Type a question and the assistant answers in real time, streaming token-by-token. Every answer cites the source document it pulled from — click the citation chip to see the original text. Suggested prompts at the top of the page adapt to your role (HR gets HR questions, engineers get engineering ones, etc.).

**Tips:**
- The chat remembers your conversation — you can scroll back, ask follow-ups, or start a fresh thread with the **Reset conversation** button in the top bar.
- **Stop** button (left of the send button) cancels a reply mid-stream.

### 📂 Projects (`/projects`)
- **Employees** see only the projects they're a member of.
- **Managers & Admins** can create new projects, edit them, change status, add or remove members, and delete projects.
- Click any project card to see its full description, members, and status.

### 📚 Knowledge Base / Documents (`/knowledge`, `/documents`)
Browse the company documents the AI uses as its source of truth — HR policies, security guides, onboarding checklists. Search by keyword; click a doc to read it. Documents are role-gated: you only see the ones your role is allowed to read.

### 📊 Analytics (`/analytics`)
Charts and numbers showing how the AI is being used — most-asked questions, top documents, usage over time. Useful for managers and admins to spot trends.

### 🕘 Chat History (`/history`)
Every conversation you've had with the AI is saved here. Click any to reopen it. Useful for finding an answer you got last week without re-asking.

### 👤 Profile (`/profile`)
Your personal card. View your role, department, manager, contact info, and skills. Edit your full name, phone, and bio. Some fields (like your email and role) are read-only — only an admin can change those.

### ⚙️ Settings (`/settings`)
Personal preferences:
- **Theme** — dark or light mode
- **Language** — interface language (where translations exist)
- **Account** — change password, request a reset

### 🛡️ Admin (`/admin`) — *admins only*
A hidden-from-others control panel:
- **Users** — see all accounts, change roles, deactivate
- **Activity Log** — every important action across the app, with timestamps and the user who did it

### Top bar (every page)
- **Page title** — shows where you are
- **Theme toggle** — quick switch between dark and light
- **Reset conversation** — clears the current AI chat thread
- **User menu** (top right) — your avatar and name, plus **Logout**

---

## 🔐 Roles & Permissions

| Role     | Chat | Projects (view own) | Projects (manage) | Admin Panel |
|----------|:----:|:-------------------:|:-----------------:|:-----------:|
| Employee | ✅   | ✅                  | ❌                | ❌          |
| Manager  | ✅   | ✅                  | ✅                | ❌          |
| HR       | ✅   | ✅                  | ✅                | ❌          |
| Admin    | ✅   | ✅                  | ✅                | ✅          |

---

## 🐛 Troubleshooting

**Login feels stuck or returns nothing.**
Kill any old uvicorn process (`Ctrl-C`), then start a fresh one. The lifespan startup self-heals an empty SQLite database, but only when the new process actually opens the file — a stale process keeps a handle to the old empty one.

**Chat shows `[no-key]` placeholders.**
You haven't set `GROQ_API_KEY` in `api/.env`. Get a free key at [console.groq.com](https://console.groq.com) and restart the API. The app still works without a key — just with the offline mock.

**`CORS` errors in the browser console.**
Make sure the URL you're hitting matches `CORS_ORIGINS` in `api/.env`. The default `http://localhost:5173` covers Vite dev.

**Tests can't reach the API.**
The Playwright tests assume the API is on `http://localhost:8000` and the frontend on `http://localhost:5173` (or `8080` for the preview build). Start both before running tests.

---

## 📜 License

This project is licensed under the MIT License — see `LICENSE` for details.

---

## 🙏 Credits

Built with ❤️ using FastAPI, React, LangChain, and a great deal of coffee.