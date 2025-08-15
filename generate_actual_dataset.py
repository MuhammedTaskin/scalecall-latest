"""
Generate Actual Turkish Telco Dataset
Creates the real 50K+ dialog files for training
"""
import json
import os
from dataset_step9_master_generator import MasterDatasetGenerator

def generate_and_save_dataset():
    """Generate the actual dataset and save to files."""
    print("🚀 Generating actual Turkish telco dataset...")
    
    # Initialize generator
    generator = MasterDatasetGenerator()
    
    # Generate different dataset sizes for different purposes
    datasets = {
        "mini": {
            "size": 1000,
            "description": "Mini dataset for quick testing"
        },
        "medium": {
            "size": 10000, 
            "description": "Medium dataset for development"
        },
        "full": {
            "size": 50000,
            "description": "Full dataset for competition training"
        }
    }
    
    # Create data directory if it doesn't exist
    os.makedirs("data/generated", exist_ok=True)
    
    for dataset_name, config in datasets.items():
        print(f"\n📊 Generating {dataset_name} dataset ({config['size']:,} dialogs)...")
        
        # Generate dataset
        raw_dataset = generator.generate_massive_dataset(
            size=config["size"],
            noise_ratio=0.35,
            enable_anti_memorization=True
        )
        
        # Save raw dataset
        with open(f"data/generated/{dataset_name}_raw_dataset.json", "w", encoding="utf-8") as f:
            json.dump(raw_dataset, f, ensure_ascii=False, indent=2)
        
        # Create train/test splits and save separately
        from datasets import Dataset
        dataset = Dataset.from_list(raw_dataset)
        split_dataset = dataset.train_test_split(test_size=0.1, seed=42)
        
        # Save train set
        train_data = [item for item in split_dataset["train"]]
        with open(f"data/generated/{dataset_name}_train.json", "w", encoding="utf-8") as f:
            json.dump(train_data, f, ensure_ascii=False, indent=2)
        
        # Save test set  
        test_data = [item for item in split_dataset["test"]]
        with open(f"data/generated/{dataset_name}_test.json", "w", encoding="utf-8") as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        # Save JSONL format for easy loading
        with open(f"data/generated/{dataset_name}_train.jsonl", "w", encoding="utf-8") as f:
            for item in train_data:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        
        with open(f"data/generated/{dataset_name}_test.jsonl", "w", encoding="utf-8") as f:
            for item in test_data:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        
        print(f"✅ {dataset_name} dataset saved:")
        print(f"   - Raw: data/generated/{dataset_name}_raw_dataset.json")
        print(f"   - Train: data/generated/{dataset_name}_train.json/.jsonl")
        print(f"   - Test: data/generated/{dataset_name}_test.json/.jsonl")
    
    # Generate sample conversations for review
    print("\n📝 Generating sample conversations for review...")
    sample_conversations = []
    
    for dialog in raw_dataset[:10]:  # First 10 dialogs
        sample_conversations.append({
            "scenario_type": dialog.get("scenario_type", "unknown"),
            "context": dialog.get("context", "unknown"),
            "has_noise": dialog.get("has_noise", False),
            "conversation_preview": dialog["conversations"][:4]  # First 4 turns
        })
    
    with open("data/generated/sample_conversations.json", "w", encoding="utf-8") as f:
        json.dump(sample_conversations, f, ensure_ascii=False, indent=2)
    
    print("✅ Sample conversations saved: data/generated/sample_conversations.json")
    print(f"\n🎯 Dataset generation complete! Total files created: {len(os.listdir('data/generated'))}")

if __name__ == "__main__":
    generate_and_save_dataset()
