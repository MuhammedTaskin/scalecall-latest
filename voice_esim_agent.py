#!/usr/bin/env python3
"""
VOICE E-SIM CALL CENTER AGENT
Pure tool-calling e-SIM agent with voice conversation.
NO human-like responses - only system tool calls and structured responses.
"""
import asyncio
import pyaudio
import base64
import sys
import threading
import json
from typing import Dict, List, Any, Optional

# Add backend to path
sys.path.insert(0, 'backend')

from backend.stt_service import STTService
from backend.esim_tool_agent import ESIMToolAgent

class VoiceESIMAgent:
    def __init__(self):
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.frames = []
        self.is_recording = False
        self.stream = None
        self.p = None
        
        # Initialize services
        self.stt = None
        self.agent = None
        self.conversation_state = "GREETING"
        self.current_customer_id = None
        
    async def initialize(self):
        """Initialize STT and e-SIM agent."""
        print("🏢 INITIALIZING E-SIM CALL CENTER SYSTEM...")
        print("="*50)
        
        # Initialize STT
        self.stt = STTService()
        await self.stt.initialize()
        print("✅ Speech Recognition: ONLINE")
        
        # Initialize e-SIM agent
        self.agent = ESIMToolAgent()
        print("✅ E-SIM Tool Agent: ONLINE")
        
        print("✅ CALL CENTER SYSTEM: READY")
        print("="*50)
        
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
        
        print("🔴 RECORDING IN PROGRESS...")
        
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
                print(f"❌ RECORDING_ERROR: {e}")
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
        
        print("⏹️ RECORDING STOPPED")
        
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
        print("\n📞 WAITING FOR CUSTOMER INPUT...")
        print("Press ENTER to start speaking, then ENTER again to stop")
        input()  # Wait for ENTER
        
        # Start recording
        self.start_recording()
        
        # Wait for user to press ENTER again
        input()  # This blocks until ENTER is pressed
        
        # Stop recording
        audio_data = self.stop_recording()
        
        if len(audio_data) < 1000:  # Too short
            print("❌ AUDIO_TOO_SHORT: Please speak longer")
            return None
        
        print("🔄 PROCESSING_SPEECH...")
        
        # Convert to chunks and transcribe
        chunks = self.audio_to_base64_chunks(audio_data)
        transcript = await self.stt.transcribe_audio(chunks)
        
        if transcript:
            print(f"📝 CUSTOMER_INPUT: '{transcript}'")
            return transcript
        else:
            print("❌ SPEECH_NOT_RECOGNIZED: Please try again")
            return None

    def parse_customer_intent(self, text: str) -> Dict[str, Any]:
        """Parse customer intent and extract information."""
        text_lower = text.lower()
        
        # Extract phone numbers or customer IDs
        import re
        phone_pattern = r'(\+90\s?5\d{2}\s?\d{3}\s?\d{2}\s?\d{2}|\d{6})'
        phone_match = re.search(phone_pattern, text)
        
        intent = {
            "action": "unknown",
            "parameters": {},
            "customer_identifier": None,
            "is_greeting": False,
            "needs_response": False
        }
        
        if phone_match:
            intent["customer_identifier"] = phone_match.group(1)
        
        # Check for greetings and general conversation
        greeting_words = ["merhaba", "selam", "iyi günler", "nasılsın", "nasıl", "kimsin", "adın", "ne yapıyorsun"]
        if any(word in text_lower for word in greeting_words):
            intent["is_greeting"] = True
            intent["needs_response"] = True
            intent["action"] = "greeting"
        
        # Intent recognition
        if any(word in text_lower for word in ["bakiye", "balance", "para", "hesap"]):
            intent["action"] = "check_balance"
        elif any(word in text_lower for word in ["aktif", "activate", "aç", "başlat"]):
            intent["action"] = "activate_esim"
        elif any(word in text_lower for word in ["kapat", "suspend", "durdur", "iptal"]):
            intent["action"] = "suspend_esim"
        elif any(word in text_lower for word in ["durum", "status", "kontrol", "esim"]):
            intent["action"] = "check_status"
        elif any(word in text_lower for word in ["şikayet", "complaint", "problem", "sorun"]):
            intent["action"] = "complaint"
        elif any(word in text_lower for word in ["yükle", "add", "para ekle", "ödeme"]):
            intent["action"] = "add_balance"
            # Try to extract amount
            amount_match = re.search(r'(\d+)', text)
            if amount_match:
                intent["parameters"]["amount"] = float(amount_match.group(1))
        elif any(word in text_lower for word in ["müşteri", "customer", "hesap", "bilgi"]):
            intent["action"] = "lookup_customer"
        elif any(word in text_lower for word in ["yardım", "help", "destek", "nasıl"]):
            intent["action"] = "help"
            intent["needs_response"] = True
        
        return intent

    def get_turkish_response(self, intent: Dict[str, Any], text: str) -> str:
        """Generate Turkish responses for customer interactions."""
        action = intent["action"]
        
        if action == "greeting":
            if "nasılsın" in text.lower() or "nasıl" in text.lower():
                return "Merhaba! Ben e-SIM call center otomatik sistemiyim. Size nasıl yardımcı olabilirim?"
            elif "kimsin" in text.lower() or "adın" in text.lower():
                return "Ben e-SIM call center otomatik asistanıyım. e-SIM işlemlerinizde size yardımcı oluyorum."
            else:
                return "Merhaba! e-SIM call center'a hoş geldiniz. Size nasıl yardımcı olabilirim?"
        
        elif action == "help":
            return "Size şu konularda yardımcı olabilirim: Bakiye sorgulama, e-SIM durumu kontrol etme, e-SIM aktifleştirme/kapatma, bakiye yükleme, şikayet oluşturma. Müşteri numaranızı söylerseniz işlem yapabilirim."
        
        elif action == "unknown":
            return "Anlayamadım. Lütfen müşteri numaranızı söyleyip ne yapmak istediğinizi belirtin. Örneğin: 'Müşteri 123456, bakiye kontrol et' veya 'Telefon +905551234567, e-SIM durumu'"
        
        return None

    async def execute_customer_request(self, text: str):
        """Execute customer request using tools."""
        print("\n🔧 PROCESSING_CUSTOMER_REQUEST...")
        
        # Parse intent
        intent = self.parse_customer_intent(text)
        print(f"🎯 DETECTED_INTENT: {intent['action']}")
        
        # Handle greetings and help requests first
        if intent["needs_response"]:
            response = self.get_turkish_response(intent, text)
            if response:
                print(f"\n🤖 SYSTEM_RESPONSE:")
                print(f"💬 {response}")
                return
        
        if intent["customer_identifier"] and not self.current_customer_id:
            # First lookup customer
            print("🔍 EXECUTING_TOOL: lookup_customer")
            result = await self.agent.execute_tool("lookup_customer", {
                "identifier": intent["customer_identifier"]
            })
            
            self.print_tool_result("lookup_customer", result)
            
            if result["status"] == "success":
                self.current_customer_id = result["customer_id"]
                print(f"\n🤖 SYSTEM_RESPONSE:")
                print(f"💬 Müşteri bulundu: {result['customer_data']['name']}. Ne yapmak istiyorsunuz?"
                return
        
        # Execute main action
        if intent["action"] == "check_balance" and self.current_customer_id:
            print("🔍 EXECUTING_TOOL: check_balance")
            result = await self.agent.execute_tool("check_balance", {
                "customer_id": self.current_customer_id
            })
            self.print_tool_result("check_balance", result)
            if result["status"] == "success":
                print(f"\n🤖 SYSTEM_RESPONSE:")
                print(f"💬 Bakiyeniz: {result['balance']} TL")
            
        elif intent["action"] == "check_status" and self.current_customer_id:
            print("🔍 EXECUTING_TOOL: check_esim_status")
            result = await self.agent.execute_tool("check_esim_status", {
                "customer_id": self.current_customer_id
            })
            self.print_tool_result("check_esim_status", result)
            if result["status"] == "success":
                print(f"\n🤖 SYSTEM_RESPONSE:")
                active_count = sum(1 for e in result["esims"] if e["status"] == "active")
                print(f"💬 {result['esim_count']} adet e-SIM'iniz var. {active_count} tanesi aktif.")
            
        elif intent["action"] == "activate_esim" and self.current_customer_id:
            # First get e-SIM list
            status_result = await self.agent.execute_tool("check_esim_status", {
                "customer_id": self.current_customer_id
            })
            
            if status_result["status"] == "success":
                suspended_esims = [e for e in status_result["esims"] if e["status"] == "suspended"]
                if suspended_esims:
                    esim_id = suspended_esims[0]["id"]
                    print(f"🔍 EXECUTING_TOOL: activate_esim ({esim_id})")
                    result = await self.agent.execute_tool("activate_esim", {
                        "esim_id": esim_id,
                        "customer_id": self.current_customer_id
                    })
                    self.print_tool_result("activate_esim", result)
                else:
                    print("ℹ️ SYSTEM_RESPONSE: NO_SUSPENDED_ESIMS_FOUND")
            
        elif intent["action"] == "suspend_esim" and self.current_customer_id:
            # First get e-SIM list
            status_result = await self.agent.execute_tool("check_esim_status", {
                "customer_id": self.current_customer_id
            })
            
            if status_result["status"] == "success":
                active_esims = [e for e in status_result["esims"] if e["status"] == "active"]
                if active_esims:
                    esim_id = active_esims[0]["id"]
                    print(f"🔍 EXECUTING_TOOL: suspend_esim ({esim_id})")
                    result = await self.agent.execute_tool("suspend_esim", {
                        "esim_id": esim_id,
                        "customer_id": self.current_customer_id
                    })
                    self.print_tool_result("suspend_esim", result)
                else:
                    print("ℹ️ SYSTEM_RESPONSE: NO_ACTIVE_ESIMS_FOUND")
            
        elif intent["action"] == "add_balance" and self.current_customer_id:
            amount = intent["parameters"].get("amount", 50.0)  # Default 50 TL
            print(f"🔍 EXECUTING_TOOL: add_balance ({amount} TL)")
            result = await self.agent.execute_tool("add_balance", {
                "customer_id": self.current_customer_id,
                "amount": amount
            })
            self.print_tool_result("add_balance", result)
            
        elif intent["action"] == "complaint" and self.current_customer_id:
            print("🔍 EXECUTING_TOOL: create_support_ticket")
            result = await self.agent.execute_tool("create_support_ticket", {
                "customer_id": self.current_customer_id,
                "issue_type": "complaint",
                "description": text
            })
            self.print_tool_result("create_support_ticket", result)
            
        elif intent["action"] == "lookup_customer" and intent["customer_identifier"]:
            print("🔍 EXECUTING_TOOL: lookup_customer")
            result = await self.agent.execute_tool("lookup_customer", {
                "identifier": intent["customer_identifier"]
            })
            self.print_tool_result("lookup_customer", result)
            
            if result["status"] == "success":
                self.current_customer_id = result["customer_id"]
        
        else:
            # Handle unknown requests with Turkish response
            if intent["action"] == "unknown":
                response = self.get_turkish_response(intent, text)
                print(f"\n🤖 SYSTEM_RESPONSE:")
                print(f"💬 {response}")
            else:
                print("❓ UNKNOWN_REQUEST: Transferring to human agent")
                result = await self.agent.execute_tool("transfer_to_human", {
                    "reason": "Unrecognized customer request",
                    "customer_id": self.current_customer_id
                })
                self.print_tool_result("transfer_to_human", result)

    def print_tool_result(self, tool_name: str, result: Dict[str, Any]):
        """Print structured tool result."""
        print(f"\n📊 TOOL_RESULT: {tool_name.upper()}")
        print("=" * 40)
        
        if result["status"] == "success":
            print(f"✅ STATUS: SUCCESS")
            print(f"📝 MESSAGE: {result['message']}")
            
            # Print specific data based on tool
            if tool_name == "lookup_customer":
                customer = result["customer_data"]
                print(f"👤 CUSTOMER: {customer['name']}")
                print(f"📱 PHONE: {customer['phone']}")
                print(f"💰 BALANCE: {customer['balance']} TL")
                
            elif tool_name == "check_esim_status":
                print(f"📱 ESIM_COUNT: {result['esim_count']}")
                for esim in result["esims"]:
                    print(f"   📡 {esim['id']}: {esim['status']} - {esim['plan']}")
                    
            elif tool_name == "check_balance":
                print(f"💰 BALANCE: {result['balance']} {result['currency']}")
                
            elif tool_name == "add_balance":
                print(f"➕ ADDED: {result['amount_added']} TL")
                print(f"💰 NEW_BALANCE: {result['new_balance']} TL")
                
            elif tool_name == "create_support_ticket":
                print(f"🎫 TICKET_ID: {result['ticket_id']}")
                
        else:
            print(f"❌ STATUS: ERROR")
            print(f"📝 MESSAGE: {result['message']}")
        
        print("=" * 40)

    async def conversation_loop(self):
        """Main conversation loop."""
        print("\n" + "="*60)
        print("📞 E-SIM CALL CENTER - AUTOMATED SYSTEM")
        print("="*60)
        print("🤖 SYSTEM: Pure tool-calling agent")
        print("🎯 SERVICES: E-SIM management, billing, support")
        print("🗣️ INPUT: Voice commands")
        print("📊 OUTPUT: Structured tool responses")
        print("="*60)
        print("\nSUPPORTED COMMANDS:")
        print("• Customer lookup: 'Müşteri 123456' or 'Telefon +905551234567'")
        print("• Balance check: 'Bakiye kontrol et'")
        print("• E-SIM status: 'E-SIM durumu'") 
        print("• Activate: 'E-SIM aktif et'")
        print("• Suspend: 'E-SIM kapat'")
        print("• Add balance: 'Bakiye yükle 100'")
        print("• Complaint: 'Şikayet oluştur'")
        print("="*60)
        
        while True:
            # Check if user wants to quit
            print(f"\n🤖 CALL CENTER READY")
            if self.current_customer_id:
                print(f"👤 ACTIVE_CUSTOMER: {self.current_customer_id}")
            
            choice = input("Press ENTER to take customer call, or type 'quit': ").strip().lower()
            
            if choice == 'quit':
                print("🔚 CALL CENTER SYSTEM SHUTDOWN")
                break
            
            # Process voice input
            text = await self.process_voice_input()
            
            if text:
                # Execute customer request
                await self.execute_customer_request(text)
            
            print("-" * 60)

async def main():
    """Main function."""
    print("📞 E-SIM CALL CENTER VOICE SYSTEM")
    print("==================================")
    print("Automated e-SIM management with voice input")
    print("Pure tool-calling agent - no human-like responses")
    print("")
    
    # Initialize system
    agent = VoiceESIMAgent()
    await agent.initialize()
    
    # Start call center
    await agent.conversation_loop()

if __name__ == "__main__":
    asyncio.run(main())
