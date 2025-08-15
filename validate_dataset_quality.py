"""
Dataset Quality Validator - Check for errors and issues
"""
import json
import re
from typing import Dict, List, Tuple

def validate_json_structure(dialog: Dict) -> List[str]:
    """Validate dialog JSON structure."""
    errors = []
    
    # Check required fields
    if "conversations" not in dialog:
        errors.append("Missing 'conversations' field")
        return errors
    
    if not isinstance(dialog["conversations"], list):
        errors.append("'conversations' must be a list")
        return errors
    
    # Check each conversation turn
    for i, turn in enumerate(dialog["conversations"]):
        if "role" not in turn:
            errors.append(f"Turn {i}: Missing 'role'")
        if "content" not in turn:
            errors.append(f"Turn {i}: Missing 'content'")
        elif not isinstance(turn["content"], list):
            errors.append(f"Turn {i}: 'content' must be a list")
    
    return errors

def validate_tool_calls(dialog: Dict) -> List[str]:
    """Validate tool call syntax and format."""
    errors = []
    
    for i, turn in enumerate(dialog["conversations"]):
        if turn["role"] == "assistant":
            for content in turn["content"]:
                text = content.get("text", "")
                if "tool_call" in text:
                    try:
                        # Try to parse as JSON
                        tool_data = json.loads(text)
                        if "tool_call" in tool_data:
                            tc = tool_data["tool_call"]
                            if "id" not in tc:
                                errors.append(f"Turn {i}: tool_call missing 'id'")
                            if "name" not in tc:
                                errors.append(f"Turn {i}: tool_call missing 'name'")
                            if "arguments" not in tc:
                                errors.append(f"Turn {i}: tool_call missing 'arguments'")
                    except json.JSONDecodeError as e:
                        errors.append(f"Turn {i}: Invalid JSON in tool_call: {e}")
    
    return errors

def validate_turkish_quality(dialog: Dict) -> List[str]:
    """Check Turkish language quality."""
    errors = []
    
    # Common Turkish words that should appear
    turkish_indicators = ["mı", "mi", "mu", "mü", "nasıl", "nedir", "istiyorum", "yardım"]
    
    for i, turn in enumerate(dialog["conversations"]):
        if turn["role"] == "user":
            text = " ".join([c.get("text", "") for c in turn["content"]])
            # Check if text contains Turkish characters or words
            has_turkish = any(char in text for char in "çşğıöüÇŞĞIÖÜ") or \
                         any(word in text.lower() for word in turkish_indicators)
            
            if not has_turkish and len(text) > 10:
                errors.append(f"Turn {i}: User text may not be Turkish: '{text[:50]}...'")
    
    return errors

def validate_customer_consistency(dialog: Dict) -> List[str]:
    """Check customer ID consistency throughout dialog."""
    errors = []
    customer_ids = set()
    
    for i, turn in enumerate(dialog["conversations"]):
        if turn["role"] == "user" and any("tool_result" in c.get("text", "") for c in turn["content"]):
            # Extract customer ID from tool results
            for content in turn["content"]:
                text = content.get("text", "")
                if "tool_result" in text:
                    try:
                        result_data = json.loads(text.replace("<tool_result>", "").replace("</tool_result>", ""))
                        if "data" in result_data and "customer_id" in result_data["data"]:
                            customer_ids.add(result_data["data"]["customer_id"])
                    except:
                        pass
    
    if len(customer_ids) > 1:
        errors.append(f"Inconsistent customer IDs: {customer_ids}")
    
    return errors

def validate_dataset_sample(file_path: str, max_samples: int = 100):
    """Validate a sample of the dataset."""
    print(f"🔍 Validating dataset: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        if file_path.endswith('.jsonl'):
            dialogs = []
            for i, line in enumerate(f):
                if i >= max_samples:
                    break
                dialogs.append(json.loads(line))
        else:
            data = json.load(f)
            dialogs = data[:max_samples] if isinstance(data, list) else [data]
    
    total_errors = 0
    error_summary = {
        "json_structure": 0,
        "tool_calls": 0,
        "turkish_quality": 0,
        "customer_consistency": 0
    }
    
    for i, dialog in enumerate(dialogs):
        all_errors = []
        
        # Run all validations
        json_errors = validate_json_structure(dialog)
        tool_errors = validate_tool_calls(dialog)
        turkish_errors = validate_turkish_quality(dialog)
        consistency_errors = validate_customer_consistency(dialog)
        
        all_errors.extend(json_errors)
        all_errors.extend(tool_errors)
        all_errors.extend(turkish_errors)
        all_errors.extend(consistency_errors)
        
        error_summary["json_structure"] += len(json_errors)
        error_summary["tool_calls"] += len(tool_errors)
        error_summary["turkish_quality"] += len(turkish_errors)
        error_summary["customer_consistency"] += len(consistency_errors)
        
        if all_errors:
            print(f"❌ Dialog {i+1} errors:")
            for error in all_errors[:3]:  # Show first 3 errors
                print(f"   - {error}")
            if len(all_errors) > 3:
                print(f"   ... and {len(all_errors)-3} more")
            total_errors += len(all_errors)
    
    print(f"\n📊 Validation Results:")
    print(f"   Total dialogs checked: {len(dialogs)}")
    print(f"   Total errors found: {total_errors}")
    print(f"   Error rate: {total_errors/len(dialogs):.2f} errors per dialog")
    
    print(f"\n🔍 Error Breakdown:")
    for error_type, count in error_summary.items():
        print(f"   {error_type}: {count} errors")
    
    if total_errors == 0:
        print("🎉 Dataset validation PASSED! No errors found.")
    else:
        print(f"⚠️  Dataset has quality issues. Consider review and fixes.")
    
    return total_errors == 0

if __name__ == "__main__":
    import sys
    import os
    
    if len(sys.argv) > 1:
        # Validate specific file from command line
        file_path = sys.argv[1]
        print(f"🔍 Validating specific file: {file_path}")
        validate_dataset_sample(file_path, max_samples=50)
    else:
        # Validate the generated datasets
        data_dir = "data/generated"
        if os.path.exists(data_dir):
            files = [f for f in os.listdir(data_dir) if f.endswith('.json') and 'samples' not in f]
            for file in files[:3]:  # Check first 3 files
                validate_dataset_sample(f"{data_dir}/{file}", max_samples=50)
                print("="*60)
        else:
            print("No generated data found. Run dataset generation first.")
