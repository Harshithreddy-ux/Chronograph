# ChronoGraph

An agentic simulation environment for learning codebases through fault injection and debugging.

## Architecture

- **Frontend**: Next.js 14 with React Flow for graph visualization
- **Backend**: FastAPI with LangGraph for multi-agent orchestration
- **Database**: Neo4j for knowledge graph storage
- **Sandbox**: E2B for secure code execution

## Setup

### Prerequisites

- Node.js 18+
- Python 3.10+
- Docker & Docker Compose
- E2B API Key (get from https://e2b.dev)
- OpenAI API Key

### 1. Start Neo4j

```bash
docker-compose up -d
```

Access Neo4j Browser at http://localhost:7474 (neo4j/chronograph123)

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your API keys
```

Run backend:
```bash
python main.py
```

API will be available at http://localhost:8000

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at http://localhost:3000

## Usage

1. Open http://localhost:3000
2. Enter a GitHub repository URL
3. Select a fault type (race_condition, memory_leak, deadlock)
4. Click "Start Mission"
5. Explore the dependency graph
6. Chat with the tutor agent to learn about the injected bug
7. Use the time-travel slider to see execution states

## API Endpoints

- `POST /api/mission/start` - Initialize sandbox and inject fault
- `POST /api/chat` - Interact with tutor agent
- `GET /api/graph` - Get dependency graph data
- `POST /api/simulation/run` - Run k6 load test

## Project Structure

```
chronograph/
├── backend/
│   ├── main.py                    # FastAPI app
│   ├── services/
│   │   ├── ingestion.py          # Code parsing & graph population
│   │   ├── graph_service.py      # Neo4j operations
│   │   ├── simulation.py         # E2B sandbox management
│   │   └── agent_orchestrator.py # LangGraph agents
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── page.tsx              # Main UI
│   │   └── layout.tsx
│   ├── components/
│   │   ├── DependencyGraph.tsx   # React Flow visualization
│   │   ├── CodeEditor.tsx        # Monaco editor
│   │   ├── ChatInterface.tsx     # Agent chat
│   │   └── TimelineSlider.tsx    # Time-travel control
│   └── package.json
└── docker-compose.yml             # Neo4j setup
```

## Features Implemented

- Repository ingestion with Tree-sitter parsing  
- Neo4j knowledge graph storage  
- E2B sandbox initialization  
- Fault injection (race conditions, memory leaks)  
- LangGraph multi-agent system (Supervisor, Tutor, Debugger)  
- React Flow dependency visualization  
- Monaco code editor  
- Chat interface with scaffolding prompts  
- Time-travel debugging UI  

## Next Steps

- Implement actual time-travel state recording
- Add more fault injection patterns
- Enhance graph layout algorithms
- Add code patching and verification
- Implement session persistence
