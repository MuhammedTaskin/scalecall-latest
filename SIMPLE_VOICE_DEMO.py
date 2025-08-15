#!/usr/bin/env python3
"""
TEKNOFEST 2025 - SIMPLE VOICE DEMO
Click button -> Talk -> Get AI response
"""

import tkinter as tk
from tkinter import ttk
import asyncio
import threading
import sounddevice as sd
import numpy as np
import requests
import json
from datetime import datetime

class VoiceDemo:
    def __init__(self):
        self.server_url = "http://localhost:8000"
        self.recording = False
        self.audio_data = None
        
        # Create GUI
        self.root = tk.Tk()
        self.root.title("TEKNOFEST 2025 - Voice Demo")
        self.root.geometry("500x400")
        
        # Status
        self.status = tk.StringVar(value="Ready to record")
        tk.Label(self.root, textvariable=self.status, font=("Arial", 14)).pack(pady=10)
        
        # Record button
        self.record_btn = tk.Button(
            self.root, 
            text="🎤 PRESS TO TALK", 
            font=("Arial", 16),
            bg="red",
            fg="white",
            width=20,
            height=3,
            command=self.toggle_recording
        )
        self.record_btn.pack(pady=20)
        
        # Response area
        tk.Label(self.root, text="AI Response:", font=("Arial", 12)).pack()
        self.response_text = tk.Text(self.root, height=10, width=60)
        self.response_text.pack(pady=10, padx=10)
        
        # Test connection
        self.test_connection()
    
    def test_connection(self):
        try:
            response = requests.get(f"{self.server_url}/health", timeout=3)
            if response.status_code == 200:
                self.status.set("✅ Connected to Gemma 3N")
            else:
                self.status.set("❌ Connection failed")
        except:
            self.status.set("❌ Cannot reach server")
    
    def toggle_recording(self):
        if not self.recording:
            self.start_recording()
    
    def start_recording(self):
        self.recording = True
        self.record_btn.config(text="🔴 RECORDING...", bg="green")
        self.status.set("🎤 Recording for 5 seconds...")
        
        # Record in background thread
        threading.Thread(target=self.record_audio, daemon=True).start()
    
    def record_audio(self):
        # Record 5 seconds of audio
        sample_rate = 16000
        duration = 5
        
        try:
            self.audio_data = sd.rec(
                int(duration * sample_rate), 
                samplerate=sample_rate, 
                channels=1,
                dtype=np.float32
            )
            sd.wait()  # Wait for recording to complete
            
            # Process the audio
            self.root.after(0, self.process_audio)
            
        except Exception as e:
            self.root.after(0, lambda: self.status.set(f"❌ Recording error: {e}"))
            self.root.after(0, self.reset_button)
    
    def process_audio(self):
        self.status.set("🤖 Sending to Gemma 3N...")
        self.record_btn.config(text="🤖 PROCESSING...", bg="blue")
        
        # Process in background thread
        threading.Thread(target=self.send_to_ai, daemon=True).start()
    
    def send_to_ai(self):
        try:
            # Detect emotion
            audio_array = self.audio_data.flatten()
            emotion = self.detect_emotion(audio_array)
            
            # Send to Gemma 3N
            payload = {
                "text": "",  # Pure audio input
                "emotion": emotion,
                "audio_data": audio_array.tolist()
            }
            
            response = requests.post(
                f"{self.server_url}/predict",
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                self.root.after(0, lambda: self.show_response(result, emotion))
            else:
                self.root.after(0, lambda: self.status.set(f"❌ Server error: {response.status_code}"))
                
        except Exception as e:
            self.root.after(0, lambda: self.status.set(f"❌ Error: {e}"))
        
        self.root.after(0, self.reset_button)
    
    def detect_emotion(self, audio_data):
        """Simple emotion detection"""
        if len(audio_data) == 0:
            return "neutral"
        
        energy = np.mean(np.abs(audio_data))
        variance = np.var(audio_data)
        
        if energy > 0.05 and variance > 0.01:
            return "angry"
        elif energy < 0.01:
            return "sad"
        elif variance > 0.02:
            return "confused"
        elif energy > 0.02 and variance < 0.005:
            return "happy"
        else:
            return "neutral"
    
    def show_response(self, result, emotion):
        response_text = result.get('generated_text', 'No response')
        tools = result.get('tools_extracted', [])
        
        # Display result
        output = f"🎭 Emotion: {emotion}\n"
        output += f"🤖 Response: {response_text}\n"
        output += f"🔧 Tools: {', '.join(tools) if tools else 'None'}\n"
        output += f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}\n"
        output += "-" * 50 + "\n"
        
        self.response_text.insert(tk.END, output)
        self.response_text.see(tk.END)
        
        self.status.set("✅ Response received!")
    
    def reset_button(self):
        self.recording = False
        self.record_btn.config(text="🎤 PRESS TO TALK", bg="red")
        self.status.set("Ready to record")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    try:
        demo = VoiceDemo()
        demo.run()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure sounddevice is installed: pip install sounddevice")