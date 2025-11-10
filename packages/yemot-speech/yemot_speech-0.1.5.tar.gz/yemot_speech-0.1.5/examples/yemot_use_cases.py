#!/usr/bin/env python3
"""
מקרי שימוש נפוצים לשילוב yemot-speech עם Yemot
Common use cases for yemot-speech and Yemot integration
"""
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from yemot_speech import STT, TTS


class YemotUseCases:
    """מקרי שימוש נפוצים במערכות ימות המשיח"""
    
    def __init__(self):
        """אתחול המחלקה עם הגדרות בסיסיות"""
        self.stt = None
        self.tts = None
        self.yemot_client = None
        
    def setup_speech_services(
        self, 
        stt_provider: str = 'openai',
        tts_provider: str = 'gtts',
        api_key: Optional[str] = None,
        language: str = 'he'
    ):
        """הגדרת שירותי הדיבור"""
        try:
            self.stt = STT(provider=stt_provider, api_key=api_key)
            self.tts = TTS(provider=tts_provider, language=language)
            print(f"✅ Speech services initialized: STT={stt_provider}, TTS={tts_provider}")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize speech services: {e}")
            return False
    
    def use_case_1_voicemail_transcription(self):
        """מקרה שימוש 1: המרת הודעות קוליות לטקסט"""
        print("\n📱 Use Case 1: Voicemail Transcription")
        print("-" * 50)
        
        # דמיית קבצי הודעות קוליות
        voicemail_files = [
            "voicemail_001.wav",  # "שלום, אני רוצה לדעת מתי השיעור השבועי"
            "voicemail_002.wav",  # "יש לי שאלה על זמני התפילות"
            "voicemail_003.wav",  # "תודה על ההודעה, אני מעוניין להשתתף"
        ]
        
        # סימולציה של תמלול הודעות
        simulated_transcriptions = [
            "שלום, אני רוצה לדעת מתי השיעור השבועי התורני בבית הכנסת",
            "יש לי שאלה חשובה על זמני התפילות לשבת הקרובה", 
            "תודה רבה על ההודעה, אני מאוד מעוניין להשתתף בשיעור"
        ]
        
        results = []
        for i, (file, simulated_text) in enumerate(zip(voicemail_files, simulated_transcriptions), 1):
            print(f"\n🎵 Processing voicemail {i}: {file}")
            
            # במציאות: transcription = self.stt.transcribe(file)
            transcription = simulated_text  # דמיה
            
            # ניתוח התוכן
            analysis = self._analyze_voicemail_content(transcription)
            
            result = {
                'file': file,
                'transcription': transcription,
                'category': analysis['category'],
                'priority': analysis['priority'],
                'auto_response': analysis['suggested_response']
            }
            
            results.append(result)
            
            print(f"📝 Transcription: {transcription}")
            print(f"🏷️ Category: {analysis['category']}")
            print(f"⚡ Priority: {analysis['priority']}")
            print(f"🤖 Suggested response: {analysis['suggested_response']}")
        
        # יצירת סיכום
        self._create_voicemail_summary(results)
        
        return results
    
    def _analyze_voicemail_content(self, text: str) -> Dict[str, Any]:
        """ניתוח תוכן הודעה קולית"""
        text_lower = text.lower()
        
        analysis = {
            'category': 'general',
            'priority': 'medium',
            'suggested_response': 'תודה על הפנייה, נחזור אליכם בהקדם'
        }
        
        # זיהוי קטגוריה
        if any(word in text_lower for word in ['שיעור', 'לימוד', 'הרצאה']):
            analysis['category'] = 'education'
            analysis['suggested_response'] = 'השיעור השבועי מתקיים בימי ראשון בשעה 20:30'
            
        elif any(word in text_lower for word in ['זמנים', 'תפילות', 'שעות']):
            analysis['category'] = 'zmanim'
            analysis['suggested_response'] = 'זמני התפילות מתעדכנים מדי שבוע באתר הקהילה'
            
        elif any(word in text_lower for word in ['השתתפות', 'רישום', 'מעוניין']):
            analysis['category'] = 'registration'
            analysis['priority'] = 'high'
            analysis['suggested_response'] = 'תודה על הרישום, נשלח אליכם פרטים נוספים'
            
        elif any(word in text_lower for word in ['דחוף', 'חשוב', 'בעיה']):
            analysis['priority'] = 'high'
            analysis['suggested_response'] = 'קיבלנו את הפנייה הדחופה, נחזור אליכם בהקדם'
        
        return analysis
    
    def _create_voicemail_summary(self, results: List[Dict]):
        """יצירת סיכום הודעות קוליות"""
        print(f"\n📊 Voicemail Summary Report")
        print("=" * 40)
        
        categories = {}
        priority_counts = {'high': 0, 'medium': 0, 'low': 0}
        
        for result in results:
            category = result['category']
            priority = result['priority']
            
            categories[category] = categories.get(category, 0) + 1
            priority_counts[priority] += 1
        
        print(f"📈 Total messages: {len(results)}")
        print(f"📊 By category:")
        for cat, count in categories.items():
            print(f"   {cat}: {count}")
        
        print(f"⚡ By priority:")
        for priority, count in priority_counts.items():
            print(f"   {priority}: {count}")
        
        # יצירת תגובה אוטומטית
        if self.tts:
            summary_text = f"""
            דוח הודעות קוליות יומי.
            התקבלו {len(results)} הודעות היום.
            {priority_counts['high']} הודעות בעדיפות גבוהה דורשות מענה מיידי.
            """
            
            summary_file = f"voicemail_summary_{datetime.now().strftime('%Y%m%d')}.mp3"
            try:
                # במציאות: self.tts.save_audio(summary_text.strip(), summary_file)
                print(f"🔊 Summary audio would be saved to: {summary_file}")
            except:
                print(f"⚠️ Could not create summary audio")
    
    def use_case_2_automated_announcements(self):
        """מקרה שימוש 2: יצירת הודעות אוטומטיות"""
        print("\n📢 Use Case 2: Automated Announcements")
        print("-" * 50)
        
        # הודעות שונות לאירועים שונים
        announcements = {
            'daily_zmanim': {
                'text': self._generate_zmanim_announcement(),
                'frequency': 'daily',
                'time': '06:00'
            },
            'weekly_shiur': {
                'text': 'הודעה שבועית: השיעור יתקיים מחר ביום ראשון בשעה 20:30 באולם הגדול. הנושא השבוע: הלכות שבת.',
                'frequency': 'weekly', 
                'time': 'saturday_evening'
            },
            'holiday_greeting': {
                'text': self._generate_holiday_greeting(),
                'frequency': 'as_needed',
                'time': 'before_holiday'
            },
            'urgent_notification': {
                'text': 'הודעה חשובה: בגלל מזג אוויר סוער, התפילה תתקיים בבניין הראשי ולא בחצר. אנא הגיעו מוקדם.',
                'frequency': 'as_needed',
                'time': 'immediate'
            }
        }
        
        for announcement_type, details in announcements.items():
            print(f"\n🎯 Creating {announcement_type}...")
            print(f"📝 Text: {details['text'][:100]}...")
            print(f"⏰ Frequency: {details['frequency']}")
            
            # יצירת קובץ שמע
            audio_file = f"announcement_{announcement_type}_{datetime.now().strftime('%Y%m%d')}.mp3"
            
            try:
                # במציאות: self.tts.save_audio(details['text'], audio_file)
                print(f"🔊 Audio created: {audio_file}")
                
                # הגדרת הפצה
                distribution = self._plan_announcement_distribution(announcement_type, details)
                print(f"📡 Distribution: {distribution}")
                
            except Exception as e:
                print(f"❌ Failed to create {announcement_type}: {e}")
    
    def _generate_zmanim_announcement(self) -> str:
        """יצירת הודעת זמנים יומית"""
        # במציאות נמשוך מAPI של זמנים
        return """
        זמני התפילות היום:
        שחרית בשעה 6 ו-30 דקות,
        מנחה בשעה 6 ו-30 אחר הצהריים,
        מעריב בשעה 8 בערב.
        שבוע טוב לכולם!
        """
    
    def _generate_holiday_greeting(self) -> str:
        """יצירת ברכת חג"""
        return """
        לקראת שבת קודש הבעלת,
        אנו מאחלים לכל קהל קדוש שלנו
        שבת שלום ומבורך,
        מלא באושר ובריאות וכל טוב.
        """
    
    def _plan_announcement_distribution(self, announcement_type: str, details: Dict) -> str:
        """תכנון הפצת הודעה"""
        if details['frequency'] == 'daily':
            return f"שידור יומי בשעה {details['time']}"
        elif details['frequency'] == 'weekly':
            return "שידור שבועי במוצאי שבת"
        elif details['time'] == 'immediate':
            return "שידור מיידי לכל הרשומים"
        else:
            return "שידור לפי צורך"
    
    def use_case_3_interactive_menu_processing(self):
        """מקרה שימוש 3: עיבוד תפריט אינטראקטיבי"""
        print("\n🎛️ Use Case 3: Interactive Menu Processing")
        print("-" * 50)
        
        # סימולציה של תגובות משתמשים לתפריט
        user_responses = [
            "אחד",           # בחירה 1 - זמנים
            "שתיים",         # בחירה 2 - הודעות  
            "זמני תפילות",   # דיבור חופשי
            "אני רוצה עזרה", # בקשת עזרה
            "לא הבנתי",      # בעיה
        ]
        
        # תפריט המערכת
        menu_structure = {
            '1': {
                'title': 'זמני תפילות',
                'response': 'זמני התפילות היום: שחרית 6:30, מנחה 18:30, מעריב 20:00'
            },
            '2': {
                'title': 'הודעות',
                'response': 'יש 3 הודעות חדשות במערכת. לחצו 1 לשמיעת ההודעות'
            },
            '9': {
                'title': 'עזרה',
                'response': 'מרכז עזרה: לחצו 0 לתפריט ראשי, 9 לחזרה על ההודעה'
            }
        }
        
        results = []
        for i, user_input in enumerate(user_responses, 1):
            print(f"\n🎤 Processing user input {i}: '{user_input}'")
            
            # זיהוי כוונת המשתמש
            intent = self._recognize_intent(user_input, menu_structure)
            
            # יצירת תגובה מתאימה
            response = self._generate_menu_response(intent, menu_structure)
            
            result = {
                'user_input': user_input,
                'recognized_intent': intent,
                'system_response': response
            }
            
            results.append(result)
            
            print(f"🎯 Intent: {intent}")
            print(f"🤖 Response: {response}")
            
            # יצירת תגובה קולית
            if self.tts and response:
                audio_file = f"menu_response_{i}.mp3"
                try:
                    # במציאות: self.tts.save_audio(response, audio_file)
                    print(f"🔊 Audio response created: {audio_file}")
                except:
                    print("⚠️ Could not create audio response")
        
        # ניתוח ביצועי התפריט
        self._analyze_menu_performance(results)
        
        return results
    
    def _recognize_intent(self, user_input: str, menu_structure: Dict) -> str:
        """זיהוי כוונת המשתמש"""
        user_input_lower = user_input.lower()
        
        # זיהוי מספרים מילוליים
        number_words = {
            'אחד': '1', 'שתיים': '2', 'שלוש': '3',
            'ארבע': '4', 'חמש': '5', 'תשע': '9', 'אפס': '0'
        }
        
        for word, number in number_words.items():
            if word in user_input_lower and number in menu_structure:
                return f"menu_option_{number}"
        
        # זיהוי נושאים
        if any(word in user_input_lower for word in ['זמנים', 'תפילות']):
            return 'menu_option_1'
        elif any(word in user_input_lower for word in ['הודעות', 'חדשות']):
            return 'menu_option_2'  
        elif any(word in user_input_lower for word in ['עזרה', 'לא הבנתי', 'לא יודע']):
            return 'menu_option_9'
        
        return 'unknown_intent'
    
    def _generate_menu_response(self, intent: str, menu_structure: Dict) -> str:
        """יצירת תגובה לכוונה מזוהה"""
        if intent.startswith('menu_option_'):
            option = intent.split('_')[-1]
            if option in menu_structure:
                return menu_structure[option]['response']
        
        return 'לא הבנתי את בחירתכם. אנא לחצו על מספר מהתפריט או לחצו 9 לעזרה.'
    
    def _analyze_menu_performance(self, results: List[Dict]):
        """ניתוח ביצועי התפריט"""
        print(f"\n📊 Menu Performance Analysis")
        print("=" * 40)
        
        total_inputs = len(results)
        recognized = sum(1 for r in results if not r['recognized_intent'].startswith('unknown'))
        recognition_rate = (recognized / total_inputs) * 100
        
        print(f"📈 Total user inputs: {total_inputs}")
        print(f"✅ Successfully recognized: {recognized}")
        print(f"📊 Recognition rate: {recognition_rate:.1f}%")
        
        # ההצעות לשיפור
        if recognition_rate < 80:
            print("💡 Suggestions for improvement:")
            print("   - Add more voice training data")
            print("   - Improve intent recognition algorithms")
            print("   - Add more alternative phrasings")
    
    def use_case_4_campaign_feedback_analysis(self):
        """מקרה שימוש 4: ניתוח משוב קמפיינים"""
        print("\n📊 Use Case 4: Campaign Feedback Analysis")
        print("-" * 50)
        
        # סימולציה של תגובות לקמפיין
        campaign_responses = [
            "כן, אני מעוניין להשתתף בשיעור",
            "לא יכול להגיע השבוע, אולי בפעם הבאה",
            "תודה על ההזמנה, אני בהחלט אגיע",
            "לא מעוניין, תודה",
            "איך אפשר להירשם? יש לי שאלות",
            "מעולה! אבוא עם המשפחה",
            "לא יודע עדיין, אני אעדכן",
            "בטוח! נתראה שם"
        ]
        
        analysis_results = {
            'positive_responses': 0,
            'negative_responses': 0,
            'neutral_responses': 0,
            'questions': 0,
            'total_responses': len(campaign_responses)
        }
        
        detailed_analysis = []
        
        for i, response in enumerate(campaign_responses, 1):
            print(f"\n🎤 Analyzing response {i}: '{response}'")
            
            # ניתוח סנטימנט ותוכן
            sentiment = self._analyze_sentiment(response)
            content_analysis = self._analyze_response_content(response)
            
            # עדכון סטטיסטיקות
            if sentiment == 'positive':
                analysis_results['positive_responses'] += 1
            elif sentiment == 'negative':
                analysis_results['negative_responses'] += 1
            else:
                analysis_results['neutral_responses'] += 1
                
            if '?' in response or any(word in response.lower() for word in ['איך', 'מה', 'מתי', 'איפה']):
                analysis_results['questions'] += 1
            
            result = {
                'response_id': i,
                'text': response,
                'sentiment': sentiment,
                'intent': content_analysis['intent'],
                'requires_followup': content_analysis['requires_followup']
            }
            
            detailed_analysis.append(result)
            
            print(f"😊 Sentiment: {sentiment}")
            print(f"🎯 Intent: {content_analysis['intent']}")
            print(f"📞 Follow-up needed: {content_analysis['requires_followup']}")
        
        # הצגת סיכום
        self._display_campaign_summary(analysis_results, detailed_analysis)
        
        # יצירת תגובה אוטומטית
        self._create_campaign_followup(analysis_results)
        
        return detailed_analysis
    
    def _analyze_sentiment(self, text: str) -> str:
        """ניתוח רגש התגובה"""
        text_lower = text.lower()
        
        positive_indicators = ['כן', 'בטוח', 'מעולה', 'תודה', 'אגיע', 'מעוניין']
        negative_indicators = ['לא', 'לא יכול', 'לא מעוניין']
        
        positive_score = sum(1 for word in positive_indicators if word in text_lower)
        negative_score = sum(1 for word in negative_indicators if word in text_lower)
        
        if positive_score > negative_score:
            return 'positive'
        elif negative_score > positive_score:
            return 'negative'
        else:
            return 'neutral'
    
    def _analyze_response_content(self, text: str) -> Dict[str, Any]:
        """ניתוח תוכן התגובה"""
        text_lower = text.lower()
        
        analysis = {
            'intent': 'general_response',
            'requires_followup': False
        }
        
        if any(word in text_lower for word in ['שאלות', 'איך', 'מה']):
            analysis['intent'] = 'question'
            analysis['requires_followup'] = True
        elif any(word in text_lower for word in ['מעוניין', 'אגיע', 'כן']):
            analysis['intent'] = 'positive_confirmation'
        elif any(word in text_lower for word in ['לא מעוניין', 'לא יכול']):
            analysis['intent'] = 'decline'
        elif any(word in text_lower for word in ['אולי', 'לא יודע']):
            analysis['intent'] = 'uncertain'
            analysis['requires_followup'] = True
        
        return analysis
    
    def _display_campaign_summary(self, stats: Dict, details: List[Dict]):
        """הצגת סיכום קמפיין"""
        print(f"\n📈 Campaign Response Summary")
        print("=" * 40)
        
        total = stats['total_responses']
        print(f"📊 Response Statistics:")
        print(f"   Total responses: {total}")
        print(f"   😊 Positive: {stats['positive_responses']} ({stats['positive_responses']/total*100:.1f}%)")
        print(f"   😐 Neutral: {stats['neutral_responses']} ({stats['neutral_responses']/total*100:.1f}%)")
        print(f"   😕 Negative: {stats['negative_responses']} ({stats['negative_responses']/total*100:.1f}%)")
        print(f"   ❓ Questions: {stats['questions']}")
        
        followup_needed = sum(1 for d in details if d['requires_followup'])
        print(f"\n📞 Follow-up Actions:")
        print(f"   Responses requiring follow-up: {followup_needed}")
    
    def _create_campaign_followup(self, stats: Dict):
        """יצירת מעקב אחר קמפיין"""
        positive_rate = stats['positive_responses'] / stats['total_responses'] * 100
        
        if positive_rate > 70:
            followup_message = f"""
            תודה רבה לכולם!
            התגובה לקמפיין הייתה מעולה - {positive_rate:.0f}% תגובות חיוביות.
            נתראה בשיעור!
            """
        elif positive_rate > 40:
            followup_message = f"""
            תודה לכל מי שהגיב!
            קיבלנו תגובה טובה - {positive_rate:.0f}% אישרו השתתפות.
            מי שעדיין לא החליט מוזמן לפנות אלינו.
            """
        else:
            followup_message = f"""
            תודה לכל מי שהגיב.
            אנו עדיין מחכים לתגובות נוספות.
            לפרטים נוספים אנא פנו אלינו.
            """
        
        if self.tts:
            try:
                # במציאות: self.tts.save_audio(followup_message.strip(), "campaign_followup.mp3")
                print(f"🔊 Follow-up message created: campaign_followup.mp3")
            except:
                print("⚠️ Could not create follow-up audio")
        
        print(f"\n📝 Follow-up message: {followup_message.strip()}")


def main():
    """הפעלת כל מקרי השימוש"""
    print("🎯 Yemot-Speech Common Use Cases")
    print("=" * 50)
    
    use_cases = YemotUseCases()
    
    # אתחול שירותי דיבור
    success = use_cases.setup_speech_services()
    if not success:
        print("⚠️ Running in demo mode without real speech services")
    
    print("\n🚀 Running all use cases...")
    
    try:
        # מקרה שימוש 1: תמלול הודעות קוליות
        use_cases.use_case_1_voicemail_transcription()
        
        # מקרה שימוש 2: הודעות אוטומטיות
        use_cases.use_case_2_automated_announcements()
        
        # מקרה שימוש 3: תפריט אינטראקטיבי
        use_cases.use_case_3_interactive_menu_processing()
        
        # מקרה שימוש 4: ניתוח משוב קמפיינים
        use_cases.use_case_4_campaign_feedback_analysis()
        
        print("\n✅ All use cases completed successfully!")
        
    except Exception as e:
        print(f"❌ Error running use cases: {e}")
    
    print(f"\n💡 These examples show how yemot-speech can enhance:")
    print(f"   📱 Voicemail management and transcription")
    print(f"   📢 Automated announcement generation")
    print(f"   🎛️ Interactive voice menu processing")
    print(f"   📊 Campaign response analysis")


if __name__ == "__main__":
    main()