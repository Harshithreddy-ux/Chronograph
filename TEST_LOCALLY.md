# Test ChronoGraph Locally (Before AWS)

## Step 1: Start Neo4j
```bash
docker run --name chronograph-neo4j \
  -p7474:7474 -p7687:7687 \
  -e NEO4J_AUTH=neo4j/chronograph123 \
  -d neo4j
```

Visit http://localhost:7474 to verify Neo4j is running.

## Step 2: Install Backend Dependencies
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

## Step 3: Configure Environment
Create `backend/.env`:
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=chronograph123
AWS_REGION=us-east-1
AWS_S3_BUCKET=chronograph-execution-logs
AWS_DYNAMODB_TABLE=ChronographSessions
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

## Step 4: Start Backend
```bash
cd backend
uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Test: http://localhost:8000/health

## Step 5: Install Frontend Dependencies
```bash
cd frontend
npm install
```

## Step 6: Start Frontend
```bash
npm run dev
```

Visit: http://localhost:3000

## Step 7: Test the Flow

1. Click "Upload Python Code"
2. Select any `.py` file (try `backend/main.py`)
3. You should see:
   - Session ID appears
   - Graph populates with nodes
   - Can click nodes to view code

4. Type in chat: "What does this code do?"
5. AI responds (if AWS Bedrock is configured)

## Without AWS (Mock Mode)

If you don't have AWS configured yet, the app will still work but:
- Chat will fail (needs Bedrock)
- Session won't save to DynamoDB
- Logs won't save to S3

To test without AWS, comment out AWS calls in `backend/main.py`:
```python
# await aws_service.save_session(...)
# await aws_service.log_execution(...)
```

## Troubleshooting

### Neo4j connection failed
```bash
docker ps | grep neo4j
docker logs chronograph-neo4j
```

### Backend won't start
```bash
# Check Python version (need 3.9+)
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend build errors
```bash
# Clear cache
rm -rf node_modules package-lock.json
npm install
```

### Port already in use
```bash
# Kill process on port 8000
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:8000 | xargs kill -9
```
