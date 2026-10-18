import pytest
from ai_service import ai_service
from language_service import language_service
from scam_logic import scam_rule_engine

def test_ai_service_structure_and_fallback():
    # Tests analysis structure even without Gemini API key (clean fallback)
    text = "Someone claiming to be police told me I am under digital arrest and must send £5000."
    res = ai_service.analyze_content(text=text, lang="en")
    
    assert "risk_level" in res
    assert res["risk_level"] in ("very_likely_scam", "suspicious", "probably_legitimate")
    assert "title" in res
    assert "why" in res
    assert "do_now" in res
    assert "do_not_do" in res
    assert res["show_what_not_to_do"] is True
    assert res["show_already_acted"] is True
    assert isinstance(res["why"], list)
    assert len(res["why"]) <= 4

def test_legitimate_result_structure():
    text = "Your Tesco grocery delivery will arrive between 14:00 and 15:00 today."
    res = ai_service.analyze_content(text=text, lang="en")
    assert res["risk_level"] == "probably_legitimate"
    assert res["show_what_not_to_do"] is False
    assert res["show_already_acted"] is False
    assert len(res["do_not_do"]) == 0

def test_safety_principles():
    # Prompt rule #46: Test that the bot NEVER asks for OTP/PIN/Password/Card numbers
    text = "Someone asked me for my bank card number."
    res = ai_service.analyze_content(text=text, lang="en")
    msg = ai_service.format_whatsapp_message(res, lang="en")
    
    forbidden_terms = ["please send your password", "give me your pin", "tell me your pin", "send your full card number"]
    for term in forbidden_terms:
        assert term not in msg.lower()

def test_whatsapp_message_formatting_scam():
    res = {
        "risk_level": "very_likely_scam",
        "title": "🔴 VERY LIKELY A SCAM",
        "scam_type": "fake_kyc",
        "why": ["Account suspension threat", "Suspicious link"],
        "do_now": ["Do not click the link", "Call bank using card number"],
        "do_not_do": ["Do not share PIN"],
        "show_what_not_to_do": True,
        "show_already_acted": True,
        "confidence": "high"
    }
    msg = ai_service.format_whatsapp_message(res, lang="en")
    assert "🔴 VERY LIKELY A SCAM" in msg
    assert "Why it looks suspicious:" in msg
    assert "What to do now:" in msg
    assert "What NOT to do:" in msg
    assert "Have you already sent something" in msg

def test_whatsapp_message_formatting_legitimate():
    res = {
        "risk_level": "probably_legitimate",
        "title": "🟢 PROBABLY LEGITIMATE",
        "scam_type": "general",
        "why": ["No obvious scam signs were found."],
        "do_now": ["Check the sender.", "Use the organisation's official app or website.", "Never share an OTP or PIN."],
        "do_not_do": [],
        "show_what_not_to_do": False,
        "show_already_acted": False,
        "confidence": "medium"
    }
    msg = ai_service.format_whatsapp_message(res, lang="en")
    assert "🟢 PROBABLY LEGITIMATE" in msg
    assert "No obvious scam signs were found." in msg
    # Must NOT display 'What NOT to do'
    assert "What NOT to do:" not in msg
    # Must NOT ask 'Have you already sent something?'
    assert "Have you already sent" not in msg

def test_user_reported_loss_handling():
    # Even if original message appeared legitimate, user reporting financial loss gets money advice
    advice = language_service.get_recovery_advice("money", "en")
    assert "bank immediately" in advice["points"][0].lower()
    assert "stopped or recalled" in advice["points"][1].lower() or "stopped or recalled" in advice["points"][2].lower()
