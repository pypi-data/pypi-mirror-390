"""
TalkLabs STT SDK - Speech-to-Text API Client

Transcrição de áudio via API TalkLabs, compatível com Deepgram.

Usage:
    from talklabs_stt import STTClient, TranscriptionOptions

    # Cliente básico
    client = STTClient(api_key="tlk_live_xxxxx")

    # REST API
    result = client.transcribe_file("audio.wav")
    print(result["results"]["channels"][0]["alternatives"][0]["transcript"])

    # WebSocket Streaming
    async def main():
        await client.transcribe_stream(
            "audio.wav",
            on_transcript=lambda data: print(data)
        )

    asyncio.run(main())

Author: Francisco Lima <franciscorllima@gmail.com>
License: MIT
Repository: https://github.com/talklabs/talklabs-stt
"""

__version__ = "1.0.3"
__author__ = "Francisco Lima"
__email__ = "franciscorllima@gmail.com"
__license__ = "MIT"

from .stt import STTClient, TranscriptionOptions

__all__ = ["STTClient", "TranscriptionOptions"]
