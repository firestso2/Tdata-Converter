# Session Exporter Bot

Author: **@vorache777**

A Telegram bot that authenticates via phone number and exports your
account into three portable formats:

| Format | Description |
|---|---|
| `.session` | SQLite file for use with `TelegramClient('name', …)` |
| Session string | Single-line string for `StringSession(…)` |
| `tdata.zip` | Minimal Telegram Desktop session folder |
| `session.json` | API credentials + account metadata |

---

## Quick start

```bash
git clone …
cd tg_session_bot
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env — set BOT_TOKEN, API_ID, API_HASH

python bot.py
```

## Configuration

| Variable | Required | Description |
|---|---|---|
| `BOT_TOKEN` | ✅ | From [@BotFather](https://t.me/BotFather) |
| `API_ID` | ✅ | From [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | ✅ | From [my.telegram.org](https://my.telegram.org) |

> **Default API credentials** (`2040` / `b18441a1ff607e10a989891a5462e627`) are
> the official Telegram Desktop credentials — safe to use for personal bots.

---

## Project layout

```
tg_session_bot/
├── bot.py                  # Entry point — polling loop
├── config.py               # Config dataclass + env loader
├── keyboards.py            # Inline keyboard factories
├── requirements.txt
├── states/
│   └── auth.py             # FSM states (phone → code → 2FA → done)
├── handlers/
│   ├── start.py            # /start + back-to-menu
│   ├── auth.py             # FSM flow: phone / code / 2FA password
│   └── download.py         # Inline button download callbacks
└── utils/
    ├── client_manager.py   # Per-user Telethon client pool
    ├── session_export.py   # .session file + session string + JSON
    └── tdata_export.py     # Minimal tdata/ ZIP builder
```

---

## Auth flow (FSM)

```
/start
  └─[Login with phone]──► waiting_phone
                              │ valid phone → send_code_request
                              ▼
                          waiting_code
                              │ correct code → sign_in
                              │ PhoneCodeInvalidError → stay, ask again
                              │ SessionPasswordNeededError ──►
                              ▼
                          waiting_password
                              │ correct pwd → sign_in
                              │ PasswordHashInvalidError → stay, ask again
                              ▼
                          authenticated ──► download menu
```

---

## tdata format notes

The `tdata.zip` contains:

```
tdata/
├── key_datas          — AES-IGE encrypted auth key + DC info
├── 1C6EB2A0/          — working directory (CRC32 of "data")
│   └── map0           — encrypted data map
├── settings0          — connection settings
└── version            — TD version marker
```

Encryption uses **AES-IGE** with a key derived via
**PBKDF2-HMAC-SHA1** (1 iteration, empty passcode).  
This matches Telegram Desktop ≤ 4.x local storage format.

---

## Dependencies

- [aiogram 3.x](https://docs.aiogram.dev/) — async bot framework
- [Telethon](https://docs.telethon.dev/) — MTProto client / session auth
- [cryptography](https://cryptography.io/) — AES-IGE for tdata encryption
