#!/usr/bin/env python3
"""
CREATE PERFECT EXAMPLES FOR GEMMA 3N TRAINING
These will be included to guide the model on EXACTLY what to do
"""

import json
from pathlib import Path

# Create PERFECT hand-crafted examples showing EXACTLY what we want
PERFECT_EXAMPLES = [
    {
        "audio": "data/tts_audio_final/flash_heavy_0174_turn_1.mp3",
        "text": "<agent>RouterAgent</agent>\n<tools>verify_user(tc_no=12345678910, mother_maiden_name=YI)->{verified:true, customer_id:CUS789456}</tools>\n<response>Merhaba, eSIM aktivasyon sorununuz için üzgünüz. Güvenliğiniz için kimlik doğrulaması yapmam gerekiyor. TC kimlik numaranızı ve annenizin kızlık soyadını söyler misiniz?</response>"
    },
    {
        "audio": "data/tts_audio_final/flash_heavy_0174_turn_2.mp3", 
        "text": "<agent>RouterAgent</agent>\n<tools>get_customer_status(customer_id=CUS789456)->{status:active, plan:Genç Tarife 10GB, balance:0}</tools>\n<tools>route_to_agent(from_agent=RouterAgent, to_agent=TechAgent, reason=eSIM activation issue)->{transferred:true}</tools>\n<response>Kimliğinizi doğruladım Can Bey. eSIM aktivasyon sorununuz için sizi teknik destek ekibine yönlendiriyorum. Lütfen hatta kalın.</response>"
    },
    {
        "audio": "data/tts_audio_final/flash_heavy_0174_turn_3.mp3",
        "text": "<agent>TechAgent</agent>\n<tools>check_esim_status(phone_number=5551234567)->{esim_active:false, issue:activation_pending}</tools>\n<tools>check_device_imei(imei=356789123456789)->{device_compatible:true, model:iPhone 14 Pro, esim_capable:true}</tools>\n<tools>reissue_activation_code(phone_number=5551234567)->{qr_code:QR789456, sms_sent:true, expires_in:24h}</tools>\n<response>Can Bey, iPhone 14 Pro cihazınız eSIM uyumlu. Aktivasyon sorununuzu çözmek için yeni QR kod oluşturdum ve SMS ile gönderdim. QR kodu taratarak 5 dakika içinde aktif edebilirsiniz.</response>"
    },
    {
        "audio": "data/tts_audio_final/flash_heavy_0074_turn_1.mp3",
        "text": "<agent>RouterAgent</agent>\n<tools>verify_user(tc_no=98765432109, mother_maiden_name=DE)->{verified:true, customer_id:CUS456789}</tools>\n<response>İyi günler efendim, Türk Telekom'a hoş geldiniz. Kimliğinizi doğrulamak için TC kimlik numaranızı ve annenizin kızlık soyadını alabilir miyim?</response>"
    },
    {
        "audio": "data/tts_audio_final/flash_heavy_0057_turn_1.mp3",
        "text": "<agent>RouterAgent</agent>\n<tools>verify_user(tc_no=55566677788, mother_maiden_name=KA)->{verified:true, customer_id:CUS112233}</tools>\n<response>Merhaba, size nasıl yardımcı olabilirim? Öncelikle güvenlik için kimlik doğrulaması yapalım.</response>"
    }
]

# Create extended examples with different scenarios
SCENARIO_EXAMPLES = [
    # Billing scenario
    {
        "scenario": "billing_inquiry",
        "audio": "data/tts_audio_final/flash_heavy_0082_turn_1.mp3",
        "text": "<agent>BillingAgent</agent>\n<tools>get_last_bill(customer_id=CUS123789)->{amount:299.90, period:2024-12, paid:false}</tools>\n<tools>get_unpaid_amount(customer_id=CUS123789)->{total_debt:599.80, overdue:299.90, current:299.90}</tools>\n<response>Son faturanız 299.90 TL tutarında ve ödenmemiş durumda. Toplam borcunuz 599.80 TL. Ödeme yapmak ister misiniz?</response>"
    },
    # Plan change scenario
    {
        "scenario": "plan_upgrade",
        "audio": "data/tts_audio_final/flash_heavy_0110_turn_1.mp3",
        "text": "<agent>PlanAgent</agent>\n<tools>get_customer_plan(customer_id=CUS445566)->{plan_name:Genç Tarife 10GB, monthly_fee:199.90, data_limit:10GB}</tools>\n<tools>list_all_plans()->{plans:[{name:200GB Mega, price:399},{name:Sınırsız Pro, price:599}]}</tools>\n<tools>change_customer_plan(customer_id=CUS445566, new_plan_id=PLAN_MEGA)->{success:true, effective_date:next_billing_cycle}</tools>\n<response>Mevcut Genç Tarife 10GB paketinizden 200GB Mega pakete geçişinizi tamamladım. Yeni paketiniz gelecek fatura döneminde aktif olacak.</response>"
    },
    # FAQ scenario
    {
        "scenario": "general_inquiry",
        "audio": "data/tts_audio_final/flash_heavy_0091_turn_1.mp3",
        "text": "<agent>FAQAgent</agent>\n<tools>search_faq(query=roaming tarifeleri)->{results:[{title:Yurtdışı Paketleri, content:Günlük 39TL}], found:3}</tools>\n<tools>send_help_sms(phone_number=5559998877, content=Roaming bilgileri)->{sent:true, delivery_status:delivered}</tools>\n<response>Yurtdışı roaming paketlerimiz günlük 39 TL'den başlıyor. Detaylı bilgileri SMS olarak gönderdim.</response>"
    },
    # Escalation scenario
    {
        "scenario": "escalation_needed",
        "audio": "data/tts_audio_final/flash_heavy_0145_turn_3.mp3",
        "text": "<agent>TechAgent</agent>\n<tools>create_tech_ticket(customer_id=CUS998877, issue_description=Complex network issue)->{ticket_id:TT789456, priority:high, estimated_resolution:2h}</tools>\n<tools>escalate_to_human(reason=Complex technical issue, priority=high)->{escalated:true, human_agent_id:H123, wait_time:30s}</tools>\n<response>Sorununuz için teknik destek kaydı oluşturdum. Konunun karmaşıklığı nedeniyle sizi uzman temsilcimize aktarıyorum. 30 saniye içinde bağlanacaksınız.</response>"
    },
    # End conversation scenario
    {
        "scenario": "successful_resolution",
        "audio": "data/tts_audio_final/flash_heavy_0155_turn_4.mp3",
        "text": "<agent>RouterAgent</agent>\n<tools>end_conversation(resolution_status=resolved)->{ended:true, satisfaction_survey_sent:true}</tools>\n<response>Sorununuz çözüldüğüne sevindim. İyi günler dilerim. Memnuniyet anketimiz SMS ile gönderilecek.</response>"
    }
]

def create_training_dataset_with_examples():
    """Create the complete training dataset with perfect examples first"""
    
    print("🎯 CREATING PERFECT TRAINING EXAMPLES FOR GEMMA 3N")
    print("=" * 60)
    
    # Start with perfect examples
    training_data = []
    
    print("\n📝 Adding PERFECT hand-crafted examples...")
    for i, example in enumerate(PERFECT_EXAMPLES):
        # Check if audio exists
        if Path(example["audio"]).exists():
            training_data.append(example)
            print(f"  ✅ Example {i+1}: {example['audio']}")
            
            # Parse and show what model will learn
            text = example["text"]
            agent = text.split("<agent>")[1].split("</agent>")[0] if "<agent>" in text else "Unknown"
            tools = text.count("<tools>")
            print(f"     → Agent: {agent}, Tools: {tools}")
    
    print(f"\n📝 Adding SCENARIO examples...")
    for scenario in SCENARIO_EXAMPLES:
        if Path(scenario["audio"]).exists():
            training_data.append({
                "audio": scenario["audio"],
                "text": scenario["text"]
            })
            print(f"  ✅ Scenario: {scenario['scenario']}")
    
    # Now add the rest of the refined data
    print("\n📝 Processing remaining conversations...")
    
    # Load all conversations
    with open('data/selected_for_tts.json', 'r') as f:
        selected = json.load(f)
    
    # Process each conversation (simplified version without Gemini for now)
    for conv_info in selected['conversations'][:20]:  # First 20 for testing
        conv_path = Path(conv_info['path'])
        if not conv_path.exists():
            continue
        
        with open(conv_path, 'r') as f:
            conv = json.load(f)
        
        conv_id = conv_info['id']
        customer_turns = conv.get('customer_turns_for_tts', [])
        agent_responses = conv.get('agent_responses', [])
        
        for i in range(min(len(customer_turns), len(agent_responses))):
            audio_file = f"data/tts_audio_final/{conv_id}_turn_{i+1}.mp3"
            
            if not Path(audio_file).exists():
                continue
            
            # Get agent response
            agent_response = agent_responses[i]
            agent_name = agent_response.get('agent_persona', 'RouterAgent')
            agent_text = agent_response.get('text', '')
            tools = agent_response.get('tools_triggered', [])
            
            # Fix agent names
            if agent_name == "TechnicalSupportAgent":
                agent_name = "TechAgent"
            elif agent_name == "SalesAgent":
                agent_name = "PlanAgent"
            
            # Create simplified training format
            output_text = f"<agent>{agent_name}</agent>\n"
            
            # Add tools with basic execution
            for tool in tools:
                if tool == "verify_user":
                    output_text += f"<tools>{tool}(tc_no=12345678910, mother_maiden_name=AY)->{{verified:true, customer_id:CUS{i:06d}}}</tools>\n"
                elif tool == "get_customer_status":
                    output_text += f"<tools>{tool}(customer_id=CUS{i:06d})->{{status:active, plan:Standard, balance:0}}</tools>\n"
                elif tool == "route_to_agent":
                    output_text += f"<tools>{tool}(from={agent_name}, to=TechAgent)->{{transferred:true}}</tools>\n"
                else:
                    output_text += f"<tools>{tool}()->{{success:true}}</tools>\n"
            
            output_text += f"<response>{agent_text}</response>"
            
            training_data.append({
                "audio": audio_file,
                "text": output_text
            })
    
    print(f"\n✅ Total training examples: {len(training_data)}")
    
    # Save as JSON
    with open('GEMMA3N_TRAINING_WITH_EXAMPLES.json', 'w', encoding='utf-8') as f:
        json.dump(training_data, f, ensure_ascii=False, indent=2)
    
    # Save as JSONL for training
    with open('gemma3n_training_final.jsonl', 'w', encoding='utf-8') as f:
        for item in training_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    print("\n" + "=" * 60)
    print("📄 FILES CREATED:")
    print("  - GEMMA3N_TRAINING_WITH_EXAMPLES.json")
    print("  - gemma3n_training_final.jsonl")
    
    # Show first example
    print("\n🎯 FIRST TRAINING EXAMPLE:")
    if training_data:
        print(f"INPUT (Audio): {training_data[0]['audio']}")
        print(f"OUTPUT (Text):")
        print(training_data[0]['text'])
    
    print("\n✅ READY FOR GEMMA 3N E4B-IT 4-BIT FINE-TUNING!")
    print("\nThe model will learn:")
    print("  1. Process Turkish audio input natively")
    print("  2. Identify the appropriate agent")
    print("  3. Execute tools with parameters")
    print("  4. Generate natural Turkish responses")
    print("  5. Handle handoffs between agents")
    
    return training_data

if __name__ == "__main__":
    training_data = create_training_dataset_with_examples()
    
    # Show statistics
    print(f"\n📊 DATASET STATISTICS:")
    print(f"  Total examples: {len(training_data)}")
    print(f"  Perfect examples: {len(PERFECT_EXAMPLES)}")
    print(f"  Scenario examples: {len(SCENARIO_EXAMPLES)}")
    print(f"  Audio files used: {len([t for t in training_data if Path(t['audio']).exists()])}")
    
    # Count agents
    agents = {}
    for item in training_data:
        if '<agent>' in item['text']:
            agent = item['text'].split('<agent>')[1].split('</agent>')[0]
            agents[agent] = agents.get(agent, 0) + 1
    
    print(f"\n👥 AGENT DISTRIBUTION:")
    for agent, count in agents.items():
        print(f"  - {agent}: {count} responses")