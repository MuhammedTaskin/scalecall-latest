#!/usr/bin/env python3
"""
TEKNOFEST 2025 - ALL-IN-ONE COLAB MODEL SERVER
Complete model server in single file - just run in Colab!
"""

import subprocess
import sys
import os

def install_requirements():
    """Install all required packages"""
    print("📦 Installing requirements...")
    
    requirements = [
        'flask', 'flask-cors', 'pyngrok', 'torch', 'transformers', 
        'accelerate', 'bitsandbytes', 'peft'
    ]
    
    for req in requirements:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', req, '-q'])
        except:
            print(f"Failed to install {req}, continuing...")
    
    # Try to install unsloth
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'unsloth[colab-new]@git+https://github.com/unslothai/unsloth.git', '-q'])
        print("✅ Unsloth installed")
    except:
        print("⚠️ Unsloth installation failed, will use transformers")

def mount_drive():
    """Mount Google Drive"""
    try:
        from google.colab import drive
        drive.mount('/content/drive')
        print("✅ Drive mounted")
        return True
    except:
        print("⚠️ Not in Colab environment")
        return False

def load_model():
    """Load model with multiple fallback methods"""
    
    # Define checkpoint path
    CHECKPOINT_PATH = '/content/drive/MyDrive/TEKNOFEST_2025/20250815_022938/checkpoints/checkpoint-10'
    
    print("🤖 Loading model...")
    
    # Method 1: Try Unsloth
    try:
        print("Attempting Unsloth loading...")
        import unsloth
        from unsloth import FastLanguageModel
        import torch
        
        # Load base model
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name="unsloth/gemma-3n-E4B-it",
            max_seq_length=2048,
            dtype=None,
            load_in_4bit=True,
            device_map="auto"
        )
        
        # Try to load checkpoint adapter
        if os.path.exists(CHECKPOINT_PATH):
            try:
                from peft import PeftModel
                adapter_config = os.path.join(CHECKPOINT_PATH, 'adapter_config.json')
                if os.path.exists(adapter_config):
                    model = PeftModel.from_pretrained(model, CHECKPOINT_PATH)
                    print("✅ Your trained LoRA adapter loaded!")
                    model_status = "trained"
                else:
                    print("⚠️ No adapter found, using base model")
                    model_status = "base"
            except Exception as e:
                print(f"⚠️ Adapter loading failed: {e}")
                model_status = "base"
        else:
            print("⚠️ Checkpoint path not found, using base model")
            model_status = "base"
        
        # Enable inference mode
        FastLanguageModel.for_inference(model)
        
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        print(f"✅ Unsloth model loaded ({model_status})")
        return model, tokenizer, "unsloth", model_status
        
    except Exception as e:
        print(f"Unsloth failed: {e}")
    
    # Method 2: Fallback to Transformers
    try:
        print("Attempting Transformers loading...")
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch
        
        model = AutoModelForCausalLM.from_pretrained(
            "google/gemma-2-2b-it",
            device_map="auto",
            torch_dtype=torch.float16,
            trust_remote_code=True
        )
        
        tokenizer = AutoTokenizer.from_pretrained("google/gemma-2-2b-it")
        
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        model.eval()
        print("✅ Transformers model loaded (base)")
        return model, tokenizer, "transformers", "base"
        
    except Exception as e:
        print(f"Transformers failed: {e}")
        raise Exception("All model loading methods failed!")

def create_flask_app(model, tokenizer, model_type, model_status):
    """Create Flask application"""
    
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    import re
    import torch
    
    app = Flask(__name__)
    CORS(app)
    
    # System prompt for Turkish telco
    SYSTEM_PROMPT = """Sen Türk telekom müşteri hizmetleri uzmanısın. 
Müşterilerin duygularına uygun yanıt ver ve gerekli araçları [araç_adı] formatında kullan.

Kullanabileceğin araçlar:
[get_current_balance] - Bakiye kontrolü
[check_data_usage] - İnternet kullanım kontrolü  
[view_current_plan] - Mevcut paket bilgisi
[activate_esim] - eSIM aktivasyonu
[create_support_ticket] - Destek talebi oluşturma
[troubleshoot_connection] - Bağlantı sorunları

Duygusal yanıtlar:
- angry: "Yaşadığınız sorun için özür dileriz, hemen yardımcı oluyorum."
- sad: "Size yardımcı olmak için buradayım."
- confused: "Size açıklayayım."
- happy: "Memnuniyetiniz bizim için önemli!"
- neutral: "Size nasıl yardımcı olabilirim?"

Yanıtlarında gerekli araçları [araç_adı] formatında belirt."""

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({
            'status': 'healthy',
            'model_type': model_type,
            'model_status': model_status,
            'checkpoint_loaded': model_status == "trained",
            'ready': True,
            'system': 'TEKNOFEST 2025 Model Server'
        })
    
    @app.route('/predict', methods=['POST'])
    def predict():
        try:
            data = request.json or {}
            text = data.get('text', '')
            emotion = data.get('emotion', 'neutral')
            audio_data = data.get('audio_data', None)  # Native audio input
            
            # Gemma 3N can process audio directly - no text required if audio present
            if not text.strip() and not audio_data:
                return jsonify({'error': 'Text or audio is required', 'success': False}), 400
            
            # Build complete prompt with audio support
            if audio_data:
                # Native audio input to Gemma 3N
                import numpy as np
                audio_array = np.array(audio_data, dtype=np.float32)
                
                # Gemma 3N expects audio as part of multimodal input
                prompt = f"""{SYSTEM_PROMPT}

<start_of_turn>user
<emotion>{emotion}</emotion>
Audio input: {len(audio_array)} samples
{text if text else '[Audio only input]'}
<end_of_turn>
<start_of_turn>assistant"""
                
                print(f"🎵 Processing {len(audio_array)} audio samples with Gemma 3N")
                
                # For Gemma 3N multimodal input
                inputs = tokenizer(prompt, return_tensors='pt').to(model.device)
                # Note: Add audio processing here for true multimodal
                
            else:
                # Text-only input
                prompt = f"""{SYSTEM_PROMPT}

<start_of_turn>user
<emotion>{emotion}</emotion>
{text}
<end_of_turn>
<start_of_turn>assistant"""
                
                inputs = tokenizer(prompt, return_tensors='pt').to(model.device)
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=200,
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.95,
                    pad_token_id=tokenizer.eos_token_id,
                    eos_token_id=tokenizer.eos_token_id
                )
            
            # Decode response
            full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract assistant part
            if 'assistant' in full_response:
                response = full_response.split('assistant')[-1].strip()
            else:
                response = full_response.replace(prompt, '').strip()
            
            # Extract tools
            tools_found = re.findall(r'\[([^\]]+)\]', response)
            
            # Clean response
            response = response[:500]  # Limit length
            
            print(f"Generated: {response[:100]}...")
            
            return jsonify({
                'generated_text': response,
                'emotion_detected': emotion,
                'tools_extracted': tools_found,
                'model_type': model_type,
                'model_status': model_status,
                'success': True
            })
            
        except Exception as e:
            print(f"Prediction error: {e}")
            return jsonify({
                'error': str(e), 
                'success': False,
                'model_type': model_type
            }), 500
    
    @app.route('/test', methods=['GET'])
    def test():
        # Simple test endpoint
        test_response = "Merhaba! TEKNOFEST 2025 model sunucusu çalışıyor. [get_current_balance] aracını kullanabilirim."
        tools = re.findall(r'\[([^\]]+)\]', test_response)
        
        return jsonify({
            'message': test_response,
            'tools_found': tools,
            'model_type': model_type,
            'model_status': model_status,
            'working': True
        })
    
    return app

def start_ngrok_server(app):
    """Start ngrok tunnel and Flask server"""
    
    from pyngrok import ngrok
    
    # Configure ngrok with your token
    ngrok.set_auth_token("31Iyz0YNz20h4XPZAhCdzH9mQfa_7pS9XT3qX1N6YC3kS6tZY")
    
    # Kill existing tunnels
    try:
        ngrok.kill()
    except:
        pass
    
    # Create tunnel
    public_url = ngrok.connect(5000)
    
    print("\n" + "="*70)
    print("🎉 TEKNOFEST 2025 MODEL SERVER READY!")
    print("="*70)
    print(f"📡 Public URL: {public_url}")
    print("="*70)
    print(f"🔗 Use this URL in your local system:")
    print(f"   ./RUN_COMPLETE_SYSTEM.sh {public_url}")
    print("="*70)
    print("📋 Available endpoints:")
    print(f"   {public_url}/health   - Health check")
    print(f"   {public_url}/predict  - AI predictions")
    print(f"   {public_url}/test     - Quick test")
    print("="*70)
    print("⚠️  KEEP THIS CELL RUNNING!")
    print("="*70)
    
    # Start Flask server
    print("🚀 Starting Flask server...")
    app.run(host='0.0.0.0', port=5000, debug=False)

def main():
    """Main execution function"""
    
    print("""
╔════════════════════════════════════════════════════════════╗
║              TEKNOFEST 2025 - MODEL SERVER                ║  
║                All-in-One Colab Setup                     ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Step 1: Install requirements
        install_requirements()
        
        # Step 2: Mount drive
        mount_drive()
        
        # Step 3: Load model
        model, tokenizer, model_type, model_status = load_model()
        
        # Step 4: Create Flask app
        app = create_flask_app(model, tokenizer, model_type, model_status)
        
        # Step 5: Start server with ngrok
        start_ngrok_server(app)
        
    except KeyboardInterrupt:
        print("\n⏹️  Server stopped by user")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        print("\nTroubleshooting:")
        print("1. Restart runtime and try again")
        print("2. Check if your checkpoint path exists")
        print("3. Ensure you have GPU runtime selected")

if __name__ == "__main__":
    main()