#!/usr/bin/env python3
"""
Simple WebSocket client that streams microphone audio to Nubank Xpeer Agent.
Requires: pip install websockets pyaudio
"""

import asyncio
import base64
import json
import pyaudio
import websockets
import sys
import ssl

# WebSocket endpoint
WS_URL = "wss://nubank-xpeer-agent-713488125678.us-central1.run.app/ws"

# Audio settings (matching what the server expects: PCM 16-bit)
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16


class MicrophoneClient:
    def __init__(self, session_id: str = "mac-client-001"):
        self.session_id = session_id
        self.ws_url = f"{WS_URL}/{session_id}?is_audio=true"
        self.running = False
        self.audio = None
        self.stream = None

    async def connect(self):
        print(f"🔗 Connecting to: {self.ws_url}")
        
        # SSL context (bypasses certificate verification - for testing only!)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        async with websockets.connect(self.ws_url, ssl=ssl_context) as ws:
            print("✅ Connected! Speak into your microphone...")
            print("Press Ctrl+C to stop\n")
            
            self.running = True
            
            # Start tasks
            receive_task = asyncio.create_task(self.receive_messages(ws))
            send_task = asyncio.create_task(self.send_audio(ws))
            
            try:
                await asyncio.gather(receive_task, send_task)
            except asyncio.CancelledError:
                pass
            finally:
                self.running = False

    async def send_audio(self, ws):
        """Capture microphone and send audio chunks"""
        self.audio = pyaudio.PyAudio()
        
        # List available input devices
        print("🎤 Available input devices:")
        for i in range(self.audio.get_device_count()):
            dev = self.audio.get_device_info_by_index(i)
            if dev['maxInputChannels'] > 0:
                print(f"   [{i}] {dev['name']}")
        print()
        
        try:
            self.stream = self.audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=SAMPLE_RATE,
                input=True,
                frames_per_buffer=CHUNK_SIZE
            )
            
            while self.running:
                # Read audio chunk
                data = self.stream.read(CHUNK_SIZE, exception_on_overflow=False)
                
                # Encode and send
                message = {
                    "mime_type": "audio/pcm",
                    "data": base64.b64encode(data).decode("ascii"),
                    "role": "user"
                }
                await ws.send(json.dumps(message))
                
                # Small delay to prevent overwhelming
                await asyncio.sleep(0.01)
                
        except Exception as e:
            print(f"❌ Audio error: {e}")
        finally:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            if self.audio:
                self.audio.terminate()

    async def receive_messages(self, ws):
        """Receive and display messages from server"""
        audio_player = AudioPlayer()
        
        try:
            async for message in ws:
                msg = json.loads(message)
                
                # Handle different message types
                if msg.get("turn_complete"):
                    print("\n--- Turn complete ---\n")
                    
                elif msg.get("type") == "input_transcription":
                    # User's speech transcribed
                    if msg.get("finished"):
                        print(f"🎤 You: {msg['data']}")
                    
                elif msg.get("type") == "output_transcription":
                    # Model's response transcribed
                    if msg.get("finished"):
                        print(f"🤖 Agent: {msg['data']}")
                        
                elif msg.get("mime_type") == "text/plain":
                    # Text response
                    print(f"📝 {msg['data']}", end="", flush=True)
                    
                elif msg.get("mime_type") == "audio/pcm":
                    # Audio response - play it
                    audio_data = base64.b64decode(msg["data"])
                    audio_player.play(audio_data)
                    
                elif msg.get("type") == "tool_use":
                    print(f"\n🔧 Tool: {msg['tool_name']} → {msg.get('tool_args', {})}")
                    
        except websockets.exceptions.ConnectionClosed:
            print("\n🔌 Connection closed")
        except Exception as e:
            print(f"\n❌ Receive error: {e}")


class AudioPlayer:
    """Simple audio player for PCM data"""
    
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=24000,  # Gemini outputs at 24kHz
            output=True
        )
    
    def play(self, data: bytes):
        self.stream.write(data)
    
    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()


async def main():
    session_id = sys.argv[1] if len(sys.argv) > 1 else "mac-client-001"
    client = MicrophoneClient(session_id)
    
    try:
        await client.connect()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Connection error: {e}")


if __name__ == "__main__":
    print("=" * 50)
    print("🎙️  Nubank Xpeer Agent - Microphone Client")
    print("=" * 50)
    print()
    asyncio.run(main())