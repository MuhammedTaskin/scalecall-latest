"""
🚀 ULTIMATE TRAINING CONFIGURATION
Optimized settings for competition-winning Turkish telco agent
"""

# ULTIMATE TRAINING PARAMETERS
ULTIMATE_CONFIG = {
    # Model Configuration
    "model_name": "unsloth/gemma-3n-E4B-it",
    "max_seq_length": 1024,
    "load_in_4bit": True,
    "dtype": "float16",
    
    # LoRA Configuration (Optimized for Competition)
    "lora_r": 32,  # Higher rank for better adaptation
    "lora_alpha": 64,  # Strong adaptation signal  
    "lora_dropout": 0.1,  # Balanced dropout
    "lora_bias": "none",
    "lora_target_modules": ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    
    # Training Hyperparameters (Competition-Optimized)
    "learning_rate": 1e-4,  # Stable learning
    "warmup_ratio": 0.1,  # Gradual warmup
    "weight_decay": 0.05,  # Regularization
    "max_grad_norm": 0.3,  # Gradient clipping
    "label_smoothing_factor": 0.1,  # Anti-overconfidence
    
    # Batch Configuration
    "per_device_train_batch_size": 1,
    "per_device_eval_batch_size": 2,
    "gradient_accumulation_steps": 8,  # Effective batch = 8
    "dataloader_num_workers": 4,
    
    # Training Schedule
    "max_steps": 1000,  # Competition-ready
    "eval_steps": 100,
    "save_steps": 200,
    "logging_steps": 25,
    
    # Optimization Settings
    "optim": "adamw_8bit",  # Memory efficient
    "lr_scheduler_type": "cosine",  # Smooth decay
    "fp16": True,  # Faster training
    "gradient_checkpointing": True,  # Memory optimization
    
    # Early Stopping & Quality Control
    "early_stopping_patience": 5,
    "load_best_model_at_end": True,
    "metric_for_best_model": "eval_loss",
    "greater_is_better": False,
    
    # Advanced Features
    "dataloader_pin_memory": True,
    "remove_unused_columns": False,
    "prediction_loss_only": False,
    "include_inputs_for_metrics": True,
    
    # Curriculum Learning Stages
    "curriculum_stages": [
        {
            "name": "foundation",
            "steps": 200,
            "lr": 2e-4,
            "focus": "Basic Turkish patterns and simple tool usage"
        },
        {
            "name": "reasoning", 
            "steps": 400,
            "lr": 1e-4,
            "focus": "Complex reasoning and multi-step chains"
        },
        {
            "name": "robustness",
            "steps": 300,
            "lr": 5e-5,
            "focus": "ASR noise handling and edge cases"
        },
        {
            "name": "integration",
            "steps": 200,
            "lr": 2e-5,
            "focus": "Full integration and final tuning"
        }
    ],
    
    # Quality Thresholds (Competition Standards)
    "min_turkish_quality": 0.85,
    "min_tool_validity": 0.90,
    "min_json_validity": 0.95,
    "min_politeness": 0.80,
    "min_brevity": 0.85,
    "target_competition_score": 0.90,
    
    # Data Processing
    "noise_ratio": 0.35,  # 35% of data has ASR noise
    "validation_split": 0.1,  # 10% for validation
    "test_split": 0.05,  # 5% for final testing
    
    # Memory Optimization
    "use_unsloth": True,
    "optimize_memory": True,
    "clear_cache_frequency": 100,  # Clear every 100 steps
    
    # Evaluation Settings
    "eval_strategy": "steps",
    "eval_accumulation_steps": 10,
    "eval_delay": 0,
    "greater_is_better": False,
    
    # Output Settings
    "output_dir": "./ultimate_turkish_telco_model",
    "save_total_limit": 3,  # Keep only 3 checkpoints
    "save_safetensors": True,
    
    # Reproducibility
    "seed": 42,
    "data_seed": 42,
    "transformers_seed": 42,
    
    # Logging & Monitoring
    "report_to": "none",  # Can change to "wandb" for tracking
    "logging_first_step": True,
    "logging_nan_inf_filter": True,
    
    # Turkish-Specific Settings
    "turkish_patterns": {
        "politeness_markers": ["hanım", "bey", "lütfen", "rica ederim", "memnuniyetle"],
        "tool_reasoning": ["kontrol ediyorum", "sorgusu yapıyorum", "bakıyorum", "için"],
        "brevity_targets": [".", "!", "?"],  # Should end with punctuation
        "max_sentences": 2,  # Turkish responses should be ≤2 sentences
    },
    
    # Tool Validation
    "valid_tools": [
        "verify_user", "get_user_info", "check_device_registration",
        "reissue_activation_code", "get_activation_steps", "get_activation_status", 
        "get_available_packages", "change_package", "create_support_ticket"
    ],
    
    # ASR Noise Patterns
    "turkish_noise_patterns": {
        "diacritic_loss": {"ı": "i", "ğ": "g", "ü": "u", "ş": "s", "ö": "o", "ç": "c"},
        "common_confusions": {
            "eSIM": ["esim", "e sim", "mevsim", "eşim", "e-sim"],
            "çekmiyor": ["cekmiyor", "çekmiyo", "cekmiyo"],
            "değiştirmek": ["degistirmek", "değiştirmek"],
            "paket": ["paketi", "paketim", "tarife"],
            "IMEI": ["imei", "aymay", "imey", "cihaz kodu"]
        },
        "number_noise": {
            "beş": "5", "on": "10", "yirmi": "20", "otuz": "30",
            "yüz": "100", "bin": "1000"
        }
    }
}

# PERFORMANCE TARGETS (Competition Standards)
COMPETITION_TARGETS = {
    "overall_score": 0.90,  # 90%+ for winning
    "turkish_quality": 0.85,  # Natural Turkish
    "tool_validity": 0.95,  # Correct tool usage
    "json_validity": 0.98,  # Perfect JSON format
    "reasoning_quality": 0.80,  # Dynamic reasoning
    "noise_robustness": 0.85,  # ASR noise handling
    "response_brevity": 0.90,  # ≤2 sentences
    "politeness": 0.85,  # Turkish politeness markers
}

# MEMORY OPTIMIZATION SETTINGS
MEMORY_CONFIG = {
    "max_memory_usage": 0.85,  # Use 85% of available GPU memory
    "gradient_checkpointing": True,
    "dataloader_pin_memory": True,
    "empty_cache_frequency": 50,  # Clear cache every 50 steps
    "mixed_precision": True,
    "use_8bit_optimizer": True,
}

# CURRICULUM LEARNING DATA DISTRIBUTION
CURRICULUM_DATA_DIST = {
    "foundation": {
        "quality_tiers": ["foundation", "intermediate"],
        "scenario_types": ["single_tool", "simple_dialog"],
        "noise_ratio": 0.2,  # Light noise
        "max_complexity": 2  # Max 2 tool calls
    },
    "reasoning": {
        "quality_tiers": ["intermediate", "advanced"], 
        "scenario_types": ["multi_step", "context_switching"],
        "noise_ratio": 0.3,  # Medium noise
        "max_complexity": 5  # Up to 5 tool calls
    },
    "robustness": {
        "quality_tiers": ["robustness", "precision"],
        "scenario_types": ["noise_focused", "error_handling"],
        "noise_ratio": 0.6,  # Heavy noise
        "max_complexity": 4  # Complex but focused
    },
    "integration": {
        "quality_tiers": ["all"],
        "scenario_types": ["all"],
        "noise_ratio": 0.35,  # Balanced noise
        "max_complexity": 6  # Full complexity
    }
}

print("✅ Ultimate training configuration loaded")
print(f"🎯 Target competition score: {COMPETITION_TARGETS['overall_score']:.0%}")
print(f"⚡ LoRA config: r={ULTIMATE_CONFIG['lora_r']}, alpha={ULTIMATE_CONFIG['lora_alpha']}")
print(f"🎓 Curriculum stages: {len(ULTIMATE_CONFIG['curriculum_stages'])}")
print(f"💾 Memory optimizations: {'ON' if MEMORY_CONFIG['mixed_precision'] else 'OFF'}")
