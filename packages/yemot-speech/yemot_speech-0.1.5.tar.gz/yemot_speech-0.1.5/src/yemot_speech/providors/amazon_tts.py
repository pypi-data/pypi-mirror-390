"""
Amazon Polly Text-to-Speech provider for Yemot HaMashiach systems
"""
from typing import Union
from pathlib import Path
from ..base import TTSProvider

try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False


class AmazonTTS(TTSProvider):
    """Amazon Polly Text-to-Speech provider"""
    
    def __init__(self, aws_access_key_id: str = None, aws_secret_access_key: str = None, 
                 region_name: str = 'us-east-1', voice_id: str = 'Joanna', **kwargs):
        """
        Initialize Amazon Polly TTS provider
        
        Args:
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
            region_name: AWS region (default: us-east-1)
            voice_id: Voice to use (Joanna, Matthew, etc.)
            **kwargs: Additional configuration
        """
        if not HAS_BOTO3:
            raise ImportError("boto3 package is required. Install with: pip install boto3")
        
        super().__init__(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
            voice_id=voice_id,
            **kwargs
        )
        
        # Initialize AWS client
        session_kwargs = {'region_name': region_name}
        if aws_access_key_id and aws_secret_access_key:
            session_kwargs.update({
                'aws_access_key_id': aws_access_key_id,
                'aws_secret_access_key': aws_secret_access_key
            })
        
        session = boto3.Session(**session_kwargs)
        self.polly_client = session.client('polly')
        self.voice_id = voice_id
    
    def synthesize(self, text: str, output_file: Union[str, Path] = None, **kwargs) -> Union[bytes, str]:
        """
        Synthesize text using Amazon Polly
        
        Args:
            text: Text to convert to speech
            output_file: Optional path to save audio file
            **kwargs: Additional parameters
            
        Returns:
            Audio bytes if output_file is None, otherwise path to saved file
        """
        try:
            # Prepare parameters
            params = {
                'Text': text,
                'OutputFormat': kwargs.get('output_format', 'mp3'),
                'VoiceId': kwargs.get('voice_id', self.voice_id),
                'Engine': kwargs.get('engine', 'standard'),  # standard or neural
            }
            
            # Add optional parameters
            if 'language_code' in kwargs:
                params['LanguageCode'] = kwargs['language_code']
            if 'lexicon_names' in kwargs:
                params['LexiconNames'] = kwargs['lexicon_names']
            if 'speech_mark_types' in kwargs:
                params['SpeechMarkTypes'] = kwargs['speech_mark_types']
            if 'sample_rate' in kwargs:
                params['SampleRate'] = str(kwargs['sample_rate'])
            
            # Make API call
            response = self.polly_client.synthesize_speech(**params)
            
            # Get audio stream
            audio_stream = response['AudioStream']
            audio_content = audio_stream.read()
            
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
                
        except (BotoCoreError, ClientError) as e:
            raise RuntimeError(f"Amazon Polly synthesis failed: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Amazon TTS error: {str(e)}")
    
    def get_available_voices(self, language_code: str = None) -> list:
        """Get available voices from Amazon Polly"""
        try:
            params = {}
            if language_code:
                params['LanguageCode'] = language_code
            
            response = self.polly_client.describe_voices(**params)
            return response['Voices']
        except Exception as e:
            raise RuntimeError(f"Failed to get voices: {str(e)}")


class YemotAmazonTTS(AmazonTTS):
    """Specialized Amazon TTS for Yemot HaMashiach with Hebrew optimizations"""
    
    # Hebrew voices in Amazon Polly (if available)
    HEBREW_VOICES = ['Ayelet']  # Add more as they become available
    
    def __init__(self, aws_access_key_id: str = None, aws_secret_access_key: str = None, 
                 voice_id: str = 'Ayelet', **kwargs):
        """Initialize with Hebrew voice if available"""
        super().__init__(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            voice_id=voice_id,
            **kwargs
        )
    
    def synthesize_hebrew(self, text: str, output_file: Union[str, Path] = None, **kwargs) -> Union[bytes, str]:
        """
        Synthesize Hebrew text with optimized settings
        """
        hebrew_kwargs = {
            'voice_id': kwargs.get('voice_id', 'Ayelet'),
            'language_code': kwargs.get('language_code', 'he-IL'),
            'engine': kwargs.get('engine', 'neural'),  # Use neural if available
            'output_format': kwargs.get('output_format', 'mp3'),
            **kwargs
        }
        
        return self.synthesize(text, output_file, **hebrew_kwargs)
    
    def create_yemot_announcement(self, message: str, output_file: str = None) -> Union[bytes, str]:
        """
        Create a Yemot-style announcement
        """
        full_message = f"הודעה חשובה: {message}. תודה רבה."
        return self.synthesize_hebrew(full_message, output_file)
    
    def create_phone_menu(self, options: dict, output_file: str = None) -> Union[bytes, str]:
        """
        Create a phone menu for Yemot system
        
        Args:
            options: Dict of {key: description} for menu options
            output_file: Optional output file
        """
        menu_text = "בחרו מהאפשרויות הבאות: "
        
        for key, description in options.items():
            menu_text += f"לחצו {key} עבור {description}. "
        
        menu_text += "אנא בחרו כעת."
        
        return self.synthesize_hebrew(menu_text, output_file, 
                                    engine='neural',  # Better quality for menus
                                    sample_rate=8000)  # Phone quality