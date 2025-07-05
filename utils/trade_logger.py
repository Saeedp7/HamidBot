import sqlite3
from typing import Any, Dict, Optional


class TradeLogger:
    """Log executed trades to a SQLite database."""

    def __init__(self, db_path: str = "journal/trade_log.db") -> None:
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self._create_table()

    def _create_table(self) -> None:
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            side TEXT,
            symbol TEXT,
            qty REAL,
            price REAL
        )"""
        )
        self.conn.commit()

    def log_trade(self, trade: Dict[str, Any]) -> None:
        """Insert a trade record into the database."""
        self.conn.execute(
            "INSERT INTO trades (timestamp, side, symbol, qty, price) VALUES (?, ?, ?, ?, ?)",
            (
                trade.get("timestamp")
                or trade.get("datetime"),
                trade.get("side"),
                trade.get("symbol"),
                float(trade.get("amount") or trade.get("qty")),
                float(trade.get("price")) if trade.get("price") is not None else None,
            ),
        )
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()
