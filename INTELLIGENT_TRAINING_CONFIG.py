#!/usr/bin/env python3
"""
🔥 INTELLIGENT ADAPTIVE TRAINING SYSTEM - TEKNOFEST 2025
Ultra-smart training with dynamic learning rate, loss-aware adjustments, and early stopping
"""

from trl import SFTTrainer
from transformers import TrainingArguments, TrainerCallback
from unsloth import is_bfloat16_supported
import torch
import numpy as np
from typing import Dict, List, Optional
import json
from datetime import datetime
import matplotlib.pyplot as plt

class IntelligentLearningRateScheduler(TrainerCallback):
    """
    🧠 ULTRA-SMART Learning Rate Scheduler
    - Monitors loss patterns
    - Detects plateaus and adjusts dynamically
    - Implements aggressive decay when overfitting detected
    """
    
    def __init__(self, 
                 initial_lr: float = 5e-5,
                 min_lr: float = 1e-6,
                 patience: int = 5,
                 factor: float = 0.5,
                 spike_threshold: float = 0.2,
                 plateau_threshold: float = 0.01):
        
        self.initial_lr = initial_lr
        self.min_lr = min_lr
        self.patience = patience
        self.factor = factor
        self.spike_threshold = spike_threshold
        self.plateau_threshold = plateau_threshold
        
        # Tracking metrics
        self.loss_history = []
        self.lr_history = []
        self.best_loss = float('inf')
        self.patience_counter = 0
        self.last_lr_change = 0
        self.plateau_counter = 0
        
        print(f"""
╔════════════════════════════════════════════════════════════╗
║  🧠 INTELLIGENT LR SCHEDULER ACTIVATED                     ║
╠════════════════════════════════════════════════════════════╣
║  • Initial LR: {initial_lr:.2e}                                 ║
║  • Min LR: {min_lr:.2e}                                         ║
║  • Patience: {patience} steps                                    ║
║  • Reduction factor: {factor}                                   ║
╚════════════════════════════════════════════════════════════╝
        """)
    
    def on_log(self, args, state, control, logs=None, **kwargs):
        """Monitor each logging step and adjust LR intelligently"""
        
        if logs and 'loss' in logs:
            current_loss = logs['loss']
            current_step = state.global_step
            current_lr = state.log_history[-1].get('learning_rate', self.initial_lr) if state.log_history else self.initial_lr
            
            self.loss_history.append(current_loss)
            self.lr_history.append(current_lr)
            
            # Analyze loss pattern
            analysis = self._analyze_loss_pattern()
            
            # Make intelligent decisions
            new_lr = self._decide_lr_adjustment(current_loss, current_lr, current_step, analysis)
            
            if new_lr != current_lr:
                self._update_lr(kwargs['model'], new_lr)
                print(f"\n🔄 LR Adjusted: {current_lr:.2e} → {new_lr:.2e} (Step {current_step})")
                print(f"   Reason: {analysis['reason']}")
                self.last_lr_change = current_step
            
            # Print intelligent status
            if current_step % 5 == 0:
                self._print_smart_status(current_step, current_loss, current_lr, analysis)
    
    def _analyze_loss_pattern(self) -> Dict:
        """Analyze recent loss patterns for intelligent decisions"""
        
        if len(self.loss_history) < 3:
            return {"pattern": "warming_up", "reason": "Initial training phase"}
        
        recent_losses = self.loss_history[-10:]  # Last 10 steps
        
        # Check for loss spike (sudden increase)
        if len(recent_losses) >= 2:
            loss_change = recent_losses[-1] - recent_losses[-2]
            if loss_change > self.spike_threshold:
                return {
                    "pattern": "spike",
                    "reason": f"Loss spike detected ({loss_change:.3f} increase)",
                    "action": "reduce_lr_aggressive"
                }
        
        # Check for plateau (no improvement)
        if len(recent_losses) >= 5:
            std_dev = np.std(recent_losses[-5:])
            if std_dev < self.plateau_threshold:
                self.plateau_counter += 1
                if self.plateau_counter >= self.patience:
                    return {
                        "pattern": "plateau",
                        "reason": f"Loss plateau for {self.plateau_counter} steps",
                        "action": "reduce_lr_moderate"
                    }
        else:
            self.plateau_counter = 0
        
        # Check for consistent improvement
        if len(recent_losses) >= 3:
            improving = all(recent_losses[i] > recent_losses[i+1] for i in range(len(recent_losses)-1))
            if improving:
                return {
                    "pattern": "improving",
                    "reason": "Consistent loss decrease",
                    "action": "maintain_lr"
                }
        
        # Check for oscillation
        if len(recent_losses) >= 4:
            diffs = [recent_losses[i+1] - recent_losses[i] for i in range(len(recent_losses)-1)]
            sign_changes = sum(1 for i in range(len(diffs)-1) if diffs[i] * diffs[i+1] < 0)
            if sign_changes >= len(diffs) * 0.6:  # 60% sign changes
                return {
                    "pattern": "oscillating",
                    "reason": "Loss oscillation detected",
                    "action": "reduce_lr_slight"
                }
        
        return {"pattern": "normal", "reason": "Standard training progress", "action": "maintain_lr"}
    
    def _decide_lr_adjustment(self, current_loss: float, current_lr: float, 
                              current_step: int, analysis: Dict) -> float:
        """Make intelligent LR adjustment decision"""
        
        # Don't change too frequently
        if current_step - self.last_lr_change < 3:
            return current_lr
        
        action = analysis.get('action', 'maintain_lr')
        
        if action == 'reduce_lr_aggressive':
            # Aggressive reduction for spikes
            new_lr = max(current_lr * 0.3, self.min_lr)
            
        elif action == 'reduce_lr_moderate':
            # Moderate reduction for plateaus
            new_lr = max(current_lr * self.factor, self.min_lr)
            
        elif action == 'reduce_lr_slight':
            # Slight reduction for oscillations
            new_lr = max(current_lr * 0.8, self.min_lr)
            
        elif action == 'maintain_lr':
            # Keep current LR
            new_lr = current_lr
            
        else:
            new_lr = current_lr
        
        # Special case: If loss is very low, be more conservative
        if current_loss < 0.5:
            new_lr = min(new_lr, 1e-5)
        
        return new_lr
    
    def _update_lr(self, model, new_lr: float):
        """Update learning rate in optimizer"""
        if hasattr(model, 'optimizer'):
            for param_group in model.optimizer.param_groups:
                param_group['lr'] = new_lr
    
    def _print_smart_status(self, step: int, loss: float, lr: float, analysis: Dict):
        """Print intelligent training status"""
        
        # Calculate trend
        if len(self.loss_history) >= 10:
            recent_avg = np.mean(self.loss_history[-5:])
            older_avg = np.mean(self.loss_history[-10:-5])
            trend = "📈" if recent_avg > older_avg else "📉" if recent_avg < older_avg else "➡️"
        else:
            trend = "🔄"
        
        print(f"\n📊 Step {step} | Loss: {loss:.4f} {trend} | LR: {lr:.2e} | Pattern: {analysis['pattern']}")


class AdaptiveEarlyStoppingCallback(TrainerCallback):
    """
    🛑 Smart Early Stopping with adaptive patience
    """
    
    def __init__(self, initial_patience: int = 10, min_delta: float = 0.001):
        self.initial_patience = initial_patience
        self.patience = initial_patience
        self.min_delta = min_delta
        self.best_loss = float('inf')
        self.wait = 0
        self.stopped = False
        
    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs and 'loss' in logs:
            current_loss = logs['loss']
            
            if current_loss < self.best_loss - self.min_delta:
                self.best_loss = current_loss
                self.wait = 0
                # Increase patience if we're still improving
                self.patience = min(self.patience + 1, self.initial_patience * 2)
            else:
                self.wait += 1
                
            if self.wait >= self.patience:
                print(f"\n🛑 Early stopping triggered! Best loss: {self.best_loss:.4f}")
                control.should_training_stop = True
                self.stopped = True
                
        return control


class GradientMonitorCallback(TrainerCallback):
    """
    📈 Monitor gradient norms and detect issues
    """
    
    def __init__(self, explosion_threshold: float = 10.0):
        self.explosion_threshold = explosion_threshold
        self.gradient_history = []
        
    def on_before_optimizer_step(self, args, state, control, **kwargs):
        model = kwargs['model']
        
        # Calculate gradient norm
        total_norm = 0
        for p in model.parameters():
            if p.grad is not None:
                param_norm = p.grad.data.norm(2)
                total_norm += param_norm.item() ** 2
        total_norm = total_norm ** 0.5
        
        self.gradient_history.append(total_norm)
        
        # Detect gradient explosion
        if total_norm > self.explosion_threshold:
            print(f"\n⚠️ Gradient explosion detected! Norm: {total_norm:.2f}")
            # Could implement gradient clipping here
        
        # Print status every 10 steps
        if state.global_step % 10 == 0 and state.global_step > 0:
            avg_norm = np.mean(self.gradient_history[-10:])
            print(f"   Gradient norm (avg): {avg_norm:.3f}")


def create_intelligent_trainer(model, tokenizer, dataset, max_seq_length=2048):
    """
    🚀 Create ultra-intelligent trainer with all smart features
    """
    
    print("""
╔════════════════════════════════════════════════════════════╗
║  🧠 INTELLIGENT TRAINING SYSTEM v2.0                       ║
╠════════════════════════════════════════════════════════════╣
║  Features:                                                  ║
║  • Dynamic learning rate adjustment                        ║
║  • Loss pattern analysis                                   ║
║  • Adaptive early stopping                                 ║
║  • Gradient monitoring                                     ║
║  • Smart batch scheduling                                  ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Calculate optimal batch size based on model size
    model_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    optimal_batch_size = 1 if model_params > 1e9 else 2
    gradient_accumulation = 16 // optimal_batch_size
    
    # Smart training arguments
    training_args = TrainingArguments(
        per_device_train_batch_size=optimal_batch_size,
        gradient_accumulation_steps=gradient_accumulation,
        
        # Smart warmup (10% of total steps)
        warmup_ratio=0.1,
        max_steps=500,  # More steps for better convergence
        
        # Start with higher LR, let intelligent scheduler handle it
        learning_rate=5e-5,
        
        # Advanced optimization
        optim="adamw_torch_fused" if torch.cuda.is_available() else "adamw_8bit",
        adam_beta1=0.9,
        adam_beta2=0.999,
        adam_epsilon=1e-8,
        weight_decay=0.01,
        
        # Initial scheduler (will be overridden by our intelligent one)
        lr_scheduler_type="cosine",
        
        # Mixed precision for speed
        fp16=not is_bfloat16_supported(),
        bf16=is_bfloat16_supported(),
        tf32=True if torch.cuda.is_available() else False,
        
        # Gradient handling
        max_grad_norm=1.0,  # Gradient clipping
        gradient_checkpointing=True if model_params > 2e9 else False,
        
        # Logging
        logging_steps=1,
        logging_first_step=True,
        
        # Saving
        output_dir="./intelligent_teknofest_outputs",
        save_strategy="steps",
        save_steps=10,
        save_total_limit=3,
        load_best_model_at_end=True,
        
        # Other optimizations
        dataloader_num_workers=2,
        remove_unused_columns=False,
        push_to_hub=False,
        report_to="none",
        
        # Seed for reproducibility
        seed=42,
        data_seed=42,
        
        # Advanced features
        torch_compile=False,  # Set True if using PyTorch 2.0+
        ddp_find_unused_parameters=False,
        dataloader_pin_memory=True,
    )
    
    # Initialize callbacks
    intelligent_lr_scheduler = IntelligentLearningRateScheduler(
        initial_lr=5e-5,
        min_lr=1e-6,
        patience=5,
        factor=0.5
    )
    
    early_stopping = AdaptiveEarlyStoppingCallback(
        initial_patience=15,
        min_delta=0.0001
    )
    
    gradient_monitor = GradientMonitorCallback(
        explosion_threshold=10.0
    )
    
    # Create trainer with all intelligent features
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="text",
        max_seq_length=max_seq_length,
        dataset_num_proc=4,  # Use more processors
        packing=False,  # Don't pack sequences for better learning
        args=training_args,
        callbacks=[intelligent_lr_scheduler, early_stopping, gradient_monitor],
    )
    
    # Print configuration summary
    print(f"""
📋 CONFIGURATION SUMMARY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Model Parameters: {model_params/1e6:.1f}M
  Batch Size: {optimal_batch_size} × {gradient_accumulation} = {optimal_batch_size * gradient_accumulation}
  Max Steps: {training_args.max_steps}
  Initial LR: {training_args.learning_rate:.2e}
  Warmup Steps: {int(training_args.max_steps * training_args.warmup_ratio)}
  Optimizer: {training_args.optim}
  Mixed Precision: {'bf16' if training_args.bf16 else 'fp16' if training_args.fp16 else 'fp32'}
  Gradient Checkpointing: {training_args.gradient_checkpointing}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    
    return trainer


class TrainingAnalyzer:
    """
    📊 Analyze training metrics and provide insights
    """
    
    def __init__(self, trainer):
        self.trainer = trainer
        self.metrics = {
            'loss_history': [],
            'lr_history': [],
            'gradient_norms': [],
            'training_speed': []
        }
    
    def analyze_and_plot(self):
        """Generate training analysis and plots"""
        
        if not self.trainer.state.log_history:
            print("No training history to analyze")
            return
        
        # Extract metrics
        for log in self.trainer.state.log_history:
            if 'loss' in log:
                self.metrics['loss_history'].append(log['loss'])
            if 'learning_rate' in log:
                self.metrics['lr_history'].append(log['learning_rate'])
        
        # Analysis
        print("""
╔════════════════════════════════════════════════════════════╗
║  📊 TRAINING ANALYSIS REPORT                               ║
╚════════════════════════════════════════════════════════════╝
        """)
        
        if self.metrics['loss_history']:
            initial_loss = self.metrics['loss_history'][0]
            final_loss = self.metrics['loss_history'][-1]
            improvement = (initial_loss - final_loss) / initial_loss * 100
            
            print(f"  📉 Loss Reduction: {improvement:.1f}%")
            print(f"     Initial: {initial_loss:.4f}")
            print(f"     Final: {final_loss:.4f}")
            
            # Find best checkpoint
            best_loss_idx = np.argmin(self.metrics['loss_history'])
            best_loss = self.metrics['loss_history'][best_loss_idx]
            print(f"  🏆 Best Loss: {best_loss:.4f} (Step {best_loss_idx})")
            
            # Convergence analysis
            if len(self.metrics['loss_history']) > 20:
                recent_std = np.std(self.metrics['loss_history'][-10:])
                if recent_std < 0.01:
                    print("  ✅ Model has converged!")
                elif recent_std < 0.05:
                    print("  🔄 Model is converging...")
                else:
                    print("  ⚠️ Model still learning actively")
        
        # Learning rate analysis
        if self.metrics['lr_history']:
            print(f"\n  🎯 Learning Rate Journey:")
            print(f"     Start: {self.metrics['lr_history'][0]:.2e}")
            print(f"     End: {self.metrics['lr_history'][-1]:.2e}")
            print(f"     Reductions: {sum(1 for i in range(1, len(self.metrics['lr_history'])) if self.metrics['lr_history'][i] < self.metrics['lr_history'][i-1])}")
        
        return self.metrics


# Example usage
def train_with_intelligence(model, tokenizer, dataset, max_seq_length=2048):
    """
    🚀 Complete intelligent training pipeline
    """
    
    # Create intelligent trainer
    trainer = create_intelligent_trainer(model, tokenizer, dataset, max_seq_length)
    
    print("\n🏃 Starting intelligent training...")
    print("━" * 60)
    
    # Train with real-time monitoring
    try:
        trainer.train()
        
        print("\n✅ Training completed successfully!")
        
        # Analyze results
        analyzer = TrainingAnalyzer(trainer)
        metrics = analyzer.analyze_and_plot()
        
        # Save the best model
        print("\n💾 Saving model...")
        trainer.save_model("./best_teknofest_model")
        tokenizer.save_pretrained("./best_teknofest_model")
        
        print("✅ Model saved to ./best_teknofest_model")
        
        return trainer, metrics
        
    except KeyboardInterrupt:
        print("\n⚠️ Training interrupted by user")
        print("💾 Saving checkpoint...")
        trainer.save_model("./interrupted_checkpoint")
        return trainer, None
    
    except Exception as e:
        print(f"\n❌ Training failed: {e}")
        raise


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║  🧠 INTELLIGENT TRAINING SYSTEM                            ║
    ╠════════════════════════════════════════════════════════════╣
    ║  This is a standalone configuration module.                ║
    ║  Import and use with your model:                           ║
    ║                                                             ║
    ║  from INTELLIGENT_TRAINING_CONFIG import train_with_intelligence ║
    ║  trainer, metrics = train_with_intelligence(model, tokenizer, dataset) ║
    ╚════════════════════════════════════════════════════════════╝
    """)