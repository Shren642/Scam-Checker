import os
import io
import sys

# Configure UTF-8 console output safely on Windows
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")
except Exception:
    pass

from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
from config import Config
from scam_logic import scam_rule_engine
from ai_service import ai_service
from voice_service import voice_service
from language_service import language_service
from whatsapp_service import whatsapp_service

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
    static_url_path="/static"
)
app.config.from_object(Config)

# Ensure uploads directory exists safely without crashing on read-only serverless filesystems
try:
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
except Exception:
    app.config["UPLOAD_FOLDER"] = "/tmp/uploads"
    try:
        os.makedirs("/tmp/uploads", exist_ok=True)
    except Exception:
        pass

@app.route("/favicon.ico")
def favicon():
    return "", 204

@app.route("/")
def index():
    lang = session.get("lang", Config.DEFAULT_LANGUAGE)
    t = language_service.get_all_translations_for_lang(lang)
    recovery_options = language_service.get_recovery_options(lang)
    return render_template(
        "index.html",
        lang=lang,
        t=t,
        supported_langs=Config.SUPPORTED_LANGUAGES,
        recovery_options=recovery_options
    )

@app.route("/guide")
def guide():
    lang = session.get("lang", Config.DEFAULT_LANGUAGE)
    t = language_service.get_all_translations_for_lang(lang)
    return render_template(
        "guide.html",
        lang=lang,
        t=t,
        supported_langs=Config.SUPPORTED_LANGUAGES
    )

@app.route("/api/translations", methods=["GET"])
def get_translations():
    lang = request.args.get("lang") or session.get("lang", Config.DEFAULT_LANGUAGE)
    t = language_service.get_all_translations_for_lang(lang)
    recovery_options = language_service.get_recovery_options(lang)
    return jsonify({
        "success": True,
        "language": lang,
        "translations": t,
        "recovery_options": recovery_options
    })

@app.route("/api/set-language", methods=["POST"])
def set_language():
    data = request.get_json() or {}
    lang = data.get("language", "en").lower()
    if lang in Config.SUPPORTED_LANGUAGES:
        session["lang"] = lang
        t = language_service.get_all_translations_for_lang(lang)
        recovery_options = language_service.get_recovery_options(lang)
        return jsonify({
            "success": True,
            "language": lang,
            "translations": t,
            "recovery_options": recovery_options
        })
    return jsonify({"success": False, "error": "Unsupported language"}), 400

@app.route("/api/check", methods=["POST"])
def check_content():
    """
    Main checking endpoint for text, image, or audio input.
    """
    lang = request.form.get("lang") or session.get("lang", "en")
    text_content = request.form.get("text", "").strip()
    
    image_bytes = None
    mime_type = "image/jpeg"
    transcribed_text = ""

    # Check for uploaded image
    if "image" in request.files:
        file = request.files["image"]
        if file and file.filename != "":
            image_bytes = file.read()
            mime_type = file.mimetype or "image/jpeg"

    # Check for uploaded voice/audio
    if "audio" in request.files:
        audio_file = request.files["audio"]
        if audio_file and audio_file.filename != "":
            audio_bytes = io.BytesIO(audio_file.read())
            transcription = voice_service.transcribe_audio_file(audio_bytes, lang=lang)
            if transcription.get("success"):
                transcribed_text = transcription["text"]
                # Append transcribed speech to text_content
                text_content = f"{text_content} {transcribed_text}".strip()
            else:
                # If audio transcription fails, return friendly error in user's language
                error_msg = transcription.get("error") or language_service.get_text("fallback_error", lang)
                return jsonify({
                    "success": False,
                    "error": error_msg
                })

    if not text_content and not image_bytes:
        return jsonify({
            "success": False,
            "error": language_service.get_text("input_message_hint", lang)
        }), 400

    # Analyse content
    analysis = ai_service.analyze_content(
        text=text_content,
        image_bytes=image_bytes,
        mime_type=mime_type,
        lang=lang
    )

    # Generate speech script for 'Hear this advice' audio button
    tts_text = voice_service.generate_speech_text(analysis, lang=lang)

    return jsonify({
        "success": True,
        "transcribed_text": transcribed_text,
        "analysis": analysis,
        "tts_text": tts_text
    })

@app.route("/api/recovery-advice", methods=["POST"])
def recovery_advice():
    """
    Returns targeted 3-4 bullet point advice for the specific recovery option chosen by the user.
    """
    data = request.get_json() or {}
    category = data.get("category", "money")
    user_text = data.get("text", "")
    lang = data.get("lang") or session.get("lang", "en")

    # If category is "something_else" and text was provided, classify into targeted category
    if category == "something_else" and user_text:
        matched = scam_rule_engine.match_recovery_intent(user_text)
        if matched != "something_else":
            category = matched

    advice = language_service.get_recovery_advice(category, lang)
    return jsonify({
        "success": True,
        "category": category,
        "advice": advice
    })

@app.route("/api/recovery-voice", methods=["POST"])
def recovery_voice():
    """
    Accepts voice audio answering 'What did you send or do?', transcribes it,
    matches the intent, and returns targeted advice.
    """
    lang = request.form.get("lang") or session.get("lang", "en")
    if "audio" not in request.files:
        return jsonify({"success": False, "error": "No audio provided"}), 400
    
    audio_file = request.files["audio"]
    audio_bytes = io.BytesIO(audio_file.read())
    transcription = voice_service.transcribe_audio_file(audio_bytes, lang=lang)
    
    if not transcription.get("success"):
        return jsonify({
            "success": False,
            "error": transcription.get("error", language_service.get_text("voice_status_error", lang))
        })
    
    spoken_text = transcription["text"]
    category = scam_rule_engine.match_recovery_intent(spoken_text)
    advice = language_service.get_recovery_advice(category, lang)

    return jsonify({
        "success": True,
        "transcribed_text": spoken_text,
        "category": category,
        "advice": advice
    })

@app.route("/api/damage-control", methods=["POST"])
def damage_control():
    """Legacy endpoint preserved for backwards compatibility, returning money advice."""
    data = request.get_json() or {}
    lang = data.get("lang") or session.get("lang", "en")
    advice = language_service.get_recovery_advice("money", lang)
    return jsonify({
        "success": True,
        "title": advice.get("title"),
        "instructions": "\n".join(f"• {p}" for p in advice.get("points", []))
    })

# ----------------- WhatsApp Cloud API Webhook -----------------

@app.route("/webhook", methods=["GET"])
def whatsapp_verify():
    """Meta WhatsApp Cloud API Webhook Verification."""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    return whatsapp_service.verify_webhook(mode, token, challenge)

@app.route("/webhook", methods=["POST"])
def whatsapp_incoming():
    """Meta WhatsApp Cloud API Incoming Messages."""
    payload = request.get_json() or {}
    result = whatsapp_service.process_incoming_cloud_message(payload)
    return jsonify(result), 200

# ----------------- Twilio WhatsApp Webhook -----------------

@app.route("/twilio/webhook", methods=["POST"])
def twilio_incoming():
    """Twilio WhatsApp Sandbox Webhook handler."""
    from_number = request.form.get("From", "").replace("whatsapp:", "")
    body = request.form.get("Body", "").strip()
    num_media = int(request.form.get("NumMedia", 0))

    lang = language_service.get_user_language(from_number)
    state = whatsapp_service.user_state.get(from_number, {})

    if num_media > 0:
        media_url = request.form.get("MediaUrl0")
        media_type = request.form.get("MediaContentType0", "")
        
        try:
            res = requests.get(media_url, timeout=10)
            if "image" in media_type:
                analysis = ai_service.analyze_content(text=body, image_bytes=res.content, mime_type=media_type, lang=lang)
                reply = ai_service.format_whatsapp_message(analysis, lang=lang)
            elif "audio" in media_type:
                trans = voice_service.transcribe_audio_file(io.BytesIO(res.content), lang=lang)
                if trans.get("success"):
                    spoken = trans["text"]
                    if state.get("awaiting") == "recovery_choice":
                        cat = scam_rule_engine.match_recovery_intent(spoken)
                        reply = f"🎤 _{spoken}_\n\n" + whatsapp_service._format_targeted_recovery_whatsapp(cat, lang)
                    else:
                        analysis = ai_service.analyze_content(text=spoken, lang=lang)
                        reply = f"🎤 *Voice Note:*\n_{spoken}_\n\n" + ai_service.format_whatsapp_message(analysis, lang=lang)
                else:
                    reply = trans.get("error", "Could not transcribe audio.")
            else:
                reply = "Unsupported attachment type. Please send a screenshot or voice note."
        except Exception as e:
            reply = f"Could not retrieve media attachment: {e}"
    else:
        reply = whatsapp_service._handle_text_input(from_number, body, lang, state)

    # Return Twilio TwiML response
    twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{reply}</Message>
</Response>"""
    return twiml_response, 200, {"Content-Type": "application/xml"}

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "Scam-Check Bot",
        "gemini_configured": bool(Config.GEMINI_API_KEY),
        "whatsapp_configured": bool(Config.WHATSAPP_TOKEN and Config.WHATSAPP_PHONE_NUMBER_ID)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
