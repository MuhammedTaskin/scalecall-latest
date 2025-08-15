#!/usr/bin/env python3
"""
GEMMA 3N ULTRA TRAINER
Single model, 5 personas, voice-native Turkish telco agent
"""

import os
import json
import torch
import base64
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, TaskType
import soundfile as sf
from torch.utils.data import Dataset, DataLoader

@dataclass
class TrainingConfig:
    model_name: str = "google/gemma-2-9b-it"  # Gemma 3N when available
    output_dir: str = "./gemma-telco-model"
    
    # LoRA parameters
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.1
    
    # Training parameters
    num_epochs: int = 3
    batch_size: int = 4
    gradient_accumulation_steps: int = 4
    learning_rate: float = 2e-4
    warmup_steps: int = 100
    
    # Optimization
    fp16: bool = True
    gradient_checkpointing: bool = True
    optim: str = "adamw_torch"
    
    # Data
    max_length: int = 2048
    audio_sample_rate: int = 16000

class TelcoAgentDataset(Dataset):
    """Dataset for multimodal telco conversations"""
    
    def __init__(self, data_dir: str, tokenizer, config: TrainingConfig):
        self.data_dir = Path(data_dir)
        self.tokenizer = tokenizer
        self.config = config
        
        # Agent personas
        self.personas = {
            "RouterAgent": """Sen bir Türk telekom çağrı merkezi yönlendirme asistanısın.
Görevin: Müşteriyi doğrula, sorunu anla, doğru birime yönlendir.
Araçların: verify_user, get_customer_status, route_to_agent""",
            
            "TechAgent": """Sen bir teknik destek uzmanısın.
Görevin: eSIM, network, cihaz sorunlarını çöz.
Araçların: check_esim_status, check_device_imei, reissue_activation_code, create_tech_ticket""",
            
            "BillingAgent": """Sen bir fatura ve ödeme uzmanısın.
Görevin: Fatura sorunları, ödemeler, indirimler.
Araçların: get_last_bill, get_unpaid_amount, apply_campaign_discount, create_payment_note""",
            
            "PlanAgent": """Sen bir tarife ve paket uzmanısın.
Görevin: Plan değişiklikleri, yeni paketler, özellikler.
Araçların: get_customer_plan, list_all_plans, change_customer_plan, check_plan_compatibility""",
            
            "FAQAgent": """Sen bir genel bilgi asistanısın.
Görevin: Sık sorulan sorular, genel yardım.
Araçların: search_faq, get_common_solutions, send_help_sms, create_info_ticket"""
        }
        
        # Load training pairs
        self.training_pairs = self.load_training_data()
    
    def load_training_data(self) -> List[Dict]:
        """Load and align conversations with audio"""
        
        training_pairs = []
        
        # Load selected conversations
        with open("data/selected_for_tts.json", 'r') as f:
            selection = json.load(f)
        
        for conv_info in selection['conversations']:
            # Load conversation
            with open(conv_info['path'], 'r') as f:
                conv = json.load(f)
            
            # Process each turn
            customer_turns = conv.get('customer_turns_for_tts', conv.get('customer_turns', []))
            agent_responses = conv.get('agent_responses', [])
            handoffs = conv.get('agent_handoffs', [])
            
            for i, turn in enumerate(customer_turns):
                if i >= len(agent_responses):
                    break
                
                # Check for audio file
                audio_path = f"data/tts_audio_final/{conv_info['id']}_turn_{i+1}.mp3"
                
                # Get current and next agent
                current_agent = agent_responses[i].get('agent_persona', 'RouterAgent')
                next_agent = None
                
                for handoff in handoffs:
                    if handoff.get('at_turn') == i + 2:
                        next_agent = handoff.get('to')
                        break
                
                # Extract tools
                tools = agent_responses[i].get('tools_triggered', [])
                tool_names = []
                for tool in tools:
                    if isinstance(tool, dict):
                        tool_names.append(tool.get('name', ''))
                    else:
                        tool_names.append(tool)
                
                training_pairs.append({
                    "audio_path": audio_path,
                    "transcript": turn.get('text', ''),
                    "emotion": turn.get('emotion', 'normal'),
                    "current_agent": current_agent,
                    "response": agent_responses[i].get('text', ''),
                    "tools": tool_names,
                    "next_agent": next_agent,
                    "conversation_id": conv_info['id'],
                    "turn_index": i
                })
        
        return training_pairs
    
    def __len__(self):
        return len(self.training_pairs)
    
    def __getitem__(self, idx):
        pair = self.training_pairs[idx]
        
        # Load audio if exists
        audio_embedding = None
        if os.path.exists(pair['audio_path']):
            try:
                # For now, use text as proxy (Gemma 3N would process audio directly)
                audio_embedding = f"[AUDIO: {pair['audio_path']}]"
            except:
                pass
        
        # Create prompt
        system_prompt = self.personas[pair['current_agent']]
        
        input_text = f"""{system_prompt}

MÜŞTERİ SESİ: {audio_embedding if audio_embedding else '[Ses yok]'}
MÜŞTERİ METNİ: {pair['transcript']}
MÜŞTERİ DUYGUSU: {pair['emotion']}

ASISTAN:"""
        
        # Create target output
        output_parts = [pair['response']]
        
        if pair['tools']:
            output_parts.append(f"\n[ARAÇLAR: {', '.join(pair['tools'])}]")
        
        if pair['next_agent']:
            output_parts.append(f"\n[YÖNLENDİRME: {pair['next_agent']}]")
        
        target_text = "".join(output_parts)
        
        # Full text for training
        full_text = input_text + " " + target_text
        
        # Tokenize
        encoding = self.tokenizer(
            full_text,
            truncation=True,
            padding="max_length",
            max_length=self.config.max_length,
            return_tensors="pt"
        )
        
        # Create labels (mask input, keep output)
        labels = encoding["input_ids"].clone()
        input_len = len(self.tokenizer.encode(input_text))
        labels[0, :input_len] = -100  # Mask input portion
        
        return {
            "input_ids": encoding["input_ids"].squeeze(),
            "attention_mask": encoding["attention_mask"].squeeze(),
            "labels": labels.squeeze()
        }

class GemmaTelcoTrainer:
    """Main trainer for Gemma telco agent"""
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        
        # Setup device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"🔧 Using device: {self.device}")
        
        # Load model and tokenizer
        self.setup_model()
    
    def setup_model(self):
        """Setup model with LoRA and quantization"""
        
        print("📦 Loading model...")
        
        # Quantization config for memory efficiency
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4"
        )
        
        # Load base model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True
        )
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.config.model_name,
            trust_remote_code=True
        )
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Setup LoRA
        lora_config = LoraConfig(
            r=self.config.lora_r,
            lora_alpha=self.config.lora_alpha,
            target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
            lora_dropout=self.config.lora_dropout,
            bias="none",
            task_type=TaskType.CAUSAL_LM
        )
        
        # Apply LoRA
        self.model = get_peft_model(self.model, lora_config)
        self.model.print_trainable_parameters()
        
        # Enable gradient checkpointing
        if self.config.gradient_checkpointing:
            self.model.gradient_checkpointing_enable()
    
    def train(self):
        """Main training loop"""
        
        print("🚀 Starting training...")
        
        # Load dataset
        dataset = TelcoAgentDataset(
            data_dir="data",
            tokenizer=self.tokenizer,
            config=self.config
        )
        
        # Split dataset (80/20)
        train_size = int(0.8 * len(dataset))
        val_size = len(dataset) - train_size
        train_dataset, val_dataset = torch.utils.data.random_split(
            dataset, [train_size, val_size]
        )
        
        print(f"📊 Dataset: {train_size} train, {val_size} validation")
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=self.config.output_dir,
            num_train_epochs=self.config.num_epochs,
            per_device_train_batch_size=self.config.batch_size,
            per_device_eval_batch_size=self.config.batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            warmup_steps=self.config.warmup_steps,
            learning_rate=self.config.learning_rate,
            fp16=self.config.fp16,
            logging_steps=10,
            evaluation_strategy="steps",
            eval_steps=50,
            save_strategy="epoch",
            load_best_model_at_end=True,
            push_to_hub=False,
            optim=self.config.optim,
            gradient_checkpointing=self.config.gradient_checkpointing,
        )
        
        # Create trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            tokenizer=self.tokenizer,
        )
        
        # Train!
        trainer.train()
        
        # Save model
        trainer.save_model(f"{self.config.output_dir}/final")
        self.tokenizer.save_pretrained(f"{self.config.output_dir}/final")
        
        print(f"✅ Training complete! Model saved to {self.config.output_dir}/final")
    
    def inference(self, audio_path: str, transcript: str, emotion: str = "normal", current_agent: str = "RouterAgent"):
        """Run inference on new input"""
        
        self.model.eval()
        
        # Prepare input
        personas = {
            "RouterAgent": "Sen yönlendirme uzmanısın",
            "TechAgent": "Sen teknik destek uzmanısın",
            "BillingAgent": "Sen fatura uzmanısın",
            "PlanAgent": "Sen tarife uzmanısın",
            "FAQAgent": "Sen bilgi asistanısın"
        }
        
        prompt = f"""{personas[current_agent]}

MÜŞTERİ: {transcript}
DUYGU: {emotion}

ASISTAN:"""
        
        # Tokenize
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=256,
                temperature=0.7,
                do_sample=True,
                top_p=0.9
            )
        
        # Decode
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        response = response.split("ASISTAN:")[-1].strip()
        
        # Parse tools and handoff
        tools = []
        next_agent = None
        
        if "[ARAÇLAR:" in response:
            tools_str = response.split("[ARAÇLAR:")[1].split("]")[0]
            tools = [t.strip() for t in tools_str.split(",")]
        
        if "[YÖNLENDİRME:" in response:
            next_agent = response.split("[YÖNLENDİRME:")[1].split("]")[0].strip()
        
        # Clean response text
        clean_response = response.split("[ARAÇLAR:")[0].split("[YÖNLENDİRME:")[0].strip()
        
        return {
            "response": clean_response,
            "tools": tools,
            "next_agent": next_agent
        }

def main():
    print("🚀 GEMMA TELCO TRAINER")
    print("="*60)
    
    # Check for audio files
    audio_count = len(list(Path("data/tts_audio_final").glob("*.mp3")))
    print(f"🎵 Found {audio_count} audio files")
    
    if audio_count < 100:
        print("⏳ Waiting for more audio files...")
        return
    
    # Initialize trainer
    config = TrainingConfig()
    trainer = GemmaTelcoTrainer(config)
    
    # Start training
    trainer.train()
    
    # Test inference
    print("\n🧪 Testing inference...")
    result = trainer.inference(
        audio_path="test.mp3",
        transcript="eSIM'im çalışmıyor, yardım eder misiniz?",
        emotion="frustrated",
        current_agent="RouterAgent"
    )
    
    print(f"Response: {result['response']}")
    print(f"Tools: {result['tools']}")
    print(f"Handoff: {result['next_agent']}")

if __name__ == "__main__":
    main()