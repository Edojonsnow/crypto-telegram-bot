from telethon.sync import TelegramClient
from dotenv import load_dotenv
import os

load_dotenv()
client = TelegramClient('session_name', os.getenv("TELEGRAM_API_ID"), os.getenv("TELEGRAM_API_HASH"))
client.start()

async def get_chats():
    async for dialog in client.iter_dialogs():
        print(f"{dialog.name} (ID: {dialog.id})")

client.loop.run_until_complete(get_chats())