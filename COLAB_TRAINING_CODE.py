#!/usr/bin/env python3
"""
COPY THIS CODE INTO COLAB CELLS
Each section is a separate cell
"""

# ============================================
# CELL 1: Check GPU
# ============================================
!nvidia-smi

# ============================================
# CELL 2: Install Unsloth
# ============================================
!pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
!pip install --no-deps "trl<0.9.0" peft accelerate bitsandbytes

# ============================================
# CELL 3: Mount Drive and Import
# ============================================
from google.colab import drive
drive.mount('/content/drive')

from unsloth import FastLanguageModel
import torch
from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import Dataset
import json

print(f"PyTorch: {torch.__version__}")
print(f"CUDA: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}")

# ============================================
# CELL 4: Load Model
# ============================================
max_seq_length = 2048
dtype = None
load_in_4bit = True

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/gemma-3n-E4B-it",
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = load_in_4bit,
    device_map = "auto",
)

print("✅ Loaded Gemma 3N E4B-IT")
print(f"   Parameters: 4.67B")
print(f"   Multimodal: Audio + Text")
print(f"   Context: {max_seq_length} tokens")

# ============================================
# CELL 5: Configure LoRA
# ============================================
model = FastLanguageModel.get_peft_model(
    model,
    r = 16,
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                     "gate_proj", "up_proj", "down_proj"],
    lora_alpha = 16,
    lora_dropout = 0,
    bias = "none",
    use_gradient_checkpointing = "unsloth",
    random_state = 42,
)

print("✅ LoRA adapters configured")
print("   Rank: 16 (efficient parameter adaptation)")
print("   Target: Attention + MLP layers")

# ============================================
# CELL 6: Load Dataset
# ============================================
def format_telco_prompt(item):
    """Format for Gemma 3N multimodal training"""
    
    # Build instruction
    instruction = f"""Sen bir Türk telekom çağrı merkezi temsilcisisin. Müşteri konuşması: {item.get('context', 'Yeni konuşma')}

Müşterinin sesini dinle ve uygun yanıtı ver."""
    
    # Expected output
    output = json.dumps({
        "agent": item['output']['agent'],
        "tools": item['output']['tools'],
        "response": item['output']['response']
    }, ensure_ascii=False)
    
    # Format for Gemma instruction tuning
    text = f"""<bos><start_of_turn>user
{instruction}<end_of_turn>
<start_of_turn>model
{output}<end_of_turn><eos>"""
    
    return text

# Load dataset
dataset_path = "/content/drive/MyDrive/teknofest/gemma3n_autonomous_training.jsonl"

examples = []
with open(dataset_path, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            item = json.loads(line)
            text = format_telco_prompt(item)
            if text:  # Ensure text is not None
                examples.append({"text": text})
        except Exception as e:
            print(f"Skipping line due to error: {e}")
            continue

train_dataset = Dataset.from_list(examples)
print(f"✅ Loaded {len(train_dataset)} training examples")

# ============================================
# CELL 7: Training Configuration
# ============================================
training_args = TrainingArguments(
    per_device_train_batch_size = 4,  # Optimized for V100/A100 memory
    gradient_accumulation_steps = 2,   # Effective batch size of 8
    warmup_steps = 1,                  # Quick adaptation phase
    num_train_epochs = 1,              # Sufficient for domain adaptation
    learning_rate = 1e-5,              # Conservative learning rate for stability
    fp16 = not torch.cuda.is_bf16_supported(),
    bf16 = torch.cuda.is_bf16_supported(),
    logging_steps = 1,                 # Detailed training metrics
    optim = "adamw_8bit",
    weight_decay = 0.001,              # L2 regularization
    lr_scheduler_type = "constant",    # Stable learning throughout
    seed = 42,
    output_dir = "outputs",
    save_strategy = "steps",
    save_steps = 50,                   # Regular checkpointing
    report_to = "tensorboard",         # Training visualization
    max_steps = 100,                   # Prevent overfitting
)

trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = train_dataset,
    dataset_text_field = "text",
    max_seq_length = max_seq_length,
    dataset_num_proc = 1,  # Use single process to avoid multiprocessing issues
    packing = False,
    args = training_args,
)

print("✅ Trainer configured")
print(f"   Batch size: {training_args.per_device_train_batch_size}")
print(f"   Epochs: {training_args.num_train_epochs}")
print(f"   Learning rate: {training_args.learning_rate}")

# ============================================
# CELL 8: Train
# ============================================
print("🚀 Starting training...")
print("   Initial loss expected: 2-3")
print("   Estimated duration: 10-15 minutes on V100/A100")

trainer_stats = trainer.train()

print("\n✅ TRAINING COMPLETE!")
print(f"   Final loss: {trainer_stats.training_loss:.4f}")
print(f"   Total steps: {trainer_stats.global_step}")

# ============================================
# CELL 9: Save Model
# ============================================
model.save_pretrained("gemma3n_telco_lora")
tokenizer.save_pretrained("gemma3n_telco_lora")

print("✅ Saved LoRA adapters to gemma3n_telco_lora/")
print("   Adapter size: ~20MB")

# Zip for download
!zip -r gemma3n_telco_lora.zip gemma3n_telco_lora/
print("\n📦 Created gemma3n_telco_lora.zip for download")

# ============================================
# CELL 10: Test Model
# ============================================
def test_model(audio_path: str, context: str = ""):
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

# Test
test_audio = "data/tts_audio_final/flash_heavy_0174_turn_1.mp3"
result = test_model(test_audio)
print("🎤 Test Result:")
print(result)