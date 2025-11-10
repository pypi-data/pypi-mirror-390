import numpy as np
from typing import get_args

from .constants import EncodedBytesFormat, AudioFormat, DType

class AudioValidator:
    """Shared validation logic for audio conversion."""
    
    @staticmethod
    def validate_data(data: bytes | np.ndarray):
        """Validate that data is bytes or numpy array and not empty."""
        if not isinstance(data, (bytes, np.ndarray)):
            raise TypeError(
                f"Data must be bytes or numpy array, got {type(data).__name__}"
            )
        
        if len(data) == 0:
            raise ValueError("Data must not be empty")
    
    @staticmethod
    def validate_sample_rate(sample_rate: int):
        """Validate that sample_rate is a positive integer."""
        if not isinstance(sample_rate, int):
            raise TypeError(
                f"Sample rate must be an integer, got {type(sample_rate).__name__}"
            )
        
        if sample_rate <= 0:
            raise ValueError("Sample rate must be greater than 0")
    
    @staticmethod
    def validate_output_format(output_format: str):
        """Validate that output_format is one of the supported byte formats."""
        if output_format not in get_args(EncodedBytesFormat):
            raise ValueError(
                f"Invalid output format: {output_format}. "
                f"Valid formats are: {get_args(EncodedBytesFormat)}"
            )
    
    @staticmethod
    def validate_target_dtype(target_dtype: str):
        """Validate that target_dtype is one of the supported types."""
        if target_dtype not in get_args(DType):
            raise ValueError(
                f"Invalid target dtype: {target_dtype}. "
                f"Valid dtypes are: {get_args(DType)}"
            )
    
    @staticmethod
    def validate_encoded_format_for_data(data: bytes | np.ndarray, encoded_format: str):
        """
        Validate that encoded_format matches the data type (bytes or numpy).
        
        Used by AudioData to ensure numpy arrays use 'raw' and bytes use valid byte formats.
        """
        is_numpy = isinstance(data, np.ndarray)
        is_bytes = isinstance(data, bytes)
        
        if is_numpy and encoded_format != "raw":
            raise ValueError(
                f"Invalid encoded format for numpy array: {encoded_format}. "
                f"The only valid format is 'raw'"
            )
        
        if is_bytes and encoded_format not in get_args(EncodedBytesFormat):
            raise ValueError(
                f"Invalid encoded format for bytes: {encoded_format}. "
                f"Valid formats are: {get_args(EncodedBytesFormat)}"
            )
    
    @staticmethod
    def validate_encoded_format(encoded_format: str):
        """
        Validate that encoded_format is a supported audio format."""
        valid_formats = get_args(AudioFormat)
        if encoded_format not in valid_formats:
            raise ValueError(
                f"Invalid encoded format: {encoded_format}. "
                f"Valid formats are: {valid_formats}"
            )

    @staticmethod
    def validate_audio_data_inputs(
        data: bytes | np.ndarray,
        sample_rate: int,
        encoded_format: str
    ):
        """Validate all inputs for AudioData initialization."""
        AudioValidator.validate_data(data)
        AudioValidator.validate_sample_rate(sample_rate)
        AudioValidator.validate_encoded_format_for_data(data, encoded_format)

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