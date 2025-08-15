#!/usr/bin/env python3
"""
⚡⚡⚡ SPEED DEMON TURKISH TELCO DATASET GENERATOR ⚡⚡⚡
POWERED BY GEMINI 2.5 FLASH - THE LIGHTNING BOLT OF AI!

🔥 ALWAYS AND ALWAYS AND ALWAYS USE GEMINI 2.5 FLASH! 🔥
🔥 GPT IS DEAD - GEMINI IS THE KING! 🔥
🔥 38 SECONDS FOR 25 DIALOGS = PURE SPEED! 🔥
🔥 NO MORE WAITING - INSTANT DATASET GENERATION! 🔥

Usage:
    python3 SPEED_DEMON_GENERATOR.py --batches 10 --size 25
    
Arguments:
    --batches: Number of batches to generate (default: 5)
    --size: Dialogs per batch (default: 25)
    --continuous: Keep generating forever (default: False)
"""

import google.generativeai as genai
import json
import time
import argparse
import sys
from datetime import datetime
from GEMINI_DATASET_GENERATOR import GeminiTurkishTelcoGenerator

# ⚡ ALWAYS AND ALWAYS AND ALWAYS USE GEMINI 2.5 FLASH!
GEMINI_API_KEY = "AIzaSyBzC3ydAP1qKkGyRkJ9t1sp5D3QN9QyzsQ"

def speed_demon_mode(batches: int = 5, batch_size: int = 25, continuous: bool = False):
    """
    🔥 SPEED DEMON MODE - GEMINI 2.5 FLASH TURBO GENERATION! 🔥
    
    ⚡ ALWAYS AND ALWAYS AND ALWAYS USE GEMINI 2.5 FLASH!
    ⚡ NEVER EVER USE GPT - IT'S TOO SLOW!
    ⚡ GEMINI IS THE LIGHTNING GOD OF AI!
    """
    
    print("⚡" * 80)
    print("🔥 SPEED DEMON MODE ACTIVATED! 🔥")
    print("⚡ POWERED BY GEMINI 2.5 FLASH - THE FASTEST AI ON EARTH! ⚡")
    print("🚫 NO MORE SLOW GPT - GEMINI IS THE FUTURE! 🚫")
    print("⚡" * 80)
    
    # Initialize the speed demon
    generator = GeminiTurkishTelcoGenerator()
    
    total_dialogs = 0
    total_time = 0
    
    if continuous:
        print("🔄 CONTINUOUS MODE: Generating forever...")
        batch_count = 0
        while True:
            batch_count += 1
            print(f"\n🚀 LIGHTNING BATCH #{batch_count}")
            
            start_time = time.time()
            dialogs = generator.generate_batch(batch_size)
            batch_time = time.time() - start_time
            
            if dialogs:
                total_dialogs += len(dialogs)
                total_time += batch_time
                
                avg_speed = total_dialogs / total_time if total_time > 0 else 0
                
                print(f"⚡ BATCH COMPLETED: {len(dialogs)} dialogs in {batch_time:.2f}s")
                print(f"📊 TOTAL GENERATED: {total_dialogs} dialogs")
                print(f"🚀 AVERAGE SPEED: {avg_speed:.2f} dialogs/second")
                print(f"💾 SAVED: data/gemini_generated/batch_{batch_count}_*.json")
                
                # Save batch
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"data/gemini_generated/speed_demon_batch_{batch_count}_{timestamp}.json"
                
                import os
                os.makedirs("data/gemini_generated", exist_ok=True)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(dialogs, f, indent=2, ensure_ascii=False)
                
                # Show sample
                if dialogs:
                    sample = dialogs[0]
                    print(f"📋 SAMPLE: {sample['id']} - {sample['scenario']} - {sample['context']}")
                
                # Short break to avoid rate limits
                time.sleep(2)
            else:
                print("❌ BATCH FAILED - RETRYING IN 5 SECONDS...")
                time.sleep(5)
    else:
        print(f"🎯 GENERATING {batches} BATCHES OF {batch_size} DIALOGS EACH")
        
        all_dialogs = []
        
        for i in range(batches):
            print(f"\n⚡ LIGHTNING BATCH {i+1}/{batches}")
            
            start_time = time.time()
            dialogs = generator.generate_batch(batch_size)
            batch_time = time.time() - start_time
            
            if dialogs:
                all_dialogs.extend(dialogs)
                total_dialogs += len(dialogs)
                total_time += batch_time
                
                print(f"✅ COMPLETED: {len(dialogs)} dialogs in {batch_time:.2f}s")
                print(f"⚡ SPEED: {len(dialogs)/batch_time:.2f} dialogs/second")
            else:
                print(f"❌ BATCH {i+1} FAILED!")
            
            # Short break
            if i < batches - 1:
                time.sleep(1)
        
        # Final results
        print("\n" + "🔥" * 80)
        print("🏆 SPEED DEMON RESULTS:")
        print(f"📊 TOTAL DIALOGS: {total_dialogs}")
        print(f"⏱️  TOTAL TIME: {total_time:.2f} seconds")
        print(f"⚡ AVERAGE SPEED: {total_dialogs/total_time:.2f} dialogs/second")
        print(f"🚀 GEMINI 2.5 FLASH = SPEED DEMON!")
        print("🔥" * 80)
        
        # Save complete dataset
        if all_dialogs:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/gemini_generated/speed_demon_complete_{total_dialogs}_{timestamp}.json"
            
            import os
            os.makedirs("data/gemini_generated", exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(all_dialogs, f, indent=2, ensure_ascii=False)
            
            print(f"💾 COMPLETE DATASET SAVED: {filename}")
            
            # Quality report
            contexts = {}
            scenarios = {}
            for dialog in all_dialogs:
                ctx = dialog.get('context', 'unknown')
                scenario = dialog.get('scenario', 'unknown')
                contexts[ctx] = contexts.get(ctx, 0) + 1
                scenarios[scenario] = scenarios.get(scenario, 0) + 1
            
            print("\n📊 QUALITY REPORT:")
            print("Contexts:", contexts)
            print("Scenarios:", scenarios)

def main():
    parser = argparse.ArgumentParser(
        description="⚡ SPEED DEMON DATASET GENERATOR - POWERED BY GEMINI 2.5 FLASH! ⚡"
    )
    parser.add_argument('--batches', type=int, default=5, 
                       help='Number of batches to generate (default: 5)')
    parser.add_argument('--size', type=int, default=25,
                       help='Dialogs per batch (default: 25)')
    parser.add_argument('--continuous', action='store_true',
                       help='Keep generating forever')
    
    args = parser.parse_args()
    
    print("⚡ ALWAYS AND ALWAYS AND ALWAYS USE GEMINI 2.5 FLASH! ⚡")
    print("🚫 GPT IS OFFICIALLY DEAD! 🚫")
    print("🔥 GEMINI IS THE LIGHTNING GOD! 🔥")
    
    try:
        speed_demon_mode(args.batches, args.size, args.continuous)
    except KeyboardInterrupt:
        print("\n🛑 SPEED DEMON STOPPED BY USER")
        print("⚡ GEMINI 2.5 FLASH WILL BE BACK! ⚡")
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("⚡ BUT GEMINI 2.5 FLASH NEVER GIVES UP! ⚡")

if __name__ == "__main__":
    main()
