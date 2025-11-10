from re import S
import numpy as np
from typing import get_args

from .constants import EncodedBytesFormat, AudioFormat, DType
from .validation import AudioValidator

class AudioConverter:
    """Handles encoding and decoding between audio formats."""
    
    @staticmethod
    def to_bytes(
        data: bytes | np.ndarray,
        sample_rate: int,
        encoded_format: AudioFormat,
        output_format: EncodedBytesFormat
    ) -> bytes:
        """
        Convert bytes or numpy array to the specified bytes output format.
        
        Args:
            data: Bytes or numpy array of audio data to convert
            sample_rate: Audio sample rate in Hz
            encoded_format: Format of the audio data any of "pcm", "mp3", "wav", "raw"
            output_format: Target bytes output format any of "pcm", "wav", "mp3"
        
        Returns:
            Audio data as bytes in the specified format
        """
        AudioValidator.validate_to_bytes_inputs(
            data,
            sample_rate,
            encoded_format,
            output_format
        )
        
        if isinstance(data, bytes):
            if encoded_format == output_format:
                return data
            data = AudioConverter._decode_to_numpy(data, encoded_format)
        else:
            data = AudioConverter._numpy_to_int16(data)
        
        return AudioConverter._encode_to_bytes(data, sample_rate, output_format)
    
    @staticmethod
    def to_numpy(
        data: bytes | np.ndarray,
        encoded_format: AudioFormat,
        target_dtype: DType
    ) -> np.ndarray:
        """
        Convert bytes data to numpy array with specified dtype.
        
        Args:
            data: Bytes of audio data to convert
            encoded_format: Format of the audio data any of "pcm", "mp3", "wav"
            target_dtype: Target numpy dtype any of "float32", "float16", "int16", or "int32"
        
        Returns:
            Numpy array with mono audio samples in target dtype
        """
        AudioValidator.validate_to_numpy_inputs(
            data,
            encoded_format,
            target_dtype
        )

        if isinstance(data, bytes):
            data = AudioConverter._decode_to_numpy(data, encoded_format)
        
        if data.dtype == target_dtype: 
            return data 
        
        return AudioConverter._convert_to_dtype(data, np.dtype(target_dtype))

    @staticmethod
    def _encode_to_bytes(
        data: np.ndarray,
        sample_rate: int,
        output_format: EncodedBytesFormat
    ) -> bytes:
        """Encode numpy array to bytes in specified format."""
        match output_format:
            case "pcm":
                return AudioConverter._encode_pcm(data)
            case "wav":
                return AudioConverter._encode_wav(data, sample_rate)
            case "mp3":
                return AudioConverter._encode_mp3(data, sample_rate)
            case _:
                raise ValueError(f"Cannot encode format: {output_format}")

    @staticmethod
    def _numpy_to_int16(data: np.ndarray) -> np.ndarray:
        """Convert numpy array to int16 samples."""
        if data.dtype in (np.float16, np.float32):
            return (data * 32767.0).astype(np.int16)
        else:
            return data.astype(np.int16)
    
    @staticmethod
    def _convert_to_dtype(data: np.ndarray, target_dtype: np.dtype) -> np.ndarray:
        """Convert numpy array to target dtype with proper scaling."""
        if data.dtype == target_dtype:
            return data
        
        current_is_float = data.dtype in (np.float16, np.float32)
        target_is_float = target_dtype in (np.float16, np.float32)
        
        if current_is_float and not target_is_float:
            target_max = np.iinfo(target_dtype).max
            return (data * target_max).astype(target_dtype)
        
        if not current_is_float and target_is_float:
            current_max = np.iinfo(data.dtype).max
            return (data / current_max).astype(target_dtype)
        
        if current_is_float and target_is_float:
            return data.astype(target_dtype)
        
        current_max = np.iinfo(data.dtype).max
        target_max = np.iinfo(target_dtype).max
        
        if current_max < target_max:
            scale = target_max // current_max
            return (data.astype(target_dtype) * scale).astype(target_dtype)
        elif current_max > target_max:
            scale = current_max // target_max
            return (data // scale).astype(target_dtype)
        
        return data.astype(target_dtype)
        
    @staticmethod
    def _decode_to_numpy(data: bytes, encoded_format: EncodedBytesFormat) -> np.ndarray:
        """Decode bytes to int16 mono numpy array."""
        match encoded_format:
            case "pcm":
                return AudioConverter._decode_pcm(data)
            case "wav":
                return AudioConverter._decode_wav(data)
            case "mp3":
                return AudioConverter._decode_mp3(data)
            case _:
                raise ValueError(f"Cannot decode format: {encoded_format}")
    
    @staticmethod
    def _decode_pcm(data: bytes) -> np.ndarray:
        """Decode PCM bytes to int16 numpy array."""
        return np.frombuffer(data, dtype=np.int16)
    
    @staticmethod
    def _decode_wav(data: bytes) -> np.ndarray:
        """Decode WAV bytes to int16 numpy array."""
        import io
        import wave
        
        with wave.open(io.BytesIO(data), "rb") as wav_file:
            frames = wav_file.readframes(wav_file.getnframes())
            return np.frombuffer(frames, dtype=np.int16)
    
    @staticmethod
    def _decode_mp3(data: bytes) -> np.ndarray:
        """Decode MP3 bytes to int16 numpy array."""
        try:
            import io
            from pydub import AudioSegment
            
            audio_seg = AudioSegment.from_mp3(io.BytesIO(data))
            return np.array(audio_seg.get_array_of_samples(), dtype=np.int16)
        except ImportError:
            raise ImportError(
                "MP3 decoding requires 'pydub' and 'ffmpeg'. "
                "Install: pip install pydub"
            )
    
    @staticmethod
    def _encode_pcm(data: np.ndarray) -> bytes:
        """Encode int16 numpy array to PCM format bytes."""
        return data.tobytes()

    @staticmethod
    def _encode_wav(data: np.ndarray, sample_rate: int) -> bytes:
        """Encode int16 numpy array to WAV format bytes."""
        import io
        import wave
        
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(data.tobytes())
        
        return buffer.getvalue()
    
    @staticmethod
    def _encode_mp3(data: np.ndarray, sample_rate: int) -> bytes:
        """Encode int16 numpy array to MP3 format bytes."""
        try:
            import io
            from pydub import AudioSegment
            
            audio = AudioSegment(
                data=data.tobytes(),
                sample_width=2,
                frame_rate=sample_rate,
                channels=1
            )
            
            buffer = io.BytesIO()
            audio.export(
                buffer,
                format="mp3",
                codec="libmp3lame",
                bitrate="128k"
            )
            return buffer.getvalue()
        except ImportError:
            raise ImportError(
                "MP3 encoding requires 'pydub' and 'ffmpeg'. "
                "Install: pip install pydub"
            )

    @staticmethod
    def validate_to_bytes_inputs(
        data: bytes | np.ndarray,
        sample_rate: int,
        encoded_format: str,
        output_format: str
    ):
        """Validate all inputs for to_bytes conversion."""
        AudioValidator.validate_data(data)
        AudioValidator.validate_sample_rate(sample_rate)
        AudioValidator.validate_encoded_format(encoded_format)
        AudioValidator.validate_output_format(output_format)
    
    @staticmethod
    def validate_to_numpy_inputs(
        data: bytes | np.ndarray,
        encoded_format: str,
        target_dtype: str
    ):
        """Validate all inputs for to_numpy conversion."""
        AudioValidator.validate_data(data)
        AudioValidator.validate_encoded_format(encoded_format)
        AudioValidator.validate_target_dtype(target_dtype)