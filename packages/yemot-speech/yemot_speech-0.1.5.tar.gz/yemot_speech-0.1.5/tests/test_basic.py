"""
Basic test for yemot-speech STT functionality
"""
# import pytest  # Will use manual testing instead
import sys
import os

# Add src to path - go up one level from tests/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from yemot_speech import STT
from yemot_speech.base import STTProvider


def test_stt_import():
    """Test that STT can be imported"""
    assert STT is not None


def test_stt_provider_registry():
    """Test provider registration system"""
    # Test getting available providers (should be empty initially)
    providers = STT.get_available_providers()
    assert isinstance(providers, list)
    
    # Test manual provider registration
    class DummySTT(STTProvider):
        def transcribe(self, audio_file, **kwargs):
            return "dummy transcription"
        
        def transcribe_bytes(self, audio_bytes, **kwargs):
            return "dummy transcription from bytes"
    
    STT.register_provider('dummy', DummySTT)
    assert 'dummy' in STT.get_available_providers()


def test_stt_initialization_with_dummy():
    """Test STT initialization with dummy provider"""
    
    # Register dummy provider
    class DummySTT(STTProvider):
        def transcribe(self, audio_file, **kwargs):
            return "test transcription"
        
        def transcribe_bytes(self, audio_bytes, **kwargs):
            return "test transcription from bytes"
    
    STT.register_provider('test', DummySTT)
    
    # Test initialization
    stt = STT(provider='test')
    assert stt.provider_name == 'test'
    assert isinstance(stt.provider, DummySTT)


def test_stt_transcribe_with_dummy():
    """Test actual transcription with dummy provider"""
    
    class DummySTT(STTProvider):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.test_param = kwargs.get('test_param', 'default')
        
        def transcribe(self, audio_file, **kwargs):
            return f"transcribed: {audio_file} with {self.test_param}"
        
        def transcribe_bytes(self, audio_bytes, **kwargs):
            return f"transcribed bytes: {len(audio_bytes)} bytes with {self.test_param}"
    
    STT.register_provider('test_dummy', DummySTT)
    
    # Test with configuration
    stt = STT(provider='test_dummy', test_param='configured')
    
    # Test file transcription
    result = stt.transcribe('test.wav')
    assert 'test.wav' in result
    assert 'configured' in result
    
    # Test bytes transcription
    test_bytes = b'fake audio data'
    result = stt.transcribe_bytes(test_bytes)
    assert str(len(test_bytes)) in result
    assert 'configured' in result


def test_stt_provider_info():
    """Test provider info functionality"""
    
    class InfoSTT(STTProvider):
        def transcribe(self, audio_file, **kwargs):
            return "info test"
        
        def transcribe_bytes(self, audio_bytes, **kwargs):
            return "info test bytes"
    
    STT.register_provider('info_test', InfoSTT)
    
    stt = STT(provider='info_test', test_config='test_value')
    info = stt.get_provider_info()
    
    assert info['name'] == 'info_test'
    assert 'InfoSTT' in info['class']
    assert isinstance(info['config'], dict)


def test_invalid_provider():
    """Test error handling for invalid provider"""
    try:
        STT(provider='nonexistent')
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Provider 'nonexistent' not found" in str(e)


def test_quick_transcribe_function():
    """Test the quick transcribe function"""
    from yemot_speech import transcribe
    
    # Register dummy for testing
    class QuickSTT(STTProvider):
        def transcribe(self, audio_file, **kwargs):
            return f"quick: {audio_file}"
        
        def transcribe_bytes(self, audio_bytes, **kwargs):
            return f"quick bytes: {len(audio_bytes)}"
    
    STT.register_provider('quick_test', QuickSTT)
    
    result = transcribe('test_file.wav', provider='quick_test')
    assert 'quick: test_file.wav' == result


if __name__ == "__main__":
    # Run tests manually if pytest is not available
    print("Running basic tests...")
    
    try:
        test_stt_import()
        print("✅ Import test passed")
        
        test_stt_provider_registry()
        print("✅ Provider registry test passed")
        
        test_stt_initialization_with_dummy()
        print("✅ Initialization test passed")
        
        test_stt_transcribe_with_dummy()
        print("✅ Transcription test passed")
        
        test_stt_provider_info()
        print("✅ Provider info test passed")
        
        test_quick_transcribe_function()
        print("✅ Quick transcribe test passed")
        
        print("🎉 All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()