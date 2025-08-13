"""
Secure LLM API endpoints with Supabase authentication.
"""
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from starlette.responses import StreamingResponse

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from llm.index import default_provider as llm_provider
from lib.supabase_client import supabase_admin
from auth import get_current_user

# Request/Response models
class ChatMessage(BaseModel):
    role: str = Field(..., description="Message role: user, assistant, or system")
    content: str = Field(..., description="Message content")

class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="Conversation messages")
    stream: bool = Field(default=True, description="Whether to stream the response")

class ChatResponse(BaseModel):
    message: ChatMessage
    message_id: str

# Rate limiting (simple in-memory implementation)
from collections import defaultdict
from time import time

rate_limit_store = defaultdict(list)
RATE_LIMIT_REQUESTS = 10  # requests per minute
RATE_LIMIT_WINDOW = 60  # seconds

def check_rate_limit(user_id: str) -> bool:
    """Simple rate limiting check."""
    now = time()
    user_requests = rate_limit_store[user_id]
    
    # Remove old requests outside the window
    rate_limit_store[user_id] = [req_time for req_time in user_requests if now - req_time < RATE_LIMIT_WINDOW]
    
    # Check if under limit
    if len(rate_limit_store[user_id]) >= RATE_LIMIT_REQUESTS:
        return False
    
    # Add current request
    rate_limit_store[user_id].append(now)
    return True

# Router
router = APIRouter(prefix="/api/llm", tags=["llm"])

@router.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Secure LLM chat endpoint with authentication and rate limiting.
    """
    user_id = current_user["id"]
    
    # Check rate limit
    if not check_rate_limit(user_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Convert Pydantic models to dicts for LLM provider
    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
    
    if request.stream:
        return StreamingResponse(
            stream_llm_response(messages, user_id),
            media_type="text/plain"
        )
    else:
        # Non-streaming response
        try:
            response_text = await llm_provider.generate_complete(messages)
            
            # Store in database
            message_id = await store_message(user_id, "assistant", response_text)
            
            return ChatResponse(
                message=ChatMessage(role="assistant", content=response_text),
                message_id=message_id
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"LLM generation failed: {str(e)}")

async def stream_llm_response(messages: List[Dict], user_id: str):
    """Stream LLM response with Server-Sent Events format."""
    accumulated_text = ""
    
    try:
        async for chunk in llm_provider.stream(messages):
            text = chunk.get("text", "")
            if text:
                accumulated_text += text
                
                # Send SSE formatted chunk
                yield f"data: {json.dumps({'text': text, 'type': 'delta'})}\n\n"
                
                # Small delay to prevent overwhelming the client
                await asyncio.sleep(0.01)
        
        # Store complete message in database
        if accumulated_text.strip():
            message_id = await store_message(user_id, "assistant", accumulated_text.strip())
            yield f"data: {json.dumps({'message_id': message_id, 'type': 'complete'})}\n\n"
        
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
        
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e), 'type': 'error'})}\n\n"

async def store_message(user_id: str, role: str, content: str) -> str:
    """Store message in Supabase database."""
    if not supabase_admin:
        # Log warning if Supabase is not available
        import logging
        logging.warning("Supabase not available, message not stored")
        return "mock-message-id"
    
    try:
        result = supabase_admin.table("messages").insert({
            "user_id": user_id,
            "role": role,
            "content": {"text": content},
        }).execute()
        
        return result.data[0]["id"] if result.data else ""
    except Exception as e:
        # Log error but don't fail the request
        import logging
        logging.error(f"Failed to store message: {e}")
        return ""

@router.get("/messages")
async def get_messages(
    limit: int = 50,
    current_user: Dict = Depends(get_current_user)
):
    """Get user's conversation history."""
    user_id = current_user["id"]
    
    if not supabase_admin:
        return {"messages": []}
    
    try:
        result = supabase_admin.table("messages").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
        
        return {"messages": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch messages: {str(e)}")

@router.delete("/messages")
async def clear_messages(
    current_user: Dict = Depends(get_current_user)
):
    """Clear user's conversation history."""
    user_id = current_user["id"]
    
    if not supabase_admin:
        return {"deleted_count": 0}
    
    try:
        result = supabase_admin.table("messages").delete().eq("user_id", user_id).execute()
        
        return {"deleted_count": len(result.data) if result.data else 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear messages: {str(e)}")
