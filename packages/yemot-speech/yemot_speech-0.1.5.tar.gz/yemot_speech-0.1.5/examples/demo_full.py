#!/usr/bin/env python3
"""
דמו מלא של yemot-speech - STT ו-TTS
Complete demo of yemot-speech - STT and TTS
"""

import sys
import os

# Add src to path - go up one level from examples/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from yemot_speech import STT, TTS
from yemot_speech.base import STTProvider, TTSProvider


# Demo providers for testing
class DemoSTT(STTProvider):
    """ספק דמו ל-STT / Demo STT provider"""
    
    def transcribe(self, audio_file, **kwargs):
        if 'hebrew' in str(audio_file).lower():
            return "זוהי דוגמה למרת שמע לטקסט בעברית"
        return f"This is a demo transcription of {audio_file}"
    
    def transcribe_bytes(self, audio_bytes, **kwargs):
        return f"Demo transcription of {len(audio_bytes)} audio bytes"


class DemoTTS(TTSProvider):
    """ספק דמו ל-TTS / Demo TTS provider"""
    
    def synthesize(self, text, output_file=None, **kwargs):
        # Simulate audio generation
        fake_audio_bytes = f"[AUDIO:{text}]".encode('utf-8')
        
        if output_file:
            with open(output_file, 'wb') as f:
                f.write(fake_audio_bytes)
            return output_file
        else:
            return fake_audio_bytes


def demo_stt():
    """דמו STT / STT Demo"""
    print("\n" + "="*50)
    print("🎤 דמו STT (Speech-to-Text)")
    print("🎤 STT (Speech-to-Text) Demo")
    print("="*50)
    
    # Register demo provider
    STT.register_provider('demo', DemoSTT)
    
    # Create STT instance
    stt = STT(provider='demo')
    
    # Demo transcriptions
    test_files = [
        'english_audio.wav',
        'hebrew_audio.wav',
        'yemot_call.wav'
    ]
    
    for file in test_files:
        print(f"\n🎵 Transcribing: {file}")
        result = stt.transcribe(file)
        print(f"📝 Result: {result}")
    
    # Demo bytes transcription
    print(f"\n📊 Transcribing audio bytes...")
    result = stt.transcribe_bytes(b"fake audio data" * 50)
    print(f"📝 Result: {result}")


def demo_tts():
    """דמו TTS / TTS Demo"""
    print("\n" + "="*50)
    print("🔊 דמו TTS (Text-to-Speech)")
    print("🔊 TTS (Text-to-Speech) Demo")
    print("="*50)
    
    # Register demo provider
    TTS.register_provider('demo', DemoTTS)
    
    # Create TTS instance
    tts = TTS(provider='demo')
    
    # Demo synthesis
    test_texts = [
        'שלום עליכם וברוכים הבאים!',
        'Hello and welcome to Yemot HaMashiach!',
        'תפריט ראשי: לחצו 1 עבור זמני תפילות, לחצו 2 עבור הודעות'
    ]
    
    for text in test_texts:
        print(f"\n💬 Synthesizing: {text}")
        audio_bytes = tts.synthesize(text)
        print(f"🔊 Generated: {len(audio_bytes)} bytes")
        print(f"📄 Content preview: {audio_bytes.decode('utf-8', errors='ignore')}")
    
    # Demo file saving
    print(f"\n💾 Saving to file...")
    output_file = tts.save_audio('שלום וברכה לכולם!', 'demo_output.wav')
    print(f"📁 Saved to: {output_file}")
    
    # Clean up
    try:
        os.remove(output_file)
        print("🗑️  Cleaned up demo file")
    except:
        pass


def demo_combined_workflow():
    """דמו זרימת עבודה משולבת / Combined Workflow Demo"""
    print("\n" + "="*50)
    print("🔄 דמו זרימת עבודה משולבת")
    print("🔄 Combined Workflow Demo")
    print("="*50)
    
    # Register demo providers
    STT.register_provider('demo', DemoSTT)
    TTS.register_provider('demo', DemoTTS)
    
    print("📱 סימולציה של מערכת ימות המשיח")
    print("📱 Simulating Yemot HaMashiach system")
    
    # Step 1: Receive audio message (STT)
    print("\n1️⃣ קבלת הודעה קולית / Receiving voice message")
    stt = STT(provider='demo')
    user_message = stt.transcribe('user_hebrew_message.wav')
    print(f"👤 User said: {user_message}")
    
    # Step 2: Process the message (example logic)
    print("\n2️⃣ עיבוד ההודעה / Processing message")
    if 'תפילות' in user_message or 'זמנים' in user_message:
        response = "זמני התפילות היום: שחרית 6:30, מנחה 18:30, מעריב 20:00"
    elif 'הודעות' in user_message:
        response = "יש לכם 3 הודעות חדשות. לחצו 1 לשמיעה"
    else:
        response = "לא הבנתי את בקשתכם. אנא נסו שוב או לחצו 0 לעזרה"
    
    print(f"🤖 System response: {response}")
    
    # Step 3: Generate response audio (TTS)
    print("\n3️⃣ יצירת תגובה קולית / Generating voice response")
    tts = TTS(provider='demo')
    audio_response = tts.synthesize(response)
    print(f"🔊 Generated response: {len(audio_response)} bytes")
    
    print("\n✅ זרימת העבודה הושלמה בהצלחה!")
    print("✅ Workflow completed successfully!")


def demo_yemot_specific_features():
    """דמו תכונות ספציפיות לימות המשיח / Yemot-specific features demo"""
    print("\n" + "="*50)
    print("🏛️  תכונות מיוחדות לימות המשיח")
    print("🏛️  Yemot HaMashiach Special Features")
    print("="*50)
    
    TTS.register_provider('demo', DemoTTS)
    tts = TTS(provider='demo')
    
    # Create menu
    print("\n📋 יצירת תפריט מערכת / Creating system menu")
    menu_options = {
        '1': 'זמני התפילות',
        '2': 'הודעות חדשות',
        '3': 'לוח השבוע',
        '9': 'צור קשר',
        '0': 'חזרה לתפריט הראשי'
    }
    
    menu_text = "תפריט ראשי - אנא בחרו מהאפשרויות הבאות: "
    for key, desc in menu_options.items():
        menu_text += f"לחצו {key} עבור {desc}. "
    
    menu_audio = tts.synthesize(menu_text)
    print(f"📱 Menu audio generated: {len(menu_audio)} bytes")
    
    # Create personalized greeting
    print("\n👋 יצירת ברכה אישית / Creating personalized greeting")
    greeting = "בוקר טוב ושבת שלום רבי משה! ברוכים הבאים למערכת ימות המשיח"
    greeting_audio = tts.synthesize(greeting)
    print(f"🎙️  Greeting audio: {len(greeting_audio)} bytes")
    
    # Create announcement
    print("\n📢 יצירת הודעה חשובה / Creating important announcement")
    announcement = "הודעה חשובה: מחר, יום ראשון, יתקיים אסיפה כללית בשעה 20:00. נא להגיע בזמן. תודה רבה"
    announcement_audio = tts.synthesize(announcement)
    print(f"📣 Announcement audio: {len(announcement_audio)} bytes")


def demo_provider_management():
    """דמו ניהול ספקים / Provider management demo"""
    print("\n" + "="*50)
    print("⚙️  ניהול ספקים / Provider Management")
    print("="*50)
    
    # STT Providers
    print("\n🎤 STT Providers:")
    available_stt = STT.get_available_providers()
    print(f"📋 Available STT providers: {available_stt}")
    
    STT.register_provider('demo', DemoSTT)
    print("✅ Registered demo STT provider")
    
    updated_stt = STT.get_available_providers()
    print(f"📋 Updated STT providers: {updated_stt}")
    
    # TTS Providers  
    print("\n🔊 TTS Providers:")
    available_tts = TTS.get_available_providers()
    print(f"📋 Available TTS providers: {available_tts}")
    
    TTS.register_provider('demo', DemoTTS)
    print("✅ Registered demo TTS provider")
    
    updated_tts = TTS.get_available_providers()
    print(f"📋 Updated TTS providers: {updated_tts}")
    
    # Provider info
    print("\n📊 Provider Information:")
    stt = STT(provider='demo')
    tts = TTS(provider='demo')
    
    stt_info = stt.get_provider_info()
    tts_info = tts.get_provider_info()
    
    print(f"🎤 STT Info: {stt_info}")
    print(f"🔊 TTS Info: {tts_info}")


def main():
    """הרצת כל הדמואים / Run all demos"""
    print("🎉 ברוכים הבאים ל-yemot-speech - דמו מלא!")
    print("🎉 Welcome to yemot-speech - Complete Demo!")
    print("📚 ספריה מלאה להמרת שמע לטקסט וטקסט לשמע")
    print("📚 Complete library for Speech-to-Text and Text-to-Speech")
    
    try:
        demo_stt()
        demo_tts()
        demo_combined_workflow()
        demo_yemot_specific_features()
        demo_provider_management()
        
        print("\n" + "="*50)
        print("✅ כל הדמואים הסתיימו בהצלחה!")
        print("✅ All demos completed successfully!")
        print("="*50)
        
        print("\n📖 לשימוש אמיתי:")
        print("📖 For real usage:")
        print("   from yemot_speech import STT, TTS")
        print("   stt = STT(provider='openai', api_key='your-key')")
        print("   tts = TTS(provider='gtts', language='he')")
        print("   text = stt.transcribe('audio.wav')")
        print("   audio = tts.synthesize('שלום עליכם!')")
        
    except Exception as e:
        print(f"\n❌ Error in demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()