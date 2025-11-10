"""
Local Speech-to-Text provider for Yemot HaMashiach systems
Uses local models like Whisper or other offline solutions
"""
from typing import Union, BinaryIO
from pathlib import Path
from ..base import STTProvider

try:
    import whisper
    HAS_WHISPER = True
except ImportError:
    HAS_WHISPER = False

try:
    import speech_recognition as sr
    HAS_SPEECH_RECOGNITION = True
except ImportError:
    HAS_SPEECH_RECOGNITION = False


class LocalSTT(STTProvider):
    """Local Speech-to-Text provider using Whisper or SpeechRecognition"""
    
    def __init__(self, engine: str = "whisper", model_name: str = "base", **kwargs):
        """
        Initialize Local STT provider
        
        Args:
            engine: Engine to use ("whisper", "sphinx", "google_free")
            model_name: Model name for Whisper (tiny, base, small, medium, large)
            **kwargs: Additional configuration
        """
        super().__init__(engine=engine, model_name=model_name, **kwargs)
        
        self.engine = engine.lower()
        self.model_name = model_name
        
        if self.engine == "whisper":
            if not HAS_WHISPER:
                raise ImportError("whisper package is required. Install with: pip install openai-whisper")
            self.model = whisper.load_model(model_name)
        elif self.engine in ["sphinx", "google_free"]:
            if not HAS_SPEECH_RECOGNITION:
                raise ImportError("SpeechRecognition package is required. Install with: pip install SpeechRecognition")
            self.recognizer = sr.Recognizer()
        else:
            raise ValueError(f"Unsupported engine: {engine}")
    
    def transcribe(self, audio_file: Union[str, Path, BinaryIO], **kwargs) -> str:
        """
        Transcribe audio file using local models
        
        Args:
            audio_file: Path to audio file or file-like object
            **kwargs: Additional parameters
            
        Returns:
            Transcribed text
        """
        if self.engine == "whisper":
            return self._transcribe_whisper(audio_file, **kwargs)
        else:
            return self._transcribe_speech_recognition(audio_file, **kwargs)
    
    def transcribe_bytes(self, audio_bytes: bytes, **kwargs) -> str:
        """
        Transcribe audio bytes using local models
        
        Args:
            audio_bytes: Audio data as bytes
            **kwargs: Additional parameters
            
        Returns:
            Transcribed text
        """
        import tempfile
        import os
        
        # Save bytes to temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file_path = tmp_file.name
        
        try:
            return self.transcribe(tmp_file_path, **kwargs)
        finally:
            # Clean up temporary file
            os.unlink(tmp_file_path)
    
    def _transcribe_whisper(self, audio_file, **kwargs):
        """Transcribe using Whisper model"""
        try:
            # Convert file path to string if it's a Path object
            if isinstance(audio_file, Path):
                audio_file = str(audio_file)
            
            # If it's a file-like object, we need to save it temporarily
            if hasattr(audio_file, 'read'):
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                    tmp_file.write(audio_file.read())
                    tmp_file_path = tmp_file.name
                
                try:
                    result = self.model.transcribe(tmp_file_path, **kwargs)
                    return result["text"]
                finally:
                    os.unlink(tmp_file_path)
            else:
                result = self.model.transcribe(audio_file, **kwargs)
                return result["text"]
                
        except Exception as e:
            raise RuntimeError(f"Whisper transcription failed: {str(e)}")
    
    def _transcribe_speech_recognition(self, audio_file, **kwargs):
        """Transcribe using SpeechRecognition library"""
        try:
            with sr.AudioFile(str(audio_file)) as source:
                audio_data = self.recognizer.record(source)
            
            if self.engine == "sphinx":
                return self.recognizer.recognize_sphinx(audio_data, **kwargs)
            elif self.engine == "google_free":
                return self.recognizer.recognize_google(audio_data, language="he-IL", **kwargs)
            
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            raise RuntimeError(f"SpeechRecognition error: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Local transcription failed: {str(e)}")


class YemotLocalSTT(LocalSTT):
    """Specialized Local STT for Yemot HaMashiach with Hebrew optimizations"""
    
    def __init__(self, model_name: str = "medium", **kwargs):
        """Initialize with better model for Hebrew"""
        super().__init__(engine="whisper", model_name=model_name, **kwargs)
    
    def transcribe_hebrew(self, audio_file: Union[str, Path, BinaryIO], **kwargs) -> str:
        """
        Transcribe with Hebrew language specification
        """
        whisper_kwargs = {
            'language': 'hebrew',
            'task': 'transcribe',
            **kwargs
        }
        return self.transcribe(audio_file, **whisper_kwargs)
