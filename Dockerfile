# Multi-stage build for production deployment
FROM python:3.12-slim as backend

WORKDIR /app

# Install dependencies
COPY backend_v2/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend_v2/app ./app

# Expose port
EXPOSE 8001

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
