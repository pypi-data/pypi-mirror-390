"""
Azure Cognitive Services Text-to-Speech provider for Yemot HaMashiach systems
"""
from typing import Union
from pathlib import Path
from ..base import TTSProvider

try:
    import azure.cognitiveservices.speech as speechsdk
    HAS_AZURE = True
except ImportError:
    HAS_AZURE = False


class AzureTTS(TTSProvider):
    """Azure Cognitive Services Text-to-Speech provider"""
    
    def __init__(self, subscription_key: str = None, region: str = "eastus", 
                 voice_name: str = "he-IL-AvigailNeural", **kwargs):
        """
        Initialize Azure TTS provider
        
        Args:
            subscription_key: Azure Cognitive Services subscription key
            region: Azure region (eastus, westus2, etc.)
            voice_name: Voice to use (he-IL-AvigailNeural for Hebrew female)
            **kwargs: Additional configuration
        """
        if not HAS_AZURE:
            raise ImportError("azure-cognitiveservices-speech package is required. Install with: pip install azure-cognitiveservices-speech")
        
        super().__init__(
            subscription_key=subscription_key,
            region=region,
            voice_name=voice_name,
            **kwargs
        )
        
        if not subscription_key:
            raise ValueError("Azure subscription key is required")
        
        # Initialize Azure speech config
        self.speech_config = speechsdk.SpeechConfig(
            subscription=subscription_key,
            region=region
        )
        self.speech_config.speech_synthesis_voice_name = voice_name
        self.voice_name = voice_name
    
    def synthesize(self, text: str, output_file: Union[str, Path] = None, **kwargs) -> Union[bytes, str]:
        """
        Synthesize text using Azure TTS
        
        Args:
            text: Text to convert to speech
            output_file: Optional path to save audio file
            **kwargs: Additional parameters
            
        Returns:
            Audio bytes if output_file is None, otherwise path to saved file
        """
        try:
            # Set voice if provided
            voice_name = kwargs.get('voice_name', self.voice_name)
            self.speech_config.speech_synthesis_voice_name = voice_name
            
            # Set output format if provided
            if 'output_format' in kwargs:
                format_map = {
                    'wav': speechsdk.SpeechSynthesisOutputFormat.Riff16Khz16BitMonoPcm,
                    'mp3': speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3,
                    'ogg': speechsdk.SpeechSynthesisOutputFormat.Ogg16Khz16BitMonoOpus,
                }
                format_id = format_map.get(kwargs['output_format'].lower())
                if format_id:
                    self.speech_config.set_speech_synthesis_output_format(format_id)
            
            if output_file:
                # Synthesize to file
                output_path = Path(output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                audio_config = speechsdk.audio.AudioOutputConfig(filename=str(output_path))
                synthesizer = speechsdk.SpeechSynthesizer(
                    speech_config=self.speech_config,
                    audio_config=audio_config
                )
                
                result = synthesizer.speak_text_async(text).get()
                
                if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                    return str(output_path)
                else:
                    raise RuntimeError(f"Azure TTS failed: {result.reason}")
            else:
                # Synthesize to bytes
                synthesizer = speechsdk.SpeechSynthesizer(
                    speech_config=self.speech_config,
                    audio_config=None  # Use default
                )
                
                result = synthesizer.speak_text_async(text).get()
                
                if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                    return result.audio_data
                else:
                    raise RuntimeError(f"Azure TTS failed: {result.reason}")
                    
        except Exception as e:
            raise RuntimeError(f"Azure TTS synthesis failed: {str(e)}")
    
    def synthesize_ssml(self, ssml: str, output_file: Union[str, Path] = None, **kwargs) -> Union[bytes, str]:
        """
        Synthesize SSML text using Azure TTS
        
        Args:
            ssml: SSML formatted text
            output_file: Optional path to save audio file
            **kwargs: Additional parameters
            
        Returns:
            Audio bytes if output_file is None, otherwise path to saved file
        """
        try:
            if output_file:
                output_path = Path(output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                audio_config = speechsdk.audio.AudioOutputConfig(filename=str(output_path))
                synthesizer = speechsdk.SpeechSynthesizer(
                    speech_config=self.speech_config,
                    audio_config=audio_config
                )
                
                result = synthesizer.speak_ssml_async(ssml).get()
                
                if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                    return str(output_path)
                else:
                    raise RuntimeError(f"Azure SSML TTS failed: {result.reason}")
            else:
                synthesizer = speechsdk.SpeechSynthesizer(
                    speech_config=self.speech_config,
                    audio_config=None
                )
                
                result = synthesizer.speak_ssml_async(ssml).get()
                
                if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                    return result.audio_data
                else:
                    raise RuntimeError(f"Azure SSML TTS failed: {result.reason}")
                    
        except Exception as e:
            raise RuntimeError(f"Azure SSML TTS synthesis failed: {str(e)}")


class YemotAzureTTS(AzureTTS):
    """Specialized Azure TTS for Yemot HaMashiach with Hebrew optimizations"""
    
    # Hebrew voices available in Azure
    HEBREW_VOICES = {
        'female_neural': 'he-IL-AvigailNeural',
        'male_neural': 'he-IL-HilaNeural',
        'female_standard': 'he-IL-Asaf',
    }
    
    def __init__(self, subscription_key: str = None, region: str = "eastus", 
                 voice_type: str = "female_neural", **kwargs):
        """
        Initialize with Hebrew voice
        
        Args:
            voice_type: Type of Hebrew voice (female_neural, male_neural, female_standard)
        """
        voice_name = self.HEBREW_VOICES.get(voice_type, 'he-IL-AvigailNeural')
        super().__init__(
            subscription_key=subscription_key,
            region=region,
            voice_name=voice_name,
            **kwargs
        )
    
    def synthesize_hebrew(self, text: str, output_file: Union[str, Path] = None, **kwargs) -> Union[bytes, str]:
        """
        Synthesize Hebrew text with optimized settings
        """
        return self.synthesize(text, output_file, **kwargs)
    
    def create_yemot_ssml(self, text: str, rate: str = "medium", pitch: str = "medium", 
                         volume: str = "default") -> str:
        """
        Create SSML for Yemot messages with Hebrew settings
        
        Args:
            text: Text to speak
            rate: Speech rate (x-slow, slow, medium, fast, x-fast)
            pitch: Speech pitch (x-low, low, medium, high, x-high)
            volume: Speech volume (silent, x-soft, soft, medium, loud, x-loud, default)
        """
        ssml = f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="he-IL">
    <voice name="{self.voice_name}">
        <prosody rate="{rate}" pitch="{pitch}" volume="{volume}">
            {text}
        </prosody>
    </voice>
</speak>'''
        return ssml
    
    def create_yemot_menu_ssml(self, options: dict, title: str = "תפריט ראשי") -> str:
        """
        Create SSML for Yemot menu with pauses and emphasis
        """
        ssml_parts = [
            f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="he-IL">',
            f'<voice name="{self.voice_name}">',
            f'<emphasis level="strong">{title}</emphasis>',
            '<break time="500ms"/>',
            'אנא בחרו מהאפשרויות הבאות:',
            '<break time="300ms"/>'
        ]
        
        for key, description in options.items():
            ssml_parts.append(f'לחצו <emphasis level="moderate">{key}</emphasis> עבור {description}.')
            ssml_parts.append('<break time="200ms"/>')
        
        ssml_parts.extend([
            '<break time="500ms"/>',
            'תודה רבה.',
            '</voice>',
            '</speak>'
        ])
        
        return ''.join(ssml_parts)
    
    def synthesize_yemot_menu(self, options: dict, title: str = "תפריט ראשי", 
                             output_file: Union[str, Path] = None, **kwargs) -> Union[bytes, str]:
        """
        Synthesize a Yemot menu with proper pauses and emphasis
        """
        ssml = self.create_yemot_menu_ssml(options, title)
        return self.synthesize_ssml(ssml, output_file, **kwargs)