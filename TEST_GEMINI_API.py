#!/usr/bin/env python3
"""
Test Gemini API connection
"""

import os
import google.generativeai as genai

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("⚠️ Set GEMINI_API_KEY environment variable!")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)

# Test configuration with deterministic settings
generation_config = {
    "temperature": 0.1,  # Deterministic
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 100,
    "candidate_count": 1
}

# Initialize model
model = genai.GenerativeModel(
    "gemini-2.5-flash",
    generation_config=generation_config
)

# Test prompt
prompt = "Simply respond with 'API is working' in Turkish"

try:
    response = model.generate_content(prompt)
    print(f"✅ Gemini API Test Successful!")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")