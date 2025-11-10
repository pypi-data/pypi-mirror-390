#!/usr/bin/env python3
"""
דוגמאות בסיסיות ל-TTS (Text-to-Speech)
Basic TTS (Text-to-Speech) examples
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from yemot_speech import TTS, synthesize, speak


def gtts_example():
    """דוגמה ל-Google TTS (gTTS)"""
    print("🔊 Google TTS Example")
    
    # יצירת אובייקט TTS עם Google TTS
    tts = TTS(provider='gtts', language='he')
    
    # המרת טקסט לשמע וקבלת bytes
    text = 'שלום עליכם! ברוכים הבאים למערכת ימות המשיח'
    audio_bytes = tts.synthesize(text)
    print(f"🎵 Generated {len(audio_bytes)} bytes of audio")
    
    # שמירה לקובץ
    audio_file = tts.save_audio(text, 'greeting.mp3')
    print(f"💾 Audio saved to: {audio_file}")
    
    # השמעה ישירה (דורש pygame)
    try:
        tts.play_audio(text)
        print("🎵 Audio played successfully")
    except Exception as e:
        print(f"⚠️ Playback failed: {e}")


def openai_tts_example():
    """דוגמה ל-OpenAI TTS"""
    print("🔊 OpenAI TTS Example")
    
    # יצירת אובייקט TTS עם OpenAI
    tts = TTS(
        provider='openai',
        api_key='your-openai-api-key',
        voice='nova'  # עובד טוב עם עברית
    )
    
    # המרת טקסט לשמע באיכות גבוהה
    text = 'שלום וברכה לכולם. זוהי הודעה מהמערכת'
    audio_bytes = tts.synthesize(text, voice='nova', speed=1.0)
    print(f"🎵 OpenAI TTS generated: {len(audio_bytes)} bytes")
    
    # שמירה עם פורמט ספציפי
    audio_file = tts.save_audio(
        text,
        'openai_greeting.mp3',
        response_format='mp3'
    )
    print(f"💾 High-quality audio saved to: {audio_file}")


def azure_tts_example():
    """דוגמה ל-Azure TTS"""
    print("🔊 Azure TTS Example")
    
    # יצירת אובייקט TTS עם Azure
    tts = TTS(
        provider='azure',
        subscription_key='your-azure-key',
        region='eastus',
        voice_name='he-IL-AvigailNeural'
    )
    
    # המרת טקסט לשמע עם קול עברי
    text = 'שלום לכולם. ברוכים הבאים לשירות הלקוחות'
    audio_bytes = tts.synthesize(text)
    print(f"🎵 Azure TTS generated: {len(audio_bytes)} bytes")
    
    # יצירת SSML מתקדם
    ssml = '''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="he-IL">
        <voice name="he-IL-AvigailNeural">
            <prosody rate="slow" pitch="medium">
                שלום וברכה לכולם!
            </prosody>
            <break time="500ms"/>
            <prosody rate="fast" volume="loud">
                זוהי הודעה חשובה!
            </prosody>
        </voice>
    </speak>'''
    
    ssml_audio = tts.synthesize_ssml(ssml, 'ssml_message.wav')
    print(f"🎵 SSML audio saved to: {ssml_audio}")


def amazon_polly_example():
    """דוגמה ל-Amazon Polly"""
    print("🔊 Amazon Polly Example")
    
    # יצירת אובייקט TTS עם Amazon Polly
    tts = TTS(
        provider='amazon',
        aws_access_key_id='your-access-key',
        aws_secret_access_key='your-secret-key',
        region_name='us-east-1'
    )
    
    # המרת טקסט לשמע
    text = 'ברוכים הבאים לשירותי ימות המשיח'
    audio_bytes = tts.synthesize(text, voice_id='Joanna', language_code='en-US')
    print(f"🎵 Amazon Polly generated: {len(audio_bytes)} bytes")
    
    # שמירה לקובץ
    audio_file = tts.save_audio(text, 'polly_message.mp3')
    print(f"💾 Audio saved to: {audio_file}")


def quick_functions_example():
    """דוגמה לפונקציות TTS מהירות"""
    print("⚡ Quick TTS Functions")
    
    # המרה מהירה ללא יצירת אובייקט
    audio_bytes = synthesize(
        'שלום עליכם וברכה טובה',
        provider='gtts',
        language='he'
    )
    print(f"⚡ Quick synthesize: {len(audio_bytes)} bytes")
    
    # שמירה מהירה לקובץ
    audio_file = synthesize(
        'הודעה חשובה מהמערכת',
        provider='gtts',
        output_file='quick_message.mp3',
        language='he'
    )
    print(f"💾 Quick save: {audio_file}")
    
    # השמעה מהירה (דורש pygame)
    try:
        speak('שלום וברכה לכולם!', provider='gtts', language='he')
        print("🎵 Quick speak successful")
    except Exception as e:
        print(f"⚠️ Quick speak failed: {e}")


def voice_options_example():
    """דוגמה לאפשרויות קול שונות"""
    print("🎙️ Voice Options Example")
    
    # טקסט לבדיקה
    test_text = "זוהי בדיקת קולות שונים במערכת"
    
    # קולות שונים עם gTTS
    print("🔊 gTTS Voice Options:")
    languages = ['he', 'en', 'ar']
    for lang in languages:
        try:
            tts = TTS(provider='gtts', language=lang)
            audio_file = tts.save_audio(
                test_text if lang == 'he' else 'This is a voice test',
                f'voice_test_{lang}.mp3'
            )
            print(f"✅ {lang}: {audio_file}")
        except Exception as e:
            print(f"❌ {lang}: {e}")
    
    # מהירויות שונות
    print("\n🏃 Speed Options:")
    speeds = [True, False]  # slow, normal
    for i, slow in enumerate(speeds):
        try:
            tts = TTS(provider='gtts', language='he')
            speed_name = "slow" if slow else "normal"
            audio_file = tts.save_audio(
                f"זוהי בדיקת מהירות {speed_name}",
                f'speed_test_{speed_name}.mp3',
                slow=slow
            )
            print(f"✅ {speed_name}: {audio_file}")
        except Exception as e:
            print(f"❌ {speed_name}: {e}")


if __name__ == "__main__":
    print("🎯 דוגמאות TTS בסיסיות - Basic TTS Examples")
    print("=" * 50)
    
    try:
        # הרץ דוגמאות במצב דמו (ללא API keys אמיתיים)
        print("📋 Testing basic functionality...")
        
        # בדיקה בסיסית של הספריה
        tts = TTS()  # ספק ברירת מחדל
        test_audio = tts.synthesize("בדיקה")
        print(f"✅ Default TTS works: {len(test_audio)} bytes generated")
        
        # הצג אפשרויות
        providers = tts.get_available_providers()
        print(f"📋 Available providers: {providers}")
        
        print("\n💡 לשימוש אמיתי:")
        print("  1. התקן ספק: pip install yemot-speech[tts]")
        print("  2. עדכן API keys בקוד")
        print("  3. הרץ את הפונקציות עם נתונים אמיתיים")
        print("  4. בדוק שקבצי השמע נוצרים כמו שצריך")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 ודא שהספריה מותקנת: pip install yemot-speech")