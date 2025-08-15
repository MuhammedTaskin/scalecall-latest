#!/usr/bin/env python3
"""
SIMPLE MLX CONVERTER FOR GEMMA 3N
No torch dependency needed
"""

import json
import shutil
from pathlib import Path

def convert_to_mlx():
    """Simple conversion by updating config"""
    
    src_path = Path("./models/gemma3n-e4b-4bit")
    dst_path = Path("./models/gemma3n-mlx-fixed")
    
    print("🔄 Converting Gemma 3N for MLX...")
    print("=" * 60)
    
    # Create destination
    dst_path.mkdir(parents=True, exist_ok=True)
    
    # Copy all files first
    print("📋 Copying model files...")
    for file in src_path.glob("*"):
        if file.is_file():
            print(f"  Copying {file.name}...")
            shutil.copy(file, dst_path / file.name)
    
    # Fix config.json
    print("🔧 Fixing config for MLX...")
    config_path = dst_path / "config.json"
    
    with open(config_path, "r") as f:
        config = json.load(f)
    
    # Critical fixes for MLX
    config["architectures"] = ["GemmaForCausalLM"]
    config["model_type"] = "gemma"
    
    # Remove problematic fields
    fields_to_remove = ["audio_config", "gemma3n", "Gemma3n"]
    for field in fields_to_remove:
        if field in config:
            del config[field]
    
    # Ensure required fields
    if "vocab_size" not in config:
        config["vocab_size"] = 256000  # Gemma default
    
    if "hidden_size" not in config:
        config["hidden_size"] = 3584  # For 3B model
    
    if "num_hidden_layers" not in config:
        config["num_hidden_layers"] = 28
    
    if "num_attention_heads" not in config:
        config["num_attention_heads"] = 16
    
    if "num_key_value_heads" not in config:
        config["num_key_value_heads"] = 16
    
    if "intermediate_size" not in config:
        config["intermediate_size"] = 14336
    
    # Save fixed config
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ Config fixed!")
    
    # Create a simple wrapper script
    wrapper_script = dst_path / "run_training.sh"
    with open(wrapper_script, "w") as f:
        f.write("""#!/bin/bash
# MLX Training Script for Gemma 3N

echo "🚀 Starting MLX training..."

python -m mlx_lm.lora \\
    --model . \\
    --train \\
    --data ../../gemma3n_training.jsonl \\
    --batch-size 1 \\
    --lora-layers 4 \\
    --lora-rank 8 \\
    --iters 20 \\
    --learning-rate 1e-4 \\
    --adapter-path ../../adapters/test \\
    --save-every 10

echo "✅ Training complete!"
""")
    
    wrapper_script.chmod(0o755)
    
    print(f"\n✅ Conversion complete!")
    print(f"📁 Fixed model at: {dst_path}")
    print(f"\n🎯 Now try:")
    print(f"cd {dst_path}")
    print(f"./run_training.sh")
    
    return dst_path

if __name__ == "__main__":
    try:
        convert_to_mlx()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()