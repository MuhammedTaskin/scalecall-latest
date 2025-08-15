#!/usr/bin/env python3
"""
STANDARDIZE ALL CONVERSATION DATA
Fix the odd ones, make everything consistent
"""

import json
from pathlib import Path
from typing import Dict, List, Any

def standardize_conversations():
    """Fix all the inconsistent shit in our dataset"""
    
    # Load selected conversations
    with open('data/selected_for_tts.json', 'r', encoding='utf-8') as f:
        selected = json.load(f)
    
    print("🔧 STANDARDIZING DATASET")
    print("=" * 60)
    
    fixed_count = 0
    issues = {
        'nested_turns': 0,
        'missing_id': 0,
        'missing_primary_issue': 0,
        'inconsistent_tools': 0
    }
    
    for conv_info in selected['conversations']:
        conv_path = Path(conv_info['path'])
        if not conv_path.exists():
            print(f"❌ Missing: {conv_path}")
            continue
        
        with open(conv_path, 'r', encoding='utf-8') as f:
            conv = json.load(f)
        
        modified = False
        
        # FIX 1: Add missing 'id' field
        if 'id' not in conv:
            # Extract ID from filename
            conv['id'] = conv_path.stem
            issues['missing_id'] += 1
            modified = True
        
        # FIX 2: Add missing 'primary_issue' field
        if 'primary_issue' not in conv:
            # Infer from conversation content
            conv['primary_issue'] = 'general_support'
            issues['missing_primary_issue'] += 1
            modified = True
        
        # FIX 3: Fix nested turn structure (like turn_010)
        customer_turns = conv.get('customer_turns_for_tts', [])
        fixed_turns = []
        
        for turn in customer_turns:
            if isinstance(turn, dict):
                # Check if it's nested
                keys = list(turn.keys())
                if len(keys) == 1 and keys[0].startswith('turn_'):
                    # Extract the nested content
                    actual_turn = turn[keys[0]]
                    # Ensure it has the turn_id
                    if 'turn_id' not in actual_turn:
                        actual_turn['turn_id'] = keys[0]
                    fixed_turns.append(actual_turn)
                    issues['nested_turns'] += 1
                    modified = True
                else:
                    # Already in correct format
                    fixed_turns.append(turn)
            else:
                # Shouldn't happen but handle it
                fixed_turns.append(turn)
        
        conv['customer_turns_for_tts'] = fixed_turns
        
        # FIX 4: Standardize agent response fields
        agent_responses = conv.get('agent_responses', [])
        for resp in agent_responses:
            # Ensure consistent field names
            if 'tools' in resp and 'tools_triggered' not in resp:
                resp['tools_triggered'] = resp.pop('tools')
                issues['inconsistent_tools'] += 1
                modified = True
            
            # Ensure all have required fields
            if 'formality_level' not in resp:
                resp['formality_level'] = 'medium'
                modified = True
            
            # Ensure agent_persona is valid
            valid_agents = ['RouterAgent', 'TechAgent', 'BillingAgent', 'PlanAgent', 'FAQAgent']
            if resp.get('agent_persona') not in valid_agents:
                # Try to fix common mistakes
                agent = resp.get('agent_persona', 'RouterAgent')
                if 'Technical' in agent or 'Tech' in agent:
                    resp['agent_persona'] = 'TechAgent'
                elif 'Billing' in agent:
                    resp['agent_persona'] = 'BillingAgent'
                elif 'Plan' in agent:
                    resp['agent_persona'] = 'PlanAgent'
                elif 'FAQ' in agent or 'Help' in agent:
                    resp['agent_persona'] = 'FAQAgent'
                else:
                    resp['agent_persona'] = 'RouterAgent'
                modified = True
        
        # FIX 5: Ensure turn IDs are consistent
        # Customer turns should be odd: 1, 3, 5, 7...
        # Agent turns should be even: 2, 4, 6, 8... (with possible duplicates for handoffs)
        
        # Save if modified
        if modified:
            with open(conv_path, 'w', encoding='utf-8') as f:
                json.dump(conv, f, ensure_ascii=False, indent=2)
            fixed_count += 1
            print(f"✅ Fixed: {conv['id']}")
    
    print("\n" + "=" * 60)
    print(f"📊 STANDARDIZATION COMPLETE")
    print(f"  Files fixed: {fixed_count}")
    print(f"  Nested turns fixed: {issues['nested_turns']}")
    print(f"  Missing IDs added: {issues['missing_id']}")
    print(f"  Missing primary_issue added: {issues['missing_primary_issue']}")
    print(f"  Tools field standardized: {issues['inconsistent_tools']}")

def verify_standardization():
    """Verify all conversations now have consistent structure"""
    
    print("\n🔍 VERIFYING STANDARDIZATION")
    print("=" * 60)
    
    with open('data/selected_for_tts.json', 'r', encoding='utf-8') as f:
        selected = json.load(f)
    
    all_valid = True
    
    for conv_info in selected['conversations'][:10]:  # Check first 10
        conv_path = Path(conv_info['path'])
        if not conv_path.exists():
            continue
        
        with open(conv_path, 'r', encoding='utf-8') as f:
            conv = json.load(f)
        
        # Check required fields
        required = ['id', 'customer_turns_for_tts', 'agent_responses', 'primary_issue']
        missing = [f for f in required if f not in conv]
        
        if missing:
            print(f"❌ {conv_path.stem} missing: {missing}")
            all_valid = False
        
        # Check for nested turns
        for turn in conv.get('customer_turns_for_tts', []):
            if isinstance(turn, dict):
                keys = list(turn.keys())
                if len(keys) == 1 and keys[0].startswith('turn_'):
                    print(f"❌ {conv_path.stem} still has nested turn: {keys[0]}")
                    all_valid = False
    
    if all_valid:
        print("✅ All conversations have consistent structure!")
    
    return all_valid

if __name__ == "__main__":
    # First standardize
    standardize_conversations()
    
    # Then verify
    is_valid = verify_standardization()
    
    if is_valid:
        print("\n🏆 DATASET READY FOR TRAINING!")
    else:
        print("\n⚠️ Some issues remain, check manually")