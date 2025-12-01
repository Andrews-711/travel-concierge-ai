"""
LLM-based search for travel information
Uses Gemini to generate real place names and information
"""
from typing import Dict, Any, List
import json
from datetime import datetime
from app.llm import llm


class LLMSearch:
    """
    Use LLM to generate real travel information
    More reliable than web scraping, has knowledge of real places
    """
    
    async def search_attractions(self, city: str) -> Dict[str, Any]:
        """Get real attractions using LLM knowledge"""
        
        prompt = f"""List the top 15 most popular tourist attractions in {city}.
For each attraction, provide:
- Exact name (as locals call it)
- Brief description (1 sentence)
- Typical entry fee (if applicable)
- Best visiting hours

Respond with ONLY valid JSON, no markdown:
{{
    "places": [
        {{
            "name": "Exact Attraction Name",
            "description": "Brief description",
            "price": "Entry fee or Free",
            "hours": "Opening hours"
        }}
    ]
}}"""

        try:
            response = await llm.generate(
                prompt=prompt,
                system="You are a travel expert with deep knowledge of destinations worldwide. Provide accurate, real information.",
                max_tokens=3000,
                temperature=0.3
            )
            
            # Parse JSON response
            response_clean = response.strip()
            
            # Remove markdown code blocks if present
            if '```json' in response_clean:
                response_clean = response_clean.split('```json')[1].split('```')[0].strip()
            elif '```' in response_clean:
                response_clean = response_clean.split('```')[1].split('```')[0].strip()
            
            # If response doesn't start with {, try to find JSON object
            if not response_clean.startswith('{'):
                start_idx = response_clean.find('{')
                if start_idx != -1:
                    response_clean = response_clean[start_idx:]
            
            # Parse the JSON
            data = json.loads(response_clean)
            places = data.get('places', [])
            
            print(f"Successfully extracted {len(places)} attractions")
            
            return {
                'city': city,
                'query': f'attractions in {city}',
                'places': places,
                'timestamp': datetime.now().isoformat()
            }
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error for attractions: {e}")
            print(f"Response was: {response[:200] if 'response' in locals() else 'No response'}...")
            return {
                'city': city,
                'query': f'attractions in {city}',
                'places': [],
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"LLM search error for attractions: {e}")
            return {
                'city': city,
                'query': f'attractions in {city}',
                'places': [],
                'timestamp': datetime.now().isoformat()
            }
    
    async def search_restaurants(self, city: str) -> Dict[str, Any]:
        """Get real restaurants using LLM knowledge"""
        
        prompt = f"""List 15 popular, highly-rated restaurants in {city}.
Include a mix of local cuisine and international options, different price ranges.
For each restaurant, provide:
- Exact name
- Cuisine type
- Price range ($, $$, $$$)
- Brief description (1 sentence)

Respond with ONLY valid JSON, no markdown:
{{
    "places": [
        {{
            "name": "Restaurant Name",
            "description": "Cuisine type - What they're known for",
            "price": "$$",
            "cuisine": "Cuisine type"
        }}
    ]
}}"""

        try:
            response = await llm.generate(
                prompt=prompt,
                system="You are a food critic with extensive knowledge of restaurants worldwide. Provide real restaurant names.",
                max_tokens=3000,
                temperature=0.3
            )
            
            # Parse JSON
            response_clean = response.strip()
            if '```json' in response_clean:
                response_clean = response_clean.split('```json')[1].split('```')[0].strip()
            elif '```' in response_clean:
                response_clean = response_clean.split('```')[1].split('```')[0].strip()
            
            if not response_clean.startswith('{'):
                start_idx = response_clean.find('{')
                if start_idx != -1:
                    response_clean = response_clean[start_idx:]
            
            data = json.loads(response_clean)
            places = data.get('places', [])
            
            print(f"Successfully extracted {len(places)} restaurants")
            
            return {
                'city': city,
                'query': f'restaurants in {city}',
                'places': places,
                'timestamp': datetime.now().isoformat()
            }
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error for restaurants: {e}")
            print(f"Response was: {response[:200] if 'response' in locals() else 'No response'}...")
            return {
                'city': city,
                'query': f'restaurants in {city}',
                'places': [],
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"LLM search error for restaurants: {e}")
            return {
                'city': city,
                'query': f'restaurants in {city}',
                'places': [],
                'timestamp': datetime.now().isoformat()
            }
    
    async def search_hotels(self, city: str) -> Dict[str, Any]:
        """Get real hotels using LLM knowledge"""
        
        prompt = f"""List 12 popular hotels in {city} across different price ranges (budget, mid-range, luxury).
For each hotel, provide:
- Exact hotel name
- Approximate price per night
- Brief description (1 sentence)
- Key amenities

Respond with ONLY valid JSON, no markdown:
{{
    "places": [
        {{
            "name": "Hotel Name",
            "description": "Brief description and location",
            "price": "$50-80/night or $$$ for luxury",
            "amenities": "Pool, Spa, WiFi"
        }}
    ]
}}"""

        try:
            response = await llm.generate(
                prompt=prompt,
                system="You are a travel accommodation expert with knowledge of hotels worldwide. Provide real hotel names.",
                max_tokens=3000,
                temperature=0.3
            )
            
            # Parse JSON
            response_clean = response.strip()
            if '```json' in response_clean:
                response_clean = response_clean.split('```json')[1].split('```')[0].strip()
            elif '```' in response_clean:
                response_clean = response_clean.split('```')[1].split('```')[0].strip()
            
            if not response_clean.startswith('{'):
                start_idx = response_clean.find('{')
                if start_idx != -1:
                    response_clean = response_clean[start_idx:]
            
            data = json.loads(response_clean)
            places = data.get('places', [])
            
            print(f"Successfully extracted {len(places)} hotels")
            
            return {
                'city': city,
                'query': f'hotels in {city}',
                'places': places,
                'timestamp': datetime.now().isoformat()
            }
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error for hotels: {e}")
            print(f"Response was: {response[:200] if 'response' in locals() else 'No response'}...")
            return {
                'city': city,
                'query': f'hotels in {city}',
                'places': [],
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"LLM search error for hotels: {e}")
            return {
                'city': city,
                'query': f'hotels in {city}',
                'places': [],
                'timestamp': datetime.now().isoformat()
            }
    
    async def search_weather(self, city: str) -> Dict[str, Any]:
        """Get weather information using LLM knowledge"""
        
        prompt = f"""Provide current typical weather information for {city} in December 2025.
Include temperature, conditions, and what to expect.
Keep it brief (2-3 sentences)."""

        try:
            response = await llm.generate(
                prompt=prompt,
                system="You are a weather expert. Provide typical weather patterns.",
                max_tokens=200,
                temperature=0.3
            )
            
            return {
                'city': city,
                'query': f'weather in {city}',
                'results': [{'title': f'Weather in {city}', 'snippet': response.strip(), 'url': ''}],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"LLM search error for weather: {e}")
            return {
                'city': city,
                'query': f'weather in {city}',
                'results': [],
                'timestamp': datetime.now().isoformat()
            }
    
    async def search_travel_tips(self, destination: str) -> Dict[str, Any]:
        """Get travel tips using LLM knowledge"""
        
        prompt = f"""Provide 5 essential travel tips for visiting {destination}.
Include practical advice about transportation, money, customs, safety, and best times to visit.
Keep each tip to 1-2 sentences."""

        try:
            response = await llm.generate(
                prompt=prompt,
                system="You are a travel advisor with extensive destination knowledge.",
                max_tokens=400,
                temperature=0.3
            )
            
            return {
                'destination': destination,
                'query': f'travel tips for {destination}',
                'results': [{'title': f'Travel Tips for {destination}', 'snippet': response.strip(), 'url': ''}],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"LLM search error for tips: {e}")
            return {
                'destination': destination,
                'query': f'travel tips for {destination}',
                'results': [],
                'timestamp': datetime.now().isoformat()
            }


# Global instance
llm_search = LLMSearch()
