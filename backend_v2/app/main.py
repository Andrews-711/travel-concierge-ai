"""
Lightweight Travel Concierge API
Stateless, no database, real-time information
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uuid
import traceback
import logging

from app.config import get_settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from app.schemas import (
    ChatRequest, ChatResponse,
    TripPlanRequest, TripPlanResponse,
    DocumentUploadResponse
)
from app.agents.planner import planner_agent
from app.agents.chat import chat_agent
from app.document_processor import process_document
from app.rag_minimal import rag  # Using minimal RAG (no ChromaDB)
from app.llm import llm
from app.observability import logger, metrics, tracer, measure_performance, trace_operation

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Real-time travel planning with multi-agent AI"
)

# CORS middleware - allow all origins (no authentication)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "✈️ Travel Concierge API",
        "version": settings.VERSION,
        "status": "running",
        "llm": "Gemini" if llm.use_gemini else "Ollama",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        llm_status = await llm.is_healthy()
        return {
            "status": "healthy",
            "version": settings.VERSION,
            "llm_provider": "Gemini" if llm.use_gemini else "Ollama",
            "llm_connected": llm_status
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return {
            "status": "degraded",
            "error": str(e)
        }


@app.get("/metrics")
async def get_metrics():
    """Get application metrics"""
    return metrics.get_metrics()


@app.get("/metrics/summary")
async def get_metrics_summary():
    """Get metrics summary"""
    return metrics.get_summary()


@app.get("/traces")
async def get_active_traces():
    """Get active request traces"""
    return tracer.get_active_traces()


@app.post("/chat", response_model=ChatResponse)
@measure_performance("chat")
@trace_operation("chat_request")
async def chat(request: ChatRequest):
    """
    Send a message and get AI response
    Uses RAG + web search + LLM
    """
    try:
        logger.info(
            "Chat request received",
            message_preview=request.message[:50],
            session_id=request.session_id
        )
        
        response = await chat_agent.process_message(
            message=request.message,
            session_id=request.session_id
        )
        
        logger.info(
            "Chat response generated",
            session_id=response.session_id,
            tools_used=response.tool_calls
        )
        
        return response
    except Exception as e:
        logger.error(
            "Chat processing failed",
            error=str(e),
            error_type=type(e).__name__
        )
        metrics.record_error(type(e).__name__, "chat")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@app.post("/plan", response_model=TripPlanResponse)
@measure_performance("plan")
@trace_operation("trip_planning")
async def plan_trip(request: TripPlanRequest):
    """
    Plan a trip with 3 budget options
    Uses web search for real-time information
    """
    try:
        logger.info(
            "Trip planning started",
            destination=request.destination,
            duration=request.duration_days,
            budget=request.budget,
            interests=request.interests
        )
        
        plan = await planner_agent.plan_trip(request)
        
        logger.info(
            "Trip plan generated",
            destination=plan.destination,
            options_count=len(plan.options),
            total_days=plan.duration
        )
        
        return plan
    except Exception as e:
        logger.error(
            "Trip planning failed",
            destination=request.destination,
            error=str(e),
            error_type=type(e).__name__
        )
        metrics.record_error(type(e).__name__, "plan")
        raise HTTPException(status_code=500, detail=f"Planning error: {str(e)}")


@app.post("/upload", response_model=DocumentUploadResponse)
@measure_performance("upload")
@trace_operation("document_upload")
async def upload_document(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(None)
):
    """
    Upload a travel document for RAG
    Supports PDF, DOCX, TXT
    """
    try:
        logger.info(
            "Document upload started",
            filename=file.filename,
            session_id=session_id
        )
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Check file extension
        filename = file.filename
        ext = filename.lower().split('.')[-1]
        
        if ext not in ['pdf', 'docx', 'txt']:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {ext}. Supported: PDF, DOCX, TXT"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Check file size
        size_mb = len(file_content) / (1024 * 1024)
        if size_mb > settings.MAX_UPLOAD_SIZE_MB:
            raise HTTPException(
                status_code=400,
                detail=f"File too large: {size_mb:.2f}MB. Max: {settings.MAX_UPLOAD_SIZE_MB}MB"
            )
        
        # Process document
        doc_data = process_document(filename, file_content)
        
        # Add to RAG
        chunks_added = rag.add_documents(
            session_id=session_id,
            texts=doc_data['chunks'],
            metadatas=doc_data['metadatas']
        )
        
        return DocumentUploadResponse(
            filename=filename,
            pages=len(doc_data['chunks']) // 2,  # Estimate
            chunks=chunks_added,
            status="success",
            message=f"Document processed successfully. Session ID: {session_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


@app.get("/session/{session_id}")
async def get_session_info(session_id: str):
    """Get information about a session's documents"""
    info = rag.get_session_info(session_id)
    return {
        "session_id": session_id,
        **info
    }


@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear all documents for a session"""
    rag.clear_session(session_id)
    return {
        "session_id": session_id,
        "status": "cleared"
    }


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Travel Concierge API",
        "version": settings.VERSION,
        "docs": "/docs",
        "endpoints": {
            "health": "GET /health",
            "chat": "POST /chat",
            "plan": "POST /plan",
            "upload": "POST /upload",
            "session_info": "GET /session/{session_id}",
            "clear_session": "DELETE /session/{session_id}"
        }
    }
