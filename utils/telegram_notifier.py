from __future__ import annotations

from typing import Optional

import schedule
from telegram import Bot
from telegram.error import TelegramError


class TelegramNotifier:
    """Simple wrapper around python-telegram-bot for sending alerts."""

    def __init__(self, token: str, chat_id: str, metrics: Optional[object] = None) -> None:
        self.bot = Bot(token)
        self.chat_id = chat_id
        self.metrics = metrics

    def send_message(self, text: str) -> None:
        try:
            self.bot.send_message(chat_id=self.chat_id, text=text)
        except TelegramError as exc:
            print(f"Telegram error: {exc}")

    def send_trade_alert(self, order: dict) -> None:
        msg = (
            f"Trade: {order.get('side')} {order.get('symbol')} "
            f"qty={order.get('qty')} price={order.get('price')}"
        )
        self.send_message(msg)

    def send_error(self, message: str) -> None:
        self.send_message(f"Error: {message}")

    def send_summary(self) -> None:
        if not self.metrics:
            return
        balance = getattr(self.metrics, "balance", 0.0)
        pnl = getattr(self.metrics, "pnl", lambda: 0.0)()
        self.send_message(f"Account balance: {balance:.2f}\nPnL: {pnl:.2f}")

    def schedule_summary(self) -> None:
        if self.metrics:
            schedule.every().hour.do(self.send_summary)
