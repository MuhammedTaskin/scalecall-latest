# Alternative Cell 6 if audio causes issues
# Use this if the main Cell 6 doesn't work

# ============================================
# CELL 6: Load Dataset (Text-Only Fallback)
# ============================================
def format_telco_prompt(item):
    """Format for Gemma 3N training - text representation"""
    
    # Build instruction with audio path reference
    instruction = f"""Sen bir Türk telekom çağrı merkezi temsilcisisin.

Müşteri ses dosyası: {item['audio']}
Önceki konuşma: {item.get('context', 'Yeni konuşma başlangıcı')}

Müşteriye uygun yanıtı ver."""
    
    # Expected output
    response = item['output']['response']
    agent = item['output']['agent']
    tools = ', '.join(item['output']['tools']) if item['output']['tools'] else 'Araç yok'
    
    output = f"""Agent: {agent}
Araçlar: {tools}
Yanıt: {response}"""
    
    # Simple format that won't break
    text = f"### Instruction:\n{instruction}\n\n### Response:\n{output}"
    
    return text

# Load dataset
dataset_path = "/content/drive/MyDrive/teknofest/gemma3n_autonomous_training.jsonl"

examples = []
with open(dataset_path, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            item = json.loads(line)
            text = format_telco_prompt(item)
            if text:
                examples.append({"text": text})
        except Exception as e:
            print(f"Skipping line: {e}")
            continue

train_dataset = Dataset.from_list(examples)
print(f"✅ Loaded {len(train_dataset)} training examples")
print(f"   Format: Text-based (audio paths referenced)")

# Test tokenization with one example
test_text = train_dataset[0]["text"]
test_tokens = tokenizer(test_text, return_tensors="pt")
print(f"✅ Tokenization test passed")
print(f"   Sample length: {len(test_tokens['input_ids'][0])} tokens")