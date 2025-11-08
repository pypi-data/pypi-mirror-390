#!/usr/bin/env python3
"""
Exemplo Simples - Transcrição REST API
"""
import os
from dotenv import load_dotenv
from talklabs_stt import STTClient

load_dotenv()

# Configuração
API_KEY = os.getenv("TALKLABS_STT_API_KEY")
AUDIO_FILE = "/home/TALKLABS/STT/teste_base_bookplay.wav"

def main():
    # Cria cliente
    client = STTClient(api_key=API_KEY)
    
    # Transcreve
    print(f"📂 Transcrevendo: {AUDIO_FILE}")
    result = client.transcribe_file(
        AUDIO_FILE,
        model="large-v3",
        language="pt"
    )
    
    # Extrai resultado
    transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]
    confidence = result["results"]["channels"][0]["alternatives"][0]["confidence"]
    duration = result["metadata"]["duration"]
    
    print(f"\n✅ Transcrição completa!")
    print(f"Duração: {duration:.2f}s")
    print(f"Confiança: {confidence:.2%}")
    print(f"\nTexto: {transcript}")

if __name__ == "__main__":
    main()
