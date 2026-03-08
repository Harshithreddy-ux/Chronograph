from fastapi import APIRouter, UploadFile, File, HTTPException
from services.ingestion import IngestionService
from services.graph_service import GraphService
from services.aws_service import AWSService
import tempfile
import os
import uuid

router = APIRouter()

graph_service = GraphService()
ingestion_service = IngestionService(graph_service)
aws_service = AWSService()

@router.post("/api/upload/code")
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
