"""
LLM Provider abstraction layer.
Single entry point for all LLM operations.
"""
import os
import asyncio
import json
from typing import AsyncIterator, Dict, List, Any, Optional
import logging
from abc import ABC, abstractmethod

import google.generativeai as genai
from google.generativeai.types import GenerateContentResponse
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def stream(self, messages: List[Dict]) -> AsyncIterator[Dict[str, str]]:
        """Stream LLM responses."""
        pass
    
    @abstractmethod
    async def generate_complete(self, messages: List[Dict]) -> str:
        """Generate complete response (non-streaming)."""
        pass


class GeminiProvider(LLMProvider):
    """Google Gemini 2.5 Flash provider with streaming support."""
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.model_name = model_name
        self._initialized = False
        self.model = None
        
        # Configure Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable must be set")
        
        genai.configure(api_key=api_key)
        
    async def _initialize(self):
        """Initialize the Gemini model."""
        if self._initialized:
            return
            
        try:
            self.model = genai.GenerativeModel(self.model_name)
            self._initialized = True
            logger.info(f"Gemini model {self.model_name} initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            raise
    
    def _format_messages_for_gemini(self, messages: List[Dict]) -> List[Dict]:
        """Format messages for Gemini API."""
        formatted = []
        
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            # Gemini uses "user" and "model" roles
            if role == "system":
                # Prepend system message to user content
                if formatted and formatted[-1]["role"] == "user":
                    formatted[-1]["parts"][0]["text"] = f"{content}\n\n{formatted[-1]['parts'][0]['text']}"
                else:
                    formatted.append({
                        "role": "user",
                        "parts": [{"text": content}]
                    })
            elif role == "user":
                formatted.append({
                    "role": "user", 
                    "parts": [{"text": content}]
                })
            elif role == "assistant":
                formatted.append({
                    "role": "model",
                    "parts": [{"text": content}]
                })
        
        return formatted
    
    async def stream(self, messages: List[Dict]) -> AsyncIterator[Dict[str, str]]:
        """Stream responses from Gemini."""
        await self._initialize()
        
        try:
            formatted_messages = self._format_messages_for_gemini(messages)
            
            # Use async streaming
            response = await self.model.generate_content_async(
                contents=formatted_messages,
                stream=True,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 1024,
                }
            )
            
            async for chunk in response:
                if chunk.text:
                    yield {"text": chunk.text}
                    
        except Exception as e:
            logger.error(f"Gemini streaming error: {e}")
            yield {"text": "Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin."}
    
    async def generate_complete(self, messages: List[Dict]) -> str:
        """Generate complete response from Gemini."""
        await self._initialize()
        
        try:
            formatted_messages = self._format_messages_for_gemini(messages)
            
            response = await self.model.generate_content_async(
                contents=formatted_messages,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 1024,
                }
            )
            
            return response.text if response.text else "Üzgünüm, yanıt oluşturulamadı."
            
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            return "Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin."


class MockProvider(LLMProvider):
    """Mock provider for testing and fallback."""
    
    async def stream(self, messages: List[Dict]) -> AsyncIterator[Dict[str, str]]:
        """Mock streaming responses."""
        mock_responses = [
            "Merhaba! Size nasıl yardımcı olabilirim?",
            "eSIM ile ilgili sorularınızı yanıtlayabilirim.",
            "Lütfen kimlik doğrulama bilgilerinizi paylaşın."
        ]
        
        import random
        response = random.choice(mock_responses)
        
        # Stream word by word
        words = response.split()
        for word in words:
            await asyncio.sleep(0.1)  # Simulate streaming delay
            yield {"text": word + " "}
    
    async def generate_complete(self, messages: List[Dict]) -> str:
        """Mock complete response."""
        return "Merhaba! Size nasıl yardımcı olabilirim?"


# Factory function to create appropriate provider
def create_llm_provider() -> LLMProvider:
    """Create LLM provider based on environment configuration."""
    provider_type = os.getenv("LLM_PROVIDER", "gemini").lower()
    
    if provider_type == "gemini":
        try:
            return GeminiProvider()
        except Exception as e:
            logger.warning(f"Failed to create Gemini provider: {e}, falling back to mock")
            return MockProvider()
    elif provider_type == "mock":
        return MockProvider()
    else:
        logger.warning(f"Unknown provider type: {provider_type}, using mock")
        return MockProvider()


# Default provider instance
default_provider = create_llm_provider()
