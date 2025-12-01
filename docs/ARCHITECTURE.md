# Architecture Overview

## System Components

### 1. API Layer (FastAPI)

**Purpose**: HTTP REST API for client interactions

**Key Components**:
- Authentication endpoints (`/auth/*`)
- Trip planning endpoints (`/itinerary/*`)
- Chat endpoints (`/chat/*`)
- Document management (`/documents/*`)

**Technologies**:
- FastAPI (async web framework)
- Pydantic (data validation)
- JWT (authentication)
- CORS middleware

### 2. Agent Orchestration Layer

**Purpose**: Coordinate AI agents and tools to fulfill user requests

**Key Agents**:

#### PlannerAgent
- Generates trip itineraries
- Calls external data tools (weather, flights, hotels)
- Creates 3 options: budget, balanced, splurge
- Uses LLM for enhanced descriptions

#### ChatAgent
- Conversational interface
- Intent analysis
- RAG retrieval for user documents
- Tool calling based on query type

**Design Pattern**: Each agent is self-contained with its own tool access

### 3. RAG (Retrieval-Augmented Generation) Pipeline

**Purpose**: Enable knowledge retrieval from user-uploaded documents

**Components**:

#### Document Ingestion
1. Upload (PDF, HTML, DOCX)
2. Text extraction (PyPDF2, BeautifulSoup, python-docx)
3. Chunking (1000 chars with 200 char overlap)
4. Embedding generation (Sentence Transformers)
5. Vector storage (Chroma)

#### Retrieval
1. Query embedding
2. Similarity search (cosine)
3. Top-k results
4. Context injection into LLM prompt

**Vector Store**: ChromaDB with persistent storage

### 4. LLM Integration Layer

**Purpose**: Interface with self-hosted LLM server

**Implementation**:
- Ollama REST API client
- Support for multiple models (Llama3, Mistral, Phi3)
- Fallback responses when LLM unavailable
- Token tracking

**Deployment Options**:
- CPU-only (slower)
- GPU-accelerated (recommended)
- Cloud GPU instances

### 5. External Data Tools

**Purpose**: Fetch real-time travel information

**Tools**:

#### WeatherTool
- Current weather
- 5-day forecast
- Caching (6 hours)
- Fallback to mock data

#### FlightTool
- Flight search (mock implementation)
- Integration ready for: Amadeus, Skyscanner APIs

#### HotelTool
- Hotel search by city
- Budget filtering
- Mock data with realistic structure

#### LocalInfoTool
- Attractions
- Restaurants (dietary filtering)
- Transportation info
- Local tips & customs

#### CurrencyTool
- Currency conversion
- Mock rates (integrate live API)

### 6. Data Persistence Layer

**Databases**:

#### PostgreSQL
- User accounts
- Itineraries
- Chat history
- Document metadata
- Usage logs

**Tables**:
- `users`: Authentication & profile
- `documents`: Upload metadata
- `document_chunks`: RAG chunks
- `itineraries`: Trip plans
- `chat_history`: Conversations
- `usage_logs`: API usage tracking

#### ChromaDB (Vector Store)
- Document embeddings
- Semantic search
- User-specific collections

#### Redis (Caching)
- API response caching
- Rate limiting
- Session management

### 7. Observability Stack

**Logging**:
- Structured JSON logs
- Request/response tracking
- Error tracing
- User action audit

**Metrics** (Prometheus):
- Request count by endpoint
- Response time histograms
- Error rates
- Token usage

**Visualization** (Grafana):
- Real-time dashboards
- Alert configuration
- Performance monitoring

## Data Flow Diagrams

### Trip Planning Flow

```
User Request (POST /itinerary/plan)
    ↓
[API Authentication Middleware]
    ↓
[Itinerary Router]
    ↓
[PlannerAgent]
    ├→ [WeatherTool] → Weather API
    ├→ [FlightTool] → Flight API (mock)
    ├→ [HotelTool] → Hotel API (mock)
    ├→ [LocalInfoTool] → Attractions/Restaurants
    └→ [LLM] → Enhanced descriptions
    ↓
[Generate 3 Options]
    ↓
[Save to PostgreSQL]
    ↓
[Return JSON Response]
```

### Chat Flow

```
User Message (POST /chat/message)
    ↓
[API Authentication]
    ↓
[ChatAgent]
    ├→ [Intent Analysis]
    │   └→ Determine: needs_rag, needs_weather, needs_local_info, location
    ├→ [RAG Retrieval] (if needed)
    │   └→ ChromaDB → Top-K relevant documents
    ├→ [Tool Execution] (if needed)
    │   ├→ WeatherTool
    │   └→ LocalInfoTool
    └→ [LLM Generation]
        └→ Prompt = System + Context + History + Query
    ↓
[Compile Response + Sources]
    ↓
[Save to chat_history]
    ↓
[Return ChatResponse]
```

### Document Upload & RAG Ingestion

```
File Upload (POST /documents/upload)
    ↓
[Validate File Type & Size]
    ↓
[Save to Disk]
    ↓
[Create Document Record (status=pending)]
    ↓
[DocumentIngestion.process_document]
    ├→ [Extract Text]
    │   ├─ PDF → PyPDF2
    │   ├─ HTML → BeautifulSoup
    │   └─ DOCX → python-docx
    ├→ [Chunk Text] (1000 chars, 200 overlap)
    ├→ [Generate Embeddings] (Sentence Transformers)
    └→ [Store in ChromaDB]
        └→ Collection: user_{user_id}
    ↓
[Update Document Record (status=completed)]
    ↓
[Return DocumentResponse]
```

## Scalability Considerations

### Current Architecture (Phase 1)
- Single backend instance
- Suitable for 100-1000 users
- LLM server can be scaled independently

### Future Scaling (Phase 2+)
- Multiple backend replicas (load balanced)
- Database read replicas
- Distributed vector store (Weaviate, Pinecone)
- Message queue for async tasks (Celery + RabbitMQ)
- CDN for static assets

## Security Architecture

### Authentication
- JWT tokens (short-lived)
- Password hashing (bcrypt)
- Rate limiting per user

### Data Privacy
- User data isolation (user-specific vector collections)
- Document encryption at rest (future)
- GDPR-compliant data deletion

### API Security
- HTTPS in production
- Input validation (Pydantic)
- SQL injection protection (SQLAlchemy ORM)
- CORS configuration

## Extension Points

### Adding New Tools
1. Create tool class in `app/tools/`
2. Implement async methods
3. Add caching logic
4. Integrate in ChatAgent or PlannerAgent

### Adding New Agents
1. Create agent class in `app/agents/`
2. Inherit base patterns (LLM client, tool access)
3. Define prompts and orchestration logic
4. Create API endpoint in `app/api/`

### Swapping LLM Provider
- Modify `LLMClient` in `app/agents/llm_client.py`
- Support OpenAI, Anthropic, Azure OpenAI, etc.
- Keep interface consistent

### Custom Vector Store
- Implement interface in `app/rag/vector_store.py`
- Options: FAISS, Weaviate, Pinecone, Qdrant
- Maintain collection management methods

## Performance Characteristics

### Latency (Typical)
- Authentication: < 50ms
- Simple query (no LLM): < 200ms
- Chat with LLM: 2-10s (model dependent)
- Trip planning: 5-15s (multiple tool calls + LLM)
- Document upload: 100ms - 2s (file size dependent)
- RAG ingestion: 1-10s (document size dependent)

### Bottlenecks
1. **LLM inference**: Use GPU, smaller models, or caching
2. **Vector search**: Index tuning, dimensionality reduction
3. **External APIs**: Caching, batch requests
4. **Database**: Indexing, connection pooling

## Deployment Architecture

### Development
- Docker Compose on local machine
- Hot reload enabled
- Debug logging

### Production
- Docker Compose or Kubernetes
- Load balancer (Nginx, Traefik)
- Database backups
- Monitoring & alerting
- Secrets management (Vault, K8s Secrets)

### Cloud Options
- **AWS**: ECS, RDS, ElastiCache, S3
- **Azure**: Container Apps, Azure Database, Redis Cache
- **GCP**: Cloud Run, Cloud SQL, Memorystore
- **Self-hosted**: VPS with Docker Compose
