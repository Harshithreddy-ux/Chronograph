Design Specification: ChronoGraph
1. Architecture Overview
ChronoGraph implements a Simulation-First Agentic Architecture. It decouples the "Knowledge Plane" (Static Analysis) from the "Execution Plane" (Runtime Simulation).

System Diagrammermaid
graph TD
User -->|Interacts| UI[Next.js Frontend]
UI -->|API Calls| API
subgraph "Orchestration Layer"
    API -->|Manages| Supervisor
    Supervisor -->|Routes| Tutor
    Supervisor -->|Routes| Debugger
end

subgraph "Knowledge Plane"
    Ingest -->|Writes| Neo4j
    Tutor -->|Queries| Neo4j
end

subgraph "Execution Plane (Simulation)"
    Debugger -->|Controls| E2B
    E2B -->|Runs| App[User Code]
    E2B -->|Runs| Chaos[Fault Injector]
    E2B -->|Runs| Load
end
## 2. Core Components

### A. Frontend (Interface)
*   **Framework:** Next.js 14 (App Router)
*   **Visualizer:** React Flow (XyFlow) for rendering the Dependency Graph.
*   **Editor:** Monaco Editor for code viewing and patching.
*   **State:** Zustand for managing the "Time Travel" slider position.

### B. Backend (Orchestration)
*   **Framework:** Python FastAPI.
*   **Agent Framework:** LangGraph (Stateful Multi-Agent Workflow).
*   **Agents:**
    *   `Supervisor`: Router and state manager.
    *   `Tutor`: RAG-enabled pedagogue (Access to Neo4j).
    *   `Chaos`: Responsible for breaking the code in E2B.

### C. Data Persistence (Knowledge Graph)
*   **Database:** Neo4j (AuraDB or Local Docker).
*   **Schema Definition:**
    *   `(:File {path, language})`
    *   `(:Function {name, start_line, end_line, source})`
    *   `(:Function)-->(:Function)`
    *   `(:File)-->(:Module)`

### D. Runtime Environment (E2B)
*   **Container:** Firecracker MicroVM (via E2B SDK).
*   **Tools Installed:** Python 3.10, k6 (Load Testing), Pytest.
*   **Security:** No root access for user; outbound network restricted to package managers.

## 3. Data Flow

### Ingestion Pipeline
1.  **Input:** Git Clone URL.
2.  **Process:** Recursive file walk -> Tree-sitter Parse -> Extract AST Nodes.
3.  **Storage:** Batch write nodes and edges to Neo4j.

### The "Tutoring Loop"
1.  **User Input:** "Why is the request failing?"
2.  **Graph Retrieval:** Tutor Agent performs a Cypher query:
    ```cypher
    MATCH (f:Function {name: 'handle_request'})-->(d:Dependency)
    RETURN f, d
    ```
3.  **Context Construction:** LLM receives the code + the graph topology.
4.  **Response:** "Notice that `handle_request` calls `db_save` without a retry mechanism."

## 4. API Specification

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/mission/start` | Initializes E2B sandbox, runs ingestion, injects fault. |
| `POST` | `/api/chat` | Main entry for LangGraph agent interaction. |
| `GET` | `/api/graph` | Returns JSON of nodes/edges for React Flow. |
| `POST` | `/api/simulation/run` | Triggers k6 load test in the sandbox. |

## 5. Security & Constraints
*   **Sandboxing:** All user-submitted code MUST run inside E2B.
*   **Rate Limiting:** Maximum 5 simulation runs per minute per user.
*   **Data Minimization:** Only store code metadata in Neo4j; do not store full proprietary source code if possible.