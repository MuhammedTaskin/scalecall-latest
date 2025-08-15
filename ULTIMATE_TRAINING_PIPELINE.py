"""
🚀 ULTIMATE TRAINING PIPELINE
Elite Turkish Telco Agent Training with Maximum Optimization
Competition-Winning Fine-Tuning Setup
"""

import os
import json
import torch
import gc
import time
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

# Core ML libraries
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    TrainingArguments,
    EarlyStoppingCallback,
    DataCollatorForLanguageModeling
)
from datasets import Dataset, DatasetDict
from trl import SFTTrainer, SFTConfig
from peft import LoraConfig, TaskType, get_peft_model
import wandb

# Unsloth for optimization
try:
    from unsloth import FastModel
    from unsloth.chat_templates import get_chat_template, standardize_data_formats, train_on_responses_only
    UNSLOTH_AVAILABLE = True
    print("✅ Unsloth loaded - Ultimate optimization enabled")
except ImportError:
    UNSLOTH_AVAILABLE = False
    print("⚠️ Unsloth not available - Using standard HuggingFace")

@dataclass
class UltimateTrainingConfig:
    """Ultimate training configuration for competition-winning performance."""
    
    # Model settings
    model_name: str = "unsloth/gemma-3n-E4B-it"
    max_seq_length: int = 1024
    load_in_4bit: bool = True
    
    # LoRA configuration (optimized for flexibility)
    lora_r: int = 32  # Higher rank for better adaptation
    lora_alpha: int = 64  # Strong adaptation signal
    lora_dropout: float = 0.1  # Balanced dropout
    lora_target_modules: List[str] = None  # Auto-detect
    lora_bias: str = "none"
    
    # Training hyperparameters (competition-optimized)
    learning_rate: float = 1e-4  # Stable learning
    warmup_ratio: float = 0.1  # Gradual warmup
    weight_decay: float = 0.05  # Regularization
    max_grad_norm: float = 0.3  # Gradient clipping
    label_smoothing_factor: float = 0.1  # Anti-overconfidence
    
    # Batch configuration
    per_device_train_batch_size: int = 1
    per_device_eval_batch_size: int = 2
    gradient_accumulation_steps: int = 8  # Effective batch = 8
    dataloader_num_workers: int = 4
    
    # Training schedule
    max_steps: int = 1000
    eval_steps: int = 100
    save_steps: int = 200
    logging_steps: int = 25
    
    # Optimization settings
    optim: str = "adamw_8bit"  # Memory efficient
    lr_scheduler_type: str = "cosine"  # Smooth decay
    fp16: bool = True  # Faster training
    
    # Early stopping & checkpointing
    early_stopping_patience: int = 5
    load_best_model_at_end: bool = True
    metric_for_best_model: str = "eval_loss"
    greater_is_better: bool = False
    
    # Advanced features
    gradient_checkpointing: bool = True  # Memory optimization
    dataloader_pin_memory: bool = True  # GPU optimization
    remove_unused_columns: bool = False  # Keep all data
    
    # Curriculum learning stages
    enable_curriculum: bool = True
    curriculum_stages: int = 4

class UltimateMemoryOptimizer:
    """Memory optimization utilities for maximum efficiency."""
    
    @staticmethod
    def optimize_gpu_memory():
        """Optimize GPU memory usage."""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            gc.collect()
            
            # Set memory growth
            if hasattr(torch.cuda, 'memory_fraction'):
                torch.cuda.set_per_process_memory_fraction(0.85)
            
            print(f"🔧 GPU Memory: {torch.cuda.get_device_properties(0).total_memory // 1024**3}GB")
            print(f"💾 Available: {torch.cuda.memory_allocated() // 1024**2}MB allocated")
    
    @staticmethod
    def setup_mixed_precision():
        """Setup optimal mixed precision training."""
        if torch.cuda.is_available():
            torch.backends.cudnn.benchmark = True
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            print("⚡ Mixed precision optimizations enabled")

class UltimateDataProcessor:
    """Advanced data processing for Turkish telco dialogs."""
    
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.max_length = 1024
        
    def process_dialog_for_training(self, dialog: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single dialog for optimal training."""
        
        # Convert conversations to chat format
        conversations = dialog["conversations"]
        
        # Build chat messages
        messages = []
        for turn in conversations:
            role = turn["role"]
            content = turn["content"][0]["text"] if turn["content"] else ""
            
            if role == "user":
                messages.append({"role": "user", "content": content})
            elif role == "assistant":
                messages.append({"role": "assistant", "content": content})
        
        # Apply chat template
        formatted_text = self.tokenizer.apply_chat_template(
            messages, 
            tokenize=False, 
            add_generation_prompt=False
        )
        
        # Add metadata as system context
        system_context = f"Context: {dialog.get('context', 'GENERAL')}, Scenario: {dialog.get('scenario_type', 'unknown')}"
        if dialog.get('has_noise', False):
            system_context += ", ASR_NOISE: true"
        
        return {
            "text": formatted_text,
            "system_context": system_context,
            "quality_tier": dialog.get("quality_tier", "intermediate"),
            "scenario_type": dialog.get("scenario_type", "unknown"),
            "has_noise": dialog.get("has_noise", False)
        }
    
    def create_curriculum_datasets(self, raw_data: List[Dict]) -> Dict[str, Dataset]:
        """Create curriculum learning datasets."""
        
        # Stage 1: Foundation (simple dialogs)
        foundation_data = [
            d for d in raw_data 
            if d.get("quality_tier") in ["foundation", "intermediate"]
            and d.get("scenario_type") in ["single_tool", "simple_dialog"]
        ]
        
        # Stage 2: Reasoning (multi-step)
        reasoning_data = [
            d for d in raw_data
            if d.get("scenario_type") in ["multi_step", "context_switching"]
            and d.get("quality_tier") in ["intermediate", "advanced"]
        ]
        
        # Stage 3: Robustness (noise + edge cases)
        robustness_data = [
            d for d in raw_data
            if d.get("has_noise") or d.get("quality_tier") in ["robustness", "precision"]
        ]
        
        # Stage 4: Integration (all data mixed)
        integration_data = raw_data
        
        # Process each stage
        stages = {
            "foundation": foundation_data,
            "reasoning": reasoning_data, 
            "robustness": robustness_data,
            "integration": integration_data
        }
        
        processed_stages = {}
        for stage_name, stage_data in stages.items():
            processed = [self.process_dialog_for_training(d) for d in stage_data]
            processed_stages[stage_name] = Dataset.from_list(processed)
            print(f"📊 {stage_name.title()} stage: {len(processed)} samples")
        
        return processed_stages

class UltimateEvaluator:
    """Comprehensive evaluation system for Turkish telco agent."""
    
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        
        # Turkish-specific evaluation patterns
        self.turkish_patterns = {
            "politeness": ["hanım", "bey", "lütfen", "rica ederim", "memnuniyetle"],
            "tool_reasoning": ["kontrol ediyorum", "sorgusu yapıyorum", "bakıyorum"],
            "brevity": [".", "!", "?"]  # Should end with punctuation
        }
        
        # Tool call validation
        self.valid_tools = {
            "verify_user", "get_user_info", "check_device_registration",
            "reissue_activation_code", "get_activation_steps", "get_activation_status",
            "get_available_packages", "change_package", "create_support_ticket"
        }
    
    def evaluate_predictions(self, predictions: List[str], references: List[str]) -> Dict[str, float]:
        """Comprehensive evaluation of model predictions."""
        
        scores = {
            "turkish_quality": [],
            "tool_validity": [],
            "politeness": [],
            "brevity": [],
            "json_validity": [],
            "reasoning_presence": []
        }
        
        for pred, ref in zip(predictions, references):
            scores["turkish_quality"].append(self._evaluate_turkish_quality(pred))
            scores["tool_validity"].append(self._evaluate_tool_validity(pred))
            scores["politeness"].append(self._evaluate_politeness(pred))
            scores["brevity"].append(self._evaluate_brevity(pred))
            scores["json_validity"].append(self._evaluate_json_validity(pred))
            scores["reasoning_presence"].append(self._evaluate_reasoning(pred))
        
        # Aggregate scores
        final_scores = {}
        for metric, values in scores.items():
            final_scores[metric] = np.mean(values)
        
        # Overall competition score
        final_scores["competition_score"] = (
            final_scores["turkish_quality"] * 0.25 +
            final_scores["tool_validity"] * 0.25 +
            final_scores["politeness"] * 0.15 +
            final_scores["brevity"] * 0.1 +
            final_scores["json_validity"] * 0.15 +
            final_scores["reasoning_presence"] * 0.1
        )
        
        return final_scores
    
    def _evaluate_turkish_quality(self, text: str) -> float:
        """Evaluate Turkish language quality."""
        # Check for Turkish characters
        turkish_chars = "çğıöşüÇĞIÖŞÜ"
        has_turkish = any(char in text for char in turkish_chars)
        
        # Check sentence structure (simple heuristic)
        sentences = text.split('.')
        avg_length = np.mean([len(s.split()) for s in sentences if s.strip()])
        
        # Turkish sentences should be 5-15 words typically
        length_score = 1.0 if 5 <= avg_length <= 15 else 0.7
        char_score = 1.0 if has_turkish else 0.5
        
        return (length_score + char_score) / 2
    
    def _evaluate_tool_validity(self, text: str) -> float:
        """Evaluate tool call validity."""
        import json
        import re
        
        tool_calls = re.findall(r'"tool_call"[^}]+}[^}]*}', text)
        if not tool_calls:
            return 1.0  # No tool calls is valid
        
        valid_calls = 0
        for call in tool_calls:
            try:
                # Try to parse the tool call
                full_json = "{" + call + "}"
                parsed = json.loads(full_json)
                
                if "tool_call" in parsed:
                    tool_name = parsed["tool_call"].get("name", "")
                    if tool_name in self.valid_tools:
                        valid_calls += 1
            except:
                continue
        
        return valid_calls / len(tool_calls) if tool_calls else 1.0
    
    def _evaluate_politeness(self, text: str) -> float:
        """Evaluate Turkish politeness markers."""
        politeness_count = sum(
            1 for marker in self.turkish_patterns["politeness"]
            if marker.lower() in text.lower()
        )
        return min(1.0, politeness_count / 2)
    
    def _evaluate_brevity(self, text: str) -> float:
        """Evaluate response brevity (≤2 sentences)."""
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        if len(sentences) <= 2:
            return 1.0
        elif len(sentences) <= 3:
            return 0.7
        else:
            return 0.3
    
    def _evaluate_json_validity(self, text: str) -> float:
        """Evaluate JSON validity in tool calls."""
        import json
        import re
        
        json_patterns = re.findall(r'\{[^}]*"tool_call"[^}]*\}', text)
        if not json_patterns:
            return 1.0  # No JSON is valid
        
        valid_json = 0
        for pattern in json_patterns:
            try:
                json.loads(pattern)
                valid_json += 1
            except:
                continue
        
        return valid_json / len(json_patterns) if json_patterns else 1.0
    
    def _evaluate_reasoning(self, text: str) -> float:
        """Evaluate presence of reasoning indicators."""
        reasoning_words = ["çünkü", "için", "bu nedenle", "kontrol", "sorgula"]
        reasoning_count = sum(1 for word in reasoning_words if word in text.lower())
        return min(1.0, reasoning_count / 3)

class UltimateTrainer:
    """Ultimate training pipeline orchestrator."""
    
    def __init__(self, config: UltimateTrainingConfig):
        self.config = config
        self.model = None
        self.tokenizer = None
        self.data_processor = None
        self.evaluator = None
        
        # Setup optimizations
        UltimateMemoryOptimizer.optimize_gpu_memory()
        UltimateMemoryOptimizer.setup_mixed_precision()
    
    def setup_model_and_tokenizer(self):
        """Setup model and tokenizer with ultimate optimization."""
        print(f"🚀 Loading {self.config.model_name}...")
        
        if UNSLOTH_AVAILABLE:
            # Use Unsloth for maximum optimization
            self.model, self.tokenizer = FastModel.from_pretrained(
                model_name=self.config.model_name,
                max_seq_length=self.config.max_seq_length,
                load_in_4bit=self.config.load_in_4bit,
                dtype=torch.float16
            )
            
            # Apply chat template
            self.tokenizer = get_chat_template(
                self.tokenizer,
                chat_template="gemma-3",
                mapping={"role": "role", "content": "content", "user": "user", "assistant": "assistant"}
            )
            
            # Add LoRA adapters
            self.model = FastModel.get_peft_model(
                self.model,
                r=self.config.lora_r,
                lora_alpha=self.config.lora_alpha,
                lora_dropout=self.config.lora_dropout,
                bias=self.config.lora_bias,
                target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
                use_gradient_checkpointing="unsloth",
                random_state=42
            )
            
            print("✅ Unsloth model loaded with ultimate optimization")
            
        else:
            # Standard HuggingFace setup
            self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.config.model_name,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            
            # LoRA configuration
            peft_config = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                r=self.config.lora_r,
                lora_alpha=self.config.lora_alpha,
                lora_dropout=self.config.lora_dropout,
                bias=self.config.lora_bias
            )
            
            self.model = get_peft_model(self.model, peft_config)
            print("✅ Standard model loaded with LoRA")
        
        # Setup processors
        self.data_processor = UltimateDataProcessor(self.tokenizer)
        self.evaluator = UltimateEvaluator(self.tokenizer)
        
        # Print model info
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in self.model.parameters())
        print(f"🎯 Trainable parameters: {trainable_params:,} ({trainable_params/total_params*100:.2f}%)")
    
    def train_with_curriculum(self, raw_data: List[Dict], output_dir: str = "./turkish_telco_model"):
        """Train with curriculum learning for maximum performance."""
        
        print("🚀 Starting curriculum-based training...")
        
        # Create curriculum datasets
        curriculum_datasets = self.data_processor.create_curriculum_datasets(raw_data)
        
        # Training stages
        stages = ["foundation", "reasoning", "robustness", "integration"]
        stage_configs = [
            {"max_steps": 200, "learning_rate": 2e-4},
            {"max_steps": 400, "learning_rate": 1e-4}, 
            {"max_steps": 300, "learning_rate": 5e-5},
            {"max_steps": 200, "learning_rate": 2e-5}
        ]
        
        best_scores = []
        
        for stage_idx, (stage_name, stage_config) in enumerate(zip(stages, stage_configs)):
            print(f"\n🎓 Training Stage {stage_idx + 1}: {stage_name.title()}")
            
            # Get stage dataset
            train_dataset = curriculum_datasets[stage_name]
            
            # Create validation split
            split_dataset = train_dataset.train_test_split(test_size=0.1, seed=42)
            
            # Stage-specific training arguments
            training_args = SFTConfig(
                output_dir=f"{output_dir}/stage_{stage_idx + 1}_{stage_name}",
                max_steps=stage_config["max_steps"],
                learning_rate=stage_config["learning_rate"],
                
                per_device_train_batch_size=self.config.per_device_train_batch_size,
                per_device_eval_batch_size=self.config.per_device_eval_batch_size,
                gradient_accumulation_steps=self.config.gradient_accumulation_steps,
                
                warmup_ratio=self.config.warmup_ratio,
                weight_decay=self.config.weight_decay,
                max_grad_norm=self.config.max_grad_norm,
                label_smoothing_factor=self.config.label_smoothing_factor,
                
                logging_steps=self.config.logging_steps,
                eval_strategy="steps",
                eval_steps=self.config.eval_steps,
                save_strategy="steps",
                save_steps=self.config.save_steps,
                
                load_best_model_at_end=True,
                metric_for_best_model="eval_loss",
                greater_is_better=False,
                
                fp16=self.config.fp16,
                gradient_checkpointing=self.config.gradient_checkpointing,
                dataloader_num_workers=self.config.dataloader_num_workers,
                dataloader_pin_memory=self.config.dataloader_pin_memory,
                
                optim=self.config.optim,
                lr_scheduler_type=self.config.lr_scheduler_type,
                
                report_to="none",
                remove_unused_columns=False,
                dataset_text_field="text",
                
                seed=42,
                data_seed=42
            )
            
            # Create trainer
            trainer = SFTTrainer(
                model=self.model,
                tokenizer=self.tokenizer,
                args=training_args,
                train_dataset=split_dataset["train"],
                eval_dataset=split_dataset["test"],
                callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
            )
            
            # Apply response-only training for chat format
            if UNSLOTH_AVAILABLE:
                trainer = train_on_responses_only(
                    trainer,
                    instruction_part="<start_of_turn>user\n",
                    response_part="<start_of_turn>model\n"
                )
            
            # Train stage
            print(f"⚡ Training {stage_name} stage...")
            start_time = time.time()
            
            trainer.train()
            
            stage_time = time.time() - start_time
            print(f"✅ Stage {stage_name} completed in {stage_time/60:.1f} minutes")
            
            # Evaluate stage
            eval_results = trainer.evaluate()
            best_scores.append(eval_results.get("eval_loss", 0))
            
            print(f"📊 Stage {stage_name} eval_loss: {eval_results.get('eval_loss', 0):.4f}")
            
            # Save stage checkpoint
            trainer.save_model(f"{output_dir}/stage_{stage_idx + 1}_{stage_name}_final")
            
            # Memory cleanup
            UltimateMemoryOptimizer.optimize_gpu_memory()
        
        print(f"\n🏆 Curriculum training completed!")
        print(f"📈 Best scores per stage: {best_scores}")
        
        return self.model, best_scores
    
    def final_evaluation(self, test_data: List[Dict]) -> Dict[str, float]:
        """Comprehensive final evaluation."""
        print("\n🎯 Running final evaluation...")
        
        # Process test data
        test_samples = [self.data_processor.process_dialog_for_training(d) for d in test_data[:100]]
        
        # Generate predictions
        predictions = []
        references = []
        
        for sample in test_samples:
            # Extract input and reference
            text = sample["text"]
            input_part = text.split("<start_of_turn>model\n")[0] + "<start_of_turn>model\n"
            reference = text.split("<start_of_turn>model\n")[1] if "<start_of_turn>model\n" in text else ""
            
            # Generate prediction
            inputs = self.tokenizer.encode(input_part, return_tensors="pt").to(self.model.device)
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs, 
                    max_new_tokens=128,
                    do_sample=True,
                    temperature=0.7,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            prediction = self.tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
            
            predictions.append(prediction)
            references.append(reference)
        
        # Evaluate
        eval_scores = self.evaluator.evaluate_predictions(predictions, references)
        
        print("\n📊 Final Evaluation Results:")
        for metric, score in eval_scores.items():
            print(f"   {metric}: {score:.4f}")
        
        return eval_scores

def main():
    """Main training pipeline execution."""
    print("🚀 Ultimate Turkish Telco Agent Training Pipeline")
    print("=" * 60)
    
    # Configuration
    config = UltimateTrainingConfig()
    trainer = UltimateTrainer(config)
    
    # Setup model
    trainer.setup_model_and_tokenizer()
    
    # Load training data (placeholder - replace with actual data loading)
    print("📊 Loading training data...")
    # raw_data = load_your_turkish_dialogs()  # Implement this
    
    print("✅ Ultimate training pipeline ready!")
    print("🎯 To start training, call: trainer.train_with_curriculum(raw_data)")
    
    return trainer

if __name__ == "__main__":
    trainer = main()
