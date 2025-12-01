# Multi-Agent Travel Concierge — Open-Source Edition

A production-ready travel planning & chat assistant web application powered by AI agents, RAG (Retrieval-Augmented Generation), and real-time data sources.

## 🌟 Features

- **Intelligent Trip Planning**: Generate customized itineraries with 3 budget options (budget, balanced, splurge)
- **AI Chat Assistant**: Conversational interface with context-aware responses
- **Document Upload & RAG**: Upload travel documents (PDFs, HTML) for personalized recommendations
- **Real-time Data**: Integration with weather, flights, hotels, and local information APIs
- **User Management**: JWT-based authentication and personalized travel history
- **Observability**: Structured logging, Prometheus metrics, and monitoring
- **Fully Self-Hosted**: No proprietary SaaS dependencies

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌────────────────────┐
│ FastAPI Backend │────▶│ Agent Orchestr.  │────▶│ LLM Server (Ollama)│
│   (REST API)    │     │ (Planner + Chat) │     │  (Llama3 / Mistral)│
└─────────────────┘     └──────────────────┘     └────────────────────┘
         │                       │                          │
         │                       ▼                          ▼
         │              ┌──────────────────┐      ┌────────────────┐
         │              │  RAG / Retrieval │◀────▶│  Vector DB     │
         │              │   (Embeddings)   │      │  (Chroma/FAISS)│
         │              └──────────────────┘      └────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌──────────────────┐
│   PostgreSQL    │     │ External APIs    │
│   (User Data)   │     │ Weather, Hotels  │
└─────────────────┘     │ Flights, Maps    │
                        └──────────────────┘
```

## 📋 Prerequisites

- **Docker** & **Docker Compose** (v2.0+)
- **Python 3.11+** (for local development)
- At least 8GB RAM (16GB recommended for LLM)
- GPU (optional but recommended for faster LLM inference)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
cd "C:\Program Files\projectcode\capestone"
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and configure:
- Database credentials
- JWT secret key
- API keys for external services (optional for mock data)

### 3. Start Services with Docker Compose

```bash
docker-compose up -d
```

This starts:
- PostgreSQL (port 5432)
- Redis (port 6379)
- Chroma Vector DB (port 8000)
- Ollama LLM Server (port 11434)
- FastAPI Backend (port 8080)
- Prometheus (port 9090)
- Grafana (port 3000)

### 4. Pull LLM Model

```bash
docker exec -it travel_ollama ollama pull llama3:8b
```

**Alternative models:**
```bash
ollama pull mistral:7b
ollama pull phi3:mini
```

### 5. Access the API

- **API Documentation**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/health
- **Metrics**: http://localhost:8080/metrics
- **Grafana Dashboard**: http://localhost:3000 (admin/admin)

## 📖 API Usage Examples

### Register a New User

```bash
curl -X POST "http://localhost:8080/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "full_name": "John Doe"
  }'
```

### Login

```bash
curl -X POST "http://localhost:8080/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

Response includes `access_token` - use this in subsequent requests.

### Plan a Trip

```bash
curl -X POST "http://localhost:8080/itinerary/plan" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "destination": "Tokyo",
    "duration_days": 5,
    "budget": 50000,
    "currency": "INR",
    "dietary_preferences": ["vegetarian"],
    "interests": ["museums", "markets", "temples"]
  }'
```

Returns 3 itinerary options with day-by-day plans, costs, and recommendations.

### Chat with Assistant

```bash
curl -X POST "http://localhost:8080/chat/message" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "message": "What is the best way to travel inside Tokyo?"
  }'
```

### Upload Travel Document

```bash
curl -X POST "http://localhost:8080/documents/upload" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@visa_guidelines.pdf"
```

## 🛠️ Local Development (Without Docker)

### 1. Install Dependencies

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Start External Services

```bash
docker-compose up postgres redis chroma ollama -d
```

### 3. Run Backend

```powershell
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

## 📂 Project Structure

```
travel-concierge/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI entry point
│   │   ├── config.py               # Configuration & settings
│   │   ├── database.py             # Database connection
│   │   ├── auth.py                 # JWT authentication
│   │   ├── logging_config.py       # Structured logging
│   │   ├── api/                    # API route handlers
│   │   │   ├── auth.py
│   │   │   ├── itinerary.py
│   │   │   ├── chat.py
│   │   │   └── documents.py
│   │   ├── agents/                 # AI agent logic
│   │   │   ├── llm_client.py
│   │   │   ├── planner.py
│   │   │   └── chat_agent.py
│   │   ├── rag/                    # RAG pipeline
│   │   │   ├── vector_store.py
│   │   │   ├── ingestion.py
│   │   │   └── retriever.py
│   │   ├── tools/                  # External API wrappers
│   │   │   ├── weather.py
│   │   │   ├── flights.py
│   │   │   ├── hotels.py
│   │   │   └── local_info.py
│   │   ├── models/                 # Database models
│   │   └── schemas/                # Pydantic schemas
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://travel_user:travel_pass@localhost:5432/travel_concierge` |
| `SECRET_KEY` | JWT secret key | Required |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` |
| `LLM_MODEL` | LLM model to use | `llama3:8b` |
| `CHROMA_HOST` | Chroma vector DB host | `localhost` |
| `OPENWEATHER_API_KEY` | Weather API key (optional) | Mock data if not provided |

### External APIs (Optional)

The application works with mock data by default. For real data, configure:

- **OpenWeather API**: https://openweathermap.org/api
- **Flight APIs**: Amadeus, Skyscanner (requires integration)
- **Hotel APIs**: Booking.com, Hotels.com (requires integration)

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

## 📊 Monitoring

### Prometheus Metrics

Access metrics at http://localhost:9090

Key metrics:
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency

### Grafana Dashboards

1. Access Grafana: http://localhost:3000
2. Login: admin/admin
3. Add Prometheus data source: http://prometheus:9090
4. Import dashboard or create custom

### Structured Logs

Logs are output in JSON format for easy parsing:

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "message": "Trip planned successfully",
  "request_id": "abc-123",
  "user_id": "user-456"
}
```

## 🔒 Security

- **JWT Authentication**: Secure token-based auth
- **Password Hashing**: Bcrypt with salt
- **Rate Limiting**: Configured per user
- **Input Validation**: Pydantic models
- **CORS**: Configurable origins

## 🚢 Deployment

### Docker Production Deployment

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Kubernetes (Future)

Kubernetes manifests will be added in `infra/k8s/`

## 📝 API Documentation

Full API documentation available at: http://localhost:8080/docs

Interactive OpenAPI (Swagger) interface with:
- All endpoints documented
- Request/response schemas
- Try-it-out functionality

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file

## 🔮 Future Enhancements (Phase 2+)

- **React Frontend**: User-friendly web interface
- **Real-time Updates**: WebSocket support for live updates
- **Multi-language**: i18n support
- **Advanced RAG**: Better chunking strategies, hybrid search
- **More Integrations**: Additional travel APIs
- **Mobile App**: React Native or Flutter
- **Payment Integration**: Booking capabilities
- **Social Features**: Share itineraries, reviews

## 📞 Support

For issues or questions:
- GitHub Issues: [Project Issues](https://github.com/your-repo/issues)
- Documentation: See `/docs` folder

## 🙏 Acknowledgments

Built with:
- FastAPI
- Ollama
- ChromaDB
- LangChain
- Sentence Transformers

---

**Note**: This is a Phase 1 implementation focused on backend, agents, and data pipeline. Frontend (React) will be Phase 2.
