"""
Simple Dataset Generator - No external dependencies
Creates the actual Turkish telco dataset files
"""
import json
import os
import random
from dataset_step9_master_generator import MasterDatasetGenerator

def simple_train_test_split(data, test_ratio=0.1):
    """Simple train/test split without datasets library."""
    random.shuffle(data)
    split_point = int(len(data) * (1 - test_ratio))
    return data[:split_point], data[split_point:]

def generate_and_save_dataset():
    """Generate the actual dataset and save to files."""
    print("🚀 Generating actual Turkish telco dataset...")
    
    # Initialize generator
    generator = MasterDatasetGenerator()
    
    # Create data directory
    os.makedirs("data/generated", exist_ok=True)
    
    # Generate datasets of different sizes
    sizes = [1000, 5000, 20000]  # Start smaller, then scale up
    
    for size in sizes:
        print(f"\n📊 Generating dataset with {size:,} dialogs...")
        
        # Generate dataset
        raw_dataset = generator.generate_massive_dataset(
            size=size,
            noise_ratio=0.35,
            enable_anti_memorization=True
        )
        
        print(f"✅ Generated {len(raw_dataset):,} total dialogs (including variations)")
        
        # Save complete dataset
        filename = f"data/generated/turkish_telco_{size}k_complete.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(raw_dataset, f, ensure_ascii=False, indent=2)
        print(f"💾 Saved: {filename}")
        
        # Create train/test split
        train_data, test_data = simple_train_test_split(raw_dataset, test_ratio=0.1)
        
        # Save train set
        train_filename = f"data/generated/turkish_telco_{size}k_train.json"
        with open(train_filename, "w", encoding="utf-8") as f:
            json.dump(train_data, f, ensure_ascii=False, indent=2)
        
        # Save test set
        test_filename = f"data/generated/turkish_telco_{size}k_test.json"
        with open(test_filename, "w", encoding="utf-8") as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        print(f"📊 Split saved:")
        print(f"   Train: {len(train_data):,} dialogs → {train_filename}")
        print(f"   Test:  {len(test_data):,} dialogs → {test_filename}")
        
        # Save JSONL format for easy loading
        train_jsonl = f"data/generated/turkish_telco_{size}k_train.jsonl"
        with open(train_jsonl, "w", encoding="utf-8") as f:
            for item in train_data:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        
        test_jsonl = f"data/generated/turkish_telco_{size}k_test.jsonl"
        with open(test_jsonl, "w", encoding="utf-8") as f:
            for item in test_data:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        
        print(f"📝 JSONL saved: {train_jsonl}, {test_jsonl}")
        
        # Generate samples for review
        sample_file = f"data/generated/turkish_telco_{size}k_samples.json"
        samples = []
        for i, dialog in enumerate(raw_dataset[:20]):  # First 20 dialogs
            samples.append({
                "sample_id": i + 1,
                "scenario_type": dialog.get("scenario_type", "unknown"),
                "context": dialog.get("context", "unknown"),
                "has_noise": dialog.get("has_noise", False),
                "quality_tier": dialog.get("quality_tier", "unknown"),
                "conversation_length": len(dialog["conversations"]),
                "preview": dialog["conversations"][:3]  # First 3 turns
            })
        
        with open(sample_file, "w", encoding="utf-8") as f:
            json.dump(samples, f, ensure_ascii=False, indent=2)
        print(f"🔍 Samples saved: {sample_file}")
    
    print(f"\n🎯 All datasets generated successfully!")
    print(f"📁 Files saved in: data/generated/")
    
    # List all generated files
    generated_files = os.listdir("data/generated")
    print(f"📋 Total files created: {len(generated_files)}")
    for file in sorted(generated_files):
        size = os.path.getsize(f"data/generated/{file}")
        print(f"   {file} ({size//1024//1024:.1f} MB)")

if __name__ == "__main__":
    generate_and_save_dataset()
