#!/usr/bin/env python3
"""
DIRECT AGENT CONVERSATION TEST
Talk to AI agents via voice input - no frontend needed!
"""
import asyncio
import pyaudio
import base64
import sys
import threading
import json

# Add backend to path
sys.path.insert(0, 'backend')

from backend.stt_service import STTService
from backend.orchestrator import Orchestrator

class VoiceAgentChat:
    def __init__(self):
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.frames = []
        self.is_recording = False
        self.stream = None
        self.p = None
        
        # Initialize services
        self.stt = None
        self.orchestrator = None
        self.messages = []
        self.current_persona = "RouterAgent"
        
    async def initialize(self):
        """Initialize STT and orchestrator."""
        print("🤖 Initializing AI Agent System...")
        
        # Initialize STT
        self.stt = STTService()
        await self.stt.initialize()
        print("✅ Speech-to-Text ready")
        
        # Initialize orchestrator
        self.orchestrator = Orchestrator()
        print("✅ AI Orchestrator ready")
        
        print("✅ Agent conversation system ready!")
        
    def start_recording(self):
        """Start recording audio."""
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        self.frames = []
        self.is_recording = True
        
        print("🔴 RECORDING... (Press ENTER to stop)")
        
        # Start recording in background thread
        self.record_thread = threading.Thread(target=self._record_loop)
        self.record_thread.start()
    
    def _record_loop(self):
        """Background recording loop."""
        while self.is_recording:
            try:
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                self.frames.append(data)
            except Exception as e:
                print(f"Recording error: {e}")
                break
    
    def stop_recording(self):
        """Stop recording and return audio data."""
        self.is_recording = False
        
        if hasattr(self, 'record_thread') and self.record_thread:
            self.record_thread.join()
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        if self.p:
            self.p.terminate()
        
        print("⏹️ Recording stopped!")
        
        return b''.join(self.frames) if self.frames else b''

    def audio_to_base64_chunks(self, audio_data, chunk_size=1600):
        """Convert audio data to base64 chunks."""
        chunks = []
        for i in range(0, len(audio_data), chunk_size):
            chunk = audio_data[i:i + chunk_size]
            base64_chunk = base64.b64encode(chunk).decode('utf-8')
            chunks.append(base64_chunk)
        return chunks

    async def process_voice_input(self):
        """Record voice and convert to text."""
        print("\n🎤 Press ENTER to start speaking...")
        input()  # Wait for ENTER
        
        # Start recording
        self.start_recording()
        
        # Wait for user to press ENTER again
        input()  # This blocks until ENTER is pressed
        
        # Stop recording
        audio_data = self.stop_recording()
        
        if len(audio_data) < 1000:  # Too short
            print("❌ Recording too short, try again")
            return None
        
        print("🔄 Converting speech to text...")
        
        # Convert to chunks and transcribe
        chunks = self.audio_to_base64_chunks(audio_data)
        transcript = await self.stt.transcribe_audio(chunks)
        
        if transcript:
            print(f"📝 You said: '{transcript}'")
            return transcript
        else:
            print("❌ Could not understand speech, try again")
            return None

    async def talk_to_agent(self, text):
        """Send text to AI agent and get response."""
        print(f"\n💭 Sending to {self.current_persona}...")
        
        # Add user message to conversation
        user_message = {"role": "user", "content": text}
        self.messages.append(user_message)
        
        print("🤖 Agent is thinking...")
        
        try:
            # Stream response from orchestrator
            full_response = ""
            async for chunk in self.orchestrator.stream(self.messages, self.current_persona):
                if "delta" in chunk:
                    # Print agent response as it streams
                    delta = chunk["delta"]
                    print(delta, end="", flush=True)
                    full_response += delta
                    
                elif "tool_call" in chunk:
                    tool_call = chunk["tool_call"]
                    print(f"\n🔧 Agent is using tool: {tool_call['name']}")
                    
                    # Execute tool
                    tool_result = await self.orchestrator.execute_tool(tool_call)
                    print(f"🔧 Tool result: {tool_result}")
                    
                elif "handoff" in chunk:
                    new_persona = chunk["handoff"]["persona"]
                    print(f"\n🔄 Transferring to: {new_persona}")
                    self.current_persona = new_persona
                    
                elif "complete" in chunk:
                    # Add assistant response to conversation
                    if full_response:
                        assistant_message = {"role": "assistant", "content": full_response}
                        self.messages.append(assistant_message)
                    break
            
            print("\n")  # New line after response
            
        except Exception as e:
            print(f"\n❌ Agent error: {e}")
            import traceback
            traceback.print_exc()

    async def conversation_loop(self):
        """Main conversation loop."""
        print("\n" + "="*60)
        print("🎙️  VOICE CONVERSATION WITH AI AGENTS")
        print("="*60)
        print(f"Current Agent: {self.current_persona}")
        print("\nInstructions:")
        print("1. Press ENTER to start recording")
        print("2. Speak your question/request")
        print("3. Press ENTER again to stop recording")
        print("4. Wait for agent response")
        print("5. Type 'quit' to exit")
        print("="*60)
        
        while True:
            # Check if user wants to quit
            print(f"\n🤖 Ready to chat with {self.current_persona}")
            choice = input("Press ENTER to speak, or type 'quit' to exit: ").strip().lower()
            
            if choice == 'quit':
                print("👋 Goodbye!")
                break
            
            # Process voice input
            text = await self.process_voice_input()
            
            if text:
                # Talk to agent
                await self.talk_to_agent(text)
            
            print("-" * 60)

async def main():
    """Main function."""
    print("🤖 AI AGENT VOICE CONVERSATION")
    print("==============================")
    print("Talk directly to AI agents using your voice!")
    print("")
    
    # Initialize chat system
    chat = VoiceAgentChat()
    await chat.initialize()
    
    # Start conversation
    await chat.conversation_loop()

if __name__ == "__main__":
    asyncio.run(main())
