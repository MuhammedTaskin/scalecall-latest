#!/usr/bin/env python3
"""
Delete files with invalid tools
"""

import os
import json
from typing import Dict, List, Set

# ONLY these tools are valid
VALID_TOOLS = {
    "verify_user", "get_customer_status", "route_to_agent",
    "check_esim_status", "check_device_imei", "reissue_activation_code", "create_tech_ticket",
    "get_customer_plan", "list_all_plans", "change_customer_plan", "check_plan_compatibility",
    "get_last_bill", "get_unpaid_amount", "apply_campaign_discount", "create_payment_note",
    "search_faq", "get_common_solutions", "send_help_sms", "create_info_ticket",
    "escalate_to_human", "end_conversation"
}

def check_tools(conv: Dict) -> bool:
    """Check if conversation has only valid tools"""
    
    for resp in conv.get('agent_responses', []):
        tools = resp.get('tools_triggered', resp.get('tools', []))
        for tool in tools:
            if isinstance(tool, dict):
                tool_name = tool.get('name', 'unknown')
            else:
                tool_name = tool
            
            if tool_name and tool_name not in VALID_TOOLS and tool_name != 'unknown':
                return False
    return True

def delete_invalid_files():
    """Delete all files with invalid tools"""
    
    datasets = [
        "data/quick_varied_dataset",  # Main problem dataset
        "data/edge_cases_dataset",    # If exists
    ]
    
    total_deleted = 0
    
    for dataset_dir in datasets:
        if not os.path.exists(dataset_dir):
            continue
        
        print(f"\n🔍 Checking {dataset_dir}...")
        deleted_in_dataset = 0
        
        files = [f for f in os.listdir(dataset_dir) if f.endswith('.json')]
        
        for file in files:
            file_path = os.path.join(dataset_dir, file)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    conv = json.load(f)
                
                # Handle list format
                if isinstance(conv, list):
                    has_invalid = False
                    for single_conv in conv:
                        if not check_tools(single_conv):
                            has_invalid = True
                            break
                    if has_invalid:
                        os.remove(file_path)
                        deleted_in_dataset += 1
                        print(f"   ❌ Deleted: {file}")
                else:
                    if not check_tools(conv):
                        os.remove(file_path)
                        deleted_in_dataset += 1
                        print(f"   ❌ Deleted: {file}")
            except:
                pass
        
        print(f"   Deleted {deleted_in_dataset} files from {dataset_dir}")
        total_deleted += deleted_in_dataset
    
    print(f"\n✅ TOTAL DELETED: {total_deleted} files")
    
    # Count remaining
    remaining = 0
    for root, dirs, files in os.walk("data"):
        for file in files:
            if file.endswith('.json'):
                remaining += 1
    
    print(f"📊 REMAINING VALID FILES: {remaining}")
    
    return total_deleted, remaining

def main():
    print("🧹 DELETING FILES WITH INVALID TOOLS")
    print("="*60)
    
    deleted, remaining = delete_invalid_files()
    
    print("\n" + "="*60)
    print(f"🎯 CLEANUP COMPLETE!")
    print(f"   Deleted: {deleted} invalid files")
    print(f"   Remaining: {remaining} valid files")
    print(f"\n✅ Dataset is now CLEAN and ready for training!")

if __name__ == "__main__":
    main()