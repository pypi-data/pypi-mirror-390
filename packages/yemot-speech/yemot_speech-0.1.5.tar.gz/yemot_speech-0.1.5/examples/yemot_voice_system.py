#!/usr/bin/env python3
"""
דוגמאות לתפריטים ומערכות קוליות של ימות המשיח
Examples for Yemot HaMashiach voice menus and systems
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from yemot_speech import TTS


def create_main_menu():
    """יצירת תפריט ראשי מלא"""
    print("📱 Creating Main Menu System")
    
    tts = TTS(provider='gtts', language='he')
    
    # 1. ברכת כניסה
    greeting = """
    שלום וברכה וברוכים הבאים למערכת ימות המשיח.
    אנא האזינו בעיון לאפשרויות הבאות ובחרו את המספר המתאים.
    """
    
    greeting_file = tts.save_audio(greeting.strip(), 'menu_greeting.mp3', slow=False)
    print(f"✅ Greeting: {greeting_file}")
    
    # 2. תפריט עיקרי
    menu_options = {
        '1': 'זמני התפילות והזמנים',
        '2': 'הודעות וחדשות הקהילה', 
        '3': 'לוח השבוע וחגים',
        '4': 'תרומות והקדשות',
        '5': 'שיעורים ולימודים',
        '6': 'לוח משפחות וזיווגים',
        '7': 'איחולים וברכות',
        '8': 'ארגון אירועים',
        '9': 'צור קשר ועזרה',
        '0': 'חזרה לתפריט הראשי'
    }
    
    menu_text = "תפריט ראשי. "
    for key, desc in menu_options.items():
        if key == '0':
            continue
        menu_text += f"לחצו {key} עבור {desc}. "
    menu_text += "לחצו 0 לחזרה לתפריט הראשי או 9 לעזרה."
    
    menu_file = tts.save_audio(menu_text, 'main_menu.mp3', slow=True)
    print(f"✅ Main menu: {menu_file}")
    
    return menu_options


def create_zmanim_system():
    """יצירת מערכת זמני תפילות"""
    print("🕐 Creating Zmanim System")
    
    tts = TTS(provider='gtts', language='he')
    
    # זמנים לדוגמה
    zmanim_data = {
        'today': {
            'shacharit': '06:30',
            'mincha': '18:30',
            'maariv': '20:00',
            'shabbat_in': '17:45',
            'shabbat_out': '18:50'
        }
    }
    
    # הודעות זמנים
    messages = [
        f"זמני התפילות להיום: שחרית בשעה {zmanim_data['today']['shacharit']}, מנחה בשעה {zmanim_data['today']['mincha']}, ומעריב בשעה {zmanim_data['today']['maariv']}.",
        
        f"כניסת שבת היום בשעה {zmanim_data['today']['shabbat_in']} ויציאת שבת מחר בשעה {zmanim_data['today']['shabbat_out']}.",
        
        "לחצו 1 לזמני התפילות, 2 לזמני שבת, 3 לזמני חגים, 0 לחזרה לתפריט הראשי."
    ]
    
    for i, message in enumerate(messages, 1):
        audio_file = tts.save_audio(message, f'zmanim_message_{i}.mp3')
        print(f"✅ Zmanim {i}: {audio_file}")


def create_announcement_system():
    """יצירת מערכת הודעות"""
    print("📢 Creating Announcement System")
    
    tts = TTS(provider='gtts', language='he')
    
    # סוגי הודעות
    announcements = [
        {
            'type': 'urgent',
            'text': 'הודעה חשובה: מחר לא יתקיים השיעור הרגיל. במקומו יתקיים שיעור מיוחד בשעה 20:00 באולם הגדול.',
            'priority': 'high'
        },
        {
            'type': 'reminder', 
            'text': 'תזכורת: תרומות לקופת צדקה יתקבלו עד סוף החודש במשרד הקהילה או דרך המערכת.',
            'priority': 'medium'
        },
        {
            'type': 'weekly',
            'text': 'שבת שלום לכל בית ישראל! השיעור השבועי יתקיים כרגיל ביום ראשון בשעה 20:30.',
            'priority': 'low'
        },
        {
            'type': 'event',
            'text': 'הזמנה לכולם: ערב מוזיקה וזמר יתקיים ביום שלישי בשעה 19:30. הכניסה חופשית.',
            'priority': 'medium'
        }
    ]
    
    for i, announcement in enumerate(announcements, 1):
        # הוספת פתיח מתאים לרמת החשיבות
        if announcement['priority'] == 'high':
            prefix = "הודעה דחופה וחשובה! "
        elif announcement['priority'] == 'medium':
            prefix = "הודעה חשובה: "
        else:
            prefix = "הודעה: "
            
        full_text = prefix + announcement['text'] + " תודה רבה."
        
        filename = f"announcement_{announcement['type']}.mp3"
        audio_file = tts.save_audio(full_text, filename)
        print(f"✅ {announcement['type'].title()}: {audio_file}")


def create_error_messages():
    """יצירת הודעות שגיאה ועזרה"""
    print("❗ Creating Error Messages")
    
    tts = TTS(provider='gtts', language='he')
    
    error_messages = {
        'invalid_input': 'מצטערים, לא זיהינו את הבחירה. אנא לחצו על מספר מ-0 עד 9 ונסו שוב.',
        'timeout': 'זמן הבחירה פקע. אנא הקישו את בחירתכם במהירות. חוזרים לתפריט הראשי.',
        'system_busy': 'המערכת עסוקה כרגע בשל עומס רב. אנא נסו שוב בעוד מספר דקות. תודה על הסבלנות.',
        'connection_error': 'יש בעיה בחיבור. אנא ודאו שהחיבור שלכם תקין ונסו שוב מאוחר יותר.',
        'help_general': 'זוהי מערכת ימות המשיח. לחצו על מספר הרצוי מהתפריט. לעזרה נוספת לחצו 9 או דברו עם מפעיל.',
        'help_navigation': 'לחזרה לתפריט הראשי לחצו 0. לחזרה לתפריט הקודם לחצו כוכבית. לעזרה לחצו 9.',
        'goodbye': 'תודה שהשתמשתם במערכת ימות המשיח. שיהיה לכם יום טוב וברכה. להתראות.'
    }
    
    for error_type, message in error_messages.items():
        audio_file = tts.save_audio(message, f'error_{error_type}.mp3')
        print(f"✅ {error_type}: {audio_file}")


def create_personalized_messages():
    """יצירת הודעות מותאמות אישית"""
    print("👤 Creating Personalized Messages")
    
    tts = TTS(provider='gtts', language='he')
    
    # דוגמאות הודעות מותאמות
    personal_templates = {
        'birthday': 'מזל טוב {name} ליום הולדתך! מאחלים לך שנה טובה ומתוקה מלאה בברכה והצלחה.',
        'anniversary': 'מזל טוב למשפחת {name} לרגל יום נישואיהם! יהי רצון שתזכו לעוד הרבה שנים בבריאות ואושר.',
        'welcome_new': 'ברוכים הבאים {name} לקהילתנו! אנו שמחים שהצטרפתם אלינו ומזמינים אתכם לכל הפעילויות.',
        'donation_thanks': 'תודה רבה {name} על תרומתכם הנדיבה לקופת הצדקה. זכותכם תגן עליכם ועל בני ביתכם.',
        'event_reminder': '{name}, זוהי תזכורת לאירוע שנרשמתם אליו מחר בשעה {time}. נתראה שם!'
    }
    
    # יצירת דוגמאות מלאות
    examples = [
        ('birthday', {'name': 'רחל כהן'}),
        ('anniversary', {'name': 'לוי'}),
        ('welcome_new', {'name': 'משפחת אברהם'}),
        ('donation_thanks', {'name': 'דוד שלמה'}),
        ('event_reminder', {'name': 'משה', 'time': '19:30'})
    ]
    
    for template_type, params in examples:
        message = personal_templates[template_type].format(**params)
        audio_file = tts.save_audio(message, f'personal_{template_type}_example.mp3')
        print(f"✅ {template_type}: {audio_file}")


def create_interactive_responses():
    """יצירת תגובות אינטראקטיביות"""
    print("🎯 Creating Interactive Responses")
    
    tts = TTS(provider='gtts', language='he')
    
    # תגובות לקלט משתמש נפוץ
    user_responses = {
        'yes_responses': [
            'מעולה! ממשיכים.',
            'תודה! עוברים לשלב הבא.',
            'נהדר! אנא המתינו לרגע.'
        ],
        'no_responses': [
            'בסדר, אין בעיה.',
            'מובן, חוזרים לתפריט הקודם.',
            'כמובן, אנא בחרו אפשרות אחרת.'
        ],
        'repeat_requests': [
            'כמובן, חוזרים על ההודעה.',
            'בשמחה, נחזור על המידע.',
            'אין בעיה, אנא הקשיבו שוב.'
        ],
        'clarification': [
            'אנא הבהירו את בקשתכם.',
            'לא הבנו בדיוק, תוכלו לחזור?',
            'אנא דברו בבירור יותר.'
        ]
    }
    
    for response_type, messages in user_responses.items():
        for i, message in enumerate(messages, 1):
            audio_file = tts.save_audio(message, f'response_{response_type}_{i}.mp3')
            print(f"✅ {response_type} {i}: {audio_file}")


def create_complete_yemot_system():
    """יצירת מערכת ימות המשיח מלאה"""
    print("\n🏛️ Creating Complete Yemot HaMashiach System")
    print("=" * 60)
    
    # צור את כל הרכיבים
    menu_options = create_main_menu()
    create_zmanim_system()
    create_announcement_system()
    create_error_messages()
    create_personalized_messages()
    create_interactive_responses()
    
    print("\n✅ Complete Yemot system created!")
    print("📁 All audio files have been generated")
    print("\n📋 System includes:")
    print("  🎙️ Main menu and greetings")
    print("  🕐 Zmanim (prayer times) system")
    print("  📢 Announcements and news")
    print("  ❗ Error messages and help")
    print("  👤 Personalized messages")
    print("  🎯 Interactive responses")
    
    return menu_options


if __name__ == "__main__":
    print("🎯 מערכות קוליות לימות המשיח - Yemot Voice Systems")
    print("=" * 60)
    
    try:
        # בדיקה שהספריה עובדת
        tts = TTS()  # ספק ברירת מחדל
        test_audio = tts.synthesize("בדיקת מערכת")
        print(f"✅ TTS system ready: {len(test_audio)} bytes")
        
        print("\n💡 למערכת מלאה:")
        print("  1. התקן: pip install yemot-speech[tts]")
        print("  2. הרץ: python yemot_voice_system.py")
        print("  3. הקבצים ישמרו בתיקיית הדוגמאות")
        
        print("\n🎯 לחצו Enter ליצירת מערכת דמו...")
        input()
        
        # יצור מערכת דמו קטנה
        print("🎬 Creating demo system...")
        demo_messages = [
            "ברוכים הבאים למערכת ימות המשיח",
            "תפריט ראשי: לחצו 1 לזמנים, 2 להודעות",
            "תודה שהשתמשתם במערכת"
        ]
        
        for i, message in enumerate(demo_messages, 1):
            audio = tts.synthesize(message)
            print(f"✅ Demo message {i}: {len(audio)} bytes")
        
        print("🎉 Demo system created successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 ודא שהספריה מותקנת: pip install yemot-speech")