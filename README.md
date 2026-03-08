# ChronoGraph - AI-Powered Code Analysis & Visualization

Interactive code dependency graph with AI-powered error detection and time-travel debugging.

## How it works
- Initially user uploads the python file
- AI analysis is performed for detecting errors and suggesting improvements.
- Based on the AI report in the previous step A Graph is created to visualize the code
- Codes Blocks are highlighted based on ai report
- Red -> Error is present ; Yellow -> suggested improvement.
- On Selecting a Block user can ask ai at the Bottom right regarding that particualr section of Code
- "Time Travel Debugger" - Shows the time taken to execute each function and also  flow of the Code

## Current Limitations
- Upload becomes slow if the current demand for the model used in the code is spiked (FREE TIER LIMITATION).
- Sometimes blocks in the graph might not be connected properly if current code's flow is improper



## Features

- **Beautiful Dependency Graphs** - Visualize code structure with smooth bezier curves
- **AI Error Detection** - Gemini-powered analysis finds bugs and suggests improvements
- **Time-Travel Debugger** - Step through execution flow like a movie
- **AI Code Tutor** - Chat with AI about your codebase
- **Modern UI** - Gradient backgrounds, animated particles, professional design

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Gemini API Key (get free at: https://ai.google.dev/)
- Neo4j (or use Neo4j Aura free tier)

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/Harshithreddy-ux/Chronograph.git
cd Chronograph
```

2. Create `.env` file:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=chronograph123
```

3. Start services:
```bash
docker-compose up -d --build
```

4. Access the app:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Neo4j: http://localhost:7474

## Web Service
- Currently the project simply uses an E2C instance to make it accessible over the internet
- It uses Gemini Api for the ai analysis and responses
- 


## Tech Stack

- **Frontend**: Next.js, React, TailwindCSS, React Flow
- **Backend**: FastAPI, Python
- **Database**: Neo4j
- **AI**: Google Gemini Flash
- **Deployment**: Docker, AWS EC2

## Architecture

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Next.js   │─────▶│   FastAPI   │─────▶│   Neo4j     │
│  Frontend   │      │   Backend   │      │  Database   │
└─────────────┘      └─────────────┘      └─────────────┘
                            │
                            ▼
                     ┌─────────────┐
                     │   Gemini    │
                     │     AI      │
                     └─────────────┘
```

## Usage

1. **Upload Code**: Click upload and select Python files
2. **View Graph**: See dependency graph with error highlighting
3. **Chat with AI**: Ask questions about your code
4. **Time Travel**: Use slider to step through execution
5. **Click Functions**: View source code and details

## Cost

### AWS EC2 Deployment
- t3.medium: ~$30/month
- With $100 credit: FREE for 3+ months

### Alternative Free Options
- Railway: $5 credit (1 month free)
- Vercel + Render: FREE forever

## Documentation

- [EC2 Manual Setup](EC2_MANUAL_SETUP.md)
- [AWS Deployment Options](DEPLOY_AWS_SIMPLE.md)
- [Time-Travel Debugger Guide](TIME_TRAVEL_DEBUGGER_EXPLAINED.md)
- [AI Error Detection](AI_ERROR_DETECTION_UPDATE.md)

## License

MIT

## Contributing

Pull requests welcome!

## Support

Open an issue for bugs or feature requests.
