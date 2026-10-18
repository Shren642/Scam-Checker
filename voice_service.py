import os
import io
try:
    import speech_recognition as sr
    HAVE_SR = True
except Exception as e:
    sr = None
    HAVE_SR = False
    print(f"Warning: speech_recognition could not be loaded: {e}")

from config import Config

# Language mapping for SpeechRecognition Google STT
STT_LANG_CODES = {
    "en": "en-GB",
    "pa": "pa-IN",
    "pl": "pl-PL",
    "ro": "ro-RO",
    "pt": "pt-PT"
}

class VoiceService:
    def __init__(self):
        if HAVE_SR and sr:
            self.recognizer = sr.Recognizer()
        else:
            self.recognizer = None

    def transcribe_audio_file(self, file_path_or_bytes, lang: str = "en") -> dict:
        """
        Transcribes an audio recording (WAV, FLAC, AIFF) to text using speech recognition.
        Returns a dict with 'success', 'text', and 'language'.
        """
        stt_lang = STT_LANG_CODES.get(lang, "en-GB")
        
        if not self.recognizer or not sr:
            return {
                "success": False,
                "text": "",
                "error": "Speech recognition service is currently initializing. Please type what happened or try again."
            }

        try:
            # If path was given
            if isinstance(file_path_or_bytes, str):
                with sr.AudioFile(file_path_or_bytes) as source:
                    audio = self.recognizer.record(source)
            else:
                # BytesIO or in-memory
                with sr.AudioFile(file_path_or_bytes) as source:
                    audio = self.recognizer.record(source)

            # Try primary recognition in user's selected language
            text = self.recognizer.recognize_google(audio, language=stt_lang)
            return {
                "success": True,
                "text": text,
                "language": lang
            }
        except sr.UnknownValueError:
            return {
                "success": False,
                "text": "",
                "error": "I didn't hear that clearly. Please send another voice message or type what the caller said."
            }
        except sr.RequestError as e:
            # Fallback or connection issue
            print(f"STT API request error: {e}")
            return {
                "success": False,
                "text": "",
                "error": "Could not access speech recognition service. Please try typing what they told you."
            }
        except Exception as e:
            print(f"Audio processing error: {e}")
            return {
                "success": False,
                "text": "",
                "error": "Audio format could not be decoded. Please send a WAV or record directly."
            }

    def generate_speech_text(self, analysis_result: dict, lang: str = "en") -> str:
        """
        Creates a clear, elderly-friendly script for Text-to-Speech playback.
        Uses short sentences and a warm, steady, reassuring tone.
        """
        title = analysis_result.get("title", "")
        why = analysis_result.get("why", [])
        do_now = analysis_result.get("do_now", [])
        
        script = f"{title}. "
        if why:
            script += "Here is why: " + ". ".join(why) + ". "
        if do_now:
            script += "Here is what you should do right now: " + ". ".join(do_now) + ". "
        
        script += "Remember, real police and your bank will never ask for your PIN, password, or security code."
        return script

# Singleton instance
voice_service = VoiceService()
