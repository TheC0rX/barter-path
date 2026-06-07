<div align="center">

# <img src=".github/assets/images/logo.png" width="38" height="38" align="center" style="vertical-align: middle; margin-right: 8px; border-radius: 6px;" alt="Barter Path Logo"> Barter Path

[![Python](https://img.shields.io/badge/Python-1F2937?style=for-the-badge&logo=python&logoColor=FFFFFF)](https://www.python.org/)
[![Aiogram](https://img.shields.io/badge/aiogram-1F2937?style=for-the-badge&logo=telegram&logoColor=FFFFFF)](https://aiogram.dev/)
[![I18n](https://img.shields.io/badge/aiogram--i18n-1F2937?style=for-the-badge&logo=googletranslate&logoColor=FFFFFF)](https://github.com/aiogram/i18n)
[![SqlAlchemy](https://img.shields.io/badge/SQLAlchemy-1F2937?style=for-the-badge&logo=sqlalchemy&logoColor=FFFFFF)](https://www.sqlalchemy.org/)
[![PostgreSQL](https://img.shields.io/badge/Postgres-1F2937?style=for-the-badge&logo=postgresql&logoColor=FFFFFF)](https://www.postgresql.org/)
[![Alembic](https://img.shields.io/badge/Alembic-1F2937?style=for-the-badge)](https://github.com/sqlalchemy/alembic)

An automated Stalcraft barter tracker providing real-time resource calculations, discount management, and progression monitoring via official database.

</div>

## Features

- 🤖 **Interactive Bot Control** — Easy navigation via inline keyboards.
- 🎒 **Stalcraft Barter Tracker** — Add crafting goals (e.g., A-545) and track your progress.
- 📊 **Dynamic Loot Logging** — Log successfully extracted resources to instantly recalculate what is left.
- 🌍 **Multi-Language Support** — Full English and Russian localization via Fluent.

## Project Structure

```text
├── logs/                             # App logs
├── migrations/                       # DB migrations (Alembic)
├── src/                              # Source code
│   ├── bot/                          # Telegram bot core (aiogram)
│   ├── db/                           # Database module
│   ├── locales/                      # Localization (en/ru)
│   ├── services/                     # External APIs & background updating
│   ├── config.py                     # Config loader
│   └── __main__.py                   # Main entry point
├── .env.example                      # Env template
├── poetry.lock                       # Frozen dependencies log
└── pyproject.toml                    # Dependencies
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
DB_USER=DATABASE_USER
DB_PASSWORD=DATABASE_PASSWORD
DB_HOST=DATABASE_HOST
DB_PORT=DATABASE_PORT
DB_NAME=DATABASE_NAME

BOT_TOKEN=BOT_TOKEN
GITHUB_TOKEN=PAT_TOKEN
```

> ⚠️ **Note:** Create an empty PostgreSQL database matching your `DB_NAME` before proceeding to the next step.

### 4. Run database migrations

```bash
poetry run alembic upgrade head
```

### 5. Run application

```bash
poetry run python -m src
```
