#!/usr/bin/env python3
"""
FINAL AUDIO TRAINING REFINER
Takes our 76 conversations with 441 audio files and refines them for Gemma 3N training
"""

import json
import os
from pathlib import Path
import google.generativeai as genai

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("❌ No API key!")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)

generation_config = {
    "temperature": 0.1,  # DETERMINISTIC
    "top_p": 0.9,
    "top_k": 20,
    "max_output_tokens": 1500,
    "candidate_count": 1
}

model = genai.GenerativeModel(
    "gemini-2.5-flash",
    generation_config=generation_config
)

# The 21 valid tools with their signatures
TOOL_SIGNATURES = {
    "verify_user": "verify_user(tc_no, mother_maiden_name) -> {verified, customer_id}",
    "get_customer_status": "get_customer_status(customer_id) -> {status, plan, balance}",
    "route_to_agent": "route_to_agent(from_agent, to_agent, reason) -> {transferred}",
    "check_esim_status": "check_esim_status(phone_number) -> {esim_active, issue}",
    "check_device_imei": "check_device_imei(imei) -> {device_compatible, model}",
    "reissue_activation_code": "reissue_activation_code(phone_number) -> {qr_code, sms_sent}",
    "create_tech_ticket": "create_tech_ticket(customer_id, issue) -> {ticket_id}",
    "get_customer_plan": "get_customer_plan(customer_id) -> {plan_name, monthly_fee}",
    "list_all_plans": "list_all_plans() -> {plans[]}",
    "change_customer_plan": "change_customer_plan(customer_id, new_plan) -> {success}",
    "check_plan_compatibility": "check_plan_compatibility(customer_id, plan_id) -> {compatible}",
    "get_last_bill": "get_last_bill(customer_id) -> {amount, period, paid}",
    "get_unpaid_amount": "get_unpaid_amount(customer_id) -> {total_debt, overdue}",
    "apply_campaign_discount": "apply_campaign_discount(customer_id, campaign) -> {applied, discount}",
    "create_payment_note": "create_payment_note(customer_id, note) -> {note_id}",
    "search_faq": "search_faq(query) -> {results[]}",
    "get_common_solutions": "get_common_solutions(issue_type) -> {solutions[]}",
    "send_help_sms": "send_help_sms(phone_number, content) -> {sent}",
    "create_info_ticket": "create_info_ticket(customer_id, request) -> {ticket_id}",
    "escalate_to_human": "escalate_to_human(reason, priority) -> {escalated}",
    "end_conversation": "end_conversation(resolution_status) -> {ended}"
}

def load_conversations_with_audio():
    """Load the 76 conversations we have audio for"""
    
    with open('data/selected_for_tts.json', 'r', encoding='utf-8') as f:
        selected = json.load(f)
    
    conversations = []
    for conv_info in selected['conversations']:
        conv_path = Path(conv_info['path'])
        if conv_path.exists():
            with open(conv_path, 'r', encoding='utf-8') as f:
                conv_data = json.load(f)
                conv_data['conv_id'] = conv_info['id']
                conversations.append(conv_data)
    
    return conversations

def refine_conversation_with_gemini(conversation):
    """Refine a single conversation using Gemini"""
    
    conv_id = conversation.get('conv_id', conversation.get('id', 'unknown'))
    customer_turns = conversation.get('customer_turns_for_tts', [])
    agent_responses = conversation.get('agent_responses', [])
    
    refined_training_pairs = []
    
    for i in range(min(len(customer_turns), len(agent_responses))):
        # Get customer turn
        customer_turn = customer_turns[i]
        
        # Handle nested structure
        if isinstance(customer_turn, dict):
            if len(customer_turn) == 1 and list(customer_turn.keys())[0].startswith('turn_'):
                turn_key = list(customer_turn.keys())[0]
                customer_turn = customer_turn[turn_key]
        
        customer_text = customer_turn.get('text', '')
        customer_emotion = customer_turn.get('emotion', 'normal')
        
        # Check if audio exists
        audio_file = f"data/tts_audio_final/{conv_id}_turn_{i+1}.mp3"
        if not Path(audio_file).exists():
            continue
        
        # Get agent response
        agent_response = agent_responses[i]
        agent_text = agent_response.get('text', '')
        agent_name = agent_response.get('agent_persona', 'RouterAgent')
        tools = agent_response.get('tools_triggered', [])
        
        # Fix agent names
        if agent_name == "TechnicalSupportAgent":
            agent_name = "TechAgent"
        elif agent_name == "SalesAgent":
            agent_name = "PlanAgent"
        
        # Create prompt for Gemini to refine
        prompt = f"""You are refining Turkish telco training data for an audio-to-text model.

CUSTOMER AUDIO CONTENT (what customer says in Turkish):
"{customer_text}"
Emotion: {customer_emotion}

CURRENT AGENT RESPONSE:
Agent: {agent_name}
Response: "{agent_text}"
Tools mentioned: {tools}

REFINE this into a complete training output with proper tool execution.
Use ONLY these valid tools: {list(TOOL_SIGNATURES.keys())}

Return EXACTLY this format (no JSON, just the formatted string):
<agent>{agent_name}</agent>
<tools>tool_name(param1=value1, param2=value2)->{{result1:value1, result2:value2}}</tools>
<response>Natural Turkish response that references the tool results</response>

Example:
<agent>RouterAgent</agent>
<tools>verify_user(tc_no=12345678910, mother_maiden_name=AY)->{{verified:true, customer_id:CUS123456}}</tools>
<response>Kimliğinizi doğruladım Sayın Müşteri. Size nasıl yardımcı olabilirim?</response>

Make the response natural and reference the tool execution results."""

        try:
            response = model.generate_content(prompt)
            refined_output = response.text.strip()
            
            # Create training pair
            training_pair = {
                "conversation_id": conv_id,
                "turn": i + 1,
                
                # INPUT: Audio file that Gemma 3N will load
                "audio_input": audio_file,
                
                # CONTEXT (for reference during training)
                "customer_text": customer_text,
                "customer_emotion": customer_emotion,
                
                # OUTPUT: What Gemma 3N should generate
                "model_output": refined_output
            }
            
            refined_training_pairs.append(training_pair)
            
        except Exception as e:
            # Fallback to simple format
            simple_output = f"<agent>{agent_name}</agent>\n"
            simple_output += f"<tools>{','.join(tools)}</tools>\n"
            simple_output += f"<response>{agent_text}</response>"
            
            training_pair = {
                "conversation_id": conv_id,
                "turn": i + 1,
                "audio_input": audio_file,
                "customer_text": customer_text,
                "customer_emotion": customer_emotion,
                "model_output": simple_output
            }
            
            refined_training_pairs.append(training_pair)
    
    return refined_training_pairs

def main():
    """Process all conversations and create final training dataset"""
    
    print("🚀 FINAL AUDIO TRAINING REFINER FOR GEMMA 3N")
    print("=" * 60)
    
    # Load conversations
    conversations = load_conversations_with_audio()
    print(f"📊 Loaded {len(conversations)} conversations with audio")
    
    # Process each conversation
    all_training_pairs = []
    
    for idx, conv in enumerate(conversations):
        conv_id = conv.get('conv_id', conv.get('id', f'conv_{idx}'))
        print(f"\n[{idx+1}/{len(conversations)}] Processing {conv_id}...")
        
        # Refine with Gemini
        refined_pairs = refine_conversation_with_gemini(conv)
        all_training_pairs.extend(refined_pairs)
        
        print(f"  ✅ Generated {len(refined_pairs)} training pairs")
    
    # Save complete dataset
    with open('GEMMA3N_FINAL_TRAINING_DATASET.json', 'w', encoding='utf-8') as f:
        json.dump(all_training_pairs, f, ensure_ascii=False, indent=2)
    
    # Create JSONL for actual training
    with open('gemma3n_training.jsonl', 'w', encoding='utf-8') as f:
        for pair in all_training_pairs:
            # Format for Gemma 3N training
            training_item = {
                "audio": pair["audio_input"],
                "text": pair["model_output"]
            }
            f.write(json.dumps(training_item, ensure_ascii=False) + '\n')
    
    # Create a sample to show
    print("\n" + "=" * 60)
    print("📄 SAMPLE TRAINING PAIR:")
    if all_training_pairs:
        sample = all_training_pairs[0]
        print(f"\nINPUT (Audio): {sample['audio_input']}")
        print(f"Customer says: \"{sample['customer_text'][:100]}...\"")
        print(f"\nOUTPUT (Model should generate):")
        print(sample['model_output'])
    
    print("\n" + "=" * 60)
    print("✅ TRAINING DATASET COMPLETE!")
    print(f"  Total training pairs: {len(all_training_pairs)}")
    print(f"  Conversations processed: {len(conversations)}")
    print("\n📄 Files created:")
    print("  - GEMMA3N_FINAL_TRAINING_DATASET.json")
    print("  - gemma3n_training.jsonl")
    print("\n🎯 READY FOR GEMMA 3N E4B-IT 4-BIT FINE-TUNING!")
    print("\nTraining format:")
    print("  INPUT: Customer audio file (native audio processing)")
    print("  OUTPUT: Agent response with tool execution")
    
    # Show statistics
    if all_training_pairs:
        agents = {}
        for pair in all_training_pairs:
            output = pair['model_output']
            if '<agent>' in output:
                agent = output.split('<agent>')[1].split('</agent>')[0]
                agents[agent] = agents.get(agent, 0) + 1
        
        print(f"\nAgent distribution:")
        for agent, count in agents.items():
            print(f"  - {agent}: {count} responses")

if __name__ == "__main__":
    main()