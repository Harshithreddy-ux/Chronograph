import boto3
import json
import os
from datetime import datetime
from typing import Dict, Any, List

class AWSService:
    """Handles all AWS integrations: S3, DynamoDB, Bedrock"""
    
    def __init__(self):
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self.s3_bucket = os.getenv("AWS_S3_BUCKET", "chronograph-execution-logs")
        self.dynamodb_table = os.getenv("AWS_DYNAMODB_TABLE", "ChronographSessions")
        
        # Initialize AWS clients
        self.s3 = boto3.client("s3", region_name=self.region)
        self.dynamodb = boto3.resource("dynamodb", region_name=self.region)
        self.table = self.dynamodb.Table(self.dynamodb_table)
    
    # ===== DynamoDB Session Management =====
    
    async def save_session(self, session_id: str, data: Dict[str, Any]):
        """Save session state to DynamoDB"""
        try:
            self.table.put_item(
                Item={
                    "session_id": session_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": json.dumps(data)
                }
            )
            return True
        except Exception as e:
            print(f"DynamoDB save error: {e}")
            return False
    
    async def get_session(self, session_id: str) -> Dict[str, Any]:
        """Retrieve session from DynamoDB"""
        try:
            response = self.table.get_item(Key={"session_id": session_id})
            if "Item" in response:
                return json.loads(response["Item"]["data"])
            return {}
        except Exception as e:
            print(f"DynamoDB get error: {e}")
            return {}
    
    async def append_message(self, session_id: str, role: str, content: str):
        """Append chat message to session history"""
        session = await self.get_session(session_id)
        if "messages" not in session:
            session["messages"] = []
        
        session["messages"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        await self.save_session(session_id, session)
    
    # ===== S3 Logging =====
    
    async def log_execution(self, session_id: str, log_type: str, data: Any):
        """Log execution data to S3"""
        try:
            key = f"{session_id}/{log_type}_{datetime.utcnow().isoformat()}.json"
            self.s3.put_object(
                Bucket=self.s3_bucket,
                Key=key,
                Body=json.dumps(data, indent=2),
                ContentType="application/json"
            )
            return key
        except Exception as e:
            print(f"S3 log error: {e}")
            return None
    
    async def get_execution_logs(self, session_id: str) -> List[str]:
        """List all logs for a session"""
        try:
            response = self.s3.list_objects_v2(
                Bucket=self.s3_bucket,
                Prefix=f"{session_id}/"
            )
            if "Contents" in response:
                return [obj["Key"] for obj in response["Contents"]]
            return []
        except Exception as e:
            print(f"S3 list error: {e}")
            return []
