import os
import json
import base64
import requests
from config import Config
from scam_logic import scam_rule_engine
from language_service import language_service

SYSTEM_PROMPT = """You are Scam-Check, an accessible scam-awareness assistant designed to help elderly and vulnerable people identify fraud.

CRITICAL LANGUAGE INSTRUCTION:
- The user has chosen the language: {target_language}.
- ALL text in your output MUST be written in {target_language}.
- The chosen language is AUTHORITATIVE. Do not switch back to English halfway through an answer.
- Do not translate the response into multiple languages; use ONLY {target_language}.
- Do not invent translations for official organisation names, web addresses or verified phone numbers.
- Use simple, familiar wording and short sentences suitable for older adults.

You are not law enforcement, a bank employee, or a financial adviser.
Analyse the suspicious message, screenshot, image, or voice transcript provided.

Classify strictly into one of three risk levels:
1. "very_likely_scam" (🔴 VERY LIKELY A SCAM)
2. "suspicious" (🟠 SUSPICIOUS / BE CAREFUL)
3. "probably_legitimate" (🟢 PROBABLY LEGITIMATE)

Rules:
- For "probably_legitimate":
  - Keep it calm and short.
  - "why": 1-2 points stating no obvious scam signs were found.
  - "do_now": 2-3 standard safe practices (check sender, use official app, never share OTP/PIN).
  - "do_not_do": MUST be an empty array [].
  - "show_what_not_to_do": false.
  - "show_already_acted": false.
- For "suspicious" and "very_likely_scam":
  - "why": 2 to 4 concise bullet points explaining why.
  - "do_now": 2 to 4 concise bullet points of what to do.
  - "do_not_do": 2 to 3 concise bullet points of what NOT to do.
  - "show_what_not_to_do": true.
  - "show_already_acted": true.
- Never ask for passwords, PINs, OTPs, full bank card numbers, or online banking credentials.
- Never tell the user to click links or call numbers found in the suspicious message.
- Tell them to contact their bank using the number printed on the back of their bank card.
- Be calm, reassuring, and non-judgemental.

Respond ONLY with valid JSON in this exact structure:
{
  "risk_level": "very_likely_scam | suspicious | probably_legitimate",
  "title": "Localised title",
  "scam_type": "digital_arrest | fake_kyc | upi_payment | otp_theft | fake_delivery | remote_access | family_impersonation | fake_bank | crypto | lottery | general",
  "why": [
    "Short reason 1",
    "Short reason 2"
  ],
  "do_now": [
    "Action 1",
    "Action 2"
  ],
  "do_not_do": [
    "Don't do 1"
  ],
  "show_what_not_to_do": true,
  "show_already_acted": true,
  "confidence": "high | medium | low",
  "needs_human_help": false
}
"""

class AIService:
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        self.model = Config.GEMINI_MODEL or "gemini-2.5-flash"

    def analyze_content(self, text: str = "", image_bytes: bytes = None, mime_type: str = "image/jpeg", lang: str = "en") -> dict:
        """
        Main analysis entrypoint: Combines deterministic rule engine and Gemini AI.
        Falls back smoothly to deterministic rule engine if Gemini API key is missing or call fails.
        """
        # Step 1: Run deterministic scam rule engine
        rule_result = scam_rule_engine.evaluate(text) if text else None
        
        # Step 2: Try Gemini API if API key is configured
        if self.api_key and (text or image_bytes):
            try:
                ai_result = self._call_gemini(text, image_bytes, mime_type, lang, rule_result)
                if ai_result:
                    return ai_result
            except Exception as e:
                print(f"Gemini API call failed: {e}. Falling back to deterministic rule engine.")

        # Step 3: Deterministic fallback
        if not rule_result:
            rule_result = scam_rule_engine.evaluate(text or "Screenshot or image")
        
        return self._format_rule_result_for_lang(rule_result, lang)

    def _call_gemini(self, text: str, image_bytes: bytes, mime_type: str, lang: str, rule_result: dict) -> dict | None:
        """Calls Google Gemini API via official REST endpoint with JSON schema enforcement."""
        lang_names = {
            "en": "English",
            "pa": "ਪੰਜਾਬੀ (Punjabi)",
            "pl": "Polski (Polish)",
            "ro": "Română (Romanian)",
            "pt": "Português (Portuguese)"
        }
        target_language = lang_names.get(lang, "English")
        prompt = SYSTEM_PROMPT.replace("{target_language}", target_language)

        # Build context from deterministic rule engine
        context_hint = ""
        if rule_result:
            indicators = [k for k, v in rule_result.get("indicators", {}).items() if v]
            context_hint = f"\n[Rule Engine Detected: {', '.join(indicators) if indicators else 'None'}. Preliminary Risk: {rule_result.get('risk_level')}]."

        parts = []
        if text:
            parts.append({"text": f"{context_hint}\nUser content to analyse:\n\"\"\"{text}\"\"\""})
        elif context_hint:
            parts.append({"text": f"{context_hint}\nPlease analyse the provided screenshot/image."})

        if image_bytes:
            parts.append({
                "inline_data": {
                    "mime_type": mime_type,
                    "data": base64.b64encode(image_bytes).decode("utf-8")
                }
            })

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": prompt}] + parts}
            ],
            "generationConfig": {
                "temperature": 0.1,
                "response_mime_type": "application/json"
            }
        }

        response = requests.post(url, headers=headers, json=payload, timeout=12)
        if response.status_code == 200:
            data = response.json()
            candidates = data.get("candidates", [])
            if candidates:
                raw_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                parsed = json.loads(raw_text)
                return self._validate_and_normalize(parsed, lang)
        else:
            print(f"Gemini API returned error {response.status_code}: {response.text}")
        return None

    def _validate_and_normalize(self, data: dict, lang: str) -> dict:
        """Validates AI response structure and enforces application-level conditional rules."""
        valid_risks = {"very_likely_scam", "suspicious", "probably_legitimate"}
        risk = data.get("risk_level", "suspicious")
        if risk not in valid_risks:
            risk = "suspicious"

        # Application logic determines section visibility based on validated risk_level
        show_what_not_to_do = risk in ["suspicious", "very_likely_scam"]
        show_already_acted = risk in ["suspicious", "very_likely_scam"]

        # Match localized title badge
        if risk == "very_likely_scam":
            title = language_service.get_text("risk_very_likely", lang)
        elif risk == "suspicious":
            title = language_service.get_text("risk_suspicious", lang)
        else:
            title = language_service.get_text("risk_legitimate", lang)

        why_points = data.get("why", [])
        if not why_points and risk == "probably_legitimate":
            why_points = [language_service.get_text("legit_no_signs_found", lang)]

        do_now_points = data.get("do_now", [])
        if not do_now_points and risk == "probably_legitimate":
            do_now_points = [
                language_service.get_text("legit_check_sender", lang),
                language_service.get_text("legit_official_app", lang),
                language_service.get_text("legit_never_share_otp", lang)
            ]

        do_not_do_points = data.get("do_not_do", []) if show_what_not_to_do else []

        return {
            "risk_level": risk,
            "title": title,
            "scam_type": data.get("scam_type", "general"),
            "why": why_points[:4],
            "do_now": do_now_points[:4],
            "do_not_do": do_not_do_points[:3] if show_what_not_to_do else [],
            "show_what_not_to_do": show_what_not_to_do,
            "show_already_acted": show_already_acted,
            "confidence": data.get("confidence", "high"),
            "needs_human_help": bool(data.get("needs_human_help", False))
        }

    def _format_rule_result_for_lang(self, rule_result: dict, lang: str) -> dict:
        """Translates deterministic rule results to target language for display."""
        risk = rule_result.get("risk_level", "suspicious")
        
        # Localized title
        if risk == "very_likely_scam":
            title = language_service.get_text("risk_very_likely", lang)
        elif risk == "suspicious":
            title = language_service.get_text("risk_suspicious", lang)
        else:
            title = language_service.get_text("risk_legitimate", lang)

        show_what_not_to_do = risk in ["suspicious", "very_likely_scam"]
        show_already_acted = risk in ["suspicious", "very_likely_scam"]

        res = dict(rule_result)
        res["title"] = title
        res["show_what_not_to_do"] = show_what_not_to_do
        res["show_already_acted"] = show_already_acted

        if not show_what_not_to_do:
            res["do_not_do"] = []

        # Localized reasons and actions for legitimate notices
        if risk == "probably_legitimate":
            res["why"] = [language_service.get_text("legit_no_signs_found", lang)]
            res["do_now"] = [
                language_service.get_text("legit_check_sender", lang),
                language_service.get_text("legit_official_app", lang),
                language_service.get_text("legit_never_share_otp", lang)
            ]
            
        return res

    def format_whatsapp_message(self, result: dict, lang: str = "en") -> str:
        """Formats analysis result into a clean, elderly-friendly WhatsApp message."""
        title = result.get("title", "Scam-Check")
        why_list = result.get("why", [])
        do_now_list = result.get("do_now", [])
        do_not_do_list = result.get("do_not_do", [])
        show_what_not_to_do = result.get("show_what_not_to_do", False)
        show_already_acted = result.get("show_already_acted", False)
        
        why_hdr = language_service.get_text("why_heading", lang)
        do_hdr = language_service.get_text("do_now_heading", lang)
        dont_hdr = language_service.get_text("do_not_do_heading", lang)
        reassurance = language_service.get_text("reassurance_msg", lang)
        already_q = language_service.get_text("already_acted_question", lang)
        check_another = language_service.get_text("check_another_btn", lang)

        parts = [f"*{title}*\n"]
        
        if why_list:
            parts.append(f"*{why_hdr}*")
            for item in why_list:
                parts.append(f"• {item}")
            parts.append("")

        if do_now_list:
            parts.append(f"*{do_hdr}*")
            for item in do_now_list:
                parts.append(f"• {item}")
            parts.append("")

        if show_what_not_to_do and do_not_do_list:
            parts.append(f"*{dont_hdr}*")
            for item in do_not_do_list:
                parts.append(f"• {item}")
            parts.append("")

        # Legitimate messages end cleanly without recovery question
        if not show_already_acted:
            parts.append(f"_{check_another}_: Type *CHECK* to check another message.")
            return "\n".join(parts)

        # Suspicious or scam messages include reassuring message and targeted YES/NO question
        parts.append(f"_{reassurance}_\n")
        parts.append(f"❓ *{already_q}*")
        yes_label = language_service.get_text("already_acted_yes", lang)
        no_label = language_service.get_text("already_acted_no", lang)
        parts.append(f"Reply *YES* ({yes_label}) or *NO* ({no_label}).")

        return "\n".join(parts)

# Singleton instance
ai_service = AIService()
