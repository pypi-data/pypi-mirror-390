"""
Yemot Speech - Speech-to-Text and Text-to-Speech library for Yemot HaMashiach systems
"""

from .stt import STT, transcribe
from .tts import TTS, synthesize, speak
from .base import STTProvider, TTSProvider

__version__ = "0.1.0"
__all__ = ["STT", "TTS", "transcribe", "synthesize", "speak", "STTProvider", "TTSProvider"]


def main() -> None:
    print("Hello from yemot-speech!")
