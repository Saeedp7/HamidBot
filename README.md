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
│ └── broker_api.py
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