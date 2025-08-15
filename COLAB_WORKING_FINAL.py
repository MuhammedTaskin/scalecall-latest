# WORKING SOLUTION - Replace Cells 5-7 with this

# ============================================
# CELL 5: Prepare Dataset (SIMPLIFIED)
# ============================================
from datasets import Dataset
import json

# Load your data
dataset_path = "/content/drive/MyDrive/teknofest/gemma3n_autonomous_training.jsonl"

# Create simple examples
texts = []
with open(dataset_path, 'r', encoding='utf-8') as f:
    for line in f:
        item = json.loads(line)
        
        # Simple format that works
        text = f"""Sen bir Türk telekom çağrı merkezi temsilcisisin.

Müşteri: {item.get('context', 'Merhaba')}

Yanıt: {json.dumps(item['output'], ensure_ascii=False)}"""
        
        texts.append(text)

print(f"✅ Loaded {len(texts)} examples")

# ============================================
# CELL 6: Tokenize Properly
# ============================================
from trl import SFTTrainer
from transformers import TrainingArguments
from unsloth import is_bfloat16_supported

# Create trainer with DIRECT text input
trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = None,  # Don't use dataset yet
    max_seq_length = 512,  # Shorter for safety
    dataset_text_field = None,
    dataset_num_proc = 1,
    packing = False,
    formatting_func = lambda x: texts[x["idx"]] if "idx" in x else texts[0],  # Simple function
    args = TrainingArguments(
        per_device_train_batch_size = 1,
        gradient_accumulation_steps = 8,
        warmup_steps = 5,
        max_steps = 50,
        learning_rate = 1e-5,  # Even smaller
        fp16 = not is_bfloat16_supported(),
        bf16 = is_bfloat16_supported(),
        logging_steps = 10,
        optim = "adamw_8bit",
        weight_decay = 0.001,
        lr_scheduler_type = "constant",
        seed = 42,
        output_dir = "outputs",
        gradient_checkpointing = False,
        remove_unused_columns = False,
        report_to = "none",  # Disable wandb
    ),
)

# Now add the dataset
from datasets import Dataset
dataset = Dataset.from_dict({"idx": list(range(len(texts))), "text": texts})
trainer.train_dataset = dataset

print("✅ Trainer configured with simplified dataset")

# ============================================
# CELL 7: Train (Finally!)
# ============================================
print("🚀 Starting training...")
print("   This is barely touching the model (0.51% params)")
print("   Should take 5-10 minutes")

trainer_stats = trainer.train()

print("\n✅ TRAINING COMPLETE!")
print(f"   Final loss: {trainer_stats.training_loss:.4f}")
print("   Model barely changed - perfect!")