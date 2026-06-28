# Graph Report - .  (2026-06-26)

## Corpus Check
- 51 files · ~37,802 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 311 nodes · 729 edges · 20 communities (11 shown, 9 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 29 edges (avg confidence: 0.67)
- Token cost: 19,532 input · 0 output

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
- [[_COMMUNITY_bcrypt|bcrypt]]
- [[_COMMUNITY_Faker|Faker]]
- [[_COMMUNITY_itsdangerous|itsdangerous]]
- [[_COMMUNITY_python-dotenv|python-dotenv]]

## God Nodes (most connected - your core abstractions)
1. `User` - 56 edges
2. `get_settings()` - 35 edges
3. `Role` - 24 edges
4. `LocalAuthProvider` - 20 edges
5. `AuthService` - 18 edges
6. `AuthProvider` - 16 edges
7. `get_auth_service()` - 15 edges
8. `SessionManager` - 15 edges
9. `AI-Generated Assignment Rules (Annex K)` - 14 edges
10. `get_session()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `ChromaDB Vector Store + RAG Pipeline` --references--> `pypdf 5.0.1`  [INFERRED]
  data/umbrella_corp_policies.pdf → requirements.txt
- `Web Search Tools (DuckDuckGo, Arxiv, Wikipedia)` --references--> `langchain-community 0.3.14`  [INFERRED]
  data/umbrella_corp_policies.pdf → requirements.txt
- `LLM-Driven Quiz Generation` --references--> `langchain-groq >=0.2.0`  [EXTRACTED]
  data/umbrella_corp_policies.pdf → requirements.txt
- `ChromaDB Vector Store + RAG Pipeline` --references--> `chromadb 0.5.23`  [EXTRACTED]
  data/umbrella_corp_policies.pdf → requirements.txt
- `ChromaDB Vector Store + RAG Pipeline` --references--> `langchain-chroma 0.2.0`  [EXTRACTED]
  data/umbrella_corp_policies.pdf → requirements.txt

## Import Cycles
- 1-file cycle: `ui/__init__.py -> ui/__init__.py`

## Hyperedges (group relationships)
- **LangChain Ecosystem Dependencies** — requirements_langchain, requirements_langchain_community, requirements_langchain_huggingface, requirements_langchain_chroma, requirements_langchain_groq, requirements_chromadb [INFERRED 0.95]
- **Streamlit Application Runtime Dependencies** — requirements_streamlit, requirements_pydantic, requirements_pydantic_settings, requirements_bcrypt, requirements_itsdangerous, requirements_python_dotenv [INFERRED 0.85]
- **Document Processing and Test Data Generation** — requirements_pypdf, requirements_faker [INFERRED 0.75]

## Communities (20 total, 9 thin omitted)

### Community 0 - "Auth & Security Helpers"
Cohesion: 0.08
Nodes (39): Any, _get_serializer(), hash_password(), Password hashing and signed token helpers., Hash a password with bcrypt., Constant-time bcrypt comparison., Return a signed, max-age-limited token. `max_age` is in seconds., Verify a token. Returns the payload dict or None if invalid/expired. (+31 more)

### Community 1 - "User & AuthService"
Cohesion: 0.08
Nodes (22): ABC, An authenticated user account. Persisted to data/users.json., User, AuthService, Generate a reset token for the given email.          Demo-only behaviour: the to, _next_holiday(), Dashboard page — Active Projects, Leave Balance, Upcoming Holidays, AI Usage., render_dashboard() (+14 more)

### Community 2 - "App Entry & Auth UI"
Cohesion: 0.09
Nodes (31): FirstStepAI — Enterprise AI Assistant entrypoint.  Orchestrates the boot sequenc, Render the login form. Returns True if the user was just authenticated., Open the forgot-password flow inside a Streamlit modal., render_compact_login_form(), render_forgot_password_dialog(), BaseSettings, Application configuration loaded from environment / .env file., Settings (+23 more)

### Community 3 - "Chat Page & Prompts"
Cohesion: 0.07
Nodes (24): Back-compat shim — the `Assistant` class has moved to `services.chat_service.Cha, BaseMessage, _build_chat_service(), Chat page — streaming chat with employee context and role-aware RAG., Lazy-construct (or re-bind) the ChatService for the current user., render_chat(), Prompts package — system prompt, welcome message, per-role suggestions., System prompt for the Umbrella Corp AI assistant.  Injects the logged-in employe (+16 more)

### Community 4 - "RBAC & Role-Aware RAG"
Cohesion: 0.13
Nodes (18): Permission, Auth models — User, Role, Permission., Role, BaseRetriever, Cross-cutting concerns: session management, RBAC, exceptions.  Note: this packag, allowed_doc_roles(), can_access(), permissions_for_role() (+10 more)

### Community 5 - "RAG Pipeline & Ingest"
Cohesion: 0.15
Nodes (21): Document, HuggingFaceEndpointEmbeddings, Path, build_embeddings(), Embedding model factory., Return the HF inference-API embeddings used for both ingest and query.      Fall, add_document_text(), ensure_indexed() (+13 more)

### Community 6 - "Umbrella Corp Policy Rules"
Cohesion: 0.12
Nodes (24): AI-Generated Assignment Rules (Annex K), 80% Quiz Pass Threshold, FirstStepAI Onboarding System, Hallucination Control via System-Prompt Guardrails, LangChain Agent Orchestration, LLM-Driven Quiz Generation, Manager Approval Escalation, Mixed Multiple-Choice and Numerical Quiz (+16 more)

### Community 7 - "Employee Profile"
Cohesion: 0.16
Nodes (15): EmployeeProfile, Extended employee fields the chatbot can talk about., Format the profile for system-prompt injection., BaseModel, _default_permissions_for(), generate_employee_data(), load_employee_profile_for_email(), _make_employee_id() (+7 more)

### Community 8 - "Admin & Profile Pages"
Cohesion: 0.24
Nodes (10): get_auth_service(), Raised when an authenticated user tries to access a protected resource., UnauthorizedError, Admin page — user management and document upload (gated to Role.ADMIN)., render_admin(), My Profile page — view and edit the logged-in user's profile + change password., render_profile(), get_employee_profile() (+2 more)

## Knowledge Gaps
- **12 isolated node(s):** `Umbrella Corporation`, `30-Second Intro Video + 10-Question Quiz`, `Mixed Multiple-Choice and Numerical Quiz`, `langchain-huggingface`, `streamlit 1.38.0` (+7 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User & AuthService` to `Auth & Security Helpers`, `App Entry & Auth UI`, `Chat Page & Prompts`, `RBAC & Role-Aware RAG`, `Employee Profile`, `Admin & Profile Pages`, `Session Manager`?**
  _High betweenness centrality (0.196) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `Auth & Security Helpers` to `User & AuthService`, `App Entry & Auth UI`, `Chat Page & Prompts`, `RAG Pipeline & Ingest`, `Employee Profile`, `Session Manager`?**
  _High betweenness centrality (0.133) - this node is a cross-community bridge._
- **Why does `Role` connect `RBAC & Role-Aware RAG` to `Auth & Security Helpers`, `App Entry & Auth UI`, `Chat Page & Prompts`, `Employee Profile`, `Admin & Profile Pages`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `User` (e.g. with `AuthService` and `SessionManager`) actually correct?**
  _`User` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `Role` (e.g. with `LocalAuthProvider` and `Config`) actually correct?**
  _`Role` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `LocalAuthProvider` (e.g. with `AuthService` and `Role`) actually correct?**
  _`LocalAuthProvider` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `AuthService` (e.g. with `User` and `InvalidCredentialsError`) actually correct?**
  _`AuthService` has 5 INFERRED edges - model-reasoned connections that need verification._