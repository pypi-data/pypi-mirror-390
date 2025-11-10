"""
Google Text-to-Speech (gTTS) provider for Yemot HaMashiach systems
"""
from typing import Union
from pathlib import Path
import tempfile
import io
from ..base import TTSProvider

try:
    from gtts import gTTS
    HAS_GTTS = True
except ImportError:
    HAS_GTTS = False

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False


class GoogleTTS(TTSProvider):
    """Google Text-to-Speech provider using gTTS"""
    
    def __init__(self, language: str = 'he', **kwargs):
        """
        Initialize Google TTS provider
        
        Args:
            language: Language code (he=Hebrew, en=English, etc.)
            **kwargs: Additional configuration
        """
        if not HAS_GTTS:
            raise ImportError("gTTS package is required. Install with: pip install gTTS")
        
        super().__init__(language=language, **kwargs)
        self.language = language
    
    def synthesize(self, text: str, output_file: Union[str, Path] = None, **kwargs) -> Union[bytes, str]:
        """
        Convert text to speech using Google TTS
        
        Args:
            text: Text to convert to speech
            output_file: Optional path to save audio file
            **kwargs: Additional parameters
            
        Returns:
            Audio bytes if output_file is None, otherwise path to saved file
        """
        try:
            # Create gTTS object
            tts = gTTS(
                text=text,
                lang=kwargs.get('language', self.language),
                slow=kwargs.get('slow', False),
                tld=kwargs.get('tld', 'com')  # Top-level domain
            )
            
            if output_file:
                # Save to file
                output_path = Path(output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                tts.save(str(output_path))
                return str(output_path)
            else:
                # Return bytes
                audio_buffer = io.BytesIO()
                tts.write_to_fp(audio_buffer)
                audio_buffer.seek(0)
                return audio_buffer.read()
                
        except Exception as e:
            raise RuntimeError(f"Google TTS synthesis failed: {str(e)}")
    
    def play_audio(self, audio_bytes: bytes):
        """Play audio bytes directly (requires pygame)"""
        if not HAS_PYGAME:
            raise ImportError("pygame package is required for audio playback. Install with: pip install pygame")
        
        try:
            # Initialize pygame mixer
            pygame.mixer.init()
            
            # Create temporary file for pygame
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_file_path = tmp_file.name
            
            try:
                # Play the audio
                pygame.mixer.music.load(tmp_file_path)
                pygame.mixer.music.play()
                
                # Wait for playback to finish
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)
            finally:
                # Clean up temp file
                import os
                try:
                    os.unlink(tmp_file_path)
                except:
                    pass  # Ignore cleanup errors
                
        except Exception as e:
            raise RuntimeError(f"Audio playback failed: {str(e)}")


class YemotGoogleTTS(GoogleTTS):
    """Specialized Google TTS for Yemot HaMashiach with Hebrew optimizations"""
    
    def __init__(self, **kwargs):
        """Initialize with Hebrew as default"""
        super().__init__(language='he', **kwargs)
    
    def synthesize_hebrew(self, text: str, output_file: Union[str, Path] = None, **kwargs) -> Union[bytes, str]:
        """
        Synthesize Hebrew text with optimized settings
        """
        hebrew_kwargs = {
            'language': 'he',
            'slow': kwargs.get('slow', False),
            'tld': kwargs.get('tld', 'co.il'),  # Israeli Google for better Hebrew
            **kwargs
        }
        return self.synthesize(text, output_file, **hebrew_kwargs)
    
    def create_yemot_message(self, message: str, output_file: str = None) -> Union[bytes, str]:
        """
        Create a typical Yemot message with standard greeting and closing
        """
        full_message = f"שלום וברכה. {message}. תודה רבה וכל טוב."
        return self.synthesize_hebrew(full_message, output_file)
    
    def create_yemot_menu(self, options: dict, title: str = "תפריט ראשי", 
                         output_file: str = None) -> Union[bytes, str]:
        """
        Create a menu announcement for Yemot system
        
        Args:
            options: Dict of {key: description} for menu options
            title: Menu title
            output_file: Optional output file
        """
        menu_parts = [f"{title}."]
        menu_parts.append("אנא בחרו מהאפשרויות הבאות:")
        
        for key, description in options.items():
            menu_parts.append(f"לחצו {key} עבור {description}.")
        
        menu_parts.append("תודה רבה.")
        
        menu_text = " ".join(menu_parts)
        
        return self.synthesize_hebrew(menu_text, output_file, slow=True)  # Slower for menus
    
    def create_yemot_greeting(self, name: str = None, time_of_day: str = None, 
                             output_file: str = None) -> Union[bytes, str]:
        """
        Create personalized Yemot greeting
        
        Args:
            name: Optional person's name
            time_of_day: Optional time greeting (בוקר טוב, ערב טוב, etc.)
            output_file: Optional output file
        """
        greeting_parts = []
        
        if time_of_day:
            greeting_parts.append(time_of_day)
        
        greeting_parts.append("שלום וברכה")
        
        if name:
            greeting_parts.append(f"וברוכים הבאים {name}")
        else:
            greeting_parts.append("וברוכים הבאים")
        
        greeting_parts.append("למערכת ימות המשיח.")
        
        greeting_text = " ".join(greeting_parts)
        
        return self.synthesize_hebrew(greeting_text, output_file)
