#!/usr/bin/env python3
"""
דוגמאות בסיסיות ל-STT (Speech-to-Text)
Basic STT (Speech-to-Text) examples
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from yemot_speech import STT, transcribe


def openai_whisper_example():
    """דוגמה לשימוש ב-OpenAI Whisper"""
    print("🎤 OpenAI Whisper Example")
    
    # יצירת אובייקט STT עם ספק OpenAI
    stt = STT(provider='openai', api_key='your-openai-api-key')
    
    # המרת קובץ שמע לטקסט
    audio_file = 'path/to/audio.wav'
    text = stt.transcribe(audio_file, language='he')  # עברית
    print(f"📝 Transcribed text: {text}")
    
    # המרת bytes לטקסט
    with open(audio_file, 'rb') as f:
        audio_bytes = f.read()
    text = stt.transcribe_bytes(audio_bytes, language='he')
    print(f"📝 From bytes: {text}")


def google_cloud_example():
    """דוגמה לשימוש ב-Google Cloud Speech"""
    print("🎤 Google Cloud Speech Example")
    
    # יצירת אובייקט STT עם ספק Google
    stt = STT(
        provider='google',
        credentials_path='path/to/google-credentials.json',
        language_code='he-IL'
    )
    
    # המרת קובץ שמע לטקסט
    audio_file = 'path/to/audio.wav'
    text = stt.transcribe(audio_file)
    print(f"📝 Google transcribed: {text}")


def local_whisper_example():
    """דוגמה לשימוש במודל מקומי (Whisper)"""
    print("🎤 Local Whisper Example")
    
    # יצירת אובייקט STT עם מודל מקומי
    stt = STT(provider='local', engine='whisper', model_name='medium')
    
    # המרת קובץ שמע לטקסט
    audio_file = 'path/to/audio.wav'
    text = stt.transcribe(audio_file, language='hebrew')
    print(f"📝 Local Whisper: {text}")


def quick_transcribe_example():
    """דוגמה לשימוש בפונקציית transcribe המהירה"""
    print("⚡ Quick Transcribe Example")
    
    # המרה מהירה ללא יצירת אובייקט
    text = transcribe(
        'path/to/audio.wav',
        provider='openai',
        api_key='your-key',
        language='he'
    )
    print(f"⚡ Quick transcribe: {text}")


def provider_info_example():
    """דוגמה לקבלת מידע על ספקים"""
    print("📋 Provider Information")
    
    try:
        # ניסיון עם ספק דמו
        stt = STT()  # ספק ברירת מחדל
        
        info = stt.get_provider_info()
        print(f"ℹ️ Provider info: {info}")
        
        # רשימת ספקים זמינים
        providers = stt.get_available_providers()
        print(f"📋 Available providers: {providers}")
        
    except Exception as e:
        print(f"⚠️ Info gathering failed: {e}")
        print("💡 This is normal without API keys - examples work with real providers")


if __name__ == "__main__":
    print("🎯 דוגמאות STT בסיסיות - Basic STT Examples")
    print("=" * 50)
    
    try:
        # הרץ דוגמאות במצב דמו (ללא API keys אמיתיים)
        provider_info_example()
        
        print("\n💡 לשימוש אמיתי:")
        print("  1. התקן: pip install yemot-speech[openai]")
        print("  2. עדכן API keys בקוד")
        print("  3. הכן קבצי שמע לבדיקה")
        print("  4. הרץ את הפונקציות עם נתונים אמיתיים")
        
    except Exception as e:
        print(f"❌ Error: {e}")