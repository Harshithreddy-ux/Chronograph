# ChronoGraph AWS Deployment Checklist

## ✅ What You've Done
- [x] Created S3 bucket: `chronograph-execution-logs`
- [x] Created DynamoDB table: `ChronographSessions`
- [x] Created IAM Role: `ChronographEC2Role`
- [x] Launched EC2 instance with Neo4j
- [x] Enabled Bedrock model access

## 🔧 What You Need to Do Now

### 1. Update EC2 Backend Code
SSH into your EC2 instance:
```bash
ssh ubuntu@<YOUR-EC2-IP>
cd Chronograph
git pull origin master
```

### 2. Install Python Dependencies
```bash
source venv/bin/activate
pip install boto3 langchain-aws
```

### 3. Configure Environment Variables
Edit `.env` file on EC2:
```bash
nano backend/.env
```

Paste:
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=chronograph123
AWS_REGION=us-east-1
AWS_S3_BUCKET=chronograph-execution-logs
AWS_DYNAMODB_TABLE=ChronographSessions
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

### 4. Restart Backend
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Update Frontend API URL
In `frontend/components/ChatInterface.tsx` and `DependencyGraph.tsx`, replace:
```typescript
'http://localhost:8000'
```
with:
```typescript
'http://<YOUR-EC2-PUBLIC-IP>:8000'
```

Or better, create `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://<YOUR-EC2-PUBLIC-IP>:8000
```

Then use in code:
```typescript
fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/chat`, ...)
```

### 6. Deploy Frontend to Amplify
Push changes to GitHub:
```bash
git add .
git commit -m "Wire AWS services"
git push origin master
```

Amplify will auto-deploy.

### 7. Update CORS on Backend
Once you have your Amplify URL (e.g., `https://main.xxxxx.amplifyapp.com`), update `backend/main.py`:
```python
allow_origins=["http://localhost:3000", "https://main.xxxxx.amplifyapp.com"]
```

## 🧪 Testing the Flow

### Test 1: Upload Code
1. Go to your Amplify URL
2. Click "Upload Python Code"
3. Upload a `.py` file
4. Should see session ID appear

### Test 2: View Graph
- Graph should populate with nodes from your code
- Nodes = files and functions
- Edges = relationships (CONTAINS, CALLS)

### Test 3: Chat with AI
1. Click on a function node
2. Ask: "What does this function do?"
3. AI should respond using Bedrock

### Test 4: Check AWS Services
- **DynamoDB**: Go to AWS Console → DynamoDB → ChronographSessions → Items
  - Should see session entries
- **S3**: Go to S3 → chronograph-execution-logs
  - Should see folders with session IDs containing logs

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check logs
journalctl -u chronograph-backend -f

# Test Neo4j connection
docker ps | grep neo4j
```

### Bedrock permission denied
```bash
# Verify IAM role attached to EC2
aws sts get-caller-identity

# Test Bedrock access
python3 -c "import boto3; print(boto3.client('bedrock-runtime').list_foundation_models())"
```

### Frontend can't reach backend
- Check EC2 Security Group allows port 8000
- Verify backend is running: `curl http://localhost:8000/health`
- Check CORS settings in `main.py`

## 📊 Architecture Flow

```
User uploads .py file
    ↓
Frontend (Amplify) → POST /api/upload/code
    ↓
Backend (EC2) parses with tree-sitter
    ↓
Stores in Neo4j graph database
    ↓
Returns graph data + session_id
    ↓
Frontend displays graph
    ↓
User clicks node + asks question
    ↓
Backend queries Neo4j for context
    ↓
Sends to Bedrock (Claude) with RAG
    ↓
Saves chat to DynamoDB
    ↓
Logs execution to S3
    ↓
Returns AI response to user
```

## 🎯 Next Steps
1. Add error highlighting in CodeEditor
2. Implement TimelineSlider with execution traces
3. Add E2B sandbox for running code
4. Create simulation with k6 load testing
