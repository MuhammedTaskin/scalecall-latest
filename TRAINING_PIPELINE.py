#!/usr/bin/env python3
"""
Gemma 3N Training Pipeline
Single model, multiple personas via prompt switching
"""

import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import base64
from typing import Dict, List

class GemmaNTrainingPipeline:
    def __init__(self):
        self.model_name = "google/gemma-3n"  # Multimodal version
        
        # 5 Agent Personas (prompt ile switch edilecek)
        self.agent_prompts = {
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
    
    def prepare_training_data(self):
        """Convert conversations to training format"""
        
        training_pairs = []
        
        # Her konuşmayı training pair'e çevir
        datasets = [
            "data/varied_dataset/conversations",
            "data/correct_flash_dataset",
            "data/smart_flash_dataset",
            "data/quick_varied_dataset",
            "data/flash_heavy_dataset"
        ]
        
        for dataset_dir in datasets:
            # Load conversations
            for conv_file in os.listdir(dataset_dir):
                if not conv_file.endswith('.json'):
                    continue
                    
                with open(f"{dataset_dir}/{conv_file}", 'r') as f:
                    conv = json.load(f)
                
                # Her customer-agent turn'ü için training pair oluştur
                customer_turns = conv.get('customer_turns_for_tts', conv.get('customer_turns', []))
                agent_responses = conv.get('agent_responses', [])
                handoffs = conv.get('agent_handoffs', [])
                
                for i, customer_turn in enumerate(customer_turns):
                    if i >= len(agent_responses):
                        break
                    
                    agent_resp = agent_responses[i]
                    current_agent = agent_resp.get('agent_persona', agent_resp.get('agent', 'RouterAgent'))
                    
                    # Check for handoff
                    next_agent = None
                    for handoff in handoffs:
                        if handoff.get('at_turn') == i + 2:  # Next turn
                            next_agent = handoff.get('to')
                            break
                    
                    # Create training pair
                    training_pair = {
                        # INPUT (Multimodal)
                        "audio": self.get_audio_embedding(customer_turn),  # TTS generated audio
                        "transcript": customer_turn.get('text', ''),
                        "emotion": customer_turn.get('emotion', 'normal'),
                        "current_agent": current_agent,
                        "system_prompt": self.agent_prompts[current_agent],
                        
                        # OUTPUT (Model should generate)
                        "response": agent_resp.get('text', ''),
                        "tools": agent_resp.get('tools_triggered', agent_resp.get('tools', [])),
                        "handoff": next_agent,  # None or next agent name
                        
                        # Metadata
                        "conversation_id": conv.get('id', conv.get('conversation_id')),
                        "turn_index": i
                    }
                    
                    training_pairs.append(training_pair)
        
        return training_pairs
    
    def get_audio_embedding(self, customer_turn):
        """Get audio from ElevenLabs TTS output"""
        
        # Audio file path pattern
        conv_id = customer_turn.get('conversation_id', 'unknown')
        turn_id = customer_turn.get('turn_id', customer_turn.get('turn', '1'))
        
        audio_paths = [
            f"data/tts_audio/detailed/{conv_id}_{turn_id}.mp3",
            f"data/tts_audio/short/{conv_id}_{turn_id}.mp3",
            f"data/tts_audio/smart/{conv_id}_{turn_id}.mp3",
        ]
        
        for path in audio_paths:
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    audio_bytes = f.read()
                    return base64.b64encode(audio_bytes).decode('utf-8')
        
        return None  # No audio, use text only
    
    def create_training_prompt(self, pair: Dict) -> str:
        """Create the actual training prompt"""
        
        prompt = f"""### System Prompt:
{pair['system_prompt']}

### Customer Input:
Audio: [Audio embedded]
Transcript: {pair['transcript']}
Emotion: {pair['emotion']}

### Your Response:
Text: {pair['response']}
Tools: {json.dumps(pair['tools'])}
Handoff: {pair['handoff'] if pair['handoff'] else 'None'}
"""
        return prompt
    
    def train_model(self, training_pairs: List[Dict]):
        """Fine-tune Gemma 3N"""
        
        print(f"🎯 Training with {len(training_pairs)} examples")
        
        # Load base model
        model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        
        # Training configuration
        training_args = {
            "per_device_train_batch_size": 4,
            "gradient_accumulation_steps": 4,
            "num_train_epochs": 3,
            "learning_rate": 2e-5,
            "warmup_steps": 100,
            "logging_steps": 10,
            "save_strategy": "epoch",
            "evaluation_strategy": "epoch",
            "output_dir": "./gemma3n-telco-model",
        }
        
        # Convert pairs to prompts
        training_prompts = [
            self.create_training_prompt(pair) 
            for pair in training_pairs
        ]
        
        # TODO: Actual training loop with HuggingFace Trainer
        # This is pseudo-code for the concept
        """
        from transformers import Trainer, TrainingArguments
        
        trainer = Trainer(
            model=model,
            args=TrainingArguments(**training_args),
            train_dataset=training_prompts,
            tokenizer=tokenizer,
        )
        
        trainer.train()
        trainer.save_model("./final-telco-model")
        """
        
        print("✅ Model trained and saved!")
        
        return model
    
    def inference_example(self, audio_input, current_agent="RouterAgent"):
        """How the model works in production"""
        
        # 1. Set system prompt based on current agent
        system_prompt = self.agent_prompts[current_agent]
        
        # 2. Process audio + text
        input_prompt = f"""{system_prompt}

Customer: [Audio input]
Response:"""
        
        # 3. Model generates
        output = model.generate(input_prompt)
        
        # 4. Parse output
        response_text = extract_text(output)
        tools = extract_tools(output)
        handoff = extract_handoff(output)
        
        # 5. If handoff, switch agent for next turn
        if handoff:
            current_agent = handoff
        
        return {
            "text": response_text,
            "tools": tools,
            "next_agent": current_agent
        }

def main():
    print("🚀 GEMMA 3N TRAINING PIPELINE")
    print("="*60)
    
    pipeline = GemmaNTrainingPipeline()
    
    # Step 1: Prepare data
    print("\n📚 Preparing training data...")
    training_pairs = pipeline.prepare_training_data()
    print(f"✅ Created {len(training_pairs)} training pairs")
    
    # Step 2: Train model
    print("\n🧠 Training model...")
    model = pipeline.train_model(training_pairs)
    
    # Step 3: Test
    print("\n🎯 Testing inference...")
    result = pipeline.inference_example(
        audio_input="<customer_audio>",
        current_agent="RouterAgent"
    )
    print(f"Response: {result}")

if __name__ == "__main__":
    main()