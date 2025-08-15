#!/usr/bin/env python3
"""
Clean Invalid Tools from Flash Heavy Dataset
Removes conversations with undefined tools
"""

import os
import json
from typing import List, Set

# ONLY these tools are allowed
VALID_TOOLS = {
    "verify_user", "get_customer_status", "route_to_agent",
    "check_esim_status", "check_device_imei", "reissue_activation_code", "create_tech_ticket",
    "get_customer_plan", "list_all_plans", "change_customer_plan", "check_plan_compatibility",
    "get_last_bill", "get_unpaid_amount", "apply_campaign_discount", "create_payment_note",
    "search_faq", "get_common_solutions", "send_help_sms", "create_info_ticket",
    "escalate_to_human", "end_conversation"
}

def check_conversation_tools(conv_path: str) -> tuple[bool, List[str]]:
    """Check if conversation has invalid tools"""
    
    with open(conv_path, 'r', encoding='utf-8') as f:
        conv = json.load(f)
    
    invalid_tools = []
    
    for resp in conv.get('agent_responses', []):
        tools = resp.get('tools_triggered', resp.get('tools', []))
        for tool in tools:
            if isinstance(tool, str) and tool not in VALID_TOOLS:
                invalid_tools.append(tool)
    
    return len(invalid_tools) == 0, invalid_tools

def clean_dataset(dataset_dir: str):
    """Clean dataset by removing conversations with invalid tools"""
    
    if not os.path.exists(dataset_dir):
        print(f"❌ Directory not found: {dataset_dir}")
        return
    
    files = [f for f in os.listdir(dataset_dir) if f.endswith('.json')]
    
    print(f"🔍 Checking {len(files)} files in {dataset_dir}")
    
    valid_count = 0
    deleted_count = 0
    all_invalid_tools = set()
    
    for file in files:
        file_path = os.path.join(dataset_dir, file)
        is_valid, invalid_tools = check_conversation_tools(file_path)
        
        if is_valid:
            valid_count += 1
        else:
            # Delete file with invalid tools
            os.remove(file_path)
            deleted_count += 1
            all_invalid_tools.update(invalid_tools)
            print(f"  ❌ Deleted {file}: invalid tools {invalid_tools[:3]}")
    
    print(f"\n📊 CLEANING RESULTS:")
    print(f"  ✅ Valid conversations: {valid_count}")
    print(f"  ❌ Deleted conversations: {deleted_count}")
    
    if all_invalid_tools:
        print(f"\n🔧 Invalid tools found:")
        for tool in sorted(all_invalid_tools)[:10]:
            print(f"    - {tool}")
        if len(all_invalid_tools) > 10:
            print(f"    ... and {len(all_invalid_tools) - 10} more")
    
    return valid_count, deleted_count

def main():
    print("🧹 CLEANING FLASH HEAVY DATASET")
    print("="*60)
    
    # Clean Flash Heavy dataset
    dataset_dir = "data/flash_heavy_dataset"
    valid, deleted = clean_dataset(dataset_dir)
    
    print(f"\n✅ Dataset cleaned!")
    print(f"   Remaining valid conversations: {valid}")
    
    # Kill the running process if still generating
    print("\n⚠️ Killing any running Flash Heavy generation...")
    os.system("pkill -f FLASH_HEAVY_GENERATOR.py 2>/dev/null")
    
    print("\n🔄 Ready to restart generation with fixed tool list")

if __name__ == "__main__":
    main()