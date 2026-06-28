# Graph Report - FirstStepAI  (2026-06-26)

## Corpus Check
- 185 files · ~70,943 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1075 nodes · 2236 edges · 101 communities (76 shown, 25 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 150 edges (avg confidence: 0.63)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a6896645`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Auth & Security Helpers|Auth & Security Helpers]]
- [[_COMMUNITY_User & AuthService|User & AuthService]]
- [[_COMMUNITY_App Entry & Auth UI|App Entry & Auth UI]]
- [[_COMMUNITY_Chat Page & Prompts|Chat Page & Prompts]]
- [[_COMMUNITY_RBAC & Role-Aware RAG|RBAC & Role-Aware RAG]]
- [[_COMMUNITY_RAG Pipeline & Ingest|RAG Pipeline & Ingest]]
- [[_COMMUNITY_Umbrella Corp Policy Rules|Umbrella Corp Policy Rules]]
- [[_COMMUNITY_Employee Profile|Employee Profile]]
- [[_COMMUNITY_Admin & Profile Pages|Admin & Profile Pages]]
- [[_COMMUNITY_Session Manager|Session Manager]]
- [[_COMMUNITY_Smoke Test|Smoke Test]]
- [[_COMMUNITY_Config Package|Config Package]]
- [[_COMMUNITY_Pydantic Settings|Pydantic Settings]]
- [[_COMMUNITY_Services Package|Services Package]]
- [[_COMMUNITY_RAG Package|RAG Package]]
- [[_COMMUNITY_bcrypt|bcrypt]]
- [[_COMMUNITY_Faker|Faker]]
- [[_COMMUNITY_itsdangerous|itsdangerous]]
- [[_COMMUNITY_python-dotenv|python-dotenv]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 70|Community 70]]
- [[_COMMUNITY_Community 71|Community 71]]
- [[_COMMUNITY_Community 72|Community 72]]
- [[_COMMUNITY_Community 73|Community 73]]
- [[_COMMUNITY_Community 74|Community 74]]
- [[_COMMUNITY_Community 75|Community 75]]
- [[_COMMUNITY_Community 76|Community 76]]
- [[_COMMUNITY_Community 77|Community 77]]
- [[_COMMUNITY_Community 79|Community 79]]
- [[_COMMUNITY_Community 80|Community 80]]
- [[_COMMUNITY_Community 81|Community 81]]
- [[_COMMUNITY_Community 82|Community 82]]
- [[_COMMUNITY_Community 83|Community 83]]
- [[_COMMUNITY_Community 84|Community 84]]
- [[_COMMUNITY_Community 85|Community 85]]
- [[_COMMUNITY_Community 92|Community 92]]

## God Nodes (most connected - your core abstractions)
1. `User` - 55 edges
2. `User` - 29 edges
3. `useAuthStore` - 25 edges
4. `Employee` - 23 edges
5. `cn()` - 23 edges
6. `Role` - 22 edges
7. `Document` - 21 edges
8. `SQLAuthProvider` - 21 edges
9. `LocalAuthProvider` - 21 edges
10. `AuthService` - 19 edges

## Surprising Connections (you probably didn't know these)
- `ChromaDB Vector Store + RAG Pipeline` --references--> `pypdf 5.0.1`  [INFERRED]
  data/umbrella_corp_policies.pdf → requirements.txt
- `Web Search Tools (DuckDuckGo, Arxiv, Wikipedia)` --references--> `langchain-community 0.3.14`  [INFERRED]
  data/umbrella_corp_policies.pdf → requirements.txt
- `SQLAuthProvider` --uses--> `InvalidCredentialsError`  [INFERRED]
  api/app/services/auth_providers/db_provider.py → core/exceptions.py
- `SQLAuthProvider` --uses--> `UserNotFoundError`  [INFERRED]
  api/app/services/auth_providers/db_provider.py → core/exceptions.py
- `AuthService` --uses--> `InvalidCredentialsError`  [INFERRED]
  api/app/services/auth_service.py → core/exceptions.py

## Import Cycles
- 1-file cycle: `ui/__init__.py -> ui/__init__.py`

## Hyperedges (group relationships)
- **LangChain Ecosystem Dependencies** — requirements_langchain, requirements_langchain_community, requirements_langchain_huggingface, requirements_langchain_chroma, requirements_langchain_groq, requirements_chromadb [INFERRED 0.95]
- **Streamlit Application Runtime Dependencies** — requirements_streamlit, requirements_pydantic, requirements_pydantic_settings, requirements_bcrypt, requirements_itsdangerous, requirements_python_dotenv [INFERRED 0.85]
- **Document Processing and Test Data Generation** — requirements_pypdf, requirements_faker [INFERRED 0.75]

## Communities (101 total, 25 thin omitted)

### Community 0 - "Auth & Security Helpers"
Cohesion: 0.10
Nodes (14): _get_serializer(), Password hashing and signed token helpers., Return a signed, max-age-limited token. `max_age` is in seconds., Verify a token. Returns the payload dict or None if invalid/expired., Like verify_token but swallows expired/invalid errors and returns None., safe_verify_token(), sign_token(), verify_token() (+6 more)

### Community 1 - "User & AuthService"
Cohesion: 0.11
Nodes (9): An authenticated user account. Persisted to data/users.json., User, AuthService, Generate a reset token for the given email.          Demo-only behaviour: the to, AuthProvider, AuthProvider, Abstract base class for authentication providers.  Future SSO / LDAP providers (, Pluggable auth backend. (+1 more)

### Community 2 - "App Entry & Auth UI"
Cohesion: 0.09
Nodes (26): Alembic environment configuration.  Reads DATABASE_URL from the application sett, FirstStepAI — Enterprise AI Assistant entrypoint.  Orchestrates the boot sequenc, get_session(), _next_holiday(), Dashboard page — Active Projects, Leave Balance, Upcoming Holidays, AI Usage., render_dashboard(), _badge(), Knowledge Base page — browse role-filtered documents. (+18 more)

### Community 3 - "Chat Page & Prompts"
Cohesion: 0.11
Nodes (17): _build_chat_service(), Chat page — streaming chat with employee context and role-aware RAG., Lazy-construct (or re-bind) the ChatService for the current user., render_chat(), Prompts package — system prompt, welcome message, per-role suggestions., Per-role suggested prompts shown above the chat input., First-turn welcome message., build_llm() (+9 more)

### Community 4 - "RBAC & Role-Aware RAG"
Cohesion: 0.21
Nodes (13): Role, allowed_doc_roles(), can_access(), permissions_for_role(), Role-based access control.  The role -> permission matrix is the single source o, role_badge_color(), True if the given role has the permission. Role may be a string or enum., Roles a doc may be tagged with for this user to retrieve it.      Every role can (+5 more)

### Community 5 - "RAG Pipeline & Ingest"
Cohesion: 0.31
Nodes (8): add_document_text(), ensure_indexed(), Document ingestion with role-based metadata tagging., reindex_pdf(), _tag_metadata(), Load, split, tag, and add the PDF to the vector store. Returns chunk count., Add a single text document to the existing vector store with metadata., Build the vector store from the bundled PDF if it doesn't already exist.      Re

### Community 6 - "Umbrella Corp Policy Rules"
Cohesion: 0.12
Nodes (24): AI-Generated Assignment Rules (Annex K), 80% Quiz Pass Threshold, FirstStepAI Onboarding System, Hallucination Control via System-Prompt Guardrails, LangChain Agent Orchestration, LLM-Driven Quiz Generation, Manager Approval Escalation, Mixed Multiple-Choice and Numerical Quiz (+16 more)

### Community 7 - "Employee Profile"
Cohesion: 0.24
Nodes (11): _default_permissions_for(), generate_employee_data(), load_employee_profile_for_email(), _make_employee_id(), _make_profile(), Employee data + user-database seeding.  The original module generated a single f, Map role to a permission list (matches core.rbac but kept local to avoid     a c, Generate `num_employees` random employee dicts (legacy entrypoint). (+3 more)

### Community 8 - "Admin & Profile Pages"
Cohesion: 0.12
Nodes (22): EmployeeProfile, Permission, Auth models — User, Role, Permission., Extended employee fields the chatbot can talk about., Format the profile for system-prompt injection., get_auth_service(), Auth facade — login / logout / forgot-password / reset / remember-me.  Provider-, Auth UI helpers — login form, forgot-password modal.  The actual login *page chr (+14 more)

### Community 9 - "Session Manager"
Cohesion: 0.05
Nodes (86): AdminPage(), ACTION_COLORS, AnalyticsPage(), LoginPage(), ChatPage(), SUGGESTIONS, DashboardPage(), DocumentsPage() (+78 more)

### Community 11 - "Config Package"
Cohesion: 0.05
Nodes (19): ABC, AuthProvider, AuthProvider ABC — pluggable auth backends (local DB, AzureAD, Google, LDAP)., Abstract base for auth backends. Mirrors the existing AuthProvider ABC., Return the User on success; raise InvalidCredentialsError on failure., LLMService, LLM service abstraction — wraps any provider behind a uniform async iterator., Common interface for chat completions with streaming. (+11 more)

### Community 15 - "RAG Package"
Cohesion: 0.05
Nodes (39): dependencies, axios, class-variance-authority, clsx, framer-motion, lucide-react, react, react-dom (+31 more)

### Community 20 - "Community 20"
Cohesion: 0.07
Nodes (22): create_access_token(), create_refresh_token(), decode_access_token(), hash_refresh_token(), _hash_token(), _now(), JWT access + refresh token encode/decode.  Access tokens are short-lived (15 min, Mint an HS256 JWT. Returns (token, ttl_seconds). (+14 more)

### Community 21 - "Community 21"
Cohesion: 0.09
Nodes (31): _auth_error(), healthz(), _invalid_credentials(), lifespan(), FastAPI application entrypoint.  Wires:   - CORS (per CORS_ORIGINS env var)   -, Lightweight health probe — used by docker-compose and load balancers., _token_expired(), _token_invalid() (+23 more)

### Community 22 - "Community 22"
Cohesion: 0.09
Nodes (27): AuthError, InvalidCredentialsError, Domain exceptions.  Ported verbatim from core/exceptions.py. FastAPI exception h, Raised when email or password is wrong., Raised when an operation references an unknown user., Raised when a signed token (remember-me, password-reset) is past its max age., Raised when a signed token is malformed or tampered with., Base class for authentication / authorization errors. (+19 more)

### Community 23 - "Community 23"
Cohesion: 0.18
Nodes (22): Base, SQLAlchemy declarative Base used by all models and Alembic., Common declarative base. All ORM models inherit from this., DeclarativeBase, _conv_out(), ConversationCreate, ConversationOut, ConversationPatch (+14 more)

### Community 24 - "Community 24"
Cohesion: 0.16
Nodes (21): Document service — list, fetch, upload, delete, reindex.  Role filter is enforce, get_employee_profile(), get_my_profile(), list_profiles(), ProfileOut, ProfileUpdate, Profile endpoints — read/update current user's employee profile., Fetch a single employee profile by employee_id (HR/ADMIN only). (+13 more)

### Community 25 - "Community 25"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, baseUrl, isolatedModules, jsx, lib, module, moduleResolution (+12 more)

### Community 26 - "Community 26"
Cohesion: 0.19
Nodes (15): Employee, Employee ORM model — extended fields used by the LLM system prompt., Format the profile for system-prompt injection (parity with auth/models.py)., Project, ProjectMember, Project + ProjectMember ORM models., create_project(), delete_project() (+7 more)

### Community 27 - "Community 27"
Cohesion: 0.18
Nodes (6): PostgreSQL-backed auth provider. Preserves the existing AuthProvider surface., SQLAuthProvider, hash_password(), Hash a password with bcrypt., Constant-time bcrypt comparison., verify_password()

### Community 28 - "Community 28"
Cohesion: 0.26
Nodes (16): get_auth_service_dep(), Depends, change_password(), reset_password(), create_project(), delete_project(), get_project(), list_employee_options() (+8 more)

### Community 29 - "Community 29"
Cohesion: 0.21
Nodes (16): DemoAccountRow, _clear_cookies(), _employee_dict(), get_demo_accounts(), login(), logout(), me(), Auth endpoints — login, logout, refresh, password management, demo accounts. (+8 more)

### Community 30 - "Community 30"
Cohesion: 0.17
Nodes (11): load_pdf(), load_text(), chunk_documents(), Document, Document ORM model — metadata for indexed knowledge-base docs., Path, load_pdf(), load_text() (+3 more)

### Community 31 - "Community 31"
Cohesion: 0.21
Nodes (15): BaseModel, forgot_password(), Issue a reset token. Always returns ok:true to avoid email enumeration.      The, ChangePasswordRequest, DemoAccountRow, ForgotPasswordRequest, ForgotPasswordResponse, LoginRequest (+7 more)

### Community 32 - "Community 32"
Cohesion: 0.20
Nodes (13): Chat service — orchestrates retrieval + LLM streaming + persistence., System prompt builders — preserved from prompts/system.py., Conversation, build_system_prompt(), Render the FirstStepAI system prompt with company + employee + RAG context., _employee_block(), get_or_create_conversation(), _history_messages() (+5 more)

### Community 33 - "Community 33"
Cohesion: 0.15
Nodes (7): Role-aware retriever (ported verbatim from rag/retriever.py).  Wraps a Chroma ve, RoleAwareRetriever, BaseRetriever, RoleAwareRetriever, Wrap a base retriever and inject a Chroma `filter` for role metadata.      Falls, Wrap a base retriever and inject a Chroma `filter` for role metadata.      Filte, Set ``search_kwargs['filter']`` on the base retriever, then restore.

### Community 34 - "Community 34"
Cohesion: 0.16
Nodes (11): SQL-backed AuthProvider. Replaces LocalAuthProvider (JSON file)., datetime, ActivityLog, Activity log — append-only audit trail., User ORM model. Preserves existing bcrypt hashes from data/users.json., list_logs(), Activity log service — append-only listing for admin analytics., Insert an activity log row.      When ``commit=False``, the row is added to the (+3 more)

### Community 35 - "Community 35"
Cohesion: 0.26
Nodes (13): allowed_doc_roles(), can_access(), permissions_for_role(), Role-based access control.  The role -> permission matrix is the single source o, role_badge_color(), all_roles(), Permission, True if the given role has the permission. Role may be a string or enum. (+5 more)

### Community 36 - "Community 36"
Cohesion: 0.15
Nodes (12): _build_engine(), get_db(), is_sqlite(), SQLAlchemy engine + session factory.  Pluggable: uses Postgres when DATABASE_URL, FastAPI dependency that yields a session and ensures cleanup.      Rolls back an, True when the configured engine targets SQLite (dev fallback)., ip_column(), json_column() (+4 more)

### Community 37 - "Community 37"
Cohesion: 0.29
Nodes (9): Any, Local JSON-backed auth provider.  Users are persisted in `data/users.json` as a, Feedback service — persist 👍/👎 ratings to data/feedback.json., Append a feedback entry. Idempotent per (message_id, rating)., record_feedback(), ensure_dir(), JSON helpers with atomic writes — never leave a half-written file behind., read_json() (+1 more)

### Community 38 - "Community 38"
Cohesion: 0.20
Nodes (6): Back-compat shim — the `Assistant` class has moved to `services.chat_service.Cha, BaseMessage, ChatService, _history_to_messages(), Chat service — owns the LCEL chain, employee context, and role-aware retriever., Owns the LangChain chain. Per-session instance.

### Community 39 - "Community 39"
Cohesion: 0.22
Nodes (7): get_settings(), Application configuration loaded from environment / .env file.  Ported from the, Settings, BaseSettings, get_settings(), Application configuration loaded from environment / .env file., Settings

### Community 40 - "Community 40"
Cohesion: 0.18
Nodes (9): build_embeddings(), Embedding model factory (ported from rag/embeddings.py)., HuggingFaceEndpointEmbeddings, is_zero_embeddings(), build_embeddings(), Embedding model factory., Return the HF inference-API embeddings used for both ingest and query.      Fall, Return the HF inference-API embeddings used for both ingest and query.      Fall (+1 more)

### Community 41 - "Community 41"
Cohesion: 0.27
Nodes (10): add_document_text(), ensure_indexed(), Document ingestion with role-based metadata tagging (ported from rag/ingest.py)., reindex_pdf(), _tag_metadata(), _guard_real_embeddings(), Refuse to operate if embeddings is the zero-vector stub.      Cosine similarity, Load, split, tag, and add the PDF to the vector store. Returns chunk count. (+2 more)

### Community 42 - "Community 42"
Cohesion: 0.24
Nodes (8): chat_message(), ChatRequest, Chat endpoint — Server-Sent Events streaming., _sse_format(), _stream_frames(), get_dashboard_summary(), FastAPI, StreamingResponse

### Community 43 - "Community 43"
Cohesion: 0.38
Nodes (9): delete_document(), DocumentOut, DocumentUpload, get_document(), list_documents(), Document endpoints — list, fetch, upload, delete, reindex., reindex(), upload_document() (+1 more)

### Community 44 - "Community 44"
Cohesion: 0.27
Nodes (8): Permission, Role-Permission seed tables. Mirrors core/rbac.py::ROLE_PERMISSIONS., RolePermission, _check(), main(), Verify Phase 1 HTTP endpoints via FastAPI TestClient.  Uses an ephemeral SQLite, _reset(), _seed()

### Community 45 - "Community 45"
Cohesion: 0.44
Nodes (8): get_activity_log(), list_users(), Admin endpoints — user list/role change, activity log summary (Phase 7)., RoleUpdate, update_role(), _user_to_out(), UserOut, require_role

### Community 46 - "Community 46"
Cohesion: 0.36
Nodes (7): branding(), get_my_settings(), patch_my_settings(), Settings endpoints — get/patch user-scoped settings; branding is public., Public — used by LoginPage and TopBar before the user is logged in., SettingsOut, SettingsPatch

### Community 47 - "Community 47"
Cohesion: 0.31
Nodes (7): AIUsage, Announcement, DashboardSummary, UpcomingHoliday, build_summary(), _holidays_for(), Dashboard summary service — assembles a per-user dashboard payload.  For the MVP

### Community 48 - "Community 48"
Cohesion: 0.42
Nodes (7): get_active_theme(), inject_css(), inject_login_css(), Theme + CSS injection for the entire app., Inject the base stylesheet + activate the current theme.      Should be called o, Inject the same stylesheet for the login page (without the app chrome)., _read()

### Community 49 - "Community 49"
Cohesion: 0.36
Nodes (6): date, _coerce_date(), _import_users(), main(), One-shot importer for data/users.json.  Preserves the existing bcrypt password h, Returns (imported, skipped_existing, flagged_must_reset).

### Community 50 - "Community 50"
Cohesion: 0.25
Nodes (3): ChatStreamSource, ChatStreamState, SSEEvent

### Community 51 - "Community 51"
Cohesion: 0.29
Nodes (6): FirstStep AI — Production Deployment, Production checklist, Services, Smoke tests, SSE streaming, Volumes

### Community 52 - "Community 52"
Cohesion: 0.38
Nodes (5): User settings (theme, language, telemetry) — 1:1 with users., UserSettings, get_or_create(), patch_settings(), Settings service — read/patch UserSettings (theme, language, telemetry).

### Community 53 - "Community 53"
Cohesion: 0.48
Nodes (6): _check(), main(), Verify Phase 1 end-to-end: schema creation, demo accounts, login, JWT round-trip, _reset_schema(), _seed_rbac(), _seed_users()

### Community 54 - "Community 54"
Cohesion: 0.48
Nodes (6): _check(), main(), _parse_sse(), Verify Phase 5: SSE chat streaming + persistence., _reset_db(), _seed()

### Community 55 - "Community 55"
Cohesion: 0.48
Nodes (6): _check(), main(), _parse_sse(), Verify Phase 6: /conversations CRUD + /messages + /feedback., _reset_db(), _seed()

### Community 56 - "Community 56"
Cohesion: 0.29
Nodes (4): Toast, ToastContext, ToastContextValue, ToastVariant

### Community 57 - "Community 57"
Cohesion: 0.33
Nodes (3): GUID, Platform-independent GUID stored as 36-char string on SQLite, native     UUID on, TypeDecorator

### Community 58 - "Community 58"
Cohesion: 0.53
Nodes (5): _check(), main(), Verify Phase 3 HTTP endpoints via FastAPI TestClient.  Ephemeral SQLite DB. Co, _reset(), _seed()

### Community 59 - "Community 59"
Cohesion: 0.53
Nodes (5): _check(), main(), Verify Phase 4: documents endpoints + RBAC enforcement + lifespan ensure_indexed, _reset_db(), _seed()

### Community 60 - "Community 60"
Cohesion: 0.60
Nodes (4): build_vectorstore(), ensure_store_dir(), load_vectorstore(), Chroma vector store factory (ported from rag/vectorstore.py).

### Community 61 - "Community 61"
Cohesion: 0.40
Nodes (4): get_redis(), Async Redis client for rate limiting + future pubsub., Return a process-wide async Redis client (lazy-initialized)., Redis

### Community 62 - "Community 62"
Cohesion: 0.50
Nodes (3): queryClient, App(), root

### Community 63 - "Community 63"
Cohesion: 0.60
Nodes (4): build_vectorstore(), ensure_store_dir(), load_vectorstore(), Chroma vector store factory.

### Community 64 - "Community 64"
Cohesion: 0.80
Nodes (4): check(), http(), login(), main()

### Community 65 - "Community 65"
Cohesion: 0.50
Nodes (3): setup_logging(), Logging setup — mirrors utils/logging.py from the existing app., Configure root logger to write to stderr at the requested level.

## Knowledge Gaps
- **116 isolated node(s):** `entrypoint.sh script`, `firststepai-api`, `name`, `private`, `version` (+111 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **25 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Document` connect `Community 30` to `Community 33`, `RAG Pipeline & Ingest`, `Community 41`, `Community 23`, `Community 24`, `Community 57`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Why does `User` connect `User & AuthService` to `Auth & Security Helpers`, `Community 33`, `App Entry & Auth UI`, `Chat Page & Prompts`, `RBAC & Role-Aware RAG`, `Community 37`, `Community 38`, `Admin & Profile Pages`, `Community 31`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Why does `User` connect `Community 23` to `Community 33`, `Community 34`, `Community 42`, `Config Package`, `Community 43`, `Community 45`, `Community 46`, `Community 20`, `Community 24`, `Community 57`, `Community 26`, `Community 27`, `Community 28`, `Community 30`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `User` (e.g. with `AuthService` and `SessionManager`) actually correct?**
  _`User` has 7 INFERRED edges - model-reasoned connections that need verification._
- **What connects `FirstStep AI — FastAPI backend.`, `Alembic environment configuration.  Reads DATABASE_URL from the application sett`, `Admin endpoints — user list/role change, activity log summary (Phase 7).` to the rest of the system?**
  _340 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Auth & Security Helpers` be split into smaller, more focused modules?**
  _Cohesion score 0.09852216748768473 - nodes in this community are weakly interconnected._
- **Should `User & AuthService` be split into smaller, more focused modules?**
  _Cohesion score 0.10810810810810811 - nodes in this community are weakly interconnected._