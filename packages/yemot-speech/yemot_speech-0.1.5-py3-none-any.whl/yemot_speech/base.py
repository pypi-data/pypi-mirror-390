"""
Base classes for speech-to-text and text-to-speech providers
"""
from abc import ABC, abstractmethod
from typing import Union, BinaryIO
from pathlib import Path


class STTProvider(ABC):
    """Abstract base class for Speech-to-Text providers"""
    
    def __init__(self, **kwargs):
        """Initialize the provider with configuration parameters"""
        self.config = kwargs
    
    @abstractmethod
    def transcribe(self, audio_file: Union[str, Path, BinaryIO], **kwargs) -> str:
        """
        Convert audio to text
        
        Args:
            audio_file: Path to audio file or file-like object
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Transcribed text
        """
        pass
    
    @abstractmethod
    def transcribe_bytes(self, audio_bytes: bytes, **kwargs) -> str:
        """
        Convert audio bytes to text
        
        Args:
            audio_bytes: Audio data as bytes
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Transcribed text
        """
        pass


class TTSProvider(ABC):
    """Abstract base class for Text-to-Speech providers"""
    
    def __init__(self, **kwargs):
        """Initialize the provider with configuration parameters"""
        self.config = kwargs
    
    @abstractmethod
    def synthesize(self, text: str, output_file: Union[str, Path] = None, **kwargs) -> Union[bytes, str]:
        """
        Convert text to speech
        
        Args:
            text: Text to convert to speech
            output_file: Optional path to save audio file
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Audio bytes if output_file is None, otherwise path to saved file
        """
        pass