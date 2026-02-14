from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

from services.ingestion import IngestionService
from services.graph_service import GraphService
from services.agent_orchestrator import AgentOrchestrator
from services.simulation import SimulationService

load_dotenv()

app = FastAPI(title="ChronoGraph API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
graph_service = GraphService()
ingestion_service = IngestionService(graph_service)
simulation_service = SimulationService()
agent_orchestrator = AgentOrchestrator(graph_service)


class MissionStartRequest(BaseModel):
    repo_url: str
    fault_type: str = "race_condition"


class ChatRequest(BaseModel):
    message: str
    session_id: str


class SimulationRunRequest(BaseModel):
    session_id: str


@app.post("/api/mission/start")
async def start_mission(request: MissionStartRequest):
    """Initialize E2B sandbox, ingest repo, inject fault"""
    try:
        # Clone and ingest repository
        repo_path = await ingestion_service.clone_repo(request.repo_url)
        await ingestion_service.parse_and_store(repo_path)
        
        # Initialize E2B sandbox
        sandbox_id = await simulation_service.create_sandbox(repo_path)
        
        # Inject fault
        await simulation_service.inject_fault(sandbox_id, request.fault_type)
        
        return {
            "status": "success",
            "sandbox_id": sandbox_id,
            "message": "Mission initialized successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Main entry for LangGraph agent interaction"""
    try:
        response = await agent_orchestrator.process_message(
            request.message,
            request.session_id
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/graph")
async def get_graph():
    """Returns JSON of nodes/edges for React Flow"""
    try:
        graph_data = await graph_service.get_visualization_data()
        return graph_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/simulation/run")
async def run_simulation(request: SimulationRunRequest):
    """Triggers k6 load test in the sandbox"""
    try:
        result = await simulation_service.run_load_test(request.session_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
