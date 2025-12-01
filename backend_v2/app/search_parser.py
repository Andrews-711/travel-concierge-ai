"""
Intelligent search result parser
Extracts structured information from web search results
"""
import re
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class Attraction:
    """Structured attraction information"""
    name: str
    description: str
    location: str = ""
    price: str = ""
    hours: str = ""
    rating: str = ""


@dataclass
class Restaurant:
    """Structured restaurant information"""
    name: str
    cuisine: str = ""
    location: str = ""
    price_range: str = ""
    rating: str = ""
    description: str = ""


@dataclass
class Hotel:
    """Structured hotel information"""
    name: str
    location: str = ""
    price_per_night: str = ""
    rating: str = ""
    amenities: List[str] = None
    description: str = ""


class SearchResultParser:
    """Parse and extract structured data from search results"""
    
    # Fallback well-known attractions by city
    KNOWN_ATTRACTIONS = {
        'bali': [
            'Tanah Lot Temple', 'Uluwatu Temple', 'Ubud Monkey Forest', 
            'Tegallalang Rice Terraces', 'Sacred Monkey Forest Sanctuary',
            'Tirta Empul Temple', 'Mount Batur', 'Seminyak Beach',
            'Kuta Beach', 'Besakih Temple', 'Nusa Penida Island',
            'Goa Gajah (Elephant Cave)', 'Jatiluwih Rice Terraces'
        ],
        'paris': [
            'Eiffel Tower', 'Louvre Museum', 'Notre-Dame Cathedral',
            'Arc de Triomphe', 'Sacré-Cœur', 'Musée d\'Orsay',
            'Champs-Élysées', 'Palace of Versailles', 'Latin Quarter'
        ],
        'tokyo': [
            'Senso-ji Temple', 'Tokyo Skytree', 'Meiji Shrine',
            'Shibuya Crossing', 'Tsukiji Outer Market', 'Tokyo Tower',
            'Imperial Palace', 'Akihabara', 'Shinjuku Gyoen'
        ],
        'chennai': [
            'Marina Beach', 'Kapaleeshwarar Temple', 'Fort St. George',
            'Government Museum', 'San Thome Cathedral', 'Mahabalipuram Shore Temple',
            'Vadapalani Murugan Temple', 'Guindy National Park', 'DakshinaChitra'
        ]
    }
    
    def parse_attractions(self, search_results: List[Dict]) -> List[Attraction]:
        """Extract attraction information from search results"""
        attractions = []
        
        for result in search_results:
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            
            # Skip if it's just a list article
            if self._is_listicle(title):
                # Try to extract individual attractions from snippet
                extracted = self._extract_places_from_text(snippet)
                for name in extracted[:5]:  # Max 5 from each listicle
                    attractions.append(Attraction(
                        name=name,
                        description=self._extract_description_for_place(name, snippet),
                        location=""
                    ))
            else:
                # Clean the title
                name = self._clean_title(title)
                if name and len(name) > 3:
                    # Extract price if mentioned
                    price = self._extract_price(snippet)
                    hours = self._extract_hours(snippet)
                    rating = self._extract_rating(snippet)
                    
                    attractions.append(Attraction(
                        name=name,
                        description=snippet[:200],
                        price=price,
                        hours=hours,
                        rating=rating
                    ))
        
        # If we got very few attractions, add known ones
        if len(attractions) < 5:
            attractions.extend(self._get_known_attractions_for_city(search_results))
        
        return attractions[:15]  # Limit to 15 attractions
    
    def parse_restaurants(self, search_results: List[Dict]) -> List[Restaurant]:
        """Extract restaurant information from search results"""
        restaurants = []
        
        for result in search_results:
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            
            if self._is_listicle(title):
                # Extract restaurant names from snippet
                extracted = self._extract_places_from_text(snippet)
                for name in extracted[:5]:
                    restaurants.append(Restaurant(
                        name=name,
                        description=self._extract_description_for_place(name, snippet),
                        price_range=self._extract_price_range(snippet)
                    ))
            else:
                name = self._clean_title(title)
                if name and len(name) > 3:
                    cuisine = self._extract_cuisine(snippet)
                    price_range = self._extract_price_range(snippet)
                    rating = self._extract_rating(snippet)
                    
                    restaurants.append(Restaurant(
                        name=name,
                        cuisine=cuisine,
                        price_range=price_range,
                        rating=rating,
                        description=snippet[:150]
                    ))
        
        return restaurants[:20]  # Limit to 20 restaurants
    
    def parse_hotels(self, search_results: List[Dict]) -> List[Hotel]:
        """Extract hotel information from search results"""
        hotels = []
        
        for result in search_results:
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            
            if self._is_listicle(title):
                extracted = self._extract_places_from_text(snippet)
                for name in extracted[:2]:
                    hotels.append(Hotel(
                        name=name,
                        description=f"Recommended accommodation"
                    ))
            else:
                name = self._clean_title(title)
                if name and len(name) > 3:
                    price = self._extract_hotel_price(snippet)
                    rating = self._extract_rating(snippet)
                    amenities = self._extract_amenities(snippet)
                    
                    hotels.append(Hotel(
                        name=name,
                        price_per_night=price,
                        rating=rating,
                        amenities=amenities,
                        description=snippet[:150]
                    ))
        
        return hotels[:8]  # Limit to 8 hotels
    
    def _is_listicle(self, title: str) -> bool:
        """Check if title is a listicle article"""
        patterns = [
            r'\d+\s+(best|top|epic|amazing)',
            r'(best|top)\s+\d+',
            r'ultimate\s+(guide|list)',
            r'things to do',
            r'where to stay'
        ]
        title_lower = title.lower()
        return any(re.search(pattern, title_lower) for pattern in patterns)
    
    def _clean_title(self, title: str) -> str:
        """Clean article title to extract place name"""
        # Remove date prefixes like "Dec 1, 2025 ·"
        title = re.sub(r'^[A-Z][a-z]{2}\s+\d+,\s+\d{4}\s*·\s*', '', title)
        
        # Remove common suffixes
        suffixes = [
            r'\s*-\s*.*$',  # Everything after dash
            r'\s*\|.*$',    # Everything after pipe
            r'\s*\(.*\)$',  # Content in parentheses at end
            r'\s+2025$',    # Year
            r'\s+2024$',
        ]
        for pattern in suffixes:
            title = re.sub(pattern, '', title, count=1)
        
        return title.strip()
    
    def _extract_places_from_text(self, text: str) -> List[str]:
        """Extract place names from text (from listicles)"""
        places = []
        
        # Look for numbered items or bullet points
        # Pattern: "1. Place Name" or "• Place Name" or "- Place Name"
        patterns = [
            r'\d+\.\s+([A-Z][^.!?\n]{3,80}?)(?=\s*[-–—:,]|\s*\(|\n|$)',
            r'[•\-]\s+([A-Z][^.!?\n]{3,80}?)(?=\s*[-–—:,]|\s*\(|\n|$)',
            r'(?:Visit|Try|Explore|See)\s+([A-Z][^.!?\n]{5,70}?)(?=\s*[-–—:,]|\s*\(|\n|for|with|at)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                cleaned = match.strip()
                # Remove common prefixes
                cleaned = re.sub(r'^(the|The)\s+', '', cleaned)
                # Only keep if it looks like a place name (has capital letters, reasonable length)
                if len(cleaned) > 3 and len(cleaned) < 70 and re.search(r'[A-Z]', cleaned):
                    places.append(cleaned)
        
        # Also try to find place names mentioned directly in sentences
        # Look for proper nouns (capitalized words)
        sentences = re.split(r'[.!?]\s+', text)
        for sentence in sentences[:5]:  # First 5 sentences
            # Find sequences of capitalized words (potential place names)
            proper_nouns = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})\b', sentence)
            for noun in proper_nouns:
                # Filter out common words
                if noun not in ['The', 'This', 'These', 'Those', 'Here', 'There', 'Best', 'Top', 'Things', 'Bali', 'Indonesia']:
                    if len(noun) > 3 and len(noun) < 50:
                        places.append(noun)
        
        # Deduplicate while preserving order
        seen = set()
        unique_places = []
        for place in places:
            place_lower = place.lower()
            if place_lower not in seen and len(place) > 3:
                seen.add(place_lower)
                unique_places.append(place)
        
        return unique_places[:15]
    
    def _extract_description_for_place(self, place_name: str, text: str) -> str:
        """Extract description for a specific place from text"""
        # Try to find the sentence containing this place
        sentences = re.split(r'[.!?]\s+', text)
        for sentence in sentences:
            if place_name.lower() in sentence.lower():
                # Return this sentence as description
                return sentence.strip()[:150]
        return "Popular attraction"
    
    def _get_known_attractions_for_city(self, search_results: List[Dict]) -> List[Attraction]:
        """Get known attractions for a city as fallback"""
        attractions = []
        
        # Try to detect city from search results
        all_text = ' '.join([r.get('snippet', '') for r in search_results[:3]]).lower()
        
        for city, known_places in self.KNOWN_ATTRACTIONS.items():
            if city in all_text:
                for place_name in known_places[:10]:
                    attractions.append(Attraction(
                        name=place_name,
                        description=f"Must-visit attraction in {city.title()}",
                        location=city.title()
                    ))
                break
        
        return attractions
    
    def _extract_price(self, text: str) -> str:
        """Extract price information"""
        # Look for currency symbols and amounts
        patterns = [
            r'(?:IDR|Rp|₹|USD|\$|€|£)\s*[\d,]+(?:\.\d{2})?',
            r'[\d,]+\s*(?:IDR|Rp|₹|USD|dollars|rupiah)',
            r'(?:entry|admission|ticket)(?:\s+fee)?:\s*[\d,]+',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return ""
    
    def _extract_hours(self, text: str) -> str:
        """Extract opening hours"""
        patterns = [
            r'\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?\s*-\s*\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?',
            r'(?:open|hours):\s*[\d:AMP\s-]+',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return ""
    
    def _extract_rating(self, text: str) -> str:
        """Extract rating information"""
        patterns = [
            r'\d+\.?\d*\s*(?:out of|/)\s*[45](?:\s+stars?)?',
            r'\d+\.?\d*\s*stars?',
            r'rated\s+\d+\.?\d*',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return ""
    
    def _extract_cuisine(self, text: str) -> str:
        """Extract cuisine type"""
        cuisines = [
            'indonesian', 'balinese', 'italian', 'french', 'japanese', 'chinese',
            'thai', 'indian', 'mexican', 'mediterranean', 'seafood', 'vegan',
            'vegetarian', 'fusion', 'international', 'asian', 'european'
        ]
        
        text_lower = text.lower()
        for cuisine in cuisines:
            if cuisine in text_lower:
                return cuisine.title()
        
        return ""
    
    def _extract_price_range(self, text: str) -> str:
        """Extract restaurant price range ($ symbols)"""
        # Look for $ symbols
        match = re.search(r'\$+', text)
        if match:
            return match.group(0)
        
        # Look for words
        if re.search(r'\b(expensive|upscale|fine dining)\b', text, re.IGNORECASE):
            return "$$$"
        elif re.search(r'\b(moderate|mid-range)\b', text, re.IGNORECASE):
            return "$$"
        elif re.search(r'\b(cheap|budget|affordable)\b', text, re.IGNORECASE):
            return "$"
        
        return "$$"
    
    def _extract_hotel_price(self, text: str) -> str:
        """Extract hotel price per night"""
        patterns = [
            r'(?:from|starting at|from)\s*(?:IDR|Rp|₹|USD|\$|€|£)\s*[\d,]+(?:/night)?',
            r'(?:IDR|Rp|₹|USD|\$|€|£)\s*[\d,]+\s*(?:per night|/night)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return ""
    
    def _extract_amenities(self, text: str) -> List[str]:
        """Extract hotel amenities"""
        amenities = []
        amenity_keywords = [
            'pool', 'wifi', 'breakfast', 'spa', 'gym', 'parking',
            'restaurant', 'bar', 'beach', 'ocean view', 'airport shuttle'
        ]
        
        text_lower = text.lower()
        for amenity in amenity_keywords:
            if amenity in text_lower:
                amenities.append(amenity.title())
        
        return amenities[:5]


# Global parser instance
search_parser = SearchResultParser()
