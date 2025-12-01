"""
Test LLM directly to see response format
"""
import asyncio
from app.llm import llm


async def test_llm():
    print("Testing LLM directly\n")
    
    prompt = """List 5 popular tourist attractions in Bali.
For each attraction, provide:
- Exact name
- Brief description

Respond with ONLY valid JSON, no markdown:
{
    "places": [
        {
            "name": "Attraction Name",
            "description": "Brief description"
        }
    ]
}"""

    response = await llm.generate(
        prompt=prompt,
        system="You are a travel expert. Provide accurate information.",
        max_tokens=1000,
        temperature=0.3
    )
    
    print("=== RAW LLM RESPONSE ===")
    print(response)
    print(f"\nResponse length: {len(response)}")
    print(f"Response type: {type(response)}")


if __name__ == "__main__":
    asyncio.run(test_llm())
