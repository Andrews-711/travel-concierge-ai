"""
Travel Planning Agent
Uses LLM-based search for real place names + LLM to create trip itineraries
"""
from typing import Dict, Any, List
import json

from app.llm import llm
from app.llm_search import llm_search
from app.schemas import TripPlanRequest, Itinerary, DayPlan, TripPlanResponse


class TravelPlannerAgent:
    """
    Agent for creating trip itineraries
    - Uses LLM to get real place names (attractions, restaurants, hotels)
    - LLM for generating structured itineraries
    - Creates 3 budget options
    """
    
    async def plan_trip(self, request: TripPlanRequest) -> TripPlanResponse:
        """
        Create complete trip plan with 3 budget options
        
        Args:
            request: Trip planning request
        
        Returns:
            Trip plan with 3 itinerary options
        """
        # Step 1: Gather real-time information via LLM search
        # Only search for attractions - everything else will be in the main itinerary generation
        print(f"\n=== STARTING LLM SEARCH FOR {request.destination} ===")
        
        attractions_data = await llm_search.search_attractions(request.destination)
        
        # Extract places from LLM search
        attractions = attractions_data.get('places', [])
        
        print(f"\n=== LLM SEARCH RESULTS ===")
        print(f"Found: {len(attractions)} attractions")
        if attractions:
            print(f"Sample attractions: {[a['name'] for a in attractions[:5]]}")
        
        # Add fallback popular places if LLM search returned nothing
        if not attractions:
            print("Using fallback attractions")
            attractions = self._get_fallback_attractions(request.destination)
        
        print("===================\n")
        
        # Step 2: Generate single itinerary with LLM choosing restaurants/hotels
        itinerary = await self._generate_single_itinerary(
            request=request,
            attractions=attractions
        )
        
        # Step 3: Create map link
        map_link = f"https://www.google.com/maps/search/{request.destination.replace(' ', '+')}"
        
        return TripPlanResponse(
            destination=request.destination,
            duration=request.duration_days,
            options=[itinerary],  # Single best option
            weather_info={},  # Not needed for now
            map_link=map_link
        )
    
    
    async def _generate_single_itinerary(
        self,
        request: TripPlanRequest,
        attractions: List[Dict]
    ) -> Itinerary:
        """Generate single best itinerary with LLM choosing restaurants and hotels"""
        
        # Build list of actual attractions
        attraction_list = "\n".join([
            f"  {i+1}. {a['name']}" + (f" - {a.get('description', '')[:80]}" if a.get('description') else "")
            for i, a in enumerate(attractions[:15])
        ]) if attractions else "  (Will recommend popular attractions)"
        
        # Build comprehensive system message
        system_message = """You are an expert travel planner creating detailed, realistic itineraries.
Use the provided attraction names and recommend actual restaurants and hotels in the destination.
CRITICAL: Use real place names - actual attractions, real restaurant names, real hotel names that exist in the destination."""
        
        # Build detailed prompt - LLM will choose restaurants/hotels
        prompt = f"""Create a detailed {request.duration_days}-day trip itinerary for {request.destination}.

TRIP PARAMETERS:
- Total Budget: {request.budget:.2f} {request.currency}
- Daily Budget: ~{request.budget/request.duration_days:.2f} {request.currency}/day
- Traveler Interests: {', '.join(request.interests) if request.interests else 'general sightseeing, culture, food'}
- Dietary Preferences: {', '.join(request.dietary_preferences) if request.dietary_preferences else 'none'}

AVAILABLE ATTRACTIONS (USE THESE EXACT NAMES):
{attraction_list}

INSTRUCTIONS:
1. Use the actual attraction names listed above for activities
2. Recommend REAL restaurants in {request.destination} (research and use actual restaurant names)
3. Recommend REAL hotels in {request.destination} (research and use actual hotel names)
4. Create realistic daily schedules with specific timing
5. Include different places each day for variety
6. Match activities to user interests: {', '.join(request.interests) if request.interests else 'general'}
7. Suggest authentic local dishes and must-try foods in {request.destination}

FOR EACH DAY INCLUDE:
- Morning activity (8 AM - 12 PM) with specific attraction name from list
- Afternoon activity (12 PM - 6 PM) with specific attraction name from list
- Evening activity (6 PM - 10 PM) with dinner location
- Meals with REAL restaurant names in {request.destination} and specific local dishes to try
- Total estimated daily cost

RESPOND WITH VALID JSON ONLY (no markdown, no extra text):
{{
    "days": [
        {{
            "day": 1,
            "morning": "9 AM: Visit [Actual Attraction Name from list] - [Activity description]. Entry: [Cost if known]. Duration: [time]",
            "afternoon": "2 PM: Explore [Another Attraction from list] - [Activity]. Entry: [Cost]",
            "evening": "7 PM: Dinner at [Real Restaurant Name in {request.destination}]. Try their [specific local dish].",
            "meals": {{
                "breakfast": "[Real Restaurant Name] - [Local dish] (Est. cost)",
                "lunch": "[Real Restaurant Name] - [Local dish] (Est. cost)",
                "dinner": "[Real Restaurant Name] - [Local dish] (Est. cost)"
            }},
            "estimated_cost": {request.budget/request.duration_days:.2f}
        }}
    ],
    "accommodation_suggestions": [
        "[Real Hotel Name in {request.destination}] - [Price range] - [Brief description]",
        "[Another Real Hotel Name] - [Price range] - [Brief description]"
    ],
    "packing_list": ["Item 1", "Item 2", ...],
    "tips": ["Tip 1", "Tip 2", ...]
}}"""

        # Generate with LLM
        response = await llm.generate(
            prompt=prompt,
            system=system_message,
            max_tokens=3000,
            temperature=0.7
        )
        
        # Parse response
        try:
            # Clean JSON from response
            response_clean = response.strip()
            if '```json' in response_clean:
                response_clean = response_clean.split('```json')[1].split('```')[0].strip()
            elif '```' in response_clean:
                response_clean = response_clean.split('```')[1].split('```')[0].strip()
            
            # Extract JSON object
            if not response_clean.startswith('{'):
                start_idx = response_clean.find('{')
                if start_idx != -1:
                    response_clean = response_clean[start_idx:]
            
            data = json.loads(response_clean)
            
            # Log the parsed data to verify costs
            print(f"Parsed itinerary data - Days count: {len(data.get('days', []))}")
            
            days = [
                DayPlan(**day_data)
                for day_data in data.get('days', [])
            ]
            
            total_cost = sum(day.estimated_cost for day in days)
            print(f"Daily costs: {[day.estimated_cost for day in days]}")
            print(f"Total cost calculated: {total_cost} (should be close to {request.budget})")
            
            return Itinerary(
                title=f"Best Trip to {request.destination}",
                budget_type="balanced",
                total_cost=total_cost,
                currency=request.currency,
                days=days,
                accommodation_suggestions=data.get('accommodation_suggestions', []),
                packing_list=data.get('packing_list', []),
                tips=data.get('tips', [])
            )
            
        except (json.JSONDecodeError, KeyError, Exception) as e:
            print(f"JSON parsing error: {e}")
            print(f"LLM Response: {response[:300] if response else 'Empty'}...")
            
            # Fallback itinerary with real place names
            return self._create_fallback_itinerary(
                request=request,
                budget_type="balanced",
                adjusted_budget=request.budget,
                attractions=attractions,
                restaurants=[],
                hotels=[]
            )
    
    async def _generate_itinerary(
        self,
        request: TripPlanRequest,
        budget_type: str,
        attractions: List[Dict],
        restaurants: List[Dict],
        hotels: List[Dict],
        weather_info: Dict,
        tips_info: Dict
    ) -> Itinerary:
        """Generate single itinerary using LLM with actual place data"""
        
        # Calculate budget multiplier
        multipliers = {"budget": 0.7, "balanced": 1.0, "luxury": 1.4}
        multiplier = multipliers[budget_type]
        adjusted_budget = request.budget * multiplier
        
        # Build list of actual places
        attraction_list = "\n".join([
            f"  {i+1}. {a['name']}" + (f" - {a.get('description', '')[:80]}" if a.get('description') else "")
            for i, a in enumerate(attractions[:15])
        ]) if attractions else "  (Search in progress - will use general recommendations)"
        
        restaurant_list = "\n".join([
            f"  {i+1}. {r['name']}" + (f" - {r.get('description', '')[:60]}" if r.get('description') else "")
            for i, r in enumerate(restaurants[:15])
        ]) if restaurants else "  (Search in progress - will use local dining options)"
        
        hotel_list = "\n".join([
            f"  {i+1}. {h['name']}" + (f" - {h.get('description', '')[:60]}" if h.get('description') else "")
            for i, h in enumerate(hotels[:10])
        ]) if hotels else "  (Search in progress - will recommend suitable accommodation)"
        
        # Build weather context
        weather_context = ""
        if weather_info.get('results'):
            weather_context = "\n".join([
                r.get('snippet', '')[:120] for r in weather_info['results'][:2]
            ])
        
        # Build tips context
        tips_context = ""
        if tips_info.get('results'):
            tips_context = "\n".join([
                f"- {r.get('snippet', '')[:150]}" for r in tips_info['results'][:3]
            ])
        
        # Build comprehensive system message
        system_message = """You are an expert travel planner creating detailed itineraries.
Use the ACTUAL PLACE NAMES provided. Create realistic, day-by-day plans with specific locations, timing, and costs.
CRITICAL: Use only the real attraction, restaurant, and hotel names from the provided lists."""
        
        # Build detailed prompt
        prompt = f"""Create a detailed {request.duration_days}-day trip itinerary for {request.destination}.

TRIP PARAMETERS:
- Total Budget: {adjusted_budget:.2f} {request.currency} ({budget_type} tier)
- Daily Budget: ~{adjusted_budget/request.duration_days:.2f} {request.currency}/day
- Traveler Interests: {', '.join(request.interests) if request.interests else 'general sightseeing'}
- Dietary Preferences: {', '.join(request.dietary_preferences) if request.dietary_preferences else 'none'}

WEATHER INFO:
{weather_context}

AVAILABLE ATTRACTIONS (USE THESE EXACT NAMES):
{attraction_list}

AVAILABLE RESTAURANTS (USE THESE EXACT NAMES):
{restaurant_list}

AVAILABLE HOTELS (USE THESE EXACT NAMES):
{hotel_list}

TRAVEL TIPS:
{tips_context}

INSTRUCTIONS:
1. Use ONLY the actual attraction, restaurant, and hotel names listed above
2. Create realistic daily schedules with specific timing (e.g., "9 AM: Visit Tanah Lot Temple")
3. Include different places each day for variety
4. Add estimated costs for activities and meals
5. Match activities to user interests: {', '.join(request.interests) if request.interests else 'general'}

FOR EACH DAY INCLUDE:
- Morning activity (8 AM - 12 PM) with specific attraction name
- Afternoon activity (12 PM - 6 PM) with specific attraction name
- Evening activity (6 PM - 10 PM) with dinner location
- Meals with specific restaurant names and estimated costs
- Total estimated daily cost

RESPOND WITH VALID JSON ONLY (no markdown, no extra text):
{{
    "days": [
        {{
            "day": 1,
            "morning": "9 AM: Visit [Actual Attraction Name from list] - [Activity description]. Entry: [Cost if known]. Duration: [time]",
            "afternoon": "2 PM: Explore [Another Attraction from list] - [Activity]. Entry: [Cost]",
            "evening": "7 PM: Dinner at [Restaurant Name from list]. Evening activity.",
            "meals": {{
                "breakfast": "[Restaurant Name] - [Dish type] (Est. cost)",
                "lunch": "[Restaurant Name] - [Dish type] (Est. cost)",
                "dinner": "[Restaurant Name] - [Dish type] (Est. cost)"
            }},
            "estimated_cost": {adjusted_budget/request.duration_days:.2f}
        }}
    ],
    "accommodation_suggestions": [
        "[Hotel Name from list] - [Details]",
        "[Another Hotel Name] - [Details]"
    ],
    "packing_list": ["Item 1", "Item 2", ...],
    "tips": ["Tip 1", "Tip 2", ...]
}}"""

        # Generate with LLM
        response = await llm.generate(
            prompt=prompt,
            system=system_message,
            max_tokens=3000,
            temperature=0.7
        )
        
        # Parse response
        try:
            # Clean JSON from response
            response_clean = response.strip()
            if '```json' in response_clean:
                response_clean = response_clean.split('```json')[1].split('```')[0].strip()
            elif '```' in response_clean:
                response_clean = response_clean.split('```')[1].split('```')[0].strip()
            
            # Extract JSON object
            if not response_clean.startswith('{'):
                start_idx = response_clean.find('{')
                end_idx = response_clean.rfind('}')
                if start_idx != -1 and end_idx != -1:
                    response_clean = response_clean[start_idx:end_idx+1]
            
            data = json.loads(response_clean)
            
            days = [
                DayPlan(**day_data)
                for day_data in data.get('days', [])
            ]
            
            total_cost = sum(day.estimated_cost for day in days)
            
            return Itinerary(
                title=f"{budget_type.title()} Trip to {request.destination}",
                budget_type=budget_type,
                total_cost=total_cost,
                currency=request.currency,
                days=days,
                accommodation_suggestions=data.get('accommodation_suggestions', []),
                packing_list=data.get('packing_list', []),
                tips=data.get('tips', [])
            )
            
        except (json.JSONDecodeError, KeyError, Exception) as e:
            print(f"JSON parsing error: {e}")
            print(f"LLM Response: {response[:300]}...")
            
            # Fallback itinerary with real place names
            return self._create_fallback_itinerary(
                request=request,
                budget_type=budget_type,
                adjusted_budget=adjusted_budget,
                attractions=attractions,
                restaurants=restaurants,
                hotels=hotels
            )
    
    def _create_fallback_itinerary(
        self,
        request: TripPlanRequest,
        budget_type: str,
        adjusted_budget: float,
        attractions: List[Dict],
        restaurants: List[Dict],
        hotels: List[Dict]
    ) -> Itinerary:
        """Create fallback itinerary using actual place names"""
        
        days = []
        daily_budget = adjusted_budget / request.duration_days
        
        # Use actual places or create generic ones
        if not attractions:
            attractions = [{'name': f'Popular attraction in {request.destination}', 'description': 'Must-see location'}]
        if not restaurants:
            restaurants = [{'name': 'Local restaurant', 'description': 'Traditional cuisine'}]
        if not hotels:
            hotels = [{'name': f'{budget_type.title()} hotel in {request.destination}', 'description': 'Comfortable accommodation'}]
        
        # Create days with place rotation
        for day_num in range(1, request.duration_days + 1):
            morning_idx = ((day_num - 1) * 2) % len(attractions)
            afternoon_idx = ((day_num - 1) * 2 + 1) % len(attractions)
            
            breakfast_idx = ((day_num - 1) * 3) % len(restaurants)
            lunch_idx = ((day_num - 1) * 3 + 1) % len(restaurants)
            dinner_idx = ((day_num - 1) * 3 + 2) % len(restaurants)
            
            morning_place = attractions[morning_idx]
            afternoon_place = attractions[afternoon_idx]
            
            days.append(DayPlan(
                day=day_num,
                morning=f"9 AM: Visit {morning_place['name']} - {morning_place.get('description', 'Sightseeing and exploration')}",
                afternoon=f"2 PM: Explore {afternoon_place['name']} - {afternoon_place.get('description', 'Continue exploring')}",
                evening=f"7 PM: Dinner at {restaurants[dinner_idx]['name']} followed by evening stroll",
                meals={
                    "breakfast": f"{restaurants[breakfast_idx]['name']} - Local breakfast",
                    "lunch": f"{restaurants[lunch_idx]['name']} - Lunch",
                    "dinner": f"{restaurants[dinner_idx]['name']} - Dinner"
                },
                estimated_cost=daily_budget
            ))
        
        # Accommodation suggestions
        accommodation_list = [f"{h['name']} - {h.get('description', 'Good location')}" for h in hotels[:5]]
        if not accommodation_list:
            accommodation_list = [f"{budget_type.title()} hotel in {request.destination}"]
        
        return Itinerary(
            title=f"{budget_type.title()} Trip to {request.destination}",
            budget_type=budget_type,
            total_cost=adjusted_budget,
            currency=request.currency,
            days=days,
            accommodation_suggestions=accommodation_list,
            packing_list=[
                "Comfortable walking shoes",
                "Weather-appropriate clothing",
                "Travel documents and copies",
                "Camera/smartphone with charger",
                "Universal power adapter",
                "Personal toiletries",
                "Daypack for excursions",
                "Reusable water bottle",
                "Sunscreen and sunglasses",
                "Light rain jacket"
            ],
            tips=[
                f"Book {request.destination} attractions in advance to save time",
                "Download offline maps before arrival",
                "Try authentic local cuisine",
                "Use local transportation to save money",
                "Respect local customs and dress codes",
                "Keep copies of important documents",
                f"Check visa requirements for {request.destination}"
            ]
        )


# Fallback data methods
    def _get_fallback_attractions(self, destination: str) -> List[Dict]:
        """Get fallback attractions when search fails"""
        dest_lower = destination.lower()
        
        fallback_data = {
            'bali': [
                {'name': 'Tanah Lot Temple', 'description': 'Ancient Hindu shrine on rock formation'},
                {'name': 'Ubud Monkey Forest', 'description': 'Sacred sanctuary with temples and monkeys'},
                {'name': 'Tegallalang Rice Terraces', 'description': 'Iconic terraced rice fields'},
                {'name': 'Uluwatu Temple', 'description': 'Clifftop temple with ocean views'},
                {'name': 'Seminyak Beach', 'description': 'Popular beach with restaurants and clubs'},
                {'name': 'Mount Batur', 'description': 'Active volcano with sunrise treks'},
                {'name': 'Tirta Empul Temple', 'description': 'Holy spring water temple'},
                {'name': 'Nusa Penida', 'description': 'Island with stunning beaches and cliffs'},
            ],
            'paris': [
                {'name': 'Eiffel Tower', 'description': 'Iconic iron landmark'},
                {'name': 'Louvre Museum', 'description': 'World-famous art museum'},
                {'name': 'Notre-Dame Cathedral', 'description': 'Gothic cathedral'},
                {'name': 'Arc de Triomphe', 'description': 'Triumphal arch monument'},
                {'name': 'Sacré-Cœur', 'description': 'Basilica on Montmartre hill'},
                {'name': 'Versailles Palace', 'description': 'Royal palace with gardens'},
            ],
            'tokyo': [
                {'name': 'Senso-ji Temple', 'description': 'Ancient Buddhist temple in Asakusa'},
                {'name': 'Tokyo Skytree', 'description': 'Tallest structure in Japan'},
                {'name': 'Shibuya Crossing', 'description': 'Famous pedestrian scramble'},
                {'name': 'Meiji Shrine', 'description': 'Shinto shrine in forest'},
                {'name': 'Tsukiji Outer Market', 'description': 'Fresh seafood and food stalls'},
                {'name': 'Tokyo Tower', 'description': 'Communications and observation tower'},
            ]
        }
        
        # Try to find matching destination
        for key in fallback_data:
            if key in dest_lower:
                return fallback_data[key]
        
        # Generic fallback
        return [
            {'name': f'Historic District of {destination}', 'description': 'Cultural heritage area'},
            {'name': f'Main Square of {destination}', 'description': 'Central gathering place'},
            {'name': f'{destination} Museum', 'description': 'Local history and culture'},
            {'name': f'Popular Market in {destination}', 'description': 'Local shopping experience'},
        ]
    
    def _get_fallback_restaurants(self, destination: str) -> List[Dict]:
        """Get fallback restaurants when search fails"""
        dest_lower = destination.lower()
        
        fallback_data = {
            'bali': [
                {'name': 'Locavore', 'description': 'Award-winning modern Indonesian cuisine'},
                {'name': 'Warung Biah Biah', 'description': 'Authentic Balinese food'},
                {'name': 'Mozaic Restaurant', 'description': 'French-Indonesian fusion'},
                {'name': 'Sardine', 'description': 'Fresh seafood in rice fields'},
                {'name': 'La Plancha', 'description': 'Beach club with Spanish food'},
            ],
            'paris': [
                {'name': 'Le Comptoir du Relais', 'description': 'Classic French bistro'},
                {'name': 'Septime', 'description': 'Modern French cuisine'},
                {'name': 'Chez L\'Ami Jean', 'description': 'Traditional Basque-French'},
            ],
            'tokyo': [
                {'name': 'Sukiyabashi Jiro', 'description': 'Renowned sushi restaurant'},
                {'name': 'Ichiran Ramen', 'description': 'Famous tonkotsu ramen chain'},
                {'name': 'Narisawa', 'description': 'Innovative Japanese cuisine'},
            ]
        }
        
        for key in fallback_data:
            if key in dest_lower:
                return fallback_data[key]
        
        return [
            {'name': f'Traditional Restaurant in {destination}', 'description': 'Local cuisine'},
            {'name': f'Popular Eatery {destination}', 'description': 'Local favorites'},
        ]
    
    def _get_fallback_hotels(self, destination: str) -> List[Dict]:
        """Get fallback hotels when search fails"""
        return [
            {'name': f'Central Hotel {destination}', 'description': 'Downtown location'},
            {'name': f'{destination} Resort', 'description': 'Resort with amenities'},
            {'name': f'Budget Inn {destination}', 'description': 'Affordable accommodation'},
        ]


# Global planner agent
planner_agent = TravelPlannerAgent()
