# TEKNOFEST 2025 - Enterprise Telco AI Platform

Production-ready autonomous customer service system with emotion recognition, tool orchestration, and multimodal AI capabilities.

## System Architecture

- **Enterprise Telco Platform**: Core AI system with 21 telco tools
- **Turkish TTS Engine**: Professional voice synthesis 
- **Database**: SQLite with 5 customers and complete telco operations
- **Agent Handoff**: 7 specialized agents with context preservation
- **Colab Integration**: Fine-tuned Gemma 3N model server

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the complete system
./START_SYSTEM.sh

# 3. Or start with Colab model
./START_SYSTEM.sh https://your-ngrok-url.ngrok.io
```

## System Components

### Core Files
- `ENTERPRISE_TELCO_PLATFORM.py` - Main AI platform
- `database_config.py` - SQLite database with telco operations
- `TURKISH_TTS_ENGINE.py` - Professional Turkish text-to-speech
- `AGENT_HANDOFF_SYSTEM.py` - Multi-agent orchestration
- `TEKNOFEST_COLAB_SERVER.py` - Colab model server
- `tr_TR-fahrettin-medium.onnx` - Turkish TTS model (63MB)

### System Health
```bash
curl http://localhost:8000/health
```

## API Usage

```bash
# Process customer request
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Faturamı öğrenmek istiyorum"}'

# Get audio response
curl http://localhost:8000/audio/{filename}
```

## Features

✓ Production-Ready Architecture  
✓ 21 Integrated Telecommunications Tools  
✓ Advanced Emotion Recognition Engine  
✓ Real-time Tool Orchestration  
✓ Gemma 3N Model Integration Support  
✓ Zero External Dependencies  
✓ Turkish TTS with Emotion-Aware Voice  
✓ Multi-Agent Handoff System  
✓ SQLite Database with Telco Operations

## Government Presentation Ready

This system is designed for professional government presentation with:
- Enterprise-grade error handling
- Comprehensive logging
- Production database
- Professional Turkish responses
- Complete working demonstration
