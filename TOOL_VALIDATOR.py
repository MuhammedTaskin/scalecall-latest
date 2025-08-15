#!/usr/bin/env python3
"""
Tool Validator - Check all datasets for tool validity
"""

import os
import json
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple

# ONLY these tools are valid
VALID_TOOLS = {
    "verify_user", "get_customer_status", "route_to_agent",
    "check_esim_status", "check_device_imei", "reissue_activation_code", "create_tech_ticket",
    "get_customer_plan", "list_all_plans", "change_customer_plan", "check_plan_compatibility",
    "get_last_bill", "get_unpaid_amount", "apply_campaign_discount", "create_payment_note",
    "search_faq", "get_common_solutions", "send_help_sms", "create_info_ticket",
    "escalate_to_human", "end_conversation"
}

class ToolValidator:
    def __init__(self):
        self.datasets = [
            ("data/varied_dataset/conversations", "Detailed"),
            ("data/correct_flash_dataset", "Short"),
            ("data/smart_flash_dataset", "Smart"),
            ("data/quick_varied_dataset", "Edge Cases"),
            ("data/flash_heavy_dataset", "Flash Heavy"),
            ("data/gemini_generated", "Gemini Generated"),
            ("data/generated", "Generated"),
            ("data/flash_lite_dataset", "Flash Lite")
        ]
        
        self.stats = {
            "total_files": 0,
            "valid_files": 0,
            "invalid_files": 0,
            "total_tools_used": 0,
            "invalid_tools_found": set(),
            "tool_frequency": Counter()
        }
    
    def extract_tools(self, conv: Dict) -> Tuple[List[str], List[str]]:
        """Extract all tools from a conversation"""
        
        valid_tools = []
        invalid_tools = []
        
        for resp in conv.get('agent_responses', []):
            # Handle both formats
            tools = resp.get('tools_triggered', resp.get('tools', []))
            
            for tool in tools:
                if isinstance(tool, dict):
                    tool_name = tool.get('name', 'unknown')
                else:
                    tool_name = tool
                
                if tool_name in VALID_TOOLS:
                    valid_tools.append(tool_name)
                else:
                    if tool_name and tool_name != 'unknown':
                        invalid_tools.append(tool_name)
        
        return valid_tools, invalid_tools
    
    def validate_file(self, file_path: str) -> Dict:
        """Validate a single file"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                conv = json.load(f)
        except:
            return {"valid": False, "error": "JSON parse error"}
        
        # Handle files that are lists vs single conversation
        if isinstance(conv, list):
            # Some datasets store multiple conversations in one file
            all_valid = []
            all_invalid = []
            for single_conv in conv:
                v, i = self.extract_tools(single_conv)
                all_valid.extend(v)
                all_invalid.extend(i)
            valid_tools, invalid_tools = all_valid, all_invalid
        else:
            valid_tools, invalid_tools = self.extract_tools(conv)
        
        return {
            "valid": len(invalid_tools) == 0,
            "valid_tools": valid_tools,
            "invalid_tools": invalid_tools,
            "total_tools": len(valid_tools) + len(invalid_tools)
        }
    
    def validate_dataset(self, dataset_dir: str, dataset_name: str) -> Dict:
        """Validate an entire dataset"""
        
        if not os.path.exists(dataset_dir):
            return {"exists": False}
        
        files = [f for f in os.listdir(dataset_dir) if f.endswith('.json')]
        
        dataset_stats = {
            "name": dataset_name,
            "total_files": len(files),
            "valid_files": 0,
            "invalid_files": 0,
            "invalid_tools": set(),
            "tool_usage": Counter()
        }
        
        for file in files:
            result = self.validate_file(os.path.join(dataset_dir, file))
            
            if result.get("valid"):
                dataset_stats["valid_files"] += 1
            else:
                dataset_stats["invalid_files"] += 1
                dataset_stats["invalid_tools"].update(result.get("invalid_tools", []))
            
            # Count tool usage
            for tool in result.get("valid_tools", []):
                dataset_stats["tool_usage"][tool] += 1
        
        return dataset_stats
    
    def run_validation(self):
        """Run validation on all datasets"""
        
        print("🔧 TOOL VALIDATION REPORT")
        print("="*80)
        print(f"Valid tools defined: {len(VALID_TOOLS)}")
        print("="*80)
        
        all_results = []
        total_valid = 0
        total_invalid = 0
        all_invalid_tools = set()
        
        for dataset_dir, dataset_name in self.datasets:
            result = self.validate_dataset(dataset_dir, dataset_name)
            
            if not result.get("exists", True):
                continue
            
            all_results.append(result)
            total_valid += result["valid_files"]
            total_invalid += result["invalid_files"]
            all_invalid_tools.update(result["invalid_tools"])
            
            # Print dataset summary
            print(f"\n📁 {dataset_name}:")
            print(f"   Files: {result['total_files']}")
            print(f"   ✅ Valid: {result['valid_files']}")
            print(f"   ❌ Invalid: {result['invalid_files']}")
            
            if result["invalid_files"] > 0:
                print(f"   ⚠️ Invalid tools found: {len(result['invalid_tools'])}")
                # Show first 5 invalid tools
                for tool in list(result["invalid_tools"])[:5]:
                    print(f"      - {tool}")
                if len(result["invalid_tools"]) > 5:
                    print(f"      ... and {len(result['invalid_tools']) - 5} more")
        
        # Global statistics
        print("\n" + "="*80)
        print("📊 GLOBAL STATISTICS:")
        print(f"   Total files: {total_valid + total_invalid}")
        print(f"   ✅ Valid files: {total_valid}")
        print(f"   ❌ Invalid files: {total_invalid}")
        print(f"   Success rate: {100*total_valid/(total_valid+total_invalid):.1f}%")
        
        if all_invalid_tools:
            print(f"\n🔴 Total unique invalid tools: {len(all_invalid_tools)}")
        
        # Tool usage frequency (across all valid files)
        print("\n📈 TOP 10 MOST USED VALID TOOLS:")
        global_tool_usage = Counter()
        for result in all_results:
            global_tool_usage.update(result["tool_usage"])
        
        for tool, count in global_tool_usage.most_common(10):
            print(f"   {tool}: {count} uses")
        
        # Unused tools
        used_tools = set(global_tool_usage.keys())
        unused_tools = VALID_TOOLS - used_tools
        if unused_tools:
            print(f"\n⚠️ DEFINED BUT NEVER USED:")
            for tool in unused_tools:
                print(f"   - {tool}")
        
        return {
            "total_valid": total_valid,
            "total_invalid": total_invalid,
            "invalid_tools": all_invalid_tools
        }
    
    def clean_invalid_files(self, delete: bool = False):
        """Remove or report files with invalid tools"""
        
        print("\n🧹 CLEANING RECOMMENDATIONS:")
        
        files_to_clean = []
        
        for dataset_dir, dataset_name in self.datasets:
            if not os.path.exists(dataset_dir):
                continue
            
            for file in os.listdir(dataset_dir):
                if not file.endswith('.json'):
                    continue
                
                file_path = os.path.join(dataset_dir, file)
                result = self.validate_file(file_path)
                
                if not result.get("valid"):
                    files_to_clean.append({
                        "path": file_path,
                        "dataset": dataset_name,
                        "invalid_tools": result.get("invalid_tools", [])
                    })
        
        print(f"Found {len(files_to_clean)} files with invalid tools")
        
        if delete and files_to_clean:
            response = input("Delete these files? (y/n): ")
            if response.lower() == 'y':
                for file_info in files_to_clean:
                    os.remove(file_info["path"])
                    print(f"   Deleted: {file_info['path']}")
                print(f"✅ Deleted {len(files_to_clean)} files")
        else:
            print("Run with delete=True to remove invalid files")
        
        return files_to_clean

def main():
    validator = ToolValidator()
    
    # Run validation
    results = validator.run_validation()
    
    # Decision point
    print("\n" + "="*80)
    print("🎯 DECISION REQUIRED:")
    
    if results["total_invalid"] > 0:
        print(f"⚠️ Found {results['total_invalid']} files with invalid tools")
        print("\nOptions:")
        print("1. Delete invalid files (lose data but ensure quality)")
        print("2. Keep them (more data but potential errors)")
        print("3. Fix them (map invalid tools to valid ones)")
        
        # Show cleaning option
        validator.clean_invalid_files(delete=False)
    else:
        print("✅ ALL FILES ARE VALID!")
        print("🚀 Ready for training!")

if __name__ == "__main__":
    main()