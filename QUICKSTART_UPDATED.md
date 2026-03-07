# ChronoGraph - Quick Start Guide

## 🚀 How It Works Now

1. **Upload Python Code** → File gets parsed with tree-sitter
2. **Graph Generated** → Functions and calls stored in Neo4j
3. **Click on Node** → View code snippet
4. **Ask AI** → Bedrock (Claude) explains errors using graph context
5. **Chat History** → Saved to DynamoDB
6. **Execution Logs** → Stored in S3

## 🏃 Run Locally (Development)

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start Neo4j with Docker
docker run --name neo4j -p7474:7474 -p7687:7687 \
  -e NEO4J_AUTH=neo4j/chronograph123 -d neo4j

# Run backend
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Visit: http://localhost:3000

## 🧪 Test the Flow

1. Click "Upload Python Code"
2. Select a `.py` file (try `backend/main.py`)
3. Wait for graph to appear
4. Click on a function node
5. Ask: "What does this function do?"
6. AI responds using Bedrock

## ☁️ Deploy to AWS (Production)

### Prerequisites
- AWS Account
- EC2 instance running
- Neo4j on EC2
- Bedrock access enabled
- S3 bucket created
- DynamoDB table created

### Update Backend on EC2
```bash
ssh ubuntu@<EC2-IP>
cd Chronograph
git pull
source venv/bin/activate
pip install -r backend/requirements.txt

# Update .env with your AWS resources
nano backend/.env

# Restart backend
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Deploy Frontend to Amplify
```bash
git add .
git commit -m "Wire AWS services"
git push origin master
```

Amplify auto-deploys from GitHub.

### Update API URL
In `frontend/components/ChatInterface.tsx` and `DependencyGraph.tsx`:
```typescript
// Change from:
'http://localhost:8000'

// To:
'http://<YOUR-EC2-IP>:8000'
```

Or create `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://<YOUR-EC2-IP>:8000
```

## 🔧 Environment Variables

### Backend `.env`
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=chronograph123
AWS_REGION=us-east-1
AWS_S3_BUCKET=chronograph-execution-logs
AWS_DYNAMODB_TABLE=ChronographSessions
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

### Frontend `.env.local`
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📊 Check AWS Resources

### DynamoDB
```bash
aws dynamodb scan --table-name ChronographSessions
```

### S3
```bash
aws s3 ls s3://chronograph-execution-logs/
```

### Bedrock
```bash
aws bedrock list-foundation-models --region us-east-1
```

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Neo4j
docker ps | grep neo4j

# Test connection
python -c "from neo4j import GraphDatabase; print('OK')"
```

### Frontend can't reach backend
- Check CORS in `backend/main.py`
- Verify backend is running: `curl http://localhost:8000/health`
- Check EC2 Security Group allows port 8000

### Bedrock errors
- Verify IAM role attached to EC2
- Check model access in Bedrock console
- Test: `aws bedrock-runtime invoke-model --help`

## 📝 API Endpoints

- `POST /api/upload/code` - Upload Python file
- `POST /api/chat` - Send message to AI
- `GET /api/graph` - Get dependency graph
- `GET /api/session/{id}/history` - Get chat history
- `GET /health` - Health check

## 🎯 What's Next

- Add error highlighting in code editor
- Implement execution timeline
- Add E2B sandbox for running code
- Create load testing simulation
