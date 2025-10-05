# Astrobiomers Frontend# Astrobiomers Frontend Wrapper



The original frontend has been replaced by the new application located in `./new frontend` (provided by your collaborator). This folder now acts as a thin wrapper so existing tooling continues to work.The original frontend has been replaced by the new application located in `./new frontend` (provided by your collaborator). This folder now acts as a thin wrapper so existing tooling continues to work without modifying the new codebase.



> ✅ No files inside `frontend/new frontend` or `backend/` were modified. The integration uses a lightweight adapter service.> ✅ No files inside `frontend/new frontend` were changed. All commands below delegate to that project.



## 🚀 Quick Start (Three Services)## 🚀 Quick Start



Run these in **separate terminals**:```powershell

cd frontend

```powershellnpm run install            # installs dependencies inside "new frontend"

# Terminal 1: Backend API (existing FastAPI on port 8000)

cd backend# Backend (run from repository root in a separate terminal)

.\.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000cd backend

.\.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 5000

# Terminal 2: Adapter REST API (bridges new UI to backend on port 5000)

cd frontend# Frontend (new terminal)

python api_adapter.pycd frontend

npm run dev                # runs new frontend on http://localhost:3000

# Terminal 3: Frontend UI (Vite dev server on port 3000)```

cd frontend

npm install### Why port 5000 for the backend?

npm run devThe new UI expects the API at `http://localhost:5000/api`. Starting Uvicorn with `--port 5000` keeps the backend untouched while satisfying the new frontend’s defaults.

```

### Why port 3000 for the frontend?

Open **http://localhost:3000** in your browser.The FastAPI app already whitelists `http://localhost:3000` for CORS. The wrapper passes `--port 3000` when running `npm run dev`, so you don’t need to change the backend.



## 🔌 Architecture## � Available Wrapper Scripts



```| Command | What it does |

┌──────────────────┐|---------|---------------|

│   Browser        │ http://localhost:3000| `npm run install` | Runs `npm install` inside `new frontend` |

│  (React UI)      │| `npm run dev` | Delegates to `new frontend` dev server (port 3000) |

└────────┬─────────┘| `npm run build` | Builds the new frontend |

         │| `npm run preview` | Previews the production build |

         ▼ REST calls| `npm run lint` | Forwards to the new frontend lint command |

┌──────────────────┐| `npm run test` | Forwards to the new frontend test command |

│  Adapter API     │ http://localhost:5000/api

│  (api_adapter.py)│ - /knowledge-graphAll documentation, component guides, and extra scripts live in [`frontend/new frontend/README.md`](./new%20frontend/README.md) and the related docs inside that directory.

└────────┬─────────┘ - /paper/:id

         │## 🔌 Backend & Database

         ▼ Neo4j queries via QueryEngine

┌──────────────────┐The backend and Neo4j configuration remain exactly as before. Just make sure they’re running before launching the UI:

│  Backend API     │ http://localhost:8000

│  (FastAPI)       │ + Neo4j database```powershell

└──────────────────┘# Backend API

```cd backend

.\.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 5000

### Why an adapter?

The new UI expects endpoints like `GET /api/knowledge-graph?q=...` which differ from the original backend routes. The adapter (`frontend/api_adapter.py`) reuses `backend/knowledge_graph/query_engine.py` to fetch data from Neo4j and transforms it into the shape the frontend needs—**without editing either codebase**.# Neo4j (if using Docker)

docker compose up neo4j

## 📦 Available Commands```



| Command | Description |The frontend hits these endpoints:

|---------|-------------|

| `npm install` | Installs dependencies in `new frontend` |- `GET http://localhost:5000/api/knowledge-graph?q=...`

| `npm run dev` | Starts Vite dev server (port 3000) |- `GET http://localhost:5000/api/paper/:id`

| `npm run build` | Production build |

| `npm run preview` | Preview production build |If you prefer to keep the backend on port 8000, update its startup command to `--port 5000` or configure a reverse proxy—no code changes required.

| `npm run lint` | Lint code |

| `npm run test` | Run tests |## 📚 Need More Details?



All source code lives in `frontend/new frontend/src/`. See [`frontend/new frontend/README.md`](./new%20frontend/README.md) for component documentation.Refer to the detailed guides bundled with the new UI:



## 🔧 Configuration- [`frontend/new frontend/README.md`](./new%20frontend/README.md)

- [`frontend/new frontend/KNOWLEDGE_GRAPH_USER_GUIDE.md`](./new%20frontend/KNOWLEDGE_GRAPH_USER_GUIDE.md)

- **Backend:** Uses existing `.env` in `backend/` (Neo4j credentials, etc.)- [`frontend/new frontend/KNOWLEDGE_GRAPH_SETUP.md`](./new%20frontend/KNOWLEDGE_GRAPH_SETUP.md)

- **Adapter:** Automatically imports `QueryEngine` from `backend/`

- **Frontend:** Hardcoded to `http://localhost:5000/api` in `frontend/new frontend/src/pages/KnowledgeGraph.tsx` (line 12)These documents cover component architecture, design system, and deployment steps for the new interface.



No environment variables needed for the adapter—it reads Neo4j config through the backend's `QueryEngine`.---



## 🐛 TroubleshootingEnjoy the upgraded experience! �️🧬


**Adapter fails to import QueryEngine:**
```powershell
cd backend
.\.venv\Scripts\pip install -r requirements.txt
```

**Frontend can't reach API:**
- Verify adapter is running: `curl http://localhost:5000/api/health`
- Check CORS: Adapter allows `http://localhost:3000` by default

**Neo4j connection errors:**
- Ensure Neo4j is running (Docker: `docker compose up neo4j`)
- Verify credentials in `backend/.env`

## 📚 Documentation

- **New Frontend:** [`frontend/new frontend/README.md`](./new%20frontend/README.md)
- **User Guide:** [`frontend/new frontend/KNOWLEDGE_GRAPH_USER_GUIDE.md`](./new%20frontend/KNOWLEDGE_GRAPH_USER_GUIDE.md)
- **Setup Details:** [`frontend/new frontend/KNOWLEDGE_GRAPH_SETUP.md`](./new%20frontend/KNOWLEDGE_GRAPH_SETUP.md)

---

Built with ❤️ for space biology research 🚀🌌
