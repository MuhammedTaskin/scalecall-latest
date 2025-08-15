#!/usr/bin/env python3
"""
Fixed Training Arguments for TEKNOFEST - No evaluation needed
"""

from transformers import TrainingArguments
from unsloth import is_bfloat16_supported

# Calculate optimal settings
total_steps = 100  # Adjust based on your dataset
save_every = 5     # Save checkpoint every 5 steps
warmup = int(total_steps * 0.1)  # 10% warmup

# FIXED VERSION - Without load_best_model_at_end
training_args = TrainingArguments(
    # Batch settings
    per_device_train_batch_size=1,
    gradient_accumulation_steps=16,
    
    # Steps and warmup
    max_steps=total_steps,
    warmup_steps=warmup,
    
    # Learning rate (start higher, callbacks will adjust)
    learning_rate=5e-5,
    
    # Optimizer
    optim="adamw_8bit",
    weight_decay=0.01,
    lr_scheduler_type="cosine",
    
    # Mixed precision
    fp16=not is_bfloat16_supported(),
    bf16=is_bfloat16_supported(),
    # tf32=True,  # Removed - not supported on your GPU
    
    # Gradient
    max_grad_norm=1.0,
    gradient_checkpointing=True,
    
    # Logging
    logging_steps=1,
    logging_first_step=True,
    
    # AGGRESSIVE SAVING (FIXED)
    output_dir="./outputs",
    save_strategy="steps",
    save_steps=save_every,
    save_total_limit=None,  # Keep ALL checkpoints locally
    save_safetensors=True,
    
    # REMOVED load_best_model_at_end - We track best manually in callback
    # load_best_model_at_end=False,  # Removed completely
    # metric_for_best_model="loss",  # Not needed
    # greater_is_better=False,  # Not needed
    
    # Others
    remove_unused_columns=False,
    report_to="none",
    seed=42,
    data_seed=42,
    
    # Performance
    dataloader_num_workers=2,
    dataloader_pin_memory=True,
)

print(f"✅ Training configured (FIXED):")
print(f"   Total steps: {total_steps}")
print(f"   Save every: {save_every} steps")
print(f"   Warmup: {warmup} steps")
print(f"   Effective batch: {16}")
print(f"   Best model tracking: Via callback (not args)")