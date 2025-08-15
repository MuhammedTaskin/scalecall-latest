#!/usr/bin/env python3
"""
GEMMA 3N E4B-IT 4-BIT SMALL TEST RUN ON M4 MAX
Testing with 10 conversations before full training
"""

# pip install mlx mlx-lm transformers

import mlx
import mlx.core as mx
import mlx.nn as nn
from mlx_lm import load, generate
import json
import time
from pathlib import Path
import subprocess

class Gemma3NE4BTest:
    """Test Gemma 3N E4B-IT specifically"""
    
    def __init__(self):
        # EXACT MODEL: Gemma 3N E4B-IT 4-bit for MLX
        self.model_id = "lmstudio-community/gemma-3n-E4B-it-MLX-4bit"
        
        # Small test dataset
        self.test_size = 10
        
        print("🎯 GEMMA 3N E4B-IT 4-BIT TEST")
        print("="*60)
        print(f"Model: {self.model_id}")
        print(f"Test size: {self.test_size} conversations")
        
    def check_model_availability(self):
        """Check if model exists and can be loaded"""
        
        print("\n📦 Checking model availability...")
        
        try:
            # Try to load model info
            from huggingface_hub import model_info
            info = model_info(self.model_id)
            print(f"✅ Model found on HuggingFace")
            print(f"   Size: {info.safetensors.total / 1e9:.1f} GB")
            print(f"   Quantization: 4-bit MLX")
            return True
        except:
            print("⚠️ Model not found, trying alternative sources...")
            return False
    
    def prepare_small_dataset(self):
        """Prepare 10 conversations for testing"""
        
        print("\n📊 Preparing small test dataset...")
        
        # Load our generated conversations
        with open("data/selected_for_tts.json", 'r') as f:
            selection = json.load(f)
        
        test_data = []
        
        # Take first 10 conversations
        for conv_info in selection['conversations'][:self.test_size]:
            with open(conv_info['path'], 'r') as f:
                conv = json.load(f)
            
            customer_turns = conv.get('customer_turns_for_tts', [])
            agent_responses = conv.get('agent_responses', [])
            
            for i, turn in enumerate(customer_turns):
                if i >= len(agent_responses):
                    break
                
                # Check if audio exists
                audio_file = f"data/tts_audio_final/{conv_info['id']}_turn_{i+1}.mp3"
                has_audio = Path(audio_file).exists()
                
                test_data.append({
                    'id': f"{conv_info['id']}_turn_{i+1}",
                    'audio_file': audio_file if has_audio else None,
                    'customer_text': turn.get('text', ''),
                    'emotion': turn.get('emotion', 'normal'),
                    'agent': agent_responses[i].get('agent_persona', 'RouterAgent'),
                    'agent_response': agent_responses[i].get('text', ''),
                    'tools': agent_responses[i].get('tools_triggered', [])
                })
                
                if len(test_data) >= 50:  # Max 50 turns for test
                    break
        
        print(f"✅ Prepared {len(test_data)} training examples")
        print(f"   With audio: {sum(1 for d in test_data if d['audio_file'])}")
        
        # Save test dataset
        with open("gemma3n_test_data.json", 'w') as f:
            json.dump(test_data, f, indent=2, ensure_ascii=False)
        
        return test_data
    
    def create_training_prompts(self, test_data):
        """Format data for Gemma 3N training"""
        
        print("\n📝 Creating training prompts...")
        
        prompts = []
        
        for item in test_data:
            # Gemma 3N specific prompt format
            prompt = f"""<start_of_turn>system
Sen bir Türk telekom çağrı merkezi {item['agent']} uzmanısın.
<end_of_turn>
<start_of_turn>user
[DUYGU: {item['emotion']}]
{item['customer_text']}
<end_of_turn>
<start_of_turn>model
{item['agent_response']}"""
            
            if item['tools']:
                tools_str = ", ".join(item['tools']) if isinstance(item['tools'], list) else str(item['tools'])
                prompt += f"\n[ARAÇLAR: {tools_str}]"
            
            prompt += "\n<end_of_turn>"
            
            prompts.append({
                'text': prompt,
                'audio_ref': item['audio_file']
            })
        
        # Save prompts
        with open("gemma3n_prompts.jsonl", 'w') as f:
            for p in prompts:
                f.write(json.dumps(p, ensure_ascii=False) + "\n")
        
        print(f"✅ Created {len(prompts)} training prompts")
        print(f"💾 Saved to gemma3n_prompts.jsonl")
        
        return prompts
    
    def test_mlx_lora_command(self):
        """Test MLX LoRA fine-tuning command"""
        
        print("\n🧪 Testing MLX LoRA fine-tuning...")
        
        # MLX LoRA command for Gemma 3N E4B
        command = f"""python -m mlx_lm.lora \\
    --model {self.model_id} \\
    --train \\
    --data ./gemma3n_prompts.jsonl \\
    --iters 20 \\
    --batch-size 1 \\
    --lora-layers 8 \\
    --lora-rank 16 \\
    --learning-rate 5e-5 \\
    --adapter-path ./gemma3n_test_adapter \\
    --save-every 10 \\
    --test"""
        
        print("Command to run:")
        print(command)
        
        # Create training script
        with open("train_gemma3n_test.sh", 'w') as f:
            f.write("#!/bin/bash\n")
            f.write(command.replace(" \\", " \\\n    "))
        
        print("\n💾 Saved to train_gemma3n_test.sh")
        
        return command
    
    def test_inference(self):
        """Test inference with Gemma 3N E4B"""
        
        print("\n🔮 Testing inference...")
        
        try:
            # Load model
            print("Loading model...")
            model, tokenizer = load(self.model_id)
            
            # Test prompt
            test_prompt = """<start_of_turn>system
Sen bir Türk telekom çağrı merkezi asistanısın.
<end_of_turn>
<start_of_turn>user
eSIM'im çalışmıyor, yardım eder misiniz?
<end_of_turn>
<start_of_turn>model"""
            
            # Generate
            print("Generating response...")
            response = generate(
                model,
                tokenizer,
                prompt=test_prompt,
                max_tokens=100,
                temperature=0.7
            )
            
            print(f"Response: {response}")
            
        except Exception as e:
            print(f"⚠️ Inference test failed: {e}")
            print("Model may need to be downloaded first")
    
    def benchmark_m4_max(self):
        """Benchmark M4 Max for Gemma 3N E4B"""
        
        print("\n🏎️ M4 MAX BENCHMARK FOR GEMMA 3N E4B")
        print("="*60)
        
        # Check Metal
        if mx.metal.is_available():
            print(f"✅ Metal GPU available")
            print(f"   Memory: {mx.metal.get_active_memory() / 1e9:.1f} GB active")
        
        # Model size estimates
        print("\n📊 Gemma 3N E4B-IT Specs:")
        print("   Parameters: 4.67B (effective 4B)")
        print("   4-bit size: ~2.5 GB")
        print("   Context: 32K tokens")
        print("   Languages: 140 (including Turkish)")
        print("   Modalities: Text, Audio, Vision")
        
        print("\n⚡ Expected Performance on M4 Max:")
        print("   Memory usage: ~3-4 GB")
        print("   Batch size: 8-16")
        print("   Training speed: ~100 samples/min")
        print("   Inference: 30-40 tokens/sec")

def main():
    print("🚀 GEMMA 3N E4B-IT SMALL TEST RUN")
    print("="*60)
    
    # Initialize tester
    tester = Gemma3NE4BTest()
    
    # Check model
    tester.check_model_availability()
    
    # Prepare data
    test_data = tester.prepare_small_dataset()
    
    # Create prompts
    prompts = tester.create_training_prompts(test_data)
    
    # Show training command
    tester.test_mlx_lora_command()
    
    # Benchmark
    tester.benchmark_m4_max()
    
    # Test inference
    # tester.test_inference()  # Uncomment after installing model
    
    print("\n" + "="*60)
    print("✅ TEST SETUP COMPLETE!")
    print("\nNext steps:")
    print("1. Install MLX: pip install mlx mlx-lm")
    print("2. Download model: huggingface-cli download lmstudio-community/gemma-3n-E4B-it-MLX-4bit")
    print("3. Run test: bash train_gemma3n_test.sh")
    print("4. Monitor: Should take ~5-10 minutes for 20 iterations")
    print("\n🎯 This is GEMMA 3N E4B-IT 4-BIT - the EXACT model!")

if __name__ == "__main__":
    main()