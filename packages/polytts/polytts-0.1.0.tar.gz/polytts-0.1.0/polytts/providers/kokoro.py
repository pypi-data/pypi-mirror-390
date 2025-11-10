import numpy as np
from typing import Generator, Any

from ..base import TTSProvider
from ..audio import AudioData


class KokoroTTS(TTSProvider):
    SAMPLE_RATE = 24000

    def __init__(self, lang_code: str = "a", device: str | None = None):
        """
        Initialize Kokoro TTS provider.

        Args:
            lang_code: Language code for G2P processing. Options:
                "a" or "en-us": American English
                "b" or "en-gb": British English
                "e" or "es": Spanish (espeak-ng)
                "f" or "fr-fr": French (espeak-ng)
                "h" or "hi": Hindi (espeak-ng)
                "i" or "it": Italian (espeak-ng)
                "j" or "ja": Japanese (requires: pip install misaki[ja])
                "p" or "pt-br": Brazilian Portuguese (espeak-ng)
                "z" or "zh": Mandarin Chinese
            
            device: Device to run model on. Options: "cuda", "cpu", or
                None for auto-detect
        """
        try:
            from kokoro import KPipeline
        except ImportError:
            raise ImportError(
                "Kokoro is not installed. Install with: pip install polytts[kokoro]"
            )

        self.client = KPipeline(lang_code=lang_code, device=device)

    def get_sample_rate(self) -> int:
        return self.SAMPLE_RATE

    def run(
        self,
        text: str,
        voice: str = "af_heart",
        **kwargs: Any
    ) -> AudioData:
        """
        Generate speech from text using Kokoro TTS.

        Args:
            text: The text to convert to speech.
                Long texts are automatically chunked.
            
            voice: Voice identifier to use. Common voices:
                "af_heart", "af_bella", "af_jessica", "af_sarah", "am_adam", "am_michael"
            
            **kwargs: Additional parameters. Common parameters:
                speed: Speech speed multiplier. Default: 1.0
                
                split_pattern: Regex pattern for text splitting. Default: r'\\n+'

            For complete API reference: https://github.com/hexgrad/kokoro

        Returns:
            AudioData object with generated audio

        Example:
            >>> tts = KokoroTTS()
            >>> audio = tts.run("Hello world")
        """
        response = self.client(
            text=text,
            voice=voice,
            **kwargs
        )

        audio_chunks = [audio.numpy() for _, _, audio in response]

        audio = (
            np.concatenate(audio_chunks)
            if audio_chunks
            else np.array([], dtype=np.float32)
        )

        return AudioData(audio, self.get_sample_rate(), "raw")

    def stream(
        self,
        text: str,
        voice: str = "af_heart",
        **kwargs: Any
    ) -> Generator[AudioData, None, None]:
        """
        Stream speech generation from text using Kokoro TTS.

        Args:
            text: The text to convert to speech.
                Long texts are automatically chunked.
            
            voice: Voice identifier to use. Common voices:
                "af_heart", "af_bella", "af_jessica", "af_sarah", "am_adam", "am_michael"
            
            **kwargs: Additional parameters. Common parameters:
                speed: Speech speed multiplier. Default: 1.0
                
                split_pattern: Regex pattern for text splitting. Default: r'\\n+'

            For complete API reference: https://github.com/hexgrad/kokoro

        Returns:
            AudioData object with generated audio

        Example:
            >>> tts = KokoroTTS()
            >>> for chunk in tts.stream("Hello world"):
            ...     print(chunk)
        """
        response = self.client(
            text=text,
            voice=voice,
            **kwargs
        )

        for _, _, audio in response:
            yield AudioData(audio.numpy(), self.get_sample_rate(), "raw")
