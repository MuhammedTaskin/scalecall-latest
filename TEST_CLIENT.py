#!/usr/bin/env python3
"""
🧪 Test Client for TEKNOFEST 2025 Pipeline
Simple client to test the complete emotion-aware system
"""

import asyncio
import websockets
import json
from typing import Dict
import random

# Test scenarios with different emotions
TEST_SCENARIOS = [
    {
        "text": "3 gündür arıyorum, kimse yardımcı olmuyor! Faturamı öğrenmek istiyorum!",
        "emotion": "angry",
        "expected_agent": "BillingAgent"
    },
    {
        "text": "İnternet paketimi değiştirmek istiyorum ama hangisi uygun bilmiyorum",
        "emotion": "confused",
        "expected_agent": "PlanAgent"
    },
    {
        "text": "Telefon numaramı taşımak istiyorum, bilgilerim kaybolur mu?",
        "emotion": "worried",
        "expected_agent": "TechAgent"
    },
    {
        "text": "Yeni kampanyalarınız hakkında bilgi alabilir miyim?",
        "emotion": "neutral",
        "expected_agent": "PlanAgent"
    },
    {
        "text": "Teşekkür ederim, çok yardımcı oldunuz!",
        "emotion": "happy",
        "expected_agent": "FAQAgent"
    }
]

class TestClient:
    """Test client for WebSocket communication"""
    
    def __init__(self, url: str = "ws://localhost:8000/ws/test_client"):
        self.url = url
        self.websocket = None
    
    async def connect(self):
        """Connect to WebSocket server"""
        print("🔌 Connecting to server...")
        self.websocket = await websockets.connect(self.url)
        
        # Receive connection message
        response = await self.websocket.recv()
        data = json.loads(response)
        print(f"✅ Connected: {data.get('message')}")
        return True
    
    async def send_text(self, text: str):
        """Send text message"""
        message = {
            "type": "text",
            "text": text
        }
        
        print(f"\n📤 Sending: {text}")
        await self.websocket.send(json.dumps(message))
    
    async def send_audio(self, audio_path: str):
        """Send audio message"""
        message = {
            "type": "audio",
            "audio": audio_path
        }
        
        print(f"\n🎤 Sending audio: {audio_path}")
        await self.websocket.send(json.dumps(message))
    
    async def send_command(self, command: str):
        """Send command"""
        message = {
            "type": "command",
            "command": command
        }
        
        await self.websocket.send(json.dumps(message))
    
    async def receive_responses(self):
        """Receive and display responses"""
        full_response = ""
        emotion_detected = None
        agent_used = None
        tools_used = []
        
        while True:
            try:
                response = await asyncio.wait_for(
                    self.websocket.recv(),
                    timeout=5.0
                )
                data = json.loads(response)
                
                # Process different message types
                if data["type"] == "emotion_analysis":
                    emotion_detected = data["emotion"]
                    confidence = data["confidence"]
                    print(f"   🎭 Emotion: {emotion_detected} ({confidence:.0%})")
                
                elif data["type"] == "profile":
                    profile = data["profile_type"]
                    priority = data["priority"]
                    print(f"   👤 Profile: {profile} (Priority: {priority})")
                
                elif data["type"] == "agent":
                    agent_used = data["name"]
                    print(f"   🤖 Agent: {agent_used}")
                
                elif data["type"] == "response_chunk":
                    chunk = data["text"]
                    full_response += chunk + " "
                    print(f"   💬 {chunk}", end=" ")
                    
                    if data.get("is_final"):
                        print()  # New line after final chunk
                
                elif data["type"] == "tools_used":
                    tools_used = data["tools"]
                    print(f"   🔧 Tools: {', '.join(tools_used)}")
                
                elif data["type"] == "audio_response":
                    audio_url = data["audio_url"]
                    tone = data["emotion_tone"]
                    print(f"   🔊 Audio generated with {tone} tone")
                
                elif data["type"] == "transcription":
                    text = data["text"]
                    print(f"   📝 Transcribed: {text}")
                
            except asyncio.TimeoutError:
                # No more messages
                break
            except Exception as e:
                print(f"   ⚠️ Error: {e}")
                break
        
        return {
            "response": full_response.strip(),
            "emotion": emotion_detected,
            "agent": agent_used,
            "tools": tools_used
        }
    
    async def test_scenario(self, scenario: Dict):
        """Test a single scenario"""
        print("\n" + "="*60)
        print(f"🧪 TEST SCENARIO")
        print("="*60)
        print(f"Expected emotion: {scenario['emotion']}")
        print(f"Expected agent: {scenario['expected_agent']}")
        
        # Send text
        await self.send_text(scenario["text"])
        
        # Receive responses
        result = await self.receive_responses()
        
        # Validate results
        print("\n📊 RESULTS:")
        print(f"   Detected emotion: {result['emotion']} ✅" if result['emotion'] == scenario['emotion'] else f"   Detected emotion: {result['emotion']} ❌ (expected {scenario['emotion']})")
        print(f"   Used agent: {result['agent']} ✅" if result['agent'] == scenario['expected_agent'] else f"   Used agent: {result['agent']} ❌ (expected {scenario['expected_agent']})")
        
        return result
    
    async def run_all_tests(self):
        """Run all test scenarios"""
        print("""
╔══════════════════════════════════════════════════════╗
║  🧪 TEKNOFEST 2025 - PIPELINE TEST CLIENT 🧪        ║
╠══════════════════════════════════════════════════════╣
║  Testing emotion-aware responses across scenarios    ║
╚══════════════════════════════════════════════════════╝
        """)
        
        # Connect to server
        await self.connect()
        
        # Get initial stats
        await self.send_command("get_stats")
        await asyncio.sleep(1)
        
        # Run test scenarios
        results = []
        for scenario in TEST_SCENARIOS:
            result = await self.test_scenario(scenario)
            results.append(result)
            await asyncio.sleep(2)  # Delay between tests
        
        # Print summary
        print("\n" + "="*60)
        print("📈 TEST SUMMARY")
        print("="*60)
        
        correct_emotions = sum(1 for i, r in enumerate(results) 
                              if r['emotion'] == TEST_SCENARIOS[i]['emotion'])
        correct_agents = sum(1 for i, r in enumerate(results)
                           if r['agent'] == TEST_SCENARIOS[i]['expected_agent'])
        
        print(f"Emotion detection accuracy: {correct_emotions}/{len(TEST_SCENARIOS)} ({correct_emotions/len(TEST_SCENARIOS)*100:.0f}%)")
        print(f"Agent routing accuracy: {correct_agents}/{len(TEST_SCENARIOS)} ({correct_agents/len(TEST_SCENARIOS)*100:.0f}%)")
        
        # Close connection
        await self.websocket.close()
        print("\n✅ Tests completed!")
    
    async def interactive_mode(self):
        """Interactive testing mode"""
        print("""
╔══════════════════════════════════════════════════════╗
║  💬 INTERACTIVE MODE - TEKNOFEST 2025 AI            ║
╠══════════════════════════════════════════════════════╣
║  Type your messages to test the emotion-aware AI     ║
║  Commands:                                           ║
║    /quit - Exit                                      ║
║    /reset - Reset conversation                       ║
║    /stats - Get statistics                           ║
╚══════════════════════════════════════════════════════╝
        """)
        
        # Connect
        await self.connect()
        
        while True:
            # Get user input
            user_input = input("\n👤 You: ")
            
            if user_input == "/quit":
                break
            elif user_input == "/reset":
                await self.send_command("reset")
                print("🔄 Conversation reset")
                continue
            elif user_input == "/stats":
                await self.send_command("get_stats")
                await asyncio.sleep(1)
                continue
            
            # Send message
            await self.send_text(user_input)
            
            # Get response
            print("\n🤖 AI Response:")
            await self.receive_responses()
        
        # Close connection
        await self.websocket.close()
        print("\n👋 Goodbye!")

async def main():
    """Main function"""
    
    client = TestClient()
    
    # Ask user for mode
    print("""
╔══════════════════════════════════════════════════════╗
║  🚀 TEKNOFEST 2025 TEST CLIENT                      ║
╠══════════════════════════════════════════════════════╣
║  Select mode:                                        ║
║  1. Run automated tests                              ║
║  2. Interactive chat                                 ║
║  3. Test audio input (mock)                          ║
╚══════════════════════════════════════════════════════╝
    """)
    
    choice = input("Enter choice (1-3): ")
    
    if choice == "1":
        await client.run_all_tests()
    elif choice == "2":
        await client.interactive_mode()
    elif choice == "3":
        # Test audio
        await client.connect()
        print("\n🎤 Testing audio input...")
        await client.send_audio("test_audio.wav")
        await client.receive_responses()
        await client.websocket.close()
    else:
        print("Invalid choice")

if __name__ == "__main__":
    asyncio.run(main())