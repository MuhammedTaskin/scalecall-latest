#!/usr/bin/env python3
"""
RUN GEMMA 3N E4B-IT TRAINING WITH AUDIO AWARENESS
"""

import subprocess
import sys
import time

def run_training():
    print("🚀 GEMMA 3N E4B-IT TRAINING WITH AUDIO")
    print("="*60)
    
    # Training command with audio-aware dataset
    cmd = [
        sys.executable, "-m", "mlx_lm.lora",
        "--model", "./models/gemma3n-e4b-4bit",
        "--train",
        "--data", "./gemma3n_training.jsonl",
        "--batch-size", "2",
        "--lora-layers", "8",  # Start small
        "--lora-rank", "16",   # Conservative rank
        "--iters", "50",        # Quick test
        "--learning-rate", "2e-4",
        "--warmup", "5",
        "--adapter-path", "./adapters/gemma3n-telco-test",
        "--save-every", "25",
        "--test",  # Test mode
        "--seed", "42"
    ]
    
    print("Training command:")
    print(" ".join(cmd))
    print("\nStarting training...")
    
    start_time = time.time()
    
    try:
        # Run training
        result = subprocess.run(cmd, capture_output=False, text=True)
        
        elapsed = time.time() - start_time
        print(f"\n✅ Training completed in {elapsed/60:.1f} minutes")
        
        if result.returncode == 0:
            print("🎉 SUCCESS! Model trained with audio-aware data!")
            test_inference()
        else:
            print(f"⚠️ Training failed with code {result.returncode}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_inference():
    """Test the fine-tuned model"""
    
    print("\n🧪 TESTING INFERENCE")
    print("="*60)
    
    test_prompts = [
        "eSIM'im çalışmıyor, yardım eder misiniz?",
        "Faturamda haksız ücret var!",
        "Daha hızlı internet paketi istiyorum"
    ]
    
    try:
        from mlx_lm import load, generate
        
        # Load model with adapters
        print("Loading model with adapters...")
        model, tokenizer = load(
            "./models/gemma3n-e4b-4bit",
            adapter_path="./adapters/gemma3n-telco-test"
        )
        
        for prompt in test_prompts:
            print(f"\n📞 Customer: {prompt}")
            
            # Format for Gemma 3N
            formatted = f"""### Instruction:
Sen bir Türk telekom asistanısın.

### Input:
[DUYGU: normal]
{prompt}

### Output:"""
            
            # Generate
            response = generate(
                model,
                tokenizer,
                prompt=formatted,
                max_tokens=100,
                temperature=0.7
            )
            
            # Extract response
            if "### Output:" in response:
                output = response.split("### Output:")[-1].strip()
            else:
                output = response
            
            print(f"🤖 Agent: {output[:200]}...")
            
    except Exception as e:
        print(f"⚠️ Inference test failed: {e}")
        print("Model may still be downloading or training didn't complete")

if __name__ == "__main__":
    run_training()