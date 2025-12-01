"""
Real-time web search tool using DuckDuckGo
No API keys required, completely free
"""
import asyncio
from typing import List, Dict, Any
from duckduckgo_search import DDGS
import httpx
from datetime import datetime

from app.schemas import SearchResult


class WebSearchTool:
    """
    Web search for real-time travel information
    Uses DuckDuckGo (no API key needed)
    """
    
    def __init__(self):
        self.ddgs = DDGS()
    
    async def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """
        Search the web for real-time information
        
        Args:
            query: Search query
            max_results: Maximum number of results
        
        Returns:
            List of search results
        """
        try:
            # Run in thread pool since duckduckgo_search is synchronous
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                lambda: list(self.ddgs.text(query, max_results=max_results))
            )
            
            return [
                SearchResult(
                    title=r.get('title', ''),
                    url=r.get('href', ''),
                    snippet=r.get('body', '')
                )
                for r in results
            ]
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    async def search_weather(self, city: str) -> Dict[str, Any]:
        """Search for current weather information"""
        query = f"current weather in {city} today"
        results = await self.search(query, max_results=3)
        
        return {
            'city': city,
            'query': query,
            'results': [r.model_dump() for r in results],
            'timestamp': datetime.now().isoformat()
        }
    
    async def search_hotels(self, city: str, budget: str = "mid-range") -> Dict[str, Any]:
        """Search for hotel recommendations"""
        query = f"best {budget} hotels in {city} 2025"
        results = await self.search(query, max_results=5)
        
        return {
            'city': city,
            'budget': budget,
            'query': query,
            'results': [r.model_dump() for r in results],
            'timestamp': datetime.now().isoformat()
        }
    
    async def search_attractions(self, city: str) -> Dict[str, Any]:
        """Search for top attractions"""
        query = f"top things to do in {city} attractions"
        results = await self.search(query, max_results=5)
        
        return {
            'city': city,
            'query': query,
            'results': [r.model_dump() for r in results],
            'timestamp': datetime.now().isoformat()
        }
    
    async def search_restaurants(self, city: str, cuisine: str = "") -> Dict[str, Any]:
        """Search for restaurant recommendations"""
        cuisine_part = f"{cuisine} " if cuisine else ""
        query = f"best {cuisine_part}restaurants in {city} 2025"
        results = await self.search(query, max_results=5)
        
        return {
            'city': city,
            'cuisine': cuisine,
            'query': query,
            'results': [r.model_dump() for r in results],
            'timestamp': datetime.now().isoformat()
        }
    
    async def search_flights(self, origin: str, destination: str) -> Dict[str, Any]:
        """Search for flight information"""
        query = f"flights from {origin} to {destination} 2025"
        results = await self.search(query, max_results=5)
        
        return {
            'origin': origin,
            'destination': destination,
            'query': query,
            'results': [r.model_dump() for r in results],
            'timestamp': datetime.now().isoformat()
        }
    
    async def search_transportation(self, city: str) -> Dict[str, Any]:
        """Search for local transportation info"""
        query = f"public transportation in {city} metro bus train"
        results = await self.search(query, max_results=3)
        
        return {
            'city': city,
            'query': query,
            'results': [r.model_dump() for r in results],
            'timestamp': datetime.now().isoformat()
        }
    
    async def search_travel_tips(self, destination: str) -> Dict[str, Any]:
        """Search for travel tips and guides"""
        query = f"travel guide tips for visiting {destination} 2025"
        results = await self.search(query, max_results=5)
        
        return {
            'destination': destination,
            'query': query,
            'results': [r.model_dump() for r in results],
            'timestamp': datetime.now().isoformat()
        }


# Global instance
web_search = WebSearchTool()
