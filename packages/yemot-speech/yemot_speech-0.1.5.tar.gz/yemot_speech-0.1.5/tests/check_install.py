#!/usr/bin/env python3
"""
בדיקת התקנה מהירה של yemot-speech
Quick installation check for yemot-speech
"""
import sys
import os

# Add src to path - go up one level from tests/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def check_installation():
    """בדיקה שהתקנה עבדה / Check if installation worked"""
    print("🔍 בודק התקנה / Checking installation...")
    
    try:
        # Basic import test
        from yemot_speech import STT, TTS, transcribe, synthesize, speak
        print("✅ Basic import successful")
        
        # Check available providers
        stt_providers = STT.get_available_providers()
        tts_providers = TTS.get_available_providers()
        print(f"📋 Available STT providers: {stt_providers}")
        print(f"📋 Available TTS providers: {tts_providers}")
        
        # Check optional dependencies
        check_optional_dependencies()
        
        print("\n🎉 התקנה הושלמה בהצלחה!")
        print("🎉 Installation completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Installation check failed: {e}")
        return False


def check_optional_dependencies():
    """בדיקת תלויות אופציונליות / Check optional dependencies"""
    print("\n🔍 בודק תלויות אופציונליות / Checking optional dependencies:")
    
    # Check OpenAI
    try:
        import openai
        print("✅ OpenAI package available")
        has_openai = True
    except ImportError:
        print("❌ OpenAI package not installed (install with: pip install yemot-speech[openai])")
        has_openai = False
    
    # Check Google Cloud Speech
    try:
        from google.cloud import speech
        print("✅ Google Cloud Speech package available")
        has_google = True
    except ImportError:
        print("❌ Google Cloud Speech not installed (install with: pip install yemot-speech[google])")
        has_google = False
    
    # Check Amazon/Boto3
    try:
        import boto3
        print("✅ Boto3 (Amazon) package available")
        has_amazon = True
    except ImportError:
        print("❌ Boto3 not installed (install with: pip install yemot-speech[amazon])")
        has_amazon = False
    
    # Check local/Whisper
    try:
        import whisper
        print("✅ Whisper package available")
        has_whisper = True
    except ImportError:
        print("❌ Whisper not installed (install with: pip install yemot-speech[local])")
        has_whisper = False
    
    # Check SpeechRecognition
    try:
        import speech_recognition as sr
        print("✅ SpeechRecognition package available")
        has_sr = True
    except ImportError:
        print("❌ SpeechRecognition not installed (install with: pip install yemot-speech[local])")
        has_sr = False
    
    # Check gTTS (for TTS)
    try:
        from gtts import gTTS
        print("✅ gTTS package available")
        has_gtts = True
    except ImportError:
        print("❌ gTTS not installed (install with: pip install yemot-speech[tts])")
        has_gtts = False
    
    # Check pygame (for audio playback)
    try:
        import pygame
        print("✅ Pygame package available")
        has_pygame = True
    except ImportError:
        print("❌ Pygame not installed (install with: pip install yemot-speech[tts])")
        has_pygame = False
    
    # Check Azure TTS
    try:
        import azure.cognitiveservices.speech as speechsdk
        print("✅ Azure Speech Services available")
        has_azure = True
    except ImportError:
        print("❌ Azure Speech not installed (install with: pip install yemot-speech[azure])")
        has_azure = False
    
    # Recommendations
    print("\n💡 המלצות / Recommendations:")
    
    if not any([has_openai, has_google, has_amazon, has_whisper]):
        print("⚠️  לא נמצאו ספקי STT! התקן לפחות ספק אחד:")
        print("⚠️  No STT providers found! Install at least one provider:")
        print("   pip install yemot-speech[openai]  # מומלץ / Recommended")
        print("   pip install yemot-speech[local]   # ללא API keys / No API keys needed")
    
    if not any([has_gtts, has_openai, has_azure, has_amazon]):
        print("⚠️  לא נמצאו ספקי TTS! התקן לפחות ספק אחד:")
        print("⚠️  No TTS providers found! Install at least one provider:")
        print("   pip install yemot-speech[tts]     # Google TTS - מומלץ / Recommended")
        print("   pip install yemot-speech[openai]  # OpenAI TTS - איכות גבוהה / High quality")
    
    print("\n🌟 המלצות שימוש / Usage Recommendations:")
    
    if has_openai:
        print("🌟 OpenAI זמין - מצוין ל-STT ו-TTS בעברית!")
        print("🌟 OpenAI available - excellent for Hebrew STT and TTS!")
    
    if has_gtts:
        print("🔊 gTTS זמין - מצוין ל-TTS חינמי!")
        print("🔊 gTTS available - great for free TTS!")
    
    if has_whisper:
        print("🔒 Whisper מקומי זמין - עובד ללא אינטרנט!")
        print("🔒 Local Whisper available - works offline!")
    
    if has_azure:
        print("🎯 Azure זמין - קולות עבריים איכותיים!")
        print("🎯 Azure available - high-quality Hebrew voices!")


def test_basic_functionality():
    """בדיקה בסיסית של הפונקציונליות / Basic functionality test"""
    print("\n🧪 בודק פונקציונליות בסיסית / Testing basic functionality...")
    
    try:
        from yemot_speech import STT, TTS
        from yemot_speech.base import STTProvider, TTSProvider
        
        # Create test providers
        class TestSTT(STTProvider):
            def transcribe(self, audio_file, **kwargs):
                return f"Test transcription of {audio_file}"
            
            def transcribe_bytes(self, audio_bytes, **kwargs):
                return f"Test transcription of {len(audio_bytes)} bytes"
        
        class TestTTS(TTSProvider):
            def synthesize(self, text, output_file=None, **kwargs):
                fake_audio = f"AUDIO:{text}".encode('utf-8')
                if output_file:
                    with open(output_file, 'wb') as f:
                        f.write(fake_audio)
                    return output_file
                return fake_audio
        
        # Register and test STT
        STT.register_provider('test', TestSTT)
        stt = STT(provider='test')
        
        result = stt.transcribe('test.wav')
        assert 'test.wav' in result
        
        result = stt.transcribe_bytes(b'fake audio')
        assert 'bytes' in result
        
        # Register and test TTS
        TTS.register_provider('test', TestTTS)
        tts = TTS(provider='test')
        
        audio_bytes = tts.synthesize('שלום')
        assert b'AUDIO:' in audio_bytes
        
        # Test file saving
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            result_path = tts.save_audio('test message', tmp_path)
            assert result_path == tmp_path
            
            # Verify file was created
            with open(tmp_path, 'rb') as f:
                content = f.read()
                assert b'AUDIO:test message' == content
                
        finally:
            # Clean up
            import os
            try:
                os.unlink(tmp_path)
            except:
                pass
        
        print("✅ Basic STT and TTS functionality tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False


def main():
    """הרצת כל הבדיקות / Run all checks"""
    print("🎯 בדיקת התקנה של yemot-speech")
    print("🎯 yemot-speech Installation Check")
    print("=" * 50)
    
    success = True
    
    # Check installation
    if not check_installation():
        success = False
    
    # Test basic functionality
    if not test_basic_functionality():
        success = False
    
    print("\n" + "=" * 50)
    
    if success:
        print("🎉 כל הבדיקות עברו בהצלחה!")
        print("🎉 All checks passed successfully!")
        print("\n📚 כעת אתה יכול להשתמש ב-yemot-speech:")
        print("📚 You can now use yemot-speech:")
        print("   from yemot_speech import STT")
        print("   stt = STT(provider='openai', api_key='your-key')")
        print("   text = stt.transcribe('audio.wav', language='he')")
    else:
        print("❌ יש בעיות עם ההתקנה")
        print("❌ There are issues with the installation")
        print("\n🔧 פתרונות אפשריים:")
        print("🔧 Possible solutions:")
        print("   pip install yemot-speech[all] --upgrade")
        print("   pip install --upgrade pip")


if __name__ == "__main__":
    main()