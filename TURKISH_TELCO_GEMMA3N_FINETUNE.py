"""
🚀 TURKISH TELCO GEMMA 3N 4B FINE-TUNING
⚡ ALWAYS AND ALWAYS AND ALWAYS USE GEMINI 2.5 FLASH FOR DATA!
🔥 ULTIMATE TURKISH TELCO AGENT TRAINING!
"""

import os
import json
import torch
import time
from datetime import datetime
from typing import Dict, List, Any

# Unsloth imports
from unsloth import FastModel
from unsloth.chat_templates import get_chat_template, standardize_data_formats, train_on_responses_only
from datasets import Dataset
from transformers import TextStreamer
from trl import SFTTrainer, SFTConfig
import gc

class TurkishTelcoFineTuner:
    """Ultimate Turkish Telco Gemma 3N fine-tuner."""
    
    def __init__(self):
        # ⚡ ALWAYS AND ALWAYS AND ALWAYS USE GEMINI 2.5 FLASH!
        print("🚀 Turkish Telco Gemma 3N 4B Fine-Tuner")
        print("⚡ BEST TRAINING SETUP FOR TURKISH CALL CENTER!")
        print("=" * 60)
        
        self.model = None
        self.tokenizer = None
        self.trainer = None
        
    def setup_model(self):
        """Setup Gemma 3N 4B model with optimal settings."""
        
        print("🧠 Loading Gemma 3N 4B model...")
        
        # Load model with 4-bit quantization
        self.model, self.tokenizer = FastModel.from_pretrained(
            model_name="unsloth/gemma-3n-E4B-it",  # 4B instruction-tuned
            dtype=None,  # Auto detection
            max_seq_length=1024,  # Perfect for Turkish dialogs
            load_in_4bit=True,  # Memory efficient
            full_finetuning=False,  # LoRA fine-tuning
        )
        
        # Apply Gemma-3 chat template
        self.tokenizer = get_chat_template(
            self.tokenizer,
            chat_template="gemma-3",
        )
        
        # Add LoRA adapters - OPTIMIZED FOR TURKISH!
        self.model = FastModel.get_peft_model(
            self.model,
            finetune_vision_layers=False,  # Text only
            finetune_language_layers=True,  # Essential for Turkish
            finetune_attention_modules=True,  # Good for conversation
            finetune_mlp_modules=True,  # Always keep on
            
            # Optimized LoRA settings for Turkish
            r=16,  # Higher for Turkish complexity
            lora_alpha=32,  # Strong adaptation
            lora_dropout=0.1,  # Prevent overfitting
            bias="none",
            random_state=3407,
        )
        
        print("✅ Gemma 3N 4B loaded and configured!")
        
        # Show memory stats
        if torch.cuda.is_available():
            gpu_stats = torch.cuda.get_device_properties(0)
            memory_used = round(torch.cuda.max_memory_reserved() / 1024 / 1024 / 1024, 3)
            max_memory = round(gpu_stats.total_memory / 1024 / 1024 / 1024, 3)
            print(f"🔧 GPU: {gpu_stats.name}")
            print(f"💾 Memory: {memory_used}GB / {max_memory}GB used")
    
    def load_turkish_dataset(self):
        """Load our Turkish telco dataset."""
        
        print("📊 Loading Turkish telco dataset...")
        
        # Try to load the best available dataset
        dataset_files = [
            "data/gemini_generated/speed_demon_complete_168_20250814_025211.json",
            "data/gemini_generated/MEGA_COMPREHENSIVE_*.json",
            "data/cleaned/turkish_telco_*_cleaned.json"
        ]
        
        dialogs = []
        loaded_file = None
        
        for pattern in dataset_files:
            if "*" in pattern:
                import glob
                files = glob.glob(pattern)
                if files:
                    # Take the largest file
                    loaded_file = max(files, key=os.path.getsize)
                    break
            elif os.path.exists(pattern):
                loaded_file = pattern
                break
        
        if loaded_file:
            print(f"📂 Loading dataset: {loaded_file}")
            with open(loaded_file, 'r', encoding='utf-8') as f:
                dialogs = json.load(f)
            print(f"✅ Loaded {len(dialogs)} dialogs")
        else:
            print("❌ No dataset found! Generate dataset first!")
            return None
        
        # Convert to HuggingFace dataset format
        print("🔄 Converting to training format...")
        
        # Apply chat template formatting
        def format_dialog(dialog):
            conversations = dialog["conversations"]
            
            # Convert to chat format
            formatted_convos = []
            for turn in conversations:
                role = turn["role"]
                content = turn["content"][0]["text"] if turn["content"] else ""
                
                if role == "assistant":
                    formatted_convos.append({"role": "model", "content": content})
                else:
                    formatted_convos.append({"role": "user", "content": content})
            
            return {"conversations": formatted_convos}
        
        # Format all dialogs
        formatted_dialogs = [format_dialog(d) for d in dialogs]
        
        # Create HuggingFace dataset
        dataset = Dataset.from_list(formatted_dialogs)
        
        # Standardize format
        dataset = standardize_data_formats(dataset)
        
        print(f"✅ Dataset prepared: {len(dataset)} samples")
        return dataset
    
    def format_dataset_for_training(self, dataset):
        """Format dataset for Gemma-3 training."""
        
        print("🔧 Applying Gemma-3 chat template...")
        
        def formatting_prompts_func(examples):
            convos = examples["conversations"]
            texts = [
                self.tokenizer.apply_chat_template(
                    convo, 
                    tokenize=False, 
                    add_generation_prompt=False
                ).removeprefix('<bos>') 
                for convo in convos
            ]
            return {"text": texts}
        
        dataset = dataset.map(formatting_prompts_func, batched=True)
        
        print("✅ Chat template applied")
        return dataset
    
    def setup_trainer(self, dataset):
        """Setup the SFT trainer with optimal settings."""
        
        print("⚙️ Setting up trainer...")
        
        # Split dataset
        split_dataset = dataset.train_test_split(test_size=0.1, seed=42)
        train_dataset = split_dataset["train"]
        eval_dataset = split_dataset["test"]
        
        print(f"📊 Training samples: {len(train_dataset)}")
        print(f"📊 Evaluation samples: {len(eval_dataset)}")
        
        # Create trainer with Turkish-optimized settings
        self.trainer = SFTTrainer(
            model=self.model,
            tokenizer=self.tokenizer,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            args=SFTConfig(
                dataset_text_field="text",
                
                # Batch settings
                per_device_train_batch_size=1,
                per_device_eval_batch_size=1,
                gradient_accumulation_steps=8,  # Effective batch = 8
                
                # Training schedule
                num_train_epochs=3,  # 3 epochs for good learning
                max_steps=-1,  # Use epochs instead
                
                # Learning settings
                learning_rate=2e-4,  # Higher for Turkish complexity
                warmup_steps=10,
                weight_decay=0.01,
                
                # Optimization
                optim="adamw_8bit",
                lr_scheduler_type="cosine",
                
                # Logging & evaluation
                logging_steps=10,
                eval_strategy="steps",
                eval_steps=50,
                save_strategy="steps",
                save_steps=100,
                
                # Output
                output_dir="./turkish_telco_gemma3n",
                report_to="none",
                
                # Stability
                seed=3407,
                fp16=True,
                gradient_checkpointing=True,
            ),
        )
        
        # Apply response-only training (train only on assistant outputs)
        self.trainer = train_on_responses_only(
            self.trainer,
            instruction_part="<start_of_turn>user\n",
            response_part="<start_of_turn>model\n",
        )
        
        print("✅ Trainer configured for Turkish telco fine-tuning!")
    
    def train_model(self):
        """Train the model on Turkish telco data."""
        
        print("\n🚀 STARTING TURKISH TELCO FINE-TUNING!")
        print("=" * 60)
        
        # Memory stats before training
        if torch.cuda.is_available():
            start_memory = round(torch.cuda.max_memory_reserved() / 1024 / 1024 / 1024, 3)
            print(f"🔧 Starting memory: {start_memory}GB")
        
        # Start training
        start_time = time.time()
        trainer_stats = self.trainer.train()
        training_time = time.time() - start_time
        
        # Memory stats after training
        if torch.cuda.is_available():
            end_memory = round(torch.cuda.max_memory_reserved() / 1024 / 1024 / 1024, 3)
            training_memory = round(end_memory - start_memory, 3)
            print(f"🔧 Peak memory: {end_memory}GB")
            print(f"🔧 Training memory: {training_memory}GB")
        
        print("\n🏆 TRAINING COMPLETED!")
        print(f"⏱️ Training time: {training_time/60:.2f} minutes")
        print(f"📊 Final loss: {trainer_stats.log_history[-1].get('train_loss', 'N/A')}")
        
        return trainer_stats
    
    def save_model(self):
        """Save the fine-tuned model."""
        
        print("\n💾 Saving Turkish telco model...")
        
        # Save LoRA adapters
        model_path = "./turkish_telco_gemma3n_final"
        self.model.save_pretrained(model_path)
        self.tokenizer.save_pretrained(model_path)
        
        print(f"✅ Model saved to: {model_path}")
        
        # Save merged model for deployment
        try:
            merged_path = "./turkish_telco_gemma3n_merged"
            self.model.save_pretrained_merged(merged_path, self.tokenizer)
            print(f"✅ Merged model saved to: {merged_path}")
        except Exception as e:
            print(f"⚠️ Merged save failed: {e}")
    
    def test_model(self):
        """Test the fine-tuned model with Turkish telco scenarios."""
        
        print("\n🧪 Testing Turkish telco model...")
        
        # Test scenarios
        test_scenarios = [
            "Merhaba, eSIM kurulumu yapmak istiyorum",
            "Paketimi 5GB'den 10GB'a yükseltebilir misiniz?",
            "Faturamda hata var galiba, kontrol edebilir misiniz?",
            "Şile'de sinyal çekmiyor, ne yapabilirim?"
        ]
        
        print("🎭 Test conversations:")
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n💬 Test {i}:")
            print(f"👤 User: {scenario}")
            
            # Format message
            messages = [{
                "role": "user",
                "content": scenario
            }]
            
            # Generate response
            inputs = self.tokenizer.apply_chat_template(
                messages,
                add_generation_prompt=True,
                return_tensors="pt",
                tokenize=True,
                return_dict=True,
            ).to("cuda")
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=128,
                    temperature=0.7,
                    top_p=0.9,
                    top_k=50,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                )
            
            response = self.tokenizer.decode(
                outputs[0][inputs["input_ids"].shape[1]:], 
                skip_special_tokens=True
            )
            
            print(f"🤖 Agent: {response.strip()}")
    
    def run_complete_training(self):
        """Run the complete Turkish telco fine-tuning pipeline."""
        
        try:
            # Setup
            self.setup_model()
            
            # Load dataset
            dataset = self.load_turkish_dataset()
            if dataset is None:
                return False
            
            # Format dataset
            dataset = self.format_dataset_for_training(dataset)
            
            # Setup trainer
            self.setup_trainer(dataset)
            
            # Train
            trainer_stats = self.train_model()
            
            # Save
            self.save_model()
            
            # Test
            self.test_model()
            
            print("\n🏆 TURKISH TELCO GEMMA 3N FINE-TUNING COMPLETE!")
            print("🎯 Model ready for Turkish call center deployment!")
            
            return True
            
        except Exception as e:
            print(f"❌ Training failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            # Cleanup
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()

def main():
    """Main training function."""
    print("🚀 TURKISH TELCO GEMMA 3N 4B FINE-TUNING PIPELINE")
    print("⚡ ALWAYS AND ALWAYS AND ALWAYS USE GEMINI 2.5 FLASH FOR DATA!")
    print("🔥 ULTIMATE TURKISH CALL CENTER AGENT TRAINING!")
    print("=" * 80)
    
    # Check CUDA
    if not torch.cuda.is_available():
        print("❌ CUDA not available! Need GPU for training.")
        return
    
    print(f"✅ CUDA available: {torch.cuda.get_device_name(0)}")
    
    # Initialize trainer
    trainer = TurkishTelcoFineTuner()
    
    # Run training
    success = trainer.run_complete_training()
    
    if success:
        print("\n🎉 SUCCESS! Turkish telco agent is ready!")
    else:
        print("\n❌ Training failed. Check logs above.")

if __name__ == "__main__":
    main()
