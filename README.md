# 🚀 Scalecall - Premium Telco eSIM Agent

**Offline-first, agentic call center demo for telco eSIM workflows in Turkish**

A modern conversational AI system demonstrating:
- **Single on-device LLM** (Gemma-3 4B Instruct via MLX)
- **Function Calling** with strict JSON format
- **Prompt-Swap Handoff** (persona switching, same context)
- **Voice capabilities** (STT: Whisper PTT, TTS: XTTS-v2)
- **Premium React UI** with real-time event feed

## ✨ Features

### 🎯 **Core Capabilities**
- **End-to-end eSIM flow**: Verify → Device Check → Issue LPA → Activation
- **Multi-persona system**: Sales, Technical Support, FAQ specialists
- **Real-time WebSocket**: Streaming responses and live events
- **Voice interaction**: Press-to-talk STT, instant TTS with interrupt
- **PII protection**: Automatic masking of sensitive data

### 🛠 **Technical Stack**
- **Backend**: Python 3.11, FastAPI, WebSocket, SQLAlchemy (SQLite)
- **LLM**: Gemma-3 4B Instruct (MLX, 4-bit quantization, streaming)
- **Voice**: Whisper (faster-whisper), XTTS-v2 (sentence chunks)
- **Frontend**: React + TypeScript (Vite), Tailwind CSS v4, Radix Primitives
- **Evaluation**: Automated KPI tracking with 100+ test cases

## 🚀 Quick Start

### Prerequisites
- **macOS** (tested on M3 Pro)
- **Python 3.11+**
- **Node.js 18+**
- **MLX** compatible hardware

### 1. Clone & Setup
```bash
git clone https://github.com/MuhammedTaskin/scalecall-latest.git
cd scalecall-latest
```

### 2. Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Initialize database
python -c "from backend.db import init_db; init_db()"

# Start backend server
cd backend && python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Frontend Setup
```bash
# Install Node.js dependencies
cd frontend && npm install

# Start development server
npm run dev
```

### 4. Access the Application
- **Frontend UI**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🎬 Demo Script (1 minute)

### **Turkish eSIM Purchase Flow**

1. **Open**: http://localhost:5173
2. **Greeting**: `"Merhaba, eSIM almak istiyorum"`
3. **Verification**: `"Adım Ahmet Yılmaz, annemin kızlık soyadı Kaya, numaram 905551234567"`
4. **Device Check**: `"Cihazımı kontrol edebilir misiniz? IMEI: 123456789012345"`
5. **Package Selection**: Follow agent recommendations
6. **Watch**: Event Feed for function calls and persona handoffs!

### **Voice Features**
- **PTT**: Hold microphone button to speak
- **Interrupt**: Large red button stops TTS instantly
- **Transcript**: See STT results before sending

## 🏗 Architecture

### **Agentic System**
```
User Input → Orchestrator → LLM (Gemma-3) → Function Call/Handoff → Tools → Response
```

### **Message Types**
- `user_text`, `user_audio_*` → User inputs
- `model_delta` → Streaming LLM responses  
- `tool_call`, `tool_result` → Function execution
- `handoff` → Persona switching
- `tts_chunk` → Audio output
- `interrupt` → Stop TTS immediately

### **Tools Available**
- **Customer Verification**: Identity validation
- **Device Compatibility**: IMEI checking
- **Package Management**: eSIM plans and pricing
- **Order Processing**: LPA code generation
- **eSIM Activation**: Status tracking

## 📊 Evaluation System

### **Run KPI Analysis**
```bash
python backend/eval_runner.py
```

### **Metrics Tracked**
- **Success Rate**: End-to-end flow completion
- **Tool Accuracy**: Correct function calling
- **Response Latency**: Streaming performance
- **Handoff Quality**: Persona switching smoothness
- **PII Protection**: Sensitive data masking

### **Sample Output**
```
📊 TELCO AGENT KPI REPORT
========================
Test Cases: 100
Success Rate: 94%
Avg Latency: 1.2s
Tool Accuracy: 98%
PII Masking: 100%
```

## 🎨 UI Components

### **Core Components**
- **Chat.tsx**: Message interface with typing indicators
- **EventFeed.tsx**: Real-time system events sidebar
- **PersonaBadge.tsx**: Current agent persona display
- **MicButton.tsx**: Press-to-talk voice input
- **Interrupt.tsx**: Emergency TTS stop button

### **Design System**
- **Colors**: Professional blue/gray palette
- **Typography**: Inter (UI), IBM Plex Mono (code)
- **Animations**: Smooth transitions, persona changes
- **Responsive**: Mobile-friendly layout

## 🔧 Configuration

### **Backend Settings**
```python
# backend/config.py
MODEL_PATH = "mlx-community/Gemma-3-4B-Instruct-4bit"
MAX_TOKENS = 1024
TEMPERATURE = 0.7
STREAM_CHUNK_SIZE = 32
```

### **Frontend Environment**
```bash
# frontend/.env.local
VITE_WS_URL=ws://localhost:8000/ws
VITE_API_URL=http://localhost:8000
```

## 📝 Development

### **Backend Structure**
```
backend/
├── app.py                 # FastAPI application
├── orchestrator.py        # LLM orchestration
├── llm_abi.py            # MLX LLM provider
├── stt_service.py        # Whisper STT
├── tts_service.py        # XTTS-v2 TTS
├── db.py                 # Database models
├── eval_runner.py        # KPI evaluation
└── tools/
    ├── registry.py       # Tool management
    ├── telecom.py        # eSIM operations
    └── esim_extra.py     # Extended eSIM tools
```

### **Frontend Structure**
```
frontend/
├── src/
│   ├── App.tsx           # Main application
│   ├── components/       # React components
│   ├── lib/
│   │   ├── ws.ts         # WebSocket client
│   │   └── audio.ts      # Audio management
│   └── styles/
│       └── tokens.css    # Design tokens
├── tailwind.config.js    # Tailwind v4 config
└── package.json
```

## 🐛 Troubleshooting

### **Common Issues**

**MLX Installation**
```bash
# If MLX fails to install
pip install --upgrade pip
pip install mlx mlx-lm
```

**Tailwind CSS v4**
```bash
# If CSS not loading
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**WebSocket Connection**
```bash
# Check backend is running
curl http://localhost:8000/health
```

**Voice Features**
- Ensure microphone permissions in browser
- Check XTTS model download progress
- Verify audio device settings

## 📋 Todo / Future Enhancements

- [ ] **Multi-language support** (English, German)
- [ ] **Advanced eSIM provisioning** (QR code generation)
- [ ] **Customer analytics dashboard**
- [ ] **Voice activity detection** (no PTT required)
- [ ] **Integration tests** for all tools
- [ ] **Docker deployment** setup
- [ ] **Production monitoring** with metrics

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📞 Support

For questions or issues:
- Create an issue on GitHub
- Check the troubleshooting section
- Review API documentation at `/docs`

---

**Built with ❤️ for the future of conversational AI**