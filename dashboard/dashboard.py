from __future__ import annotations

from flask import Flask, jsonify, render_template_string


class PerformanceMetrics:
    """Track trades and compute basic performance statistics."""

    def __init__(self, initial_balance: float = 0.0) -> None:
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.trades: list[tuple[str, float, float]] = []

    def record_trade(self, side: str, qty: float, price: float) -> None:
        side = side.lower()
        self.trades.append((side, qty, price))
        if side == "buy":
            self.balance -= qty * price
        elif side == "sell":
            self.balance += qty * price

    def pnl(self) -> float:
        return self.balance - self.initial_balance

    def win_rate(self) -> float:
        results = []
        entry = None
        for side, qty, price in self.trades:
            if side == "buy":
                entry = price
            elif side == "sell" and entry is not None:
                results.append(price - entry)
                entry = None
        if not results:
            return 0.0
        wins = sum(1 for r in results if r > 0)
        return wins / len(results) * 100

    def drawdown(self) -> float:
        equity = [self.initial_balance]
        bal = self.initial_balance
        for side, qty, price in self.trades:
            if side == "buy":
                bal -= qty * price
            else:
                bal += qty * price
            equity.append(bal)
        peak = equity[0]
        max_dd = 0.0
        for val in equity:
            if val > peak:
                peak = val
            dd = peak - val
            if dd > max_dd:
                max_dd = dd
        return max_dd


metrics = PerformanceMetrics()
app = Flask(__name__)


@app.route("/")
def index() -> str:
    return render_template_string(
        """
        <h1>Trading Dashboard</h1>
        <ul>
            <li>PnL: {{ metrics.pnl() }}</li>
            <li>Win Rate: {{ metrics.win_rate() }}%</li>
            <li>Drawdown: {{ metrics.drawdown() }}</li>
        </ul>
        """,
        metrics=metrics,
    )


@app.route("/metrics")
def metrics_route():
    return jsonify(
        {
            "pnl": metrics.pnl(),
            "win_rate": metrics.win_rate(),
            "drawdown": metrics.drawdown(),
        }
    )


def start_dashboard(port: int = 5000) -> None:
    app.run(port=port)
