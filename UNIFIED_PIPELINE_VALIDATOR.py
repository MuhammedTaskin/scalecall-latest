#!/usr/bin/env python3
"""
Unified Pipeline Validator
Ensures all datasets fit together for training pipeline
"""

import os
import json
from typing import Dict, List, Tuple
from collections import defaultdict

class UnifiedPipelineValidator:
    def __init__(self):
        self.datasets = [
            ("data/varied_dataset/conversations", "detailed"),
            ("data/correct_flash_dataset", "short"),
            ("data/smart_flash_dataset", "smart"),
            ("data/quick_varied_dataset", "edge"),
            ("data/flash_heavy_dataset", "heavy")
        ]
        
        # Expected fields for training
        self.required_fields = {
            "customer_turns": ["customer_turns_for_tts", "customer_turns"],
            "agent_responses": ["agent_responses"],
            "id_field": ["id", "conversation_id"],
        }
        
        # Tool mapping consistency
        self.defined_tools = {
            "verify_user", "get_customer_status", "route_to_agent",
            "check_esim_status", "check_device_imei", "reissue_activation_code", "create_tech_ticket",
            "get_customer_plan", "list_all_plans", "change_customer_plan", "check_plan_compatibility",
            "get_last_bill", "get_unpaid_amount", "apply_campaign_discount", "create_payment_note",
            "search_faq", "get_common_solutions", "send_help_sms", "create_info_ticket",
            "escalate_to_human", "end_conversation",
            # Additional tools found in heavy dataset
            "check_service_status", "run_diagnostics", "check_billing_history",
            "resolve_billing_issue", "apply_credit", "temporary_international_line_activation",
            "fraud_detection_protocol_initiation", "check_line_status", "remote_line_management"
        }
        
        self.issues = []
        self.statistics = defaultdict(int)
    
    def analyze_structure(self, conv: Dict, dataset_type: str) -> Dict:
        """Analyze conversation structure"""
        
        result = {
            "has_id": False,
            "has_customer_turns": False,
            "has_agent_responses": False,
            "customer_turn_format": None,
            "agent_response_format": None,
            "has_handoffs": False,
            "tools_format": None,
            "issues": []
        }
        
        # Check ID
        if "id" in conv or "conversation_id" in conv:
            result["has_id"] = True
        else:
            result["issues"].append("Missing ID field")
        
        # Check customer turns
        if "customer_turns_for_tts" in conv:
            result["has_customer_turns"] = True
            result["customer_turn_format"] = "tts_format"
            # Check turn structure
            if conv["customer_turns_for_tts"]:
                sample_turn = conv["customer_turns_for_tts"][0]
                if "turn_id" not in sample_turn:
                    result["issues"].append("Missing turn_id in customer turns")
                if "text" not in sample_turn:
                    result["issues"].append("Missing text in customer turns")
                if "emotion" not in sample_turn:
                    result["issues"].append("Missing emotion in customer turns")
        elif "customer_turns" in conv:
            result["has_customer_turns"] = True
            result["customer_turn_format"] = "simple_format"
            # Check turn structure
            if conv["customer_turns"]:
                sample_turn = conv["customer_turns"][0]
                if "text" not in sample_turn:
                    result["issues"].append("Missing text in customer turns")
        else:
            result["issues"].append("No customer turns field")
        
        # Check agent responses
        if "agent_responses" in conv:
            result["has_agent_responses"] = True
            if conv["agent_responses"]:
                sample_resp = conv["agent_responses"][0]
                
                # Check agent field
                if "agent_persona" in sample_resp:
                    result["agent_response_format"] = "persona_format"
                elif "agent" in sample_resp:
                    result["agent_response_format"] = "simple_format"
                else:
                    result["issues"].append("Missing agent identifier")
                
                # Check tools field
                if "tools_triggered" in sample_resp:
                    result["tools_format"] = "triggered_format"
                elif "tools" in sample_resp:
                    result["tools_format"] = "simple_format"
                else:
                    result["issues"].append("Missing tools field")
        else:
            result["issues"].append("No agent responses field")
        
        # Check handoffs
        if "agent_handoffs" in conv and len(conv.get("agent_handoffs", [])) > 0:
            result["has_handoffs"] = True
        
        return result
    
    def validate_tools(self, conv: Dict) -> List[str]:
        """Validate tools used in conversation"""
        
        undefined_tools = []
        
        for resp in conv.get("agent_responses", []):
            tools = resp.get("tools_triggered", resp.get("tools", []))
            for tool in tools:
                if isinstance(tool, str) and tool not in self.defined_tools:
                    if tool not in undefined_tools:
                        undefined_tools.append(tool)
        
        return undefined_tools
    
    def create_unified_format(self, conv: Dict, dataset_type: str) -> Dict:
        """Convert to unified training format"""
        
        unified = {
            "id": conv.get("id", conv.get("conversation_id", "unknown")),
            "dataset_type": dataset_type,
            "customer_turns": [],
            "agent_turns": [],
            "handoffs": [],
            "metadata": {}
        }
        
        # Extract customer turns
        customer_data = conv.get("customer_turns_for_tts", conv.get("customer_turns", []))
        for i, turn in enumerate(customer_data):
            unified_turn = {
                "index": i + 1,
                "text": turn.get("text", ""),
                "emotion": turn.get("emotion", "normal")
            }
            
            # Add extra metadata if available
            if "dialect_markers" in turn:
                unified_turn["dialect"] = turn["dialect_markers"]
            if "pace" in turn:
                unified_turn["pace"] = turn["pace"]
            if "context" in turn:
                unified_turn["context"] = turn["context"]
            
            unified["customer_turns"].append(unified_turn)
        
        # Extract agent turns
        for i, resp in enumerate(conv.get("agent_responses", [])):
            agent_name = resp.get("agent_persona", resp.get("agent", "unknown"))
            tools = resp.get("tools_triggered", resp.get("tools", []))
            
            unified_turn = {
                "index": i + 1,
                "agent": agent_name,
                "text": resp.get("text", ""),
                "tools": tools if isinstance(tools, list) else []
            }
            
            unified["agent_turns"].append(unified_turn)
        
        # Extract handoffs
        for handoff in conv.get("agent_handoffs", []):
            unified["handoffs"].append({
                "at_turn": handoff.get("at_turn", 0),
                "from": handoff.get("from", ""),
                "to": handoff.get("to", ""),
                "reason": handoff.get("reason", "")
            })
        
        # Add metadata
        unified["metadata"]["complexity"] = conv.get("complexity", "medium")
        unified["metadata"]["scenario"] = conv.get("scenario", conv.get("primary_issue", "unknown"))
        unified["metadata"]["urgency"] = conv.get("urgency", "normal")
        
        return unified
    
    def validate_pipeline(self):
        """Validate entire pipeline compatibility"""
        
        print("🔍 UNIFIED PIPELINE VALIDATOR")
        print("="*80)
        
        all_conversations = []
        format_issues = defaultdict(list)
        
        for dataset_dir, dataset_type in self.datasets:
            if not os.path.exists(dataset_dir):
                print(f"⚠️ Dataset not found: {dataset_dir}")
                continue
            
            files = [f for f in os.listdir(dataset_dir) if f.endswith('.json')]
            print(f"\n📁 Checking {dataset_type} dataset ({len(files)} files)...")
            
            for file in files[:5]:  # Sample check
                with open(os.path.join(dataset_dir, file), 'r') as f:
                    conv = json.load(f)
                
                # Analyze structure
                structure = self.analyze_structure(conv, dataset_type)
                if structure["issues"]:
                    format_issues[dataset_type].extend(structure["issues"])
                
                # Check tools
                undefined = self.validate_tools(conv)
                if undefined:
                    self.statistics["undefined_tools"] += len(undefined)
                
                # Convert to unified format
                unified = self.create_unified_format(conv, dataset_type)
                all_conversations.append(unified)
                
                # Track statistics
                self.statistics["total_conversations"] += 1
                self.statistics[f"{dataset_type}_count"] += 1
                self.statistics["total_customer_turns"] += len(unified["customer_turns"])
                self.statistics["total_agent_turns"] += len(unified["agent_turns"])
                if unified["handoffs"]:
                    self.statistics["conversations_with_handoffs"] += 1
        
        # Report findings
        print("\n" + "="*80)
        print("📊 PIPELINE COMPATIBILITY REPORT")
        print("="*80)
        
        print("\n✅ STRUCTURE ANALYSIS:")
        for dataset_type, issues in format_issues.items():
            if issues:
                print(f"  {dataset_type}: {len(set(issues))} unique issues")
                for issue in set(issues):
                    print(f"    - {issue}")
            else:
                print(f"  {dataset_type}: ✅ No issues")
        
        print("\n📈 STATISTICS:")
        print(f"  Total conversations checked: {self.statistics['total_conversations']}")
        print(f"  Total customer turns: {self.statistics['total_customer_turns']}")
        print(f"  Total agent turns: {self.statistics['total_agent_turns']}")
        print(f"  Conversations with handoffs: {self.statistics['conversations_with_handoffs']}")
        
        print("\n🔧 TOOL COMPATIBILITY:")
        if self.statistics["undefined_tools"] > 0:
            print(f"  ⚠️ Found {self.statistics['undefined_tools']} undefined tools")
            print(f"  Consider adding these to the defined_tools set")
        else:
            print(f"  ✅ All tools are defined")
        
        # Training format recommendation
        print("\n📚 UNIFIED TRAINING FORMAT:")
        print("""
{
  "audio": "base64_encoded_customer_audio",
  "transcript": "customer_text",
  "emotion": "customer_emotion",
  "agent": "current_agent_persona",
  "response": "agent_response_text",
  "tools": ["list_of_tools_to_trigger"],
  "handoff": "next_agent_or_null"
}
        """)
        
        print("\n🎯 PIPELINE READINESS:")
        readiness_score = 100
        
        if format_issues:
            readiness_score -= 20
            print(f"  ⚠️ Format inconsistencies detected (-20%)")
        
        if self.statistics["undefined_tools"] > 0:
            readiness_score -= 10
            print(f"  ⚠️ Undefined tools found (-10%)")
        
        if self.statistics["conversations_with_handoffs"] < self.statistics["total_conversations"] * 0.5:
            readiness_score -= 10
            print(f"  ⚠️ Low handoff rate (-10%)")
        
        print(f"\n  🏆 READINESS SCORE: {readiness_score}%")
        
        if readiness_score >= 80:
            print(f"  ✅ Pipeline is ready for training!")
        else:
            print(f"  ⚠️ Some adjustments needed for optimal training")
        
        return all_conversations

def main():
    validator = UnifiedPipelineValidator()
    unified_data = validator.validate_pipeline()
    
    print("\n💡 RECOMMENDATIONS:")
    print("1. Create a unified converter script to standardize all formats")
    print("2. Add missing tools to the defined set")
    print("3. Generate TTS for customer turns")
    print("4. Create training pairs with audio + text + agent response")
    print("5. Fine-tune Gemma 3N with unified format")

if __name__ == "__main__":
    main()