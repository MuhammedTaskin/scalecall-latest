#!/usr/bin/env python3
"""
ElevenLabs Cost Estimator for Turkish Telco Dataset
Calculates exact character count and estimated costs
"""

import os
import json
from typing import Dict, List

def count_dataset_characters(dataset_dir: str, dataset_name: str) -> Dict:
    """Count characters in a dataset"""
    
    if not os.path.exists(dataset_dir):
        return {"files": 0, "turns": 0, "characters": 0, "conversations": []}
    
    files = [f for f in os.listdir(dataset_dir) if f.endswith('.json')]
    
    total_chars = 0
    total_turns = 0
    conversations = []
    
    for file in files:
        with open(os.path.join(dataset_dir, file), 'r', encoding='utf-8') as f:
            conv = json.load(f)
        
        conv_chars = 0
        conv_turns = 0
        
        # Handle different formats
        customer_turns = conv.get('customer_turns_for_tts', conv.get('customer_turns', []))
        
        for turn in customer_turns:
            text = turn.get('text', '')
            conv_chars += len(text)
            conv_turns += 1
        
        total_chars += conv_chars
        total_turns += conv_turns
        
        conversations.append({
            "id": conv.get('conversation_id', conv.get('id', file)),
            "turns": conv_turns,
            "characters": conv_chars
        })
    
    return {
        "name": dataset_name,
        "files": len(files),
        "turns": total_turns,
        "characters": total_chars,
        "conversations": conversations[:5]  # Sample
    }

def main():
    print("🧮 ELEVENLABS COST ESTIMATOR")
    print("="*80)
    
    datasets = [
        ("data/varied_dataset/conversations", "Detailed"),
        ("data/correct_flash_dataset", "Short"),
        ("data/smart_flash_dataset", "Smart")
    ]
    
    all_stats = []
    total_chars = 0
    total_turns = 0
    
    for dataset_dir, name in datasets:
        stats = count_dataset_characters(dataset_dir, name)
        all_stats.append(stats)
        total_chars += stats["characters"]
        total_turns += stats["turns"]
        
        print(f"\n📊 {name} Dataset:")
        print(f"   Files: {stats['files']}")
        print(f"   Turns: {stats['turns']}")
        print(f"   Characters: {stats['characters']:,}")
        print(f"   Avg chars/turn: {stats['characters']//stats['turns'] if stats['turns'] > 0 else 0}")
        
        if stats["conversations"]:
            print(f"   Sample conversations:")
            for conv in stats["conversations"][:3]:
                print(f"     - {conv['id']}: {conv['turns']} turns, {conv['characters']} chars")
    
    print("\n" + "="*80)
    print("💰 COST BREAKDOWN")
    print("="*80)
    
    print(f"\n📈 TOTAL STATISTICS:")
    print(f"   Total conversations: {sum(s['files'] for s in all_stats)}")
    print(f"   Total customer turns: {total_turns}")
    print(f"   Total characters: {total_chars:,}")
    print(f"   Average chars/turn: {total_chars//total_turns if total_turns > 0 else 0}")
    
    # ElevenLabs pricing (as of 2025)
    print(f"\n💳 ELEVENLABS PRICING:")
    print(f"   Model: Flash v2.5 (lowest latency)")
    print(f"   Free tier: 10,000 chars/month")
    print(f"   Starter ($5/mo): 30,000 chars")
    print(f"   Creator ($22/mo): 100,000 chars")
    print(f"   Pro ($99/mo): 500,000 chars")
    
    # Calculate required plan
    print(f"\n🎯 REQUIRED PLAN:")
    if total_chars <= 10000:
        print(f"   ✅ FREE TIER sufficient!")
        print(f"   Characters used: {total_chars:,} / 10,000")
        print(f"   Remaining: {10000 - total_chars:,}")
    elif total_chars <= 30000:
        print(f"   📦 STARTER plan needed ($5)")
        print(f"   Characters used: {total_chars:,} / 30,000")
        print(f"   Remaining: {30000 - total_chars:,}")
    elif total_chars <= 100000:
        print(f"   📦 CREATOR plan needed ($22)")
        print(f"   Characters used: {total_chars:,} / 100,000")
        print(f"   Remaining: {100000 - total_chars:,}")
    else:
        print(f"   📦 PRO plan needed ($99)")
        print(f"   Characters used: {total_chars:,} / 500,000")
    
    # Time estimates
    print(f"\n⏱️ TIME ESTIMATES:")
    print(f"   API calls: {total_turns}")
    print(f"   Rate limit: ~3 requests/second")
    print(f"   Processing time: ~{total_turns // 3 // 60} minutes")
    print(f"   With retries: ~{total_turns // 2 // 60} minutes")
    
    # Optimization suggestions
    print(f"\n💡 OPTIMIZATION TIPS:")
    if total_chars > 10000:
        reduced = total_chars * 0.7
        print(f"   1. Reducing text by 30% → {int(reduced):,} chars")
        if reduced <= 10000:
            print(f"      ✅ Would fit in FREE tier!")
    
    print(f"   2. Use only critical conversations:")
    critical = sum(s['characters'] for s in all_stats if s['name'] != 'Smart')
    print(f"      Detailed + Short only: {critical:,} chars")
    if critical <= 10000:
        print(f"      ✅ Would fit in FREE tier!")
    
    print(f"   3. Sample subset for testing:")
    sample = total_chars // 10
    print(f"      10% sample: {sample:,} chars")
    if sample <= 10000:
        print(f"      ✅ Would fit in FREE tier!")
    
    # Save report
    report = {
        "generated_at": __import__('datetime').datetime.now().isoformat(),
        "datasets": all_stats,
        "totals": {
            "conversations": sum(s['files'] for s in all_stats),
            "turns": total_turns,
            "characters": total_chars,
            "estimated_cost": "$22" if total_chars > 30000 else ("$5" if total_chars > 10000 else "$0")
        }
    }
    
    with open("data/tts_cost_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Report saved to: data/tts_cost_report.json")

if __name__ == "__main__":
    main()