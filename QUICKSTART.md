# ChronoGraph - Quick Start

## Instant Demo (No Installation)

**Double-click `demo.html`** or run `start_demo.bat` to see the working prototype!

The demo includes:
- ✅ Interactive dependency graph visualization
- ✅ Code editor with injected fault examples
- ✅ AI tutor chat with scaffolding prompts
- ✅ Time-travel debugging slider
- ✅ Full UI/UX implementation

## What You're Seeing

The demo shows a Python Flask application with an injected **race condition** bug:
- The `handle_request()` function calls `db_save()` without thread synchronization
- Multiple concurrent requests can corrupt the database
- The tutor guides you to discover the bug using the Scaffolding pattern

## Full Installation (Optional)

To run the complete backend with real code analysis:

### Prerequisites
1. Install Node.js from https://nodejs.org
2. Install Docker Desktop from https://docker.com
3. Get API keys:
   - E2B: https://e2b.dev
   - OpenAI: https://platform.openai.com

### Setup Steps

1. **Start Neo4j Database**
   ```cmd
   docker-compose up -d
   ```

2. **Configure Backend**
   - Edit `backend/.env` and add your real API keys

3. **Install Backend Dependencies**
   ```cmd
   cd backend
   pip install -r requirements.txt
   python main.py
   ```

4. **Install Frontend Dependencies**
   ```cmd
   cd frontend
   npm install
   npm run dev
   ```

5. **Open Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Neo4j Browser: http://localhost:7474

## Project Status

✅ **Completed Features:**
- Repository ingestion with Tree-sitter parsing
- Neo4j knowledge graph storage
- E2B sandbox management
- Fault injection system (race conditions, memory leaks, deadlocks)
- LangGraph multi-agent orchestration
- React Flow dependency visualization
- Monaco code editor integration
- Scaffolding-based tutoring system
- Time-travel debugging UI
- Complete REST API

## Architecture

```
Frontend (Next.js 14)
    ↓ HTTP
Backend (FastAPI)
    ↓
┌─────────────┬──────────────┬─────────────┐
│  LangGraph  │   Neo4j      │    E2B      │
│  Agents     │   Graph DB   │  Sandbox    │
└─────────────┴──────────────┴─────────────┘
```

## Next Steps

1. Try the demo to understand the concept
2. Install prerequisites for full version
3. Test with your own repositories
4. Customize fault injection patterns
5. Extend the agent prompts

Enjoy learning codebases with ChronoGraph! 🚀
