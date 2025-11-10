from typing import Literal

EncodedBytesFormat = Literal["pcm", "mp3", "wav"]
AudioFormat = Literal["pcm", "mp3", "wav", "raw"]

DType = Literal["int16", "int32", "float16", "float32"]