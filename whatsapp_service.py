import os
import requests
from config import Config
from language_service import language_service
from ai_service import ai_service
from voice_service import voice_service
from scam_logic import scam_rule_engine

class WhatsAppService:
    def __init__(self):
        self.token = Config.WHATSAPP_TOKEN
        self.phone_number_id = Config.WHATSAPP_PHONE_NUMBER_ID
        self.verify_token = Config.WHATSAPP_VERIFY_TOKEN
        self.user_state = {}  # In-memory session tracking for each user phone number

    def verify_webhook(self, mode: str, token: str, challenge: str):
        """Verifies WhatsApp Cloud API webhook registration handshake."""
        if mode == "subscribe" and token == self.verify_token:
            return challenge, 200
        return "Verification token mismatch", 403

    def process_incoming_cloud_message(self, data: dict) -> dict:
        """Processes incoming payload from Meta WhatsApp Business Cloud API."""
        try:
            entry = data.get("entry", [])[0]
            changes = entry.get("changes", [])[0]
            value = changes.get("value", {})
            messages = value.get("messages", [])
            
            if not messages:
                return {"status": "no_messages"}

            message = messages[0]
            sender = message.get("from")  # User's WhatsApp number
            msg_type = message.get("type")
            msg_id = message.get("id")

            # Check/retrieve user's language
            lang = language_service.get_user_language(sender)
            state = self.user_state.get(sender, {})

            reply_text = ""

            # 1. Handle TEXT messages
            if msg_type == "text":
                text_content = message.get("text", {}).get("body", "").strip()
                reply_text = self._handle_text_input(sender, text_content, lang, state)

            # 2. Handle VOICE / AUDIO notes
            elif msg_type in ("voice", "audio"):
                media_id = message.get(msg_type, {}).get("id")
                audio_bytes = self._download_meta_media(media_id)
                if audio_bytes:
                    transcription = voice_service.transcribe_audio_file(audio_bytes, lang=lang)
                    if transcription.get("success"):
                        spoken_text = transcription["text"]
                        
                        # If user was in recovery state, match intent to targeted advice
                        if state.get("awaiting") in ("recovery_choice", "recovery_other"):
                            category = scam_rule_engine.match_recovery_intent(spoken_text)
                            self.user_state[sender] = {"awaiting": None}
                            reply_text = f"🎤 _{spoken_text}_\n\n" + self._format_targeted_recovery_whatsapp(category, lang)
                        else:
                            analysis = ai_service.analyze_content(text=spoken_text, lang=lang)
                            reply_text = f"🎤 *Transcribed Voice Note:*\n_{spoken_text}_\n\n" + ai_service.format_whatsapp_message(analysis, lang=lang)
                    else:
                        reply_text = transcription.get("error", language_service.get_text("fallback_error", lang))
                else:
                    reply_text = "Sorry, I could not download the voice note. Please try recording again or type what they said."

            # 3. Handle IMAGES / SCREENSHOTS
            elif msg_type == "image":
                media_id = message.get("image", {}).get("id")
                caption = message.get("image", {}).get("caption", "")
                image_bytes = self._download_meta_media(media_id)
                if image_bytes:
                    analysis = ai_service.analyze_content(text=caption, image_bytes=image_bytes, mime_type="image/jpeg", lang=lang)
                    reply_text = ai_service.format_whatsapp_message(analysis, lang=lang)
                else:
                    reply_text = "Sorry, I could not load the screenshot. Please try sending it again."

            # 4. Handle BUTTON / INTERACTIVE responses
            elif msg_type == "interactive":
                btn_id = message.get("interactive", {}).get("button_reply", {}).get("id", "")
                reply_text = self._handle_text_input(sender, btn_id, lang, state)

            # Send response back to user
            if reply_text:
                self.send_whatsapp_message(sender, reply_text)

            return {"status": "success", "sender": sender}

        except Exception as e:
            print(f"Error handling Cloud API message: {e}")
            return {"status": "error", "error": str(e)}

    def _handle_text_input(self, sender: str, text: str, lang: str, state: dict) -> str:
        """Routes text commands, damage control replies, menu options, or scam analysis."""
        text_clean = text.strip()
        text_upper = text_clean.upper()

        # Check if user is in the middle of the step-by-step recovery flow
        awaiting = state.get("awaiting")
        if awaiting == "recovery_choice":
            num_map = {
                "1": "money", "2": "otp", "3": "password", "4": "bank_card",
                "5": "personal_id", "6": "clicked_link", "7": "installed_app", "8": "something_else"
            }
            if text_clean in num_map:
                cat = num_map[text_clean]
                if cat == "something_else":
                    self.user_state[sender] = {"awaiting": "recovery_other"}
                    return language_service.get_text("advice_something_else_prompt", lang)
                self.user_state[sender] = {"awaiting": None}
                return self._format_targeted_recovery_whatsapp(cat, lang)
            else:
                cat = scam_rule_engine.match_recovery_intent(text_clean)
                self.user_state[sender] = {"awaiting": None}
                return self._format_targeted_recovery_whatsapp(cat, lang)

        if awaiting == "recovery_other":
            cat = scam_rule_engine.match_recovery_intent(text_clean)
            self.user_state[sender] = {"awaiting": None}
            return self._format_targeted_recovery_whatsapp(cat, lang)

        # Check for YES reply (begins the step-by-step recovery flow)
        if text_upper in ("YES", "Y", "HAAN", "TAK", "DA", "SIM", "1"):
            # Check if previous context was awaiting yes/no
            self.user_state[sender] = {"awaiting": "recovery_choice"}
            return self._format_recovery_options_whatsapp(lang)
            
        # Check for NO reply
        if text_upper in ("NO", "N", "NAHI", "NIE", "NU", "NÃO", "2") and awaiting == "already_acted":
            self.user_state[sender] = {"awaiting": None}
            return language_service.get_text("no_action_reassurance", lang)

        # Bot Commands
        if text_upper in ("HELP", "START", "HELLO", "HI", "MENU"):
            self.user_state[sender] = {"awaiting": None}
            return language_service.get_welcome_menu(lang)

        if text_upper in ("CHECK", "RESET", "CLEAR"):
            self.user_state[sender] = {"awaiting": None}
            return "📩 " + language_service.get_text("input_message_label", lang)

        if text_upper in ("LANGUAGE", "LANG", "BHASHA", "JEZYK", "LIMBA", "IDIOMA"):
            self.user_state[sender] = {"awaiting": "language"}
            return language_service.get_language_prompt()

        if text_clean in ("1", "2", "3", "4", "5") and state.get("awaiting") == "language":
            new_lang = language_service.set_user_language(sender, text_clean)
            self.user_state[sender] = {"awaiting": None}
            return language_service.get_text("language_changed", new_lang)

        # Menu choices from Welcome Menu
        if text_clean == "1":
            return "📩 " + language_service.get_text("input_message_label", lang)
        if text_clean == "2":
            return "📷 " + language_service.get_text("input_screenshot_label", lang)
        if text_clean == "3":
            return "🎤 " + language_service.get_text("input_voice_label", lang)
        if text_clean == "4":
            return language_service.get_text("guide_options", lang)
        if text_clean == "5":
            self.user_state[sender] = {"awaiting": "language"}
            return language_service.get_language_prompt()

        # Check if user requested one of the guides
        if "MESSAGE" in text_upper and "HOW" in text_upper:
            return language_service.get_text("guide_message", lang)
        if "SCREENSHOT" in text_upper and "HOW" in text_upper:
            return language_service.get_text("guide_screenshot", lang)
        if "VOICE" in text_upper and "HOW" in text_upper:
            return language_service.get_text("guide_voice", lang)
        if "CALL" in text_upper and "HOW" in text_upper:
            return language_service.get_text("guide_call", lang)

        # Detect language change keywords
        if text_clean.lower() in ("english", "punjabi", "polski", "polish", "romana", "romanian", "portugues", "portuguese"):
            new_lang = language_service.set_user_language(sender, text_clean)
            return language_service.get_text("language_changed", new_lang)

        # Check language detection in user's query
        detected = language_service.detect_potential_language(text_clean)
        if detected and detected != lang:
            lang = language_service.set_user_language(sender, detected)

        # Check if user is reporting that they already lost money (immediate damage control)
        if any(w in text_clean.lower() for w in ["sent money", "transferred money", "lost money", "already paid", "scammed me", "paguei", "transferi", "przelałem", "am trimis bani", "ਪੈਸੇ ਭੇਜੇ"]):
            return self._format_targeted_recovery_whatsapp("money", lang)

        # Standard scam check flow
        analysis = ai_service.analyze_content(text=text_clean, lang=lang)
        if analysis.get("show_already_acted"):
            self.user_state[sender] = {"awaiting": "already_acted"}
        else:
            self.user_state[sender] = {"awaiting": None}

        return ai_service.format_whatsapp_message(analysis, lang=lang)

    def _format_recovery_options_whatsapp(self, lang: str = "en") -> str:
        """Formats the 8 step-by-step recovery options into a clean WhatsApp menu."""
        q = language_service.get_text("recovery_question", lang)
        title = language_service.get_text("recovery_options_title", lang)
        options = language_service.get_recovery_options(lang)

        lines = [f"*{q}*", f"_{title}_\n"]
        for idx, opt in enumerate(options, 1):
            lines.append(f"{idx}️⃣ {opt['icon']} {opt['label']}")
        
        lines.append("\n" + "Reply with a number (1-8) or send a voice message.")
        return "\n".join(lines)

    def _format_targeted_recovery_whatsapp(self, category: str, lang: str = "en") -> str:
        """Formats ONLY the targeted 3-4 bullet points for the selected action."""
        adv = language_service.get_recovery_advice(category, lang)
        title = adv.get("title", "ACT NOW")
        points = adv.get("points", [])
        
        lines = [f"*{title}*\n"]
        for p in points:
            lines.append(f"• {p}")
        
        lines.append("")
        lines.append(f"📞 *{adv.get('official_contacts_title')}*")
        lines.append(f"• {adv.get('official_bank_line')}")
        lines.append(f"• {adv.get('official_action_fraud')}")
        lines.append(f"• {adv.get('official_police_101')}")
        lines.append("")
        lines.append(f"Type *CHECK* to check another message.")
        return "\n".join(lines)

    def send_whatsapp_message(self, to_phone: str, text: str) -> bool:
        """Sends an outbound WhatsApp text message via Meta Graph API."""
        if not self.token or not self.phone_number_id:
            try:
                print(f"[Simulated Outbound WhatsApp to {to_phone}]:\n{text}\n")
            except Exception:
                safe_text = text.encode("ascii", "replace").decode("ascii")
                print(f"[Simulated Outbound WhatsApp to {to_phone}]:\n{safe_text}\n")
            return True

        url = f"https://graph.facebook.com/v21.0/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_phone,
            "type": "text",
            "text": {"preview_url": False, "body": text}
        }

        try:
            res = requests.post(url, headers=headers, json=payload, timeout=10)
            return res.status_code in (200, 201)
        except Exception as e:
            print(f"Failed to send Meta Cloud API message: {e}")
            return False

    def _download_meta_media(self, media_id: str) -> bytes | None:
        """Retrieves media bytes from Meta Cloud API."""
        if not self.token or not media_id:
            return None
        try:
            media_info_url = f"https://graph.facebook.com/v21.0/{media_id}"
            headers = {"Authorization": f"Bearer {self.token}"}
            info_res = requests.get(media_info_url, headers=headers, timeout=10)
            if info_res.status_code == 200:
                media_url = info_res.json().get("url")
                download_res = requests.get(media_url, headers=headers, timeout=15)
                if download_res.status_code == 200:
                    return download_res.content
        except Exception as e:
            print(f"Error downloading Meta media: {e}")
        return None

# Singleton instance
whatsapp_service = WhatsAppService()
