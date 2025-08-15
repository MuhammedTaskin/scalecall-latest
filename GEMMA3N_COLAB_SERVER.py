"""
TEKNOFEST 2025 - BULLETPROOF COLAB MODEL SERVER
Simple, reliable model serving from Colab
"""

# Cell 1: Setup (run first)
def setup_colab():
    # Mount Drive
    from google.colab import drive
    drive.mount('/content/drive')
    
    # Install requirements
    import subprocess
    subprocess.run(['pip', 'install', 'flask', 'flask-cors', 'pyngrok', '-q'], check=True)
    
    print("✅ Setup complete")

# Cell 2: Load Model (restart runtime first if needed)
def load_model():
    import os
    
    # Your checkpoint path
    CHECKPOINT_PATH = '/content/drive/MyDrive/TEKNOFEST_2025/20250815_022938/checkpoints/checkpoint-10'
    
    # Option 1: Try with unsloth
    try:
        import unsloth
        from unsloth import FastLanguageModel
        
        print("Loading with Unsloth...")
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name="unsloth/gemma-3n-E4B-it",
            max_seq_length=2048,
            dtype=None,
            load_in_4bit=True,
            device_map="auto"
        )
        
        # Try to load your adapter
        if os.path.exists(CHECKPOINT_PATH):
            try:
                from peft import PeftModel
                if os.path.exists(os.path.join(CHECKPOINT_PATH, 'adapter_config.json')):
                    model = PeftModel.from_pretrained(model, CHECKPOINT_PATH)
                    print("✅ Your LoRA adapter loaded!")
                else:
                    print("⚠️ Using base model (no adapter found)")
            except Exception as e:
                print(f"⚠️ Adapter loading failed: {e}")
        
        FastLanguageModel.for_inference(model)
        print("✅ Unsloth model ready")
        return model, tokenizer, "unsloth"
        
    except Exception as e:
        print(f"Unsloth failed: {e}")
        
        # Option 2: Fallback to transformers
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            
            print("Loading with transformers...")
            model = AutoModelForCausalLM.from_pretrained(
                "google/gemma-2-2b-it",
                device_map="auto",
                torch_dtype=torch.float16
            )
            
            tokenizer = AutoTokenizer.from_pretrained("google/gemma-2-2b-it")
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            model.eval()
            print("✅ Transformers model ready")
            return model, tokenizer, "transformers"
            
        except Exception as e2:
            print(f"All loading methods failed: {e2}")
            raise e2

# Cell 3: Create Server
def create_server(model, tokenizer, model_type):
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    import re
    
    app = Flask(__name__)
    CORS(app)
    
    # System prompt for Turkish telco
    SYSTEM_PROMPT = """Sen Türk telekom müşteri hizmetleri asistanısın. 
Müşterilerin duygularına uygun yanıt ver ve gerekli araçları [araç_adı] formatında kullan.

Kullanabileceğin araçlar:
[get_current_balance] - Bakiye sorgula
[check_data_usage] - İnternet kullanımı
[activate_esim] - eSIM aktivasyonu
[create_support_ticket] - Destek talebi

Duygulara göre yanıt ver:
- angry: Özür dile, hızlı çözüm sun
- neutral: Profesyonel ol"""
    
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({
            'status': 'healthy',
            'model_type': model_type,
            'ready': True
        })
    
    @app.route('/predict', methods=['POST'])
    def predict():
        try:
            data = request.json
            text = data.get('text', '')
            emotion = data.get('emotion', 'neutral')
            
            # Build prompt
            prompt = f"""{SYSTEM_PROMPT}

<start_of_turn>user
<emotion>{emotion}</emotion>
{text}
<end_of_turn>
<start_of_turn>assistant"""
            
            # Generate based on model type
            if model_type == "unsloth":
                # Unsloth method
                inputs = tokenizer(prompt, return_tensors='pt').to(model.device)
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=200,
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.95
                )
                response = tokenizer.decode(outputs[0], skip_special_tokens=True)
                
            else:
                # Transformers method
                inputs = tokenizer(prompt, return_tensors='pt').to(model.device)
                with torch.no_grad():
                    outputs = model.generate(
                        **inputs,
                        max_new_tokens=200,
                        temperature=0.7,
                        do_sample=True,
                        top_p=0.95,
                        pad_token_id=tokenizer.eos_token_id
                    )
                response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract assistant response
            if 'assistant' in response:
                response = response.split('assistant')[-1].strip()
            
            # Extract tools
            tools_found = re.findall(r'\[([^\]]+)\]', response)
            
            return jsonify({
                'generated_text': response,
                'emotion_detected': emotion,
                'tools_extracted': tools_found,
                'model_type': model_type,
                'success': True
            })
            
        except Exception as e:
            return jsonify({'error': str(e), 'success': False}), 500
    
    return app

# Cell 4: Start Server with ngrok
def start_server(app):
    from pyngrok import ngrok
    import threading
    
    # Configure ngrok
    ngrok.set_auth_token("31Iyz0YNz20h4XPZAhCdzH9mQfa_7pS9XT3qX1N6YC3kS6tZY")
    
    # Kill existing tunnels
    ngrok.kill()
    
    # Start tunnel
    public_url = ngrok.connect(5000)
    
    print("="*60)
    print("🎉 MODEL SERVER READY!")
    print("="*60)
    print(f"Your model URL: {public_url}")
    print("="*60)
    print(f"\nUse this URL in your local system:")
    print(f"./RUN_COMPLETE_SYSTEM.sh {public_url}")
    print("\n⚠️ Keep this running!")
    print("="*60)
    
    # Start Flask server
    app.run(port=5000, debug=False, host='0.0.0.0')

# Cell 5: Complete Setup (run all at once)
def complete_setup():
    print("🚀 Starting complete setup...")
    
    # Step 1: Setup
    setup_colab()
    
    # Step 2: Load model
    model, tokenizer, model_type = load_model()
    
    # Step 3: Create server
    app = create_server(model, tokenizer, model_type)
    
    # Step 4: Start server
    start_server(app)

# Instructions for Colab
print("""
INSTRUCTIONS FOR COLAB:

1. Run: setup_colab()
2. RESTART RUNTIME (Runtime → Restart runtime)
3. Run: model, tokenizer, model_type = load_model()
4. Run: app = create_server(model, tokenizer, model_type)
5. Run: start_server(app)

OR run everything at once:
complete_setup()

Then copy the ngrok URL to your local system!
""")