# Multi-stage build for production deployment
FROM node:18-alpine as frontend-builder

WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Backend with frontend serving
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY backend_v2/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend_v2/app ./app

# Copy built frontend
COPY --from=frontend-builder /frontend/dist ./static

# Expose port
EXPOSE 8001

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
