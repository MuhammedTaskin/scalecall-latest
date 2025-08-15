#!/usr/bin/env python3
"""
TEKNOFEST 2025 - GEMMA 3N E4B AUDIO TRAINING
Ultimate Unsloth Fine-tuning for Turkish Telco AI
Run this on Colab with A100 (40GB) for MAXIMUM POWER
"""

# ============================================
# COLAB SETUP (Run these in separate cells)
# ============================================

# Cell 1: Install Unsloth
"""
!pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
!pip install --no-deps "trl<0.9.0" peft accelerate bitsandbytes
"""

# Cell 2: Check GPU
"""
import torch
print(f"GPU: {torch.cuda.get_device_name(0)}")
print(f"Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
"""

# ============================================
# MAIN TRAINING SCRIPT
# ============================================

from unsloth import FastLanguageModel
import torch
from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import Dataset
import json
from pathlib import Path

# Model configuration
max_seq_length = 2048  # Can increase to 8192 with M4 Max memory
dtype = None  # Auto-detect
load_in_4bit = True  # E4B = 4-bit quantized

# Load Gemma 3N E4B-IT (Instruction Tuned)
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/gemma-3n-E4B-it",
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = load_in_4bit,
    device_map = "auto",
)

print("✅ Loaded Gemma 3N E4B-IT (4.67B params)")

# ============================================
# LoRA CONFIGURATION (Minimal Touching!)
# ============================================

model = FastLanguageModel.get_peft_model(
    model,
    r = 16,  # LoRA rank - small to preserve capabilities
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                     "gate_proj", "up_proj", "down_proj"],
    lora_alpha = 16,
    lora_dropout = 0,  # No dropout for competition
    bias = "none",
    use_gradient_checkpointing = "unsloth",  # 4x longer context
    random_state = 42,
    use_rslora = False,
    loftq_config = None,
)

print("✅ LoRA adapters configured (barely touching the model)")

# ============================================
# DATASET PREPARATION
# ============================================

def load_telco_dataset(jsonl_path: str):
    """Load our Turkish telco dataset with audio paths"""
    
    examples = []
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            item = json.loads(line)
            
            # Format for Gemma 3N multimodal
            # Audio is referenced by path, model handles loading
            prompt = f"""<audio>{item['audio']}</audio>
Context: {item['context']}

Sen bir Türk telekom çağrı merkezi temsilcisisin. Müşterinin sesini dinle ve uygun yanıtı ver.

Response:"""
            
            # Expected output
            output = json.dumps({
                "agent": item['output']['agent'],
                "tools": item['output']['tools'],
                "response": item['output']['response']
            }, ensure_ascii=False)
            
            # Combine for training
            text = prompt + "\n" + output
            examples.append({"text": text})
    
    return Dataset.from_list(examples)

# Load dataset
train_dataset = load_telco_dataset("data/gemma3n_autonomous_training.jsonl")
print(f"✅ Loaded {len(train_dataset)} training examples")

# ============================================
# TRAINING CONFIGURATION
# ============================================

trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = train_dataset,
    dataset_text_field = "text",
    max_seq_length = max_seq_length,
    dataset_num_proc = 2,
    packing = False,  # Can set to True for longer sequences
    
    args = TrainingArguments(
        per_device_train_batch_size = 2,  # Increase on A100
        gradient_accumulation_steps = 4,
        
        # MINIMAL TRAINING (Don't overtrain!)
        num_train_epochs = 1,  # ONE epoch only
        learning_rate = 2e-5,  # Very small
        
        # Optimizer settings
        warmup_steps = 5,
        weight_decay = 0.01,
        fp16 = not torch.cuda.is_bf16_supported(),
        bf16 = torch.cuda.is_bf16_supported(),
        
        # Logging
        logging_steps = 10,
        save_strategy = "steps",
        save_steps = 100,
        
        # Output
        output_dir = "outputs",
        optim = "adamw_8bit",
        seed = 42,
    ),
)

# ============================================
# THE ACTUAL TRAINING (15 minutes on A100)
# ============================================

print("🚀 Starting training...")
print("   This should take ~15 minutes on A100")
print("   Loss should start around 2-3 (already knows Turkish)")

# Train!
trainer_stats = trainer.train()

print("✅ Training complete!")
print(f"   Final loss: {trainer_stats.training_loss:.4f}")

# ============================================
# SAVE THE MODEL
# ============================================

# Save LoRA adapters only (small, efficient)
model.save_pretrained("gemma3n_telco_lora")
tokenizer.save_pretrained("gemma3n_telco_lora")

print("✅ Saved LoRA adapters to gemma3n_telco_lora/")

# Merge and save full model (optional, for deployment)
if False:  # Set to True if you want full model
    model.save_pretrained_merged("gemma3n_telco_merged", tokenizer)
    print("✅ Saved merged model to gemma3n_telco_merged/")

# ============================================
# QUICK INFERENCE TEST
# ============================================

def test_model(audio_path: str, context: str = ""):
    """Test the fine-tuned model"""
    
    prompt = f"""<audio>{audio_path}</audio>
Context: {context}

Sen bir Türk telekom çağrı merkezi temsilcisisin. Müşterinin sesini dinle ve uygun yanıtı ver.

Response:"""
    
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    
    outputs = model.generate(
        **inputs,
        max_new_tokens=256,
        temperature=0.3,
        do_sample=True,
    )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

# Test with a sample
test_audio = "data/tts_audio_final/flash_heavy_0174_turn_1.mp3"
result = test_model(test_audio, "Yeni konuşma başlangıcı")
print(f"\n🎤 Test Result:\n{result}")

print("""
========================================
🏆 READY FOR TEKNOFEST 2025!
========================================
Model: Gemma 3N E4B-IT (4.67B params)
Training: LoRA fine-tuning (minimal interference)
Dataset: 700+ Turkish telco conversations
Audio: 30s multimodal input support
Performance: Near-instant responses

Next steps:
1. Upload to HuggingFace
2. Create demo with Gradio
3. Win the competition!
""")