#!/usr/bin/env python3
"""
Quick test for deterministic generation
"""

import json
import os
from pathlib import Path
import google.generativeai as genai

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("⚠️ No API key!")
    exit(1)

print("🔑 API Key found")
genai.configure(api_key=GEMINI_API_KEY)

# Ultra deterministic config
generation_config = {
    "temperature": 0.1,
    "top_p": 0.9,
    "top_k": 20,
    "max_output_tokens": 1000,
    "candidate_count": 1
}

print("⚙️ Initializing model...")
model = genai.GenerativeModel(
    "gemini-2.5-flash",
    generation_config=generation_config
)

# Simple test prompt
prompt = """Generate a Turkish telco agent response in JSON format.

Customer says: "eSIM'im çalışmıyor, yardım eder misiniz?"

Return ONLY this JSON:
{
    "agent": "TechAgent",
    "response": "Turkish response here",
    "tools": ["check_esim_status"]
}"""

print("📡 Generating response...")
try:
    response = model.generate_content(prompt)
    print("✅ Response received!")
    print(response.text)
    
    # Try to parse
    result = json.loads(response.text.strip().replace("```json", "").replace("```", ""))
    print("\n✅ Parsed successfully!")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
except Exception as e:
    print(f"❌ Error: {e}")