# ChronoGraph - AI-Powered Code Analysis & Visualization 🚀

Interactive code dependency graph with AI-powered error detection and time-travel debugging.

## Features

- 📊 **Beautiful Dependency Graphs** - Visualize code structure with smooth bezier curves
- 🤖 **AI Error Detection** - Gemini-powered analysis finds bugs and suggests improvements
- ⏱️ **Time-Travel Debugger** - Step through execution flow like a movie
- 💬 **AI Code Tutor** - Chat with AI about your codebase
- 🎨 **Modern UI** - Gradient backgrounds, animated particles, professional design

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Gemini API Key (get free at: https://ai.google.dev/)
- Neo4j (or use Neo4j Aura free tier)

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/chronograph.git
cd chronograph
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

## Deploy to AWS EC2

See [EC2_MANUAL_SETUP.md](EC2_MANUAL_SETUP.md) for detailed instructions.

### Quick EC2 Deployment:

1. Launch Ubuntu 22.04 EC2 instance (t3.medium)
2. Open ports: 22, 3000, 8000, 7474, 7687
3. SSH in and run:

```bash
# Install Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker ubuntu
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone and setup
git clone https://github.com/YOUR_USERNAME/chronograph.git
cd chronograph
nano .env  # Add your GEMINI_API_KEY
nano docker-compose.yml  # Update NEXT_PUBLIC_API_URL with your EC2 IP

# Start
docker-compose up -d --build
```

4. Access: `http://YOUR_EC2_IP:3000`

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
