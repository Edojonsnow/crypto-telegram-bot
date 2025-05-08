# main.py
import asyncio
from bot import run_bot  # Your trading bot
from telegram_monitor import main as run_telegram_monitor

async def run_all():
    """Run both the trading bot and the Telegram monitor."""
    telegram_task = asyncio.create_task(run_telegram_monitor())

    await asyncio.to_thread(run_bot)

    await telegram_task


if __name__ == "__main__":
    asyncio.run(run_all())