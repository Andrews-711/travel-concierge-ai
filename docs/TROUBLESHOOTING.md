# Troubleshooting Guide

Common issues and their solutions.

## Docker Issues

### Services won't start

**Symptom**: `docker-compose up` fails or services exit immediately

**Solutions**:

1. **Check Docker is running**:
   ```powershell
   docker ps
   ```

2. **Check for port conflicts**:
   ```powershell
   netstat -ano | findstr :8080
   netstat -ano | findstr :5432
   netstat -ano | findstr :11434
   ```
   
   If ports are in use, either stop the conflicting service or change ports in `docker-compose.yml`.

3. **Remove old containers/volumes**:
   ```powershell
   docker-compose down -v
   docker-compose up -d
   ```

4. **Check logs**:
   ```powershell
   docker-compose logs backend
   docker-compose logs postgres
   docker-compose logs ollama
   ```

### Out of disk space

**Symptom**: Containers crash with disk space errors

**Solutions**:

1. **Clean up Docker**:
   ```powershell
   docker system prune -a
   docker volume prune
   ```

2. **Check disk space**:
   ```powershell
   Get-PSDrive C
   ```

### Docker Compose file not found

**Symptom**: `docker-compose: command not found` or file errors

**Solutions**:

1. Ensure you're in the project root directory
2. Check Docker Desktop is installed and running
3. Update Docker Desktop to latest version

## Database Issues

### Cannot connect to database

**Symptom**: `Connection refused` or `database does not exist`

**Solutions**:

1. **Check PostgreSQL is running**:
   ```powershell
   docker-compose ps postgres
   ```

2. **Verify connection string in .env**:
   ```env
   DATABASE_URL=postgresql://travel_user:travel_pass@localhost:5432/travel_concierge
   ```
   
   If running backend in Docker, use:
   ```env
   DATABASE_URL=postgresql://travel_user:travel_pass@postgres:5432/travel_concierge
   ```

3. **Initialize database**:
   ```powershell
   cd backend
   python -c "from app.database import init_db; init_db()"
   ```

4. **Reset database** (WARNING: deletes all data):
   ```powershell
   docker-compose down -v
   docker volume rm capestone_postgres_data
   docker-compose up -d postgres
   # Wait 10 seconds, then init_db again
   ```

### Migration errors

**Symptom**: Schema mismatch errors

**Solution**: Since Alembic isn't set up yet, drop and recreate tables:

```powershell
docker exec -it travel_postgres psql -U travel_user -d travel_concierge -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
python -c "from app.database import init_db; init_db()"
```

## LLM / Ollama Issues

### LLM not responding

**Symptom**: Fallback responses or timeouts

**Solutions**:

1. **Check Ollama is running**:
   ```powershell
   docker-compose ps ollama
   curl http://localhost:11434/api/tags
   ```

2. **Check model is downloaded**:
   ```powershell
   docker exec -it travel_ollama ollama list
   ```

3. **Pull model if missing**:
   ```powershell
   docker exec -it travel_ollama ollama pull llama3:8b
   ```

4. **Check Ollama logs**:
   ```powershell
   docker-compose logs ollama
   ```

5. **Try smaller model** (if RAM limited):
   ```powershell
   docker exec -it travel_ollama ollama pull phi3:mini
   ```
   
   Then update `.env`:
   ```env
   LLM_MODEL=phi3:mini
   ```

### LLM generation is very slow

**Causes**:
- Running on CPU (no GPU)
- Large model size
- Insufficient RAM

**Solutions**:

1. **Use smaller model**:
   - phi3:mini (~2GB)
   - mistral:7b (~4GB)
   - llama3:8b (~4.5GB)

2. **Enable GPU** (if you have NVIDIA GPU):
   - Install NVIDIA drivers
   - Install NVIDIA Container Toolkit
   - Ensure docker-compose.yml has GPU config (already included)

3. **Adjust token limits** in agent code:
   - Reduce `max_tokens` parameter
   - Use temperature=0 for faster but less creative responses

### Model download fails

**Symptom**: Download interrupted or errors

**Solutions**:

1. **Check internet connection**
2. **Retry download**:
   ```powershell
   docker exec -it travel_ollama ollama pull llama3:8b
   ```
3. **Try different model**
4. **Download directly** from Ollama library

## Vector Store (Chroma) Issues

### Chroma not accessible

**Symptom**: Cannot connect to Chroma

**Solutions**:

1. **Check Chroma is running**:
   ```powershell
   docker-compose ps chroma
   curl http://localhost:8000/api/v1/heartbeat
   ```

2. **Check logs**:
   ```powershell
   docker-compose logs chroma
   ```

3. **Restart Chroma**:
   ```powershell
   docker-compose restart chroma
   ```

### Embedding errors

**Symptom**: Errors during document ingestion

**Solutions**:

1. Check model is downloaded (happens automatically on first use)
2. Ensure sufficient disk space
3. Check backend logs for specific errors

### Search returns no results

**Causes**:
- No documents uploaded
- Collection not created
- Query embedding failed

**Solutions**:

1. **Upload a test document** via API
2. **Check collections**:
   ```powershell
   curl http://localhost:8000/api/v1/collections
   ```

## API / Backend Issues

### API not responding

**Symptom**: `Connection refused` on port 8080

**Solutions**:

1. **Check backend is running**:
   ```powershell
   # If using Docker
   docker-compose ps backend
   docker-compose logs backend
   
   # If running locally
   # Check terminal where uvicorn is running
   ```

2. **Check port availability**:
   ```powershell
   netstat -ano | findstr :8080
   ```

3. **Restart backend**:
   ```powershell
   # Docker
   docker-compose restart backend
   
   # Local
   # Ctrl+C and re-run uvicorn command
   ```

### Authentication errors

**Symptom**: 401 Unauthorized

**Solutions**:

1. **Token expired**: Login again to get new token
2. **Invalid token**: Check Authorization header format: `Bearer YOUR_TOKEN`
3. **Wrong SECRET_KEY**: Ensure .env SECRET_KEY matches what was used to create token

### Validation errors

**Symptom**: 422 Unprocessable Entity

**Cause**: Invalid request data

**Solution**: Check API docs at http://localhost:8080/docs for required fields and formats

### 500 Internal Server Error

**Solutions**:

1. **Check backend logs**:
   ```powershell
   docker-compose logs -f backend
   ```

2. **Common causes**:
   - Database connection lost
   - LLM server down
   - Chroma unavailable
   - Disk space full

## Python / Development Issues

### Virtual environment issues

**Symptom**: Cannot activate venv or import errors

**Solutions**:

1. **Recreate venv**:
   ```powershell
   Remove-Item -Recurse -Force .\venv
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. **Check Python version**:
   ```powershell
   python --version  # Should be 3.11+
   ```

### Import errors

**Symptom**: `ModuleNotFoundError`

**Solutions**:

1. **Ensure venv is activated**: Look for `(venv)` in terminal prompt
2. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```
3. **Check working directory**: Should be in `backend/` folder

### Package installation fails

**Solutions**:

1. **Update pip**:
   ```powershell
   pip install --upgrade pip
   ```

2. **Use alternative mirrors** (if behind firewall):
   ```powershell
   pip install -r requirements.txt -i https://pypi.org/simple
   ```

3. **Install system dependencies** (for psycopg2):
   - Already using `psycopg2-binary` which should work

## Performance Issues

### Slow API responses

**Causes**:
- LLM generation (expected)
- Database queries
- External API calls
- Network latency

**Solutions**:

1. **Use caching**: Most tools have caching built-in
2. **Optimize database queries**: Add indexes
3. **Use smaller LLM model**
4. **Enable GPU acceleration**

### High memory usage

**Causes**:
- LLM model loaded in memory (~4-8GB)
- Multiple Docker containers
- Large documents in vector store

**Solutions**:

1. **Close other applications**
2. **Use smaller LLM model**
3. **Limit concurrent requests**
4. **Add more RAM**

### High CPU usage

**Normal** during:
- LLM generation (CPU inference)
- Document processing
- Embedding generation

**If excessive**:
- Check for infinite loops in logs
- Reduce concurrency
- Use GPU for LLM

## File Upload Issues

### File upload fails

**Symptom**: 400 or 500 errors when uploading documents

**Solutions**:

1. **Check file size**: Max 10MB by default (change `MAX_UPLOAD_SIZE_MB` in .env)
2. **Check file type**: Only PDF, HTML, DOCX supported
3. **Check disk space**
4. **Check upload directory exists**:
   ```powershell
   mkdir -Force backend\data\uploads
   ```

### Document processing stuck

**Symptom**: Document status stays "processing"

**Solutions**:

1. **Check backend logs** for errors
2. **Verify Chroma is accessible**
3. **Try smaller document**
4. **Check embedding model is downloaded**

## Monitoring Issues

### Prometheus not collecting metrics

**Solutions**:

1. **Check Prometheus is running**:
   ```powershell
   docker-compose ps prometheus
   ```

2. **Verify Prometheus config**: `infra/prometheus.yml` should have backend target

3. **Access Prometheus UI**: http://localhost:9090/targets

### Grafana not showing data

**Solutions**:

1. **Add Prometheus data source** in Grafana:
   - URL: `http://prometheus:9090`
   - Access: Server

2. **Create dashboard** with metrics:
   - `http_requests_total`
   - `http_request_duration_seconds`

## Getting More Help

### Enable debug logging

In `.env`:
```env
LOG_LEVEL=DEBUG
LOG_FORMAT=json
```

Restart services to apply.

### Check system health

```powershell
# Run test script
.\test.ps1

# Check all services
docker-compose ps

# Check resource usage
docker stats
```

### Collect diagnostics

```powershell
# Service status
docker-compose ps > diagnostics.txt

# Logs
docker-compose logs --tail=100 >> diagnostics.txt

# System info
docker version >> diagnostics.txt
docker-compose version >> diagnostics.txt
```

### Reset everything

**WARNING**: Deletes all data

```powershell
docker-compose down -v
Remove-Item -Recurse -Force backend\data
Remove-Item -Recurse -Force backend\venv
Remove-Item .env

# Start fresh
Copy-Item .env.example .env
# Edit .env with your settings
docker-compose up -d
```

## Still Having Issues?

1. **Read the logs carefully**: They often contain the exact error
2. **Check the documentation**: README.md, ARCHITECTURE.md, DEVELOPER_GUIDE.md
3. **Search GitHub Issues**: Someone may have had the same problem
4. **Ask for help**: Create a GitHub issue with:
   - Detailed description
   - Steps to reproduce
   - Logs
   - System information

---

**Remember**: Most issues can be resolved by checking logs and ensuring all services are running properly!
