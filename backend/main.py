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

# In-memory store for uploaded code (session_id -> full_code)
code_store = {}


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
        # Always include full code context so AI knows everything
        full_code = code_store.get(request.session_id, "")
        
        # Build context message
        message_with_context = request.message
        if full_code:
            message_with_context = f"""You have access to this codebase:

```python
{full_code}
```

User question: {request.message}

Remember: Be conversational. Ask clarifying questions. Don't dump all info at once. Guide the user through understanding."""
        
        # Try to save to AWS (optional for local dev)
        try:
            await aws_service.append_message(request.session_id, "user", request.message)
        except Exception as aws_error:
            print(f"AWS logging skipped (local mode): {aws_error}")
        
        # Process through agent
        response = await agent_orchestrator.process_message(
            message_with_context,
            request.session_id
        )
        
        # Try to save to AWS (optional for local dev)
        try:
            await aws_service.append_message(request.session_id, "assistant", response)
            await aws_service.log_execution(
                request.session_id,
                "chat",
                {"user": request.message, "assistant": response}
            )
        except Exception as aws_error:
            print(f"AWS logging skipped (local mode): {aws_error}")
        
        return {"response": response}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/graph")
async def get_graph():
    """Returns JSON of nodes/edges for React Flow"""
    try:
        graph_data = await graph_service.get_visualization_data()
        return graph_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/graph/clear")
async def clear_graph():
    """Clear all nodes and edges from Neo4j"""
    try:
        await graph_service.clear_all()
        # Also clear the code store
        code_store.clear()
        return {"status": "success", "message": "Graph cleared"}
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
        
        # Count errors and improvements separately
        error_count = sum(1 for node in graph_data['nodes'] if node.get('has_error'))
        improvement_count = sum(1 for node in graph_data['nodes'] if node.get('has_improvement'))
        
        # Try to save to AWS (optional for local dev)
        try:
            await aws_service.save_session(session_id, {
                "file_name": file.filename,
                "file_path": file_path,
                "graph_nodes": len(graph_data["nodes"]),
                "graph_edges": len(graph_data["edges"])
            })
            
            await aws_service.log_execution(session_id, "upload", {
                "filename": file.filename,
                "size": len(content)
            })
        except Exception as aws_error:
            print(f"AWS logging skipped (local mode): {aws_error}")
        
        return {
            "session_id": session_id,
            "graph": graph_data,
            "errors": error_count,
            "improvements": improvement_count,
            "message": "Code uploaded and analyzed successfully"
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/session/{session_id}/history")
async def get_session_history(session_id: str):
    """Get chat history for a session"""
    try:
        session = await aws_service.get_session(session_id)
        return {"messages": session.get("messages", [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/execution-timeline")
async def get_execution_timeline():
    """Get execution timeline events for debugging"""
    try:
        # Get all function nodes from graph
        graph_data = await graph_service.get_visualization_data()
        
        # Generate mock execution timeline based on function calls
        events = []
        timestamp = 0
        
        # Find all CALLS relationships
        call_edges = [e for e in graph_data['edges'] if e['type'] == 'CALLS']
        
        # Create timeline events
        for edge in call_edges:
            source_node = next((n for n in graph_data['nodes'] if n['id'] == edge['source']), None)
            target_node = next((n for n in graph_data['nodes'] if n['id'] == edge['target']), None)
            
            if source_node and target_node:
                # Call event
                events.append({
                    'timestamp': timestamp,
                    'function': target_node['name'],
                    'file': target_node.get('file_path', 'unknown'),
                    'type': 'call',
                    'details': f"Called by {source_node['name']}"
                })
                timestamp += 10
                
                # Return event
                events.append({
                    'timestamp': timestamp,
                    'function': target_node['name'],
                    'file': target_node.get('file_path', 'unknown'),
                    'type': 'return',
                    'details': f"Returned to {source_node['name']}"
                })
                timestamp += 5
                
                # Add error event if function has error
                if target_node.get('has_error'):
                    events.append({
                        'timestamp': timestamp - 3,
                        'function': target_node['name'],
                        'file': target_node.get('file_path', 'unknown'),
                        'type': 'error',
                        'details': target_node.get('error_types', 'Unknown error')
                    })
        
        return {"events": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
