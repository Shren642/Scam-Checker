import os
import json
import re
from urllib.parse import urlparse

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
PATTERNS_FILE = os.path.join(DATA_DIR, "scam_patterns.json")
DOMAINS_FILE = os.path.join(DATA_DIR, "trusted_domains.json")

class ScamRuleEngine:
    def __init__(self):
        self.patterns = self._load_json(PATTERNS_FILE)
        self.domains_data = self._load_json(DOMAINS_FILE)
        self.categories = self.patterns.get("categories", {})
        self.trusted_domains = set(self.domains_data.get("trusted_domains", []))
        self.suspicious_tlds = tuple(self.domains_data.get("suspicious_tlds", []))
        self.shorteners = set(self.domains_data.get("shortener_domains", []))

    def _load_json(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return {}

    def extract_urls(self, text: str) -> list[str]:
        """Safely extracts visible URLs or domain references without visiting them."""
        if not text:
            return []
        url_regex = r'(?:https?:\/\/|www\.)[^\s<>"]+|(?:\b[a-zA-Z0-9-]+\.(?:com|org|net|uk|co\.uk|info|biz|top|xyz|tk|ml|ga|cf|gq|icu|online)\b(?:\/[^\s<>"]*)?)'
        matches = re.findall(url_regex, text, flags=re.IGNORECASE)
        clean_urls = []
        for m in matches:
            clean = m.rstrip(".,;!?:)'\"")
            if clean and clean not in clean_urls:
                clean_urls.append(clean)
        return clean_urls

    def analyze_urls(self, urls: list[str]) -> dict:
        """Inspects URLs against trusted list, shorteners, and suspicious TLDs."""
        analysis = {
            "has_url": bool(urls),
            "urls": urls,
            "suspicious_domains": [],
            "shortened_urls": [],
            "trusted_domains_found": [],
            "warnings": []
        }
        
        for url in urls:
            url_to_parse = url if url.startswith(("http://", "https://")) else "https://" + url
            try:
                parsed = urlparse(url_to_parse)
                hostname = (parsed.hostname or "").lower()
                
                # Check shortener
                if hostname in self.shorteners:
                    analysis["shortened_urls"].append(url)
                    analysis["warnings"].append(f"Contains a shortened link ({hostname}), which hides the real web address.")
                
                # Check suspicious TLD
                elif hostname.endswith(self.suspicious_tlds):
                    analysis["suspicious_domains"].append(url)
                    analysis["warnings"].append(f"Uses an unusual web address extension ({hostname}), commonly used in fraudulent websites.")
                
                # Check if trusted
                elif any(hostname == td or hostname.endswith("." + td) for td in self.trusted_domains):
                    analysis["trusted_domains_found"].append(hostname)
                else:
                    # Unrecognized domain
                    analysis["suspicious_domains"].append(url)
                    analysis["warnings"].append(f"The link points to '{hostname}', which is not a verified official address.")
            except Exception:
                analysis["warnings"].append("Contains an unverified or malformed web address.")
        
        return analysis

    def evaluate(self, text: str) -> dict:
        """
        Evaluates the message using deterministic scam rules and heuristics.
        Returns a structured result matching Scam-Check safety criteria.
        """
        if not text or not text.strip():
            return {
                "risk_level": "suspicious",
                "scam_type": "empty_input",
                "title": "No text received",
                "why": ["No content was provided to check."],
                "do_now": ["Please send or paste the message, screenshot, or voice note."],
                "do_not_do": ["Do not share personal details."],
                "already_acted": ["If you sent money, contact your bank immediately."],
                "confidence": "low",
                "indicators": {}
            }

        text_lower = text.lower()
        matched_categories = []
        indicators = {
            "digital_arrest": False,
            "fake_kyc": False,
            "upi_pin_theft": False,
            "otp_request": False,
            "fake_delivery": False,
            "remote_access": False,
            "family_impersonation": False,
            "fake_bank_hmrc": False,
            "investment_crypto": False,
            "lottery_prize": False,
            "urgent_pressure": False,
            "suspicious_link": False
        }

        # 1. Match categories from pattern library
        for cat_id, cat_info in self.categories.items():
            keywords = cat_info.get("keywords", [])
            for kw in keywords:
                if kw in text_lower:
                    matched_categories.append((cat_id, cat_info))
                    if cat_id in indicators:
                        indicators[cat_id] = True
                    break

        # 2. Check general high-risk triggers
        urgency_terms = ["urgent", "immediately", "within 24 hours", "account blocked today", "within 1 hour", "act now", "action required immediately"]
        if any(term in text_lower for term in urgency_terms):
            indicators["urgent_pressure"] = True

        money_terms = ["transfer money", "safe account", "send money", "gift card", "bitcoin", "pay fee", "transfer £", "transfer $", "transfer inr", "pay now"]
        demands_money = any(m in text_lower for m in money_terms)

        # 3. Analyze URLs
        urls = self.extract_urls(text)
        url_analysis = self.analyze_urls(urls)
        if url_analysis["suspicious_domains"] or url_analysis["shortened_urls"]:
            indicators["suspicious_link"] = True

        # 4. Determine Risk Level & Explanations (2 to 4 concise bullet points max)
        why_points = []
        do_now_points = []
        do_not_do_points = []
        already_acted_points = [
            "If you sent money: Call your bank immediately using the number on your bank card.",
            "If you shared an OTP or password: Contact your bank/provider immediately to freeze your account.",
            "If you clicked a link: Close the page and do not enter any more details."
        ]

        # Prioritize high-risk categories
        primary_category = None
        if matched_categories:
            primary_cat_id, primary_cat_info = matched_categories[0]
            primary_category = primary_cat_id
            
            # Specific explanations based on matched category
            if primary_cat_id == "digital_arrest":
                risk_level = "very_likely_scam"
                title = "🔴 VERY LIKELY A SCAM (Digital Arrest)"
                why_points = [
                    "They are threatening you with arrest or investigation over a phone call or chat.",
                    "Real police and courts NEVER demand money transfers or 'digital arrests' over WhatsApp or video calls.",
                    "They are trying to isolate you by telling you not to speak with family or friends."
                ]
                do_now_points = [
                    "Stop the call or block the sender immediately.",
                    "Do not transfer any money to any 'safe account'.",
                    "Speak to a family member or call 101 to verify with genuine police."
                ]
                do_not_do_points = [
                    "Do not stay on the video call to 'prove' your innocence.",
                    "Do not show your bank screen or room on camera.",
                    "Do not send money or cryptocurrency."
                ]

            elif primary_cat_id == "fake_kyc":
                risk_level = "very_likely_scam"
                title = "🔴 VERY LIKELY A SCAM (Fake Account/KYC Alert)"
                why_points = [
                    "Threatens to block or suspend your account/SIM immediately.",
                    "Contains an unverified link asking you to update personal or banking details.",
                    "Real banks never threaten same-day deactivation through WhatsApp or SMS."
                ]
                do_now_points = [
                    "Do not click the link.",
                    "Log into your bank account through their official app or verified website directly.",
                    "Call the phone number printed on the back of your physical bank card if unsure."
                ]
                do_not_do_points = [
                    "Do not tap or click the link.",
                    "Do not enter passwords, PINs, or card numbers.",
                    "Do not reply to the message."
                ]

            elif primary_cat_id == "upi_payment":
                risk_level = "very_likely_scam"
                title = "🔴 VERY LIKELY A SCAM (Payment / PIN Request)"
                why_points = [
                    "Asking for your PIN or asking you to scan a QR code to 'receive' money.",
                    "Important rule: You NEVER need to enter a PIN to receive funds — entering a PIN only sends money.",
                    "Claims of refunds or cashback requiring PIN entry are fraudulent."
                ]
                do_now_points = [
                    "Decline and cancel any payment request immediately.",
                    "Keep your PIN completely confidential.",
                    "Stop messaging the person."
                ]
                do_not_do_points = [
                    "NEVER enter your PIN to receive money.",
                    "Do not scan QR codes sent by strangers.",
                    "Do not share OTPs."
                ]

            elif primary_cat_id == "otp_theft":
                risk_level = "very_likely_scam"
                title = "🔴 VERY LIKELY A SCAM (Verification Code Theft)"
                why_points = [
                    "Asks you to share a security code or OTP sent to your phone.",
                    "Real banks and genuine companies will NEVER ask you for your OTP.",
                    "Sharing this code gives the scammer full access to your account or money."
                ]
                do_now_points = [
                    "Keep the code secret — do not tell anyone.",
                    "Delete the request and block the sender.",
                    "Check your account directly from your official app."
                ]
                do_not_do_points = [
                    "Do not forward or read the code aloud.",
                    "Do not trust someone claiming they sent it 'by mistake'."
                ]

            elif primary_cat_id == "fake_delivery":
                risk_level = "very_likely_scam"
                title = "🔴 VERY LIKELY A SCAM (Fake Delivery Fee)"
                why_points = [
                    "Claims a parcel cannot be delivered until you pay a small fee.",
                    "The link does not belong to the official delivery service (e.g. Royal Mail or Evri).",
                    "Scammers use small £1 or £2 fees as bait to steal your entire card details."
                ]
                do_now_points = [
                    "Do not click the link.",
                    "Check the parcel using your official delivery tracking number on the genuine website.",
                    "Delete the message."
                ]
                do_not_do_points = [
                    "Do not enter your card details.",
                    "Do not pay any unexpected redelivery charges."
                ]

            elif primary_cat_id == "remote_access":
                risk_level = "very_likely_scam"
                title = "🔴 VERY LIKELY A SCAM (Remote Access Trap)"
                why_points = [
                    "Asks you to install screen-sharing software (like AnyDesk, TeamViewer, or QuickSupport).",
                    "Genuine banks and tech support will NEVER ask to control your screen or device.",
                    "Allowing remote access lets someone see your bank login and passwords."
                ]
                do_now_points = [
                    "Disconnect your internet and turn off your device immediately.",
                    "Do not download or approve any app requested by the caller.",
                    "Contact your bank using the number on your card from a different phone."
                ]
                do_not_do_points = [
                    "Do not give anyone the 9-digit code on screen.",
                    "Do not log into banking while someone is connected."
                ]

            elif primary_cat_id == "family_impersonation":
                risk_level = "very_likely_scam"
                title = "🔴 VERY LIKELY A SCAM ('Hi Mum / Family' Scam)"
                why_points = [
                    "Claims to be a family member who lost or broke their phone.",
                    "Creates an urgent excuse to demand money or bill payment to a stranger's account.",
                    "This is a common scam designed to prey on caring parents and grandparents."
                ]
                do_now_points = [
                    "Do NOT send any money.",
                    "Call your loved one directly on their OLD, trusted phone number.",
                    "Ask them a personal question only your real family member would know."
                ]
                do_not_do_points = [
                    "Do not transfer money to the new account.",
                    "Do not panic — verify first."
                ]

            else:
                # Other matched high-risk categories (HMRC, crypto, lottery)
                risk_level = "very_likely_scam"
                title = f"🔴 VERY LIKELY A SCAM ({primary_cat_info.get('name', 'Suspicious Message')})"
                why_points = [
                    primary_cat_info.get("reason_template", "Contains high-risk fraud patterns."),
                    "Demands money or personal information under urgency.",
                    "Uses an unverified channel to make financial demands."
                ]
                do_now_points = primary_cat_info.get("advice", [
                    "Do not send money or share personal details.",
                    "Contact the organisation through an independently verified official channel."
                ])[:3]
                do_not_do_points = [
                    "Do not click links or send funds.",
                    "Do not call the phone number in the message."
                ]

        elif indicators["suspicious_link"] or indicators["urgent_pressure"] or demands_money:
            # Medium warning signs
            risk_level = "suspicious"
            title = "🟠 THIS LOOKS SUSPICIOUS"
            if indicators["suspicious_link"]:
                why_points.append("The message contains an unverified web link or shortened URL.")
            if indicators["urgent_pressure"]:
                why_points.append("It pressures you to act quickly or claims an urgent deadline.")
            if demands_money:
                why_points.append("It mentions transferring money or making an unexpected payment.")
            if not why_points:
                why_points.append("It contains unusual requests for personal action.")
            
            do_now_points = [
                "Don't click the link yet.",
                "Contact the company using its official website or phone number.",
                "Check with a family member or friend before doing anything."
            ]
            do_not_do_points = [
                "Do not enter personal or banking details.",
                "Do not reply until you have confirmed who sent it."
            ]

        else:
            # Low scam signs / Probably legitimate
            # Rule from prompt: Calm, short, reassuring result without scary scam recovery or 'What not to do'
            risk_level = "probably_legitimate"
            title = "🟢 PROBABLY LEGITIMATE"
            why_points = [
                "No obvious scam signs were found."
            ]
            do_now_points = [
                "Check the sender.",
                "Use the organisation's official app or website.",
                "Never share an OTP or PIN."
            ]
            do_not_do_points = []

        # Determine visibility flags strictly based on validated risk level
        show_what_not_to_do = risk_level in ["suspicious", "very_likely_scam"]
        show_already_acted = risk_level in ["suspicious", "very_likely_scam"]

        # Ensure bullet points are strictly 2-4 items max
        why_points = why_points[:4]
        do_now_points = do_now_points[:4]
        do_not_do_points = do_not_do_points[:3] if show_what_not_to_do else []

        return {
            "risk_level": risk_level,
            "title": title,
            "scam_type": primary_category or "general",
            "why": why_points,
            "do_now": do_now_points,
            "do_not_do": do_not_do_points,
            "show_what_not_to_do": show_what_not_to_do,
            "show_already_acted": show_already_acted,
            "already_acted": already_acted_points if show_already_acted else [],
            "confidence": "high" if risk_level == "very_likely_scam" else "medium",
            "indicators": indicators,
            "url_analysis": url_analysis
        }

    def match_recovery_intent(self, text: str) -> str:
        """
        Classifies user-reported recovery description (typed or voice transcript)
        into one of the 8 targeted categories across all 5 languages.
        """
        if not text:
            return "something_else"
        
        t = text.lower().strip()

        # 1. Money
        money_words = [
            "money", "sent money", "transferred", "paid", "sent £", "transfer", "wired",
            "dinheiro", "transferi", "paguei", "enviei dinheiro", "valor",
            "pieniądze", "przelew", "przelałem", "zapłaciłem", "wysłałem pieniądze",
            "bani", "am trimis bani", "am plătit", "transferat",
            "ਪੈਸੇ", "ਭੇਜੇ", "ਭੁਗਤਾਨ", "ਟਰਾਂਸਫਰ"
        ]
        if any(w in t for w in money_words):
            return "money"

        # 2. OTP / Code
        otp_words = [
            "otp", "verification code", "security code", "sms code", "6 digit", "4 digit", "code sent",
            "código", "codigo", "sms",
            "kod", "kod sms", "kod weryfikacyjny",
            "cod", "cod sms", "cod de verificare",
            "ਓਟੀਪੀ", "ਕੋਡ", "ਪੁਸ਼ਟੀ ਕੋਡ", "ਸੁਰੱਖਿਆ ਕੋਡ"
        ]
        if any(w in t for w in otp_words):
            return "otp"

        # 3. Password
        password_words = [
            "password", "login password", "passcode",
            "senha", "palavra-passe",
            "hasło", "haslo",
            "parolă", "parola",
            "ਪਾਸਵਰਡ"
        ]
        if any(w in t for w in password_words):
            return "password"

        # 4. Bank or Card details
        card_words = [
            "card", "bank card", "credit card", "debit card", "cvv", "bank account", "sort code", "account number",
            "cartão", "cartao", "conta bancária", "dados bancários",
            "karta", "numer karty", "dane konta", "rachunek",
            "card bancar", "număr card", "cont bancar",
            "ਕਾਰਡ", "ਬੈਂਕ ਖਾਤਾ", "ਖਾਤਾ ਨੰਬਰ"
        ]
        if any(w in t for w in card_words):
            return "bank_card"

        # 5. Personal or ID details
        id_words = [
            "passport", "driving licence", "id card", "identity", "national insurance", "date of birth",
            "passaporte", "identidade", "rg", "cpf", "documento",
            "pesel", "dowód", "paszport", "prawo jazdy", "dane osobowe",
            "cnp", "buletin", "pașaport", "act de identitate",
            "ਪਾਸਪੋਰਟ", "ਪਛਾਣ ਪੱਤਰ", "ਨਿੱਜੀ ਜਾਣਕਾਰੀ"
        ]
        if any(w in t for w in id_words):
            return "personal_id"

        # 6. Clicked a link
        link_words = [
            "clicked", "clicked a link", "opened link", "link", "website", "opened website",
            "cliquei", "abri o link", "link suspeito", "site",
            "kliknąłem", "otworzyłem link", "wszedłem na stronę",
            "am apăsat", "am deschis linkul", "site web",
            "ਲਿੰਕ", "ਖੋਲ੍ਹਿਆ"
        ]
        if any(w in t for w in link_words):
            return "clicked_link"

        # 7. Installed an app
        app_words = [
            "installed", "installed an app", "downloaded", "app", "anydesk", "teamviewer", "quicksupport", "remote access",
            "instalei", "baixei", "aplicativo",
            "zainstalowałem", "pobrałem", "aplikacja",
            "am instalat", "am descărcat", "aplicație",
            "ਐਪ", "ਇੰਸਟਾਲ", "ਡਾਊਨਲੋਡ"
        ]
        if any(w in t for w in app_words):
            return "installed_app"

        return "something_else"

# Singleton instance
scam_rule_engine = ScamRuleEngine()
