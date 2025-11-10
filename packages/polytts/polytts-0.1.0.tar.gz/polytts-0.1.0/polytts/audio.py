import numpy as np
from functools import cached_property
from dataclasses import dataclass

from .codecs import AudioConverter
from .constants import EncodedBytesFormat, AudioFormat, DType
from .validation import AudioValidator

@dataclass
class AudioData:
    """
    Container for audio data with metadata and conversion utilities.
    
    Stores audio as either bytes (encoded formats like PCM, WAV, MP3) or
    numpy arrays (raw samples). Provides methods to convert between formats
    and data types.
    
    Attributes:
        data: Raw audio data as bytes or numpy array
        sample_rate: Audio sample rate in Hz
        encoded_format: Format of the audio data any of "pcm", "mp3", "wav", "raw"
        dtype: Numpy dtype if data is numpy array, None otherwise
        duration: Audio duration in seconds
    """
    data: bytes | np.ndarray
    sample_rate: int
    encoded_format: AudioFormat

    def __post_init__(self):
        """Validate inputs after dataclass initialization."""
        AudioValidator.validate_audio_data_inputs(
            self.data,
            self.sample_rate,
            self.encoded_format
        )

    def __repr__(self) -> str:
        """Custom repr that properly shows computed properties."""
        data_preview = f"<{len(self.data)} bytes>" if self.is_bytes else f"<array shape={self.data.shape}>"
        return (
            f"AudioData("
            f"data={data_preview}, "
            f"sample_rate={self.sample_rate}, "
            f"encoded_format='{self.encoded_format}', "
            f"dtype={self.dtype}, "
            f"duration={self.duration:.2f}s"
            f")"
        )

    @property
    def is_numpy(self) -> bool:
        """Check if audio data is stored as numpy array."""
        return isinstance(self.data, np.ndarray)

    @property
    def is_bytes(self) -> bool:
        """Check if audio data is stored as bytes."""
        return isinstance(self.data, bytes)

    @property
    def dtype(self) -> np.dtype | None:
        """Get numpy dtype of the data, or None if data is bytes."""
        if self.is_numpy:
            return self.data.dtype
        return None

    @cached_property
    def duration(self) -> float:
        """Get audio duration in seconds."""
        if self.encoded_format == "raw":
            return len(self.data) / self.sample_rate
        elif self.encoded_format == "pcm":
            num_samples = len(self.data) // 2
            return num_samples / self.sample_rate
        elif self.encoded_format == "mp3":
            try:
                import io
                from mutagen.mp3 import MP3
                audio = MP3(io.BytesIO(self.data))
                return audio.info.length
            except ImportError:
                raise ImportError(
                    "MP3 duration requires 'mutagen'. "
                    "Install with: pip install mutagen"
                )
        elif self.encoded_format == "wav":
            import io
            import wave
            with wave.open(io.BytesIO(self.data), "rb") as wav_file:
                frames = wav_file.getnframes()
                rate = wav_file.getframerate()
                return frames / float(rate)

    def as_bytes(self, output_format: EncodedBytesFormat = "pcm") -> bytes:
        """
        Convert audio data to bytes in specified format.
        
        Converts between PCM, WAV, and MP3 formats. Always returns mono audio.
        
        Args:
            output_format: Target format any of "pcm", "wav", or "mp3"
        
        Returns:
            Audio data as bytes in the specified format
        
        Examples:
            >>> audio = AudioData(numpy_array, 24000, "raw")
            >>> pcm_bytes = audio.as_bytes("pcm")
            >>> wav_bytes = audio.as_bytes("wav")
        """
        return AudioConverter.to_bytes(
            self.data,
            self.sample_rate,
            self.encoded_format,
            output_format
        )

    def as_numpy(self, target_dtype: DType = "float32") -> np.ndarray:
        """
        Convert audio data to numpy array with specified dtype.
        
        Decodes encoded formats (PCM, WAV, MP3) to raw samples and converts
        to the target dtype with proper scaling between int and float types.
        
        Args:
            target_dtype: Target numpy dtype any of "float32", "float16", "int16", or "int32"
        
        Returns:
            Numpy array with mono audio samples in target dtype
        
        Examples:
            >>> audio = AudioData(pcm_bytes, 24000, "pcm")
            >>> samples_float32 = audio.as_numpy("float32")
            >>> samples_int16 = audio.as_numpy("int16")
        """
        return AudioConverter.to_numpy(
            self.data,
            self.encoded_format,
            target_dtype
        )