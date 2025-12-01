"""
Enhanced web search with place extraction
Combines DuckDuckGo search + webpage scraping for actual place data
"""
import asyncio
import re
from typing import List, Dict, Any
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import httpx
from datetime import datetime
import time

from app.schemas import SearchResult


class EnhancedWebSearch:
    """
    Enhanced web search that extracts actual place names
    Uses DuckDuckGo + webpage scraping with rate limiting
    """
    
    def __init__(self):
        self.ddgs = DDGS()
        self.timeout = 10.0
        self.last_request_time = 0
        self.min_request_interval = 5.0  # 5 seconds between requests to avoid rate limit
        self.max_retries = 2
    
    async def _rate_limited_search(self, query: str, max_results: int = 5) -> List[Dict]:
        """Perform rate-limited DuckDuckGo search with retries"""
        # Wait if needed to respect rate limit
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            wait_time = self.min_request_interval - time_since_last
            print(f"Rate limiting: waiting {wait_time:.1f}s...")
            await asyncio.sleep(wait_time)
        
        for attempt in range(self.max_retries):
            try:
                loop = asyncio.get_event_loop()
                results = await loop.run_in_executor(
                    None,
                    lambda: list(self.ddgs.text(query, max_results=max_results))
                )
                self.last_request_time = time.time()
                return results
            except Exception as e:
                print(f"Search attempt {attempt + 1} failed for '{query}': {e}")
                self.last_request_time = time.time()
                if attempt < self.max_retries - 1:
                    # Wait longer between retries
                    await asyncio.sleep(10)
        
        return []
    
    async def search_with_extraction(self, query: str, max_results: int = 3) -> List[Dict[str, str]]:
        """
        Search and extract actual place names from results
        
        Returns:
            List of dicts with 'name', 'description', 'url'
        """
        try:
            # Get search results with rate limiting
            results = await self._rate_limited_search(query, max_results)
            
            if not results:
                return []
            
            places = []
            
            # Try to scrape each result page for place names
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                for result in results[:2]:  # Only scrape top 2 to avoid rate limits
                    url = result.get('href', '')
                    snippet = result.get('body', '')
                    
                    try:
                        # Fetch the page
                        response = await client.get(url, follow_redirects=True)
                        if response.status_code == 200:
                            # Extract places from the page
                            extracted = await self._extract_places_from_html(
                                response.text,
                                url
                            )
                            places.extend(extracted[:5])
                    except Exception as e:
                        # If scraping fails, try to extract from snippet
                        snippet_places = self._extract_from_text(snippet)
                        places.extend(snippet_places[:2])
            
            # Deduplicate
            seen = set()
            unique_places = []
            for place in places:
                name_lower = place['name'].lower()
                if name_lower not in seen and len(place['name']) > 3:
                    seen.add(name_lower)
                    unique_places.append(place)
            
            return unique_places[:15]
            
        except Exception as e:
            print(f"Enhanced search error: {e}")
            return []
    
    async def _extract_places_from_html(self, html: str, url: str) -> List[Dict[str, str]]:
        """Extract place names from HTML content"""
        places = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove scripts and styles
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Strategy 1: Look for heading tags (h2, h3) which often contain place names
            headings = soup.find_all(['h2', 'h3', 'h4'])
            for heading in headings[:20]:
                text = heading.get_text(strip=True)
                # Clean and validate
                text = self._clean_place_name(text)
                if self._is_valid_place_name(text):
                    places.append({
                        'name': text,
                        'description': self._get_next_paragraph(heading),
                        'url': url
                    })
            
            # Strategy 2: Look for list items (often used in "Top 10" articles)
            list_items = soup.find_all('li')
            for item in list_items[:30]:
                text = item.get_text(strip=True)
                # Look for numbered patterns like "1. Place Name"
                match = re.match(r'^\d+[.\)]\s*(.+?)(?:\s*[-–—:]|$)', text)
                if match:
                    place_name = self._clean_place_name(match.group(1))
                    if self._is_valid_place_name(place_name):
                        places.append({
                            'name': place_name,
                            'description': text[:150],
                            'url': url
                        })
            
            # Strategy 3: Look for strong/bold text (place names are often bolded)
            bold_tags = soup.find_all(['strong', 'b'])
            for tag in bold_tags[:20]:
                text = tag.get_text(strip=True)
                text = self._clean_place_name(text)
                if self._is_valid_place_name(text) and len(text) > 5:
                    places.append({
                        'name': text,
                        'description': self._get_next_paragraph(tag),
                        'url': url
                    })
            
        except Exception as e:
            print(f"HTML parsing error: {e}")
        
        return places
    
    def _get_next_paragraph(self, element) -> str:
        """Get the next paragraph after an element"""
        try:
            next_p = element.find_next('p')
            if next_p:
                return next_p.get_text(strip=True)[:150]
        except:
            pass
        return ""
    
    def _clean_place_name(self, text: str) -> str:
        """Clean a place name"""
        # Remove numbers at start
        text = re.sub(r'^\d+[.\)]\s*', '', text)
        # Remove dates like "Dec 1, 2025"
        text = re.sub(r'^[A-Z][a-z]{2}\s+\d+,\s+\d{4}\s*[·•]\s*', '', text)
        # Remove common prefixes
        text = re.sub(r'^(Visit|Explore|See|Try|Check out|The)\s+', '', text, flags=re.IGNORECASE)
        # Remove parenthetical content at end
        text = re.sub(r'\s*\([^)]+\)\s*$', '', text)
        # Remove URLs
        text = re.sub(r'https?://\S+', '', text)
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text.strip()
    
    def _is_valid_place_name(self, text: str) -> bool:
        """Check if text looks like a valid place name"""
        if not text or len(text) < 4 or len(text) > 80:
            return False
        
        # Must start with capital letter
        if not text[0].isupper():
            return False
        
        # Skip if it's too generic
        generic_words = [
            'click here', 'read more', 'see more', 'advertisement',
            'subscribe', 'follow us', 'share', 'comment', 'login',
            'best', 'top', 'things to do', 'guide', 'tips',
            'welcome', 'home', 'about', 'contact', 'privacy'
        ]
        text_lower = text.lower()
        if any(word in text_lower for word in generic_words):
            return False
        
        # Skip if it's all caps (likely a category/header)
        if text.isupper() and len(text) > 10:
            return False
        
        # Must have at least one letter
        if not re.search(r'[a-zA-Z]', text):
            return False
        
        return True
    
    def _extract_from_text(self, text: str) -> List[Dict[str, str]]:
        """Extract place names from plain text"""
        places = []
        
        # Look for numbered patterns
        pattern = r'\d+[.\)]\s+([A-Z][^.!?\n]{5,70}?)(?=\s*[-–—:,]|\n|$)'
        matches = re.findall(pattern, text)
        
        for match in matches:
            cleaned = self._clean_place_name(match)
            if self._is_valid_place_name(cleaned):
                places.append({
                    'name': cleaned,
                    'description': '',
                    'url': ''
                })
        
        # Also look for capitalized phrases (proper nouns)
        proper_nouns = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b', text)
        for noun in proper_nouns[:10]:
            if self._is_valid_place_name(noun):
                places.append({
                    'name': noun,
                    'description': '',
                    'url': ''
                })
        
        return places
    
    async def search_attractions(self, city: str) -> Dict[str, Any]:
        """Search for attractions with place extraction"""
        query = f"top attractions things to do in {city}"
        places = await self.search_with_extraction(query, max_results=3)
        
        return {
            'city': city,
            'query': query,
            'places': places,
            'timestamp': datetime.now().isoformat()
        }
    
    async def search_restaurants(self, city: str) -> Dict[str, Any]:
        """Search for restaurants with place extraction"""
        query = f"best restaurants where to eat in {city}"
        places = await self.search_with_extraction(query, max_results=3)
        
        return {
            'city': city,
            'query': query,
            'places': places,
            'timestamp': datetime.now().isoformat()
        }
    
    async def search_hotels(self, city: str) -> Dict[str, Any]:
        """Search for hotels with place extraction"""
        query = f"best hotels where to stay in {city}"
        places = await self.search_with_extraction(query, max_results=3)
        
        return {
            'city': city,
            'query': query,
            'places': places,
            'timestamp': datetime.now().isoformat()
        }
    
    async def search_weather(self, city: str) -> Dict[str, Any]:
        """Search for weather (basic search, no extraction needed)"""
        query = f"weather in {city} today"
        results = await self._rate_limited_search(query, max_results=2)
        
        return {
            'city': city,
            'query': query,
            'results': [{'title': r.get('title', ''), 'snippet': r.get('body', ''), 'url': r.get('href', '')} for r in results],
            'timestamp': datetime.now().isoformat()
        }
    
    async def search_travel_tips(self, destination: str) -> Dict[str, Any]:
        """Search for travel tips"""
        query = f"travel guide tips {destination}"
        results = await self._rate_limited_search(query, max_results=2)
        
        return {
            'destination': destination,
            'query': query,
            'results': [{'title': r.get('title', ''), 'snippet': r.get('body', ''), 'url': r.get('href', '')} for r in results],
            'timestamp': datetime.now().isoformat()
        }


# Global instance
enhanced_search = EnhancedWebSearch()
