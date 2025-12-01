# 🌍 Travel Concierge V2 - Lightweight & Stateless

**Real-time AI travel planning powered by multi-agent workflow, RAG, and web search**

## ✨ Features

- **💬 Conversational AI Assistant** - Ask travel questions, get instant answers
- **🗺️ Trip Planning** - Generate 3 budget-optimized itineraries (budget, balanced, luxury)
- **📄 Document Intelligence** - Upload travel docs (PDF/DOCX) for personalized advice
- **🔍 Real-Time Web Search** - Live weather, hotels, attractions, restaurants
- **🚀 Zero Setup** - No databases, no authentication, fully stateless
- **🔓 Open Source** - Self-hosted LLM (Ollama), no API keys required

## 🏗️ Architecture

```
User → React Frontend → FastAPI → Multi-Agent System
                                   ├── Planner Agent (trip planning)
                                   ├── Chat Agent (conversations)
                                   ├── RAG System (in-memory ChromaDB)
                                   ├── Web Search (DuckDuckGo)
                                   └── LLM (Ollama/Llama3)
```

**Completely stateless:**
- ✅ No PostgreSQL
- ✅ No Redis
- ✅ No persistent storage
- ✅ Session-based RAG only
- ✅ In-memory conversation history

## 🚀 Quick Start

### Prerequisites

- Docker Desktop (with WSL 2 on Windows)
- 8GB+ RAM
- 10GB+ disk space

### 1. Start Services

```powershell
# Copy environment file
Copy-Item backend_v2\.env.example backend_v2\.env

# Start Ollama + Backend
docker-compose -f docker-compose-v2.yml up -d

# Pull LLM model (first time only, ~4GB download)
docker exec -it travel_ollama ollama pull llama3:8b
```

### 2. Test the API

```powershell
# Health check
curl http://localhost:8080/health

# Chat
curl -X POST http://localhost:8080/chat `
  -H "Content-Type: application/json" `
  -d '{"message": "What are the best places to visit in Paris?"}'

# Plan a trip
curl -X POST http://localhost:8080/plan `
  -H "Content-Type: application/json" `
  -d '{
    "destination": "Tokyo",
    "duration_days": 5,
    "budget": 50000,
    "currency": "INR",
    "interests": ["temples", "food", "shopping"]
  }'
```

### 3. Access the API

- **API Docs**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/health

## 📡 API Endpoints

### Chat
**POST /chat**
```json
{
  "message": "What's the weather like in London?",
  "session_id": "optional-session-id"
}
```

Returns: AI response with sources and tool calls

### Trip Planning
**POST /plan**
```json
{
  "destination": "Barcelona",
  "duration_days": 4,
  "budget": 2000,
  "currency": "USD",
  "interests": ["museums", "beaches"],
  "dietary_preferences": ["vegetarian"]
}
```

Returns: 3 detailed itineraries with day-by-day plans

### Document Upload
**POST /upload**
```bash
curl -X POST http://localhost:8080/upload \
  -F "file=@travel_visa.pdf" \
  -F "session_id=my-session"
```

Returns: Document processed, added to session's RAG

### Session Management
- **GET /session/{session_id}** - Get session info
- **DELETE /session/{session_id}** - Clear session documents

## 🧠 How It Works

### 1. Trip Planning Flow
```
User Request → Planner Agent
  ↓
  ├── Web Search (weather, hotels, attractions, restaurants)
  ├── Context Building
  └── LLM generates 3 itineraries (budget, balanced, luxury)
  ↓
Response (3 detailed itineraries)
```

### 2. Chat Flow
```
User Message → Chat Agent
  ↓
  ├── Intent Analysis
  ├── RAG Search (if relevant documents exist)
  ├── Web Search (if real-time data needed)
  └── LLM generates contextual response
  ↓
Response (answer + sources + tool calls)
```

### 3. Document Processing (RAG)
```
PDF/DOCX Upload
  ↓
  ├── Text Extraction (PyPDF2/python-docx)
  ├── Text Chunking (1000 chars, 200 overlap)
  ├── Embedding Generation (Sentence Transformers)
  └── Store in ChromaDB (in-memory, session-scoped)
  ↓
Available for chat queries
```

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | FastAPI (Python 3.11+) |
| **LLM** | Ollama (Llama 3, Mistral, Phi3) |
| **Embeddings** | Sentence Transformers |
| **Vector Store** | ChromaDB (in-memory) |
| **Web Search** | DuckDuckGo (no API key) |
| **Doc Processing** | PyPDF2, python-docx |
| **Container** | Docker Compose |

## 📁 Project Structure

```
capestone/
├── backend_v2/
│   ├── app/
│   │   ├── main.py            # FastAPI app
│   │   ├── config.py          # Settings
│   │   ├── schemas.py         # Pydantic models
│   │   ├── llm.py             # Ollama client
│   │   ├── rag.py             # In-memory vector store
│   │   ├── web_search.py      # DuckDuckGo search
│   │   ├── document_processor.py  # PDF/DOCX extraction
│   │   └── agents/
│   │       ├── planner.py     # Trip planner agent
│   │       └── chat.py        # Conversation agent
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── docker-compose-v2.yml
└── README-V2.md (this file)
```

## 🎯 Use Cases

1. **Trip Planning**
   - "Plan a 7-day trip to Japan with $3000 budget"
   - Get 3 detailed itineraries with activities, meals, costs

2. **Travel Research**
   - "What's the best time to visit Iceland?"
   - "Top vegetarian restaurants in Rome"
   - Real-time web search provides current information

3. **Document-Based Q&A**
   - Upload visa requirements PDF
   - Ask "What documents do I need for a tourist visa?"
   - RAG retrieves relevant info from your document

4. **Real-Time Information**
   - "Current weather in Paris"
   - "Best hotels in Bangkok under $100/night"
   - Live data from web search

## 🔧 Configuration

Edit `backend_v2/.env`:

```env
# LLM Model (choose one)
OLLAMA_MODEL=llama3:8b        # Recommended (fastest)
# OLLAMA_MODEL=mistral:latest  # Alternative
# OLLAMA_MODEL=phi3:latest     # Smaller, faster

# Upload Limits
MAX_UPLOAD_SIZE_MB=10

# Search Settings
MAX_SEARCH_RESULTS=5
```

## 📊 Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Chat (simple) | <2s | Without web search/RAG |
| Chat (with search) | 3-5s | Includes web search |
| Trip planning | 10-20s | Multiple web searches + LLM |
| Document upload | 2-5s | PDF extraction + embedding |

## 🐛 Troubleshooting

### Ollama not starting
```powershell
# Check logs
docker logs travel_ollama

# Restart
docker restart travel_ollama
```

### Model not found
```powershell
# Pull model manually
docker exec -it travel_ollama ollama pull llama3:8b
```

### Backend errors
```powershell
# Check backend logs
docker logs travel_backend

# Restart
docker restart travel_backend
```

### Web search not working
- DuckDuckGo might rate-limit
- Wait a few minutes and try again
- Or use a VPN

## 🚦 Next Steps

1. **Run the backend** - Follow Quick Start
2. **Test with curl** - Try the API endpoints
3. **Build frontend** - React chat UI (coming next)
4. **Customize agents** - Add your own tools/logic

## 📝 Notes

- **Stateless design** - No data persists between restarts
- **Session-based RAG** - Documents only available within session
- **No authentication** - Open API (add auth for production)
- **Free web search** - DuckDuckGo (no API keys)
- **Self-hosted LLM** - Complete privacy, no external API calls

## 🎉 What's Different from V1?

| Feature | V1 | V2 |
|---------|----|----|
| **Database** | PostgreSQL + Redis | None (stateless) |
| **Authentication** | JWT, users, passwords | None |
| **Monitoring** | Prometheus + Grafana | None |
| **Persistence** | Full database storage | Session-only (in-memory) |
| **Complexity** | 40+ files | 15 files |
| **Setup Time** | 10-15 minutes | 3-5 minutes |
| **Use Case** | Production multi-user app | Demo/prototype/local use |

**V2 is perfect for:**
- ✅ Rapid prototyping
- ✅ Local development
- ✅ Demos and presentations
- ✅ Learning AI agents
- ✅ Hackathons

**V1 is better for:**
- Production deployment
- Multi-user applications
- Data persistence requirements
- Advanced monitoring needs

---

**Built with ❤️ using FastAPI, Ollama, and open-source AI tools**
