"""
Flexible Training Configuration
Advanced training setup to encourage reasoning over memorization
"""
import torch
from transformers import TrainingArguments
from typing import Dict, Any

class FlexibleTrainingConfig:
    """Configuration for flexible reasoning-focused training."""
    
    def __init__(self):
        self.base_config = {
            # Model settings
            "model_name": "unsloth/gemma-3n-E4B-it",
            "max_seq_length": 1024,
            "load_in_4bit": True,
            
            # LoRA settings for flexibility
            "lora_r": 16,  # Higher rank for better adaptation
            "lora_alpha": 32,  # Increased alpha for stronger adaptation
            "lora_dropout": 0.1,  # Small dropout to prevent overfitting
            
            # Training hyperparameters for generalization
            "learning_rate": 1e-4,  # Lower LR for stable learning
            "warmup_ratio": 0.1,  # Gradual warmup
            "weight_decay": 0.05,  # Regularization
            "max_grad_norm": 0.3,  # Gradient clipping
            
            # Batch settings
            "per_device_train_batch_size": 1,
            "gradient_accumulation_steps": 8,  # Larger effective batch
            "dataloader_num_workers": 4,
            
            # Evaluation and saving
            "eval_strategy": "steps",
            "eval_steps": 100,
            "save_strategy": "steps", 
            "save_steps": 200,
            "logging_steps": 50,
            
            # Early stopping for generalization
            "load_best_model_at_end": True,
            "metric_for_best_model": "eval_loss",
            "greater_is_better": False,
            "early_stopping_patience": 5,
            
            # Regularization techniques
            "label_smoothing_factor": 0.1,  # Prevents overconfidence
            "max_steps": 1000,  # Prevent overtraining
            
            # Advanced settings
            "fp16": True,
            "dataloader_pin_memory": True,
            "remove_unused_columns": False,
            "report_to": "none"
        }
        
        # Curriculum learning stages
        self.curriculum_stages = [
            {
                "name": "foundation",
                "steps": 200,
                "lr": 2e-4,
                "data_types": ["simple_dialogs", "single_tool"],
                "focus": "Basic tool usage and Turkish patterns"
            },
            {
                "name": "reasoning",
                "steps": 400, 
                "lr": 1e-4,
                "data_types": ["multi_step", "context_switching"],
                "focus": "Complex reasoning and decision chains"
            },
            {
                "name": "robustness",
                "steps": 300,
                "lr": 5e-5,
                "data_types": ["noise_focused", "confusion_focused"],
                "focus": "Noise handling and edge cases"
            },
            {
                "name": "integration",
                "steps": 200,
                "lr": 2e-5,
                "data_types": ["mixed_all"],
                "focus": "Full integration and fine-tuning"
            }
        ]
    
    def get_sft_config(self, stage: str = "full") -> Dict[str, Any]:
        """Get SFT configuration for specific training stage."""
        config = self.base_config.copy()
        
        if stage in [s["name"] for s in self.curriculum_stages]:
            stage_config = next(s for s in self.curriculum_stages if s["name"] == stage)
            config.update({
                "max_steps": stage_config["steps"],
                "learning_rate": stage_config["lr"]
            })
        
        return config
    
    def get_anti_memorization_config(self) -> Dict[str, Any]:
        """Get configuration specifically tuned to prevent memorization."""
        return {
            # Stronger regularization
            "learning_rate": 8e-5,  # Lower learning rate
            "weight_decay": 0.1,    # Higher weight decay
            "lora_dropout": 0.15,   # More dropout
            "label_smoothing_factor": 0.15,  # More smoothing
            
            # Data augmentation during training
            "data_augmentation": True,
            "variation_sampling": True,
            "adversarial_examples": True,
            
            # Evaluation focused on generalization
            "eval_accumulation_steps": 10,
            "eval_delay": 100,
            "eval_steps": 50,
            
            # Early stopping on generalization metrics
            "metric_for_best_model": "eval_reasoning_score",
            "early_stopping_patience": 3,
            
            # Gradient noise for robustness
            "gradient_noise_scale": 0.01,
            "max_grad_norm": 0.1
        }
    
    def create_training_arguments(self, output_dir: str, stage: str = "full") -> TrainingArguments:
        """Create TrainingArguments object with flexible configuration."""
        config = self.get_sft_config(stage)
        
        return TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=1,  # Use steps instead
            max_steps=config["max_steps"],
            per_device_train_batch_size=config["per_device_train_batch_size"],
            gradient_accumulation_steps=config["gradient_accumulation_steps"],
            per_device_eval_batch_size=2,
            
            learning_rate=config["learning_rate"],
            weight_decay=config["weight_decay"],
            warmup_ratio=config["warmup_ratio"],
            max_grad_norm=config["max_grad_norm"],
            
            logging_steps=config["logging_steps"],
            eval_strategy=config["eval_strategy"],
            eval_steps=config["eval_steps"],
            save_strategy=config["save_strategy"],
            save_steps=config["save_steps"],
            
            load_best_model_at_end=config["load_best_model_at_end"],
            metric_for_best_model=config["metric_for_best_model"],
            greater_is_better=config["greater_is_better"],
            
            fp16=config["fp16"],
            dataloader_num_workers=config["dataloader_num_workers"],
            dataloader_pin_memory=config["dataloader_pin_memory"],
            remove_unused_columns=config["remove_unused_columns"],
            
            label_smoothing_factor=config["label_smoothing_factor"],
            report_to=config["report_to"],
            
            # Additional settings for robustness
            prediction_loss_only=False,
            include_inputs_for_metrics=True,
            seed=42,
            data_seed=42
        )

# Custom data collator for flexible training
class FlexibleDataCollator:
    """Data collator that applies on-the-fly variations."""
    
    def __init__(self, tokenizer, enable_variations: bool = True):
        self.tokenizer = tokenizer
        self.enable_variations = enable_variations
        
        # Text variations for preventing memorization
        self.response_alternatives = {
            "kimlik doğrulama başarılı": [
                "kimlik onaylandı",
                "doğrulama tamamlandı", 
                "kimlik kontrolü başarılı",
                "sistem doğrulaması tamam"
            ],
            "araç kullanıyorum": [
                "sistem sorgusu yapıyorum",
                "kontrol ediyorum",
                "bilgi alıyorum",
                "veri kontrol ediyorum"
            ]
        }
    
    def __call__(self, features):
        """Apply flexible data collation with optional variations."""
        if self.enable_variations:
            # Apply on-the-fly text variations to prevent memorization
            features = self._apply_text_variations(features)
        
        # Standard tokenizer collation
        batch = self.tokenizer.pad(
            features,
            padding=True,
            return_tensors="pt"
        )
        
        return batch
    
    def _apply_text_variations(self, features):
        """Apply text variations during training."""
        import random
        
        varied_features = []
        for feature in features:
            # Small chance to apply variation
            if random.random() < 0.2:  # 20% chance
                text = feature.get("text", "")
                for original, alternatives in self.response_alternatives.items():
                    if original in text:
                        alternative = random.choice(alternatives)
                        text = text.replace(original, alternative)
                        feature["text"] = text
                        break
            
            varied_features.append(feature)
        
        return varied_features

# Reasoning evaluation metrics
class ReasoningEvaluator:
    """Evaluator focused on reasoning rather than memorization."""
    
    def __init__(self):
        self.reasoning_keywords = [
            "çünkü", "bu nedenle", "bu durumda", "bu yüzden",
            "gerektiği için", "amacıyla", "için"
        ]
        
        self.tool_reasoning_patterns = [
            r"(\w+) aracını kullanmam gerekiyor",
            r"(\w+) kontrolü yapmalıyım", 
            r"(\w+) sorgusu gerekli",
            r"(\w+) için kontrol ediyorum"
        ]
    
    def evaluate_reasoning_quality(self, predictions: list, references: list) -> Dict[str, float]:
        """Evaluate reasoning quality in predictions."""
        reasoning_scores = []
        tool_logic_scores = []
        flexibility_scores = []
        
        for pred, ref in zip(predictions, references):
            # Check for reasoning explanations
            reasoning_score = self._check_reasoning_presence(pred)
            reasoning_scores.append(reasoning_score)
            
            # Check tool logic
            tool_logic_score = self._check_tool_logic(pred, ref)
            tool_logic_scores.append(tool_logic_score)
            
            # Check response flexibility
            flexibility_score = self._check_flexibility(pred, ref)
            flexibility_scores.append(flexibility_score)
        
        return {
            "reasoning_presence": sum(reasoning_scores) / len(reasoning_scores),
            "tool_logic_quality": sum(tool_logic_scores) / len(tool_logic_scores),
            "response_flexibility": sum(flexibility_scores) / len(flexibility_scores),
            "overall_reasoning": (
                sum(reasoning_scores) + sum(tool_logic_scores) + sum(flexibility_scores)
            ) / (3 * len(reasoning_scores))
        }
    
    def _check_reasoning_presence(self, text: str) -> float:
        """Check if text contains reasoning indicators."""
        reasoning_count = sum(1 for keyword in self.reasoning_keywords if keyword in text.lower())
        return min(1.0, reasoning_count / 2)  # Normalize to 0-1
    
    def _check_tool_logic(self, prediction: str, reference: str) -> float:
        """Check if tool usage follows logical patterns."""
        # Simple heuristic: check if tool calls are contextually appropriate
        import re
        
        tool_calls = re.findall(r'"tool_call".*?"name":\s*"(\w+)"', prediction)
        if not tool_calls:
            return 0.5  # Neutral if no tool calls
        
        # Check if tools are mentioned with reasoning
        logical_tools = 0
        for tool in tool_calls:
            for pattern in self.tool_reasoning_patterns:
                if re.search(pattern.replace(r"(\w+)", tool), prediction, re.IGNORECASE):
                    logical_tools += 1
                    break
        
        return logical_tools / len(tool_calls) if tool_calls else 0.5
    
    def _check_flexibility(self, prediction: str, reference: str) -> float:
        """Check if prediction shows flexibility rather than exact memorization."""
        # Simple similarity check - lower similarity can indicate flexibility
        from difflib import SequenceMatcher
        
        similarity = SequenceMatcher(None, prediction.lower(), reference.lower()).ratio()
        
        # Penalize exact matches, reward similar but varied responses
        if similarity > 0.95:
            return 0.3  # Too similar, likely memorized
        elif similarity > 0.7:
            return 1.0  # Good balance of accuracy and variation
        elif similarity > 0.4:
            return 0.8  # Some variation, good
        else:
            return 0.4  # Too different, might be incorrect

print("✅ Flexible training configuration ready - optimized for reasoning over memorization")
