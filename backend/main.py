from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import uuid
import tempfile
from dotenv import load_dotenv

from services.ingestion import IngestionService
from services.graph_service import GraphService
from services.agent_orchestrator import AgentOrchestrator
from services.simulation import SimulationService
from services.aws_service import AWSService

load_dotenv()

app = FastAPI(title="ChronoGraph API")

# Allow both localhost and Amplify frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.amplifyapp.com", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
aws_service = AWSService()
graph_service = GraphService()
ingestion_service = IngestionService(graph_service)
simulation_service = SimulationService()
agent_orchestrator = AgentOrchestrator(graph_service, aws_service)


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
        # Save user message to DynamoDB
        await aws_service.append_message(request.session_id, "user", request.message)
        
        # Process through agent
        response = await agent_orchestrator.process_message(
            request.message,
            request.session_id
        )
        
        # Save assistant response to DynamoDB
        await aws_service.append_message(request.session_id, "assistant", response)
        
        # Log to S3
        await aws_service.log_execution(
            request.session_id,
            "chat",
            {"user": request.message, "assistant": response}
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


@app.get("/api/function/{function_name}")
async def get_function_code(function_name: str, file: str):
    """Get source code for a specific function"""
    try:
        function_data = await graph_service.get_function_source(function_name, file)
        return function_data
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


@app.post("/api/upload/code")
async def upload_code(file: UploadFile = File(...)):
    """
    Upload code file, parse it, create graph, return session_id
    This is the main entry point when user uploads code
    """
    try:
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Save uploaded file temporarily
        temp_dir = tempfile.mkdtemp(prefix="chronograph_")
        file_path = os.path.join(temp_dir, file.filename)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Parse and store in Neo4j
        await ingestion_service.parse_and_store(temp_dir)
        
        # Get graph data for frontend
        graph_data = await graph_service.get_visualization_data()
        
        # Save session to DynamoDB
        await aws_service.save_session(session_id, {
            "file_name": file.filename,
            "file_path": file_path,
            "graph_nodes": len(graph_data["nodes"]),
            "graph_edges": len(graph_data["edges"])
        })
        
        # Log to S3
        await aws_service.log_execution(session_id, "upload", {
            "filename": file.filename,
            "size": len(content)
        })
        
        return {
            "session_id": session_id,
            "graph": graph_data,
            "message": "Code uploaded and analyzed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/session/{session_id}/history")
async def get_session_history(session_id: str):
    """Get chat history for a session"""
    try:
        session = await aws_service.get_session(session_id)
        return {"messages": session.get("messages", [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
