#!/usr/bin/env python3
"""
Exemplo - WebSocket Streaming
"""
import os
import asyncio
from dotenv import load_dotenv
from talklabs_stt import STTClient

load_dotenv()

API_KEY = os.getenv("TALKLABS_STT_API_KEY")
AUDIO_FILE = "/home/TALKLABS/STT/teste_base_bookplay.wav"

async def main():
    client = STTClient(api_key=API_KEY)
    
    print(f"🎤 Streaming: {AUDIO_FILE}\n")
    
    def on_transcript(data):
        transcript = data["channel"]["alternatives"][0]["transcript"]
        is_final = data["is_final"]
        
        if is_final:
            print(f"✅ FINAL: {transcript}")
        else:
            print(f"⏳ Interim: {transcript}")
    
    await client.transcribe_stream(
        AUDIO_FILE,
        interim_results=True,
        on_transcript=on_transcript
    )
    
    print("\n🎉 Streaming finalizado!")

if __name__ == "__main__":
    asyncio.run(main())
