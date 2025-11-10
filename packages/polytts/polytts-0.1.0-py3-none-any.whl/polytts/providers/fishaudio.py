import os
from typing import Generator, Any

from ..base import TTSProvider
from ..audio import AudioData
from ..constants import EncodedBytesFormat

class FishAudioTTS(TTSProvider):
    SAMPLE_RATE = 44100

    def __init__(self, api_key: str | None = None):
        """
        Initialize Fish Audio TTS provider.

        Args:
            api_key: Fish Audio API key. If None, will try to get from
            FISHAUDIO_API_KEY environment variable.
        """
        try:
            from fish_audio_sdk import Session
        except ImportError:
            raise ImportError(
                "FishAudio is not installed. Install with: "
                "pip install polytts[fishaudio]"
            )

        api_key = api_key or os.getenv("FISHAUDIO_API_KEY")
        if not api_key:
            raise ValueError(
                "Fish Audio API key is required. Provide it via the api_key parameter "
                "or set the FISHAUDIO_API_KEY environment variable."
            )
        self.client = Session(apikey=api_key)

    def get_sample_rate(self) -> int:
        return self.SAMPLE_RATE

    def run(
        self,
        text: str,
        reference_id: str | None = None,
        references: list | None = None,
        response_format: EncodedBytesFormat = "pcm",
        **kwargs: Any
    ) -> AudioData:
        """
        Generate speech from text using Fish Audio TTS.

        Args:
            text: The text to convert to speech
            
            reference_id: Reference voice ID for voice cloning
            
            references: List of ReferenceAudio objects for custom voice cloning
            
            response_format: Output audio format: pcm, mp3, wav
            
            **kwargs: Additional parameters
                speed: Speech speed multiplier. Default: 1.0

                volume: Speech volume. Default: 0.0

            For complete API reference: https://docs.fish.audio/api-reference/endpoint/openapi-v1/text-to-speech

        Returns:
            AudioData object containing the generated audio

        Example:
            >>> tts = FishAudioTTS()
            >>> audio = tts.run("Hello world")
        """
        from fish_audio_sdk import TTSRequest, Prosody

        if references is None:
            references = []

        prosody = Prosody(
            speed=kwargs.pop("speed", 1.0),
            volume=kwargs.pop("volume", 0.0)
        )

        sample_rate = self.get_sample_rate()
        response = self.client.tts(TTSRequest(
            text=text,
            format=response_format,
            reference_id=reference_id,
            references=references,
            prosody=prosody,
            **kwargs
        ))

        data = b"".join(response)
        return AudioData(data, sample_rate, response_format)

    def stream(
        self,
        text: str,
        reference_id: str | None = None,
        references: list | None = None,
        response_format: EncodedBytesFormat = "pcm",
        **kwargs: Any
    ) -> Generator[AudioData, None, None]:
        """
        Stream speech generation from text using Fish Audio TTS

        Args:
            text: The text to convert to speech
            
            reference_id: Reference voice ID for voice cloning
            
            references: List of ReferenceAudio objects for custom voice cloning
            
            response_format: Output audio format: pcm, mp3, wav
            
            **kwargs: Additional parameters
                speed: Speech speed multiplier. Default: 1.0

                volume: Speech volume. Default: 0.0

            For complete API reference: https://docs.fish.audio/api-reference/endpoint/openapi-v1/text-to-speech

        Yields:
            AudioData objects containing chunks of generated audio

        Example:
            >>> tts = FishAudioTTS()
            >>> for chunk in tts.stream("Hello world"):
            ...     print(chunk)
        """
        from fish_audio_sdk import TTSRequest, Prosody

        if references is None:
            references = []

        prosody = Prosody(
            speed=kwargs.pop("speed", 1.0),
            volume=kwargs.pop("volume", 0.0)
        )

        sample_rate = self.get_sample_rate()
        response = self.client.tts(TTSRequest(
            text=text,
            format=response_format,
            sample_rate=sample_rate,
            reference_id=reference_id,
            references=references,
            prosody=prosody,
            **kwargs
        ))

        buffer = b""
        for data in response:
            combined = buffer + data

            if len(combined) % 2 == 1:
                buffer = combined[-1:]
                combined = combined[:-1]
            else:
                buffer = b""

            if len(combined) > 0:
                yield AudioData(combined, sample_rate, response_format)

        if buffer:
            buffer += b"\x00"
            yield AudioData(buffer, sample_rate, response_format)
