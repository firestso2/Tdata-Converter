import asyncio
from typing import Dict, Any
from telethon import TelegramClient
from telethon.sessions import StringSession

# Stores per-user Telethon clients and transient data
_clients: Dict[int, TelegramClient] = {}
_user_data: Dict[int, Dict[str, Any]] = {}


async def get_or_create_client(user_id: int, api_id: int, api_hash: str,
                                device_model: str, system_version: str,
                                app_version: str, lang_code: str,
                                system_lang_code: str) -> TelegramClient:
    if user_id in _clients:
        client = _clients[user_id]
        if not client.is_connected():
            await client.connect()
        return client

    client = TelegramClient(
        StringSession(),
        api_id,
        api_hash,
        device_model=device_model,
        system_version=system_version,
        app_version=app_version,
        lang_code=lang_code,
        system_lang_code=system_lang_code,
    )
    await client.connect()
    _clients[user_id] = client
    return client


def store_user_data(user_id: int, key: str, value: Any) -> None:
    if user_id not in _user_data:
        _user_data[user_id] = {}
    _user_data[user_id][key] = value


def get_user_data(user_id: int, key: str, default: Any = None) -> Any:
    return _user_data.get(user_id, {}).get(key, default)


async def disconnect_client(user_id: int) -> None:
    client = _clients.pop(user_id, None)
    if client and client.is_connected():
        await client.disconnect()
    _user_data.pop(user_id, None)
