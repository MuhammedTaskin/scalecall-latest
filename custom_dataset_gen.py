"""
Custom Dataset Generator - Generate any size you want
"""
import json
import os
from dataset_step9_master_generator import MasterDatasetGenerator

def generate_custom_dataset(size: int, output_name: str = None):
    """Generate a custom-sized dataset."""
    if not output_name:
        output_name = f"custom_{size//1000}k"
    
    print(f"🚀 Generating {size:,} Turkish telco dialogs...")
    
    # Initialize generator
    generator = MasterDatasetGenerator()
    
    # Create output directory
    os.makedirs("data/generated", exist_ok=True)
    
    # Generate dataset
    dataset = generator.generate_massive_dataset(
        size=size,
        noise_ratio=0.35,
        enable_anti_memorization=True
    )
    
    print(f"✅ Generated {len(dataset):,} total dialogs")
    
    # Save complete dataset
    with open(f"data/generated/{output_name}_complete.json", "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    
    # Save JSONL for easy loading
    with open(f"data/generated/{output_name}.jsonl", "w", encoding="utf-8") as f:
        for item in dataset:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    
    print(f"💾 Saved: data/generated/{output_name}_complete.json")
    print(f"💾 Saved: data/generated/{output_name}.jsonl")
    print(f"📊 Total size: {len(dataset):,} dialogs")
    
    return dataset

if __name__ == "__main__":
    # Examples:
    # generate_custom_dataset(50000, "massive_50k")    # 50K dialogs
    # generate_custom_dataset(100000, "ultra_100k")   # 100K dialogs
    
    import sys
    if len(sys.argv) > 1:
        size = int(sys.argv[1])
        name = sys.argv[2] if len(sys.argv) > 2 else None
        generate_custom_dataset(size, name)
    else:
        print("Usage: python3 custom_dataset_gen.py <size> [output_name]")
        print("Example: python3 custom_dataset_gen.py 50000 massive_50k")
