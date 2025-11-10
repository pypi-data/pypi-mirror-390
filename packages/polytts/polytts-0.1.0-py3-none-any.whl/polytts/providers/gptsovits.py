from pathlib import Path
from typing import Generator, Any

from ..base import TTSProvider
from ..audio import AudioData

root_dir = Path(__file__).parent.parent

class GPTSovitsTTS(TTSProvider):
    def __init__(
        self,
        model_version: str = "v2ProPlus",
        is_half: bool = False,
        device: str | None = None,
        warmup_model: bool = False
    ):
        """
        Initialize GPT-SoVITS TTS provider.

        Args:
            model_version: Model version to use. Options:
                "v2ProPlus", "v2Pro", "v2", "v1", "v3", "v4"
            
            is_half: Whether to use half precision.
            
            device: Device to run the model on. If None, uses "cuda" if available, otherwise "cpu".
            
            warmup_model: Whether to warmup the model. Faster inference on consecutive calls
        """
        try:
            from GPT_SoVITS.TTS_infer_pack.TTS import TTS, TTS_Config
        except ImportError:
            raise ImportError(
                "GPTSoVITS is not installed. Install with one of:\n"
                "  - Install from URL: pip install git+https://github.com/spava002/GPT-SoVITS-Streaming.git (recommended)\n"
                "  - Manual setup from source: https://github.com/RVC-Boss/GPT-SoVITS"
            )
        import torch

        version_configs = TTS_Config.default_configs[model_version].copy()

        version_configs["device"] = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        version_configs["is_half"] = is_half

        self.client = TTS(TTS_Config({"custom": version_configs}))

        if warmup_model:
            self.run("Warming up...")

    def get_sample_rate(self) -> int:
        return self.client.configs.sampling_rate

    def run(
        self,
        text: str,
        text_lang: str = "en",
        ref_audio_path: str | None = None,
        **kwargs: Any,
    ) -> AudioData:
        """
        Generate speech from text using GPT-SoVITS.

        Args:
            text: The text to convert to speech
            
            text_lang: Language of the text. Options:
                "en", "zh", "ja", "yue", "ko", "all_zh", "all_ja", "all_yue", "all_ko"
            
            ref_audio_path: Path to reference audio file for voice cloning.
                Should be 3-10 seconds of clear speech. If None, uses default reference.
            
            **kwargs: Additional parameters
                prompt_text: Transcript of reference audio for better cloning. Default: "".
                
                prompt_lang: Language of prompt text. Options: "en", "zh", "ja", "ko", "yue". Default: "".
                
                aux_ref_audio_paths: Additional reference audios for tone fusion. Default: [].

                speed_factor: Speech speed multiplier. Default: 1.0
                
                For complete API reference:
                    If installed from URL: 
                    https://github.com/spava002/GPT-SoVITS-Streaming/blob/main/GPT_SoVITS/TTS_infer_pack/TTS.py#L1015
                    
                    If installed from source: 
                    https://github.com/RVC-Boss/GPT-SoVITS/blob/main/GPT_SoVITS/TTS_infer_pack/TTS.py#L984

        Returns:
            AudioData object with generated audio

        Example:
            >>> tts = GPTSovitsTTS()
            >>> audio = tts.run("Hello world")
        """

        ref_audio_path = ref_audio_path or f"{root_dir}/audio/default_{text_lang}.mp3"

        inputs = {
            "text": text,
            "text_lang": text_lang,
            "ref_audio_path": ref_audio_path,
            **kwargs,
            # Override: Streaming is not allowed here
            "return_fragment": False
        }

        response = self.client.run(inputs)

        sample_rate, data = next(response)
        return AudioData(data, sample_rate,"raw")

    def stream(
        self,
        text: str,
        text_lang: str = "en",
        ref_audio_path: str | None = None,
        **kwargs: Any,
    ) -> Generator[AudioData, None, None]:
        """
        Stream speech generation from text using GPT-SoVITS.

        Args:
            text: The text to convert to speech
            
            text_lang: Language of the text. Options:
                "en", "zh", "ja", "yue", "ko", "all_zh", "all_ja", "all_yue", "all_ko"
            
            ref_audio_path: Path to reference audio file for voice cloning.
                Should be 3-10 seconds of clear speech. If None, uses default reference.
            
            **kwargs: Additional parameters
                prompt_text: Transcript of reference audio for better cloning. Default: "".
                
                prompt_lang: Language of prompt text. Options: "en", "zh", "ja", "ko", "yue". Default: "".
                
                aux_ref_audio_paths: Additional reference audios for tone fusion. Default: [].

                speed_factor: Speech speed multiplier. Default: 1.0
                
                For complete API reference:
                    If installed from URL: 
                    https://github.com/spava002/GPT-SoVITS-Streaming/blob/main/GPT_SoVITS/TTS_infer_pack/TTS.py#L1015
                    
                    If installed from source: 
                    https://github.com/RVC-Boss/GPT-SoVITS/blob/main/GPT_SoVITS/TTS_infer_pack/TTS.py#L984

        Yields:
            AudioData objects containing chunks of generated audio

        Example:
            >>> tts = GPTSovitsTTS()
            >>> for chunk in tts.stream("Hello world"):
            ...     print(chunk)
        """
        ref_audio_path = ref_audio_path or f"{root_dir}/audio/default_{text_lang}.mp3"

        inputs = {
            "text": text,
            "text_lang": text_lang,
            "ref_audio_path": ref_audio_path,
            **kwargs,
            # Override: These are necessary for streaming to work
            "return_fragment": True,
            "parallel_infer": False,
        }

        for sample_rate, data in self.client.run(inputs):
            yield AudioData(data, sample_rate, "raw")
