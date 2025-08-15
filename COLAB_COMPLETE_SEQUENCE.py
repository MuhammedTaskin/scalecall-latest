# COMPLETE TRAINING SEQUENCE FOR COLAB
# Run these cells in order

# ============================================
# CELL 1: Install
# ============================================
!pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
!pip install --no-deps xformers trl peft accelerate bitsandbytes

# ============================================
# CELL 2: Mount Drive
# ============================================
from google.colab import drive
drive.mount('/content/drive')

# ============================================
# CELL 3: Load Model
# ============================================
from unsloth import FastLanguageModel
from transformers import AutoTokenizer
import torch

max_seq_length = 2048
dtype = None
load_in_4bit = True

model, _ = FastLanguageModel.from_pretrained(
    model_name = "unsloth/gemma-3n-E4B-it",
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = load_in_4bit,
)

# Use Gemma-2 tokenizer (Gemma3N tokenizer is broken)
tokenizer = AutoTokenizer.from_pretrained("google/gemma-2-2b-it")
print("✅ Model and tokenizer loaded")

# ============================================
# CELL 4: Add LoRA
# ============================================
model = FastLanguageModel.get_peft_model(
    model,
    r = 16,
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                      "gate_proj", "up_proj", "down_proj"],
    lora_alpha = 16,
    lora_dropout = 0,
    bias = "none",
    use_gradient_checkpointing = False,  # OFF
    random_state = 42,
)
print("✅ LoRA adapters added")

# ============================================
# CELL 5: Prepare Dataset (MUST RUN THIS!)
# ============================================
from datasets import Dataset
import json

# Simple prompt format
alpaca_prompt = """### Instruction:
{}

### Input:
{}

### Response:
{}"""

EOS_TOKEN = tokenizer.eos_token if tokenizer.eos_token else "</s>"

# Load data and format directly
dataset_path = "/content/drive/MyDrive/teknofest/gemma3n_autonomous_training.jsonl"
formatted_data = []

with open(dataset_path, 'r', encoding='utf-8') as f:
    for line in f:
        item = json.loads(line)
        
        instruction = "Sen bir Türk telekom çağrı merkezi temsilcisisin."
        input_text = f"Konuşma: {item.get('context', 'Yeni konuşma')}"
        output_text = json.dumps(item['output'], ensure_ascii=False)
        
        # Format the full text
        full_text = alpaca_prompt.format(instruction, input_text, output_text) + EOS_TOKEN
        
        formatted_data.append({"text": full_text})

# Create dataset from already formatted texts
dataset = Dataset.from_list(formatted_data)
print(f"✅ Dataset prepared: {len(dataset)} examples")

# Show sample
print("\n📝 Sample text:")
print(dataset[0]["text"][:200] + "...")

# ============================================
# CELL 6: Setup Training
# ============================================
from trl import SFTTrainer
from transformers import TrainingArguments
from unsloth import is_bfloat16_supported

trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,  # NOW dataset exists!
    dataset_text_field = "text",
    max_seq_length = max_seq_length,
    dataset_num_proc = 1,
    packing = False,
    args = TrainingArguments(
        per_device_train_batch_size = 1,
        gradient_accumulation_steps = 8,
        warmup_steps = 5,
        max_steps = 50,
        learning_rate = 2e-5,
        fp16 = not is_bfloat16_supported(),
        bf16 = is_bfloat16_supported(),
        logging_steps = 10,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 42,
        output_dir = "outputs",
        gradient_checkpointing = False,
        remove_unused_columns = False,
    ),
)
print("✅ Trainer configured")

# ============================================
# CELL 7: Train!
# ============================================
trainer_stats = trainer.train()
print("✅ Training complete!")
print(f"   Loss: {trainer_stats.training_loss:.4f}")

# ============================================
# CELL 8: Save
# ============================================
model.save_pretrained("gemma3n_lora")
tokenizer.save_pretrained("gemma3n_lora")
print("✅ Model saved!")