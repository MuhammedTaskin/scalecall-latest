"""
Provider-neutral LLM wrapper with MLX Gemma-3 4B support.
"""
import asyncio
from typing import AsyncIterator, Dict, List, Any
import logging

try:
    import mlx.core as mx
    from mlx_lm import load, generate, stream_generate
    MLX_AVAILABLE = True
except ImportError:
    MLX_AVAILABLE = False

logger = logging.getLogger(__name__)


class LLMProvider:
    """Provider-neutral LLM interface with streaming support."""
    
    def __init__(self, model_name: str = "mlx-community/gemma-2-2b-it-4bit"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self._initialized = False
        
    async def _initialize(self):
        """Initialize the MLX model."""
        if self._initialized:
            return
            
        if not MLX_AVAILABLE:
            logger.warning("MLX not available, using mock responses")
            self._initialized = True
            return
            
        try:
            logger.info(f"Loading model {self.model_name}...")
            # Run model loading in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            self.model, self.tokenizer = await loop.run_in_executor(
                None, load, self.model_name
            )
            self._initialized = True
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self._initialized = True  # Continue with mock responses
    
    async def stream(self, messages: List[Dict]) -> AsyncIterator[Dict[str, str]]:
        """Stream LLM response tokens."""
        await self._initialize()
        
        # Convert messages to prompt format
        prompt = self._format_messages(messages)
        
        if not MLX_AVAILABLE or self.model is None:
            # Mock streaming response for development
            mock_response = "Merhaba! Size nasıl yardımcı olabilirim? Öncelikle kimlik doğrulaması yapalım."
            for i, char in enumerate(mock_response):
                await asyncio.sleep(0.05)  # Simulate streaming delay
                yield {"text": char}
            return
        
        try:
            # Stream generation in thread pool
            loop = asyncio.get_event_loop()
            
            async def generate_async():
                for token in stream_generate(
                    self.model,
                    self.tokenizer,
                    prompt,
                    max_tokens=512,
                    temp=0.7,
                    verbose=False
                ):
                    yield {"text": token}
            
            async for chunk in generate_async():
                yield chunk
                
        except Exception as e:
            logger.error(f"Generation error: {e}")
            yield {"text": "Üzgünüm, teknik bir sorun yaşıyorum."}
    
    def _format_messages(self, messages: List[Dict]) -> str:
        """Format messages for Gemma prompt template."""
        formatted = ""
        
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "system":
                formatted += f"<system>\n{content}\n</system>\n\n"
            elif role == "user":
                formatted += f"<user>\n{content}\n</user>\n\n"
            elif role == "assistant":
                formatted += f"<assistant>\n{content}\n</assistant>\n\n"
        
        # Add assistant prompt
        formatted += "<assistant>\n"
        
        return formatted
    
    async def generate_complete(self, messages: List[Dict]) -> str:
        """Generate complete response (non-streaming)."""
        await self._initialize()
        
        prompt = self._format_messages(messages)
        
        if not MLX_AVAILABLE or self.model is None:
            return "Merhaba! Size nasıl yardımcı olabilirim?"
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: generate(
                    self.model,
                    self.tokenizer,
                    prompt,
                    max_tokens=512,
                    temp=0.7,
                    verbose=False
                )
            )
            return response
            
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return "Üzgünüm, teknik bir sorun yaşıyorum."
