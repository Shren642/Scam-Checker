# 🛡️ Scam-Check: WhatsApp Scam-Checking Assistant for Elderly People

**Scam-Check** is a beginner-friendly, accessibility-focused scam detection and safety assistant built specifically for older adults and their families. It helps identify potentially fraudulent messages, screenshots, voice notes, suspicious links, and phone calls.

The core philosophy of Scam-Check is **harm prevention and user empowerment**:
> "HELP THE USER AVOID LOSING MONEY OR PERSONAL INFORMATION"

It answers three simple questions for the user:
1. **"Could this be a scam?"** (🔴 VERY LIKELY A SCAM, 🟠 SUSPICIOUS / BE CAREFUL, or 🟢 NO OBVIOUS SCAM SIGNS)
2. **"Why?"** (2 to 4 simple, jargon-free bullet points)
3. **"What should I do now?"** (Clear, direct, and reassuring next steps)

---

## 🌟 Key Features

- **WhatsApp-First & Web Simulator**: Forward suspicious WhatsApp messages, attach screenshots, or record voice notes directly in WhatsApp or in the built-in senior-accessible web interface.
- **Full Multilingual Support (5 Languages)**:
  - 🇬🇧 **English** (`en`)
  - 🇮🇳 **ਪੰਜਾਬੀ / Punjabi** (`pa`)
  - 🇵🇱 **Polski / Polish** (`pl`)
  - 🇷🇴 **Română / Romanian** (`ro`)
  - 🇵🇹 **Português / Portuguese** (`pt`)
  Once a language is chosen, **all interface text, headings, buttons, instructions, and advice switch completely** to that language.
- **Calm Legitimate Notices**: Messages classified as `🟢 PROBABLY LEGITIMATE` display a clean, reassuring notice without alarming fraud checklists, hiding "What NOT to do" and the recovery flow.
- **Conditional Scam Warnings**: "What NOT to do" and "Have you already sent something?" only appear when messages are `🔴 VERY LIKELY A SCAM` or `🟠 SUSPICIOUS`.
- **Targeted Step-by-Step Recovery Flow**: Replaced the overwhelming text dump with a calm, one-question-at-a-time flow. Asks what the user actually sent/did (Money, OTP, Password, Bank or card details, Personal or ID details, Clicked a link, Installed an app, Something else) and gives **only the relevant 3-4 bullet points**, plus voice support!
- **Speech-to-Text & "Hear this advice" (TTS)**: Send voice notes explaining what happened or listen to the safety advice read aloud in a calm, clear voice for users who struggle to read small text.
- **Senior-Friendly & Calm UI**: High-contrast typography (WCAG AAA), font size toggles (A, A+, A++), large touch buttons (54px+), soft calming colors (no flashing neon or anxiety-inducing alerts).

---

## 📂 Project Structure

```text
scam-check-bot/
├── app.py                     # Flask web app, API endpoints & webhook handlers
├── scam_logic.py              # Deterministic scam pattern engine & URL inspector
├── ai_service.py              # Gemini AI integration with structured JSON schema
├── voice_service.py           # Speech-to-text transcription & speech synthesis
├── whatsapp_service.py        # Meta WhatsApp Cloud API & Twilio webhook router
├── language_service.py        # Multi-language translation & language detection
├── config.py                  # Application configuration & environment settings
│
├── templates/
│   ├── index.html             # Accessible elderly-friendly web app & simulator
│   └── guide.html             # Printable step-by-step "How to check a scam" guide
│
├── static/
│   ├── style.css              # Calm, high-contrast, accessible CSS design system
│   └── script.js              # Accessible frontend logic, recording & TTS audio
│
├── data/
│   ├── scam_patterns.json     # Curated high-risk scam triggers & heuristics
│   ├── trusted_domains.json   # Verified UK/international domains & suspicious TLDs
│   └── translations.json      # Complete translations across all 5 languages
│
├── tests/
│   ├── __init__.py
│   ├── test_scam_logic.py     # Unit tests for scam categories, URLs & rules
│   ├── test_ai_service.py     # Unit tests for AI structure, safety & damage control
│   └── test_language.py       # Unit tests for 5 languages & detection
│
├── .env.example               # Environment variables template
├── requirements.txt           # Python dependencies
└── README.md                  # Complete documentation and setup guide
```

---

## 🚀 Quick Start (Local Setup)

### 1. Prerequisites
- **Python 3.10+** (Python 3.13 fully supported with `audioop-lts` and `standard-aifc`)
- Free Google Gemini API Key from [Google AI Studio](https://aistudio.google.com/app/apikey) (optional for offline testing; deterministic engine runs without key)

### 2. Clone and Install Dependencies
```bash
git clone https://github.com/your-username/scam-check-bot.git
cd scam-check-bot

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` to add your credentials:
```env
# Gemini API Key (get free key at https://aistudio.google.com/app/apikey)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash

# Flask Secret Key
SECRET_KEY=generate_a_random_secret_key_here

# Meta WhatsApp Cloud API (optional for live WhatsApp numbers)
WHATSAPP_TOKEN=your_meta_system_user_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_VERIFY_TOKEN=scam_check_verify_token_123

# Twilio WhatsApp (optional alternative)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=whatsapp:+14155238886
```

### 4. Run the Application
```bash
python app.py
```
Open your browser and navigate to:
**`http://127.0.0.1:5000`**

You will see the senior-friendly Scam-Check dashboard with quick scam scenarios, screenshot upload, microphone recording, audio playback, and language switching.

---

## 🧪 Running the Test Suite

Run all automated unit tests using `pytest`:
```bash
python -m pytest tests/
```

All 21 comprehensive test cases verify:
1. **Digital arrest scams** (police/court impersonation, video call isolation)
2. **Fake KYC / account suspension scams** (urgent deadline, unverified link)
3. **UPI payment scams** (requests to enter PIN to "receive" refund)
4. **OTP / security code theft**
5. **Fake parcel delivery fees** (Royal Mail / Evri £1 fee traps)
6. **Remote access traps** (AnyDesk / TeamViewer requests)
7. **Family emergency scams** ("Hi Mum, I lost my phone")
8. **Crypto & guaranteed investment scams**
9. **Lottery & prize giveaways**
10. **Legitimate notices** (verifying cautious wording: `🟢 NO OBVIOUS SCAM SIGNS`, never "safe")
11. **URL extraction & suspicious TLD checks** (`.xyz`, `.top`, shorteners)
12. **Safety rules** (ensuring the bot never asks for passwords, PINs, or card numbers)
13. **Damage control emergency guidance** in English and Punjabi
14. **Multilingual translation coverage** across English, Punjabi, Polish, Romanian, Portuguese.

---

## 📲 WhatsApp Integration Setup

### Option A: Meta WhatsApp Business Cloud API (Official)

1. **Create a Meta Developer Account**:
   - Go to [developers.facebook.com](https://developers.facebook.com) and create an app with type **Business**.
   - Add the **WhatsApp** product.
2. **Get Test Credentials**:
   - Note your `Temporary Access Token` and `Phone Number ID`.
   - Add them to `.env`:
     ```env
     WHATSAPP_TOKEN=EAAG...
     WHATSAPP_PHONE_NUMBER_ID=1092837465...
     WHATSAPP_VERIFY_TOKEN=scam_check_verify_token_123
     ```
3. **Configure Webhook**:
   - Use [ngrok](https://ngrok.com) or your public server to expose port 5000:
     ```bash
     ngrok http 5000
     ```
   - In the Meta App Dashboard > WhatsApp > Configuration:
     - **Callback URL**: `https://your-domain.ngrok-free.app/webhook`
     - **Verify Token**: `scam_check_verify_token_123`
     - Subscribe to the `messages` webhook field.
4. **Send a WhatsApp Message**:
   - Send `Hello` or forward any suspicious message to your WhatsApp test number!

### Option B: Twilio WhatsApp Sandbox

1. In your Twilio Console, go to **Messaging > Try it out > Send a WhatsApp message**.
2. Set the "When a message comes in" Webhook URL to:
   `https://your-domain.ngrok-free.app/twilio/webhook` (HTTP POST).
3. The bot will automatically reply with WhatsApp formatting.

---

## 🧠 Scam Rule Engine Architecture

The system uses a **defence-in-depth architecture**:
```text
User Message / Screenshot / Voice Note
                  │
                  ▼
   1. Deterministic Scam Rule Engine
   • Digital arrest keywords
   • UPI PIN & OTP theft patterns
   • Remote access software detection
   • URL & domain analysis (trusted vs suspicious TLDs)
                  │
                  ▼
   2. Google Gemini 2.5 Flash API
   • Multimodal image / screenshot OCR & layout review
   • Plain-language explainability (2-4 reasons max)
   • Strict JSON validation & safety filtering
                  │
                  ▼
   3. Localized Formatting & Damage Control
   • 5 language translations
   • Audio script generation for "Hear this advice" (TTS)
   • Damage control prompt: "Have you already sent money?"
```

---

## 🇬🇧 UK Official Safety Guidance

Scam-Check adheres strictly to UK fraud reporting best practices:
- **Bank Card Rule**: Always advise users to call the phone number printed directly on the **back of their physical bank card**, NEVER a number from an email or message.
- **Action Fraud**: UK national reporting centre for fraud and cybercrime: **`0300 123 2040`** ([actionfraud.police.uk](https://www.actionfraud.police.uk)).
- **Police Non-Emergency**: Dial **`101`** to report suspicious callers or verify police officers.
- **Emergency**: Call **`999`** ONLY if in immediate physical danger.

---

## 🔒 Privacy and Safety Constraints

- **Zero Credential Harvesting**: The bot never asks for passwords, PINs, OTPs, or bank card details.
- **No Link Visiting**: The bot never accesses or executes untrusted links on behalf of users.
- **No Blame / High Reassurance**: Elderly users are never shamed or blamed for interacting with a scam. Scams are designed to manipulate; checking is always praised.
- **Ephemeral Processing**: Uploaded screenshots and audio files are processed in-memory or in temporary directories and never stored permanently in v1.

---

## 📄 License
MIT License. Built for community safety and senior protection.
