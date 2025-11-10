"""
Google Cloud Speech-to-Text provider for Yemot HaMashiach systems
"""
from typing import Union, BinaryIO
from pathlib import Path
from ..base import STTProvider

try:
    from google.cloud import speech
    HAS_GOOGLE_SPEECH = True
except ImportError:
    HAS_GOOGLE_SPEECH = False


class GoogleSTT(STTProvider):
    """Google Cloud Speech-to-Text provider"""
    
    def __init__(self, credentials_path: str = None, language_code: str = "he-IL", **kwargs):
        """
        Initialize Google Speech-to-Text provider
        
        Args:
            credentials_path: Path to Google Cloud service account JSON file
            language_code: Language code (default: he-IL for Hebrew)
            **kwargs: Additional configuration
        """
        if not HAS_GOOGLE_SPEECH:
            raise ImportError("google-cloud-speech package is required. Install with: pip install google-cloud-speech")
        
        super().__init__(credentials_path=credentials_path, language_code=language_code, **kwargs)
        
        # Initialize client
        if credentials_path:
            import os
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        
        self.client = speech.SpeechClient()
        self.language_code = language_code
    
    def transcribe(self, audio_file: Union[str, Path, BinaryIO], **kwargs) -> str:
        """
        Transcribe audio file using Google Speech-to-Text
        
        Args:
            audio_file: Path to audio file or file-like object
            **kwargs: Additional parameters
            
        Returns:
            Transcribed text
        """
        # Read audio content
        if isinstance(audio_file, (str, Path)):
            with open(audio_file, 'rb') as f:
                audio_content = f.read()
        else:
            audio_content = audio_file.read()
            
        return self.transcribe_bytes(audio_content, **kwargs)
    
    def transcribe_bytes(self, audio_bytes: bytes, **kwargs) -> str:
        """
        Transcribe audio bytes using Google Speech-to-Text
        
        Args:
            audio_bytes: Audio data as bytes
            **kwargs: Additional parameters
            
        Returns:
            Transcribed text
        """
        try:
            # Configure audio
            audio = speech.RecognitionAudio(content=audio_bytes)
            
            # Configure recognition
            config = speech.RecognitionConfig(
                encoding=kwargs.get('encoding', speech.RecognitionConfig.AudioEncoding.WEBM_OPUS),
                sample_rate_hertz=kwargs.get('sample_rate', 16000),
                language_code=kwargs.get('language_code', self.language_code),
                enable_automatic_punctuation=kwargs.get('enable_punctuation', True),
                model=kwargs.get('model', 'latest_long'),
            )
            
            # Perform recognition
            response = self.client.recognize(config=config, audio=audio)
            
            # Extract text from response
            transcripts = []
            for result in response.results:
                if result.alternatives:
                    transcripts.append(result.alternatives[0].transcript)
            
            return ' '.join(transcripts)
            
        except Exception as e:
            raise RuntimeError(f"Google Speech-to-Text transcription failed: {str(e)}")


class YemotGoogleSTT(GoogleSTT):
    """Specialized Google STT for Yemot HaMashiach with Hebrew optimizations"""
    
    def __init__(self, credentials_path: str = None, **kwargs):
        """Initialize with Hebrew-specific settings"""
        super().__init__(
            credentials_path=credentials_path,
            language_code="he-IL",
            **kwargs
        )
    
    def transcribe_yemot_call(self, audio_bytes: bytes, **kwargs) -> str:
        """
        Transcribe Yemot phone call audio with optimized settings
        """
        # Phone call specific settings
        phone_kwargs = {
            'encoding': speech.RecognitionConfig.AudioEncoding.MULAW,
            'sample_rate': 8000,
            'model': 'phone_call',
            'enable_punctuation': True,
            **kwargs
        }
        
        return self.transcribe_bytes(audio_bytes, **phone_kwargs)
