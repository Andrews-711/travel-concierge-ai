"""
Pydantic schemas for API requests/responses
Stateless - no user IDs, no database references
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ============= Chat Schemas =============

class ChatRequest(BaseModel):
    """User sends a message"""
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None  # Optional session tracking (in-memory only)
    

class ChatResponse(BaseModel):
    """AI response"""
    message: str
    sources: Optional[List[Dict[str, Any]]] = None
    tool_calls: Optional[List[str]] = None
    session_id: str


# ============= Trip Planning Schemas =============

class TripPlanRequest(BaseModel):
    """Request for trip planning"""
    destination: str = Field(..., min_length=2)
    duration_days: int = Field(..., ge=1, le=30)
    budget: float = Field(..., gt=0)
    currency: str = Field(default="USD")
    interests: Optional[List[str]] = Field(default=[])
    dietary_preferences: Optional[List[str]] = Field(default=[])


class DayPlan(BaseModel):
    """Single day itinerary"""
    day: int
    morning: str
    afternoon: str
    evening: str
    meals: Dict[str, str]
    estimated_cost: float


class Itinerary(BaseModel):
    """Complete trip itinerary"""
    title: str
    budget_type: str  # budget, balanced, luxury
    total_cost: float
    currency: str
    days: List[DayPlan]
    accommodation_suggestions: List[str]
    packing_list: List[str]
    tips: List[str]


class TripPlanResponse(BaseModel):
    """Response with 3 itinerary options"""
    destination: str
    duration: int
    options: List[Itinerary]
    weather_info: Optional[Dict[str, Any]] = None
    map_link: str


# ============= Document Upload Schemas =============

class DocumentUploadResponse(BaseModel):
    """Response after document upload"""
    filename: str
    pages: int
    chunks: int
    status: str
    message: str


class DocumentInfo(BaseModel):
    """Info about uploaded document (in-memory)"""
    filename: str
    uploaded_at: str
    chunks: int


# ============= Web Search Schemas =============

class SearchResult(BaseModel):
    """Single search result"""
    title: str
    url: str
    snippet: str


class WebSearchResponse(BaseModel):
    """Web search results"""
    query: str
    results: List[SearchResult]
    source: str  # "duckduckgo", "web"
