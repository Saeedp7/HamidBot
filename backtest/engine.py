from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from strategies.base import BaseStrategy, Signal


@dataclass
class Trade:
    strategy: str
    symbol: str
    timeframe: str
    side: str
    entry_time: pd.Timestamp
    exit_time: pd.Timestamp
    entry_price: float
    exit_price: float
    sl: float | None
    tp: float | None
    qty: float
    pnl: float


class BacktestEngine:
    """Run multiple strategies on historical data."""

    def __init__(
        self,
        data: Dict[Tuple[str, str], pd.DataFrame],
        strategies: List[BaseStrategy],
        config: Dict[str, float] | None = None,
    ) -> None:
        self.data = data
        self.strategies = strategies
        self.config = {
            "initial_balance": 10000.0,
            "slippage_pct": 0.0,
            "fee_pct": 0.0,
        }
        if config:
            self.config.update(config)
        self.trade_log: List[Trade] = []
        self.equity = self.config["initial_balance"]
        self.equity_curve: List[float] = [self.equity]
        self.strategy_results: Dict[str, List[float]] = {s.name: [] for s in strategies}

    def _apply_slippage(self, price: float, side: str) -> float:
        adj = price * self.config["slippage_pct"]
        return price + adj if side == "buy" else price - adj

    def _apply_fee(self, price: float, qty: float) -> float:
        return price * qty * self.config["fee_pct"]

    def _run_single(self, strategy: BaseStrategy, df: pd.DataFrame, symbol: str, timeframe: str) -> None:
        position = None
        entry_price = 0.0
        qty = 0.0
        sl = None
        tp = None
        entry_time = None
        for i in range(len(df)):
            row = df.iloc[i]
            context = df.iloc[: i + 1]
            signal = strategy.generate_signal(context)
            if position is None:
                if isinstance(signal, Signal) and signal.action in {"buy", "sell"}:
                    side = signal.action
                    entry_price = self._apply_slippage(row["close"], side)
                    sl = signal.sl
                    tp = signal.tp
                    qty = (self.equity * strategy.risk_pct) / entry_price
                    position = side
                    entry_time = row["timestamp"]
            else:
                exit_reason = None
                exit_price = row["close"]
                if position == "buy":
                    if sl is not None and row["low"] <= sl:
                        exit_price = sl
                        exit_reason = "sl"
                    elif tp is not None and row["high"] >= tp:
                        exit_price = tp
                        exit_reason = "tp"
                    elif isinstance(signal, Signal) and signal.action == "sell":
                        exit_reason = "signal"
                else:
                    if sl is not None and row["high"] >= sl:
                        exit_price = sl
                        exit_reason = "sl"
                    elif tp is not None and row["low"] <= tp:
                        exit_price = tp
                        exit_reason = "tp"
                    elif isinstance(signal, Signal) and signal.action == "buy":
                        exit_reason = "signal"
                if exit_reason:
                    exit_price = self._apply_slippage(exit_price, "sell" if position == "buy" else "buy")
                    pnl = (exit_price - entry_price) * qty if position == "buy" else (entry_price - exit_price) * qty
                    fee = self._apply_fee(entry_price, qty) + self._apply_fee(exit_price, qty)
                    pnl -= fee
                    self.equity += pnl
                    self.equity_curve.append(self.equity)
                    self.strategy_results[strategy.name].append(pnl)
                    self.trade_log.append(
                        Trade(
                            strategy=strategy.name,
                            symbol=symbol,
                            timeframe=timeframe,
                            side=position,
                            entry_time=entry_time,
                            exit_time=row["timestamp"],
                            entry_price=entry_price,
                            exit_price=exit_price,
                            sl=sl,
                            tp=tp,
                            qty=qty,
                            pnl=pnl,
                        )
                    )
                    position = None
                    sl = None
                    tp = None
        # Close open position at last price
        if position is not None:
            exit_price = self._apply_slippage(df.iloc[-1]["close"], "sell" if position == "buy" else "buy")
            pnl = (exit_price - entry_price) * qty if position == "buy" else (entry_price - exit_price) * qty
            fee = self._apply_fee(entry_price, qty) + self._apply_fee(exit_price, qty)
            pnl -= fee
            self.equity += pnl
            self.equity_curve.append(self.equity)
            self.strategy_results[strategy.name].append(pnl)
            self.trade_log.append(
                Trade(
                    strategy=strategy.name,
                    symbol=symbol,
                    timeframe=timeframe,
                    side=position,
                    entry_time=entry_time,
                    exit_time=df.iloc[-1]["timestamp"],
                    entry_price=entry_price,
                    exit_price=exit_price,
                    sl=sl,
                    tp=tp,
                    qty=qty,
                    pnl=pnl,
                )
            )

    def run(self) -> None:
        for (symbol, timeframe), df in self.data.items():
            for strategy in self.strategies:
                if strategy.symbol == symbol and strategy.timeframe == timeframe:
                    self._run_single(strategy, df, symbol, timeframe)

    # Metrics
    def summary(self) -> Dict[str, float]:
        profits = [t.pnl for t in self.trade_log]
        win_trades = [p for p in profits if p > 0]
        loss_trades = [p for p in profits if p <= 0]
        sharpe = 0.0
        if profits:
            returns = np.array(profits) / self.config["initial_balance"]
            if returns.std() != 0:
                sharpe = returns.mean() / returns.std() * np.sqrt(len(returns))
        max_dd = 0.0
        peak = self.equity_curve[0]
        for val in self.equity_curve:
            if val > peak:
                peak = val
            dd = peak - val
            if dd > max_dd:
                max_dd = dd
        expectancy = 0.0
        if profits:
            avg_win = np.mean(win_trades) if win_trades else 0.0
            avg_loss = -np.mean(loss_trades) if loss_trades else 0.0
            prob_win = len(win_trades) / len(profits)
            expectancy = prob_win * avg_win - (1 - prob_win) * avg_loss
        win_rate = len(win_trades) / len(profits) * 100 if profits else 0.0
        return {
            "net_profit": self.equity - self.config["initial_balance"],
            "win_rate": win_rate,
            "sharpe_ratio": sharpe,
            "max_drawdown": max_dd,
            "expectancy": expectancy,
        }

    def per_strategy_metrics(self) -> Dict[str, Dict[str, float]]:
        metrics: Dict[str, Dict[str, float]] = {}
        for name, pnls in self.strategy_results.items():
            wins = [p for p in pnls if p > 0]
            metrics[name] = {
                "trades": len(pnls),
                "hit_ratio": (len(wins) / len(pnls) * 100) if pnls else 0.0,
                "net_return": sum(pnls),
            }
        return metrics

    def save_trade_log(self, path: str = "backtest_results/trade_log.csv") -> None:
        Path(path).parent.mkdir(exist_ok=True)
        df = pd.DataFrame([t.__dict__ for t in self.trade_log])
        df.to_csv(path, index=False)