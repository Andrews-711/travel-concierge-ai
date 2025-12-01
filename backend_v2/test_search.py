"""
Test LLM-based search functionality
"""
import asyncio
import sys
import traceback
from app.llm_search import llm_search


async def test_search():
    print("Testing LLM-Based Search\n")
    
    # Test attractions
    print("=== Testing Attractions Search ===")
    try:
        attractions = await llm_search.search_attractions("Bali")
        print(f"Found {len(attractions.get('places', []))} attractions")
        for i, place in enumerate(attractions.get('places', [])[:8], 1):
            print(f"{i}. {place['name']} - {place.get('description', '')[:60]}")
    except Exception as e:
        print(f"Error testing attractions: {e}")
        traceback.print_exc()
    
    # Test restaurants
    print("\n=== Testing Restaurants Search ===")
    try:
        restaurants = await llm_search.search_restaurants("Bali")
        print(f"Found {len(restaurants.get('places', []))} restaurants")
        for i, place in enumerate(restaurants.get('places', [])[:8], 1):
            print(f"{i}. {place['name']} - {place.get('description', '')[:60]}")
    except Exception as e:
        print(f"Error testing restaurants: {e}")
        traceback.print_exc()
    
    # Test hotels
    print("\n=== Testing Hotels Search ===")
    try:
        hotels = await llm_search.search_hotels("Bali")
        print(f"Found {len(hotels.get('places', []))} hotels")
        for i, place in enumerate(hotels.get('places', [])[:8], 1):
            print(f"{i}. {place['name']} - {place.get('price', '')}")
    except Exception as e:
        print(f"Error testing hotels: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_search())
