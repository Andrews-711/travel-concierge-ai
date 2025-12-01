"""
Chat Agent for conversational travel assistance
Uses RAG + web search + LLM
"""
from typing import List, Optional, Dict, Any
import uuid

from app.llm import llm
from app.rag_minimal import rag  # Using minimal RAG (no ChromaDB)
from app.web_search import web_search
from app.llm_search import llm_search  # LLM-based search for real place names
from app.schemas import ChatRequest, ChatResponse


class ChatAgent:
    """
    Conversational travel assistant
    - Uses RAG for uploaded document context
    - Uses web search for real-time info
    - Generates contextual responses with LLM
    """
    
    def __init__(self):
        self.conversation_history = {}  # In-memory session storage
    
    async def process_message(
        self,
        message: str,
        session_id: Optional[str] = None
    ) -> ChatResponse:
        """
        Process user message and generate response
        
        Args:
            message: User message
            session_id: Optional session ID
        
        Returns:
            Chat response
        """
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Initialize session history if needed
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        
        # Analyze intent
        intent = self._analyze_intent(message)
        
        # Gather context
        sources = []
        tool_calls = []
        
        # 1. RAG context (if available)
        rag_context = []
        if intent.get('needs_documents'):
            docs = rag.search(session_id, message, n_results=3)
            if docs:
                rag_context = docs
                sources.extend([
                    {
                        'type': 'document',
                        'content': doc['content'][:200] + '...',
                        'distance': doc['distance']
                    }
                    for doc in docs
                ])
                tool_calls.append('rag_search')
        
        # 2. Web search context (real-time data) - Use LLM-based search for real place names
        web_context = {}
        
        if intent.get('needs_weather'):
            city = intent.get('location', '')
            if city:
                print(f"[Chat Agent] Searching weather for {city}")
                weather = await llm_search.search_weather(city)
                web_context['weather'] = weather
                sources.append({'type': 'llm_search', 'query': f"Weather for {city}"})
                tool_calls.append('weather_search')
        
        if intent.get('needs_hotels'):
            city = intent.get('location', '')
            if city:
                print(f"[Chat Agent] Searching hotels in {city}")
                hotels = await llm_search.search_hotels(city)
                if hotels.get('places'):
                    web_context['hotels'] = hotels
                    sources.append({'type': 'llm_search', 'query': f"Hotels in {city}"})
                    tool_calls.append('hotel_search')
        
        if intent.get('needs_attractions'):
            city = intent.get('location', '')
            if city:
                print(f"[Chat Agent] Searching attractions in {city}")
                attractions = await llm_search.search_attractions(city)
                if attractions.get('places'):
                    web_context['attractions'] = attractions
                    sources.append({'type': 'llm_search', 'query': f"Attractions in {city}"})
                    tool_calls.append('attractions_search')
        
        if intent.get('needs_restaurants'):
            city = intent.get('location', '')
            if city:
                print(f"[Chat Agent] Searching restaurants in {city}")
                restaurants = await llm_search.search_restaurants(city)
                if restaurants.get('places'):
                    web_context['restaurants'] = restaurants
                    sources.append({'type': 'llm_search', 'query': f"Restaurants in {city}"})
                    tool_calls.append('restaurants_search')
        
        if intent.get('needs_general_search'):
            print(f"[Chat Agent] General travel query: {message}")
            # Use LLM directly for general travel questions
            tool_calls.append('llm_knowledge')
        
        # 3. Generate response with LLM
        response_text = await self._generate_response(
            message=message,
            rag_context=rag_context,
            web_context=web_context,
            history=self.conversation_history[session_id]
        )
        
        # Update conversation history
        self.conversation_history[session_id].append({
            'role': 'user',
            'content': message
        })
        self.conversation_history[session_id].append({
            'role': 'assistant',
            'content': response_text
        })
        
        # Keep only last 10 messages
        if len(self.conversation_history[session_id]) > 10:
            self.conversation_history[session_id] = self.conversation_history[session_id][-10:]
        
        return ChatResponse(
            message=response_text,
            sources=sources if sources else None,
            tool_calls=tool_calls if tool_calls else None,
            session_id=session_id
        )
    
    def _analyze_intent(self, message: str) -> Dict[str, Any]:
        """Analyze message to determine what information is needed"""
        
        message_lower = message.lower()
        
        intent = {
            'needs_documents': False,
            'needs_weather': False,
            'needs_hotels': False,
            'needs_attractions': False,
            'needs_restaurants': False,
            'needs_general_search': False,
            'location': None
        }
        
        # Document-related queries
        if any(word in message_lower for word in ['document', 'visa', 'requirement', 'uploaded', 'my file']):
            intent['needs_documents'] = True
        
        # Weather queries
        if any(word in message_lower for word in ['weather', 'temperature', 'climate', 'forecast', 'rain']):
            intent['needs_weather'] = True
        
        # Hotel queries
        if any(word in message_lower for word in ['hotel', 'stay', 'accommodation', 'lodging', 'where to stay']):
            intent['needs_hotels'] = True
        
        # Attraction queries
        if any(word in message_lower for word in ['attraction', 'visit', 'see', 'things to do', 'sightseeing', 'places']):
            intent['needs_attractions'] = True
        
        # Restaurant queries
        if any(word in message_lower for word in ['restaurant', 'food', 'eat', 'dining', 'cuisine']):
            intent['needs_restaurants'] = True
        
        # General travel questions
        if any(word in message_lower for word in ['how to', 'what is', 'when is', 'best time', 'cost', 'price']):
            intent['needs_general_search'] = True
        
        # Extract location (enhanced keyword matching)
        common_cities = [
            'tokyo', 'paris', 'london', 'new york', 'delhi', 'mumbai', 'bangalore',
            'rome', 'barcelona', 'amsterdam', 'dubai', 'singapore', 'bangkok',
            'istanbul', 'sydney', 'toronto', 'san francisco', 'los angeles', 'chicago',
            'chennai', 'kolkata', 'hyderabad', 'pune', 'ahmedabad', 'jaipur', 'goa',
            'berlin', 'madrid', 'vienna', 'prague', 'miami', 'vegas', 'seattle'
        ]
        
        for city in common_cities:
            if city in message_lower:
                intent['location'] = city.title()
                break
        
        # If no location found but asking about places, trigger attractions search
        if not intent['location'] and any(word in message_lower for word in ['places', 'attractions']):
            # Try to extract city from context
            words = message_lower.split()
            for i, word in enumerate(words):
                if word in ['in', 'at', 'near', 'around'] and i + 1 < len(words):
                    potential_location = words[i + 1].strip('?,.')
                    intent['location'] = potential_location.title()
                    break
        
        return intent
    
    async def _generate_response(
        self,
        message: str,
        rag_context: List[Dict],
        web_context: Dict[str, Any],
        history: List[Dict]
    ) -> str:
        """Generate response using LLM with all available context"""
        
        # Build context string
        context_parts = []
        
        # RAG documents
        if rag_context:
            context_parts.append("=== FROM YOUR UPLOADED DOCUMENTS ===")
            for doc in rag_context:
                context_parts.append(f"- {doc['content'][:300]}")
            context_parts.append("")
        
        # Web search results - Enhanced formatting with real place names
        if web_context:
            context_parts.append("=== REAL-TIME INFORMATION ===")
            
            if 'weather' in web_context:
                weather_data = web_context['weather']
                context_parts.append(f"\nWeather Information:")
                context_parts.append(f"Summary: {weather_data.get('summary', 'No weather data available')}")
            
            if 'attractions' in web_context:
                places = web_context['attractions'].get('places', [])
                context_parts.append(f"\nTop Attractions ({len(places)} found):")
                for i, place in enumerate(places[:10], 1):
                    desc = place.get('description', '')
                    price = place.get('price', '')
                    context_parts.append(f"{i}. {place['name']}{f' - {desc[:100]}' if desc else ''}{f' ({price})' if price else ''}")
            
            if 'restaurants' in web_context:
                places = web_context['restaurants'].get('places', [])
                context_parts.append(f"\nRestaurants ({len(places)} found):")
                for i, place in enumerate(places[:10], 1):
                    desc = place.get('description', '')
                    cuisine = place.get('cuisine', '')
                    context_parts.append(f"{i}. {place['name']}{f' - {cuisine}' if cuisine else ''}{f' - {desc[:80]}' if desc else ''}")
            
            if 'hotels' in web_context:
                places = web_context['hotels'].get('places', [])
                context_parts.append(f"\nHotels ({len(places)} found):")
                for i, place in enumerate(places[:10], 1):
                    desc = place.get('description', '')
                    price = place.get('price', '')
                    context_parts.append(f"{i}. {place['name']}{f' - {desc[:80]}' if desc else ''}{f' - {price}' if price else ''}")
            
            context_parts.append("")
        
        context = "\n".join(context_parts)
        
        # Build conversation history
        history_text = ""
        if history:
            history_text = "\n".join([
                f"{msg['role'].title()}: {msg['content']}"
                for msg in history[-6:]  # Last 3 exchanges
            ])
        
        # Build prompt
        system_message = """You are an expert AI Travel Concierge powered by Google Gemini 2.0. Your goal is to help travelers plan amazing trips and answer travel-related questions with REAL, SPECIFIC place names.

Your Capabilities:
- Access to real-time information about attractions, restaurants, hotels, and weather
- Provide ACTUAL place names - not generic descriptions
- Give personalized travel recommendations based on user interests
- Answer questions about destinations worldwide with specific details

CRITICAL RULES:
1. ALWAYS use the EXACT place names from the context provided
2. When recommending places, use the real names (e.g., "Senso-ji Temple", "Sukiyabashi Jiro", "Park Hyatt Tokyo")
3. Include descriptions and details from the context
4. If prices are available, mention them
5. Format responses clearly with numbered lists for multiple recommendations
6. Be enthusiastic and helpful - travel is exciting!

Guidelines:
- Use specific information from the provided context
- When listing attractions/restaurants/hotels, present them in a clear numbered format
- Include practical details (descriptions, prices, cuisine types) when available
- If you don't have current information, explain that and offer to search for it
- Always prioritize accuracy over generic suggestions"""
        
        # Build user prompt with clear instructions
        user_prompt = f"""User Question: {message}

{f'Previous Conversation:{chr(10)}{history_text}{chr(10)}{chr(10)}' if history_text else ''}{f'Available Information:{chr(10)}{context}{chr(10)}{chr(10)}' if context else 'No specific data available. Use your general travel knowledge to provide helpful guidance, but mention that you can search for real-time information if needed.{chr(10)}{chr(10)'}IMPORTANT: Use the EXACT place names from the information above. Format your response clearly:
- For attractions/restaurants/hotels: Use numbered lists with names and descriptions
- Be specific and detailed
- Include prices when available

Provide a helpful, engaging response:"""

        prompt = user_prompt

        # Generate response with system message
        response = await llm.generate(
            prompt=prompt, 
            system=system_message,
            max_tokens=1000,  # Increased for detailed responses
            temperature=0.7
        )
        
        print(f"[Chat Agent] Generated response length: {len(response)} chars")
        return response


# Global chat agent
chat_agent = ChatAgent()
