# Sports Bot

A Telegram bot for collecting, analyzing, and predicting sports data to support value betting (educational purposes only). The bot gathers match statistics, injury reports, odds, and uses machine learning to estimate probabilities and identify value bets.

## Features

- Multi‑source sports data collection (API‑Football, Football‑Data.org, TheSportsDB, etc.)
- Injury parsing from various news sources
- Machine learning model (logistic regression) for match outcome prediction
- Value betting detection based on model probabilities vs bookmaker odds
- Telegram interface with interactive menus and callbacks
- Periodic data updates and model retraining via scheduler
- Logging, caching, and extensible modular design

## Project Structure

```
sports_bot/
├── api_clients/          # Wrappers for external sports APIs
├── injury_parser/        # Modules for extracting injury information
├── ml/                   # Feature engineering and ML model
├── notifications/        # Alerting utilities (Telegram, email, etc.)
├── utils/                # Scheduler, logger, helper functions
├── data/                 # SQLite database and cached data
├── models/               # Trained model artifacts (gitignored)
├── logs/                 # Runtime logs (gitignored)
├── bot.py                # Main Telegram bot logic (handlers, menus)
├── main.py               # Entry point: starts bot and scheduler
├── config.py             # Configuration (API keys, thresholds, paths)
├── requirements.txt      # Python dependencies
├── demo.py               # Demonstration script (data collection → prediction)
├── init_project.py       # Initializes virtual environment and DB
├── check_ready.py        # Verifies dependencies and readiness
├── .env.example          # Template for environment variables
└── README.md             # This file
```

## Setup

### 1. Clone the repository

```bash
git clone git@github.com:Rusl-K-row/sports_bot.git
cd sports_bot
```

### 2. Create a virtual environment (optional but recommended)

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

Copy the example file and fill in your own values:

```bash
cp .env.example .env
# Edit .env with your actual tokens and keys:
#   BOT_TOKEN=your_telegram_bot_token
#   API_FOOTBALL_KEY=your_api_football_key
#   FOOTBALL_DATA_KEY=your_football_data_key
#   THE_SPORTS_DB_KEY=your_thesportsdb_key   (optional)
#   GITHUB_TOKEN=your_github_pat            (optional, for auto‑backup)
#   MODEL_PATH=./data/model.joblib
#   CACHE_TTL=3600
#   ... (see config.py for full list)
```

### 5. Initialize the database and folders

```bash
python init_project.py
```

### 6. Run the bot

```bash
python main.py
```

The bot will start, initialize the database, launch the scheduler for periodic updates, and listen for Telegram commands.

In Telegram, start a chat with your bot and send `/start` to see the main menu.

## Usage Commands

| Command | Description |
|---------|-------------|
| `/start` | Show main menu with interactive buttons |
| `/help` | Display help and list of available commands |
| `/status` | Show current bot status (uptime, last update, etc.) |
| `/matches` | List upcoming matches with odds and predictions |
| `/value` | Show detected value bets (if any) |
| `/stats` | Display model performance and dataset statistics |

You can also use the inline buttons in the menu to navigate sections (e.g., “📊 View Matches”, “💰 Value Bets”, “🩺 Injury Reports”, “⚙️ Settings”).

## Scheduler

The bot runs a background scheduler (see `utils/scheduler.py`) that:

- Refreshes match data and odds every `CACHE_TTL` seconds (default 1 hour)
- Updates injury reports from configured sources
- Periodically retrains the ML model on the accumulated dataset
- Sends notifications for high‑confidence value bets (if enabled)

Adjust intervals in `config.py` as needed.

## Model

The model in `ml/model.py` is a `LogisticRegression` (multi‑class) predicting:

- `0` – Home win
- `1` – Draw
- `2` – Away win

Features include:

- Team form (last N matches)
- Head‑to‑head record
- Injury impact (number/severity of missing players)
- Home/away advantage
- Weather (if available)
- League-specific constants

The model is saved/loaded via `joblib` to `MODEL_PATH` (default `./data/model.joblib`).

## Injury Parsing

Injury data is extracted from various sources using `injury_parser/`. Each source implements a common interface (`BaseInjuryParser`). Currently included:

- General regex‑based parser (`general_injuries.py`) – works with plain‑text news
- Extendable for Transfermarkt, ESPN, BBC Sport, etc.

Extracted injuries are stored in the `matches` table (JSON blob) and used as features in the ML model.

## Logging

All runtime information is written to `logs/bot.log` (rotating). The logger is configured in `utils/logger.py` with levels adjustable via `config.LOG_LEVEL`.

## Testing & Demo

Run the demonstration script to see a quick pipeline:

```bash
python demo.py
```

It fetches a sample of recent matches, computes features, runs the model, and prints predictions.

## Backup & Maintenance

A helper script `scripts/update_all.sh` (located in the `kira-config` repo) can:

- Check for updates to Ollama/OpenClaw (if used)
- Pull the latest model versions
- Backup settings (IDENTITY.md, USER.md, MEMORY.md, SOUL.md, TOOLS.md) to a private GitHub repo

If you use those tools, refer to their README for details.

## License

This project is for educational and personal use only. Do not use for real‑money gambling without understanding the risks and legal restrictions in your jurisdiction.

## Contributing

Feel free to open issues or submit pull requests. Please follow the existing code style and add tests for new functionality.

---

**Created and maintained by Kira Sinth (Kira Sinth) – your IT mentor assistant.**  
💻😉 For any questions, reach out via Telegram or open an issue here.