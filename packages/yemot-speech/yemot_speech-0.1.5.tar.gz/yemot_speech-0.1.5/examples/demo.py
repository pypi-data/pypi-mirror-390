#!/usr/bin/env python3
"""
דוגמה מהירה לשימוש ב-yemot-speech
Quick demo of yemot-speech usage
"""

import sys
import os

# Add src to path - go up one level from examples/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from yemot_speech import STT
from yemot_speech.base import STTProvider


class DemoSTT(STTProvider):
    """ספק דמו להדגמה / Demo STT provider for demonstration"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.demo_language = kwargs.get('language', 'he')
        print(f"🎯 Demo STT initialized with language: {self.demo_language}")
    
    def transcribe(self, audio_file, **kwargs):
        """סימולציה של המרת קובץ שמע / Simulate audio file transcription"""
        print(f"🎵 Transcribing file: {audio_file}")
        
        # Simulate transcription based on file name
        if 'hebrew' in str(audio_file).lower() or 'עברית' in str(audio_file):
            return "שלום עליכם! זוהי דוגמה להמרת דיבור לטקסט בעברית"
        elif 'english' in str(audio_file).lower():
            return "Hello! This is a demo of speech-to-text conversion in English"
        elif 'yemot' in str(audio_file).lower() or 'ימות' in str(audio_file):
            return "ברוכים הבאים למערכת ימות המשיח. איך אוכל לעזור לכם היום?"
        else:
            return f"Demo transcription of {audio_file} - זה טקסט לדוגמה"
    
    def transcribe_bytes(self, audio_bytes, **kwargs):
        """סימולציה של המרת bytes / Simulate bytes transcription"""
        size_mb = len(audio_bytes) / 1024 / 1024
        print(f"🎵 Transcribing {len(audio_bytes)} bytes ({size_mb:.2f}MB)")
        
        if size_mb > 10:
            return "זה קובץ גדול! כנראה הקלטה ארוכה של שיחת טלפון או שיעור"
        elif size_mb > 1:
            return "הקלטה בינונית - אולי הודעה קולית או קטע קצר"
        else:
            return "הקלטה קצרה - כנראה מילה או משפט בודד"


def demo_basic_usage():
    """הדגמה בסיסית / Basic usage demo"""
    print("\n" + "="*50)
    print("🎯 הדגמה בסיסית / Basic Demo")
    print("="*50)
    
    # Register demo provider
    STT.register_provider('demo', DemoSTT)
    
    # Create STT instance
    stt = STT(provider='demo', language='he')
    
    # Demo file transcription
    demo_files = [
        'hebrew_recording.wav',
        'english_audio.mp3',
        'yemot_call.wav',
        'random_audio.m4a'
    ]
    
    for file in demo_files:
        print(f"\n📁 Processing: {file}")
        result = stt.transcribe(file)
        print(f"📝 Result: {result}")
    
    # Demo bytes transcription
    print(f"\n📊 Processing audio bytes...")
    demo_bytes = b"fake audio data" * 100  # Small fake audio
    result = stt.transcribe_bytes(demo_bytes)
    print(f"📝 Result: {result}")
    
    large_bytes = b"fake audio data" * 100000  # Large fake audio  
    result = stt.transcribe_bytes(large_bytes)
    print(f"📝 Result: {result}")


def demo_provider_info():
    """הדגמת מידע על ספקים / Provider info demo"""
    print("\n" + "="*50) 
    print("ℹ️  מידע על ספקים / Provider Information")
    print("="*50)
    
    # Register demo provider if not already registered
    if 'demo' not in STT.get_available_providers():
        STT.register_provider('demo', DemoSTT)
    
    # Show available providers
    providers = STT.get_available_providers()
    print(f"📋 Available providers: {providers}")
    
    # Show provider info
    stt = STT(provider='demo', test_config='demo_value')
    info = stt.get_provider_info()
    print(f"📊 Provider info: {info}")


def demo_error_handling():
    """הדגמת טיפול בשגיאות / Error handling demo"""
    print("\n" + "="*50)
    print("⚠️  טיפול בשגיאות / Error Handling Demo")
    print("="*50)
    
    try:
        # Try to use non-existent provider
        stt = STT(provider='nonexistent')
    except Exception as e:
        print(f"❌ Expected error: {e}")
    
    print("✅ Error handling works correctly!")


def demo_quick_transcribe():
    """הדגמת פונקציית transcribe המהירה / Quick transcribe demo"""
    print("\n" + "="*50)
    print("⚡ המרה מהירה / Quick Transcribe Demo") 
    print("="*50)
    
    from yemot_speech import transcribe
    
    # Register demo provider if needed
    if 'demo' not in STT.get_available_providers():
        STT.register_provider('demo', DemoSTT)
    
    # Quick transcription
    result = transcribe(
        'yemot_message.wav',
        provider='demo',
        language='he'
    )
    print(f"⚡ Quick result: {result}")


def main():
    """הרצת כל הדוגמאות / Run all demos"""
    print("🎉 ברוכים הבאים ל-yemot-speech!")
    print("🎉 Welcome to yemot-speech!")
    print("📚 ספריה להמרת שמע לטקסט עבור מערכות ימות המשיח")
    print("📚 Speech-to-text library for Yemot HaMashiach systems")
    
    try:
        demo_basic_usage()
        demo_provider_info()
        demo_error_handling()
        demo_quick_transcribe()
        
        print("\n" + "="*50)
        print("✅ כל הדוגמאות הסתיימו בהצלחה!")
        print("✅ All demos completed successfully!")
        print("="*50)
        
        print("\n📖 לדוגמאות נוספות ותיעוד מלא, ראה:")
        print("📖 For more examples and full documentation, see:")
        print("   - README.md")
        print("   - examples.py")
        print("   - https://github.com/your-username/yemot-speech")
        
    except Exception as e:
        print(f"\n❌ Error in demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()