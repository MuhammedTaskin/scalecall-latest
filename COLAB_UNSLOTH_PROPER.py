#!/usr/bin/env python3
"""
PROPER UNSLOTH SETUP FOR GEMMA 3N
Based on Unsloth documentation
"""

# ============================================
# CELL 1: Install Unsloth (UPDATED VERSION)
# ============================================
!pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
!pip install --no-deps xformers trl peft accelerate bitsandbytes

# ============================================
# CELL 2: Import and Setup
# ============================================
from unsloth import FastLanguageModel
import torch

max_seq_length = 2048
dtype = None  # None for auto detection
load_in_4bit = True  # Use 4bit quantization

# ============================================
# CELL 3: Load Model PROPERLY
# ============================================
# Use the proper Unsloth model ID
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/gemma-3n-E4B-it",  # Correct Unsloth model
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = load_in_4bit,
)

print("✅ Model loaded successfully")

# ============================================
# CELL 4: Add LoRA adapters
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

print("✅ LoRA adapters added")

# ============================================
# CELL 5: Prepare Dataset (SIMPLIFIED)
# ============================================
from datasets import Dataset
import json

# Load your JSONL file
dataset_path = "/content/drive/MyDrive/teknofest/gemma3n_autonomous_training.jsonl"

# Create simple text examples
alpaca_prompt = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{}

### Input:
{}

### Response:
{}"""

EOS_TOKEN = tokenizer.eos_token

def formatting_prompts_func(examples):
    instructions = examples["instruction"]
    inputs       = examples["input"]
    outputs      = examples["output"]
    texts = []
    for instruction, input, output in zip(instructions, inputs, outputs):
        text = alpaca_prompt.format(instruction, input, output) + EOS_TOKEN
        texts.append(text)
    return {"text": texts}

# Load and format data
data = []
with open(dataset_path, 'r', encoding='utf-8') as f:
    for line in f:
        item = json.loads(line)
        data.append({
            "instruction": "Sen bir Türk telekom çağrı merkezi temsilcisisin.",
            "input": f"Müşteri konuşması: {item.get('context', '')}",
            "output": json.dumps(item['output'], ensure_ascii=False)
        })

dataset = Dataset.from_list(data)
dataset = dataset.map(formatting_prompts_func, batched=True)

print(f"✅ Dataset prepared: {len(dataset)} examples")

# ============================================
# CELL 6: Training with Unsloth's SFTTrainer
# ============================================
from trl import SFTTrainer
from transformers import TrainingArguments
from unsloth import is_bfloat16_supported

trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "text",
    max_seq_length = max_seq_length,
    dataset_num_proc = 2,
    packing = False,
    args = TrainingArguments(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 5,
        max_steps = 100,
        learning_rate = 2e-4,
        fp16 = not is_bfloat16_supported(),
        bf16 = is_bfloat16_supported(),
        logging_steps = 10,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 42,
        output_dir = "outputs",
    ),
)

print("✅ Trainer configured")

# ============================================
# CELL 7: Train
# ============================================
trainer_stats = trainer.train()

print("✅ Training complete!")
print(f"   Loss: {trainer_stats.training_loss:.4f}")

# ============================================
# CELL 8: Save Model
# ============================================
model.save_pretrained("gemma3n_lora")
tokenizer.save_pretrained("gemma3n_lora")

print("✅ Model saved!")

# Optional: Save to 16bit for later use
# model.save_pretrained_merged("model_16bit", tokenizer, save_method="merged_16bit")

# ============================================
# CELL 9: Inference
# ============================================
FastLanguageModel.for_inference(model)

inputs = tokenizer(
    [
        alpaca_prompt.format(
            "Sen bir Türk telekom çağrı merkezi temsilcisisin.",
            "Müşteri: eSIM'im çalışmıyor, yardım eder misiniz?",
            "",
        )
    ], return_tensors = "pt").to("cuda")

outputs = model.generate(**inputs, max_new_tokens=128, use_cache=True)
print(tokenizer.batch_decode(outputs))