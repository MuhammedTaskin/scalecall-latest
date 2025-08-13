"""
Supabase authentication utilities for FastAPI.
"""
import os
import sys
from typing import Dict, Optional
import jwt
from fastapi import HTTPException, Header, Depends

sys.path.append(os.path.dirname(__file__))
from lib.supabase_client import supabase_admin

async def get_current_user(authorization: str = Header(None)) -> Dict:
    """
    Extract and validate user from Supabase JWT token.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    token = authorization.split(" ")[1]
    
    try:
        # Decode JWT token using Supabase JWT secret
        jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
        if not jwt_secret:
            raise HTTPException(status_code=500, detail="JWT secret not configured")
        
        # Decode and verify the token
        payload = jwt.decode(
            token, 
            jwt_secret, 
            algorithms=["HS256"],
            audience="authenticated"
        )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing user ID")
        
        # Optionally verify user exists in database (if Supabase is available)
        if supabase_admin:
            user_result = supabase_admin.table("profiles").select("*").eq("id", user_id).execute()
            
            if not user_result.data:
                raise HTTPException(status_code=401, detail="User not found")
        
        return {
            "id": user_id,
            "email": payload.get("email"),
            "role": payload.get("role", "authenticated")
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")

async def get_current_user_optional(authorization: str = Header(None)) -> Optional[Dict]:
    """
    Optional authentication - returns None if no valid token provided.
    """
    try:
        return await get_current_user(authorization)
    except HTTPException:
        return None
