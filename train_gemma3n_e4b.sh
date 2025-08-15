#!/bin/bash
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
python -m mlx_lm.lora \
    --model ./models/gemma3n-e4b-4bit \
    --train \
    --data ./gemma3n_training.jsonl \
    --batch-size 2 \
    --lora-layers 16 \
    --lora-rank 32 \
    --iters 100 \
    --learning-rate 2e-4 \
    --warmup 10 \
    --adapter-path ./adapters/gemma3n-telco \
    --save-every 25 \
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
