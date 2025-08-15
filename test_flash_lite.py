#!/usr/bin/env python3
"""Test Gemini 2.5 Flash Lite availability"""

import google.generativeai as genai

# Configure
genai.configure(api_key="AIzaSyBzC3ydAP1qKkGyRkJ9t1sp5D3QN9QyzsQ")

# Try Flash-Lite
try:
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
    response = model.generate_content("Say 'Flash-Lite works!' in 3 words")
    print("✅ Flash-Lite:", response.text)
except Exception as e:
    print("❌ Flash-Lite error:", str(e))

# Test regular Flash for comparison
try:
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content("Say 'Flash works!' in 3 words")
    print("✅ Flash:", response.text)
except Exception as e:
    print("❌ Flash error:", str(e))

# List available models
print("\nAvailable models:")
for m in genai.list_models():
    if '2.5' in m.name or 'flash' in m.name.lower():
        print(f"  - {m.name}")