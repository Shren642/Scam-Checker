import os
import json
import re

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
TRANSLATIONS_FILE = os.path.join(DATA_DIR, "translations.json")

class LanguageService:
    def __init__(self):
        self.translations = self._load_translations()
        # In-memory storage for user languages (phone number / session id -> lang_code)
        self.user_languages = {}
    
    def _load_translations(self):
        try:
            with open(TRANSLATIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading translations: {e}")
            return {}

    def get_supported_languages(self):
        return {
            "en": "English",
            "pa": "ਪੰਜਾਬੀ (Punjabi)",
            "pl": "Polski (Polish)",
            "ro": "Română (Romanian)",
            "pt": "Português (Portuguese)"
        }

    def get_user_language(self, user_id: str) -> str:
        return self.user_languages.get(user_id, "en")

    def set_user_language(self, user_id: str, lang_code: str) -> str:
        lang_code = lang_code.lower().strip()
        if lang_code in self.translations:
            self.user_languages[user_id] = lang_code
            return lang_code
        # Try matching language names or numbers
        mapping = {
            "1": "en", "english": "en",
            "2": "pa", "punjabi": "pa", "ਪੰਜਾਬੀ": "pa",
            "3": "pl", "polski": "pl", "polish": "pl",
            "4": "ro", "romana": "ro", "română": "ro", "romanian": "ro",
            "5": "pt", "portugues": "pt", "português": "pt", "portuguese": "pt"
        }
        if lang_code in mapping:
            chosen = mapping[lang_code]
            self.user_languages[user_id] = chosen
            return chosen
        
        # Default to English
        self.user_languages[user_id] = "en"
        return "en"

    def get_text(self, key: str, lang: str = "en") -> str:
        lang_dict = self.translations.get(lang, self.translations.get("en", {}))
        val = lang_dict.get(key)
        if val is None:
            # Fallback to English
            val = self.translations.get("en", {}).get(key, key)
        return val

    def get_all_translations_for_lang(self, lang: str = "en") -> dict:
        """Returns the full dictionary of translations for the selected language, with fallback to English."""
        en_dict = self.translations.get("en", {})
        target_dict = self.translations.get(lang, en_dict)
        merged = dict(en_dict)
        merged.update(target_dict)
        return merged

    def get_recovery_options(self, lang: str = "en") -> list:
        """Returns the 8 step-by-step recovery options with translated labels."""
        return [
            {"id": "money", "icon": "💵", "label": self.get_text("opt_money", lang)},
            {"id": "otp", "icon": "🔢", "label": self.get_text("opt_otp", lang)},
            {"id": "password", "icon": "🔑", "label": self.get_text("opt_password", lang)},
            {"id": "bank_card", "icon": "💳", "label": self.get_text("opt_bank_card", lang)},
            {"id": "personal_id", "icon": "🪪", "label": self.get_text("opt_personal_id", lang)},
            {"id": "clicked_link", "icon": "🔗", "label": self.get_text("opt_clicked_link", lang)},
            {"id": "installed_app", "icon": "📱", "label": self.get_text("opt_installed_app", lang)},
            {"id": "something_else", "icon": "❓", "label": self.get_text("opt_something_else", lang)},
        ]

    def get_recovery_advice(self, category: str, lang: str = "en") -> dict:
        """Returns targeted advice (title + 3-4 points) for the selected recovery option."""
        category = category.lower().strip()
        title = self.get_text("act_now_title", lang)
        
        points_map = {
            "money": [
                self.get_text("advice_money_p1", lang),
                self.get_text("advice_money_p2", lang),
                self.get_text("advice_money_p3", lang),
                self.get_text("advice_money_p4", lang),
            ],
            "otp": [
                self.get_text("advice_otp_p1", lang),
                self.get_text("advice_otp_p2", lang),
                self.get_text("advice_otp_p3", lang),
                self.get_text("advice_otp_p4", lang),
            ],
            "password": [
                self.get_text("advice_password_p1", lang),
                self.get_text("advice_password_p2", lang),
                self.get_text("advice_password_p3", lang),
                self.get_text("advice_password_p4", lang),
            ],
            "bank_card": [
                self.get_text("advice_bank_card_p1", lang),
                self.get_text("advice_bank_card_p2", lang),
                self.get_text("advice_bank_card_p3", lang),
                self.get_text("advice_bank_card_p4", lang),
            ],
            "personal_id": [
                self.get_text("advice_personal_id_p1", lang),
                self.get_text("advice_personal_id_p2", lang),
                self.get_text("advice_personal_id_p3", lang),
                self.get_text("advice_personal_id_p4", lang),
            ],
            "clicked_link": [
                self.get_text("advice_clicked_link_p1", lang),
                self.get_text("advice_clicked_link_p2", lang),
                self.get_text("advice_clicked_link_p3", lang),
            ],
            "installed_app": [
                self.get_text("advice_installed_app_p1", lang),
                self.get_text("advice_installed_app_p2", lang),
                self.get_text("advice_installed_app_p3", lang),
                self.get_text("advice_installed_app_p4", lang),
            ],
            "something_else": [
                self.get_text("advice_something_else_prompt", lang),
            ]
        }

        points = points_map.get(category, points_map["money"])
        
        return {
            "category": category,
            "title": title,
            "points": points,
            "official_contacts_title": self.get_text("official_contacts_title", lang),
            "official_bank_line": self.get_text("official_bank_line", lang),
            "official_action_fraud": self.get_text("official_action_fraud", lang),
            "official_police_101": self.get_text("official_police_101", lang),
            "check_another_btn": self.get_text("check_another_btn", lang),
            "back_btn": self.get_text("back_btn", lang),
        }

    def detect_potential_language(self, text: str) -> str | None:
        """Detects if text likely belongs to one of our supported non-English languages."""
        if not text:
            return None
        text_lower = text.lower()
        
        # Punjabi script range: \u0A00-\u0A7F
        if re.search(r"[\u0a00-\u0a7f]", text):
            return "pa"
        
        # Polish specific diacritics
        if re.search(r"[ąćęłńóśźż]", text_lower):
            return "pl"
        
        # Romanian specific diacritics
        if re.search(r"[ăâîșțşţ]", text_lower):
            return "ro"
        
        # Portuguese specific diacritics or frequent words
        if re.search(r"[ãõçê]", text_lower) or any(w in text_lower for w in ["você", "obrigado", "dinheiro", "golpe"]):
            return "pt"
            
        return None

    def get_welcome_menu(self, lang: str = "en") -> str:
        greeting = self.get_text("welcome_greeting", lang)
        q = self.get_text("welcome_question", lang)
        m1 = self.get_text("menu_1", lang)
        m2 = self.get_text("menu_2", lang)
        m3 = self.get_text("menu_3", lang)
        m4 = self.get_text("menu_4", lang)
        m5 = self.get_text("menu_5", lang)
        return f"{greeting}\n\n{q}\n\n{m1}\n{m2}\n{m3}\n{m4}\n{m5}"

    def get_language_prompt(self) -> str:
        return self.get_text("choose_language", "en")

# Singleton instance
language_service = LanguageService()
