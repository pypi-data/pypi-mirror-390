#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from talklabs_stt import STTClient

load_dotenv()
client = STTClient(api_key=os.getenv("TALKLABS_STT_API_KEY")) # type: ignore

print("📋 Modelos disponíveis:\n")
models = client.list_models()
for model in models.get("models", []):
    print(f"  - {model.get('name', 'N/A')}")
