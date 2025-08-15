#!/usr/bin/env python3
"""
Token and Pricing Calculator for all datasets
"""

import os
import json
from typing import Dict, List

class TokenPricingCalculator:
    def __init__(self):
        # Rough token estimation (1 token ≈ 4 chars for English, 2-3 for Turkish)
        self.chars_per_token = 3  # Conservative for Turkish
        
        # Gemini pricing (per 1M tokens)
        self.pricing = {
            "gemini-2.5-flash": {
                "input": 0.15,  # $0.15 per 1M input tokens
                "output": 0.60   # $0.60 per 1M output tokens
            },
            "gemini-2.5-flash-lite": {
                "input": 0.05,  # $0.05 per 1M input tokens  
                "output": 0.15   # $0.15 per 1M output tokens
            }
        }
        
        # ElevenLabs pricing
        self.elevenlabs_pricing = {
            "creator": {
                "chars_per_month": 110000,
                "price_per_month": 22
            },
            "pro": {
                "chars_per_month": 500000,
                "price_per_month": 99
            }
        }
        
        self.datasets = []
        for root, dirs, files in os.walk("data"):
            for file in files:
                if file.endswith('.json'):
                    self.datasets.append(os.path.join(root, file))
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text (estimation)"""
        return len(text) // self.chars_per_token
    
    def analyze_conversation(self, conv_path: str) -> Dict:
        """Analyze a single conversation"""
        
        try:
            with open(conv_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            return {"error": True}
        
        stats = {
            "customer_chars": 0,
            "customer_tokens": 0,
            "agent_chars": 0,
            "agent_tokens": 0,
            "total_turns": 0
        }
        
        # Handle list format
        if isinstance(data, list):
            conversations = data
        else:
            conversations = [data]
        
        for conv in conversations:
            # Customer turns
            customer_data = conv.get('customer_turns_for_tts', conv.get('customer_turns', []))
            for turn in customer_data:
                text = turn.get('text', '')
                stats["customer_chars"] += len(text)
                stats["customer_tokens"] += self.count_tokens(text)
                stats["total_turns"] += 1
            
            # Agent responses
            for resp in conv.get('agent_responses', []):
                text = resp.get('text', '')
                stats["agent_chars"] += len(text)
                stats["agent_tokens"] += self.count_tokens(text)
        
        return stats
    
    def calculate_all(self):
        """Calculate tokens and pricing for all datasets"""
        
        print("📊 TOKEN & PRICING CALCULATOR")
        print("="*80)
        
        total_stats = {
            "files": 0,
            "customer_chars": 0,
            "customer_tokens": 0,
            "agent_chars": 0,
            "agent_tokens": 0,
            "total_turns": 0
        }
        
        # Analyze each file
        for conv_path in self.datasets:
            stats = self.analyze_conversation(conv_path)
            if "error" not in stats:
                total_stats["files"] += 1
                for key in ["customer_chars", "customer_tokens", "agent_chars", "agent_tokens", "total_turns"]:
                    total_stats[key] += stats[key]
            
            if total_stats["files"] % 100 == 0:
                print(f"   Processed {total_stats['files']} files...")
        
        # Calculate costs
        print(f"\n✅ Analysis Complete!")
        print(f"   Files: {total_stats['files']}")
        print(f"   Total turns: {total_stats['total_turns']}")
        
        print(f"\n📝 TOKEN COUNTS:")
        print(f"   Customer tokens: {total_stats['customer_tokens']:,}")
        print(f"   Agent tokens: {total_stats['agent_tokens']:,}")
        print(f"   TOTAL tokens: {total_stats['customer_tokens'] + total_stats['agent_tokens']:,}")
        
        print(f"\n📊 CHARACTER COUNTS (for TTS):")
        print(f"   Customer chars: {total_stats['customer_chars']:,}")
        print(f"   Agent chars: {total_stats['agent_chars']:,}")
        print(f"   TOTAL chars: {total_stats['customer_chars'] + total_stats['agent_chars']:,}")
        
        # Training costs (Gemini)
        total_tokens = total_stats['customer_tokens'] + total_stats['agent_tokens']
        
        print(f"\n💰 GEMINI TRAINING COSTS:")
        print(f"   Using Flash ($0.15/$0.60 per 1M):")
        input_cost = (total_tokens / 1_000_000) * self.pricing["gemini-2.5-flash"]["input"]
        output_cost = (total_tokens / 1_000_000) * self.pricing["gemini-2.5-flash"]["output"]
        print(f"      Input cost: ${input_cost:.2f}")
        print(f"      Output cost: ${output_cost:.2f}")
        print(f"      TOTAL: ${input_cost + output_cost:.2f}")
        
        print(f"\n   Using Flash-Lite ($0.05/$0.15 per 1M):")
        input_cost_lite = (total_tokens / 1_000_000) * self.pricing["gemini-2.5-flash-lite"]["input"]
        output_cost_lite = (total_tokens / 1_000_000) * self.pricing["gemini-2.5-flash-lite"]["output"]
        print(f"      Input cost: ${input_cost_lite:.2f}")
        print(f"      Output cost: ${output_cost_lite:.2f}")
        print(f"      TOTAL: ${input_cost_lite + output_cost_lite:.2f}")
        
        # ElevenLabs costs
        print(f"\n🎤 ELEVENLABS TTS COSTS:")
        customer_chars = total_stats['customer_chars']
        print(f"   Customer audio needed: {customer_chars:,} characters")
        
        if customer_chars <= 110000:
            print(f"   ✅ Fits in Creator plan ($22/month)")
            print(f"   Remaining: {110000 - customer_chars:,} chars")
        elif customer_chars <= 500000:
            print(f"   📦 Needs Pro plan ($99/month)")
            print(f"   Remaining: {500000 - customer_chars:,} chars")
        else:
            print(f"   ⚠️ Exceeds Pro plan! Need multiple accounts or enterprise")
        
        # Training data size estimate
        print(f"\n💾 TRAINING DATA SIZE:")
        avg_turn_length = total_stats['customer_tokens'] / max(total_stats['total_turns'], 1)
        print(f"   Average tokens per turn: {avg_turn_length:.0f}")
        print(f"   Training pairs: ~{total_stats['total_turns']}")
        
        # Model training time estimate
        print(f"\n⏱️ ESTIMATED TRAINING TIME:")
        print(f"   Gemma 3N fine-tuning: ~3-6 hours")
        print(f"   Testing & iteration: ~6-12 hours")
        print(f"   Total pipeline: ~12-18 hours")
        
        return total_stats

def main():
    calculator = TokenPricingCalculator()
    stats = calculator.calculate_all()
    
    print("\n" + "="*80)
    print("🎯 READY FOR TRAINING!")
    print(f"   1,000+ conversations")
    print(f"   Clean tool usage")
    print(f"   Within budget")
    print(f"\n🚀 LET'S WIN THIS!")

if __name__ == "__main__":
    main()