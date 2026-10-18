import pytest
from language_service import language_service

def test_supported_languages():
    langs = language_service.get_supported_languages()
    assert "en" in langs
    assert "pa" in langs
    assert "pl" in langs
    assert "ro" in langs
    assert "pt" in langs

def test_translation_completeness():
    # Verify critical UI and recovery keys exist in all 5 languages
    critical_keys = [
        "app_title",
        "brand_subtitle",
        "welcome_greeting",
        "welcome_question",
        "risk_very_likely",
        "risk_suspicious",
        "risk_legitimate",
        "why_heading",
        "do_now_heading",
        "do_not_do_heading",
        "reassurance_msg",
        "check_another_btn",
        "back_btn",
        "legit_no_signs_found",
        "legit_before_acting",
        "legit_check_sender",
        "legit_official_app",
        "legit_never_share_otp",
        "already_acted_question",
        "already_acted_yes",
        "already_acted_no",
        "no_action_reassurance",
        "recovery_question",
        "recovery_options_title",
        "opt_money",
        "opt_otp",
        "opt_password",
        "opt_bank_card",
        "opt_personal_id",
        "opt_clicked_link",
        "opt_installed_app",
        "opt_something_else",
        "act_now_title",
        "advice_money_p1",
        "advice_otp_p1",
        "advice_password_p1",
        "advice_bank_card_p1",
        "advice_personal_id_p1",
        "advice_clicked_link_p1",
        "advice_installed_app_p1",
        "official_contacts_title",
        "official_bank_line",
        "official_action_fraud",
        "official_police_101",
        "guide_title",
        "guide_subtitle"
    ]
    for lang in ["en", "pa", "pl", "ro", "pt"]:
        full_dict = language_service.get_all_translations_for_lang(lang)
        assert len(full_dict) > 40
        for key in critical_keys:
            val = language_service.get_text(key, lang)
            assert val != key, f"Missing key '{key}' in language '{lang}'"
            assert len(val.strip()) > 0

def test_recovery_options_structure():
    for lang in ["en", "pa", "pl", "ro", "pt"]:
        options = language_service.get_recovery_options(lang)
        assert len(options) == 8
        ids = [opt["id"] for opt in options]
        assert ids == ["money", "otp", "password", "bank_card", "personal_id", "clicked_link", "installed_app", "something_else"]
        for opt in options:
            assert len(opt["label"].strip()) > 0
            assert len(opt["icon"]) > 0

def test_targeted_recovery_advice():
    for lang in ["en", "pa", "pl", "ro", "pt"]:
        for cat in ["money", "otp", "password", "bank_card", "personal_id", "clicked_link", "installed_app"]:
            advice = language_service.get_recovery_advice(cat, lang)
            assert advice["category"] == cat
            assert len(advice["points"]) >= 3
            assert len(advice["title"]) > 0
            assert len(advice["official_bank_line"]) > 0

def test_language_selection_and_switch():
    user = "user_447123456789"
    assert language_service.get_user_language(user) == "en"
    
    # Change to Punjabi
    language_service.set_user_language(user, "pa")
    assert language_service.get_user_language(user) == "pa"

    # Change via number "3" (Polish)
    language_service.set_user_language(user, "3")
    assert language_service.get_user_language(user) == "pl"

def test_language_detection():
    # Punjabi Gurmukhi script
    pa_text = "ਮੈਨੂੰ ਇੱਕ ਸ਼ੱਕੀ ਫੋਨ ਆਇਆ ਸੀ"
    assert language_service.detect_potential_language(pa_text) == "pa"

    # Polish diacritics
    pl_text = "Czy to jest oszustwo? Płatność za paczkę"
    assert language_service.detect_potential_language(pl_text) == "pl"

    # Romanian diacritics
    ro_text = "Contul dumneavoastră a fost blocat"
    assert language_service.detect_potential_language(ro_text) == "ro"

    # Portuguese text
    pt_text = "Recebi uma mensagem sobre um golpe"
    assert language_service.detect_potential_language(pt_text) == "pt"
