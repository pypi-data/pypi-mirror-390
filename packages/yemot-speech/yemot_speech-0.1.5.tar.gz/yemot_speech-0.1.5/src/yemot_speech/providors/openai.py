"""
OpenAI Speech-to-Text provider for Yemot HaMashiach systems
"""
from typing import Union, BinaryIO
from pathlib import Path
import io
from ..base import STTProvider

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


class OpenAISTT(STTProvider):
    """OpenAI Whisper Speech-to-Text provider"""
    
    def __init__(self, api_key: str = None, model: str = "whisper-1", **kwargs):
        """
        Initialize OpenAI STT provider
        
        Args:
            api_key: OpenAI API key
            model: Whisper model to use (default: whisper-1)
            **kwargs: Additional configuration
        """
        if not HAS_OPENAI:
            raise ImportError("openai package is required. Install with: pip install openai")
        
        super().__init__(api_key=api_key, model=model, **kwargs)
        
        if api_key:
            openai.api_key = api_key
        
        self.model = model
    
    def transcribe(self, audio_file: Union[str, Path, BinaryIO], **kwargs) -> str:
        """
        Transcribe audio file using OpenAI Whisper
        
        Args:
            audio_file: Path to audio file or file-like object
            **kwargs: Additional parameters (language, temperature, etc.)
            
        Returns:
            Transcribed text
        """
        # If it's a path, open the file
        if isinstance(audio_file, (str, Path)):
            with open(audio_file, 'rb') as f:
                return self._transcribe_file_object(f, **kwargs)
        else:
            return self._transcribe_file_object(audio_file, **kwargs)
    
    def transcribe_bytes(self, audio_bytes: bytes, **kwargs) -> str:
        """
        Transcribe audio bytes using OpenAI Whisper
        
        Args:
            audio_bytes: Audio data as bytes
            **kwargs: Additional parameters
            
        Returns:
            Transcribed text
        """
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.wav"  # OpenAI requires a filename
        return self._transcribe_file_object(audio_file, **kwargs)
    
    def _transcribe_file_object(self, file_obj, **kwargs):
        """Internal method to transcribe file-like object"""
        try:
            # Prepare parameters
            params = {
                'model': self.model,
                'file': file_obj
            }
            
            # Add optional parameters
            if 'language' in kwargs:
                params['language'] = kwargs['language']
            if 'temperature' in kwargs:
                params['temperature'] = kwargs['temperature']
            if 'prompt' in kwargs:
                params['prompt'] = kwargs['prompt']
            
            # Make API call
            response = openai.Audio.transcribe(**params)
            
            return response['text'] if isinstance(response, dict) else response.text
            
        except Exception as e:
            raise RuntimeError(f"OpenAI transcription failed: {str(e)}")


# Example usage for Hebrew/Yiddish content
class YemotOpenAISTT(OpenAISTT):
    """Specialized OpenAI STT for Yemot HaMashiach with Hebrew/Yiddish optimizations"""
    
    def transcribe(self, audio_file: Union[str, Path, BinaryIO], language: str = "he", **kwargs) -> str:
        """
        Transcribe with Hebrew as default language
        """
        return super().transcribe(audio_file, language=language, **kwargs)
    
    def transcribe_bytes(self, audio_bytes: bytes, language: str = "he", **kwargs) -> str:
        """
        Transcribe bytes with Hebrew as default language
        """
        return super().transcribe_bytes(audio_bytes, language=language, **kwargs)
