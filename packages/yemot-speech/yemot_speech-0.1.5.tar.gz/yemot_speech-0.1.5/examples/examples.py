"""
דוגמאות שימוש בספריית yemot-speech - STT ו-TTS
Examples for using the yemot-speech library - STT and TTS

הערה: קובץ זה מכיל את כל הדוגמאות במקום אחד.
לדוגמאות מאורגנות יותר, ראו:
- stt_basic.py - דוגמאות STT בסיסיות
- tts_basic.py - דוגמאות TTS בסיסיות  
- stt_advanced.py - דוגמאות STT מתקדמות
- yemot_voice_system.py - מערכות קוליות מלאות
- combined_workflows.py - זרימות עבודה משולבות

Note: This file contains all examples in one place.
For better organized examples, see:
- stt_basic.py - Basic STT examples
- tts_basic.py - Basic TTS examples
- stt_advanced.py - Advanced STT examples  
- yemot_voice_system.py - Complete voice systems
- combined_workflows.py - Combined workflows
"""
import sys
import os

# Add src to path - go up one level from examples/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from yemot_speech import STT, TTS, transcribe, synthesize, speak


def example_openai_stt():
    """דוגמה לשימוש ב-OpenAI Whisper"""
    # יצירת אובייקט STT עם ספק OpenAI
    stt = STT(provider='openai', api_key='your-openai-api-key')
    
    # המרת קובץ שמע לטקסט
    audio_file = 'path/to/audio.wav'
    text = stt.transcribe(audio_file, language='he')  # עברית
    print(f"Transcribed text: {text}")
    
    # המרת bytes לטקסט
    with open(audio_file, 'rb') as f:
        audio_bytes = f.read()
    text = stt.transcribe_bytes(audio_bytes, language='he')
    print(f"Transcribed from bytes: {text}")


def example_google_stt():
    """דוגמה לשימוש ב-Google Cloud Speech"""
    # יצירת אובייקט STT עם ספק Google
    stt = STT(
        provider='google',
        credentials_path='path/to/google-credentials.json',
        language_code='he-IL'
    )
    
    # המרת קובץ שמע לטקסט
    audio_file = 'path/to/audio.wav'
    text = stt.transcribe(audio_file)
    print(f"Google transcribed: {text}")


def example_local_stt():
    """דוגמה לשימוש במודל מקומי (Whisper)"""
    # יצירת אובייקט STT עם מודל מקומי
    stt = STT(provider='local', engine='whisper', model_name='medium')
    
    # המרת קובץ שמע לטקסט
    audio_file = 'path/to/audio.wav'
    text = stt.transcribe(audio_file, language='hebrew')
    print(f"Local Whisper transcribed: {text}")


def example_quick_transcribe():
    """דוגמה לשימוש בפונקציית transcribe המהירה"""
    # המרה מהירה ללא יצירת אובייקט
    text = transcribe(
        'path/to/audio.wav',
        provider='openai',
        api_key='your-key',
        language='he'
    )
    print(f"Quick transcribe: {text}")


def example_yemot_phone_call():
    """דוגמה מיוחדת לשיחות טלפון של ימות המשיח"""
    # לשיחות טלפון מומלץ להשתמש ב-Google עם הגדרות מותאמות
    stt = STT(
        provider='google',
        credentials_path='path/to/credentials.json'
    )
    
    # עבור קובצי שמע של שיחות ימות המשיח (בדרך כלל מו-לאו או WAV)
    phone_audio = 'path/to/yemot_call.wav'
    
    # המרה עם הגדרות מותאמות לשיחות טלפון
    text = stt.transcribe(
        phone_audio,
        encoding='MULAW',  # קידוד נפוץ בשיחות טלפון
        sample_rate=8000,  # תדירות נפוצה בטלפוניה
        language_code='he-IL'
    )
    
    print(f"Yemot call transcribed: {text}")


def example_provider_info():
    """דוגמה לקבלת מידע על הספק הנוכחי"""
    stt = STT(provider='openai', api_key='test')
    
    info = stt.get_provider_info()
    print(f"Provider info: {info}")
    
    # רשימת ספקים זמינים
    providers = STT.get_available_providers()
    print(f"Available providers: {providers}")


def example_gtts_tts():
    """דוגמה ל-Google TTS"""
    # יצירת אובייקט TTS עם Google TTS
    tts = TTS(provider='gtts', language='he')
    
    # המרת טקסט לשמע וקבלת bytes
    text = 'שלום עליכם! ברוכים הבאים למערכת ימות המשיח'
    audio_bytes = tts.synthesize(text)
    print(f"Generated {len(audio_bytes)} bytes of audio")
    
    # שמירה לקובץ
    audio_file = tts.save_audio(text, 'greeting.mp3')
    print(f"Audio saved to: {audio_file}")
    
    # השמעה ישירה (דורש pygame)
    try:
        tts.play_audio(text)
        print("Audio played successfully")
    except Exception as e:
        print(f"Playback failed: {e}")


def example_openai_tts():
    """דוגמה ל-OpenAI TTS"""
    # יצירת אובייקט TTS עם OpenAI
    tts = TTS(
        provider='openai',
        api_key='your-openai-api-key',
        voice='nova'  # עובד טוב עם עברית
    )
    
    # המרת טקסט לשמע באיכות גבוהה
    text = 'שלום וברכה לכולם. זוהי הודעה מהמערכת'
    audio_bytes = tts.synthesize(text, voice='nova', speed=1.0)
    print(f"OpenAI TTS generated: {len(audio_bytes)} bytes")
    
    # שמירה עם פורמט ספציפי
    audio_file = tts.save_audio(
        text,
        'openai_greeting.mp3',
        response_format='mp3'
    )
    print(f"High-quality audio saved to: {audio_file}")


def example_azure_tts():
    """דוגמה ל-Azure TTS"""
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
    print(f"Azure TTS generated: {len(audio_bytes)} bytes")
    
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
    print(f"SSML audio saved to: {ssml_audio}")


def example_quick_tts_functions():
    """דוגמה לפונקציות TTS מהירות"""
    # המרה מהירה ללא יצירת אובייקט
    audio_bytes = synthesize(
        'שלום עליכם וברכה טובה',
        provider='gtts',
        language='he'
    )
    print(f"Quick synthesize: {len(audio_bytes)} bytes")
    
    # שמירה מהירה לקובץ
    audio_file = synthesize(
        'הודעה חשובה מהמערכת',
        provider='gtts',
        output_file='quick_message.mp3',
        language='he'
    )
    print(f"Quick save: {audio_file}")
    
    # השמעה מהירה (דורש pygame)
    try:
        speak('שלום וברכה לכולם!', provider='gtts', language='he')
        print("Quick speak successful")
    except Exception as e:
        print(f"Quick speak failed: {e}")


def example_yemot_tts_workflow():
    """דוגמה לזרימת עבודה מלאה של ימות המשיח עם TTS"""
    print("\n=== זרימת עבודה מלאה של ימות המשיח ===")
    
    # יצירת מערכת TTS
    tts = TTS(provider='gtts', language='he')
    
    # 1. יצירת ברכת כניסה
    greeting = "שלום וברכה וברוכים הבאים למערכת ימות המשיח"
    greeting_audio = tts.save_audio(greeting, 'yemot_greeting.mp3', slow=False)
    print(f"✅ Greeting created: {greeting_audio}")
    
    # 2. יצירת תפריט ראשי
    menu_options = {
        '1': 'זמני התפילות',
        '2': 'הודעות חדשות',
        '3': 'לוח השבוע',
        '4': 'תרומות והקדשות',
        '9': 'צור קשר',
        '0': 'חזרה לתפריט הראשי'
    }
    
    menu_text = "תפריט ראשי. אנא בחרו מהאפשרויות הבאות: "
    for key, desc in menu_options.items():
        menu_text += f"לחצו {key} עבור {desc}. "
    menu_text += "תודה רבה."
    
    menu_audio = tts.save_audio(menu_text, 'yemot_menu.mp3', slow=True)
    print(f"✅ Menu created: {menu_audio}")
    
    # 3. יצירת הודעות מותאמות
    announcements = [
        "הודעה חשובה: מחר יתקיים שיעור מיוחד בשעה 20:00",
        "תזכורת: תרומות לקופת צדקה יתקבלו עד סוף החודש",
        "שבת שלום לכל בית ישראל! השיעור השבועי יתקיים כרגיל"
    ]
    
    for i, announcement in enumerate(announcements, 1):
        audio_file = tts.save_audio(
            f"שלום וברכה. {announcement}. תודה רבה וכל טוב.",
            f'yemot_announcement_{i}.mp3'
        )
        print(f"✅ Announcement {i} created: {audio_file}")
    
    # 4. יצירת הודעות שגיאה
    error_messages = {
        'invalid_input': 'מצטערים, לא זיהינו את הבחירה. אנא נסו שוב',
        'system_busy': 'המערכת עסוקה כרגע. אנא נסו שוב מאוחר יותר',
        'timeout': 'זמן הבחירה פקע. חוזרים לתפריט הראשי'
    }
    
    for error_type, message in error_messages.items():
        audio_file = tts.save_audio(message, f'error_{error_type}.mp3')
        print(f"✅ Error message created: {audio_file}")
    
    print("🎉 כל קבצי השמע נוצרו בהצלחה!")


def example_combined_stt_tts():
    """דוגמה לשילוב STT ו-TTS"""
    print("\n=== שילוב STT ו-TTS ===")
    
    # סימולציה של מערכת אינטראקטיבית
    stt = STT(provider='openai', api_key='your-key')
    tts = TTS(provider='gtts', language='he')
    
    # 1. המרת שמע לטקסט (STT)
    print("📞 מקבל שיחה וממיר לטקסט...")
    user_audio = 'user_request.wav'
    user_text = stt.transcribe(user_audio, language='he')
    print(f"👤 המשתמש אמר: {user_text}")
    
    # 2. עיבוד הבקשה
    if 'זמנים' in user_text or 'תפילות' in user_text:
        response = "זמני התפילות היום: שחרית 6:30, מנחה 18:30, מעריב 20:00"
    elif 'הודעות' in user_text:
        response = "יש לכם 3 הודעות חדשות במערכת"
    elif 'שבת' in user_text:
        response = "שבת נכנסת בשעה 17:45 ויוצאת בשעה 18:50"
    else:
        response = "לא הבנתי את בקשתכם. לחצו 0 לעזרה או 9 לצור קשר"
    
    print(f"🤖 המערכת מגיבה: {response}")
    
    # 3. המרת התגובה לשמע (TTS)
    response_audio = tts.save_audio(response, 'system_response.mp3')
    print(f"🔊 תגובה קולית נשמרה: {response_audio}")
    
    print("✅ מחזור מלא של STT->עיבוד->TTS הושלם!")


if __name__ == "__main__":
    print("=== דוגמאות yemot-speech - STT ו-TTS ===")
    
    # הרץ את הדוגמאות (במציאות תצטרך להחליף API keys ונתיבי קבצים)
    try:
        print("\n--- STT Examples ---")
        example_provider_info()
        
        print("\n--- TTS Examples ---")
        example_gtts_tts()
        
        print("\n--- Quick Functions ---")
        example_quick_tts_functions()
        
        print("\n--- Yemot Workflow ---")
        example_yemot_tts_workflow()
        
        print("\n--- Combined STT+TTS ---")
        example_combined_stt_tts()
        
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50)
    print("📚 לדוגמאות נוספות ותיעוד מלא:")
    print("   - README.md")
    print("   - demo_full.py")
    print("   - https://github.com/your-username/yemot-speech")
    print("\n💡 לפני השימוש האמיתי:")
    print("   1. התקן את הספק הרצוי: pip install yemot-speech[openai]")
    print("   2. עדכן API keys בקוד")
    print("   3. הכן קבצי שמע לבדיקה")