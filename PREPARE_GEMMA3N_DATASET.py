#!/usr/bin/env python3
"""
PREPARE DATASET FOR GEMMA 3N E4B-IT TRAINING
Generate AI responses and create complete training pairs
"""

import json
from pathlib import Path
import random

class Gemma3NDatasetPreparer:
    """Prepare complete dataset with AI responses"""
    
    def __init__(self):
        self.agent_tools = {
            "RouterAgent": ["verify_user", "get_customer_status", "route_to_agent"],
            "TechAgent": ["check_esim_status", "check_device_imei", "reissue_activation_code", "create_tech_ticket"],
            "BillingAgent": ["get_last_bill", "get_unpaid_amount", "apply_campaign_discount", "create_payment_note"],
            "PlanAgent": ["get_customer_plan", "list_all_plans", "change_customer_plan", "check_plan_compatibility"],
            "FAQAgent": ["search_faq", "get_common_solutions", "send_help_sms", "create_info_ticket"]
        }
        
        self.agent_responses = {
            "RouterAgent": {
                "esim": "eSIM sorununuz için sizi teknik destek birimine yönlendiriyorum. Lütfen bekleyin.",
                "fatura": "Fatura konusunda size yardımcı olması için sizi fatura birimine aktarıyorum.",
                "paket": "Tarife değişikliği için sizi ilgili birime yönlendiriyorum.",
                "default": "Size daha iyi yardımcı olabilmem için kimlik doğrulaması yapmam gerekiyor."
            },
            "TechAgent": {
                "esim": "eSIM durumunuzu kontrol ediyorum. Cihazınızın IMEI numarasını paylaşır mısınız?",
                "network": "Şebeke ayarlarınızı kontrol ediyorum. Cihazınızı yeniden başlatmayı denediniz mi?",
                "activation": "eSIM aktivasyon kodunuzu yeniden gönderiyorum. SMS olarak iletilecek.",
                "default": "Teknik sorununuzu inceliyorum. Biraz bekleyin lütfen."
            },
            "BillingAgent": {
                "high_bill": "Faturanızı detaylı inceliyorum. Geçen aya göre kullanımınızda artış görünüyor.",
                "payment": "Ödeme geçmişinizi kontrol ediyorum. Son ödemeniz alınmış görünüyor.",
                "discount": "Size uygun kampanyaları kontrol ediyorum.",
                "default": "Fatura detaylarınıza bakıyorum."
            }
        }
    
    def load_customer_conversations(self):
        """Load conversations we generated voices for"""
        
        print("📊 Loading customer conversations...")
        
        with open("data/selected_for_tts.json", 'r') as f:
            selection = json.load(f)
        
        conversations = []
        for conv_info in selection['conversations'][:20]:  # Start with 20
            with open(conv_info['path'], 'r') as f:
                conv = json.load(f)
            
            # We already have customer turns and agent responses!
            customer_turns = conv.get('customer_turns_for_tts', [])
            agent_responses = conv.get('agent_responses', [])
            
            for i, turn in enumerate(customer_turns):
                if i >= len(agent_responses):
                    break
                
                # Check audio file
                audio_file = f"data/tts_audio_final/{conv_info['id']}_turn_{i+1}.mp3"
                
                conversations.append({
                    'conversation_id': conv_info['id'],
                    'turn': i + 1,
                    'audio_file': audio_file if Path(audio_file).exists() else None,
                    'customer_text': turn.get('text', ''),
                    'customer_emotion': turn.get('emotion', 'normal'),
                    'agent_persona': agent_responses[i].get('agent_persona', 'RouterAgent'),
                    'agent_response': agent_responses[i].get('text', ''),
                    'tools_triggered': agent_responses[i].get('tools_triggered', []),
                    'next_agent': None  # Will determine from handoffs
                })
        
        print(f"✅ Loaded {len(conversations)} conversation turns")
        print(f"   With audio: {sum(1 for c in conversations if c['audio_file'])}")
        
        return conversations
    
    def create_gemma3n_format(self, conversations):
        """Format for Gemma 3N E4B training"""
        
        print("\n📝 Creating Gemma 3N training format...")
        
        training_data = []
        
        for conv in conversations:
            # Gemma 3N uses special tokens
            formatted = {
                "instruction": f"Sen bir Türk telekom {conv['agent_persona']} uzmanısın.",
                "input": f"[DUYGU: {conv['customer_emotion']}]\n{conv['customer_text']}",
                "output": conv['agent_response']
            }
            
            # Add tools if present
            if conv['tools_triggered']:
                tools_str = ", ".join(conv['tools_triggered'])
                formatted['output'] += f"\n[ARAÇLAR: {tools_str}]"
            
            # Add audio reference
            if conv['audio_file']:
                formatted['audio_ref'] = conv['audio_file']
            
            training_data.append(formatted)
        
        # Save in multiple formats
        
        # 1. JSONL format for MLX
        with open("gemma3n_training.jsonl", 'w') as f:
            for item in training_data:
                # MLX expects 'text' field
                text = f"### Instruction:\n{item['instruction']}\n\n### Input:\n{item['input']}\n\n### Output:\n{item['output']}"
                f.write(json.dumps({"text": text}, ensure_ascii=False) + "\n")
        
        # 2. JSON format for reference
        with open("gemma3n_training.json", 'w') as f:
            json.dump(training_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Created {len(training_data)} training examples")
        print(f"💾 Saved to gemma3n_training.jsonl and .json")
        
        return training_data
    
    def create_mlx_training_script(self):
        """Create the actual MLX training script"""
        
        script = """#!/bin/bash
# GEMMA 3N E4B-IT 4-BIT TRAINING ON M4 MAX

echo "🚀 Starting Gemma 3N E4B-IT training on M4 Max"
echo "============================================"

# Install requirements
echo "📦 Installing MLX..."
pip install -q mlx mlx-lm

# Download model if not exists
echo "📥 Downloading Gemma 3N E4B-IT 4-bit..."
python -c "
from huggingface_hub import snapshot_download
import os

model_id = 'lmstudio-community/gemma-3n-E4B-it-MLX-4bit'
local_dir = './models/gemma3n-e4b-4bit'

if not os.path.exists(local_dir):
    print(f'Downloading {model_id}...')
    snapshot_download(repo_id=model_id, local_dir=local_dir)
    print('✅ Model downloaded!')
else:
    print('✅ Model already exists')
"

# Run training with MLX LoRA
echo "🎯 Training with LoRA..."
python -m mlx_lm.lora \\
    --model ./models/gemma3n-e4b-4bit \\
    --train \\
    --data ./gemma3n_training.jsonl \\
    --batch-size 2 \\
    --lora-layers 16 \\
    --lora-rank 32 \\
    --iters 100 \\
    --learning-rate 2e-4 \\
    --warmup 10 \\
    --adapter-path ./adapters/gemma3n-telco \\
    --save-every 25 \\
    --grad-checkpoint

echo "✅ Training complete!"
echo "📁 Adapters saved to ./adapters/gemma3n-telco"

# Test inference
echo "🧪 Testing inference..."
python -c "
from mlx_lm import load, generate

# Load with adapters
model, tokenizer = load(
    './models/gemma3n-e4b-4bit',
    adapter_path='./adapters/gemma3n-telco'
)

# Test
prompt = 'eSIM aktivasyonu yapamıyorum'
response = generate(model, tokenizer, prompt, max_tokens=50)
print(f'Response: {response}')
"
"""
        
        with open("train_gemma3n_e4b.sh", 'w') as f:
            f.write(script)
        
        print("\n💾 Created train_gemma3n_e4b.sh")
        print("   Run with: bash train_gemma3n_e4b.sh")
    
    def analyze_dataset(self, training_data):
        """Analyze the dataset we created"""
        
        print("\n📊 DATASET ANALYSIS")
        print("="*60)
        
        # Count agents
        agents = {}
        for item in training_data:
            agent = item['instruction'].split()[-2]  # Extract agent name
            agents[agent] = agents.get(agent, 0) + 1
        
        print("Agent distribution:")
        for agent, count in agents.items():
            print(f"   {agent}: {count}")
        
        # Count tools
        tools_used = set()
        for conv in training_data:
            if "[ARAÇLAR:" in conv['output']:
                tools_str = conv['output'].split("[ARAÇLAR:")[1].split("]")[0]
                tools = [t.strip() for t in tools_str.split(",")]
                tools_used.update(tools)
        
        print(f"\nUnique tools: {len(tools_used)}")
        
        # Audio coverage
        with_audio = sum(1 for item in training_data if 'audio_ref' in item)
        print(f"\nAudio coverage: {with_audio}/{len(training_data)} ({100*with_audio/len(training_data):.1f}%)")
        
        # Text lengths
        input_lens = [len(item['input']) for item in training_data]
        output_lens = [len(item['output']) for item in training_data]
        
        print(f"\nText statistics:")
        print(f"   Avg input length: {sum(input_lens)/len(input_lens):.0f} chars")
        print(f"   Avg output length: {sum(output_lens)/len(output_lens):.0f} chars")

def main():
    print("🎯 PREPARING GEMMA 3N E4B-IT DATASET")
    print("="*60)
    
    preparer = Gemma3NDatasetPreparer()
    
    # Load existing conversations (we already have agent responses!)
    conversations = preparer.load_customer_conversations()
    
    # Format for Gemma 3N
    training_data = preparer.create_gemma3n_format(conversations)
    
    # Analyze
    preparer.analyze_dataset(training_data)
    
    # Create training script
    preparer.create_mlx_training_script()
    
    print("\n" + "="*60)
    print("✅ DATASET READY FOR GEMMA 3N E4B-IT!")
    print("\nWe discovered: The agent responses were ALREADY GENERATED!")
    print("We have complete conversation pairs with:")
    print("   - Customer text (with audio)")
    print("   - Agent responses")
    print("   - Tools triggered")
    print("   - Agent personas")
    print("\n🚀 Ready to train on M4 Max!")

if __name__ == "__main__":
    main()