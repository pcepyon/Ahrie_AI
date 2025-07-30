"""Telegram keyboard builders for creating interactive buttons."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from typing import List, Dict, Any, Optional


class KeyboardBuilder:
    """
    Builder class for creating Telegram keyboards and buttons.
    """
    
    def create_main_menu(self, language: str = "en") -> InlineKeyboardMarkup:
        """
        Create main menu keyboard.
        
        Args:
            language: Language code for button labels
            
        Returns:
            InlineKeyboardMarkup object
        """
        buttons = {
            "en": [
                [
                    InlineKeyboardButton("🏥 Procedures", callback_data="menu_procedures"),
                    InlineKeyboardButton("🏨 Clinics", callback_data="menu_clinics")
                ],
                [
                    InlineKeyboardButton("📹 Reviews", callback_data="menu_reviews"),
                    InlineKeyboardButton("🕌 Halal Guide", callback_data="menu_halal")
                ],
                [
                    InlineKeyboardButton("💬 Start Consultation", callback_data="start_consultation"),
                ],
                [
                    InlineKeyboardButton("🌐 Language", callback_data="menu_language"),
                    InlineKeyboardButton("ℹ️ Help", callback_data="menu_help")
                ]
            ],
            "ar": [
                [
                    InlineKeyboardButton("🏥 العمليات", callback_data="menu_procedures"),
                    InlineKeyboardButton("🏨 العيادات", callback_data="menu_clinics")
                ],
                [
                    InlineKeyboardButton("📹 التقييمات", callback_data="menu_reviews"),
                    InlineKeyboardButton("🕌 دليل حلال", callback_data="menu_halal")
                ],
                [
                    InlineKeyboardButton("💬 ابدأ الاستشارة", callback_data="start_consultation"),
                ],
                [
                    InlineKeyboardButton("🌐 اللغة", callback_data="menu_language"),
                    InlineKeyboardButton("ℹ️ مساعدة", callback_data="menu_help")
                ]
            ],
            "ko": [
                [
                    InlineKeyboardButton("🏥 시술", callback_data="menu_procedures"),
                    InlineKeyboardButton("🏨 클리닉", callback_data="menu_clinics")
                ],
                [
                    InlineKeyboardButton("📹 리뷰", callback_data="menu_reviews"),
                    InlineKeyboardButton("🕌 할랄 가이드", callback_data="menu_halal")
                ],
                [
                    InlineKeyboardButton("💬 상담 시작", callback_data="start_consultation"),
                ],
                [
                    InlineKeyboardButton("🌐 언어", callback_data="menu_language"),
                    InlineKeyboardButton("ℹ️ 도움말", callback_data="menu_help")
                ]
            ]
        }
        
        keyboard = buttons.get(language, buttons["en"])
        return InlineKeyboardMarkup(keyboard)
    
    def create_procedures_menu(self, language: str = "en") -> InlineKeyboardMarkup:
        """
        Create procedures menu keyboard.
        
        Args:
            language: Language code
            
        Returns:
            InlineKeyboardMarkup object
        """
        procedures = {
            "en": [
                ("👃 Rhinoplasty", "procedure_rhinoplasty"),
                ("👁️ Double Eyelid", "procedure_double_eyelid"),
                ("🦴 Facial Contouring", "procedure_facial_contouring"),
                ("💉 Fillers & Botox", "procedure_fillers"),
                ("🔄 Liposuction", "procedure_liposuction"),
                ("😊 Face Lift", "procedure_facelift")
            ],
            "ar": [
                ("👃 تجميل الأنف", "procedure_rhinoplasty"),
                ("👁️ الجفن المزدوج", "procedure_double_eyelid"),
                ("🦴 نحت الوجه", "procedure_facial_contouring"),
                ("💉 الفيلر والبوتوكس", "procedure_fillers"),
                ("🔄 شفط الدهون", "procedure_liposuction"),
                ("😊 شد الوجه", "procedure_facelift")
            ],
            "ko": [
                ("👃 코 성형", "procedure_rhinoplasty"),
                ("👁️ 쌍꺼풀 수술", "procedure_double_eyelid"),
                ("🦴 안면 윤곽술", "procedure_facial_contouring"),
                ("💉 필러 & 보톡스", "procedure_fillers"),
                ("🔄 지방흡입", "procedure_liposuction"),
                ("😊 안면 거상술", "procedure_facelift")
            ]
        }
        
        buttons = []
        proc_list = procedures.get(language, procedures["en"])
        
        # Create 2-column layout
        for i in range(0, len(proc_list), 2):
            row = []
            row.append(InlineKeyboardButton(proc_list[i][0], callback_data=proc_list[i][1]))
            if i + 1 < len(proc_list):
                row.append(InlineKeyboardButton(proc_list[i+1][0], callback_data=proc_list[i+1][1]))
            buttons.append(row)
        
        # Add back button
        back_text = {"en": "⬅️ Back", "ar": "⬅️ رجوع", "ko": "⬅️ 뒤로"}
        buttons.append([InlineKeyboardButton(back_text.get(language, "⬅️ Back"), callback_data="main_menu")])
        
        return InlineKeyboardMarkup(buttons)
    
    def create_quick_actions(self, language: str = "en") -> InlineKeyboardMarkup:
        """
        Create quick action buttons for common queries.
        
        Args:
            language: Language code
            
        Returns:
            InlineKeyboardMarkup object
        """
        actions = {
            "en": [
                [
                    InlineKeyboardButton("💰 Price Estimates", callback_data="quick_prices"),
                    InlineKeyboardButton("📅 Recovery Times", callback_data="quick_recovery")
                ],
                [
                    InlineKeyboardButton("🏆 Top Clinics", callback_data="quick_top_clinics"),
                    InlineKeyboardButton("📍 Locations", callback_data="quick_locations")
                ],
                [
                    InlineKeyboardButton("🕌 Prayer Times", callback_data="quick_prayer"),
                    InlineKeyboardButton("🍽️ Halal Food", callback_data="quick_halal_food")
                ]
            ],
            "ar": [
                [
                    InlineKeyboardButton("💰 تقديرات الأسعار", callback_data="quick_prices"),
                    InlineKeyboardButton("📅 أوقات التعافي", callback_data="quick_recovery")
                ],
                [
                    InlineKeyboardButton("🏆 أفضل العيادات", callback_data="quick_top_clinics"),
                    InlineKeyboardButton("📍 المواقع", callback_data="quick_locations")
                ],
                [
                    InlineKeyboardButton("🕌 أوقات الصلاة", callback_data="quick_prayer"),
                    InlineKeyboardButton("🍽️ طعام حلال", callback_data="quick_halal_food")
                ]
            ],
            "ko": [
                [
                    InlineKeyboardButton("💰 가격 견적", callback_data="quick_prices"),
                    InlineKeyboardButton("📅 회복 시간", callback_data="quick_recovery")
                ],
                [
                    InlineKeyboardButton("🏆 최고 클리닉", callback_data="quick_top_clinics"),
                    InlineKeyboardButton("📍 위치", callback_data="quick_locations")
                ],
                [
                    InlineKeyboardButton("🕌 기도 시간", callback_data="quick_prayer"),
                    InlineKeyboardButton("🍽️ 할랄 음식", callback_data="quick_halal_food")
                ]
            ]
        }
        
        keyboard = actions.get(language, actions["en"])
        return InlineKeyboardMarkup(keyboard)
    
    def create_language_selection(self) -> InlineKeyboardMarkup:
        """
        Create language selection keyboard.
        
        Returns:
            InlineKeyboardMarkup object
        """
        keyboard = [
            [
                InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"),
                InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
                InlineKeyboardButton("🇰🇷 한국어", callback_data="lang_ko")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    def create_help_menu(self, language: str = "en") -> InlineKeyboardMarkup:
        """
        Create help menu keyboard.
        
        Args:
            language: Language code
            
        Returns:
            InlineKeyboardMarkup object
        """
        topics = {
            "en": [
                ("📖 How to Use", "help_how_to_use"),
                ("❓ FAQs", "help_faqs"),
                ("📞 Contact Support", "help_contact"),
                ("🔒 Privacy Policy", "help_privacy"),
                ("📜 Terms of Service", "help_terms")
            ],
            "ar": [
                ("📖 كيفية الاستخدام", "help_how_to_use"),
                ("❓ الأسئلة الشائعة", "help_faqs"),
                ("📞 الدعم", "help_contact"),
                ("🔒 سياسة الخصوصية", "help_privacy"),
                ("📜 شروط الخدمة", "help_terms")
            ],
            "ko": [
                ("📖 사용 방법", "help_how_to_use"),
                ("❓ 자주 묻는 질문", "help_faqs"),
                ("📞 지원 문의", "help_contact"),
                ("🔒 개인정보 정책", "help_privacy"),
                ("📜 서비스 약관", "help_terms")
            ]
        }
        
        buttons = []
        help_topics = topics.get(language, topics["en"])
        
        for topic, callback in help_topics:
            buttons.append([InlineKeyboardButton(topic, callback_data=callback)])
        
        # Add back button
        back_text = {"en": "⬅️ Back", "ar": "⬅️ رجوع", "ko": "⬅️ 뒤로"}
        buttons.append([InlineKeyboardButton(back_text.get(language, "⬅️ Back"), callback_data="main_menu")])
        
        return InlineKeyboardMarkup(buttons)
    
    def create_medical_actions(self, language: str = "en") -> InlineKeyboardMarkup:
        """
        Create action buttons for medical consultations.
        
        Args:
            language: Language code
            
        Returns:
            InlineKeyboardMarkup object
        """
        actions = {
            "en": [
                [
                    InlineKeyboardButton("📋 Book Consultation", callback_data="book_consultation"),
                    InlineKeyboardButton("📸 Send Photos", callback_data="send_photos")
                ],
                [
                    InlineKeyboardButton("💬 Ask Question", callback_data="ask_question"),
                    InlineKeyboardButton("📄 Get Quote", callback_data="get_quote")
                ]
            ],
            "ar": [
                [
                    InlineKeyboardButton("📋 حجز استشارة", callback_data="book_consultation"),
                    InlineKeyboardButton("📸 إرسال صور", callback_data="send_photos")
                ],
                [
                    InlineKeyboardButton("💬 اسأل سؤال", callback_data="ask_question"),
                    InlineKeyboardButton("📄 احصل على عرض سعر", callback_data="get_quote")
                ]
            ],
            "ko": [
                [
                    InlineKeyboardButton("📋 상담 예약", callback_data="book_consultation"),
                    InlineKeyboardButton("📸 사진 보내기", callback_data="send_photos")
                ],
                [
                    InlineKeyboardButton("💬 질문하기", callback_data="ask_question"),
                    InlineKeyboardButton("📄 견적 받기", callback_data="get_quote")
                ]
            ]
        }
        
        keyboard = actions.get(language, actions["en"])
        return InlineKeyboardMarkup(keyboard)
    
    def create_review_actions(self, language: str = "en") -> InlineKeyboardMarkup:
        """
        Create action buttons for review-related responses.
        
        Args:
            language: Language code
            
        Returns:
            InlineKeyboardMarkup object
        """
        actions = {
            "en": [
                [
                    InlineKeyboardButton("🎥 Watch Videos", callback_data="watch_videos"),
                    InlineKeyboardButton("📊 See Statistics", callback_data="see_statistics")
                ],
                [
                    InlineKeyboardButton("🔍 Search More", callback_data="search_more_reviews")
                ]
            ],
            "ar": [
                [
                    InlineKeyboardButton("🎥 مشاهدة الفيديوهات", callback_data="watch_videos"),
                    InlineKeyboardButton("📊 عرض الإحصائيات", callback_data="see_statistics")
                ],
                [
                    InlineKeyboardButton("🔍 البحث عن المزيد", callback_data="search_more_reviews")
                ]
            ],
            "ko": [
                [
                    InlineKeyboardButton("🎥 비디오 보기", callback_data="watch_videos"),
                    InlineKeyboardButton("📊 통계 보기", callback_data="see_statistics")
                ],
                [
                    InlineKeyboardButton("🔍 더 검색하기", callback_data="search_more_reviews")
                ]
            ]
        }
        
        keyboard = actions.get(language, actions["en"])
        return InlineKeyboardMarkup(keyboard)
    
    def create_cultural_actions(self, language: str = "en") -> InlineKeyboardMarkup:
        """
        Create action buttons for cultural guidance.
        
        Args:
            language: Language code
            
        Returns:
            InlineKeyboardMarkup object
        """
        actions = {
            "en": [
                [
                    InlineKeyboardButton("🕌 Find Mosques", callback_data="find_mosques"),
                    InlineKeyboardButton("🍽️ Halal Restaurants", callback_data="halal_restaurants")
                ],
                [
                    InlineKeyboardButton("🧕 Women's Guide", callback_data="womens_guide"),
                    InlineKeyboardButton("📿 Prayer Times", callback_data="prayer_times")
                ]
            ],
            "ar": [
                [
                    InlineKeyboardButton("🕌 البحث عن مساجد", callback_data="find_mosques"),
                    InlineKeyboardButton("🍽️ مطاعم حلال", callback_data="halal_restaurants")
                ],
                [
                    InlineKeyboardButton("🧕 دليل النساء", callback_data="womens_guide"),
                    InlineKeyboardButton("📿 أوقات الصلاة", callback_data="prayer_times")
                ]
            ],
            "ko": [
                [
                    InlineKeyboardButton("🕌 모스크 찾기", callback_data="find_mosques"),
                    InlineKeyboardButton("🍽️ 할랄 레스토랑", callback_data="halal_restaurants")
                ],
                [
                    InlineKeyboardButton("🧕 여성 가이드", callback_data="womens_guide"),
                    InlineKeyboardButton("📿 기도 시간", callback_data="prayer_times")
                ]
            ]
        }
        
        keyboard = actions.get(language, actions["en"])
        return InlineKeyboardMarkup(keyboard)
    
    def create_back_button(self, destination: str, language: str = "en") -> InlineKeyboardMarkup:
        """
        Create a simple back button.
        
        Args:
            destination: Callback data for back destination
            language: Language code
            
        Returns:
            InlineKeyboardMarkup object
        """
        back_text = {"en": "⬅️ Back", "ar": "⬅️ رجوع", "ko": "⬅️ 뒤로"}
        
        keyboard = [[
            InlineKeyboardButton(
                back_text.get(language, "⬅️ Back"),
                callback_data=f"back_{destination}"
            )
        ]]
        
        return InlineKeyboardMarkup(keyboard)
    
    def create_yes_no_keyboard(self, language: str = "en", 
                              yes_callback: str = "yes", 
                              no_callback: str = "no") -> InlineKeyboardMarkup:
        """
        Create a yes/no decision keyboard.
        
        Args:
            language: Language code
            yes_callback: Callback data for yes button
            no_callback: Callback data for no button
            
        Returns:
            InlineKeyboardMarkup object
        """
        yes_no = {
            "en": ("✅ Yes", "❌ No"),
            "ar": ("✅ نعم", "❌ لا"),
            "ko": ("✅ 예", "❌ 아니오")
        }
        
        yes_text, no_text = yes_no.get(language, yes_no["en"])
        
        keyboard = [[
            InlineKeyboardButton(yes_text, callback_data=yes_callback),
            InlineKeyboardButton(no_text, callback_data=no_callback)
        ]]
        
        return InlineKeyboardMarkup(keyboard)
    
    def create_rating_keyboard(self) -> InlineKeyboardMarkup:
        """
        Create a rating keyboard with stars.
        
        Returns:
            InlineKeyboardMarkup object
        """
        keyboard = [[
            InlineKeyboardButton("⭐", callback_data="rate_1"),
            InlineKeyboardButton("⭐⭐", callback_data="rate_2"),
            InlineKeyboardButton("⭐⭐⭐", callback_data="rate_3"),
            InlineKeyboardButton("⭐⭐⭐⭐", callback_data="rate_4"),
            InlineKeyboardButton("⭐⭐⭐⭐⭐", callback_data="rate_5")
        ]]
        
        return InlineKeyboardMarkup(keyboard)
    
    def create_share_keyboard(self, language: str = "en") -> ReplyKeyboardMarkup:
        """
        Create a keyboard for sharing contact or location.
        
        Args:
            language: Language code
            
        Returns:
            ReplyKeyboardMarkup object
        """
        share_text = {
            "en": {
                "contact": "📱 Share Contact",
                "location": "📍 Share Location",
                "cancel": "❌ Cancel"
            },
            "ar": {
                "contact": "📱 مشاركة جهة الاتصال",
                "location": "📍 مشاركة الموقع",
                "cancel": "❌ إلغاء"
            },
            "ko": {
                "contact": "📱 연락처 공유",
                "location": "📍 위치 공유",
                "cancel": "❌ 취소"
            }
        }
        
        texts = share_text.get(language, share_text["en"])
        
        keyboard = [
            [
                KeyboardButton(texts["contact"], request_contact=True),
                KeyboardButton(texts["location"], request_location=True)
            ],
            [KeyboardButton(texts["cancel"])]
        ]
        
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)