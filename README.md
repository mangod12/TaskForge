# TaskForge

Multi-agent crisis logistics coordinator built with FastAPI, Gemini, MCP, PostgreSQL, and pgvector.

TaskForge turns a crisis request such as "Flood in Odisha causing food shortage across 3 districts" into a structured logistics plan. The app coordinates specialist agents, records task state in PostgreSQL, exposes MCP tools over SSE, and keeps deterministic fallbacks so the demo still produces operational output when the LLM is unavailable.

## What Is In This Repo

| Area | Path | What it does |
|---|---|---|
| FastAPI app | `app/main.py` | Mounts health, task/demo, static UI, and MCP endpoints. |
| Agent pipeline | `app/agents/` | Orchestrator, resource audit, planning, execution, and replanning agents. |
| MCP tools | `app/tools/` | Task, route, weather, calendar, and knowledge tools registered at startup. |
| Database | `app/db/`, `alembic/` | Async SQLAlchemy models, repositories, seed data, and migrations. |
| Memory/RAG | `app/memory/`, `app/llm/` | Context assembly, embeddings, Gemini client, and pgvector-backed knowledge. |
| API routes | `app/api/` | Health and task execution endpoints. |
| Static UI | `app/static/index.html`, `ui/app.py` | Browser dashboard and optional Streamlit UI. |
| Tests | `tests/` | Health, CRUD, validation, Gemini client, execution, and hardening tests. |

## Architecture

```text
User query
  -> FastAPI /execute or /api/v1/tasks
  -> OrchestratorAgent
       -> ResourceAgent      inventory and shortage analysis
       -> PlanningAgent      source depot, route, cost, ETA
       -> ExecutionAgent     subtasks, delivery schedule, dispatch actions
       -> ReplanningAgent    disruption reroute when crisis keywords appear
  -> Task repository + memory context
  -> JSON response with plan, tasks, risk notes, agent flow, and reliability fields
```

The app also mounts an MCP server:

- `GET /mcp/sse` for MCP SSE connections.
- `POST /mcp/messages/` for MCP message handling.

Registered tool modules are imported during FastAPI startup:

- `task_tools`
- `knowledge_tool`
- `calendar_tool`
- `weather_tool`
- `route_tool`

## API Surface

Core routes are mounted from `app/api/routes_health.py` and `app/api/routes_tasks.py`.

Common local routes:

| Route | Purpose |
|---|---|
| `GET /` | Static dashboard when `app/static/index.html` exists. |
| `GET /health` | Service readiness and startup status. |
| `POST /execute` | Run the crisis logistics agent pipeline. |
| `GET /api/v1/tasks` | List stored tasks. |
| `POST /api/v1/tasks` | Create a task. |
| `DELETE /api/v1/tasks/{task_id}` | Delete a task. |
| `GET /docs` | Swagger UI. |
| `GET /mcp/sse` | MCP SSE transport. |

## Local Development

TaskForge expects PostgreSQL with pgvector for the full path. The included compose file starts the database service.

```bash
git clone https://github.com/mangod12/TaskForge.git
cd TaskForge

python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell users can use .venv\Scripts\Activate.ps1
pip install -r requirements.txt

docker compose up -d db
uvicorn app.main:app --reload --port 8000
```

Open:

- Dashboard: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

Run a scenario:

```bash
curl -X POST http://localhost:8000/execute ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"Flood in Odisha causing food shortage across 3 districts\"}"
```

## Configuration

Start from `.env.example`.

Important settings:

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Async SQLAlchemy database URL. |
| `GEMINI_API_KEY` | Gemini API key for LLM-backed agent output. |
| `GEMINI_MODEL` | Model name. CI currently uses `gemini-2.0-flash`; deployment config uses `gemini-2.5-flash`. |
| `USE_VERTEX_AI` | Enables Vertex AI path when configured. |
| `LOG_LEVEL` | Runtime logging level. |

When no LLM path is available, the agents use fallback logic for credible demo output.

## Tests

```bash
python -m pytest tests/ -v --tb=short
```

The CI workflow starts `pgvector/pgvector:pg16`, installs dependencies, and runs the full `tests/` directory.

## Deployment

The repo includes:

- `Dockerfile`
- `docker-compose.yml`
- `.github/workflows/ci.yml`
- `.github/workflows/deploy.yml`

The Cloud Run deploy workflow builds an image, deploys service `taskforge`, attaches a Cloud SQL instance, sets Gemini configuration, and verifies `/health`.

The README intentionally does not link a live demo URL as a source of truth. Use the GitHub Actions deployment output or Cloud Run service URL after the current deployment is healthy.

## Current Limitations

- Startup DB initialization and preset warmup are deferred; `/health` should be checked before demos.
- pgvector is required for the intended PostgreSQL-backed memory path.
- The static dashboard is a lightweight reviewer surface, not a full operations console.
- MCP transport is SSE-based and intended for compatible MCP clients.

## License

MIT. See [LICENSE](LICENSE).
