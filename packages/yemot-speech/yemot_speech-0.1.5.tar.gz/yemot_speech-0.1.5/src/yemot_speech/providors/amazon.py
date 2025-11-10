"""
Amazon Transcribe Speech-to-Text provider for Yemot HaMashiach systems
"""
from typing import Union, BinaryIO
from pathlib import Path
import json
import time
from ..base import STTProvider

try:
    import boto3
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False


class AmazonSTT(STTProvider):
    """Amazon Transcribe Speech-to-Text provider"""
    
    def __init__(self, aws_access_key_id: str = None, aws_secret_access_key: str = None, 
                 region_name: str = 'us-east-1', **kwargs):
        """
        Initialize Amazon Transcribe STT provider
        
        Args:
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
            region_name: AWS region (default: us-east-1)
            **kwargs: Additional configuration
        """
        if not HAS_BOTO3:
            raise ImportError("boto3 package is required. Install with: pip install boto3")
        
        super().__init__(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
            **kwargs
        )
        
        # Initialize AWS clients
        session_kwargs = {'region_name': region_name}
        if aws_access_key_id and aws_secret_access_key:
            session_kwargs.update({
                'aws_access_key_id': aws_access_key_id,
                'aws_secret_access_key': aws_secret_access_key
            })
        
        session = boto3.Session(**session_kwargs)
        self.transcribe_client = session.client('transcribe')
        self.s3_client = session.client('s3')
        
        # S3 bucket for temporary audio files
        self.bucket_name = kwargs.get('bucket_name', 'yemot-speech-temp')
    
    def transcribe(self, audio_file: Union[str, Path, BinaryIO], **kwargs) -> str:
        """
        Transcribe audio file using Amazon Transcribe
        
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
        Transcribe audio bytes using Amazon Transcribe
        
        Args:
            audio_bytes: Audio data as bytes
            **kwargs: Additional parameters
            
        Returns:
            Transcribed text
        """
        import uuid
        
        try:
            # Generate unique job name
            job_name = f"yemot-speech-{uuid.uuid4().hex[:8]}"
            s3_key = f"audio/{job_name}.wav"
            
            # Upload audio to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=audio_bytes
            )
            
            # Configure transcription job
            job_params = {
                'TranscriptionJobName': job_name,
                'Media': {
                    'MediaFileUri': f's3://{self.bucket_name}/{s3_key}'
                },
                'MediaFormat': kwargs.get('media_format', 'wav'),
                'LanguageCode': kwargs.get('language_code', 'he-IL'),
            }
            
            # Add optional settings
            if kwargs.get('enable_speaker_identification'):
                job_params['Settings'] = {
                    'ShowSpeakerLabels': True,
                    'MaxSpeakerLabels': kwargs.get('max_speakers', 2)
                }
            
            # Start transcription job
            self.transcribe_client.start_transcription_job(**job_params)
            
            # Wait for completion
            max_wait_time = kwargs.get('max_wait_time', 300)  # 5 minutes
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                response = self.transcribe_client.get_transcription_job(
                    TranscriptionJobName=job_name
                )
                
                status = response['TranscriptionJob']['TranscriptionJobStatus']
                
                if status == 'COMPLETED':
                    # Download and parse results
                    transcript_uri = response['TranscriptionJob']['Transcript']['TranscriptFileUri']
                    return self._download_transcript(transcript_uri)
                elif status == 'FAILED':
                    failure_reason = response['TranscriptionJob'].get('FailureReason', 'Unknown error')
                    raise RuntimeError(f"Transcription failed: {failure_reason}")
                
                time.sleep(2)  # Wait 2 seconds before checking again
            
            raise RuntimeError(f"Transcription timed out after {max_wait_time} seconds")
            
        except Exception as e:
            raise RuntimeError(f"Amazon Transcribe error: {str(e)}")
        finally:
            # Cleanup: delete the uploaded file and job
            try:
                self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
                self.transcribe_client.delete_transcription_job(TranscriptionJobName=job_name)
            except:
                pass  # Ignore cleanup errors
    
    def _download_transcript(self, transcript_uri: str) -> str:
        """Download and parse transcript from S3"""
        import urllib.request
        
        with urllib.request.urlopen(transcript_uri) as response:
            transcript_data = json.loads(response.read())
        
        # Extract text from transcript
        transcripts = []
        for result in transcript_data['results']['transcripts']:
            transcripts.append(result['transcript'])
        
        return ' '.join(transcripts)


class YemotAmazonSTT(AmazonSTT):
    """Specialized Amazon STT for Yemot HaMashiach with Hebrew optimizations"""
    
    def __init__(self, aws_access_key_id: str = None, aws_secret_access_key: str = None, 
                 bucket_name: str = None, **kwargs):
        """Initialize with Hebrew-specific settings"""
        super().__init__(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            bucket_name=bucket_name or 'yemot-speech-hebrew',
            **kwargs
        )
    
    def transcribe_yemot_call(self, audio_bytes: bytes, **kwargs) -> str:
        """
        Transcribe Yemot phone call with optimized settings
        """
        call_kwargs = {
            'language_code': 'he-IL',
            'media_format': 'wav',
            'enable_speaker_identification': True,
            'max_speakers': 2,
            **kwargs
        }
        
        return self.transcribe_bytes(audio_bytes, **call_kwargs)
