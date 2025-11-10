from typing import Generator, Any
from abc import ABC, abstractmethod

from .audio import AudioData

from dotenv import load_dotenv

load_dotenv()

class TTSProvider(ABC):
    """
    Abstract base class for TTS providers.

    All TTS providers should inherit from this class and implement
    the required abstract methods.
    """

    @abstractmethod
    def run(self, text: str, **kwargs: Any) -> AudioData:
        """
        Generate speech from text in a single request.

        Args:
            text: The text to convert to speech
            **kwargs: Provider-specific parameters

        Returns:
            AudioData object containing the generated audio
        """
        pass

    @abstractmethod
    def stream(self, text: str, **kwargs: Any) -> Generator[AudioData, None, None]:
        """
        Generate speech from text in streaming mode.

        Args:
            text: The text to convert to speech
            **kwargs: Provider-specific parameters

        Yields:
            AudioData objects containing chunks of generated audio
        """
        pass

    @abstractmethod
    def get_sample_rate(self) -> int:
        """
        Get the sample rate of the audio output.

        Returns:
            Sample rate in Hz (e.g., 24000, 22050)
        """
        pass