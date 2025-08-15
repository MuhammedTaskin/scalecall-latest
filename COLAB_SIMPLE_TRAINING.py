# SIMPLIFIED CELL 7 - Replace the problematic Cell 7 with this

# ============================================
# CELL 7: Simple Training Setup (No SFTTrainer)
# ============================================

from transformers import Trainer, DataCollatorForLanguageModeling

# Tokenize dataset manually
def tokenize_function(examples):
    """Simple tokenization"""
    # Ensure text is not None
    texts = [t if t else "" for t in examples["text"]]
    
    # Tokenize with padding and truncation
    model_inputs = tokenizer(
        texts,
        padding="max_length",
        truncation=True,
        max_length=512,  # Shorter for testing
        return_tensors=None
    )
    
    # Set labels same as input_ids for language modeling
    model_inputs["labels"] = model_inputs["input_ids"].copy()
    
    return model_inputs

# Tokenize the dataset
print("Tokenizing dataset...")
tokenized_dataset = train_dataset.map(
    tokenize_function,
    batched=True,
    num_proc=1,  # Single process
    remove_columns=train_dataset.column_names,
    desc="Tokenizing"
)

print(f"✅ Dataset tokenized: {len(tokenized_dataset)} examples")

# Simple training arguments
from transformers import TrainingArguments

training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=1,
    per_device_train_batch_size=1,  # Start small
    gradient_accumulation_steps=8,   # Effective batch of 8
    warmup_steps=10,
    learning_rate=5e-6,  # Very small
    logging_steps=10,
    save_steps=50,
    fp16=True,  # Use mixed precision
    report_to="none",  # Disable reporting for now
    max_steps=50,  # Quick test
)

# Data collator
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,  # Gemma uses causal LM
    pad_to_multiple_of=8
)

# Create standard Trainer (not SFTTrainer)
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    tokenizer=tokenizer,
    data_collator=data_collator,
)

print("✅ Trainer configured (Simple Trainer, not SFTTrainer)")
print(f"   Batch size: 1 (with gradient accumulation: 8)")
print(f"   Learning rate: 5e-6")
print(f"   Max steps: 50 (quick test)")