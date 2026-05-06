<div align="center">
<h1>Barter PATH</h1>
  
<p>
  <a href="#"><img src="https://img.shields.io/badge/Python-1F2937?style=for-the-badge&logo=python&logoColor=white" /></a>
  <a href="#"><img src="https://img.shields.io/badge/aiogram-1F2937?style=for-the-badge&logo=telegram&logoColor=white" /></a>
  <a href="#"><img src="https://img.shields.io/badge/aiogram--i18n-1F2937?style=for-the-badge&logo=googletranslate&logoColor=white" /></a>
  <a href="#"><img src="https://img.shields.io/badge/SQLAlchemy-1F2937?style=for-the-badge&logo=sqlalchemy&logoColor=white" /></a>
  <a href="#"><img src="https://img.shields.io/badge/Postgres-1F2937?style=for-the-badge&logo=postgresql&logoColor=white" /></a>
  <a href="#"><img src="https://img.shields.io/badge/Alembic-1F2937?style=for-the-badge" /></a>
</p>

<span>An automated Stalcraft barter tracker providing real-time resource calculations, discount management, and progression monitoring via official database.</span>
</div>

## Features

- 🤖 Telegram bot interface
- 🛠️ Task management system
- 📊 Real-time barter calculations
- 🌍 Multi-language support (i18n)

## Project Structure

```bash
├── migrations/                # Alembic Migrations
├── src/
│   ├── bot/
│   │   ├── handlers/          # Bot handlers
│   │   ├── keyboard/          # Inline & callback keyboards
│   │   │   ├── callback_data.py
│   │   │   ├── inline.py
│   │   ├── middlewares/       # DB & i18n middlewares
│   │   │   ├── db.py
│   │   │   ├── i18n.py
│   │   ├── utils/             # States, UI helpers
│   │   │   ├── states.py
│   │   │   ├── ui.py
│   │   ├── main.py            # Bot entry point
│   ├── db/
│   │   ├── base.py
│   │   ├── models.py
│   │   ├── repo.py
│   ├── locales/               # Translations
│   │   ├── ru/
│   │   ├── en/
│   ├── services/
│   │   ├── stalcraft_api.py
│   │   ├── updater.py
│   ├── __main__.py            # Application launcher
│   ├── config.py              # Environment config loader
```

## Getting Started
### 1. Clone repository

```bash
git clone https://github.com/TheC0rX/barter-path.git
cd barter-path
```
### 2. Install dependencies

```bash
poetry install
```
### 3. Environment setup
Copy `.env.example` to `.env` and fill in the required values.

```env
BOT_TOKEN=your_bot_token_here
GITHUB_TOKEN=your_pat_token_here
DB_URL=postgresql+asyncpg://USER:PASS@localhost:5432/barter_path
```
### 4. Run application

```bash
poetry run python -m src
```