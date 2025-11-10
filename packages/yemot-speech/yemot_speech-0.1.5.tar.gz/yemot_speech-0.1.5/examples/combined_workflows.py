#!/usr/bin/env python3
"""
דוגמאות לשילוב STT ו-TTS - זרימות עבודה מלאות
Combined STT+TTS examples - Complete workflows
"""
import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from yemot_speech import STT, TTS


def simple_conversation_flow():
    """זרימת שיחה פשוטה - STT→עיבוד→TTS"""
    print("💬 Simple Conversation Flow")
    
    # הגדרת מערכות
    stt = STT(provider='openai', api_key='your-key')
    tts = TTS(provider='gtts', language='he')
    
    # סימולציה של קלט משתמש
    user_audio_files = [
        'user_says_zmanim.wav',    # "מתי התפילות?"
        'user_says_hodaot.wav',    # "יש הודעות?"
        'user_says_help.wav',      # "אני צריך עזרה"
    ]
    
    # מילון תגובות
    responses = {
        'זמנים|תפילות|מתי': 'זמני התפילות היום: שחרית 6:30, מנחה 18:30, מעריב 20:00',
        'הודעות|חדשות|מה יש': 'יש לכם 2 הודעות חדשות: הודעה על שיעור מחר והודעה על תרומות',
        'עזרה|לא מבין|help': 'לחצו 0 לתפריט ראשי, 9 לעזרה, או דברו עם מפעיל',
        'default': 'לא הבנתי את בקשתכם. אנא נסו שוב או לחצו 0 לעזרה'
    }
    
    for i, audio_file in enumerate(user_audio_files, 1):
        print(f"\n--- Round {i} ---")
        
        try:
            # 1. STT - המרת דבור לטקסט
            print(f"🎤 Processing: {audio_file}")
            user_text = stt.transcribe(audio_file, language='he')
            print(f"👤 User said: {user_text}")
            
            # 2. עיבוד - זיהוי כוונה
            response = responses['default']
            for keywords, reply in responses.items():
                if keywords == 'default':
                    continue
                if any(word in user_text.lower() for word in keywords.split('|')):
                    response = reply
                    break
            
            print(f"🤖 System responds: {response}")
            
            # 3. TTS - המרת תגובה לשמע
            audio_bytes = tts.synthesize(response)
            audio_file = tts.save_audio(response, f'response_{i}.mp3')
            
            print(f"🔊 Audio response: {audio_file} ({len(audio_bytes)} bytes)")
            
        except Exception as e:
            print(f"❌ Error in round {i}: {e}")


def interactive_menu_system():
    """מערכת תפריט אינטראקטיבית מלאה"""
    print("📱 Interactive Menu System")
    
    stt = STT(provider='google', credentials_path='path/to/credentials.json')
    tts = TTS(provider='gtts', language='he')
    
    # מבנה תפריטים
    menu_structure = {
        'main': {
            'greeting': 'ברוכים הבאים למערכת ימות המשיח. תפריט ראשי:',
            'options': {
                '1': {'text': 'זמני תפילות', 'action': 'zmanim_menu'},
                '2': {'text': 'הודעות', 'action': 'messages_menu'},
                '3': {'text': 'צור קשר', 'action': 'contact'},
                '9': {'text': 'עזרה', 'action': 'help'}
            }
        },
        'zmanim_menu': {
            'greeting': 'תפריט זמני תפילות:',
            'options': {
                '1': {'text': 'זמנים להיום', 'action': 'show_today'},
                '2': {'text': 'זמני שבת', 'action': 'show_shabbat'},
                '0': {'text': 'חזרה', 'action': 'main'}
            }
        }
    }
    
    current_menu = 'main'
    session_active = True
    
    while session_active:
        try:
            # הצג תפריט נוכחי
            menu = menu_structure[current_menu]
            menu_text = menu['greeting'] + ' '
            
            for key, option in menu['options'].items():
                menu_text += f"לחצו {key} עבור {option['text']}. "
            
            # יצור ושמע תפריט
            menu_audio = tts.save_audio(menu_text, f'menu_{current_menu}.mp3')
            print(f"🔊 Playing menu: {menu_audio}")
            
            # המתן לקלט משתמש (סימולציה)
            print("🎤 Listening for user input...")
            user_input_file = f'user_choice_{current_menu}.wav'  # קובץ מדומה
            
            # עיבוד קלט (בפועל - STT)
            user_choice = stt.transcribe(user_input_file, language='he')
            print(f"👤 User choice: {user_choice}")
            
            # זיהוי בחירה
            detected_option = None
            number_words = {
                'אחד': '1', 'שתיים': '2', 'שלוש': '3', 
                'אפס': '0', 'תשע': '9'
            }
            
            # חיפוש מספר או מילה
            for word, num in number_words.items():
                if word in user_choice.lower():
                    detected_option = num
                    break
            
            # או מספר ישיר
            for char in user_choice:
                if char.isdigit() and char in menu['options']:
                    detected_option = char
                    break
            
            if detected_option and detected_option in menu['options']:
                action = menu['options'][detected_option]['action']
                print(f"🎯 Executing action: {action}")
                
                if action == 'main':
                    current_menu = 'main'
                elif action in menu_structure:
                    current_menu = action
                else:
                    # פעולה ספציפית
                    response = execute_action(action, tts)
                    if response:
                        print(f"📢 Response: {response}")
            else:
                # בחירה לא מובנת
                error_msg = "לא הבנתי את הבחירה. אנא נסו שוב."
                error_audio = tts.save_audio(error_msg, 'error_invalid_choice.mp3')
                print(f"❌ Error: {error_audio}")
            
            # בדיקת יציאה (לדוגמה)
            if current_menu == 'main' and detected_option == '0':
                session_active = False
                
        except Exception as e:
            print(f"❌ Error in menu system: {e}")
            break
    
    # סיום
    goodbye = "תודה שהשתמשתם במערכת. להתראות!"
    goodbye_audio = tts.save_audio(goodbye, 'goodbye.mp3')
    print(f"👋 Session ended: {goodbye_audio}")


def execute_action(action, tts):
    """ביצוע פעולות ספציפיות"""
    responses = {
        'show_today': 'זמני התפילות היום: שחרית 6:30, מנחה 18:30, מעריב 20:00',
        'show_shabbat': 'כניסת שבת 17:45, יציאת שבת 18:50',
        'contact': 'לפניות צרו קשר במספר 02-1234567',
        'help': 'לעזרה לחצו 0 או דברו עם מפעיל'
    }
    
    if action in responses:
        response = responses[action]
        audio_file = tts.save_audio(response, f'action_{action}.mp3')
        print(f"🔊 Action response: {audio_file}")
        return audio_file
    
    return None


def real_time_assistant():
    """עוזר קולי בזמן אמת"""
    print("🤖 Real-time Voice Assistant")
    
    stt = STT(provider='openai', api_key='your-key')
    tts = TTS(provider='gtts', language='he')
    
    # בנק ידע פשוט
    knowledge_base = {
        'זמנים': {
            'שחרית': '6:30',
            'מנחה': '18:30', 
            'מעריב': '20:00'
        },
        'אנשים': {
            'רב': '02-1234567',
            'גבאי': '02-1234568',
            'מזכירות': '02-1234569'
        },
        'שירותים': {
            'מקווה': 'פתוח ימים א-ה 19:00-22:00',
            'ספרייה': 'פתוח ימים א-ה 16:00-20:00',
            'חנות': 'פתוח ימים א-ה 9:00-18:00'
        }
    }
    
    conversation_history = []
    
    print("🎙️ Voice assistant is listening...")
    
    # סימולציה של שאלות
    sample_questions = [
        'מתי התפילות?',
        'איך קוראים לרב?', 
        'מתי פתוח המקווה?',
        'תודה, זה הכל'
    ]
    
    for i, question in enumerate(sample_questions, 1):
        try:
            print(f"\n--- Question {i} ---")
            
            # סימולציה של קלט קולי
            print(f"🎤 User asks: {question}")
            conversation_history.append(f"User: {question}")
            
            # חיפוש תשובה בבנק הידע
            answer = "מצטער, לא יודע לענות על זה. אנא פנו למזכירות."
            
            question_lower = question.lower()
            
            # זיהוי נושא ומתן תשובה
            if any(word in question_lower for word in ['זמנים', 'תפילות', 'מתי']):
                times = knowledge_base['זמנים']
                answer = f"זמני התפילות: שחרית {times['שחרית']}, מנחה {times['מנחה']}, מעריב {times['מעריב']}"
            
            elif any(word in question_lower for word in ['רב', 'קוראים']):
                answer = f"ליצירת קשר עם הרב: {knowledge_base['אנשים']['רב']}"
            
            elif any(word in question_lower for word in ['מקווה', 'פתוח']):
                answer = f"שעות המקווה: {knowledge_base['שירותים']['מקווה']}"
            
            elif any(word in question_lower for word in ['תודה', 'זה הכל', 'סיום']):
                answer = "בשמחה! תמיד פה לעזור. יום טוב!"
                
            print(f"🤖 Assistant: {answer}")
            conversation_history.append(f"Assistant: {answer}")
            
            # המרה לשמע
            audio_bytes = tts.synthesize(answer)
            audio_file = tts.save_audio(answer, f'assistant_response_{i}.mp3')
            print(f"🔊 Response audio: {audio_file}")
            
            # הפסקה קצרה
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Error processing question {i}: {e}")
    
    # סיכום השיחה
    print(f"\n📋 Conversation Summary:")
    for entry in conversation_history:
        print(f"  {entry}")


def voice_controlled_automation():
    """אוטומציה מבוקרת קול"""
    print("🔧 Voice Controlled Automation")
    
    stt = STT(provider='openai', api_key='your-key')
    tts = TTS(provider='gtts', language='he')
    
    # פקודות אוטומציה
    automation_commands = {
        'הפעל מוזיקה': lambda: "מפעיל מוזיקת רקע",
        'כבה מוזיקה': lambda: "מכבה מוזיקה",
        'הדלק אורות': lambda: "מדליק אורות באולם",
        'כבה אורות': lambda: "מכבה אורות",
        'הפעל מיקרופון': lambda: "מפעיל מערכת הגברה",
        'כבה מיקרופון': lambda: "מכבה מערכת הגברה",
        'שמור הקלטה': lambda: "שומר את ההקלטה הנוכחית",
        'נקה מערכת': lambda: "מנקה קבצים זמניים"
    }
    
    # סימולציה של פקודות
    voice_commands = [
        'הדלק את האורות באולם',
        'הפעל מוזיקה לרקע',
        'שמור את ההקלטה',
        'כבה הכל וסגור'
    ]
    
    for i, command_audio in enumerate(voice_commands, 1):
        try:
            print(f"\n--- Command {i} ---")
            
            # המרת פקודה קולית (מדומה)
            print(f"🎤 Voice command: {command_audio}")
            
            # זיהוי פקודה
            detected_command = None
            for cmd_phrase in automation_commands.keys():
                if any(word in command_audio.lower() for word in cmd_phrase.split()):
                    detected_command = cmd_phrase
                    break
            
            if detected_command:
                # ביצוע פקודה
                result = automation_commands[detected_command]()
                response = f"✅ {result}"
                
                print(f"🔧 Executing: {detected_command}")
                print(f"📝 Result: {response}")
                
                # אישור קולי
                confirmation = f"בוצע: {result}"
                audio_bytes = tts.synthesize(confirmation)
                audio_file = tts.save_audio(confirmation, f'automation_{i}.mp3')
                print(f"🔊 Confirmation: {audio_file}")
                
            else:
                # פקודה לא מוכרת
                error_msg = "פקודה לא מוכרת. אנא נסו שוב."
                print(f"❌ Unknown command: {command_audio}")
                error_audio = tts.save_audio(error_msg, f'unknown_command_{i}.mp3')
                print(f"🔊 Error message: {error_audio}")
                
        except Exception as e:
            print(f"❌ Error processing command {i}: {e}")


if __name__ == "__main__":
    print("🎯 שילוב STT+TTS - דוגמאות מתקדמות")
    print("Combined STT+TTS - Advanced Examples")
    print("=" * 60)
    
    examples = [
        ("Simple Conversation", simple_conversation_flow),
        ("Interactive Menu", interactive_menu_system), 
        ("Voice Assistant", real_time_assistant),
        ("Voice Automation", voice_controlled_automation)
    ]
    
    print("בחרו דוגמה להרצה:")
    for i, (name, func) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    try:
        choice = input("\nהקישו מספר (1-4) או Enter לכל הדוגמאות: ").strip()
        
        if choice == "":
            # הרץ את כל הדוגמאות
            for name, func in examples:
                print(f"\n{'='*20} {name} {'='*20}")
                func()
        elif choice.isdigit() and 1 <= int(choice) <= len(examples):
            # הרץ דוגמה ספציפית
            name, func = examples[int(choice)-1]
            print(f"\n{'='*20} {name} {'='*20}")
            func()
        else:
            print("❌ בחירה לא תקינה")
            
    except KeyboardInterrupt:
        print("\n👋 יציאה מהתוכנית")
    except Exception as e:
        print(f"❌ שגיאה: {e}")
    
    print("\n💡 לשימוש אמיתי:")
    print("  1. התקן: pip install yemot-speech[all]")
    print("  2. הגדר API keys")
    print("  3. הכן קבצי שמע אמיתיים")
    print("  4. התאם את הקוד לצרכים שלך")