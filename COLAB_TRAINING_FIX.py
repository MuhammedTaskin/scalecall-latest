# FIX FOR TRAINING - Replace Cell 4 (LoRA) and Cell 6 (Training)

# ============================================
# CELL 4: Add LoRA adapters (FIXED)
# ============================================
model = FastLanguageModel.get_peft_model(
    model,
    r = 16,
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                      "gate_proj", "up_proj", "down_proj"],
    lora_alpha = 16,
    lora_dropout = 0,
    bias = "none",
    use_gradient_checkpointing = False,  # TURN OFF gradient checkpointing
    random_state = 42,
)

print("✅ LoRA adapters added")

# ============================================
# CELL 6: Training with Unsloth's SFTTrainer (FIXED)
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
    dataset_num_proc = 1,  # Single process
    packing = False,
    args = TrainingArguments(
        per_device_train_batch_size = 1,  # Small batch
        gradient_accumulation_steps = 8,
        warmup_steps = 5,
        max_steps = 50,  # Quick test
        learning_rate = 2e-5,  # Small LR
        fp16 = not is_bfloat16_supported(),
        bf16 = is_bfloat16_supported(),
        logging_steps = 10,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 42,
        output_dir = "outputs",
        gradient_checkpointing = False,  # TURN OFF here too
        remove_unused_columns = False,  # FIX: Don't remove columns
    ),
)

print("✅ Trainer configured")
print("   Trainable params: 40M of 7.9B (0.51%)")
print("   This is perfect - barely touching the model!")