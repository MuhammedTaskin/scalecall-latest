# 🤖 Gemma3N-E4B Colab Integration Guide - TEKNOFEST 2025

## Overview

Complete guide to connect your finetuned Gemma3N-E4B model from Google Colab to the local system. The model runs on Colab GPU while the tools and database run locally.

## Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   Local System  │◀────────│     Internet     │────────▶│  Google Colab   │
│                 │  ngrok  │                  │  ngrok  │   (GPU + Model) │
│  - Audio Input  │  tunnel │                  │  tunnel │  - Gemma3N-E4B  │
│  - 21 Tools     │◀────────│   HTTP/WebSocket │────────▶│  - Inference    │
│  - PostgreSQL   │         │                  │         │  - Emotion AI   │
└─────────────────┘         └──────────────────┘         └─────────────────┘
```

## Step-by-Step Setup

### 1️⃣ **Prepare Your Finetuned Model**

If you've already finetuned your model:
```python
# Save your model after training
model.save_pretrained("/content/drive/MyDrive/gemma3n_teknofest")
tokenizer.save_pretrained("/content/drive/MyDrive/gemma3n_teknofest")
```

### 2️⃣ **Setup Colab Server**

1. Open Google Colab: https://colab.research.google.com
2. Create new notebook with **GPU runtime** (Runtime → Change runtime type → T4 GPU)
3. Upload `TEKNOFEST_GEMMA3N_COLAB.ipynb` or copy cells manually

### 3️⃣ **Run Colab Cells**

**Cell 1: Install Dependencies**
```python
!pip install transformers accelerate flask flask-cors pyngrok unsloth -q
```

**Cell 2: Load Your Model**
```python
# Option A: From saved checkpoint
MODEL_PATH = "/content/drive/MyDrive/gemma3n_teknofest"

# Option B: From HuggingFace Hub
MODEL_PATH = "your-username/gemma3n-teknofest"

# Option C: Use base model for testing
MODEL_PATH = "unsloth/gemma-2-2b-it-bnb-4bit"
```

**Cell 3: Start Server**
The server will start and show:
```
🔥 GEMMA3N MODEL SERVER READY!
📋 Copy this URL to your local system:
   https://abc123.ngrok.io
```

### 4️⃣ **Connect from Local System**

**Method 1: Interactive Connection**
```bash
python3 GEMMA3N_COLAB_INTEGRATION.py

# Enter the ngrok URL when prompted:
# https://abc123.ngrok.io
```

**Method 2: Direct Connection in Code**
```python
import asyncio
from GEMMA3N_COLAB_INTEGRATION import Gemma3NIntegratedSystem

async def main():
    system = Gemma3NIntegratedSystem()
    
    # Connect to your Colab model
    await system.setup("https://abc123.ngrok.io")
    
    # Process audio
    audio = load_audio("customer_call.wav")  # Your audio
    result = await system.process_customer_query(audio)
    
    print(f"Model Response: {result['model_response']}")
    print(f"Tools Executed: {result['tools_executed']}")

asyncio.run(main())
```

### 5️⃣ **Complete Integration with All Components**

```python
# Full system with Model + Tools + Database
import asyncio
from GEMMA3N_COLAB_INTEGRATION import Gemma3NIntegratedSystem
from LOCAL_TELCO_TOOLS import LocalTelcoToolExecutor
from COMPLETE_SYSTEM_ENHANCED import EnhancedAISystem

class UltimateSystem:
    def __init__(self):
        self.model_system = Gemma3NIntegratedSystem()
        self.tool_executor = LocalTelcoToolExecutor()
        self.enhanced_system = EnhancedAISystem()
    
    async def process(self, audio):
        # 1. Detect emotion locally (fast)
        emotion = self.detect_emotion(audio)
        
        # 2. Get response from Gemma3N on Colab
        model_response = await self.model_system.process_customer_query(audio)
        
        # 3. Execute suggested tools locally
        for tool in model_response['tools_suggested']:
            result = await self.tool_executor.execute_tool(tool, params)
        
        # 4. Return complete response
        return {
            "model": "gemma3n-e4b-finetuned",
            "response": model_response['model_response'],
            "tools": tool_results,
            "emotion": emotion
        }
```

## 🔥 Features of Integration

### What Runs on Colab (GPU):
- ✅ Gemma3N-E4B finetuned model
- ✅ Text generation with emotion awareness
- ✅ Tool suggestion from model
- ✅ Native audio processing (if implemented)

### What Runs Locally:
- ✅ Audio preprocessing
- ✅ Fast emotion detection
- ✅ 21 telco tool execution
- ✅ PostgreSQL database
- ✅ Error handling & fallback

### Communication:
- ✅ HTTP REST API via ngrok
- ✅ WebSocket for streaming (optional)
- ✅ Automatic fallback to mock mode
- ✅ Timeout protection

## 📊 Performance Metrics

| Component | Location | Latency | Notes |
|-----------|----------|---------|-------|
| Emotion Detection | Local | <50ms | CPU only |
| Model Inference | Colab GPU | 200-500ms | Depends on length |
| Tool Execution | Local | <100ms | Database queries |
| Total Pipeline | Combined | <1s | End-to-end |

## 🛠️ Troubleshooting

### Issue: Can't connect to Colab
**Solution**: 
- Check ngrok URL is correct
- Ensure Colab cell is still running
- Try restarting ngrok tunnel

### Issue: Slow response from model
**Solution**:
- Use T4/V100 GPU in Colab
- Reduce max_new_tokens
- Use 4-bit quantization

### Issue: Model not using emotion
**Solution**:
- Check prompt format matches training
- Ensure emotion is passed correctly
- Verify model was trained with emotion tags

## 📝 Example Conversation Flow

```python
# 1. User speaks (audio input)
audio = record_audio()  # 16kHz WAV

# 2. Local emotion detection (fast)
emotion = detect_emotion(audio)  # "angry"

# 3. Send to Colab model with emotion
request = {
    "audio": base64_encode(audio),
    "emotion": emotion,
    "text": "Faturamı öğrenmek istiyorum"
}

# 4. Model generates emotion-aware response
response = await colab_model.predict(request)
# Returns: {
#   "generated_text": "Üzgünüm, hemen kontrol ediyorum...",
#   "tools": ["get_current_balance", "view_invoice_details"]
# }

# 5. Execute tools locally
balance = await tool_executor.execute_tool("get_current_balance")

# 6. Final response to user
final = f"{response['generated_text']} Bakiyeniz: {balance['amount']} TL"
```

## 🚀 Advanced Features

### 1. Streaming Responses
```python
async for token in system.stream_response(audio, emotion):
    print(token, end="", flush=True)
```

### 2. Batch Processing
```python
audios = [audio1, audio2, audio3]
results = await system.batch_process(audios)
```

### 3. Model Switching
```python
# Switch between models dynamically
system.load_model("gemma3n-v2")  # Load different version
```

## 📚 Files Reference

| File | Purpose |
|------|---------|
| `TEKNOFEST_GEMMA3N_COLAB.ipynb` | Colab notebook to run model server |
| `GEMMA3N_COLAB_INTEGRATION.py` | Local connector to Colab model |
| `LOCAL_TELCO_TOOLS.py` | 21 tools implementation |
| `COMPLETE_SYSTEM_ENHANCED.py` | Error handling & orchestration |

## 🏆 Why This Architecture?

1. **Free GPU**: Use Colab's free T4 GPU
2. **Local Control**: Tools & database stay local
3. **Scalability**: Can switch to cloud GPU later
4. **Development**: Easy to test and iterate
5. **Production Path**: Same code works with real deployment

## 🎯 Quick Test

```bash
# 1. Start Colab notebook (get URL)
# 2. Run this locally:
python3 << EOF
import asyncio
from GEMMA3N_COLAB_INTEGRATION import Gemma3NIntegratedSystem
import numpy as np

async def test():
    system = Gemma3NIntegratedSystem()
    await system.setup("YOUR_NGROK_URL")  # From Colab
    
    audio = np.random.randn(8000) * 0.1
    result = await system.process_customer_query(audio)
    print(f"Success! Model: {result['model_used']}")

asyncio.run(test())
EOF
```

## 💡 Tips for TEKNOFEST

1. **Keep Colab Running**: Use `while True: time.sleep(60)` to prevent timeout
2. **Save Model Checkpoints**: Regular saves to Google Drive
3. **Log Everything**: Track all requests/responses for demo
4. **Prepare Offline Mode**: Have mock responses ready
5. **Test Before Demo**: Run full pipeline multiple times

---

**Ready to integrate your Gemma3N model! 🚀**