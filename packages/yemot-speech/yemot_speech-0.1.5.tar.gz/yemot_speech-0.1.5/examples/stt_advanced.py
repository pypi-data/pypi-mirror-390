#!/usr/bin/env python3
"""
דוגמאות מתקדמות ל-STT עבור מערכות ימות המשיח
Advanced STT examples for Yemot HaMashiach systems
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from yemot_speech import STT


def yemot_phone_call_example():
    """דוגמה מיוחדת לשיחות טלפון של ימות המשיח"""
    print("📞 Yemot Phone Call Example")
    
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
        language_code='he-IL',
        enable_automatic_punctuation=True,
        enable_word_time_offsets=True
    )
    
    print(f"📱 Yemot call transcribed: {text}")


def interactive_voice_menu_example():
    """דוגמה לעיבוד תפריט קולי אינטראקטיבי"""
    print("🎛️ Interactive Voice Menu Processing")
    
    stt = STT(provider='openai', api_key='your-key')
    
    # סימולציה של קלט משתמש בתפריט קולי
    user_responses = [
        'path/to/user_says_zmanim.wav',      # "זמנים"
        'path/to/user_says_hodaot.wav',      # "הודעות"
        'path/to/user_says_contact.wav',     # "צור קשר"
        'path/to/user_says_number_2.wav',    # "שתיים"
    ]
    
    # מילון תגובות אפשריות
    menu_responses = {
        'זמנים': 'זמני התפילות',
        'תפילות': 'זמני התפילות',
        'הודעות': 'הודעות המערכת',
        'חדשות': 'הודעות המערכת',
        'צור קשר': 'יצירת קשר',
        'עזרה': 'מרכז עזרה',
        'אחד': '1',
        'שתיים': '2',
        'שלוש': '3',
        'ארבע': '4',
    }
    
    for i, audio_file in enumerate(user_responses, 1):
        try:
            # המרת דבור המשתמש לטקסט
            user_text = stt.transcribe(audio_file, language='he')
            print(f"👤 User {i} said: {user_text}")
            
            # זיהוי כוונת המשתמש
            intent = None
            for keyword, response in menu_responses.items():
                if keyword in user_text.lower():
                    intent = response
                    break
            
            if intent:
                print(f"🎯 Detected intent: {intent}")
            else:
                print("❓ Intent not recognized - redirecting to main menu")
                
        except Exception as e:
            print(f"❌ Error processing audio {i}: {e}")


def batch_audio_processing_example():
    """דוגמה לעיבוד אצווה של קבצי שמע"""
    print("📦 Batch Audio Processing")
    
    stt = STT(provider='openai', api_key='your-key')
    
    # רשימת קבצי שמע לעיבוד
    audio_files = [
        'recordings/call_001.wav',
        'recordings/call_002.wav', 
        'recordings/call_003.wav',
        'recordings/message_001.wav',
        'recordings/message_002.wav',
    ]
    
    results = []
    
    for i, audio_file in enumerate(audio_files, 1):
        try:
            print(f"🎵 Processing file {i}/{len(audio_files)}: {audio_file}")
            
            # המרה לטקסט
            text = stt.transcribe(audio_file, language='he')
            
            # שמירת תוצאה
            result = {
                'file': audio_file,
                'text': text,
                'length': len(text),
                'success': True
            }
            results.append(result)
            
            print(f"✅ Success: {text[:50]}...")
            
        except Exception as e:
            print(f"❌ Failed processing {audio_file}: {e}")
            results.append({
                'file': audio_file,
                'text': None,
                'error': str(e),
                'success': False
            })
    
    # סיכום תוצאות
    successful = sum(1 for r in results if r['success'])
    print(f"\n📊 Batch Results: {successful}/{len(audio_files)} successful")
    
    return results


def real_time_transcription_example():
    """דוגמה להמרה בזמן אמת (מדומה)"""
    print("⏱️ Real-time Transcription Simulation")
    
    stt = STT(provider='google', credentials_path='path/to/credentials.json')
    
    # סימולציה של חלקי שמע מגיעים בזמן אמת
    audio_chunks = [
        'chunk_001.wav',  # "שלום"
        'chunk_002.wav',  # "אני רוצה"
        'chunk_003.wav',  # "לשמוע"
        'chunk_004.wav',  # "זמני תפילות"
    ]
    
    full_transcription = ""
    
    for i, chunk in enumerate(audio_chunks, 1):
        try:
            print(f"🎙️ Processing chunk {i}...")
            
            # עיבוד חלק שמע
            chunk_text = stt.transcribe(chunk, language='he')
            full_transcription += f" {chunk_text}"
            
            print(f"📝 Chunk {i}: {chunk_text}")
            print(f"📄 Full so far: {full_transcription.strip()}")
            
        except Exception as e:
            print(f"❌ Error in chunk {i}: {e}")
    
    print(f"🎯 Final transcription: {full_transcription.strip()}")


def audio_quality_analysis_example():
    """דוגמה לניתוח איכות שמע"""
    print("🔍 Audio Quality Analysis")
    
    stt = STT(provider='openai', api_key='your-key')
    
    test_files = [
        ('high_quality.wav', 'High quality studio recording'),
        ('phone_quality.wav', 'Phone call quality'),
        ('noisy_background.wav', 'Background noise'),
        ('low_volume.wav', 'Low volume recording'),
    ]
    
    for audio_file, description in test_files:
        try:
            print(f"🎵 Testing: {description}")
            
            # נסיון להמיר לטקסט
            text = stt.transcribe(audio_file, language='he')
            
            # הערכת איכות בסיסית על בסיס אורך הטקסט ומילים ברורות
            word_count = len(text.split())
            clarity_score = min(100, word_count * 10)  # ציון פשוט
            
            print(f"📝 Text: {text}")
            print(f"📊 Words: {word_count}, Clarity Score: {clarity_score}%")
            
            if clarity_score < 30:
                print("⚠️ Poor audio quality detected")
            elif clarity_score < 70:
                print("🔶 Moderate audio quality")
            else:
                print("✅ Good audio quality")
                
        except Exception as e:
            print(f"❌ Failed to process {audio_file}: {e}")
            print("💡 Consider audio preprocessing or different provider")
        
        print("-" * 40)


if __name__ == "__main__":
    print("🎯 דוגמאות STT מתקדמות - Advanced STT Examples")
    print("=" * 60)
    
    print("\n💡 דוגמאות אלה מיועדות לשימוש מתקדם במערכות ימות המשיח")
    print("💡 These examples are for advanced usage in Yemot HaMashiach systems")
    
    print("\n🔧 לפני השימוש:")
    print("  1. התקן: pip install yemot-speech[openai] או [google]")
    print("  2. הכן API keys")
    print("  3. הכן קבצי שמע לבדיקה")
    print("  4. התאם נתיבי קבצים בקוד")
    
    # הרץ דוגמה בסיסית להדגמה
    try:
        from yemot_speech import STT
        stt = STT(provider='demo')
        print(f"\n✅ Library loaded successfully!")
        print(f"📋 Available providers: {stt.get_available_providers()}")
        
    except Exception as e:
        print(f"❌ Error loading library: {e}")