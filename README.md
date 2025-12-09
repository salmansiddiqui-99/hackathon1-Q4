# Physical AI & Humanoid Robotics Textbook + RAG Chatbot

A comprehensive, AI-native textbook on Physical AI and Humanoid Robotics with an embedded Retrieval-Augmented Generation (RAG) chatbot.

## Project Overview

This project generates a complete Docusaurus-based textbook covering:

- **Module 1**: ROS 2 - The Robotic Nervous System
- **Module 2**: Gazebo & Unity - The Digital Twin
- **Module 3**: NVIDIA Isaac - The AI-Robot Brain
- **Module 4**: VLA & Capstone - Vision-Language-Action Systems

The textbook is deployed to GitHub Pages and includes an interactive RAG chatbot for Q&A.

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API key
- Qdrant Cloud account (free tier)

### Local Development Setup

1. **Clone and setup environment**:
```bash
git clone https://github.com/yourname/physical_ai_book.git
cd physical_ai_book

# Create .env file
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys
```

2. **Setup backend**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload
```

3. **Setup frontend** (in a new terminal):
```bash
cd textbook
npm install
npm start
```

4. **Access the app**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Project Structure

```
physical_ai_book/
├── textbook/                # Docusaurus frontend
│   ├── docs/               # Book chapters (auto-generated)
│   ├── src/                # React components, themes, CSS
│   └── docusaurus.config.js
├── backend/                # FastAPI server
│   ├── src/
│   │   ├── api/           # API endpoints
│   │   ├── models/        # Pydantic models
│   │   ├── services/      # Business logic
│   │   └── main.py
│   ├── requirements.txt
│   └── .env.example
├── specs/                  # Specification documents
│   └── 001-book-creation/
├── .github/workflows/      # GitHub Actions CI/CD
└── README.md
```

## Features

✨ **Auto-Generated Chapters**: Use Claude Code subagents to generate 12 chapters

📚 **RAG Chatbot**: Ask questions about textbook content with context-only answers

🎨 **Futuristic Theme**: Dark mode with neon-blue and cyber-green accents

📱 **Responsive Design**: Works on desktop, tablet, and mobile

🚀 **GitHub Pages Deployment**: Free static site hosting

## Development Status

### Phase 1: Setup ✅
- [x] Docusaurus scaffolding
- [x] FastAPI backend initialization
- [x] Environment configuration
- [x] Linting setup
- [x] GitHub Actions CI/CD

### Phase 2: Foundation (Next)
- [ ] Database migrations (Postgres/SQLite)
- [ ] Pydantic models
- [ ] API routing
- [ ] Error handling & logging
- [ ] Health check endpoint

### Phase 3: Chapter Generation
- [ ] Claude Code subagent integration
- [ ] Content validation
- [ ] Vector indexing (Qdrant)
- [ ] API endpoints for chapters

### Phase 4: Frontend Theme & Deployment
- [ ] Futuristic theme customization
- [ ] Module cards and navigation
- [ ] Responsive design
- [ ] GitHub Pages deployment

### Phase 5: RAG Chatbot
- [ ] Retrieval service
- [ ] Response generation
- [ ] Chatbot widget
- [ ] Integration testing

## Technology Stack

**Frontend**:
- Docusaurus 3.x
- React 18
- JavaScript/TypeScript
- CSS Modules

**Backend**:
- FastAPI (Python 3.11)
- Pydantic
- SQLAlchemy
- Qdrant SDK
- OpenAI API

**Database**:
- PostgreSQL (Neon Cloud)
- Qdrant Cloud (vector store)
- SQLite (dev)

**Deployment**:
- GitHub Pages (frontend)
- Railway/Render (backend)
- GitHub Actions (CI/CD)

## Getting Help

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Spec Documents**: See `/specs/001-book-creation/`
- **Development Guide**: See `/specs/001-book-creation/quickstart.md`

## Contributing

1. Create a feature branch from `main`
2. Make your changes and test locally
3. Submit a pull request with a description of changes
4. Ensure CI/CD checks pass

## License

CC-BY-4.0 - See LICENSE file for details

## Status

🟡 **Under Development** - Phase 1 complete, Phase 2-5 in progress

Last updated: 2025-12-09

---

**Repository**: https://github.com/yourname/physical_ai_book
**Live Site**: https://yourname.github.io/physical_ai_book
