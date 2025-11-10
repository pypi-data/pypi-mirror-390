"""
Text-to-Speech (TTS) main interface for Yemot HaMashiach systems
"""
from typing import Union, BinaryIO, Type, Dict, Any
from pathlib import Path
from .base import TTSProvider


class TTS:
    """
    Main Text-to-Speech interface that supports multiple providers
    
    Usage:
        tts = TTS(provider='openai', api_key='your-key')
        audio_bytes = tts.synthesize('שלום עליכם!')
        tts.save_audio('שלום עליכם!', 'greeting.wav')
    """
    
    # Registry of available providers
    _providers: Dict[str, Type[TTSProvider]] = {}
    
    def __init__(self, provider: str = 'gtts', **provider_config):
        """
        Initialize TTS with specified provider
        
        Args:
            provider: Name of the provider ('openai', 'google', 'amazon', 'gtts', 'azure')
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
    def register_provider(cls, name: str, provider_class: Type[TTSProvider]):
        """Register a new TTS provider"""
        cls._providers[name.lower()] = provider_class
    
    @classmethod
    def get_available_providers(cls) -> list:
        """Get list of available provider names"""
        return list(cls._providers.keys())
    
    def _load_provider(self, provider_name: str):
        """Dynamically load a provider module"""
        try:
            if provider_name == 'openai':
                from .providors.openai_tts import OpenAITTS
                self.register_provider('openai', OpenAITTS)
            elif provider_name == 'google' or provider_name == 'gtts':
                from .providors.gtts import GoogleTTS
                self.register_provider('google', GoogleTTS)
                self.register_provider('gtts', GoogleTTS)
            elif provider_name == 'amazon':
                from .providors.amazon_tts import AmazonTTS
                self.register_provider('amazon', AmazonTTS)
            elif provider_name == 'azure':
                from .providors.azure_tts import AzureTTS
                self.register_provider('azure', AzureTTS)
            else:
                raise ImportError(f"Unknown provider: {provider_name}")
        except ImportError as e:
            raise ImportError(f"Failed to load provider '{provider_name}': {e}")
    
    def synthesize(self, text: str, **kwargs) -> bytes:
        """
        Convert text to speech and return audio bytes
        
        Args:
            text: Text to convert to speech
            **kwargs: Additional parameters specific to the provider
            
        Returns:
            Audio data as bytes
        """
        result = self.provider.synthesize(text, output_file=None, **kwargs)
        if isinstance(result, bytes):
            return result
        else:
            # If provider returned file path, read the file
            with open(result, 'rb') as f:
                return f.read()
    
    def save_audio(self, text: str, output_file: Union[str, Path], **kwargs) -> str:
        """
        Convert text to speech and save to file
        
        Args:
            text: Text to convert to speech
            output_file: Path where to save the audio file
            **kwargs: Additional parameters specific to the provider
            
        Returns:
            Path to the saved audio file
        """
        result = self.provider.synthesize(text, output_file=output_file, **kwargs)
        return str(result)
    
    def play_audio(self, text: str, **kwargs):
        """
        Convert text to speech and play immediately
        
        Args:
            text: Text to convert to speech
            **kwargs: Additional parameters specific to the provider
        """
        if hasattr(self.provider, 'play_audio'):
            audio_bytes = self.synthesize(text, **kwargs)
            self.provider.play_audio(audio_bytes)
        else:
            raise NotImplementedError(f"Provider '{self.provider_name}' doesn't support direct playback")
    
    def get_provider_info(self) -> dict:
        """Get information about the current provider"""
        return {
            'name': self.provider_name,
            'class': self.provider.__class__.__name__,
            'config': getattr(self.provider, 'config', {})
        }


# Convenience function for quick usage
def synthesize(text: str, provider: str = 'gtts', output_file: Union[str, Path] = None, **provider_config) -> Union[bytes, str]:
    """
    Quick synthesis function
    
    Args:
        text: Text to convert to speech
        provider: TTS provider to use
        output_file: Optional file path to save audio
        **provider_config: Configuration for the provider
        
    Returns:
        Audio bytes if output_file is None, otherwise path to saved file
    """
    tts = TTS(provider=provider, **provider_config)
    if output_file:
        return tts.save_audio(text, output_file)
    else:
        return tts.synthesize(text)


def speak(text: str, provider: str = 'gtts', **provider_config):
    """
    Quick speak function - convert text to speech and play
    
    Args:
        text: Text to speak
        provider: TTS provider to use
        **provider_config: Configuration for the provider
    """
    tts = TTS(provider=provider, **provider_config)
    tts.play_audio(text)