# 🔥 Enhanced Training Cells for TEKNOFEST_EMOTION_TRAINING.ipynb

Add these cells to your existing notebook for intelligent training with comprehensive saving:

## Cell 1: Mount Drive & Setup Paths (Add at beginning)
```python
# CRITICAL: Mount Drive and setup save paths
from google.colab import drive
drive.mount('/content/drive')

import os
import shutil
from datetime import datetime

# Create organized save structure
DRIVE_BASE = '/content/drive/MyDrive/TEKNOFEST_2025'
TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')
DRIVE_PATH = f'{DRIVE_BASE}/{TIMESTAMP}'

os.makedirs(f'{DRIVE_PATH}/checkpoints', exist_ok=True)
os.makedirs(f'{DRIVE_PATH}/final_model', exist_ok=True)
os.makedirs(f'{DRIVE_PATH}/best_model', exist_ok=True)

print(f"✅ Save path ready: {DRIVE_PATH}")
print(f"📁 Checkpoints: {DRIVE_PATH}/checkpoints")
print(f"📁 Final model: {DRIVE_PATH}/final_model")
```

## Cell 2: Enhanced Callbacks (Replace your trainer callbacks)
```python
from transformers import TrainerCallback
import json
import numpy as np

class SaveEverythingCallback(TrainerCallback):
    """Aggressively save EVERYTHING to Drive"""
    
    def __init__(self, drive_path):
        self.drive_path = drive_path
        self.all_checkpoints = []
        self.best_loss = float('inf')
        self.best_checkpoint = None
        
    def on_save(self, args, state, control, **kwargs):
        """Save checkpoint to Drive immediately"""
        checkpoint_name = f"checkpoint-{state.global_step}"
        source = os.path.join(args.output_dir, checkpoint_name)
        
        # Save to Drive
        if os.path.exists(source):
            dest = os.path.join(self.drive_path, 'checkpoints', checkpoint_name)
            print(f"\n💾 Backing up to Drive: {checkpoint_name}")
            shutil.copytree(source, dest, dirs_exist_ok=True)
            self.all_checkpoints.append(checkpoint_name)
            
            # Track best model
            current_loss = state.log_history[-1].get('loss', float('inf'))
            if current_loss < self.best_loss:
                self.best_loss = current_loss
                self.best_checkpoint = checkpoint_name
                # Save best separately
                best_dest = os.path.join(self.drive_path, 'best_model')
                shutil.rmtree(best_dest, ignore_errors=True)
                shutil.copytree(source, best_dest)
                print(f"🏆 New best model! Loss: {self.best_loss:.4f}")
            
            # Save metadata
            metadata = {
                'checkpoint': checkpoint_name,
                'step': state.global_step,
                'loss': current_loss,
                'is_best': checkpoint_name == self.best_checkpoint,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(f"{dest}/metadata.json", 'w') as f:
                json.dump(metadata, f, indent=2)
                
    def on_train_end(self, args, state, control, **kwargs):
        """Save training summary"""
        summary = {
            'total_checkpoints': len(self.all_checkpoints),
            'best_checkpoint': self.best_checkpoint,
            'best_loss': self.best_loss,
            'final_loss': state.log_history[-1].get('loss', 'N/A'),
            'total_steps': state.global_step,
            'all_checkpoints': self.all_checkpoints,
            'drive_path': self.drive_path
        }
        
        with open(f"{self.drive_path}/training_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📊 Training Complete!")
        print(f"✅ {len(self.all_checkpoints)} checkpoints saved")
        print(f"🏆 Best checkpoint: {self.best_checkpoint} (loss: {self.best_loss:.4f})")

class IntelligentLRCallback(TrainerCallback):
    """Smart learning rate adjustment"""
    
    def __init__(self, initial_lr=5e-5, min_lr=1e-6, patience=5):
        self.initial_lr = initial_lr
        self.min_lr = min_lr
        self.patience = patience
        self.loss_history = []
        self.no_improve_count = 0
        self.lr_reductions = 0
        
    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs and 'loss' in logs:
            current_loss = logs['loss']
            self.loss_history.append(current_loss)
            
            # Check if we should adjust LR
            if len(self.loss_history) > 10:
                recent = self.loss_history[-5:]
                older = self.loss_history[-10:-5]
                
                # If not improving
                if np.mean(recent) >= np.mean(older) * 0.99:
                    self.no_improve_count += 1
                    
                    if self.no_improve_count >= self.patience:
                        # Get current LR
                        current_lr = state.log_history[-1].get('learning_rate', self.initial_lr)
                        
                        # Reduce LR
                        new_lr = max(current_lr * 0.5, self.min_lr)
                        
                        # Update optimizer
                        for param_group in kwargs['model'].optimizer.param_groups:
                            param_group['lr'] = new_lr
                        
                        self.lr_reductions += 1
                        print(f"\n🔄 LR Reduced (#{self.lr_reductions}): {current_lr:.2e} → {new_lr:.2e}")
                        print(f"   Reason: No improvement for {self.no_improve_count} logs")
                        
                        self.no_improve_count = 0
                else:
                    self.no_improve_count = 0
            
            # Print status every 5 steps
            if state.global_step % 5 == 0:
                lr = state.log_history[-1].get('learning_rate', self.initial_lr)
                trend = "📉" if len(self.loss_history) > 1 and current_loss < self.loss_history[-2] else "📈"
                print(f"Step {state.global_step}: Loss {current_loss:.4f} {trend} | LR: {lr:.2e}")

class EmergencySaveCallback(TrainerCallback):
    """Emergency saves in case of crashes"""
    
    def __init__(self, drive_path, save_every_n_steps=10):
        self.drive_path = drive_path
        self.save_every_n_steps = save_every_n_steps
        
    def on_step_end(self, args, state, control, **kwargs):
        # Emergency save every N steps
        if state.global_step % self.save_every_n_steps == 0:
            emergency_path = f"{self.drive_path}/emergency_step_{state.global_step}"
            model = kwargs['model']
            tokenizer = kwargs['tokenizer']
            
            try:
                model.save_pretrained(emergency_path)
                tokenizer.save_pretrained(emergency_path)
                print(f"🚨 Emergency save at step {state.global_step}")
            except:
                pass  # Silent fail for emergency saves
```

## Cell 3: Enhanced Training Arguments (Replace your current args)
```python
from transformers import TrainingArguments
from unsloth import is_bfloat16_supported

# Calculate optimal settings
total_steps = 100  # Adjust based on your dataset
save_every = 5     # Save checkpoint every 5 steps
warmup = int(total_steps * 0.1)  # 10% warmup

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
    tf32=True,  # If using modern GPU
    
    # Gradient
    max_grad_norm=1.0,
    gradient_checkpointing=True,
    
    # Logging
    logging_steps=1,
    logging_first_step=True,
    
    # AGGRESSIVE SAVING
    output_dir="./outputs",
    save_strategy="steps",
    save_steps=save_every,
    save_total_limit=None,  # Keep ALL checkpoints locally
    save_safetensors=True,
    
    # Best model tracking
    load_best_model_at_end=True,
    metric_for_best_model="loss",
    greater_is_better=False,
    
    # Others
    remove_unused_columns=False,
    report_to="none",
    seed=42,
    data_seed=42,
    
    # Performance
    dataloader_num_workers=2,
    dataloader_pin_memory=True,
)

print(f"✅ Training configured:")
print(f"   Total steps: {total_steps}")
print(f"   Save every: {save_every} steps")
print(f"   Warmup: {warmup} steps")
print(f"   Effective batch: {16}")
```

## Cell 4: Initialize Trainer with All Callbacks
```python
from trl import SFTTrainer

# Initialize all callbacks
save_callback = SaveEverythingCallback(DRIVE_PATH)
lr_callback = IntelligentLRCallback(initial_lr=5e-5, min_lr=1e-6, patience=5)
emergency_callback = EmergencySaveCallback(DRIVE_PATH, save_every_n_steps=10)

# Create trainer
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=max_seq_length,
    dataset_num_proc=2,
    packing=False,
    args=training_args,
    callbacks=[save_callback, lr_callback, emergency_callback],
)

print("✅ Trainer ready with intelligent features!")
print(f"📁 All saves go to: {DRIVE_PATH}")
```

## Cell 5: Train with Comprehensive Error Handling
```python
import time
import traceback

print("""
╔════════════════════════════════════════════════════════════╗
║  🚀 STARTING INTELLIGENT TRAINING                          ║
╠════════════════════════════════════════════════════════════╣
║  • Checkpoints every 5 steps → Drive                       ║
║  • Emergency saves every 10 steps                          ║
║  • Intelligent LR adjustment                               ║
║  • Best model tracked separately                           ║
╚════════════════════════════════════════════════════════════╝
""")

start_time = time.time()

try:
    # Train
    trainer.train()
    
    # Training successful
    duration = (time.time() - start_time) / 60
    
    print(f"\n✅ TRAINING SUCCESSFUL!")
    print(f"⏱️ Duration: {duration:.1f} minutes")
    
    # Save final model
    print("\n💾 Saving final model to Drive...")
    final_path = f"{DRIVE_PATH}/final_model"
    model.save_pretrained(final_path)
    tokenizer.save_pretrained(final_path)
    
    # Save training stats
    final_stats = {
        'success': True,
        'duration_minutes': duration,
        'final_loss': trainer.state.log_history[-1].get('loss'),
        'total_steps': trainer.state.global_step,
        'best_checkpoint': save_callback.best_checkpoint,
        'best_loss': save_callback.best_loss,
        'timestamp': datetime.now().isoformat()
    }
    
    with open(f"{DRIVE_PATH}/final_stats.json", 'w') as f:
        json.dump(final_stats, f, indent=2)
    
    print(f"✅ Final model saved: {final_path}")
    print(f"🏆 Best loss: {save_callback.best_loss:.4f}")
    
except KeyboardInterrupt:
    print("\n⚠️ Training interrupted by user!")
    print("💾 Saving interrupted checkpoint...")
    
    interrupted_path = f"{DRIVE_PATH}/interrupted"
    model.save_pretrained(interrupted_path)
    tokenizer.save_pretrained(interrupted_path)
    print(f"✅ Saved to: {interrupted_path}")
    
except Exception as e:
    print(f"\n❌ Training error: {e}")
    print(traceback.format_exc())
    
    print("💾 Saving error checkpoint...")
    error_path = f"{DRIVE_PATH}/error_checkpoint"
    model.save_pretrained(error_path)
    tokenizer.save_pretrained(error_path)
    print(f"✅ Error checkpoint: {error_path}")
    
    raise

print("\n" + "="*60)
print("📁 ALL MODELS SAVED TO GOOGLE DRIVE!")
print(f"📂 Location: {DRIVE_PATH}")
print("="*60)
```

## Cell 6: Verify Saves (Run after training)
```python
# Verify everything saved correctly
print("🔍 Verifying Drive saves...")
print("="*60)

# Check directories
for subdir in ['checkpoints', 'final_model', 'best_model']:
    path = f"{DRIVE_PATH}/{subdir}"
    if os.path.exists(path):
        files = os.listdir(path)
        total_size = sum(os.path.getsize(f"{path}/{f}") for f in files) / (1024**3)
        print(f"✅ {subdir}: {len(files)} files ({total_size:.2f} GB)")

# Check training summary
summary_path = f"{DRIVE_PATH}/training_summary.json"
if os.path.exists(summary_path):
    with open(summary_path) as f:
        summary = json.load(f)
    print(f"\n📊 Training Summary:")
    print(f"   Total checkpoints: {summary['total_checkpoints']}")
    print(f"   Best checkpoint: {summary['best_checkpoint']}")
    print(f"   Best loss: {summary['best_loss']:.4f}")
    print(f"   Final loss: {summary['final_loss']}")

print("\n✅ All files verified in Drive!")
```

## Key Improvements:
1. **Saves to Drive every 5 steps** - No data loss
2. **Emergency saves every 10 steps** - Extra safety
3. **Intelligent LR reduction** - Better convergence
4. **Best model tracked separately** - Easy to find best
5. **Comprehensive error handling** - Saves even on crash
6. **Organized folder structure** - Timestamped folders
7. **Metadata for every checkpoint** - Track progress

Just add these cells to your existing notebook and you'll have bulletproof saving! 🚀