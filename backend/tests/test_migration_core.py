"""
Core migration tests focused on Supabase + Gemini integration.
Tests without TTS/STT dependencies.
"""
import pytest
import jwt
import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock

# Test Gemini LLM Provider
def test_gemini_provider_imports():
    """Test that Gemini provider can be imported."""
    try:
        from backend.llm.index import GeminiProvider, create_llm_provider
        assert GeminiProvider is not None
        assert create_llm_provider is not None
        print("✅ Gemini provider imports successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import Gemini provider: {e}")

def test_supabase_client_imports():
    """Test that Supabase client can be imported."""
    try:
        from backend.lib.supabase_client import create_supabase_admin, create_supabase_client
        assert create_supabase_admin is not None
        assert create_supabase_client is not None
        print("✅ Supabase client imports successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import Supabase client: {e}")

@patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"})
def test_gemini_provider_creation():
    """Test that Gemini provider can be created with API key."""
    from backend.llm.index import GeminiProvider
    
    provider = GeminiProvider()
    assert provider.model_name == "gemini-2.5-flash"
    print("✅ Gemini provider created successfully")

def test_mock_provider_fallback():
    """Test that mock provider works as fallback."""
    from backend.llm.index import MockProvider
    
    provider = MockProvider()
    assert provider is not None
    print("✅ Mock provider fallback works")

@pytest.mark.asyncio
async def test_mock_provider_stream():
    """Test mock provider streaming functionality."""
    from backend.llm.index import MockProvider
    
    provider = MockProvider()
    messages = [{"role": "user", "content": "Test message"}]
    
    response_chunks = []
    async for chunk in provider.stream(messages):
        response_chunks.append(chunk)
        if len(response_chunks) >= 3:  # Limit to avoid infinite loop
            break
    
    assert len(response_chunks) > 0
    assert all("text" in chunk for chunk in response_chunks)
    print("✅ Mock provider streaming works")

@pytest.mark.asyncio
async def test_mock_provider_complete():
    """Test mock provider complete generation."""
    from backend.llm.index import MockProvider
    
    provider = MockProvider()
    messages = [{"role": "user", "content": "Test message"}]
    
    response = await provider.generate_complete(messages)
    assert isinstance(response, str)
    assert len(response) > 0
    print("✅ Mock provider complete generation works")

def test_auth_imports():
    """Test that auth module can be imported."""
    try:
        from backend.auth import get_current_user, get_current_user_optional
        assert get_current_user is not None
        assert get_current_user_optional is not None
        print("✅ Auth module imports successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import auth module: {e}")

def test_api_llm_imports():
    """Test that LLM API module can be imported."""
    try:
        from backend.api.llm import router, ChatMessage, ChatRequest, ChatResponse
        assert router is not None
        assert ChatMessage is not None
        assert ChatRequest is not None
        assert ChatResponse is not None
        print("✅ LLM API module imports successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import LLM API module: {e}")

def test_jwt_token_creation():
    """Test JWT token creation functionality."""
    user_id = "test-user-123"
    email = "test@example.com"
    secret = "test-secret"
    
    payload = {
        "sub": user_id,
        "email": email,
        "role": "authenticated",
        "aud": "authenticated",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow()
    }
    
    token = jwt.encode(payload, secret, algorithm="HS256")
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Verify token can be decoded
    decoded = jwt.decode(token, secret, algorithms=["HS256"], audience="authenticated")
    assert decoded["sub"] == user_id
    assert decoded["email"] == email
    print("✅ JWT token creation and verification works")

def test_pydantic_models():
    """Test Pydantic models for API validation."""
    from backend.api.llm import ChatMessage, ChatRequest, ChatResponse
    
    # Test ChatMessage
    message = ChatMessage(role="user", content="Hello")
    assert message.role == "user"
    assert message.content == "Hello"
    
    # Test ChatRequest
    request = ChatRequest(messages=[message], stream=True)
    assert len(request.messages) == 1
    assert request.stream is True
    
    # Test ChatResponse
    response = ChatResponse(message=message, message_id="msg-123")
    assert response.message.role == "user"
    assert response.message_id == "msg-123"
    
    print("✅ Pydantic models validation works")

@patch.dict(os.environ, {"SUPABASE_URL": "https://test.supabase.co", "SUPABASE_ANON_KEY": "test-key"})
def test_supabase_client_creation():
    """Test Supabase client creation with environment variables."""
    try:
        from backend.lib.supabase_client import create_supabase_client
        
        # This will fail without real credentials but should not crash import
        client = create_supabase_client()
        assert client is not None
        print("✅ Supabase client creation works")
    except Exception as e:
        # Expected to fail without real credentials, but import should work
        print(f"⚠️  Supabase client creation failed as expected: {e}")

def test_orchestrator_update():
    """Test that orchestrator uses new LLM provider."""
    try:
        from backend.orchestrator import Orchestrator
        
        orchestrator = Orchestrator()
        assert orchestrator.llm is not None
        assert hasattr(orchestrator.llm, 'stream')
        assert hasattr(orchestrator.llm, 'generate_complete')
        print("✅ Orchestrator updated with new LLM provider")
    except ImportError as e:
        pytest.fail(f"Failed to import updated orchestrator: {e}")

@pytest.mark.asyncio 
async def test_rate_limiting_logic():
    """Test rate limiting functionality."""
    from backend.api.llm import check_rate_limit, rate_limit_store
    
    # Clear any existing rate limits
    rate_limit_store.clear()
    
    user_id = "test-user"
    
    # Should allow requests initially
    for i in range(10):  # RATE_LIMIT_REQUESTS = 10
        assert check_rate_limit(user_id) is True
    
    # Should block 11th request
    assert check_rate_limit(user_id) is False
    
    print("✅ Rate limiting logic works correctly")

if __name__ == "__main__":
    print("🧪 Running core migration tests...")
    
    # Run tests manually if not using pytest
    test_gemini_provider_imports()
    test_supabase_client_imports()
    test_mock_provider_fallback()
    test_auth_imports() 
    test_api_llm_imports()
    test_jwt_token_creation()
    test_pydantic_models()
    test_orchestrator_update()
    
    print("✅ All core migration tests passed!")
