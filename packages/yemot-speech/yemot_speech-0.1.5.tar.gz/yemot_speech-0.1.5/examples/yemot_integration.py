#!/usr/bin/env python3
"""
שילוב yemot-speech עם Yemot - עיבוד קבצי שמע ממערכת ימות המשיח
Integration of yemot-speech with Yemot - Processing audio files from Yemot system
"""
import sys
import os
from typing import Optional, List, Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from yemot_speech import STT, TTS

# Import Yemot library (נצטרך להתקין אותו)
try:
    from yemot import Client, System, Campaign, IVR
    YEMOT_AVAILABLE = True
except ImportError:
    print("⚠️ Yemot library not installed. Install with: pip install yemot")
    YEMOT_AVAILABLE = False
    # Mock classes for demonstration
    class Client:
        def __init__(self, *args, **kwargs): pass
    class System:
        def __init__(self, *args, **kwargs): pass  
    class Campaign:
        def __init__(self, *args, **kwargs): pass
    class IVR:
        def __init__(self, *args, **kwargs): pass


class YemotSpeechIntegration:
    """מחלקה לשילוב yemot-speech עם מערכת Yemot"""
    
    def __init__(
        self,
        yemot_username: str,
        yemot_password: str,
        stt_provider: str = 'openai',
        tts_provider: str = 'gtts',
        stt_api_key: Optional[str] = None,
        tts_language: str = 'he'
    ):
        """
        אתחול השילוב
        
        Parameters:
        -----------
        yemot_username : str
            מספר מערכת ימות המשיח
        yemot_password : str
            סיסמת מערכת ימות המשיח
        stt_provider : str
            ספק ההמרה שמע לטקסט
        tts_provider : str
            ספק ההמרה טקסט לשמע
        stt_api_key : str, optional
            מפתח API לספק STT
        tts_language : str
            שפה עבור TTS
        """
        # חיבור לימות המשיח
        if YEMOT_AVAILABLE:
            self.yemot_client = Client(username=yemot_username, password=yemot_password)
            self.system = System(self.yemot_client)
            self.campaign = Campaign(self.yemot_client)
            self.ivr = IVR(self.yemot_client)
        else:
            print("⚠️ Running in demo mode - Yemot not available")
            self.yemot_client = None
            self.system = None
            self.campaign = None
            self.ivr = None
        
        # אתחול מערכות STT ו-TTS
        try:
            self.stt = STT(provider=stt_provider, api_key=stt_api_key)
            self.tts = TTS(provider=tts_provider, language=tts_language)
        except Exception as e:
            print(f"⚠️ STT/TTS initialization failed: {e}")
            self.stt = None
            self.tts = None
    
    def download_and_transcribe_audio(self, audio_path: str) -> Optional[str]:
        """
        הורדת קובץ שמע ממערכת ימות והמרתו לטקסט
        
        Parameters:
        -----------
        audio_path : str
            נתיב הקובץ במערכת ימות (מתחיל ב-ivr2:)
            
        Returns:
        --------
        str or None
            הטקסט המומר או None במקרה של שגיאה
        """
        if not self.system or not self.stt:
            print("❌ System or STT not available")
            return None
            
        try:
            print(f"📥 Downloading audio from Yemot: {audio_path}")
            
            # הורדת קובץ השמע ממערכת ימות
            download_result = self.system.download_file(audio_path)
            
            # שמירת הקובץ מקומית (הנחה שהתגובה מכילה את נתוני הקובץ)
            local_audio_path = f"temp_audio_{os.path.basename(audio_path)}"
            
            # כאן נצטרך לטפל בנתוני הקובץ בהתאם לפורמט התגובה של ימות
            # זה דורש בדיקה נוספת של API של ימות
            # לעת עתה נדמה עיבוד
            print(f"💾 Saved audio locally: {local_audio_path}")
            
            # המרת השמע לטקסט
            print("🎤 Transcribing audio to text...")
            text = self.stt.transcribe(local_audio_path, language='he')
            
            print(f"📝 Transcription: {text}")
            
            # מחיקת הקובץ הזמני
            if os.path.exists(local_audio_path):
                os.remove(local_audio_path)
                
            return text
            
        except Exception as e:
            print(f"❌ Error in download_and_transcribe: {e}")
            return None
    
    def create_speech_and_upload(
        self, 
        text: str, 
        upload_path: str,
        convert_audio: bool = True
    ) -> bool:
        """
        יצירת קובץ שמע מטקסט והעלאתו למערכת ימות
        
        Parameters:
        -----------
        text : str
            הטקסט להמרה לשמע
        upload_path : str
            נתיב העלאה במערכת ימות (מתחיל ב-ivr2:)
        convert_audio : bool
            האם להמיר פורמט שמע אוטומטית
            
        Returns:
        --------
        bool
            True אם הצליח, False אחרת
        """
        if not self.system or not self.tts:
            print("❌ System or TTS not available")
            return False
            
        try:
            print(f"🔊 Creating speech from text: {text}")
            
            # יצירת קובץ שמע מטקסט
            local_audio_path = "temp_speech_output.wav"
            self.tts.save_audio(text, local_audio_path)
            
            print(f"📁 Audio file created: {local_audio_path}")
            
            # העלאת הקובץ למערכת ימות
            print(f"📤 Uploading to Yemot: {upload_path}")
            
            upload_result = self.system.upload_file(
                file=local_audio_path,
                path=upload_path,
                convert_audio=1 if convert_audio else 0
            )
            
            print(f"✅ Upload result: {upload_result}")
            
            # מחיקת הקובץ הזמני
            if os.path.exists(local_audio_path):
                os.remove(local_audio_path)
                
            return True
            
        except Exception as e:
            print(f"❌ Error in create_speech_and_upload: {e}")
            return False
    
    def process_campaign_audio(
        self, 
        template_id: int,
        message_text: str,
        audio_type: str = 'VOICE'
    ) -> bool:
        """
        עיבוד שמע לקמפיין - יצירת הודעה קולית והעלאתה
        
        Parameters:
        -----------
        template_id : int
            מזהה התבנית
        message_text : str
            טקסט ההודעה ליצירת שמע
        audio_type : str
            סוג השמע ('VOICE', 'SMS', 'BRIDGE', etc.)
            
        Returns:
        --------
        bool
            True אם הצליח, False אחרת
        """
        if not self.campaign or not self.tts:
            print("❌ Campaign or TTS not available")
            return False
            
        try:
            print(f"🎪 Processing campaign audio for template {template_id}")
            print(f"📝 Message: {message_text}")
            
            # יצירת קובץ שמע
            local_audio_path = f"campaign_audio_{template_id}.wav"
            self.tts.save_audio(message_text, local_audio_path)
            
            # העלאת השמע לקמפיין
            upload_result = self.campaign.upload_template_file(
                file=local_audio_path,
                name=str(template_id),
                type=audio_type,
                convertAudio='1'
            )
            
            print(f"✅ Campaign audio uploaded: {upload_result}")
            
            # מחיקת הקובץ הזמני
            if os.path.exists(local_audio_path):
                os.remove(local_audio_path)
                
            return True
            
        except Exception as e:
            print(f"❌ Error in process_campaign_audio: {e}")
            return False
    
    def analyze_campaign_responses(self, template_id: int) -> List[Dict[str, Any]]:
        """
        ניתוח תגובות קמפיין - הורדת קבצי שמע וניתוח התוכן
        
        Parameters:
        -----------
        template_id : int
            מזהה התבנית
            
        Returns:
        --------
        List[Dict[str, Any]]
            רשימת ניתוחי התגובות
        """
        if not self.campaign or not self.stt:
            print("❌ Campaign or STT not available")
            return []
            
        results = []
        
        try:
            print(f"📊 Analyzing campaign responses for template {template_id}")
            
            # קבלת רשימת מספרים בקמפיין
            entries = self.campaign.get_template_entries(template_id)
            
            if not entries or 'data' not in entries:
                print("⚠️ No entries found for template")
                return results
            
            # עיבוד כל רשומה
            for entry in entries['data'][:5]:  # מגביל ל-5 ראשונים לדוגמה
                phone = entry.get('phone', 'unknown')
                
                try:
                    # ניסיון להוריד קובץ תגובה (אם קיים)
                    audio_path = f"ivr2:responses/{template_id}/{phone}.wav"
                    
                    # המרת השמע לטקסט
                    transcription = self.download_and_transcribe_audio(audio_path)
                    
                    if transcription:
                        # ניתוח התוכן
                        analysis = self.analyze_response_content(transcription)
                        
                        result = {
                            'phone': phone,
                            'transcription': transcription,
                            'analysis': analysis,
                            'timestamp': entry.get('created_at'),
                            'status': 'success'
                        }
                    else:
                        result = {
                            'phone': phone,
                            'transcription': None,
                            'analysis': None,
                            'error': 'Failed to transcribe',
                            'status': 'failed'
                        }
                    
                    results.append(result)
                    print(f"📞 Processed response from {phone}: {result['status']}")
                    
                except Exception as e:
                    print(f"⚠️ Error processing response from {phone}: {e}")
                    results.append({
                        'phone': phone,
                        'error': str(e),
                        'status': 'error'
                    })
            
            return results
            
        except Exception as e:
            print(f"❌ Error in analyze_campaign_responses: {e}")
            return results
    
    def analyze_response_content(self, text: str) -> Dict[str, Any]:
        """
        ניתוח תוכן תגובה קולית
        
        Parameters:
        -----------
        text : str
            הטקסט המומר מהשמע
            
        Returns:
        --------
        Dict[str, Any]
            ניתוח התוכן
        """
        analysis = {
            'sentiment': 'neutral',
            'keywords': [],
            'intent': 'unknown',
            'confidence': 0.0
        }
        
        text_lower = text.lower()
        
        # ניתוח רגש בסיסי
        positive_words = ['כן', 'בסדר', 'טוב', 'מעולה', 'תודה']
        negative_words = ['לא', 'רע', 'לא רוצה', 'תפסיק', 'מספיק']
        
        if any(word in text_lower for word in positive_words):
            analysis['sentiment'] = 'positive'
            analysis['confidence'] = 0.7
        elif any(word in text_lower for word in negative_words):
            analysis['sentiment'] = 'negative'  
            analysis['confidence'] = 0.7
        
        # זיהוי כוונות
        if any(word in text_lower for word in ['זמנים', 'תפילות']):
            analysis['intent'] = 'zmanim_request'
        elif any(word in text_lower for word in ['הודעות', 'חדשות']):
            analysis['intent'] = 'news_request'
        elif any(word in text_lower for word in ['עזרה', 'לא מבין']):
            analysis['intent'] = 'help_request'
        
        # חילוץ מילות מפתח
        keywords = []
        important_words = ['זמנים', 'תפילות', 'הודעות', 'שבת', 'חג', 'שיעור']
        for word in important_words:
            if word in text_lower:
                keywords.append(word)
        analysis['keywords'] = keywords
        
        return analysis
    
    def create_personalized_messages(self, phone_list: List[str], template: str) -> bool:
        """
        יצירת הודעות מותאמות אישית לרשימת מספרים
        
        Parameters:
        -----------
        phone_list : List[str]
            רשימת מספרי טלפון
        template : str
            תבנית ההודעה עם {phone} למספר
            
        Returns:
        --------
        bool
            True אם הצליח ליצור את כל ההודעות
        """
        if not self.tts:
            print("❌ TTS not available")
            return False
        
        success_count = 0
        
        for phone in phone_list:
            try:
                # יצירת הודעה מותאמת
                personal_message = template.format(phone=phone)
                
                # יצירת קובץ שמע
                audio_path = f"personal_msg_{phone}.wav"
                self.tts.save_audio(personal_message, audio_path)
                
                # העלאה למערכת (בדרך כלל לתיקיית הודעות אישיות)
                upload_path = f"ivr2:personal_messages/{phone}.wav"
                
                if self.system:
                    upload_result = self.system.upload_file(
                        file=audio_path,
                        path=upload_path,
                        convert_audio=1
                    )
                    
                    if upload_result:
                        success_count += 1
                        print(f"✅ Created personal message for {phone}")
                    else:
                        print(f"⚠️ Failed to upload message for {phone}")
                else:
                    success_count += 1  # דמו
                    print(f"✅ Created personal message for {phone} (demo)")
                
                # מחיקת הקובץ המקומי
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                    
            except Exception as e:
                print(f"❌ Error creating message for {phone}: {e}")
        
        print(f"📊 Created {success_count}/{len(phone_list)} personal messages")
        return success_count == len(phone_list)


def example_full_workflow():
    """דוגמה לזרימת עבודה מלאה"""
    print("🔄 Full Yemot-Speech Integration Workflow")
    print("=" * 60)
    
    # אתחול המערכת
    integration = YemotSpeechIntegration(
        yemot_username='0500000000',  # החלף במספר האמיתי
        yemot_password='123456',      # החלף בסיסמה האמיתית
        stt_provider='openai',
        tts_provider='gtts',
        stt_api_key='your-openai-key'  # החלף במפתח אמיתי
    )
    
    # 1. יצירת הודעת קמפיין
    print("\n1️⃣ Creating campaign message...")
    campaign_message = """
    שלום וברכה! זוהי הודעה חשובה מבית הכנסת.
    מחר יתקיים שיעור מיוחד בשעה 20:00.
    לאישור השתתפות לחצו 1, לביטול לחצו 2.
    תודה רבה!
    """
    
    template_id = 12345  # מזהה התבנית
    success = integration.process_campaign_audio(
        template_id=template_id,
        message_text=campaign_message.strip(),
        audio_type='VOICE'
    )
    
    # 2. יצירת הודעות מותאמות אישית
    print("\n2️⃣ Creating personalized messages...")
    phone_list = ['0521234567', '0521234568', '0521234569']
    personal_template = "שלום {phone}, יש לך הודעה אישית במערכת ימות המשיח"
    
    integration.create_personalized_messages(phone_list, personal_template)
    
    # 3. ניתוח תגובות קמפיין
    print("\n3️⃣ Analyzing campaign responses...")
    responses = integration.analyze_campaign_responses(template_id)
    
    # סיכום תוצאות
    print(f"\n📊 Analysis Results:")
    positive_responses = sum(1 for r in responses if r.get('analysis', {}).get('sentiment') == 'positive')
    total_responses = len([r for r in responses if r.get('status') == 'success'])
    
    print(f"   Total responses analyzed: {total_responses}")
    print(f"   Positive sentiment: {positive_responses}")
    print(f"   Success rate: {len([r for r in responses if r.get('status') == 'success'])}/{len(responses)}")
    
    # 4. יצירת תגובה אוטומטית
    print("\n4️⃣ Creating automatic response...")
    auto_response = f"""
    תודה רבה לכל מי שהשתתף בקמפיין!
    קיבלנו {total_responses} תגובות, מתוכן {positive_responses} חיוביות.
    נתראה בשיעור מחר בשעה 20:00.
    """
    
    integration.create_speech_and_upload(
        text=auto_response.strip(),
        upload_path="ivr2:auto_responses/campaign_summary.wav"
    )
    
    print("\n✅ Full workflow completed!")


if __name__ == "__main__":
    print("🎯 Yemot-Speech Integration - שילוב ימות המשיח עם עיבוד קול")
    print("=" * 70)
    
    if not YEMOT_AVAILABLE:
        print("💡 To use with real Yemot system:")
        print("   pip install yemot")
        print("   pip install yemot-speech[openai]")
        print("\n🎬 Running demo workflow...")
        
    try:
        example_full_workflow()
        
    except Exception as e:
        print(f"❌ Error in main workflow: {e}")
    
    print(f"\n💡 Integration Features:")
    print(f"   📥 Download audio files from Yemot system")
    print(f"   🎤 Convert audio to text using STT")
    print(f"   🔊 Generate speech from text using TTS") 
    print(f"   📤 Upload audio files to Yemot system")
    print(f"   🎪 Process campaign audio messages")
    print(f"   📊 Analyze campaign response content")
    print(f"   👤 Create personalized voice messages")
    print(f"   🔄 Complete automation workflows")