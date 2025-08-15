"""
SFD to JSON Converter
Converts the ChatGPT's SFD format to our training JSON format
"""
import json
import re
import uuid
from typing import List, Dict, Any

def parse_sfd_dialog(sfd_text: str) -> Dict[str, Any]:
    """Parse a single SFD dialog into JSON format."""
    
    # Extract metadata
    metadata = {}
    for line in sfd_text.split('\n'):
        if ':' in line and any(key in line for key in ['id:', 'scenario:', 'context:', 'noise:', 'quality:']):
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip()
    
    # Parse conversations
    conversations = []
    lines = sfd_text.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        if line.startswith('U:'):
            # User message
            user_text = line[2:].strip()
            conversations.append({
                "role": "user",
                "content": [{"type": "text", "text": user_text}]
            })
        
        elif line.startswith('A:'):
            # Assistant message
            assistant_text = line[2:].strip()
            conversations.append({
                "role": "assistant", 
                "content": [{"type": "text", "text": assistant_text}]
            })
        
        elif line.startswith('TOOL:'):
            # Tool call
            tool_json = line[5:].strip()
            try:
                tool_data = json.loads(tool_json)
                # Add ID if missing
                if "id" not in tool_data:
                    tool_data["id"] = str(uuid.uuid4())
                
                tool_call_json = json.dumps({"tool_call": tool_data}, ensure_ascii=False)
                conversations.append({
                    "role": "assistant",
                    "content": [{"type": "text", "text": tool_call_json}]
                })
            except json.JSONDecodeError:
                print(f"Warning: Invalid tool JSON: {tool_json}")
        
        elif line.startswith('RESULT:'):
            # Tool result
            result_json = line[7:].strip()
            tool_result = f"<tool_result>{result_json}</tool_result>"
            conversations.append({
                "role": "user",
                "content": [{"type": "text", "text": tool_result}]
            })
        
        elif line.startswith('HANDOFF:'):
            # Persona handoff
            handoff_parts = line[8:].strip().split('|', 1)
            if len(handoff_parts) == 2:
                persona = handoff_parts[0].strip()
                message = handoff_parts[1].strip().strip('"')
                
                handoff_json = json.dumps({
                    "handoff": {"persona": persona, "say": message}
                }, ensure_ascii=False)
                
                conversations.append({
                    "role": "assistant",
                    "content": [{"type": "text", "text": handoff_json}]
                })
    
    # Build final dialog
    dialog = {
        "conversations": conversations,
        "scenario_type": metadata.get("scenario", "unknown"),
        "context": metadata.get("context", "GENERAL").upper(),
        "has_noise": metadata.get("noise", "false").lower() == "true",
        "quality_tier": metadata.get("quality", "intermediate")
    }
    
    return dialog

def convert_sfd_batch_to_json(sfd_batch_text: str) -> List[Dict[str, Any]]:
    """Convert a full SFD batch to JSON dialogs."""
    
    # Split by DIALOG_START/DIALOG_END
    dialog_pattern = r'DIALOG_START(.*?)DIALOG_END'
    dialog_matches = re.findall(dialog_pattern, sfd_batch_text, re.DOTALL)
    
    dialogs = []
    for match in dialog_matches:
        try:
            dialog = parse_sfd_dialog(match)
            dialogs.append(dialog)
        except Exception as e:
            print(f"Error parsing dialog: {e}")
    
    return dialogs

def save_dialogs_to_files(dialogs: List[Dict], batch_name: str = "batch01"):
    """Save dialogs to various file formats."""
    
    # Save complete JSON
    with open(f"data/chatgpt_{batch_name}_complete.json", "w", encoding="utf-8") as f:
        json.dump(dialogs, f, ensure_ascii=False, indent=2)
    
    # Save JSONL
    with open(f"data/chatgpt_{batch_name}.jsonl", "w", encoding="utf-8") as f:
        for dialog in dialogs:
            f.write(json.dumps(dialog, ensure_ascii=False) + "\n")
    
    # Save samples (first 5)
    with open(f"data/chatgpt_{batch_name}_samples.json", "w", encoding="utf-8") as f:
        json.dump(dialogs[:5], f, ensure_ascii=False, indent=2)
    
    print(f"✅ Saved {len(dialogs)} dialogs:")
    print(f"   - data/chatgpt_{batch_name}_complete.json")
    print(f"   - data/chatgpt_{batch_name}.jsonl")
    print(f"   - data/chatgpt_{batch_name}_samples.json")

# Example usage
if __name__ == "__main__":
    # Test with the provided SFD batch
    sfd_sample = """
DIALOG_START
id: D001
scenario: single_tool
context: COVERAGE
noise: true
quality: foundation
U: Merhaba, Sile Balibey tarafinda cekmiyo, telefonumda sinyal yok gibi.
A: Bölgenizde kapsama durumunu kontrol ediyorum. Bir saniye lütfen.
TOOL: {"name":"check_coverage","arguments":{"address":"İstanbul Şile Balibey Mahallesi"}}
RESULT: {"tech":"4G/5G","quality":"fair","note":"Vadi hattında zayıf sinyal; dış mekânda daha iyi"}
A: Bölgede kapsama orta görünüyor; dış mekânda performans daha iyi olacaktır. İsterseniz kapalı alanlar için sinyal güçlendirici önerilerini paylaşabilirim.
DIALOG_END
"""
    
    dialogs = convert_sfd_batch_to_json(sfd_sample)
    if dialogs:
        print("✅ Test conversion successful!")
        print(json.dumps(dialogs[0], ensure_ascii=False, indent=2))
    else:
        print("❌ Test conversion failed!")
