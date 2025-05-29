import os
from telethon import TelegramClient, events
from dotenv import load_dotenv
from bot import execute_trade, TRADE_AMOUNT
from ai_parser import parse_signal
from bot import exchange

# Load env vars
load_dotenv()
API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")
GROUP_ID = int(os.getenv("GROUP_ID"))

# Initialize client
async def create_telegram_client():
    client = TelegramClient(
        'signal_monitor',
        int(API_ID),
        API_HASH
    )
    
    # @client.on(events.NewMessage(chats=int(os.getenv("TEST_GROUP_ID"))))
    @client.on(events.NewMessage(chats=int(os.getenv("GROUP_ID"))))
    async def handler(event):
        print(f"New message: {event.message.text}")
        # Add your signal processing here
        await handle_new_message(event)
    return client

async def handle_new_message(event):
    raw_signal = event.message.text
    print(f"New signal: {raw_signal}")

    signal = parse_signal(raw_signal)

    if signal and signal.get('confidence', 0) > 0.7:  # Only act on high-confidence signals
        print(f"🔍 AI-Parsed Signal: {signal}")
        execute_trade(signal["symbol"], signal["action"], TRADE_AMOUNT)
    else:
        print(f"⚠️ Low confidence signal ignored: {raw_signal}")


    

async def main():
    client = await create_telegram_client()
    await client.start(phone=os.getenv("PHONE_NUMBER"))
    print("Telegram monitor started")
    balance = exchange.fetch_balance()
    usdt_balance = balance['USDT']['free']  # Available USDT
    print(f"Available USDT: {usdt_balance}")
    print("Listening for signals...")
    await client.run_until_disconnected()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())