import json
import struct
import sqlite3
import tempfile
import os
from io import BytesIO
from telethon import TelegramClient
from telethon.sessions import StringSession


async def export_session_string(client: TelegramClient) -> str:
    """Return the Telethon StringSession value."""
    return client.session.save()


async def export_session_file(client: TelegramClient, filename: str = "session") -> BytesIO:
    """
    Build a .session SQLite file in-memory and return as BytesIO.
    Telethon stores sessions in SQLite; we copy the live session into a
    temp file, then read it back into a BytesIO buffer.
    """
    session_string = client.session.save()

    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, f"{filename}.session")

        # Re-create the session in a real file so we get a proper SQLite DB
        tmp_client = TelegramClient(path, client.api_id, client.api_hash)
        tmp_session = StringSession(session_string)

        # Manually copy session data into SQLite
        conn = sqlite3.connect(path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                dc_id     INTEGER PRIMARY KEY,
                server_address TEXT,
                port      INTEGER,
                auth_key  BLOB
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id        INTEGER PRIMARY KEY,
                hash      INTEGER NOT NULL,
                username  TEXT,
                phone     TEXT,
                name      TEXT,
                date      INTEGER
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sent_files (
                md5_digest BLOB,
                file_size  INTEGER,
                type       INTEGER,
                id         INTEGER,
                hash       INTEGER,
                PRIMARY KEY (md5_digest, file_size, type)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS update_state (
                id    INTEGER PRIMARY KEY,
                pts   INTEGER,
                qts   INTEGER,
                date  INTEGER,
                seq   INTEGER
            )
        """)

        # Pull auth data from the StringSession
        dc_id = tmp_session.dc_id
        server_address = tmp_session.server_address
        port = tmp_session.port
        auth_key = bytes(tmp_session.auth_key.key) if tmp_session.auth_key else b""

        conn.execute(
            "INSERT OR REPLACE INTO sessions VALUES (?, ?, ?, ?)",
            (dc_id, server_address, port, auth_key),
        )
        conn.commit()
        conn.close()

        buf = BytesIO()
        with open(path, "rb") as f:
            buf.write(f.read())
        buf.seek(0)
        buf.name = f"{filename}.session"
        return buf


async def export_json(client: TelegramClient, api_id: int, api_hash: str,
                      device_model: str, system_version: str,
                      app_version: str) -> BytesIO:
    """Export account metadata + session string as JSON."""
    me = await client.get_me()
    session_string = client.session.save()
    tmp = StringSession(session_string)

    data = {
        "schema_version": 1,
        "session_string": session_string,
        "dc_id": tmp.dc_id,
        "server_address": tmp.server_address,
        "port": tmp.port,
        "api_id": api_id,
        "api_hash": api_hash,
        "device_model": device_model,
        "system_version": system_version,
        "app_version": app_version,
        "account": {
            "id": me.id,
            "first_name": me.first_name or "",
            "last_name": me.last_name or "",
            "username": me.username or "",
            "phone": me.phone or "",
            "is_bot": me.bot,
            "is_premium": getattr(me, "premium", False),
        },
    }

    payload = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    buf = BytesIO(payload)
    buf.name = "session.json"
    return buf
