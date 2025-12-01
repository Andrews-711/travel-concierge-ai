# Developer Setup Guide

## Prerequisites

Before starting, ensure you have:

- **Windows 10/11** (or Linux/macOS)
- **Docker Desktop** (version 20.10+)
- **Python 3.11+**
- **Git**
- **VS Code** (recommended) or any code editor
- At least **8GB RAM** (16GB recommended)
- **10GB free disk space**

## Step-by-Step Setup

### 1. Install Docker Desktop

1. Download from https://www.docker.com/products/docker-desktop
2. Install and start Docker Desktop
3. Verify installation:
   ```powershell
   docker --version
   docker-compose --version
   ```

### 2. Clone or Navigate to Project

```powershell
cd "C:\Program Files\projectcode\capestone"
```

### 3. Create Environment File

```powershell
Copy-Item .env.example .env
```

Edit `.env` with your preferred editor:

```env
# Minimal required configuration
SECRET_KEY=your-super-secret-jwt-key-change-this
DATABASE_URL=postgresql://travel_user:travel_pass@postgres:5432/travel_concierge
```

**Important**: Generate a secure `SECRET_KEY`:
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Start Infrastructure Services

Start database, vector store, and LLM server:

```powershell
docker-compose up -d postgres redis chroma ollama
```

Wait for services to be ready (30-60 seconds):

```powershell
docker-compose ps
```

All services should show `Up` status.

### 5. Pull LLM Model

```powershell
docker exec -it travel_ollama ollama pull llama3:8b
```

This downloads ~4.5GB. Alternative smaller models:
```powershell
# Smaller, faster (good for testing)
docker exec -it travel_ollama ollama pull phi3:mini

# Or Mistral
docker exec -it travel_ollama ollama pull mistral:7b
```

### 6. Set Up Python Environment

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

### 7. Initialize Database

```powershell
# From backend directory with venv activated
python -c "from app.database import init_db; init_db()"
```

This creates all necessary tables.

### 8. Run Backend (Development Mode)

```powershell
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8080
INFO:     Application startup complete.
```

### 9. Verify Installation

Open a new terminal and test:

```powershell
# Health check
curl http://localhost:8080/health

# API docs
# Open browser: http://localhost:8080/docs
```

### 10. Create Test User

Using the Swagger UI (http://localhost:8080/docs):

1. Navigate to `POST /auth/register`
2. Click "Try it out"
3. Enter:
   ```json
   {
     "email": "test@example.com",
     "password": "TestPass123!",
     "full_name": "Test User"
   }
   ```
4. Click "Execute"

Then login at `POST /auth/login` to get an access token.

## Running with Docker Compose (Alternative)

Instead of running backend locally, run everything in Docker:

```powershell
docker-compose up -d
```

This starts all services including the backend. Access at http://localhost:8080

To view logs:
```powershell
docker-compose logs -f backend
```

## Common Development Tasks

### Restart Backend

```powershell
# If running locally
# Press Ctrl+C in terminal, then re-run:
uvicorn app.main:app --reload

# If running in Docker
docker-compose restart backend
```

### View Logs

```powershell
# Local development - logs print to console

# Docker
docker-compose logs -f backend
docker-compose logs -f ollama
docker-compose logs -f chroma
```

### Database Migrations

For schema changes:

1. Modify models in `backend/app/models/`
2. Create Alembic migration:
   ```powershell
   alembic revision --autogenerate -m "description"
   ```
3. Apply migration:
   ```powershell
   alembic upgrade head
   ```

(Note: Alembic setup not included in Phase 1, but recommended for production)

### Reset Database

```powershell
# Stop services
docker-compose down

# Remove volumes (WARNING: deletes all data)
docker volume rm capestone_postgres_data capestone_chroma_data

# Restart
docker-compose up -d
```

### Add Python Dependencies

```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Install new package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt

# Rebuild Docker image if needed
docker-compose build backend
```

## IDE Setup (VS Code)

### Recommended Extensions

- Python (Microsoft)
- Docker (Microsoft)
- REST Client (Huachao Mao)
- GitLens

### VS Code Settings

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "./backend/venv/Scripts/python.exe",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true
}
```

### Launch Configuration

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "8080"
      ],
      "jinja": true,
      "cwd": "${workspaceFolder}/backend"
    }
  ]
}
```

## Debugging

### Enable Debug Logging

In `.env`:
```env
LOG_LEVEL=DEBUG
```

### Debug LLM Issues

```powershell
# Check Ollama is running
curl http://localhost:11434/api/tags

# Check available models
docker exec -it travel_ollama ollama list

# Test generation
curl http://localhost:11434/api/generate -d '{
  "model": "llama3:8b",
  "prompt": "Say hello",
  "stream": false
}'
```

### Debug Vector Store

```powershell
# Check Chroma
curl http://localhost:8000/api/v1/heartbeat

# List collections
curl http://localhost:8000/api/v1/collections
```

### Debug Database

```powershell
# Connect to PostgreSQL
docker exec -it travel_postgres psql -U travel_user -d travel_concierge

# List tables
\dt

# Query users
SELECT * FROM users;

# Exit
\q
```

## Testing

### Manual API Testing

Use Swagger UI: http://localhost:8080/docs

Or use curl/Postman/Insomnia.

### Automated Tests (Future)

```powershell
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# With coverage
pytest --cov=app
```

## Troubleshooting

### Port Already in Use

```powershell
# Find process using port 8080
netstat -ano | findstr :8080

# Kill process (replace PID)
taskkill /PID <pid> /F
```

### Docker Container Won't Start

```powershell
# View container logs
docker-compose logs backend

# Remove and recreate
docker-compose down
docker-compose up -d --force-recreate
```

### Python Import Errors

```powershell
# Ensure you're in the right directory
cd backend

# Ensure venv is activated
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

### LLM Generation Slow

- Use smaller model (phi3:mini)
- Enable GPU acceleration (requires NVIDIA GPU + CUDA)
- Reduce `max_tokens` in LLM calls

## Performance Tips

### Development
- Use smaller LLM model for faster iteration
- Disable unnecessary services during development
- Use mock data tools instead of real APIs

### Production Preparation
- Use production-grade LLM server (vLLM, TGI)
- Enable database connection pooling
- Configure Redis for caching
- Set up reverse proxy (Nginx)
- Enable HTTPS

## Next Steps

1. **Explore the API**: http://localhost:8080/docs
2. **Read Architecture**: See `docs/ARCHITECTURE.md`
3. **Try Examples**: See `docs/API_EXAMPLES.md`
4. **Extend the System**: Add new tools or agents
5. **Build Frontend**: Phase 2 - React application

## Getting Help

- Check logs: `docker-compose logs -f`
- Review documentation in `/docs`
- Examine code comments
- Test with Swagger UI

Happy coding! 🚀
