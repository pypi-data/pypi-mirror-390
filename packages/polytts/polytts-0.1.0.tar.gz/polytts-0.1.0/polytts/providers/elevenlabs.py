import os
from typing import Generator, Any

from ..base import TTSProvider
from ..audio import AudioData

class ElevenLabsTTS(TTSProvider):
    DEFAULT_SAMPLE_RATE = 22050

    def __init__(self, api_key: str | None = None):
        """
        Initialize ElevenLabs TTS provider.

        Args:
            api_key: ElevenLabs API key. If None, will try to get from
            ELEVENLABS_API_KEY environment variable.
        """
        try:
            from elevenlabs.client import ElevenLabs
        except ImportError:
            raise ImportError(
                "ElevenLabs is not installed. Install with: "
                "pip install polytts[elevenlabs]"
            )

        api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            raise ValueError(
                "ElevenLabs API key is required. Provide it via the api_key parameter "
                "or set the ELEVENLABS_API_KEY environment variable."
            )
        self.client = ElevenLabs(api_key=api_key)
        self.current_sample_rate = self.DEFAULT_SAMPLE_RATE

    def get_sample_rate(self) -> int:
        return self.current_sample_rate

    def _parse_output_format(self, output_format: str) -> tuple[str, int]:
        """Parse output format string into format and sample rate."""
        parts = output_format.split("_")
        format_type = parts[0]
        sample_rate = int(parts[1]) if len(parts) > 1 else self.current_sample_rate
        return format_type, sample_rate

    def run(
        self,
        text: str,
        voice_id: str = "JBFqnCBsd6RMkjVDRZzb",
        model_id: str = "eleven_multilingual_v2",
        response_format: str = "pcm_22050",
        **kwargs: Any,
    ) -> AudioData:
        """
        Generate speech from text using ElevenLabs TTS.

        Args:
            text: The text to convert to speech
            
            voice_id: ElevenLabs voice ID
            
            model_id: Model to use. Common options:
                eleven_multilingual_v2: Multilingual, high quality
                eleven_turbo_v2: Faster generation, lower latency
                eleven_monolingual_v1: English only, high quality
            
            response_format: Output format as "codec_samplerate". Examples:
                "pcm_22050", "pcm_44100": Uncompressed PCM audio
                "mp3_22050_32", "mp3_44100_192": MP3 with bitrate
            
            **kwargs: Additional parameters. Common parameters:
                stability: Voice stability and randomness, 0.0-1.0 (default: 0.5).
                
                similarity_boost: Adherence to original voice, 0.0-1.0 (default: 0.75).
                
                use_speaker_boost: Boost similarity to original speaker (default: True).
                
                style: Style exaggeration, 0.0-1.0 (default: 0.0).
                
                speed: Speech speed multiplier (default: 1.0).
                
                optimize_streaming_latency: Reduce latency, 0-4 (higher = faster)
                
                language_code: Force specific language (e.g., "en", "es", "fr")

            For complete API reference: https://elevenlabs.io/docs/api-reference/text-to-speech

        Returns:
            AudioData object containing the generated audio

        Example:
            >>> tts = ElevenLabsTTS()
            >>> audio = tts.run("Hello world")
        """
        from elevenlabs.types.voice_settings import VoiceSettings
        
        voice_settings = VoiceSettings(
            stability=kwargs.pop("stability", 0.5),
            use_speaker_boost=kwargs.pop("use_speaker_boost", True),
            similarity_boost=kwargs.pop("similarity_boost", 0.75),
            style=kwargs.pop("style", 0.0),
            speed=kwargs.pop("speed", 1.0),
        )

        response = self.client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id=model_id,
            output_format=response_format,
            voice_settings=voice_settings,
            **kwargs,
        )

        data = b"".join(response)
        encoded_format, sample_rate = self._parse_output_format(response_format)
        self.current_sample_rate = sample_rate
        return AudioData(data, sample_rate, encoded_format)

    def stream(
        self,
        text: str,
        voice_id: str = "JBFqnCBsd6RMkjVDRZzb",
        model_id: str = "eleven_multilingual_v2",
        response_format: str = "pcm_22050",
        **kwargs: Any,
    ) -> Generator[AudioData, None, None]:
        """
        Stream speech generation from text using ElevenLabs TTS.

        Args:
            text: The text to convert to speech
            
            voice_id: ElevenLabs voice ID
            
            model_id: Model to use. Common options:
                eleven_multilingual_v2: Multilingual, high quality
                eleven_turbo_v2: Faster generation, lower latency
                eleven_monolingual_v1: English only, high quality
            
            response_format: Output format as "codec_samplerate". Examples:
                "pcm_22050", "pcm_44100": Uncompressed PCM audio
                "mp3_22050_32", "mp3_44100_192": MP3 with bitrate
            
            **kwargs: Additional parameters. Common parameters:
                stability: Voice stability and randomness, 0.0-1.0 (default: 0.5).
                
                similarity_boost: Adherence to original voice, 0.0-1.0 (default: 0.75).
                
                use_speaker_boost: Boost similarity to original speaker (default: True).
                
                style: Style exaggeration, 0.0-1.0 (default: 0.0).
                
                speed: Speech speed multiplier (default: 1.0).
                
                optimize_streaming_latency: Reduce latency, 0-4 (higher = faster)
                
                language_code: Force specific language (e.g., "en", "es", "fr")

            For complete API reference: https://elevenlabs.io/docs/api-reference/text-to-speech

        Yields:
            AudioData objects containing chunks of generated audio

        Example:
            >>> tts = ElevenLabsTTS()
            >>> for chunk in tts.stream("Hello world"):
            ...     print(chunk)
        """
        from elevenlabs.types.voice_settings import VoiceSettings

        voice_settings = VoiceSettings(
            stability=kwargs.pop("stability", 0.5),
            use_speaker_boost=kwargs.pop("use_speaker_boost", True),
            similarity_boost=kwargs.pop("similarity_boost", 0.75),
            style=kwargs.pop("style", 0.0),
            speed=kwargs.pop("speed", 1.0),
        )

        response = self.client.text_to_speech.stream(
            text=text,
            voice_id=voice_id,
            model_id=model_id,
            output_format=response_format,
            voice_settings=voice_settings,
            **kwargs,
        )

        encoded_format, sample_rate = self._parse_output_format(response_format)
        self.current_sample_rate = sample_rate
        for data in response:
            yield AudioData(data, sample_rate, encoded_format)
