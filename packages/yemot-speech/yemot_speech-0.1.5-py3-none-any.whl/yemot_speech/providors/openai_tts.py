"""
OpenAI Text-to-Speech provider for Yemot HaMashiach systems
"""
from typing import Union
from pathlib import Path
import io
from ..base import TTSProvider

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


class OpenAITTS(TTSProvider):
    """OpenAI Text-to-Speech provider"""
    
    def __init__(self, api_key: str = None, model: str = "tts-1", voice: str = "alloy", **kwargs):
        """
        Initialize OpenAI TTS provider
        
        Args:
            api_key: OpenAI API key
            model: TTS model to use (tts-1 or tts-1-hd)
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
            **kwargs: Additional configuration
        """
        if not HAS_OPENAI:
            raise ImportError("openai package is required. Install with: pip install openai")
        
        super().__init__(api_key=api_key, model=model, voice=voice, **kwargs)
        
        if api_key:
            openai.api_key = api_key
        
        self.model = model
        self.voice = voice
    
    def synthesize(self, text: str, output_file: Union[str, Path] = None, **kwargs) -> Union[bytes, str]:
        """
        Synthesize text using OpenAI TTS
        
        Args:
            text: Text to convert to speech
            output_file: Optional path to save audio file
            **kwargs: Additional parameters (voice, model, speed, etc.)
            
        Returns:
            Audio bytes if output_file is None, otherwise path to saved file
        """
        try:
            # Prepare parameters
            params = {
                'model': kwargs.get('model', self.model),
                'voice': kwargs.get('voice', self.voice),
                'input': text
            }
            
            # Add optional parameters
            if 'speed' in kwargs:
                params['speed'] = kwargs['speed']  # 0.25 to 4.0
            if 'response_format' in kwargs:
                params['response_format'] = kwargs['response_format']  # mp3, opus, aac, flac
            
            # Make API call
            response = openai.audio.speech.create(**params)
            
            # Handle response
            audio_content = response.content
            
            if output_file:
                # Save to file
                output_path = Path(output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_path, 'wb') as f:
                    f.write(audio_content)
                
                return str(output_path)
            else:
                # Return bytes
                return audio_content
                
        except Exception as e:
            raise RuntimeError(f"OpenAI TTS synthesis failed: {str(e)}")


class YemotOpenAITTS(OpenAITTS):
    """Specialized OpenAI TTS for Yemot HaMashiach with Hebrew optimizations"""
    
    def __init__(self, api_key: str = None, voice: str = "nova", **kwargs):
        """
        Initialize with Hebrew-friendly settings
        Nova voice works well with Hebrew
        """
        super().__init__(api_key=api_key, voice=voice, **kwargs)
    
    def synthesize_hebrew(self, text: str, output_file: Union[str, Path] = None, **kwargs) -> Union[bytes, str]:
        """
        Synthesize Hebrew text with optimized settings
        """
        hebrew_kwargs = {
            'voice': kwargs.get('voice', 'nova'),  # Nova works well with Hebrew
            'speed': kwargs.get('speed', 1.0),     # Normal speed
            'response_format': kwargs.get('response_format', 'mp3'),
            **kwargs
        }
        
        return self.synthesize(text, output_file, **hebrew_kwargs)
    
    def create_yemot_greeting(self, name: str = None, output_file: str = None) -> Union[bytes, str]:
        """
        Create a standard Yemot greeting
        """
        if name:
            greeting = f"שלום וברכה {name}. ברוכים הבאים למערכת ימות המשיח."
        else:
            greeting = "שלום וברכה. ברוכים הבאים למערכת ימות המשיח."
        
        return self.synthesize_hebrew(greeting, output_file)
    
    def create_yemot_menu(self, options: list, output_file: str = None) -> Union[bytes, str]:
        """
        Create a menu announcement for Yemot system
        
        Args:
            options: List of menu options
            output_file: Optional output file
        """
        menu_text = "אנא בחרו מהאפשרויות הבאות: "
        
        for i, option in enumerate(options, 1):
            menu_text += f"לחצו {i} עבור {option}. "
        
        menu_text += "תודה רבה."
        
        return self.synthesize_hebrew(menu_text, output_file)