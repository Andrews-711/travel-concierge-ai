"""
LLM client supporting both Ollama and Google Gemini
"""
import httpx
from typing import Optional, Dict, Any
import time

from app.config import get_settings

settings = get_settings()


class LLMClient:
    """Multi-provider LLM client (Ollama + Gemini)"""
    
    def __init__(self):
        self.ollama_url = settings.OLLAMA_BASE_URL
        self.ollama_model = settings.OLLAMA_MODEL
        self.gemini_key = settings.GEMINI_API_KEY
        self.timeout = 60.0
        
        # Determine which provider to use
        self.use_gemini = bool(self.gemini_key)
    
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        system: Optional[str] = None
    ) -> str:
        """
        Generate response from LLM
        
        Args:
            prompt: User prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            system: System message
        
        Returns:
            Generated text
        """
        if self.use_gemini:
            return await self._generate_gemini(prompt, max_tokens, temperature, system)
        else:
            return await self._generate_ollama(prompt, max_tokens, temperature, system)
    
    async def _generate_ollama(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        system: Optional[str]
    ) -> str:
        """Generate using Ollama"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": temperature
                    }
                }
                
                if system:
                    payload["system"] = system
                
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("response", "").strip()
                else:
                    return self._fallback_response()
                    
        except Exception as e:
            print(f"Ollama error: {e}")
            return self._fallback_response()
    
    async def _generate_gemini(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        system: Optional[str]
    ) -> str:
        """Generate using Google Gemini"""
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Use gemini-2.0-flash-exp
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={self.gemini_key}"
                
                # Combine system and prompt
                full_prompt = f"{system}\n\n{prompt}" if system else prompt
                
                payload = {
                    "contents": [{
                        "parts": [{
                            "text": full_prompt
                        }]
                    }],
                    "generationConfig": {
                        "temperature": temperature,
                        "maxOutputTokens": max_tokens,
                        "candidateCount": 1
                    }
                }
                
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                    
                    # Log token usage and track metrics
                    usage = data.get("usageMetadata", {})
                    prompt_tokens = usage.get("promptTokenCount", 0)
                    completion_tokens = usage.get("candidatesTokenCount", 0)
                    total_tokens = usage.get("totalTokenCount", 0)
                    
                    duration = time.time() - start_time
                    
                    if total_tokens > 0:
                        print(f"Token usage: {prompt_tokens} prompt + {completion_tokens} completion = {total_tokens} total")
                        print(f"LLM call duration: {duration:.2f}s")
                        
                        # Record metrics
                        try:
                            from app.observability import metrics
                            metrics.record_llm_call("gemini-2.0-flash-exp", total_tokens, duration)
                        except:
                            pass  # Ignore if observability not available
                    
                    if not text:
                        print(f"Gemini returned empty text. Full response: {data}")
                    
                    return text
                else:
                    print(f"Gemini error: {response.status_code} - {response.text[:500]}")
                    return ""
                    
        except Exception as e:
            print(f"Gemini exception: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    async def chat(
        self,
        messages: list,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """
        Chat completion with conversation history
        
        Args:
            messages: List of {"role": "user/assistant", "content": "..."}
            max_tokens: Max tokens
            temperature: Sampling temperature
        
        Returns:
            Assistant response
        """
        # Convert to single prompt for now
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        return await self.generate(prompt, max_tokens, temperature)
    
    async def is_healthy(self) -> bool:
        """Check if LLM service is available"""
        if self.use_gemini:
            return True  # Gemini API is always available with key
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.ollama_url}/api/tags")
                return response.status_code == 200
        except:
            return False
    
    def _fallback_response(self) -> str:
        """Fallback when LLM is unavailable"""
        return ("I apologize, but I'm currently unable to process your request. "
                "The AI service may be temporarily unavailable. Please try again in a moment.")


# Global LLM client
llm = LLMClient()
