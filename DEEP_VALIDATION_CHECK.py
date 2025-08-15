#!/usr/bin/env python3
"""
DEEP VALIDATION CHECK
Ensures all datasets are ready for training
"""

import os
import json
from collections import Counter

def validate_conversation(conv_path):
    """Validate a single conversation"""
    
    with open(conv_path, 'r', encoding='utf-8') as f:
        conv = json.load(f)
    
    issues = []
    
    # Check required fields (handle both formats)
    if 'conversation_id' not in conv and 'id' not in conv:
        issues.append(f"Missing conversation_id/id")
    
    if 'customer_turns_for_tts' not in conv and 'customer_turns' not in conv:
        issues.append(f"Missing customer_turns_for_tts/customer_turns")
    
    if 'agent_responses' not in conv:
        issues.append(f"Missing agent_responses")
    
    # Check customer turns (handle both formats)
    customer_turns = conv.get('customer_turns_for_tts', conv.get('customer_turns', []))
    if len(customer_turns) < 2:
        issues.append(f"Only {len(customer_turns)} customer turns (need 2+)")
    
    # Check agent responses
    agent_responses = conv.get('agent_responses', [])
    if len(agent_responses) < 2:
        issues.append(f"Only {len(agent_responses)} agent responses (need 2+)")
    
    # Check handoffs
    handoffs = conv.get('agent_handoffs', [])
    # Handle both 'agent_persona' and 'agent' keys for agent names
    agents_used = list(set([r.get('agent_persona', r.get('agent', '')) for r in agent_responses]))
    
    # Extract tools used
    tools_used = []
    for resp in agent_responses:
        # Handle both 'tools_triggered' and 'tools' keys
        tools = resp.get('tools_triggered', resp.get('tools', []))
        # Handle both list of strings and list of dicts
        for tool in tools:
            if isinstance(tool, dict):
                tools_used.append(tool.get('name', 'unknown'))
            else:
                tools_used.append(tool)
    
    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'customer_turns': len(customer_turns),
        'agent_responses': len(agent_responses),
        'handoffs': len(handoffs),
        'agents_used': agents_used,
        'tools_used': tools_used
    }

def validate_dataset(dataset_dir, dataset_name):
    """Validate an entire dataset"""
    
    print(f"\n{'='*60}")
    print(f"🔍 VALIDATING: {dataset_name}")
    print(f"📁 Directory: {dataset_dir}")
    print(f"{'='*60}")
    
    files = [f for f in os.listdir(dataset_dir) if f.endswith('.json')]
    
    total_valid = 0
    total_issues = []
    all_tools = []
    all_agents = []
    turn_counts = []
    handoff_counts = []
    
    for file in files:
        result = validate_conversation(os.path.join(dataset_dir, file))
        
        if result['valid']:
            total_valid += 1
        else:
            total_issues.append((file, result['issues']))
        
        all_tools.extend(result['tools_used'])
        all_agents.extend(result['agents_used'])
        turn_counts.append(result['customer_turns'])
        handoff_counts.append(result['handoffs'])
    
    # Statistics
    print(f"\n📊 STATISTICS:")
    print(f"Total files: {len(files)}")
    print(f"Valid conversations: {total_valid}/{len(files)} ({100*total_valid/len(files):.1f}%)")
    print(f"Average customer turns: {sum(turn_counts)/len(turn_counts):.1f}")
    print(f"Average handoffs: {sum(handoff_counts)/len(handoff_counts):.1f}")
    print(f"Conversations with handoffs: {sum(1 for h in handoff_counts if h > 0)}/{len(files)}")
    
    # Agent distribution
    agent_counter = Counter(all_agents)
    print(f"\n👥 AGENT DISTRIBUTION:")
    for agent, count in agent_counter.most_common():
        print(f"  {agent}: {count}")
    
    # Tool distribution
    tool_counter = Counter(all_tools)
    print(f"\n🔧 TOP 10 TOOLS USED:")
    for tool, count in tool_counter.most_common(10):
        print(f"  {tool}: {count}")
    
    # Issues
    if total_issues:
        print(f"\n⚠️ ISSUES FOUND:")
        for file, issues in total_issues[:5]:
            print(f"  {file}: {issues}")
    
    return total_valid == len(files)

def check_tool_validity():
    """Check if tools match our defined set"""
    
    print(f"\n{'='*60}")
    print(f"🔧 CHECKING TOOL VALIDITY")
    print(f"{'='*60}")
    
    # Our defined tools
    defined_tools = {
        "verify_user", "get_customer_status", "route_to_agent",
        "check_esim_status", "check_device_imei", "reissue_activation_code", "create_tech_ticket",
        "get_customer_plan", "list_all_plans", "change_customer_plan", "check_plan_compatibility",
        "get_last_bill", "get_unpaid_amount", "apply_campaign_discount", "create_payment_note",
        "search_faq", "get_common_solutions", "send_help_sms", "create_info_ticket",
        "escalate_to_human", "end_conversation"
    }
    
    # Collect all tools from all datasets
    all_tools = set()
    
    for dataset_dir in ['data/varied_dataset/conversations', 'data/correct_flash_dataset', 'data/smart_flash_dataset']:
        if os.path.exists(dataset_dir):
            for file in os.listdir(dataset_dir):
                if file.endswith('.json'):
                    with open(os.path.join(dataset_dir, file), 'r') as f:
                        conv = json.load(f)
                    for resp in conv.get('agent_responses', []):
                        # Handle both 'tools_triggered' and 'tools' keys
                        tools = resp.get('tools_triggered', resp.get('tools', []))
                        for tool in tools:
                            if isinstance(tool, dict):
                                all_tools.add(tool.get('name', 'unknown'))
                            else:
                                all_tools.add(tool)
    
    # Check validity
    undefined_tools = all_tools - defined_tools
    unused_tools = defined_tools - all_tools
    
    print(f"✅ Tools used: {len(all_tools)}")
    print(f"✅ Defined tools: {len(defined_tools)}")
    
    if undefined_tools:
        print(f"\n❌ UNDEFINED TOOLS FOUND:")
        for tool in undefined_tools:
            print(f"  - {tool}")
    else:
        print(f"✅ All tools are valid!")
    
    if unused_tools:
        print(f"\n⚠️ UNUSED DEFINED TOOLS:")
        for tool in unused_tools:
            print(f"  - {tool}")

def main():
    print("🚀 DEEP VALIDATION CHECK")
    print("=" * 80)
    
    # Validate detailed dataset
    detailed_valid = validate_dataset('data/varied_dataset/conversations', 'DETAILED DATASET')
    
    # Validate short dataset
    short_valid = validate_dataset('data/correct_flash_dataset', 'SHORT DATASET')
    
    # Validate smart dataset if exists
    smart_valid = True
    if os.path.exists('data/smart_flash_dataset'):
        smart_valid = validate_dataset('data/smart_flash_dataset', 'SMART DATASET')
    
    # Check tool validity
    check_tool_validity()
    
    # Final verdict
    print(f"\n{'='*80}")
    print(f"🎯 FINAL VERDICT:")
    
    if detailed_valid and short_valid and smart_valid:
        print(f"✅ ALL DATASETS ARE VALID AND READY!")
        print(f"\n📊 TOTAL TRAINING DATA:")
        
        detailed_count = len([f for f in os.listdir('data/varied_dataset/conversations') if f.endswith('.json')])
        short_count = len([f for f in os.listdir('data/correct_flash_dataset') if f.endswith('.json')])
        smart_count = len([f for f in os.listdir('data/smart_flash_dataset') if f.endswith('.json')]) if os.path.exists('data/smart_flash_dataset') else 0
        
        print(f"  - Detailed conversations: {detailed_count}")
        print(f"  - Short conversations: {short_count}")
        print(f"  - Smart conversations: {smart_count}")
        print(f"  - TOTAL: {detailed_count + short_count + smart_count}")
        
        print(f"\n🎉 READY FOR:")
        print(f"  1. ElevenLabs TTS generation")
        print(f"  2. Training pair creation")
        print(f"  3. Gemma 3N fine-tuning")
    else:
        print(f"❌ VALIDATION FAILED - FIX ISSUES BEFORE PROCEEDING")

if __name__ == "__main__":
    main()