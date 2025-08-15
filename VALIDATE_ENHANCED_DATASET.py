#!/usr/bin/env python3
"""
Validate the enhanced dataset for TEKNOFEST 2025 requirements
"""

import json
from pathlib import Path
from collections import Counter

def validate_dataset():
    """Comprehensive validation of the enhanced dataset"""
    
    print("🔍 VALIDATING ENHANCED DATASET FOR TEKNOFEST 2025")
    print("=" * 60)
    
    # Load dataset
    with open('enhanced_training.jsonl', 'r', encoding='utf-8') as f:
        training_items = [json.loads(line) for line in f]
    
    print(f"📊 Total training items: {len(training_items)}")
    
    # Validation checks
    issues = []
    
    # 1. Check for tool execution details
    print("\n1️⃣ CHECKING TOOL EXECUTION DETAILS...")
    no_tools = 0
    tool_counts = Counter()
    
    for item in training_items:
        tools = item.get('tools', [])
        if not tools:
            no_tools += 1
        for tool in tools:
            tool_counts[tool] += 1
    
    print(f"   ✅ Items with tools: {len(training_items) - no_tools}/{len(training_items)}")
    print(f"   ⚠️ Items without tools: {no_tools}")
    
    if no_tools > len(training_items) * 0.3:  # More than 30% without tools
        issues.append("TOO MANY RESPONSES WITHOUT TOOLS")
    
    # 2. Check for tool execution results
    print("\n2️⃣ CHECKING TOOL EXECUTION RESULTS...")
    # The simple enhancer doesn't include execution results
    issues.append("NO TOOL EXECUTION RESULTS (params, returns, duration)")
    
    # 3. Check for handoffs
    print("\n3️⃣ CHECKING AGENT HANDOFFS...")
    agent_counts = Counter()
    handoff_count = 0
    
    prev_conv_id = None
    prev_agent = None
    
    for item in training_items:
        agent = item.get('agent', 'unknown')
        agent_counts[agent] += 1
        
        conv_id = item.get('conversation_id')
        if conv_id == prev_conv_id and agent != prev_agent and prev_agent:
            handoff_count += 1
        
        prev_conv_id = conv_id
        prev_agent = agent
    
    print(f"   ✅ Total handoffs detected: {handoff_count}")
    print(f"   ✅ Agent distribution: {dict(agent_counts)}")
    
    if handoff_count < 50:  # Should have many handoffs across 76 conversations
        issues.append("INSUFFICIENT AGENT HANDOFFS")
    
    # 4. Check for system prompts
    print("\n4️⃣ CHECKING SYSTEM PROMPTS...")
    has_system_prompt = sum(1 for item in training_items if 'system_prompt' in item)
    print(f"   ⚠️ Items with system_prompt: {has_system_prompt}/{len(training_items)}")
    
    if has_system_prompt == 0:
        issues.append("NO SYSTEM PROMPTS FOR AGENTS")
    
    # 5. Check audio file references
    print("\n5️⃣ CHECKING AUDIO FILE REFERENCES...")
    missing_audio = 0
    audio_files = set()
    
    for item in training_items:
        audio_file = item.get('audio_file')
        if audio_file:
            audio_files.add(audio_file)
            if not Path(audio_file).exists():
                missing_audio += 1
    
    print(f"   ✅ Unique audio files: {len(audio_files)}")
    print(f"   ⚠️ Missing audio files: {missing_audio}")
    
    if missing_audio > 0:
        issues.append(f"{missing_audio} AUDIO FILES NOT FOUND")
    
    # 6. Check for dynamic persona switching
    print("\n6️⃣ CHECKING DYNAMIC PERSONA SWITCHING...")
    # This requires tracking handoff reasons and context
    issues.append("NO HANDOFF REASONS OR CONTEXT")
    
    # 7. Check for customer sentiment tracking
    print("\n7️⃣ CHECKING CUSTOMER SENTIMENT...")
    has_emotion = sum(1 for item in training_items if 'customer_emotion' in item)
    print(f"   ✅ Items with customer_emotion: {has_emotion}/{len(training_items)}")
    
    # 8. Check tool variety
    print("\n8️⃣ CHECKING TOOL VARIETY...")
    print(f"   ✅ Unique tools used: {len(tool_counts)}")
    print(f"   Top 5 tools: {tool_counts.most_common(5)}")
    
    expected_tools = {
        "verify_user", "get_customer_status", "route_to_agent",
        "check_esim_status", "check_device_imei", "reissue_activation_code",
        "create_tech_ticket", "get_customer_plan", "list_all_plans",
        "change_customer_plan", "check_plan_compatibility",
        "get_last_bill", "get_unpaid_amount", "apply_campaign_discount",
        "create_payment_note", "search_faq", "get_common_solutions",
        "send_help_sms", "create_info_ticket", "escalate_to_human",
        "end_conversation"
    }
    
    missing_tools = expected_tools - set(tool_counts.keys())
    if missing_tools:
        print(f"   ⚠️ Missing tools: {missing_tools}")
        issues.append(f"MISSING {len(missing_tools)} EXPECTED TOOLS")
    
    # 9. Check for multi-turn conversations
    print("\n9️⃣ CHECKING CONVERSATION DEPTH...")
    conv_turns = Counter()
    for item in training_items:
        conv_turns[item['conversation_id']] += 1
    
    avg_turns = sum(conv_turns.values()) / len(conv_turns)
    print(f"   ✅ Average turns per conversation: {avg_turns:.1f}")
    print(f"   ✅ Conversations with 5+ turns: {sum(1 for c, t in conv_turns.items() if t >= 5)}")
    
    # Final verdict
    print("\n" + "=" * 60)
    print("🎯 VALIDATION RESULTS:")
    
    if issues:
        print("\n❌ CRITICAL ISSUES FOUND:")
        for issue in issues:
            print(f"   • {issue}")
        
        print("\n⚠️ THE SIMPLE ENHANCER IS NOT SUFFICIENT!")
        print("\n📋 MISSING AGENTIC CAPABILITIES:")
        print("   1. Tool execution results (params, returns, duration_ms)")
        print("   2. System prompts for each agent")
        print("   3. Handoff decisions with reasons")
        print("   4. Customer sentiment journey tracking")
        print("   5. Dynamic agent switching logic")
        print("   6. Next action planning")
        
        return False
    else:
        print("\n✅ Dataset meets basic requirements!")
        return True

def suggest_improvements():
    """Suggest improvements for the dataset"""
    
    print("\n" + "=" * 60)
    print("💡 RECOMMENDED IMPROVEMENTS:")
    print("""
1. USE GEMINI 2.5 FLASH TO GENERATE:
   - Tool execution parameters and results
   - System prompts for each agent turn
   - Handoff decisions with reasons
   - Customer sentiment analysis
   - Next action planning

2. STRUCTURE EACH TURN WITH:
   {
       "agent": "TechAgent",
       "system_prompt": "Sen bir Türk telekom teknik destek uzmanısın...",
       "response_text": "...",
       "tool_calls": [
           {
               "tool": "check_esim_status",
               "params": {"phone_number": "5551234567"},
               "result": {"esim_active": false, "issue": "activation_pending"},
               "duration_ms": 800
           }
       ],
       "handoff": {
           "needed": true,
           "to_agent": "BillingAgent",
           "reason": "Customer has billing concerns"
       },
       "customer_sentiment": {
           "current": "worried",
           "predicted_next": "relieved"
       },
       "next_action": "wait_for_customer_response"
   }

3. ENSURE REALISTIC FLOW:
   - RouterAgent always starts (verifies user)
   - Handoffs happen based on issue type
   - Tools are executed with realistic params
   - Results affect the conversation flow
""")

if __name__ == "__main__":
    is_valid = validate_dataset()
    
    if not is_valid:
        suggest_improvements()
        print("\n🚀 RECOMMENDATION: Use COMPLETE_AGENTIC_DATASET_GENERATOR.py")
        print("   with Gemini 2.5 Flash to generate full agentic capabilities!")
    else:
        print("\n✅ Dataset is ready for training!")