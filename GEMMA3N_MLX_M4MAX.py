#!/usr/bin/env python3
"""
GEMMA 3N MLX FINE-TUNING FOR M4 MAX (64GB)
Optimized for Apple Silicon with Metal Performance Shaders
"""

# pip install mlx mlx-lm

import mlx
import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
from mlx_lm import load, generate
from mlx_lm.models import gemma
from mlx_lm.tuner.lora import LoRALinear
from mlx_lm.tuner.trainer import TrainingArgs, train
from mlx_lm.tuner.datasets import Dataset
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Any
import time

class GemmaTelcoConfig:
    """Configuration for Gemma 3N fine-tuning on M4 Max"""
    
    # Model settings
    model_name = "mlx-community/gemma-3n-E4B-it-4bit"  # 4-bit quantized
    
    # LoRA settings optimized for M4 Max
    lora_rank = 16
    lora_alpha = 16
    lora_dropout = 0.05
    lora_layers = 16  # Number of layers to apply LoRA
    
    # Training settings for 64GB RAM
    batch_size = 4  # M4 Max can handle larger batches
    gradient_accumulation_steps = 2
    learning_rate = 5e-5
    num_epochs = 3
    warmup_steps = 100
    
    # Memory optimization
    grad_checkpoint = True  # Enable gradient checkpointing
    mixed_precision = True  # Use mixed precision training
    
    # Data settings
    max_seq_length = 2048
    num_workers = 8  # M4 Max has good multi-core performance

class TelcoDatasetMLX:
    """Dataset loader for MLX training"""
    
    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        self.agent_personas = {
            "RouterAgent": "Yönlendirme uzmanı",
            "TechAgent": "Teknik destek uzmanı",
            "BillingAgent": "Fatura uzmanı",
            "PlanAgent": "Tarife uzmanı",
            "FAQAgent": "Bilgi asistanı"
        }
        
    def load_conversations(self) -> List[Dict]:
        """Load and format conversations for MLX"""
        
        training_data = []
        
        # Load selected conversations
        with open(self.data_path / "selected_for_tts.json", 'r') as f:
            selection = json.load(f)
        
        for conv_info in selection['conversations']:
            with open(conv_info['path'], 'r') as f:
                conv = json.load(f)
            
            customer_turns = conv.get('customer_turns_for_tts', [])
            agent_responses = conv.get('agent_responses', [])
            
            for i, turn in enumerate(customer_turns):
                if i >= len(agent_responses):
                    break
                
                agent = agent_responses[i].get('agent_persona', 'RouterAgent')
                tools = agent_responses[i].get('tools_triggered', [])
                
                # Format for MLX training
                training_data.append({
                    "prompt": f"{self.agent_personas[agent]}\n\nMüşteri: {turn.get('text', '')}",
                    "completion": agent_responses[i].get('text', ''),
                    "tools": tools,
                    "agent": agent
                })
        
        return training_data
    
    def create_mlx_dataset(self) -> Dataset:
        """Create MLX-compatible dataset"""
        
        data = self.load_conversations()
        
        # Convert to MLX format
        prompts = [d["prompt"] for d in data]
        completions = [d["completion"] for d in data]
        
        return Dataset(
            prompts=prompts,
            completions=completions,
            tokenizer=None  # Will be set by trainer
        )

class GemmaLoRAModel(nn.Module):
    """Gemma model with LoRA adapters for MLX"""
    
    def __init__(self, base_model, config: GemmaTelcoConfig):
        super().__init__()
        self.base_model = base_model
        self.config = config
        
        # Apply LoRA to attention layers
        self.apply_lora()
    
    def apply_lora(self):
        """Apply LoRA adapters to model layers"""
        
        for i in range(self.config.lora_layers):
            layer = self.base_model.layers[i]
            
            # Replace linear layers with LoRA versions
            if hasattr(layer.self_attn, 'q_proj'):
                layer.self_attn.q_proj = LoRALinear(
                    layer.self_attn.q_proj,
                    rank=self.config.lora_rank,
                    alpha=self.config.lora_alpha,
                    dropout=self.config.lora_dropout
                )
            
            if hasattr(layer.self_attn, 'v_proj'):
                layer.self_attn.v_proj = LoRALinear(
                    layer.self_attn.v_proj,
                    rank=self.config.lora_rank,
                    alpha=self.config.lora_alpha,
                    dropout=self.config.lora_dropout
                )

class MLXTelcoTrainer:
    """Trainer for Gemma 3N on M4 Max"""
    
    def __init__(self, config: GemmaTelcoConfig):
        self.config = config
        
        # Check Metal availability
        if not mx.metal.is_available():
            print("⚠️ Metal not available, using CPU")
        else:
            print(f"✅ Metal GPU detected: {mx.metal.get_active_memory() / 1e9:.1f} GB available")
        
        # Load model and tokenizer
        self.load_model()
    
    def load_model(self):
        """Load Gemma 3N model with 4-bit quantization"""
        
        print(f"📦 Loading {self.config.model_name}...")
        
        # Load with MLX
        self.model, self.tokenizer = load(
            self.config.model_name,
            tokenizer_config={"trust_remote_code": True}
        )
        
        # Apply LoRA
        self.model = GemmaLoRAModel(self.model, self.config)
        
        # Move to Metal if available
        if mx.metal.is_available():
            self.model = mx.compile(self.model)
        
        print(f"✅ Model loaded with LoRA adapters")
    
    def train(self, dataset_path: str):
        """Fine-tune the model"""
        
        print("🚀 Starting fine-tuning on M4 Max...")
        
        # Load dataset
        dataset_loader = TelcoDatasetMLX(dataset_path)
        dataset = dataset_loader.create_mlx_dataset()
        
        # Training arguments
        training_args = TrainingArgs(
            batch_size=self.config.batch_size,
            iters=len(dataset) // self.config.batch_size * self.config.num_epochs,
            learning_rate=self.config.learning_rate,
            warmup_steps=self.config.warmup_steps,
            save_every=100,
            val_batches=10,
            grad_checkpoint=self.config.grad_checkpoint
        )
        
        # Create optimizer
        optimizer = optim.AdamW(
            learning_rate=self.config.learning_rate,
            weight_decay=0.01
        )
        
        # Training loop with Metal acceleration
        start_time = time.time()
        
        # Use MLX trainer
        train(
            model=self.model,
            tokenizer=self.tokenizer,
            args=training_args,
            train_dataset=dataset,
            optimizer=optimizer
        )
        
        training_time = time.time() - start_time
        print(f"✅ Training completed in {training_time/60:.1f} minutes")
        
        # Memory stats
        if mx.metal.is_available():
            memory_used = mx.metal.get_active_memory() / 1e9
            memory_peak = mx.metal.get_peak_memory() / 1e9
            print(f"📊 Metal memory: {memory_used:.1f} GB used, {memory_peak:.1f} GB peak")
    
    def inference(self, prompt: str, max_tokens: int = 256):
        """Run inference with the fine-tuned model"""
        
        # Format prompt
        formatted = f"### Instruction:\nSen bir Türk telekom asistanısın.\n\n### Input:\n{prompt}\n\n### Response:\n"
        
        # Generate with MLX
        response = generate(
            self.model,
            self.tokenizer,
            prompt=formatted,
            max_tokens=max_tokens,
            temp=0.7,
            top_p=0.9
        )
        
        return response
    
    def save_model(self, path: str):
        """Save fine-tuned model"""
        
        save_path = Path(path)
        save_path.mkdir(exist_ok=True)
        
        # Save LoRA weights
        mx.save(str(save_path / "lora_weights.npz"), self.model.state_dict())
        
        # Save config
        with open(save_path / "config.json", 'w') as f:
            json.dump({
                "model_name": self.config.model_name,
                "lora_rank": self.config.lora_rank,
                "lora_alpha": self.config.lora_alpha
            }, f)
        
        print(f"✅ Model saved to {save_path}")

def benchmark_m4_max():
    """Benchmark M4 Max performance"""
    
    print("🏎️ M4 MAX BENCHMARK")
    print("="*60)
    
    # Check system info
    import platform
    import subprocess
    
    print(f"System: {platform.system()} {platform.release()}")
    print(f"Processor: {platform.processor()}")
    
    # Check Metal info
    if mx.metal.is_available():
        print(f"Metal GPU: Available")
        print(f"Metal Memory: {mx.metal.get_active_memory() / 1e9:.1f} GB")
    
    # Memory info
    try:
        vm_stat = subprocess.check_output(['vm_stat']).decode('utf-8')
        lines = vm_stat.split('\n')
        for line in lines[:10]:
            print(f"  {line}")
    except:
        pass
    
    print("\n📊 Expected Performance:")
    print("  - 4-bit model size: ~2.5 GB")
    print("  - Training speed: ~50-100 samples/sec")
    print("  - Inference speed: ~20-30 tokens/sec")
    print("  - Max batch size: 8-16 with 64GB RAM")

def main():
    print("🚀 GEMMA 3N MLX TRAINER FOR M4 MAX")
    print("="*60)
    
    # Run benchmark
    benchmark_m4_max()
    
    # Initialize config
    config = GemmaTelcoConfig()
    
    # Create trainer
    trainer = MLXTelcoTrainer(config)
    
    # Train model
    trainer.train("data")
    
    # Test inference
    print("\n🧪 Testing inference...")
    test_prompts = [
        "eSIM'im çalışmıyor",
        "Faturamda hata var",
        "Internet paketimi değiştirmek istiyorum"
    ]
    
    for prompt in test_prompts:
        response = trainer.inference(prompt)
        print(f"\n📞 Customer: {prompt}")
        print(f"🤖 Agent: {response[:100]}...")
    
    # Save model
    trainer.save_model("gemma_telco_mlx")
    
    print("\n✅ Training complete!")
    print("📦 Model saved to gemma_telco_mlx/")

if __name__ == "__main__":
    main()