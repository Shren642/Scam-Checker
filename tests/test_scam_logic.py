import pytest
from scam_logic import scam_rule_engine

def test_digital_arrest():
    text = "Police say I will be arrested unless I transfer money to a safe account and stay on video call."
    res = scam_rule_engine.evaluate(text)
    assert res["risk_level"] == "very_likely_scam"
    assert res["scam_type"] == "digital_arrest"
    assert res["show_what_not_to_do"] is True
    assert res["show_already_acted"] is True
    assert len(res["do_not_do"]) > 0
    assert any("arrest" in w.lower() for w in res["why"])

def test_fake_kyc():
    text = "Your bank KYC expires today. Click this link to avoid account suspension: http://fake-bank-kyc.xyz"
    res = scam_rule_engine.evaluate(text)
    assert res["risk_level"] == "very_likely_scam"
    assert res["scam_type"] == "fake_kyc"
    assert res["show_what_not_to_do"] is True
    assert res["show_already_acted"] is True
    assert len(res["do_not_do"]) > 0

def test_upi_pin_theft():
    text = "Send your UPI PIN to receive your refund."
    res = scam_rule_engine.evaluate(text)
    assert res["risk_level"] == "very_likely_scam"
    assert res["scam_type"] == "upi_payment"
    assert any("pin" in w.lower() for w in res["why"] + res["do_now"])

def test_otp_theft():
    text = "Tell me the OTP I just sent you."
    res = scam_rule_engine.evaluate(text)
    assert res["risk_level"] == "very_likely_scam"
    assert res["scam_type"] == "otp_theft"
    assert any("otp" in w.lower() or "code" in w.lower() for w in res["why"] + res["do_now"])

def test_fake_delivery():
    text = "Your parcel could not be delivered. Pay £1 here: http://royalmail-parcel.xyz/pay"
    res = scam_rule_engine.evaluate(text)
    assert res["risk_level"] == "very_likely_scam"
    assert res["scam_type"] == "fake_delivery"
    assert len(res["why"]) <= 4
    assert len(res["do_now"]) <= 4

def test_remote_access():
    text = "Please download AnyDesk or TeamViewer so tech support can fix your computer."
    res = scam_rule_engine.evaluate(text)
    assert res["risk_level"] == "very_likely_scam"
    assert res["scam_type"] == "remote_access"

def test_family_impersonation():
    text = "Hi Mum, lost my phone and this is my new number. Pay this urgent bill please."
    res = scam_rule_engine.evaluate(text)
    assert res["risk_level"] == "very_likely_scam"
    assert res["scam_type"] == "family_impersonation"

def test_legitimate_message():
    text = "Your prescription from Boots Pharmacy is ready for collection."
    res = scam_rule_engine.evaluate(text)
    assert res["risk_level"] == "probably_legitimate"
    # Never say definitely safe
    assert "safe" not in res["title"].lower()
    # Visibility conditions: hide 'What NOT to do' and hide 'Have you already sent...'
    assert res["show_what_not_to_do"] is False
    assert res["show_already_acted"] is False
    assert len(res["do_not_do"]) == 0
    assert len(res["why"]) >= 1
    assert len(res["do_now"]) >= 2

def test_suspicious_message_conditions():
    text = "Important: Action required on your account. Review details at https://bit.ly/check-account"
    res = scam_rule_engine.evaluate(text)
    assert res["risk_level"] in ["suspicious", "very_likely_scam"]
    assert res["show_what_not_to_do"] is True
    assert res["show_already_acted"] is True
    assert len(res["do_not_do"]) > 0

def test_url_extraction_and_analysis():
    text = "Visit https://bit.ly/claim-prize or http://secure-update.top for details"
    urls = scam_rule_engine.extract_urls(text)
    assert len(urls) >= 2
    analysis = scam_rule_engine.analyze_urls(urls)
    assert len(analysis["shortened_urls"]) > 0 or len(analysis["suspicious_domains"]) > 0
    assert len(analysis["warnings"]) > 0

def test_investment_crypto():
    text = "Guaranteed profit! 100% daily return, double your money with our automated crypto investment bot."
    res = scam_rule_engine.evaluate(text)
    assert res["risk_level"] == "very_likely_scam"
    assert res["scam_type"] == "investment_crypto"

def test_lottery_prize():
    text = "You won lottery prize draw of £500,000! Pay processing fee to release prize now."
    res = scam_rule_engine.evaluate(text)
    assert res["risk_level"] == "very_likely_scam"
    assert res["scam_type"] == "lottery_prize"

def test_hmrc_tax_scam():
    text = "HMRC tax refund pending: click here or unpaid tax warrant will be issued immediately."
    res = scam_rule_engine.evaluate(text)
    assert res["risk_level"] == "very_likely_scam"
    assert res["scam_type"] == "fake_bank_hmrc"

def test_reason_count_constraints():
    text = "Urgent: Your account is blocked today. Transfer money to safe account immediately via link http://bad.xyz"
    res = scam_rule_engine.evaluate(text)
    assert 1 <= len(res["why"]) <= 4
    assert 1 <= len(res["do_now"]) <= 4
    assert len(res["do_not_do"]) <= 3

def test_match_recovery_intent():
    # Money
    assert scam_rule_engine.match_recovery_intent("I sent money to a bank account") == "money"
    assert scam_rule_engine.match_recovery_intent("Eu transferi 500 reais") == "money"
    assert scam_rule_engine.match_recovery_intent("przelałem pieniądze na konto") == "money"
    assert scam_rule_engine.match_recovery_intent("ਮੈਂ ਪੈਸੇ ਭੇਜ ਦਿੱਤੇ ਸਨ") == "money"

    # OTP
    assert scam_rule_engine.match_recovery_intent("I gave them the code my bank sent me") == "otp"
    assert scam_rule_engine.match_recovery_intent("podałem kod sms oszustowi") == "otp"
    assert scam_rule_engine.match_recovery_intent("am trimis codul primit prin sms") == "otp"

    # Password
    assert scam_rule_engine.match_recovery_intent("I entered my login password") == "password"
    assert scam_rule_engine.match_recovery_intent("mudei minha senha") == "password"

    # Bank Card
    assert scam_rule_engine.match_recovery_intent("I shared my debit card and CVV") == "bank_card"

    # Personal ID
    assert scam_rule_engine.match_recovery_intent("I sent a picture of my passport") == "personal_id"

    # Clicked link
    assert scam_rule_engine.match_recovery_intent("I clicked on the link in the message") == "clicked_link"

    # Installed app
    assert scam_rule_engine.match_recovery_intent("I downloaded AnyDesk on my computer") == "installed_app"
