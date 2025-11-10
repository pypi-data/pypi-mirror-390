"""
Speech-to-Text (STT) main interface for Yemot HaMashiach systems
"""
from typing import Union, BinaryIO, Type, Dict, Any
from pathlib import Path
from .base import STTProvider


class STT:
    """
    Main Speech-to-Text interface that supports multiple providers
    
    Usage:
        stt = STT(provider='openai', api_key='your-key')
        text = stt.transcribe('audio.wav')
    """
    
    # Registry of available providers
    _providers: Dict[str, Type[STTProvider]] = {}
    
    def __init__(self, provider: str = 'openai', **provider_config):
        """
        Initialize STT with specified provider
        
        Args:
            provider: Name of the provider ('openai', 'google', 'amazon', 'local')
            **provider_config: Configuration parameters for the provider
        """
        self.provider_name = provider.lower()
        
        if self.provider_name not in self._providers:
            self._load_provider(self.provider_name)
        
        if self.provider_name not in self._providers:
            available = ', '.join(self._providers.keys())
            raise ValueError(f"Provider '{provider}' not found. Available providers: {available}")
        
        provider_class = self._providers[self.provider_name]
        self.provider = provider_class(**provider_config)
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[STTProvider]):
        """Register a new STT provider"""
        cls._providers[name.lower()] = provider_class
    
    @classmethod
    def get_available_providers(cls) -> list:
        """Get list of available provider names"""
        return list(cls._providers.keys())
    
    def _load_provider(self, provider_name: str):
        """Dynamically load a provider module"""
        try:
            if provider_name == 'openai':
                from .providors.openai import OpenAISTT
                self.register_provider('openai', OpenAISTT)
            elif provider_name == 'google':
                from .providors.google import GoogleSTT
                self.register_provider('google', GoogleSTT)
            elif provider_name == 'amazon':
                from .providors.amazon import AmazonSTT
                self.register_provider('amazon', AmazonSTT)
            elif provider_name == 'local':
                from .providors.local import LocalSTT
                self.register_provider('local', LocalSTT)
            else:
                raise ImportError(f"Unknown provider: {provider_name}")
        except ImportError as e:
            raise ImportError(f"Failed to load provider '{provider_name}': {e}")
    
    def transcribe(self, audio_file: Union[str, Path, BinaryIO], **kwargs) -> str:
        """
        Convert audio file to text
        
        Args:
            audio_file: Path to audio file or file-like object
            **kwargs: Additional parameters specific to the provider
            
        Returns:
            Transcribed text
        """
        return self.provider.transcribe(audio_file, **kwargs)
    
    def transcribe_bytes(self, audio_bytes: bytes, **kwargs) -> str:
        """
        Convert audio bytes to text
        
        Args:
            audio_bytes: Audio data as bytes
            **kwargs: Additional parameters specific to the provider
            
        Returns:
            Transcribed text
        """
        return self.provider.transcribe_bytes(audio_bytes, **kwargs)
    
    def get_provider_info(self) -> dict:
        """Get information about the current provider"""
        return {
            'name': self.provider_name,
            'class': self.provider.__class__.__name__,
            'config': getattr(self.provider, 'config', {})
        }


# Convenience function for quick usage
def transcribe(audio_file: Union[str, Path, BinaryIO], provider: str = 'openai', **provider_config) -> str:
    """
    Quick transcription function
    
    Args:
        audio_file: Path to audio file or file-like object
        provider: STT provider to use
        **provider_config: Configuration for the provider
        
    Returns:
        Transcribed text
    """
    stt = STT(provider=provider, **provider_config)
    return stt.transcribe(audio_file)
