"""
Tests for authentication and LLM endpoints.
"""
import pytest
import jwt
import os
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from backend.app import app

client = TestClient(app)

# Test data
TEST_USER_ID = "550e8400-e29b-41d4-a716-446655440000"
TEST_EMAIL = "test@example.com"
JWT_SECRET = "test-jwt-secret"

def create_test_jwt(user_id: str = TEST_USER_ID, email: str = TEST_EMAIL, expired: bool = False) -> str:
    """Create a test JWT token."""
    exp = datetime.utcnow() + (timedelta(hours=-1) if expired else timedelta(hours=1))
    payload = {
        "sub": user_id,
        "email": email,
        "role": "authenticated",
        "aud": "authenticated",
        "exp": exp,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

class TestAuthentication:
    """Test authentication middleware and endpoints."""
    
    @patch.dict(os.environ, {"SUPABASE_JWT_SECRET": JWT_SECRET})
    @patch("backend.auth.supabase_admin")
    def test_valid_jwt_token(self, mock_supabase):
        """Test that valid JWT tokens are accepted."""
        # Mock Supabase response
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"id": TEST_USER_ID, "email": TEST_EMAIL}]
        )
        
        token = create_test_jwt()
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/llm/messages", headers=headers)
        assert response.status_code == 200

    def test_missing_authorization_header(self):
        """Test that requests without authorization header are rejected."""
        response = client.get("/api/llm/messages")
        assert response.status_code == 401
        assert "Authorization header missing" in response.json()["detail"]

    def test_invalid_authorization_format(self):
        """Test that invalid authorization header format is rejected."""
        headers = {"Authorization": "InvalidFormat token"}
        response = client.get("/api/llm/messages", headers=headers)
        assert response.status_code == 401
        assert "Invalid authorization header format" in response.json()["detail"]

    @patch.dict(os.environ, {"SUPABASE_JWT_SECRET": JWT_SECRET})
    def test_expired_jwt_token(self):
        """Test that expired JWT tokens are rejected."""
        token = create_test_jwt(expired=True)
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/llm/messages", headers=headers)
        assert response.status_code == 401
        assert "Token expired" in response.json()["detail"]

    @patch.dict(os.environ, {"SUPABASE_JWT_SECRET": JWT_SECRET})
    @patch("backend.auth.supabase_admin")
    def test_user_not_found_in_database(self, mock_supabase):
        """Test that tokens for non-existent users are rejected."""
        # Mock empty Supabase response
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[]
        )
        
        token = create_test_jwt()
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/llm/messages", headers=headers)
        assert response.status_code == 401
        assert "User not found" in response.json()["detail"]

class TestLLMEndpoints:
    """Test LLM API endpoints."""
    
    @patch.dict(os.environ, {"SUPABASE_JWT_SECRET": JWT_SECRET})
    @patch("backend.auth.supabase_admin")
    @patch("backend.api.llm.llm_provider")
    @patch("backend.api.llm.supabase_admin")
    def test_chat_endpoint_success(self, mock_llm_supabase, mock_llm_provider, mock_auth_supabase):
        """Test successful chat request."""
        # Mock authentication
        mock_auth_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"id": TEST_USER_ID, "email": TEST_EMAIL}]
        )
        
        # Mock LLM provider
        mock_llm_provider.generate_complete.return_value = "Merhaba! Size nasıl yardımcı olabilirim?"
        
        # Mock message storage
        mock_llm_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[{"id": "msg-123"}]
        )
        
        token = create_test_jwt()
        headers = {"Authorization": f"Bearer {token}"}
        
        payload = {
            "messages": [
                {"role": "user", "content": "Merhaba"}
            ],
            "stream": False
        }
        
        response = client.post("/api/llm/chat", json=payload, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"]["role"] == "assistant"
        assert "message_id" in data

    @patch.dict(os.environ, {"SUPABASE_JWT_SECRET": JWT_SECRET})
    @patch("backend.auth.supabase_admin")
    def test_chat_endpoint_rate_limiting(self, mock_supabase):
        """Test rate limiting functionality."""
        # Mock authentication
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"id": TEST_USER_ID, "email": TEST_EMAIL}]
        )
        
        token = create_test_jwt()
        headers = {"Authorization": f"Bearer {token}"}
        
        payload = {
            "messages": [{"role": "user", "content": "test"}],
            "stream": False
        }
        
        # Clear rate limit store
        from backend.api.llm import rate_limit_store
        rate_limit_store.clear()
        
        # Make requests up to the limit
        from backend.api.llm import RATE_LIMIT_REQUESTS
        for i in range(RATE_LIMIT_REQUESTS):
            response = client.post("/api/llm/chat", json=payload, headers=headers)
            # Should succeed up to the limit (may fail on LLM provider, but not on rate limiting)
            assert response.status_code in [200, 500]  # 500 might be from mock LLM provider
        
        # Next request should be rate limited
        response = client.post("/api/llm/chat", json=payload, headers=headers)
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]

    @patch.dict(os.environ, {"SUPABASE_JWT_SECRET": JWT_SECRET})
    @patch("backend.auth.supabase_admin")
    @patch("backend.api.llm.supabase_admin")
    def test_get_messages_endpoint(self, mock_llm_supabase, mock_auth_supabase):
        """Test getting user messages."""
        # Mock authentication
        mock_auth_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"id": TEST_USER_ID, "email": TEST_EMAIL}]
        )
        
        # Mock message retrieval
        mock_messages = [
            {"id": "msg-1", "role": "user", "content": {"text": "Hello"}, "created_at": "2024-01-01T00:00:00Z"},
            {"id": "msg-2", "role": "assistant", "content": {"text": "Hi there!"}, "created_at": "2024-01-01T00:00:01Z"}
        ]
        mock_llm_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
            data=mock_messages
        )
        
        token = create_test_jwt()
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/llm/messages", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "messages" in data
        assert len(data["messages"]) == 2

class TestRLSPolicies:
    """Test Row Level Security policies (requires actual Supabase connection)."""
    
    def test_rls_enabled_on_tables(self):
        """Test that RLS is enabled on critical tables."""
        # This would require actual database connection
        # For now, we check that our migration SQL includes RLS statements
        with open("supabase/migrations/20240112000001_init_profiles_and_messages.sql", "r") as f:
            migration_sql = f.read()
        
        assert "ENABLE ROW LEVEL SECURITY" in migration_sql
        assert "CREATE POLICY" in migration_sql
        assert "auth.uid()" in migration_sql

    def test_user_isolation_in_policies(self):
        """Test that RLS policies ensure user data isolation."""
        with open("supabase/migrations/20240112000001_init_profiles_and_messages.sql", "r") as f:
            migration_sql = f.read()
        
        # Check that policies reference auth.uid() for user isolation
        assert "auth.uid() = id" in migration_sql  # profiles table
        assert "auth.uid() = user_id" in migration_sql  # messages table

if __name__ == "__main__":
    pytest.main([__file__])
