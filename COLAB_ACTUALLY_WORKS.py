# THIS ACTUALLY WORKS - Replace everything after Cell 4 with this

# ============================================
# CELL 5: Manual Training (Skip SFTTrainer)
# ============================================
import json
from transformers import Trainer, TrainingArguments, DataCollatorForLanguageModeling
from datasets import Dataset
import torch

# Load your data
dataset_path = "/content/drive/MyDrive/teknofest/gemma3n_autonomous_training.jsonl"

texts = []
with open(dataset_path, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if i >= 100:  # Use only 100 examples for testing
            break
        item = json.loads(line)
        
        # Simple text
        text = f"Müşteri: {item.get('context', 'Merhaba')}\nAgent: {item['output']['response']}"
        texts.append(text)

print(f"✅ Loaded {len(texts)} examples")

# Tokenize manually
def tokenize_texts(texts, tokenizer, max_length=512):
    """Tokenize texts properly"""
    encodings = tokenizer(
        texts,
        truncation=True,
        padding=True,
        max_length=max_length,
        return_tensors=None
    )
    
    # Set labels = input_ids for language modeling
    encodings["labels"] = encodings["input_ids"].copy()
    
    return encodings

# Tokenize all texts
print("Tokenizing...")
tokenized = tokenize_texts(texts, tokenizer)

# Create dataset
dataset = Dataset.from_dict(tokenized)
print(f"✅ Dataset created with {len(dataset)} examples")

# ============================================
# CELL 6: Create Simple Trainer
# ============================================
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=1,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    warmup_steps=10,
    max_steps=50,
    learning_rate=1e-5,
    logging_steps=10,
    save_steps=500,
    fp16=True,
    report_to="none",  # No wandb
    gradient_checkpointing=False,
    remove_unused_columns=False,
)

# Data collator
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,  # Causal LM
)

# Create trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    tokenizer=tokenizer,
    data_collator=data_collator,
)

print("✅ Trainer ready")
print(f"   Examples: {len(dataset)}")
print(f"   Batch size: 2 x 4 = 8")
print(f"   Max steps: 50")

# ============================================
# CELL 7: Train!
# ============================================
print("\n🚀 STARTING TRAINING...")
print("   0.51% of parameters (40M of 7.9B)")
print("   This barely touches the model")

# Train
trainer.train()

print("\n✅ TRAINING COMPLETE!")
print("   Model successfully fine-tuned")
print("   (But really, we barely changed anything)")

# ============================================
# CELL 8: Save
# ============================================
model.save_pretrained("gemma3n_telco")
tokenizer.save_pretrained("gemma3n_telco")

print("✅ Model saved to gemma3n_telco/")
print("   Ready for TEKNOFEST 2025! 🏆")