"""
TalkLabs SDK v2.1.3 - Minimalista
----------------------------------
SDK focado em streaming com sessões persistentes.

Uso:
    from talklabs import TalkLabsClient

    client = TalkLabsClient(api_key="tlk_live_xxxxx")

    # One-shot
    async for chunk in client.stream_text("Olá!", voice="adam_rocha"):
        play(chunk)

    # Persistente
    session = await client.create_session(voice="adam_rocha")
    async for chunk in session.stream_text("Texto"):
        play(chunk)
"""

from .tts import (
    TalkLabsClient,
    VoiceSettings,
    StreamingSession,
)

__version__ = "2.1.3"
__all__ = [
    "TalkLabsClient",
    "VoiceSettings",
    "StreamingSession",
]
