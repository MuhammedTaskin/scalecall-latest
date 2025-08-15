#!/usr/bin/env python3
"""
CONVERT GEMMA 3N TO MLX FORMAT
Makes the model compatible with MLX framework
"""

import json
import shutil
from pathlib import Path
import torch
from safetensors import safe_open
from safetensors.torch import save_file

def convert_gemma3n_to_mlx():
    """Convert Gemma3n model to MLX-compatible format"""
    
    model_path = Path("./models/gemma3n-e4b-4bit")
    
    print("🔄 Converting Gemma 3N to MLX format...")
    print("=" * 60)
    
    # Read original config
    with open(model_path / "config.json", "r") as f:
        config = json.load(f)
    
    # Update config for MLX compatibility
    print("📝 Updating config for MLX...")
    
    # Change architecture to standard Gemma
    if "architectures" in config:
        config["architectures"] = ["GemmaForCausalLM"]
    
    # Remove audio_config if present
    if "audio_config" in config:
        del config["audio_config"]
    
    # Add model_type if missing
    if "model_type" not in config:
        config["model_type"] = "gemma"
    
    # Fix any gemma3n references
    config["model_type"] = "gemma"
    
    # Save updated config
    mlx_path = Path("./models/gemma3n-mlx")
    mlx_path.mkdir(parents=True, exist_ok=True)
    
    with open(mlx_path / "config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ Config updated")
    
    # Copy tokenizer files
    print("📋 Copying tokenizer files...")
    for file in ["tokenizer.model", "tokenizer.json", "tokenizer_config.json", 
                 "special_tokens_map.json", "generation_config.json"]:
        src = model_path / file
        if src.exists():
            shutil.copy(src, mlx_path / file)
    
    # Convert model weights
    print("🔧 Converting model weights...")
    
    # Load safetensors
    model_files = list(model_path.glob("model-*.safetensors"))
    
    if not model_files:
        print("⚠️ No model files found, trying direct conversion...")
        # Copy model files as-is
        for file in model_path.glob("*.safetensors"):
            shutil.copy(file, mlx_path / file.name)
    else:
        # Merge and convert multi-part model
        all_tensors = {}
        
        for model_file in sorted(model_files):
            print(f"  Loading {model_file.name}...")
            with safe_open(model_file, framework="pt") as f:
                for key in f.keys():
                    tensor = f.get_tensor(key)
                    # Rename keys if needed for MLX compatibility
                    new_key = key.replace("gemma3n", "model").replace("Gemma3n", "Gemma")
                    all_tensors[new_key] = tensor
        
        # Save as single file for MLX
        output_file = mlx_path / "model.safetensors"
        print(f"  Saving to {output_file}...")
        save_file(all_tensors, output_file)
    
    # Create index file for MLX
    index = {
        "metadata": {
            "total_size": sum(t.numel() * t.element_size() for t in all_tensors.values()) if all_tensors else 0
        },
        "weight_map": {k: "model.safetensors" for k in all_tensors.keys()} if all_tensors else {}
    }
    
    with open(mlx_path / "model.safetensors.index.json", "w") as f:
        json.dump(index, f, indent=2)
    
    print("✅ Model converted successfully!")
    print(f"📁 Converted model saved to: {mlx_path}")
    
    return mlx_path

if __name__ == "__main__":
    try:
        mlx_path = convert_gemma3n_to_mlx()
        print("\n🎉 Conversion complete! Now you can use:")
        print(f"python -m mlx_lm.lora --model {mlx_path} --train")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()