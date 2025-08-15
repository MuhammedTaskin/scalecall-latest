#!/usr/bin/env python3
"""
GEMMA 3N WITH AUDIO TRAINING
We're using those 441 audio files we spent 8 hours creating!
"""

import torch
import torchaudio
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from datasets import Dataset
import json
import base64
from pathlib import Path
from typing import Dict, List
import librosa

class AudioTextDataset:
    """Multimodal dataset with AUDIO + TEXT"""
    
    def __init__(self, audio_dir: str = "data/tts_audio_final"):
        self.audio_dir = Path(audio_dir)
        self.audio_files = list(self.audio_dir.glob("*.mp3"))
        print(f"🎵 Found {len(self.audio_files)} audio files!")
        
        # Load conversation mappings
        with open("data/selected_for_tts.json", 'r') as f:
            self.selection = json.load(f)
        
        self.training_pairs = []
        self.prepare_audio_text_pairs()
    
    def prepare_audio_text_pairs(self):
        """Match audio files with their transcripts"""
        
        audio_to_text = {}
        
        # Load all conversations and match with audio
        for conv_info in self.selection['conversations']:
            with open(conv_info['path'], 'r') as f:
                conv = json.load(f)
            
            customer_turns = conv.get('customer_turns_for_tts', conv.get('customer_turns', []))
            agent_responses = conv.get('agent_responses', [])
            
            for i, turn in enumerate(customer_turns):
                if i >= len(agent_responses):
                    break
                
                # Audio file path
                audio_file = self.audio_dir / f"{conv_info['id']}_turn_{i+1}.mp3"
                
                if audio_file.exists():
                    # Load and process audio
                    audio_features = self.extract_audio_features(str(audio_file))
                    
                    self.training_pairs.append({
                        "audio_path": str(audio_file),
                        "audio_features": audio_features,
                        "transcript": turn.get('text', ''),
                        "emotion": turn.get('emotion', 'normal'),
                        "agent_response": agent_responses[i].get('text', ''),
                        "tools": agent_responses[i].get('tools_triggered', []),
                        "agent": agent_responses[i].get('agent_persona', 'RouterAgent')
                    })
        
        print(f"✅ Created {len(self.training_pairs)} audio-text pairs!")
    
    def extract_audio_features(self, audio_path: str) -> np.ndarray:
        """Extract audio features for model input"""
        
        # Load audio with librosa (works with MP3)
        y, sr = librosa.load(audio_path, sr=16000)
        
        # Extract features
        # 1. MFCC (Mel-frequency cepstral coefficients) - captures speech characteristics
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
        
        # 2. Pitch/F0 - emotional content
        f0, voiced_flag, voiced_probs = librosa.pyin(
            y, fmin=librosa.note_to_hz('C2'), 
            fmax=librosa.note_to_hz('C7')
        )
        
        # 3. Energy/RMS - emphasis and emotion
        rms = librosa.feature.rms(y=y)
        
        # 4. Spectral features - voice quality
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        
        # Combine features
        features = {
            "mfcc": mfcc.mean(axis=1),  # Average over time
            "pitch_mean": np.nanmean(f0) if f0 is not None else 0,
            "pitch_std": np.nanstd(f0) if f0 is not None else 0,
            "energy": rms.mean(),
            "spectral_centroid": spectral_centroid.mean(),
            "duration": len(y) / sr
        }
        
        # Convert to vector
        feature_vector = np.concatenate([
            features["mfcc"],  # 40 dims
            [features["pitch_mean"], features["pitch_std"]],  # 2 dims
            [features["energy"]],  # 1 dim
            [features["spectral_centroid"]],  # 1 dim
            [features["duration"]]  # 1 dim
        ])  # Total: 45 dimensions
        
        return feature_vector

class GemmaAudioTextModel(torch.nn.Module):
    """Gemma with audio projection layer"""
    
    def __init__(self, gemma_model, audio_dim: int = 45, hidden_dim: int = 4096):
        super().__init__()
        self.gemma = gemma_model
        
        # Audio projection layers (maps audio features to text embedding space)
        self.audio_projection = torch.nn.Sequential(
            torch.nn.Linear(audio_dim, 512),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.1),
            torch.nn.Linear(512, 1024),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.1),
            torch.nn.Linear(1024, hidden_dim)  # Match Gemma's hidden size
        )
        
        # Fusion layer
        self.fusion = torch.nn.Sequential(
            torch.nn.Linear(hidden_dim * 2, hidden_dim),
            torch.nn.LayerNorm(hidden_dim),
            torch.nn.ReLU()
        )
    
    def forward(self, input_ids, attention_mask, audio_features=None):
        # Get text embeddings from Gemma
        text_outputs = self.gemma.get_input_embeddings()(input_ids)
        
        if audio_features is not None:
            # Project audio to text space
            audio_embeddings = self.audio_projection(audio_features)
            audio_embeddings = audio_embeddings.unsqueeze(1)  # Add sequence dimension
            
            # Concatenate audio and text embeddings
            combined = torch.cat([audio_embeddings, text_outputs], dim=1)
            
            # Update attention mask for audio token
            batch_size = attention_mask.shape[0]
            audio_mask = torch.ones(batch_size, 1, device=attention_mask.device)
            attention_mask = torch.cat([audio_mask, attention_mask], dim=1)
        else:
            combined = text_outputs
        
        # Pass through Gemma
        outputs = self.gemma(
            inputs_embeds=combined,
            attention_mask=attention_mask
        )
        
        return outputs

def create_audio_training_prompt(pair: Dict) -> str:
    """Create training prompt with audio context"""
    
    prompt = f"""[AUDIO EMBEDDED]
Müşteri Duygusu: {pair['emotion']}
Müşteri Sözleri: {pair['transcript']}
Ses Özellikleri: Pitch={pair['audio_features'][40]:.1f}Hz, Enerji={pair['audio_features'][42]:.2f}, Süre={pair['audio_features'][44]:.1f}s

Agent ({pair['agent']}): {pair['agent_response']}"""
    
    if pair['tools']:
        tools_str = ", ".join(pair['tools']) if isinstance(pair['tools'], list) else pair['tools']
        prompt += f"\n[ARAÇLAR: {tools_str}]"
    
    return prompt

def train_with_audio():
    """Main training function using audio"""
    
    print("🎵 TRAINING GEMMA 3N WITH AUDIO")
    print("="*60)
    
    # Load dataset
    dataset = AudioTextDataset()
    
    # Prepare for HuggingFace format
    train_data = []
    for pair in dataset.training_pairs:
        train_data.append({
            "text": create_audio_training_prompt(pair),
            "audio_features": pair['audio_features'].tolist()
        })
    
    # Convert to HF Dataset
    hf_dataset = Dataset.from_list(train_data)
    
    print(f"📊 Training with {len(hf_dataset)} audio-text pairs")
    print(f"🎵 Using {len(dataset.audio_files)} audio files")
    
    # Load base Gemma model
    model_name = "google/gemma-2-2b-it"  # Start with smaller model for audio experiments
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    base_model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    
    # Wrap with audio projection
    model = GemmaAudioTextModel(base_model)
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir="./gemma-audio-telco",
        num_train_epochs=3,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=8,
        warmup_steps=100,
        learning_rate=5e-5,
        fp16=True,
        logging_steps=10,
        save_strategy="epoch",
        evaluation_strategy="no",
        push_to_hub=False,
    )
    
    # Custom data collator for audio
    def audio_data_collator(batch):
        # Extract text and audio
        texts = [item['text'] for item in batch]
        audio_features = torch.tensor([item['audio_features'] for item in batch])
        
        # Tokenize text
        encodings = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
        
        # Add audio features
        encodings['audio_features'] = audio_features
        
        return encodings
    
    # Create trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=hf_dataset,
        tokenizer=tokenizer,
        data_collator=audio_data_collator
    )
    
    # Train!
    print("🚀 Starting audio-aware training...")
    trainer.train()
    
    # Save
    trainer.save_model("./gemma-audio-telco/final")
    print("✅ Model trained with AUDIO features!")

# Alternative: Audio embeddings as prompt prefix
def create_audio_aware_prompts():
    """Simpler approach: Encode audio features in text prompt"""
    
    print("🎯 AUDIO-AWARE PROMPT ENGINEERING")
    print("="*60)
    
    dataset = AudioTextDataset()
    enhanced_prompts = []
    
    for pair in dataset.training_pairs:
        # Encode audio characteristics in prompt
        audio_desc = []
        
        # Pitch indicates emotion
        pitch = pair['audio_features'][40]
        if pitch > 200:
            audio_desc.append("yüksek sesle")
        elif pitch < 150:
            audio_desc.append("alçak sesle")
        
        # Energy indicates urgency
        energy = pair['audio_features'][42]
        if energy > 0.1:
            audio_desc.append("enerjik")
        elif energy < 0.05:
            audio_desc.append("sakin")
        
        # Duration indicates complexity
        duration = pair['audio_features'][44]
        if duration > 5:
            audio_desc.append("uzun konuşma")
        elif duration < 2:
            audio_desc.append("kısa")
        
        # Create enhanced prompt
        prompt = f"""[SES: {', '.join(audio_desc)}]
[DUYGU: {pair['emotion']}]
Müşteri: {pair['transcript']}

{pair['agent']}: {pair['agent_response']}"""
        
        if pair['tools']:
            prompt += f"\n[ARAÇLAR: {', '.join(pair['tools'])}]"
        
        enhanced_prompts.append(prompt)
    
    print(f"✅ Created {len(enhanced_prompts)} audio-aware prompts")
    
    # Save for training
    with open("audio_aware_prompts.jsonl", 'w') as f:
        for prompt in enhanced_prompts:
            f.write(json.dumps({"text": prompt}) + "\n")
    
    print("💾 Saved to audio_aware_prompts.jsonl")
    
    return enhanced_prompts

if __name__ == "__main__":
    print("🎵 USING ALL 441 AUDIO FILES WE CREATED!")
    print("="*60)
    
    # Check audio files
    audio_count = len(list(Path("data/tts_audio_final").glob("*.mp3")))
    print(f"✅ Found {audio_count} audio files")
    print(f"💰 We paid for these - we're using them!")
    
    # Option 1: Full audio training (needs GPU)
    # train_with_audio()
    
    # Option 2: Audio-aware prompts (works anywhere)
    create_audio_aware_prompts()
    
    print("\n🔥 AUDIO DATA IS BEING USED!")
    print("Not wasting 8 hours of work!")