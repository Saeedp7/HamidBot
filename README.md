# Auto Trade Bot

An AI-powered modular crypto trading bot built in Python.

## 📁 Project Structure

auto_trade_bot/
├── config/ # Configuration files (API keys, strategy settings)
│ └── settings.yaml
├── data/ # Market data (raw and processed)
│ ├── raw/
│ └── processed/
├── strategies/ # All trading strategy implementations
│ ├── base.py # Base class all strategies inherit from
│ ├── ema_crossover.py # Sample EMA crossover strategy
│ └── breakout.py # Breakout trading strategy
├── risk/ # Risk and money management logic
│ └── risk_manager.py
├── execution/ # Order management and broker API integration
│ ├── order_manager.py
│ ├── broker_api.py
│ └── bitunix_broker.py
├── utils/ # Utility functions (TA indicators, logging)
│ ├── indicators.py
│ └── logger.py
├── engine/ # Main logic, strategy selection, regime detection
│ ├── bot_engine.py
│ ├── strategy_selector.py
│ └── regime_detector.py
├── dashboard/ # Optional web/CLI monitoring tools
│ └── dashboard.py
├── backtest/ # Historical backtesting engine
│ └── backtester.py
├── journal/ # Trade journal database/log
│ └── trade_log.db
├── main.py # Entry point to run the trading bot
├── requirements.txt # Python dependencies
├── .gitignore # Git ignored files
└── README.md # Project overview



## ✅ Features

- Modular strategy engine
- Real-time data acquisition
- Customizable risk management
- Execution via broker APIs
- Strategy switching and regime detection
- Logging and performance monitoring

## 🚀 Getting Started

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Broker API Configuration

The project includes a ready-made integration with the Bitunix exchange under the `api/` directory. You can either store credentials in `api/config.yaml` or set the environment variables `BITUNIX_API_KEY` and `BITUNIX_SECRET_KEY`. Run `main.py` with `use_real_api=True` to enable real trading.

### Strategy Optimization

You can test different strategy parameters against historical data using `analysis/optimizer.py`:

```python
from analysis.optimizer import StrategyOptimizer
from strategies.ema_crossover import EMACrossoverStrategy

grid = {"fast": [10, 12, 14], "slow": [26, 30]}
opt = StrategyOptimizer(EMACrossoverStrategy, grid, "BTC-USD", "2024-01-01", "2024-06-30")
best_params, score = opt.optimize()
print(best_params, score)
```
