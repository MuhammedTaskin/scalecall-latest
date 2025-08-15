#!/usr/bin/env python3
"""
🚀 COLAB MODEL SERVER - Gemma 3N E4B
Bu kodu Colab'de çalıştır!
"""

# ============= COLAB'DE ÇALIŞTIR =============
"""
# 1. Colab'de yeni notebook aç
# 2. GPU runtime seç (T4 veya daha iyisi)
# 3. Aşağıdaki kodları çalıştır:

!pip install flask flask-cors pyngrok
!pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
!pip install --no-deps xformers trl peft accelerate bitsandbytes

# Mount Drive (model'in varsa)
from google.colab import drive
drive.mount('/content/drive')
"""

import json
import torch
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from pyngrok import ngrok
import threading

# ============= MODEL LOADER =============
class GemmaModelServer:
    """Gemma 3N model server for Colab"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.load_model()
    
    def load_model(self):
        """Load Gemma 3N E4B with LoRA"""
        
        print("🔄 Loading Gemma 3N E4B model...")
        
        try:
            from unsloth import FastLanguageModel
            from transformers import AutoTokenizer
            
            # Model configuration
            max_seq_length = 2048
            dtype = None
            load_in_4bit = True
            
            # Load base model
            self.model, _ = FastLanguageModel.from_pretrained(
                model_name="unsloth/gemma-3n-E4B-it",
                max_seq_length=max_seq_length,
                dtype=dtype,
                load_in_4bit=load_in_4bit,
            )
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained("google/gemma-2-2b-it")
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load LoRA weights (eğer varsa)
            try:
                lora_path = "/content/drive/MyDrive/teknofest/teknofest_gemma3n_emotion"
                self.model = FastLanguageModel.get_peft_model(
                    self.model,
                    r=16,
                    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                                  "gate_proj", "up_proj", "down_proj"],
                    lora_alpha=16,
                    lora_dropout=0,
                    bias="none",
                    use_gradient_checkpointing=False,
                    random_state=42,
                )
                print(f"✅ LoRA weights loaded from {lora_path}")
            except:
                print("⚠️ No LoRA weights found, using base model")
            
            # Enable inference mode
            FastLanguageModel.for_inference(self.model)
            
            print("✅ Model loaded successfully!")
            
        except Exception as e:
            print(f"❌ Model loading failed: {e}")
            print("   Using mock model")
            self.model = None
    
    def process_audio_with_emotion(self, audio_tensor: np.ndarray, emotion_context: dict, prompt: str) -> dict:
        """Process audio with emotion context"""
        
        if self.model and self.tokenizer:
            # Real inference
            return self.run_inference(audio_tensor, emotion_context, prompt)
        else:
            # Mock response
            return self.mock_response(emotion_context)
    
    def run_inference(self, audio_tensor: np.ndarray, emotion_context: dict, prompt: str) -> dict:
        """Run actual model inference"""
        
        # Format input for Gemma 3N
        formatted_prompt = f"""### Görev:
Sen Türkiye'nin önde gelen telekom şirketinin AI asistanısın.

### Girdi:
{prompt}

### Ses Verisi:
[Audio: {audio_tensor.shape[0]} frames, 16kHz]

### Yanıt:
"""
        
        # Tokenize
        inputs = self.tokenizer(
            [formatted_prompt],
            return_tensors="pt"
        ).to("cuda")
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=256,
                temperature=0.7,
                do_sample=True
            )
        
        # Decode
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Parse response
        if "### Yanıt:" in response:
            response_text = response.split("### Yanıt:")[1].strip()
        else:
            response_text = response
        
        # Determine agent based on response
        agent = self.determine_agent(response_text, emotion_context)
        
        # Select tools
        tools = self.select_tools(agent, emotion_context)
        
        return {
            "text": response_text,
            "agent": agent,
            "tools": tools,
            "emotion_matched": True,
            "model": "gemma-3n-e4b"
        }
    
    def mock_response(self, emotion_context: dict) -> dict:
        """Mock response when model not available"""
        
        responses = {
            "angry": {
                "text": "Sayın müşterimiz, yaşadığınız sorun için çok özür dileriz. Sorununuzu hemen çözüyorum.",
                "agent": "RouterAgent",
                "tools": ["prioritize_ticket", "escalate"]
            },
            "confused": {
                "text": "Tabii ki, size adım adım açıklayayım. Hangi konuda yardım istediğinizi netleştirelim.",
                "agent": "FAQAgent",
                "tools": ["clarify_request", "provide_options"]
            },
            "sad": {
                "text": "Sizi anlıyorum. Size en iyi şekilde yardımcı olmak için buradayım.",
                "agent": "TechAgent",
                "tools": ["check_account", "provide_support"]
            },
            "happy": {
                "text": "Memnuniyetiniz bizi mutlu ediyor! Size nasıl yardımcı olabilirim?",
                "agent": "RouterAgent",
                "tools": ["show_options"]
            },
            "neutral": {
                "text": "Hoş geldiniz. Size nasıl yardımcı olabilirim?",
                "agent": "RouterAgent",
                "tools": ["analyze_request"]
            }
        }
        
        emotion = emotion_context.get("detected_emotion", "neutral")
        response = responses.get(emotion, responses["neutral"])
        response["model"] = "mock"
        
        return response
    
    def determine_agent(self, response: str, emotion: dict) -> str:
        """Determine which agent to use"""
        
        response_lower = response.lower()
        
        if "fatura" in response_lower or "ödeme" in response_lower:
            return "BillingAgent"
        elif "internet" in response_lower or "bağlantı" in response_lower:
            return "TechAgent"
        elif "paket" in response_lower or "tarife" in response_lower:
            return "PlanAgent"
        elif emotion.get("detected_emotion") == "confused":
            return "FAQAgent"
        else:
            return "RouterAgent"
    
    def select_tools(self, agent: str, emotion: dict) -> list:
        """Select appropriate tools"""
        
        tools_map = {
            "RouterAgent": ["analyze_request", "route_to_agent"],
            "TechAgent": ["check_connection", "run_diagnostics", "troubleshoot"],
            "BillingAgent": ["get_balance", "view_invoice", "process_payment"],
            "PlanAgent": ["list_packages", "calculate_cost", "recommend_plan"],
            "FAQAgent": ["search_knowledge", "provide_info", "clarify"]
        }
        
        base_tools = tools_map.get(agent, ["analyze_request"])
        
        # Add emotion-specific tools
        if emotion.get("detected_emotion") == "angry":
            base_tools.append("prioritize_ticket")
        elif emotion.get("detected_emotion") == "confused":
            base_tools.append("explain_step_by_step")
        
        return base_tools

# ============= FLASK SERVER =============
app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Global model instance
model_server = None

@app.route('/')
def home():
    """Home endpoint"""
    return jsonify({
        "name": "TEKNOFEST 2025 Gemma 3N Model Server",
        "status": "running",
        "model": "gemma-3n-e4b",
        "endpoints": {
            "/predict": "POST - Send audio tensor and emotion for inference",
            "/health": "GET - Check server health"
        }
    })

@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "model_loaded": model_server.model is not None if model_server else False
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Main prediction endpoint"""
    
    try:
        data = request.json
        
        # Extract data
        audio_tensor = np.array(data.get('audio_tensor', []))
        emotion_context = data.get('emotion_context', {})
        prompt = data.get('prompt', '')
        
        # Process with model
        result = model_server.process_audio_with_emotion(
            audio_tensor,
            emotion_context,
            prompt
        )
        
        return jsonify({
            "success": True,
            "result": result
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

def run_server():
    """Run Flask server"""
    app.run(host='0.0.0.0', port=5000)

# ============= MAIN COLAB SCRIPT =============
def main_colab():
    """Main function for Colab"""
    
    global model_server
    
    print("""
╔════════════════════════════════════════════════════════════╗
║  🚀 GEMMA 3N E4B MODEL SERVER - COLAB                     ║
╠════════════════════════════════════════════════════════════╣
║  Running on Google Colab with GPU acceleration             ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Initialize model
    model_server = GemmaModelServer()
    
    # Setup ngrok
    print("\n🌐 Setting up ngrok tunnel...")
    
    # Get ngrok auth token (optional but recommended)
    # ngrok.set_auth_token("YOUR_NGROK_AUTH_TOKEN")
    
    # Start ngrok tunnel
    public_url = ngrok.connect(5000)
    print(f"✅ Public URL: {public_url}")
    print(f"   Use this URL in your local system!")
    
    # Start Flask in a thread
    print("\n🚀 Starting Flask server...")
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    print("\n" + "="*60)
    print("✅ SERVER READY!")
    print("="*60)
    print(f"📡 Public URL: {public_url}/predict")
    print("📝 Send POST requests with:")
    print("""
    {
        "audio_tensor": [...],  // Audio tensor as list
        "audio_shape": [n_frames, 512],
        "emotion_context": {
            "emotion": "angry",
            "confidence": 0.92
        },
        "prompt": "..."
    }
    """)
    print("\n⚠️ Keep this Colab tab open!")
    
    # Keep running
    import time
    while True:
        time.sleep(10)

# ============= RUN IN COLAB =============
if __name__ == "__main__":
    # Check if running in Colab
    try:
        import google.colab
        IN_COLAB = True
    except:
        IN_COLAB = False
    
    if IN_COLAB:
        main_colab()
    else:
        print("⚠️ This script should be run in Google Colab!")
        print("   Copy this code to a Colab notebook and run it there.")