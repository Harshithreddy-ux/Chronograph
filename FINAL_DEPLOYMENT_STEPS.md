# Final Deployment Steps

## ✅ What's Now Working

1. **Upload Python Code** → Parses with tree-sitter → Creates graph in Neo4j ✅
2. **Block Diagram** → Shows files (green) and functions (blue) ✅
3. **Click Block** → Shows code snippet in editor on right ✅
4. **AI Chatbot** → Answers questions using Bedrock (Claude) ✅
5. **Timeline Slider** → Placeholder for future execution tracing

## 🚀 Deploy to AWS

### Step 1: Push Changes to GitHub
```bash
git add .
git commit -m "Wire complete flow: upload → graph → code view → AI chat"
git push origin master
```

### Step 2: Update EC2 Backend
```bash
# SSH into your EC2
ssh ubuntu@<YOUR-EC2-IP>

# Navigate to repo
cd Chronograph

# Pull latest changes
git pull origin master

# Activate virtual environment
source venv/bin/activate

# Install new dependencies
pip install -r backend/requirements.txt

# Update .env file with your AWS resources
nano backend/.env
```

Your `.env` should have:
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=chronograph123
AWS_REGION=us-east-1
AWS_S3_BUCKET=chronograph-execution-logs
AWS_DYNAMODB_TABLE=ChronographSessions
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

### Step 3: Restart Backend Service
```bash
# Kill existing process
pkill -f uvicorn

# Start new process
cd backend
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > ../logs.txt 2>&1 &

# Verify it's running
curl http://localhost:8000/health
```

### Step 4: Update Frontend API URL

Create `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://<YOUR-EC2-PUBLIC-IP>:8000
```

Then update the components to use it:

In `frontend/components/ChatInterface.tsx`, `DependencyGraph.tsx`, and `frontend/app/page.tsx`:
```typescript
// Replace 'http://localhost:8000' with:
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Then use:
fetch(`${API_URL}/api/chat`, ...)
```

### Step 5: Push Frontend Changes
```bash
git add .
git commit -m "Update API URL for production"
git push origin master
```

Amplify will auto-deploy in ~5 minutes.

### Step 6: Update CORS on Backend

Once you have your Amplify URL (e.g., `https://main.d1234.amplifyapp.com`), update `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://main.d1234.amplifyapp.com"  # Your Amplify URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Restart backend:
```bash
pkill -f uvicorn
cd backend
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > ../logs.txt 2>&1 &
```

## 🧪 Test the Complete Flow

1. Go to your Amplify URL
2. Click "Upload Python Code"
3. Upload a `.py` file
4. **See block diagram** with green (files) and blue (functions) nodes
5. **Click a blue function node**
6. **See code snippet** appear in the right panel
7. **Ask AI**: "What does this function do?"
8. **Get response** from Bedrock explaining the code

## 📊 What Each Component Does

### Timeline Slider (Not Implemented Yet)
This is a placeholder for future features:
- Show execution flow over time
- Step through code execution
- Visualize race conditions/deadlocks
- Replay debugging sessions

To implement later, you'd need:
- E2B sandbox to run code
- Execution tracing
- Store execution states in S3
- Replay mechanism

## 🐛 Troubleshooting

### Graph shows but clicking does nothing
- Check browser console for errors
- Verify `/api/function/{name}` endpoint works: `curl http://localhost:8000/api/function/main?file=main.py`

### AI chat not responding
- Check Bedrock access: `aws bedrock list-foundation-models --region us-east-1`
- Verify IAM role attached to EC2
- Check backend logs: `tail -f logs.txt`

### Frontend can't reach backend
- Check EC2 Security Group allows port 8000 from anywhere (0.0.0.0/0)
- Verify CORS settings include your Amplify URL
- Test: `curl http://<EC2-IP>:8000/health`

## 🎯 Architecture Flow

```
User uploads .py file
    ↓
Frontend sends to /api/upload/code
    ↓
Backend parses with tree-sitter
    ↓
Stores functions/calls in Neo4j
    ↓
Returns graph data to frontend
    ↓
Frontend displays block diagram
    ↓
User clicks function block
    ↓
Frontend fetches /api/function/{name}
    ↓
Backend queries Neo4j for source code
    ↓
Frontend displays in code editor
    ↓
User asks question in chat
    ↓
Backend queries Neo4j for context
    ↓
Sends to Bedrock with RAG
    ↓
Saves to DynamoDB + logs to S3
    ↓
Returns AI response
```

## ✨ You're Done!

Your app now:
- ✅ Uploads code
- ✅ Shows block diagram
- ✅ Displays code on click
- ✅ AI explains code
- ✅ Saves sessions to DynamoDB
- ✅ Logs to S3
- ✅ Uses Bedrock for AI

Timeline slider is a placeholder for future execution tracing features.
