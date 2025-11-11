"""Service for interacting with Ollama API."""

import httpx
from typing import List, AsyncIterator, Optional
from cerebro.models import OllamaModel
from datetime import datetime


class OllamaService:
    """Service for Ollama API interactions."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=300.0)
    
    async def list_local_models(self) -> List[OllamaModel]:
        """List locally available models."""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            data = response.json()
            
            models = []
            for model_data in data.get("models", []):
                models.append(OllamaModel(
                    name=model_data["name"],
                    size=model_data.get("size", 0),
                    digest=model_data.get("digest", ""),
                    modified_at=datetime.fromisoformat(
                        model_data.get("modified_at", datetime.now().isoformat())
                    ),
                    details=model_data.get("details")
                ))
            
            return sorted(models, key=lambda m: (m.size, m.name))
        except Exception as e:
            print(f"Error fetching local models: {e}")
            return []
    
    async def pull_model(self, model_name: str) -> AsyncIterator[dict]:
        """Pull a model from Ollama registry."""
        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/pull",
                json={"name": model_name}
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        import json
                        yield json.loads(line)
        except Exception as e:
            yield {"error": str(e)}
    
    async def delete_model(self, model_name: str) -> bool:
        """Delete a local model."""
        try:
            response = await self.client.delete(
                f"{self.base_url}/api/delete",
                json={"name": model_name}
            )
            response.raise_for_status()
            return True
        except Exception:
            return False
    
    async def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        context: Optional[List[int]] = None
    ) -> AsyncIterator[str]:
        """Generate completion from model."""
        payload = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "stream": True
        }
        
        if system:
            payload["system"] = system
        
        if context:
            payload["context"] = context
        
        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        import json
                        data = json.loads(line)
                        if "response" in data:
                            yield data["response"]
        except Exception as e:
            yield f"\n\nError: {str(e)}"
    
    async def chat(
        self,
        model: str,
        messages: List[dict],
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Chat with model using conversation history."""
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": True
        }
        
        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json=payload
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        import json
                        data = json.loads(line)
                        if "message" in data and "content" in data["message"]:
                            yield data["message"]["content"]
        except Exception as e:
            yield f"\n\nError: {str(e)}"
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()