"""
PolyTTS - A unified interface for multiple TTS providers with seamless hotswapping.

Provides a consistent API across cloud-based and local TTS models.
"""

from .audio import AudioData
from .constants import EncodedBytesFormat, AudioFormat, DType
from .providers import *

__version__ = "0.1.0"

__all__ = [
    "AudioData",
    "EncodedBytesFormat",
    "AudioFormat",
    "DType",
    "OpenAITTS",
    "ElevenLabsTTS",
    "FishAudioTTS",
    "KokoroTTS",
    "GPTSovitsTTS",
]